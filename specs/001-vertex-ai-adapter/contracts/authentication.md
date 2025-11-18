# Authentication API Contract

**Component**: Authentication Manager  
**Version**: 1.0.0  
**Date**: 2025-01-27

## Overview

This contract defines the interface for authentication management, supporting multiple GCP authentication methods with priority order.

## Interface: AuthenticationManager

### Class Definition

```python
class AuthenticationManager:
    """Manages GCP authentication with multiple methods and credential caching."""
    
    def __init__(self, config: Optional[VertexConfig] = None) -> None:
        """
        Initialize authentication manager.
        
        Args:
            config: Optional configuration object
        """
```

### Methods

#### authenticate

```python
def authenticate(
    self,
    credentials_path: Optional[str] = None
) -> Credentials:
    """
    Authenticate using available credentials in priority order.
    
    Priority order:
    1. Service account key file (via credentials_path or GOOGLE_APPLICATION_CREDENTIALS)
    2. User credentials (gcloud auth login)
    3. Application Default Credentials (ADC)
    4. Workload Identity (for GKE/Cloud Run)
    
    Args:
        credentials_path: Optional path to service account key file
    
    Returns:
        Valid Credentials object
    
    Raises:
        AuthenticationError: If no valid credentials found
    """
```

#### validate_credentials

```python
def validate_credentials(
    self,
    credentials: Credentials
) -> bool:
    """
    Validate that credentials are valid and not expired.
    
    Args:
        credentials: Credentials object to validate
    
    Returns:
        bool: True if credentials are valid
    
    Raises:
        AuthenticationError: If credentials are invalid and cannot be refreshed
    """
```

#### refresh_credentials

```python
def refresh_credentials(
    self,
    credentials: Credentials
) -> Credentials:
    """
    Refresh expired credentials.
    
    Args:
        credentials: Expired credentials to refresh
    
    Returns:
        Refreshed Credentials object
    
    Raises:
        AuthenticationError: If refresh fails
    """
```

#### get_credentials_path

```python
def get_credentials_path(self) -> Optional[str]:
    """
    Get path to credentials file from environment or config.
    
    Returns:
        Path to credentials file, or None if not found
    """
```

#### clear_cache

```python
def clear_cache(self) -> None:
    """
    Clear cached credentials.
    
    Useful for testing or when credentials need to be reloaded.
    """
```

## Credentials Object

The Credentials object is from Google Auth library with additional attributes:

```python
class CachedCredentials:
    """Wrapper around Google Auth Credentials with caching."""
    
    credentials: Credentials  # Google Auth credentials
    valid: bool
    expired: bool
    expires_at: Optional[datetime]
    last_validated: Optional[datetime]
    cached: bool  # Whether credentials are cached
```

## Error Responses

### AuthenticationError

```json
{
  "error": {
    "type": "AuthenticationError",
    "message": "No valid credentials found",
    "code": "AUTH_001",
    "suggested_fixes": [
      "Run 'gcloud auth login' to authenticate",
      "Set GOOGLE_APPLICATION_CREDENTIALS environment variable",
      "Use service account key file"
    ]
  }
}
```

### InvalidCredentialsError

```json
{
  "error": {
    "type": "InvalidCredentialsError",
    "message": "Service account key file is invalid or corrupted",
    "code": "AUTH_002",
    "file_path": "/path/to/credentials.json",
    "suggested_fix": "Verify service account key file is valid JSON"
  }
}
```

### ExpiredCredentialsError

```json
{
  "error": {
    "type": "ExpiredCredentialsError",
    "message": "Credentials have expired",
    "code": "AUTH_003",
    "expired_at": "2025-01-27T10:00:00Z",
    "suggested_fix": "Credentials will be automatically refreshed"
  }
}
```

### InsufficientPermissionsError

```json
{
  "error": {
    "type": "InsufficientPermissionsError",
    "message": "Service account lacks required permissions",
    "code": "AUTH_004",
    "required_role": "roles/aiplatform.user",
    "suggested_fix": "Grant 'roles/aiplatform.user' role to service account"
  }
}
```

## Implementation Notes

1. **Credential Caching**: Credentials are cached until expiry to reduce API calls
2. **Automatic Refresh**: Expired credentials are automatically refreshed when possible
3. **Priority Order**: Methods are tried in order until valid credentials are found
4. **Security**: Credentials are never logged or exposed in error messages
5. **Validation**: Credentials are validated before use to catch issues early

## Testing Requirements

- Unit tests with mocked credentials
- Integration tests with real GCP authentication
- Test each authentication method independently
- Test credential expiry and refresh
- Test error scenarios (invalid file, expired, insufficient permissions)
- Test credential caching behavior

