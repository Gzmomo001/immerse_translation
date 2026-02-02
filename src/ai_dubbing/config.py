"""
AI Video Dubbing Warehouse - 配置管理

使用 pydantic 进行配置验证和管理
"""

from pydantic_settings import BaseSettings
from typing import Literal, Optional
from pathlib import Path
from ai_dubbing.device import get_device, get_device_info


class Settings(BaseSettings):
    """全局配置"""

    # LLM 配置（从环境变量读取）
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.siliconflow.cn/v1"
    LLM_MODEL: str = "Pro/moonshotai/Kimi-K2-Thinking"

    # 模型配置
    WHISPER_MODEL: str = "large-v3"
    TTS_MODEL: str = "CosyVoice-300M"
    SEPARATOR_MODEL: str = "UVR-MDX-NET-Inst-HQ-3"

    # 模型路径
    WHISPER_MODEL_PATH: str = "./models/whisper"
    TTS_MODEL_PATH: str = "./models/cosyvoice"

    # 音频参数
    MIN_REFERENCE_DURATION: float = 2.0  # 最小参考音频时长（秒）
    MAX_STRETCH_RATIO: float = 1.25  # 最大变速比例
    MIN_STRETCH_RATIO: float = 0.8  # 最小变速比例
    SAMPLE_RATE: int = 22050  # 采样率
    MAX_SILENCE_RATIO: float = 0.3  # 最大静音比例
    MIN_VOLUME_THRESHOLD: float = 0.1  # 最小音量阈值

    # Auto-Ducking 参数
    DUCK_THRESHOLD: float = 0.3  # 闪避阈值
    DUCK_DB: float = -4.0  # 降低音量（dB）

    # 路径配置
    OUTPUT_DIR: str = "./output"
    LOG_DIR: str = "./logs"
    TEMP_DIR: str = "./temp"
    CACHE_DIR: str = "./cache"  # 缓存目录 - 用于存储模型缓存和临时文件

    # 并发配置
    MAX_CONCURRENT_SEGMENTS: int = 5  # 最大并行分段数

    # GPU 配置
    USE_GPU: bool = True
    GPU_DEVICE: int = 0
    DEVICE: Optional[str] = None  # 'cuda', 'mps', or 'cpu' (None = auto-detect)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 自动检测设备
        if self.DEVICE is None:
            detected_device = get_device()
            self.DEVICE = detected_device
        else:
            from ai_dubbing.device import set_device

            set_device(self.DEVICE)

        # 确保所有路径目录存在
        Path(self.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.LOG_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.TEMP_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.CACHE_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.WHISPER_MODEL_PATH).mkdir(parents=True, exist_ok=True)
        Path(self.TTS_MODEL_PATH).mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()
