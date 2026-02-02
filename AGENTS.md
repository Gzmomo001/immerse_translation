# AGENTS.md - AI Video Dubbing Warehouse

Guidelines for agentic coding agents working in this repository.

## Build/Test/Lint Commands

### Environment Setup
```bash
# Create virtual environment with uv
uv venv --python 3.10

# Install dependencies
uv sync

# Install with dev dependencies
uv pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
pytest

# Run single test file
pytest tests/unit/test_asr.py

# Run single test class
pytest tests/unit/test_asr.py::TestTranscribeSync

# Run single test method
pytest tests/unit/test_asr.py::TestTranscribeSync::test_transcribe_sync_basic

# Run with coverage
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v
```

### Linting & Formatting
```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Fix auto-fixable lint issues
ruff check --fix src/ tests/

# Run all checks
black src/ tests/ && ruff check src/ tests/
```

### Type Checking (Optional)
```bash
mypy src/
```

## Code Style Guidelines

### Imports
- Order: stdlib → third-party → local
- Group with blank lines between sections
- Use absolute imports for package modules
- Local imports use `from ai_dubbing.xxx import ...`

Example:
```python
import asyncio
import logging
from pathlib import Path

import numpy as np
import torch

from ai_dubbing.config import settings
from ai_dubbing.utils import retry_async
```

### Naming Conventions
- **Modules**: lowercase_with_underscores (e.g., `llm_director.py`)
- **Classes**: PascalCase (e.g., `DirectorOutput`)
- **Functions/Variables**: snake_case (e.g., `transcribe_sync`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `LLM_API_KEY`)
- **Private**: prefix with underscore (e.g., `_patched_torch_load`)

### Type Hints
- Use type hints for all function signatures
- Use `typing` imports: `List`, `Dict`, `Optional`, `Callable`
- Use Pydantic models for structured data

Example:
```python
from typing import List, Dict, Optional

def process_segments(
    segments: List[Dict[str, Any]],
    output_dir: Path,
    sample_rate: int = 22050
) -> Optional[str]:
    ...
```

### Docstrings
- Use Google-style docstrings
- Chinese comments acceptable for business logic
- Triple double quotes for all docstrings

Example:
```python
def transcribe_sync(audio_path: str) -> List[Dict]:
    """同步转录音频文件
    
    Args:
        audio_path: 音频文件路径
        
    Returns:
        转录结果列表，每个元素包含 start_time, end_time, text, speaker_id
        
    Raises:
        FileNotFoundError: 当音频文件不存在时
    """
```

### Async Patterns
- Use async/await for I/O operations
- Provide sync versions with `_sync` suffix for CPU-bound tasks
- Use `asyncio.gather()` with `return_exceptions=True` for concurrent operations
- Use `asyncio.get_event_loop().run_in_executor()` to wrap sync code

### Error Handling
- Use custom `@retry_async` decorator for transient failures
- Use `@handle_errors` decorator for graceful error handling
- Always log errors with `logger.error(..., exc_info=True)`
- Provide fallback mechanisms for non-critical failures

Example:
```python
@retry_async(max_attempts=3, delay=2.0, backoff=2.0)
async def api_call() -> Dict:
    ...

try:
    result = await api_call()
except Exception as e:
    logger.error(f"API call failed: {e}", exc_info=True)
    raise
```

### Formatting
- Line length: 88 characters (Black default)
- Use Black for formatting
- Use ruff for linting (E, F, W, I rules)
- Target Python 3.10+

### Testing Patterns
- Use pytest with async support (`@pytest.mark.asyncio`)
- Mock external dependencies (OpenAI, Whisper, etc.)
- Use fixtures in `conftest.py` for shared test data
- Test both success and error cases

### Project Structure
```
src/ai_dubbing/          # Main package
├── __init__.py
├── config.py             # Configuration management
├── device.py             # Device detection (CUDA/MPS/CPU)
├── separator.py          # Audio source separation
├── asr.py                # Speech recognition
├── llm_director.py       # LLM translation/emotion
├── tts_engine.py         # Text-to-speech
├── mixer.py              # Audio mixing
└── utils.py              # Utilities

tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests
├── conftest.py           # Shared fixtures
└── README.md             # Testing guide
```

### Key Dependencies
- PyTorch 2.0+ (CPU for macOS/Windows, CUDA for Linux)
- WhisperX for transcription
- OpenAI SDK for LLM
- Pydantic for data validation
- pytest for testing

### Platform Notes
- macOS/Windows: PyTorch CPU auto-installed
- Linux CUDA: Manual install required
- Use `uv run` prefix for commands in uv environment
