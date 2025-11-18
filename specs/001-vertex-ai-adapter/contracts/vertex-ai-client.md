# Vertex AI Client API Contract

**Component**: Core API Client  
**Version**: 1.0.0  
**Date**: 2025-01-27

## Overview

This contract defines the interface for the unified Vertex AI client that supports both MaaS (Model-as-a-Service) REST API and Native SDK access patterns.

## Interface: VertexAIClient

### Class Definition

```python
class VertexAIClient:
    """Unified client for Vertex AI models supporting both MaaS and Native SDK patterns."""
    
    def __init__(
        self,
        project_id: str,
        region: str,
        model_id: str,
        model_version: Optional[str] = None,
        credentials: Optional[Credentials] = None,
        config: Optional[VertexConfig] = None
    ) -> None:
        """
        Initialize Vertex AI client.
        
        Args:
            project_id: GCP project ID
            region: GCP region
            model_id: Model identifier (e.g., 'claude-4-5-sonnet')
            model_version: Optional model version to pin
            credentials: Optional credentials (uses ADC if not provided)
            config: Optional configuration object
        """
```

### Methods

#### generate

```python
def generate(
    self,
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False
) -> Union[str, Iterator[str]]:
    """
    Generate text using the configured model.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate
        stream: Whether to stream response
    
    Returns:
        str if stream=False, Iterator[str] if stream=True
    
    Raises:
        AuthenticationError: If credentials are invalid
        ModelNotFoundError: If model is not available in region
        APIError: For API-related errors
        RateLimitError: If rate limit exceeded
    """
```

**Request Format**:
```json
{
  "messages": [
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "temperature": 1.0,
  "max_tokens": 4096,
  "stream": false
}
```

**Response Format (non-streaming)**:
```json
{
  "content": "I'm doing well, thank you!",
  "input_tokens": 10,
  "output_tokens": 15,
  "total_tokens": 25,
  "model": "claude-4-5-sonnet@20250929",
  "finish_reason": "stop",
  "latency_ms": 450.5
}
```

**Response Format (streaming)**:
Iterator of strings, each containing a chunk of the response.

#### generate_stream

```python
def generate_stream(
    self,
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> Iterator[str]:
    """
    Generate text with streaming response.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate
    
    Yields:
        str: Chunks of generated text
    
    Raises:
        Same as generate()
    """
```

#### get_available_models

```python
@classmethod
def get_available_models(
    cls,
    project_id: str,
    region: str,
    use_cache: bool = True
) -> List[Dict[str, Any]]:
    """
    Get list of available models in the specified region.
    
    Args:
        project_id: GCP project ID
        region: GCP region
        use_cache: Whether to use cached results (TTL: 1 hour)
    
    Returns:
        List of model dicts with 'id', 'name', 'provider', 'access_pattern'
    
    Raises:
        AuthenticationError: If credentials are invalid
        APIError: For API-related errors
    """
```

**Response Format**:
```json
[
  {
    "id": "claude-4-5-sonnet",
    "name": "Claude 4.5 Sonnet",
    "provider": "anthropic",
    "access_pattern": "native_sdk",
    "available_regions": ["us-east5", "europe-west1"],
    "latest_version": "@20250929"
  },
  {
    "id": "gemini-2-5-pro",
    "name": "Gemini 2.5 Pro",
    "provider": "google",
    "access_pattern": "native_sdk",
    "available_regions": ["us-central1"],
    "latest_version": "latest"
  },
  {
    "id": "qwen-coder",
    "name": "Qwen Coder",
    "provider": "qwen",
    "access_pattern": "maas",
    "available_regions": ["us-south1"],
    "latest_version": "@20241022"
  }
]
```

#### validate_model_availability

```python
def validate_model_availability(
    self,
    model_id: str,
    region: str
) -> bool:
    """
    Validate that a model is available in the specified region.
    
    Args:
        model_id: Model identifier
        region: GCP region
    
    Returns:
        bool: True if model is available
    
    Raises:
        ModelNotFoundError: If model is not available with details
    """
```

#### get_token_usage

```python
@property
def token_usage(self) -> Dict[str, int]:
    """
    Get cumulative token usage for this client instance.
    
    Returns:
        Dict with 'input_tokens', 'output_tokens', 'total_tokens'
    """
```

## Error Responses

### AuthenticationError

```json
{
  "error": {
    "type": "AuthenticationError",
    "message": "Invalid credentials. Run 'gcloud auth login' or set GOOGLE_APPLICATION_CREDENTIALS",
    "code": 401,
    "suggested_fix": "gcloud auth login"
  }
}
```

### ModelNotFoundError

```json
{
  "error": {
    "type": "ModelNotFoundError",
    "message": "Model 'claude-4-5-sonnet' not available in 'us-west1'",
    "code": 404,
    "available_regions": ["us-east5", "europe-west1"],
    "suggested_fix": "Use region 'us-east5' or 'europe-west1'"
  }
}
```

### RateLimitError

```json
{
  "error": {
    "type": "RateLimitError",
    "message": "Rate limit exceeded",
    "code": 429,
    "retry_after": 5,
    "suggested_fix": "Wait 5 seconds and retry"
  }
}
```

### APIError

```json
{
  "error": {
    "type": "APIError",
    "message": "Internal server error",
    "code": 500,
    "retryable": true,
    "suggested_fix": "Retry after a few seconds"
  }
}
```

## Implementation Notes

1. **Access Pattern Detection**: Client automatically detects whether to use MaaS or Native SDK based on model ID
2. **Retry Logic**: Automatic retry with exponential backoff for transient errors (429, 500, 502, 503, 504)
3. **Circuit Breaker**: Prevents cascading failures after repeated errors
4. **Token Tracking**: All requests track token usage for cost estimation
5. **Response Normalization**: Different model responses are normalized to common format

## Testing Requirements

- Unit tests with mocked API responses
- Integration tests with VCR.py recorded interactions
- Error scenario tests (401, 404, 429, 500)
- Streaming response tests
- Token counting accuracy tests
- Performance tests (<500ms overhead)

