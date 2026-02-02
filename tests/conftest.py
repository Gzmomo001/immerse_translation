"""
pytest configuration and shared fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_audio_file(temp_dir):
    """Create a sample audio file for testing"""
    # This is a placeholder - in real tests you'd create actual audio data
    audio_path = temp_dir / "sample.wav"
    # Create empty file for now
    audio_path.touch()
    return str(audio_path)


@pytest.fixture
def mock_segment():
    """Return a mock segment for testing"""
    return {
        "start_time": 0.0,
        "end_time": 5.0,
        "speaker_id": "SPEAKER_0",
        "text": "Hello, this is a test.",
        "segment_id": "0000"
    }
