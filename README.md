# AI Video Dubbing Warehouse

AI视频配音仓库 - 将英文视频智能转换为中文配音

## 项目简介

这是一个基于AI的视频配音系统，能够将英文视频内容自动转换为中文配音，保持原视频的情感、语调和节奏。

## 主要功能

- **音源分离**: 使用深度学习模型分离人声和背景音
- **语音识别**: 使用Whisper进行高精度语音识别
- **AI导演**: 使用LLM进行智能翻译和情感分析
- **语音合成**: 使用CosyVoice生成情感化中文语音
- **后期处理**: 弹性同步和自动混音

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/ai-video-dubbing.git
cd ai-video-dubbing

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"
```

### 配置

创建 `.env` 文件：

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=Pro/moonshotai/Kimi-K2-Thinking
```

### 使用

```bash
python -m ai_dubbing --video_path path/to/video.mp4 --output_dir ./output
```

## 项目结构

```
ai-video-dubbing/
├── src/
│   └── ai_dubbing/
│       ├── __init__.py
│       ├── asr.py              # 语音识别模块
│       ├── llm_director.py     # AI导演模块
│       ├── mixer.py            # 混音模块
│       ├── separator.py        # 音源分离模块
│       ├── tts_engine.py       # 语音合成模块
│       ├── utils.py            # 工具函数
│       └── device.py           # 设备管理
├── tests/                      # 测试目录
├── docs/                       # 文档目录
├── scripts/                    # 工具脚本
├── pyproject.toml             # 项目配置
├── setup.py                   # 安装脚本
├── setup.cfg                  # 额外配置
├── requirements.txt           # 依赖列表
└── README.md                  # 项目说明
```

## 技术栈

- **Python 3.10+**
- **PyTorch**: 深度学习框架
- **Whisper**: 语音识别
- **CosyVoice**: 语音合成
- **OpenAI API**: LLM翻译
- **FFmpeg**: 音视频处理

## 开发

### 代码格式化

```bash
black src/
isort src/
```

### 类型检查

```bash
mypy src/
```

### 运行测试

```bash
pytest
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
