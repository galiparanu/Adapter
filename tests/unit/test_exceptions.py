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

