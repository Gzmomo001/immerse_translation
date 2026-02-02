"""
Unit tests for LLM Director module
"""

import pytest
from unittest.mock import patch, AsyncMock
import json


class TestDirectDubbing:
    """Tests for direct_dubbing function"""
    
    @pytest.mark.asyncio
    @patch('src.llm_director.AsyncOpenAI')
    async def test_direct_dubbing_success(self, mock_openai_class):
        """Test successful dubbing direction"""
        # Mock the OpenAI client
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [
            AsyncMock(message=AsyncMock(content=json.dumps({
                "translated_text": "你好世界",
                "emotion": "happy",
                "non_linguistic": None,
                "confidence": 0.95
            })))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        from src.llm_director import direct_dubbing
        
        segment = {"text": "Hello world"}
        context = "Speaker: SPEAKER_0"
        
        result = await direct_dubbing(segment, context)
        
        assert result.translated_text == "你好世界"
        assert result.emotion == "happy"
        assert result.confidence == 0.95
    
    @pytest.mark.asyncio
    @patch('src.llm_director.AsyncOpenAI')
    async def test_direct_dubbing_with_non_linguistic(self, mock_openai_class):
        """Test dubbing with non-linguistic features"""
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [
            AsyncMock(message=AsyncMock(content=json.dumps({
                "translated_text": "哈哈",
                "emotion": "happy",
                "non_linguistic": "[laughter]",
                "confidence": 0.90
            })))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        from src.llm_director import direct_dubbing
        
        segment = {"text": "Haha"}
        context = "Speaker: SPEAKER_0"
        
        result = await direct_dubbing(segment, context)
        
        assert result.non_linguistic == "[laughter]"


class TestDirectorOutput:
    """Tests for DirectorOutput model"""
    
    def test_director_output_creation(self):
        """Test creating DirectorOutput instance"""
        from src.llm_director import DirectorOutput
        
        output = DirectorOutput(
            translated_text="测试文本",
            emotion="neutral",
            confidence=0.85
        )
        
        assert output.translated_text == "测试文本"
        assert output.emotion == "neutral"
        assert output.confidence == 0.85
        assert output.non_linguistic is None
