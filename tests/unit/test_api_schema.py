"""Unit tests for API request/response schemas."""

import pytest
from pydantic import ValidationError

from vertex_spec_adapter.schemas.api import (
    APIResponse,
    AccessPattern,
    FinishReason,
    Message,
    MessageRole,
    ModelRequest,
)


class TestMessage:
    """Test Message schema."""
    
    def test_valid_message(self):
        """Test valid message."""
        message = Message(role=MessageRole.USER, content="Hello")
        assert message.role == MessageRole.USER
        assert message.content == "Hello"
    
    def test_message_empty_content(self):
        """Test message with empty content."""
        with pytest.raises(ValidationError):
            Message(role=MessageRole.USER, content="")


class TestModelRequest:
    """Test ModelRequest schema."""
    
    def test_valid_model_request(self):
        """Test valid model request."""
        request = ModelRequest(
            model_id="claude-4-5-sonnet",
            region="us-east5",
            access_pattern=AccessPattern.NATIVE_SDK,
            messages=[Message(role=MessageRole.USER, content="Hello")],
            project_id="my-project-123"
        )
        assert request.model_id == "claude-4-5-sonnet"
        assert request.region == "us-east5"
        assert request.access_pattern == AccessPattern.NATIVE_SDK
        assert len(request.messages) == 1
        assert request.temperature == 1.0
        assert request.stream is False
    
    def test_model_request_with_all_fields(self):
        """Test model request with all fields."""
        request = ModelRequest(
            model_id="gemini-2-5-pro",
            model_version="@20250929",
            region="us-central1",
            access_pattern=AccessPattern.NATIVE_SDK,
            messages=[
                Message(role=MessageRole.SYSTEM, content="You are helpful"),
                Message(role=MessageRole.USER, content="Hello")
            ],
            temperature=0.7,
            max_tokens=2048,
            stream=True,
            project_id="my-project-123"
        )
        assert request.model_version == "@20250929"
        assert request.temperature == 0.7
        assert request.max_tokens == 2048
        assert request.stream is True
        assert len(request.messages) == 2
    
    def test_model_request_empty_messages(self):
        """Test model request with empty messages."""
        with pytest.raises(ValidationError):
            ModelRequest(
                model_id="claude-4-5-sonnet",
                region="us-east5",
                access_pattern=AccessPattern.NATIVE_SDK,
                messages=[],
                project_id="my-project-123"
            )
    
    def test_model_request_invalid_temperature(self):
        """Test model request with invalid temperature."""
        with pytest.raises(ValidationError):
            ModelRequest(
                model_id="claude-4-5-sonnet",
                region="us-east5",
                access_pattern=AccessPattern.NATIVE_SDK,
                messages=[Message(role=MessageRole.USER, content="Hello")],
                temperature=3.0,  # Must be 0.0-2.0
                project_id="my-project-123"
            )
    
    def test_model_request_invalid_max_tokens(self):
        """Test model request with invalid max_tokens."""
        with pytest.raises(ValidationError):
            ModelRequest(
                model_id="claude-4-5-sonnet",
                region="us-east5",
                access_pattern=AccessPattern.NATIVE_SDK,
                messages=[Message(role=MessageRole.USER, content="Hello")],
                max_tokens=0,  # Must be > 0
                project_id="my-project-123"
            )
    
    def test_model_request_invalid_region(self):
        """Test model request with invalid region."""
        with pytest.raises(ValidationError):
            ModelRequest(
                model_id="claude-4-5-sonnet",
                region="invalid-region",
                access_pattern=AccessPattern.NATIVE_SDK,
                messages=[Message(role=MessageRole.USER, content="Hello")],
                project_id="my-project-123"
            )
    
    def test_model_request_invalid_version_format(self):
        """Test model request with invalid version format."""
        with pytest.raises(ValidationError):
            ModelRequest(
                model_id="claude-4-5-sonnet",
                model_version="invalid-version",
                region="us-east5",
                access_pattern=AccessPattern.NATIVE_SDK,
                messages=[Message(role=MessageRole.USER, content="Hello")],
                project_id="my-project-123"
            )


class TestAPIResponse:
    """Test APIResponse schema."""
    
    def test_valid_api_response(self):
        """Test valid API response."""
        response = APIResponse(
            content="Hello, world!",
            input_tokens=10,
            output_tokens=15,
            model="claude-4-5-sonnet"
        )
        assert response.content == "Hello, world!"
        assert response.input_tokens == 10
        assert response.output_tokens == 15
        assert response.total_tokens == 25
        assert response.model == "claude-4-5-sonnet"
    
    def test_api_response_with_all_fields(self):
        """Test API response with all fields."""
        response = APIResponse(
            content="Response text",
            input_tokens=20,
            output_tokens=30,
            model="gemini-2-5-pro",
            finish_reason=FinishReason.STOP,
            metadata={"temperature": 0.7},
            latency_ms=450.5
        )
        assert response.finish_reason == FinishReason.STOP
        assert response.metadata == {"temperature": 0.7}
        assert response.latency_ms == 450.5
        assert response.total_tokens == 50
    
    def test_api_response_total_tokens_calculation(self):
        """Test total_tokens is calculated correctly."""
        response = APIResponse(
            content="Test",
            input_tokens=100,
            output_tokens=200,
            model="claude-4-5-sonnet"
        )
        assert response.total_tokens == 300
    
    def test_api_response_negative_tokens(self):
        """Test API response with negative tokens."""
        with pytest.raises(ValidationError):
            APIResponse(
                content="Test",
                input_tokens=-1,  # Must be >= 0
                output_tokens=10,
                model="claude-4-5-sonnet"
            )
    
    def test_api_response_invalid_error_structure(self):
        """Test API response with invalid error structure."""
        with pytest.raises(ValidationError):
            APIResponse(
                content="",
                input_tokens=10,
                output_tokens=0,
                model="claude-4-5-sonnet",
                error={"message": "Error"}  # Missing 'code' field
            )
    
    def test_api_response_valid_error_structure(self):
        """Test API response with valid error structure."""
        response = APIResponse(
            content="",
            input_tokens=10,
            output_tokens=0,
            model="claude-4-5-sonnet",
            error={
                "code": 500,
                "message": "Internal server error",
                "retry_after": 5
            }
        )
        assert response.error["code"] == 500
        assert response.error["message"] == "Internal server error"

