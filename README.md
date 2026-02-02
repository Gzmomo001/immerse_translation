# AI Video Dubbing Warehouse

AI视频配音仓库 - 将英文视频转换为中文配音

## 功能特性

- 音频分离：从视频中分离人声和背景音乐
- 语音识别：使用WhisperX进行高精度的语音识别和说话人分离
- 智能翻译：使用LLM进行语境感知的翻译和配音脚本生成
- 语音合成：使用CosyVoice进行高质量的语音合成
- 音频混合：智能混合配音、背景音乐和音效
- 弹性同步：根据翻译后的文本长度自动调整语速

## 系统要求

- Python >= 3.10
- FFmpeg (用于音频处理)
- 可选：CUDA支持的GPU (用于加速处理)

## 快速开始

### 使用 uv (推荐)

本项目使用 [uv](https://github.com/astral-sh/uv) 作为包管理工具，支持跨平台 PyTorch 安装。

#### macOS

```bash
# 克隆仓库
git clone <repository-url>
cd immerse_translation

# 使用 uv 运行（自动安装依赖）
uv run python -m ai_dubbing --video_path your_video.mp4 --output_dir ./output
```

#### Linux (CPU)

```bash
# 使用 CPU 版本的 PyTorch
uv run python -m ai_dubbing --video_path your_video.mp4 --output_dir ./output
```

#### Linux (CUDA GPU)

```bash
# 首先安装 CUDA 版本的 PyTorch
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# 然后运行
uv run python -m ai_dubbing --video_path your_video.mp4 --output_dir ./output
```

### 使用 pip

```bash
# 安装依赖
pip install -e ".[dev]"

# 运行
python -m ai_dubbing --video_path your_video.mp4 --output_dir ./output
```

## 配置

创建 `.env` 文件来配置API密钥和其他设置：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
WHISPER_MODEL=large-v3
TTS_MODEL=CosyVoice-300M
```

## 项目结构

```
immerse_translation/
├── src/ai_dubbing/          # 主包
│   ├── __init__.py
│   ├── __main__.py          # CLI入口
│   ├── config.py            # 配置管理
│   ├── device.py            # 设备管理
│   ├── separator.py         # 音频分离
│   ├── asr.py               # 语音识别
│   ├── llm_director.py      # LLM导演
│   ├── tts_engine.py        # 语音合成
│   ├── mixer.py             # 音频混合
│   └── utils.py             # 工具函数
├── tests/                   # 测试
├── docs/                    # 文档
├── scripts/                 # 脚本
├── pyproject.toml           # 项目配置
└── README.md               # 本文件
```

## 开发

```bash
# 安装开发依赖
uv pip install -e ".[dev]"

# 运行测试
uv run pytest

# 代码格式化
uv run black src/ tests/
uv run ruff check src/ tests/

# 类型检查
uv run mypy src/
```

## 跨平台 PyTorch 支持

本项目配置支持以下平台：

- **macOS**: 自动使用 CPU/MPS 版本
- **Windows**: 自动使用 CPU 版本
- **Linux CPU**: 自动使用 CPU 版本
- **Linux CUDA**: 手动安装 CUDA 版本 (cu118 或 cu121)

### 切换 PyTorch 版本

```bash
# 安装 CUDA 11.8 版本
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安装 CUDA 12.1 版本
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安装 CPU 版本
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## 许可证

MIT License
