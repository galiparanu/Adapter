"""Unit tests for VertexAIClient."""

from unittest.mock import MagicMock, patch

import pytest

from vertex_spec_adapter.core.client import VertexAIClient
from vertex_spec_adapter.core.exceptions import ModelNotFoundError
from vertex_spec_adapter.schemas.config import VertexConfig


class TestVertexAIClient:
    """Test VertexAIClient class."""
    
    def test_init(self):
        """Test VertexAIClient initialization."""
        with patch('vertex_spec_adapter.core.client.AuthenticationManager') as mock_auth:
            mock_creds = MagicMock()
            mock_auth.return_value.authenticate.return_value = mock_creds
            
            client = VertexAIClient(
                project_id="test-project",
                region="us-east5",
                model_id="claude-4-5-sonnet",
                credentials=mock_creds,
            )
            
            assert client.project_id == "test-project"
            assert client.region == "us-east5"
            assert client.model_id == "claude-4-5-sonnet"
    
    def test_detect_access_pattern_claude(self):
        """Test access pattern detection for Claude."""
        with patch('vertex_spec_adapter.core.client.AuthenticationManager'):
            client = VertexAIClient(
                project_id="test-project",
                region="us-east5",
                model_id="claude-4-5-sonnet",
                credentials=MagicMock(),
            )
            
            assert client.access_pattern == "native_sdk"
    
    def test_detect_access_pattern_gemini(self):
        """Test access pattern detection for Gemini."""
        with patch('vertex_spec_adapter.core.client.AuthenticationManager'):
            client = VertexAIClient(
                project_id="test-project",
                region="us-east5",
                model_id="gemini-2-5-pro",
                credentials=MagicMock(),
            )
            
            assert client.access_pattern == "native_sdk"
    
    def test_detect_access_pattern_qwen(self):
        """Test access pattern detection for Qwen."""
        with patch('vertex_spec_adapter.core.client.AuthenticationManager'):
            client = VertexAIClient(
                project_id="test-project",
                region="us-east5",
                model_id="qwen-coder",
                credentials=MagicMock(),
            )
            
            assert client.access_pattern == "maas"
    
    def test_token_usage_property(self):
        """Test token usage property."""
        with patch('vertex_spec_adapter.core.client.AuthenticationManager'):
            client = VertexAIClient(
                project_id="test-project",
                region="us-east5",
                model_id="claude-4-5-sonnet",
                credentials=MagicMock(),
            )
            
            usage = client.token_usage
            assert "input_tokens" in usage
            assert "output_tokens" in usage
            assert "total_tokens" in usage
    
    def test_validate_model_availability(self):
        """Test model availability validation."""
        with patch('vertex_spec_adapter.core.client.AuthenticationManager'):
            client = VertexAIClient(
                project_id="test-project",
                region="us-east5",
                model_id="claude-4-5-sonnet",
                credentials=MagicMock(),
            )
            
            assert client.validate_model_availability("claude-4-5-sonnet", "us-east5") is True
    
    def test_validate_model_availability_not_found(self):
        """Test model availability validation for unknown model."""
        with patch('vertex_spec_adapter.core.client.AuthenticationManager'):
            client = VertexAIClient(
                project_id="test-project",
                region="us-east5",
                model_id="claude-4-5-sonnet",
                credentials=MagicMock(),
            )
            
            with pytest.raises(ModelNotFoundError):
                client.validate_model_availability("unknown-model", "us-east5")

