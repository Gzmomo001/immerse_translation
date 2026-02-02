# Tests Directory

This directory contains all test files for the AI Video Dubbing project.

## Structure

```
tests/
├── unit/              # Unit tests
│   ├── __init__.py
│   ├── test_asr.py
│   ├── test_llm_director.py
│   ├── test_mixer.py
│   ├── test_separator.py
│   ├── test_tts_engine.py
│   └── test_utils.py
├── integration/       # Integration tests
│   ├── __init__.py
│   └── test_pipeline.py
├── fixtures/          # Test fixtures and data
│   └── sample_audio.wav
└── conftest.py        # pytest configuration and fixtures
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_asr.py

# Run with verbose output
pytest -v
```
