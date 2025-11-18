"""Unit tests for custom exception hierarchy."""

import pytest

from vertex_spec_adapter.core.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ModelNotFoundError,
    QuotaExceededError,
    RateLimitError,
    VertexSpecAdapterError,
)


class TestVertexSpecAdapterError:
    """Test base exception class."""
    
    def test_base_exception_without_suggested_fix(self):
        """Test base exception without suggested fix."""
        error = VertexSpecAdapterError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.suggested_fix is None
    
    def test_base_exception_with_suggested_fix(self):
        """Test base exception with suggested fix."""
        error = VertexSpecAdapterError("Test error", "Run this command")
        assert "Test error" in str(error)
        assert "→ Run this command" in str(error)
        assert error.suggested_fix == "Run this command"


class TestAuthenticationError:
    """Test authentication error."""
    
    def test_authentication_error_basic(self):
        """Test basic authentication error."""
        error = AuthenticationError("Auth failed")
        assert error.message == "Auth failed"
        assert error.code is None
    
    def test_authentication_error_with_code(self):
        """Test authentication error with error code."""
        error = AuthenticationError(
            "Auth failed",
            code="AUTH_001",
            suggested_fix="Run 'gcloud auth login'"
        )
        assert error.code == "AUTH_001"
        assert error.suggested_fix == "Run 'gcloud auth login'"


class TestConfigurationError:
    """Test configuration error."""
    
    def test_configuration_error_basic(self):
        """Test basic configuration error."""
        error = ConfigurationError("Invalid config")
        assert error.message == "Invalid config"
        assert error.field is None
    
    def test_configuration_error_with_field(self):
        """Test configuration error with field name."""
        error = ConfigurationError(
            "Invalid value",
            field="project_id",
            suggested_fix="Use valid GCP project ID format"
        )
        assert error.field == "project_id"
        assert error.suggested_fix == "Use valid GCP project ID format"


class TestAPIError:
    """Test API error."""
    
    def test_api_error_basic(self):
        """Test basic API error."""
        error = APIError("API call failed")
        assert error.message == "API call failed"
        assert error.status_code is None
        assert error.retryable is False
    
    def test_api_error_with_status_code(self):
        """Test API error with status code."""
        error = APIError("Server error", status_code=500, retryable=True)
        assert error.status_code == 500
        assert error.retryable is True
    
    def test_api_error_with_retry_after(self):
        """Test API error with retry_after."""
        error = APIError("Rate limited", retry_after=5)
        assert error.retry_after == 5
    
    def test_api_error_auto_generates_troubleshooting_steps(self):
        """Test that APIError auto-generates troubleshooting steps."""
        error = APIError("Unauthorized", status_code=401)
        assert len(error.troubleshooting_steps) > 0
        assert "credentials" in error.troubleshooting_steps[0].lower()
    
    def test_api_error_with_custom_troubleshooting_steps(self):
        """Test APIError with custom troubleshooting steps."""
        steps = ["Step 1", "Step 2"]
        error = APIError("Error", status_code=500, troubleshooting_steps=steps)
        assert error.troubleshooting_steps == steps
    
    def test_api_error_formatted_message_includes_troubleshooting(self):
        """Test that formatted error message includes troubleshooting steps."""
        error = APIError("Error", status_code=401)
        message = str(error)
        assert "Troubleshooting steps:" in message
        assert any("credential" in step.lower() for step in error.troubleshooting_steps)
    
    def test_api_error_troubleshooting_for_different_status_codes(self):
        """Test troubleshooting steps for different status codes."""
        # 403 error
        error_403 = APIError("Forbidden", status_code=403)
        assert len(error_403.troubleshooting_steps) > 0
        assert any("permission" in step.lower() or "role" in step.lower() for step in error_403.troubleshooting_steps)
        
        # 404 error
        error_404 = APIError("Not found", status_code=404)
        assert len(error_404.troubleshooting_steps) > 0
        assert any("model" in step.lower() for step in error_404.troubleshooting_steps)
        
        # 429 error
        error_429 = APIError("Rate limit", status_code=429)
        assert len(error_429.troubleshooting_steps) > 0
        assert any("wait" in step.lower() or "quota" in step.lower() for step in error_429.troubleshooting_steps)
        
        # 500 error
        error_500 = APIError("Server error", status_code=500)
        assert len(error_500.troubleshooting_steps) > 0
        assert any("temporary" in step.lower() or "retry" in step.lower() for step in error_500.troubleshooting_steps)


class TestModelNotFoundError:
    """Test model not found error."""
    
    def test_model_not_found_error_basic(self):
        """Test basic model not found error."""
        error = ModelNotFoundError(
            "Model not found",
            model_id="claude-4-5-sonnet",
            region="us-west1"
        )
        assert error.model_id == "claude-4-5-sonnet"
        assert error.region == "us-west1"
        assert error.status_code == 404
        assert error.available_regions == []
    
    def test_model_not_found_error_with_available_regions(self):
        """Test model not found error with available regions."""
        error = ModelNotFoundError(
            "Model not found",
            model_id="claude-4-5-sonnet",
            region="us-west1",
            available_regions=["us-east5", "europe-west1"]
        )
        assert error.available_regions == ["us-east5", "europe-west1"]
        assert "us-east5" in error.suggested_fix


class TestQuotaExceededError:
    """Test quota exceeded error."""
    
    def test_quota_exceeded_error_basic(self):
        """Test basic quota exceeded error."""
        error = QuotaExceededError()
        assert error.message == "Quota exceeded"
        assert error.status_code == 429
        assert error.retryable is True
    
    def test_quota_exceeded_error_with_retry_after(self):
        """Test quota exceeded error with retry_after."""
        error = QuotaExceededError(retry_after=60)
        assert error.retry_after == 60
        assert "60 seconds" in error.suggested_fix


class TestRateLimitError:
    """Test rate limit error."""
    
    def test_rate_limit_error_basic(self):
        """Test basic rate limit error."""
        error = RateLimitError()
        assert error.message == "Rate limit exceeded"
        assert error.status_code == 429
        assert error.retryable is True
    
    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry_after."""
        error = RateLimitError(retry_after=5)
        assert error.retry_after == 5
        assert "5 seconds" in error.suggested_fix

