"""
AI Video Dubbing Warehouse - 主程序入口

完整配音流程编排
"""

import asyncio
import argparse
import logging
from pathlib import Path
import subprocess
import numpy as np
import librosa
import soundfile as sf
import torch

# 解决 PyTorch 2.6+ weights_only 问题
# 允许加载 pyannote.audio 检查点中使用的 omegaconf 类
try:
    import omegaconf.listconfig
    import omegaconf.base
    import omegaconf

    torch.serialization.add_safe_globals(
        [
            omegaconf.listconfig.ListConfig,
            omegaconf.base.ContainerMetadata,
            omegaconf.DictConfig,
            omegaconf.OmegaConf,
        ]
    )
except ImportError:
    pass
except AttributeError:
    pass

# 导入所有模块
from ai_dubbing.separator import separate_audio
from ai_dubbing.asr import transcribe_and_diarize
from ai_dubbing.llm_director import direct_dubbing
from ai_dubbing.tts_engine import synthesize_speech, extract_dynamic_reference
from ai_dubbing.mixer import elastic_sync, mix_audio
from ai_dubbing.device import get_device_info
from ai_dubbing.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("ai_dubbing.main")


def setup_logging(log_dir: str = "./logs"):
    """配置日志系统"""
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # 添加文件日志
    file_handler = logging.FileHandler(f"{log_dir}/dubbing.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # 添加到根日志记录器
    logging.getLogger().addHandler(file_handler)


def concatenate_audio_sync(audio_paths: list[str], output_path: str) -> str:
    """
    拼接多个音频文件

    Args:
        audio_paths: 音频文件路径列表
        output_path: 输出文件路径

    Returns:
        拼接后的音频路径
    """
    logger.info(f"拼接 {len(audio_paths)} 个音频文件")

    segments = []
    sr = None

    for path in audio_paths:
        if not Path(path).exists():
            logger.warning(f"音频文件不存在，跳过: {path}")
            continue
        audio, sample_rate = librosa.load(path, sr=settings.SAMPLE_RATE)
        if sr is None:
            sr = sample_rate
        segments.append(audio)

    if segments:
        concatenated = np.concatenate(segments)
        sf.write(output_path, concatenated, sr)
    else:
        logger.warning("没有有效的音频段")
        sf.write(output_path, np.zeros(22050 * 5), settings.SAMPLE_RATE)

    logger.info(f"音频拼接完成: {output_path}")

    return output_path


async def concatenate_audio(audio_paths: list[str], output_path: str) -> str:
    """
    拼接多个音频文件（异步版本）

    Args:
        audio_paths: 音频文件路径列表
        output_path: 输出文件路径

    Returns:
        拼接后的音频路径
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: concatenate_audio_sync(audio_paths, output_path)
    )


async def get_video_duration(video_path: str) -> float:
    """
    获取视频时长

    Args:
        video_path: 视频文件路径

    Returns:
        视频时长（秒）
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"ffprobe 获取视频时长失败: {stderr.decode()}")

    duration = float(stdout.decode().strip())
    logger.info(f"视频时长: {duration:.2f}s")

    return duration


async def merge_video_audio(video_path: str, audio_path: str, output_path: str) -> str:
    """
    合成视频和音频

    Args:
        video_path: 视频文件路径
        audio_path: 音频文件路径
        output_path: 输出文件路径

    Returns:
        合成后的视频路径
    """
    logger.info(f"合成视频和音频: {video_path} + {audio_path}")

    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-i",
        audio_path,
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-shortest",
        "-y",
        output_path,
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode("utf-8", errors="ignore")
        raise RuntimeError(f"ffmpeg 合成视频失败: {error_msg}")

    logger.info(f"视频合成完成: {output_path}")

    return output_path


async def process_segment(segment: dict, vocals_path: str, output_dir: str) -> str:
    """
    处理单个语音分段

    Args:
        segment: 分段数据
        vocals_path: 人声文件路径
        output_dir: 输出目录

    Returns:
        生成的中文语音路径
    """
    segment_id = segment.get("segment_id", "unknown")
    logger.info(f"处理分段 {segment_id}: {segment.get('text', '')[:50]}...")

    try:
        ref_output_path = str(Path(output_dir) / f"ref_{segment_id}.wav")
        reference_path = await extract_dynamic_reference(
            vocals_path, segment["start_time"], segment["end_time"], ref_output_path
        )

        context = f"Speaker: {segment.get('speaker_id', 'UNKNOWN')}"
        director_result = await direct_dubbing(segment, context)

        audio_output_path = str(Path(output_dir) / f"segment_{segment_id}.wav")
        dubbed_audio = await synthesize_speech(
            director_result.translated_text,
            director_result.emotion,
            reference_path,
            audio_output_path,
        )

        target_duration = segment["end_time"] - segment["start_time"]
        synced_output_path = str(Path(output_dir) / f"synced_{segment_id}.wav")
        synced_audio = await elastic_sync(
            dubbed_audio, target_duration, synced_output_path
        )

        logger.info(f"分段 {segment_id} 处理完成")

        return synced_audio

    except Exception as e:
        logger.error(f"处理分段 {segment_id} 失败: {e}", exc_info=True)
        raise


