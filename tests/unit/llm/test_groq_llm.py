import os
from unittest.mock import patch, MagicMock
from rag.llm.groq_llm import GroqLLM
import pytest
 
class TestGroqLLMInitialization:
    """Test Groq LLM initialization"""
 
    def test_groq_requires_api_key(self):
        """Test that Groq requires API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                GroqLLM()
 
    def test_groq_initializes_with_key(self):
        """Test that Groq initializes with API key"""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            llm = GroqLLM()
            assert llm is not None
            assert llm.client is not None
 
 
class TestGroqGeneration:
    """Test Groq generation"""
 
    @patch.dict(os.environ, {"GROQ_API_KEY": "test_key"})
    @patch("rag.llm.groq_llm.Groq")
    def test_generate_raw(self, mock_groq):
        """Test generate_raw method"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        # Mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        llm = GroqLLM()
        result = llm.generate_raw("Test prompt")
        
        assert result == "Test response"
 
    @patch.dict(os.environ, {"GROQ_API_KEY": "test_key"})
    @patch("rag.llm.groq_llm.Groq")
    def test_generate_with_context(self, mock_groq):
        """Test generate with context"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Answer based on context"
        mock_client.chat.completions.create.return_value = mock_response
        
        llm = GroqLLM()
        result = llm.generate("What is leave?", context="Leave is 20 days")
        
        assert len(result) > 0
 
 
class TestGroqCasualMode:
    """Test Groq casual response mode"""
 
    @patch.dict(os.environ, {"GROQ_API_KEY": "test_key"})
    @patch("rag.llm.groq_llm.Groq")
    def test_generate_casual(self, mock_groq):
        """Test casual response generation"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hi there!"
        mock_client.chat.completions.create.return_value = mock_response
        
        llm = GroqLLM()
        result = llm.generate("Hello", casual=True)
        
        assert "Hi" in result or len(result) > 0
 
 
class TestGroqFallback:
    """Test Groq fallback mode"""
 
    @patch.dict(os.environ, {"GROQ_API_KEY": "test_key"})
    @patch("rag.llm.groq_llm.Groq")
    def test_generate_fallback(self, mock_groq):
        """Test fallback response"""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "I don't have information..."
        mock_client.chat.completions.create.return_value = mock_response
        
        llm = GroqLLM()
        result = llm.generate("Random question", fallback=True)
        
        assert len(result) > 0
 
