"""Custom exception hierarchy for Vertex Spec Adapter."""

from typing import Optional


class VertexSpecAdapterError(Exception):
    """Base exception for all Vertex Spec Adapter errors."""
    
    def __init__(self, message: str, suggested_fix: Optional[str] = None):
        """
        Initialize base exception.
        
        Args:
            message: Error message
            suggested_fix: Optional suggested fix for the error
        """
        super().__init__(message)
        self.message = message
        self.suggested_fix = suggested_fix
    
    def __str__(self) -> str:
        """Return formatted error message with suggested fix if available."""
        if self.suggested_fix:
            return f"{self.message}\n  → {self.suggested_fix}"
        return self.message


class AuthenticationError(VertexSpecAdapterError):
    """Authentication-related errors."""
    
    def __init__(
        self,
        message: str,
        suggested_fix: Optional[str] = None,
        code: Optional[str] = None
    ):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
            suggested_fix: Optional suggested fix
            code: Optional error code (e.g., 'AUTH_001')
        """
        super().__init__(message, suggested_fix)
        self.code = code


class ConfigurationError(VertexSpecAdapterError):
    """Configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        suggested_fix: Optional[str] = None
    ):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            field: Optional field name that caused the error
            suggested_fix: Optional suggested fix
        """
        super().__init__(message, suggested_fix)
        self.field = field


class APIError(VertexSpecAdapterError):
    """API call errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        retry_after: Optional[int] = None,
        retryable: bool = False,
        suggested_fix: Optional[str] = None
    ):
        """
        Initialize API error.
        
        Args:
            message: Error message
            status_code: Optional HTTP status code
            retry_after: Optional seconds to wait before retry
            retryable: Whether the error is retryable
            suggested_fix: Optional suggested fix
        """
        super().__init__(message, suggested_fix)
        self.status_code = status_code
        self.retry_after = retry_after
        self.retryable = retryable


class ModelNotFoundError(APIError):
    """Model not available error."""
    
    def __init__(
        self,
        message: str,
        model_id: str,
        region: str,
        available_regions: Optional[list] = None,
        suggested_fix: Optional[str] = None
    ):
        """
        Initialize model not found error.
        
        Args:
            message: Error message
            model_id: Model identifier that was not found
            region: Region where model was requested
            available_regions: Optional list of regions where model is available
            suggested_fix: Optional suggested fix
        """
        if not suggested_fix and available_regions:
            suggested_fix = f"Use one of these regions: {', '.join(available_regions)}"
        super().__init__(message, status_code=404, suggested_fix=suggested_fix)
        self.model_id = model_id
        self.region = region
        self.available_regions = available_regions or []


class QuotaExceededError(APIError):
    """Quota exceeded error."""
    
    def __init__(
        self,
        message: str = "Quota exceeded",
        retry_after: Optional[int] = None,
        suggested_fix: Optional[str] = None
    ):
        """
        Initialize quota exceeded error.
        
        Args:
            message: Error message
            retry_after: Optional seconds to wait before retry
            suggested_fix: Optional suggested fix
        """
        if not suggested_fix:
            if retry_after:
                suggested_fix = f"Wait {retry_after} seconds and retry, or check GCP console for quota limits"
            else:
                suggested_fix = "Check GCP console for quota limits or wait before retrying"
        super().__init__(message, status_code=429, retry_after=retry_after, retryable=True, suggested_fix=suggested_fix)


class RateLimitError(APIError):
    """Rate limit exceeded error."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        suggested_fix: Optional[str] = None
    ):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Optional seconds to wait before retry
            suggested_fix: Optional suggested fix
        """
        if not suggested_fix:
            if retry_after:
                suggested_fix = f"Wait {retry_after} seconds and retry"
            else:
                suggested_fix = "Wait a few seconds and retry"
        super().__init__(message, status_code=429, retry_after=retry_after, retryable=True, suggested_fix=suggested_fix)