async def run_pipeline(video_path: str, output_dir: str):
    """
    完整配音流程

    Args:
        video_path: 输入视频路径
        output_dir: 输出目录
    """
    logger.info("=" * 50)
    logger.info("AI Video Dubbing Warehouse - 开始处理")
    logger.info(f"输入视频: {video_path}")
    logger.info(f"输出目录: {output_dir}")

    # 显示设备信息
    device_info = get_device_info()
    logger.info("=" * 50)
    logger.info("设备信息:")
    logger.info(f"  设备类型: {device_info.get('device_type', 'unknown').upper()}")
    logger.info(f"  设备名称: {device_info.get('device_name', 'N/A')}")
    if device_info.get("device_type") == "cuda":
        logger.info(f"  设备数量: {device_info.get('device_count', 1)}")
        logger.info(f"  显存总量: {device_info.get('memory_total', 0):.2f} GB")
    logger.info("=" * 50)

    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        # Step 1: 音源分离
        logger.info("\n[Step 1/7] 音源分离...")
        vocals_path, background_path = await separate_audio(video_path, output_dir)

        # Step 2: 语音识别
        logger.info("\n[Step 2/7] 语音识别和说话人聚类...")
        segments = await transcribe_and_diarize(vocals_path)
        logger.info(f"识别到 {len(segments)} 个语音分段")

        # 为每个分段添加唯一ID
        for i, segment in enumerate(segments):
            segment["segment_id"] = f"{i:04d}"

        # Step 3: 并行处理所有分段
        logger.info("\n[Step 3/7] 并行处理所有分段...")
        logger.info(f"待处理分段数: {len(segments)}")
        try:
            dubbed_segments = await asyncio.gather(
                *[process_segment(seg, vocals_path, output_dir) for seg in segments],
                return_exceptions=True,
            )

            successful_segments = [
                s for s in dubbed_segments if not isinstance(s, Exception)
            ]
            failed_segments = [
                (i, s)
                for i, s in enumerate(dubbed_segments)
                if isinstance(s, Exception)
            ]

            logger.info(
                f"分段处理完成: 成功 {len(successful_segments)}/{len(segments)}, 失败 {len(failed_segments)}"
            )

            if failed_segments:
                for i, error in failed_segments:
                    logger.error(f"分段 {i} 失败: {error}")

            if len(successful_segments) < len(segments) * 0.5:
                raise RuntimeError(
                    f"超过 50% 的分段处理失败 ({len(successful_segments)}/{len(segments)})"
                )

        except Exception as e:
            logger.error(f"分段处理失败: {e}", exc_info=True)
            raise

        # Step 4: 拼接所有中文语音
        logger.info("\n[Step 4/7] 拼接所有中文语音...")
        logger.info(f"准备拼接 {len(successful_segments)} 个音频文件")
        chinese_vocal_path = str(Path(output_dir) / "chinese_vocal.wav")

        # 确保所有项目都是字符串
        audio_paths = [str(s) for s in successful_segments]
        await concatenate_audio(audio_paths, chinese_vocal_path)
        logger.info(f"中文人声已拼接: {chinese_vocal_path}")

        # Step 5: 弹性同步（整体）
        logger.info("\n[Step 5/7] 弹性同步（整体）...")
        logger.info(f"获取视频时长...")
        video_duration = await get_video_duration(video_path)
        logger.info(f"视频时长: {video_duration:.2f}秒")
        final_vocal_path = str(Path(output_dir) / "final_vocal.wav")
        logger.info(f"对齐音频到视频时长...")
        await elastic_sync(chinese_vocal_path, video_duration, final_vocal_path)
        logger.info(f"弹性同步完成: {final_vocal_path}")

        # Step 6: 混音
        logger.info("\n[Step 6/7] 混合人声和背景音...")
        logger.info(f"人声路径: {final_vocal_path}")
        logger.info(f"背景音路径: {background_path}")
        mixed_audio_path = str(Path(output_dir) / "mixed_audio.wav")
        logger.info(f"开始混音...")
        mixed_audio = await mix_audio(
            final_vocal_path, background_path, mixed_audio_path
        )
        logger.info(f"混音完成: {mixed_audio}")

        # Step 7: 合成视频
        logger.info("\n[Step 7/7] 合成最终视频...")
        logger.info(f"原始视频: {video_path}")
        logger.info(f"混音音频: {mixed_audio}")
        final_video_path = str(Path(output_dir) / "final_dubbed_video.mp4")
        logger.info(f"开始合成...")
        await merge_video_audio(video_path, mixed_audio, final_video_path)
        logger.info(f"最终视频已生成: {final_video_path}")

        logger.info("\n" + "=" * 50)
        logger.info("✅ 处理完成！")
        logger.info(f"输出文件: {final_video_path}")
        logger.info("=" * 50)

        return final_video_path

    except Exception as e:
        logger.error("\n" + "=" * 50)
        logger.error("❌ 处理失败！")
        logger.error(f"错误: {e}")
        logger.error("=" * 50)
        raise


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="AI Video Dubbing Warehouse - 将英文视频转换为中文配音"
    )
    parser.add_argument("--video_path", required=True, help="输入视频路径")
    parser.add_argument(
        "--output_dir", default="./output", help="输出目录 (默认: ./output)"
    )

    args = parser.parse_args()

    # 配置日志
    setup_logging(args.output_dir)

    # 运行异步流程
    asyncio.run(run_pipeline(args.video_path, args.output_dir))


if __name__ == "__main__":
    main()
