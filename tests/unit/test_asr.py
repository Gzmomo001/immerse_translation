"""
Unit tests for ASR module
"""

import pytest
from unittest.mock import patch, MagicMock


class TestTranscribeSync:
    """Tests for transcribe_sync function"""
    
    @patch('src.asr.whisper.load_model')
    def test_transcribe_sync_basic(self, mock_load_model):
        """Test basic transcription"""
        # Mock the whisper model
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "segments": [
                {"start": 0.0, "end": 5.0, "text": "Hello world"}
            ]
        }
        mock_load_model.return_value = mock_model
        
        # Import after patching
        from src.asr import transcribe_sync
        
        result = transcribe_sync("dummy_path.wav")
        
        assert len(result) == 1
        assert result[0]["start_time"] == 0.0
        assert result[0]["end_time"] == 5.0
        assert result[0]["text"] == "Hello world"
        assert result[0]["speaker_id"] == "SPEAKER_0"
    
    @patch('src.asr.whisper.load_model')
    def test_transcribe_sync_multiple_segments(self, mock_load_model):
        """Test transcription with multiple segments"""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "segments": [
                {"start": 0.0, "end": 3.0, "text": "First segment"},
                {"start": 3.5, "end": 7.0, "text": "Second segment"}
            ]
        }
        mock_load_model.return_value = mock_model
        
        from src.asr import transcribe_sync
        
        result = transcribe_sync("dummy_path.wav")
        
        assert len(result) == 2
        assert result[0]["text"] == "First segment"
        assert result[1]["text"] == "Second segment"


class TestTranscribeAndDiarize:
    """Tests for transcribe_and_diarize function"""
    
    @pytest.mark.asyncio
    @patch('src.asr.transcribe_sync')
    async def test_transcribe_and_diarize(self, mock_transcribe):
        """Test async transcription"""
        mock_transcribe.return_value = [
            {"start_time": 0.0, "end_time": 5.0, "text": "Test", "speaker_id": "SPEAKER_0"}
        ]
        
        from src.asr import transcribe_and_diarize
        
        result = await transcribe_and_diarize("dummy_path.wav")
        
        assert len(result) == 1
        assert result[0]["text"] == "Test"
