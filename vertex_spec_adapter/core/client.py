"""Vertex AI client for unified model access."""

import time
from datetime import datetime
from typing import Dict, Iterator, List, Optional, Union

from vertex_spec_adapter.core.auth import AuthenticationManager
from vertex_spec_adapter.core.exceptions import (
    APIError,
    AuthenticationError,
    ModelNotFoundError,
    RateLimitError,
)
from vertex_spec_adapter.core.models import ModelRegistry
from vertex_spec_adapter.schemas.api import APIResponse, Message, ModelRequest
from vertex_spec_adapter.schemas.config import VertexConfig
from vertex_spec_adapter.utils.logging import get_logger, log_api_call
from vertex_spec_adapter.utils.metrics import UsageTracker
from vertex_spec_adapter.utils.retry import CircuitBreaker, retry_with_backoff

logger = get_logger(__name__)


class VertexAIClient:
    """
    Unified client for Vertex AI models supporting both MaaS and Native SDK patterns.
    
    Supports:
    - Claude models via anthropic[vertex] SDK
    - Gemini models via google-cloud-aiplatform SDK
    - Qwen models via MaaS REST API
    """
    
    # Model access pattern mapping
    MODEL_ACCESS_PATTERNS = {
        # Claude models - Native SDK
        "claude-4-5-sonnet": "native_sdk",
        "claude-3-5-sonnet": "native_sdk",
        "claude-3-opus": "native_sdk",
        # Gemini models - Native SDK
        "gemini-2-5-pro": "native_sdk",
        "gemini-1-5-pro": "native_sdk",
        "gemini-1-5-flash": "native_sdk",
        # Qwen models - MaaS REST API
        "qwen-coder": "maas",
        "qwen-2-5-coder": "maas",
    }
    
    def __init__(
        self,
        project_id: str,
        region: str,
        model_id: str,
        model_version: Optional[str] = None,
        credentials=None,
        config: Optional[VertexConfig] = None,
        usage_tracker: Optional[UsageTracker] = None,
    ):
        """
        Initialize Vertex AI client.
        
        Args:
            project_id: GCP project ID
            region: GCP region
            model_id: Model identifier (e.g., 'claude-4-5-sonnet')
            model_version: Optional model version to pin
            credentials: Optional credentials (uses AuthenticationManager if not provided)
            config: Optional configuration object
            usage_tracker: Optional usage tracker for metrics
        """
        self.project_id = project_id
        self.region = region
        self.model_id = model_id.lower()
        self.model_version = model_version
        self.config = config
        self.usage_tracker = usage_tracker or UsageTracker()
        self.model_registry = ModelRegistry()
        
        # Validate model availability
        self.model_registry.validate_model_availability(self.model_id, self.region)
        
        # Determine access pattern
        self.access_pattern = self.model_registry.detect_access_pattern(self.model_id)
        
        # Initialize authentication
        if credentials:
            self.credentials = credentials
        else:
            auth_manager = AuthenticationManager(config=config)
            self.credentials = auth_manager.authenticate()
        
        # Initialize model-specific client
        self._model_client = self._initialize_model_client()
        
        # Initialize circuit breaker
        failure_threshold = config.max_retries if config else 5
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=60,
            expected_exception=APIError,
        )
        
        # Token usage tracking
        self._token_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }
        
        logger.info(
            "VertexAIClient initialized",
            model=self.model_id,
            region=self.region,
            access_pattern=self.access_pattern,
        )
    
    def switch_model(
        self,
        new_model_id: str,
        new_region: Optional[str] = None,
        new_model_version: Optional[str] = None,
    ) -> None:
        """
        Switch to a different model.
        
        Args:
            new_model_id: New model identifier
            new_region: Optional new region (uses model default if not provided)
            new_model_version: Optional new model version
        
        Raises:
            ModelNotFoundError: If model is not available
        """
        new_model_id_lower = new_model_id.lower()
        
        # Get model metadata
        metadata = self.model_registry.get_model_metadata(new_model_id_lower)
        if not metadata:
            raise ModelNotFoundError(
                f"Model '{new_model_id}' not found",
                model_id=new_model_id,
                region=new_region or "unknown",
            )
        
        # Determine region
        if new_region:
            # Validate region
            self.model_registry.validate_model_availability(new_model_id_lower, new_region)
            region = new_region
        else:
            # Use model default region
            region = metadata.default_region or self.region
        
        # Determine version
        if new_model_version:
            # Validate version
            self.model_registry.validate_version(new_model_id_lower, new_model_version)
            version = new_model_version
        else:
            # Use latest version
            version = metadata.latest_version
        
        # Update client state
        old_model = self.model_id
        self.model_id = new_model_id_lower
        self.region = region
        self.model_version = version
        self.access_pattern = metadata.access_pattern
        
        # Reinitialize model client
        self._model_client = self._initialize_model_client()
        
        logger.info(
            "Model switched",
            old_model=old_model,
            new_model=self.model_id,
            region=self.region,
            version=self.model_version,
        )
    
    def _initialize_model_client(self):
        """Initialize model-specific client based on access pattern."""
        if self.access_pattern == "native_sdk":
            if self.model_id.startswith("claude"):
                return self._init_claude_client()
            elif self.model_id.startswith("gemini"):
                return self._init_gemini_client()
        elif self.access_pattern == "maas":
            if self.model_id.startswith("qwen"):
                return self._init_qwen_client()
        
        raise ModelNotFoundError(
            f"Unsupported model: {self.model_id}",
            model_id=self.model_id,
            region=self.region,
        )
    
    def _init_claude_client(self):
        """Initialize Claude client via anthropic[vertex] SDK."""
        try:
            from anthropic import AnthropicVertex
            
            # Build model name with version if specified
            model_name = self.model_id
            if self.model_version:
                model_name = f"{model_name}{self.model_version}"
            
            client = AnthropicVertex(
                project_id=self.project_id,
                region=self.region,
                credentials=self.credentials,
            )
            
            return {"type": "claude", "client": client, "model_name": model_name}
        except ImportError:
            raise APIError(
                "anthropic[vertex] SDK not installed. "
                "Install with: pip install 'anthropic[vertex]'",
                suggested_fix="pip install 'anthropic[vertex]'"
            )
    
    def _init_gemini_client(self):
        """Initialize Gemini client via google-cloud-aiplatform SDK."""
        try:
            import google.cloud.aiplatform as aiplatform
            
            # Initialize Vertex AI
            aiplatform.init(
                project=self.project_id,
                location=self.region,
                credentials=self.credentials,
            )
            
            # Build model name
            model_name = self.model_id
            if self.model_version:
                model_name = f"{model_name}{self.model_version}"
            
            return {"type": "gemini", "model_name": model_name}
        except ImportError:
            raise APIError(
                "google-cloud-aiplatform SDK not installed. "
                "Install with: pip install google-cloud-aiplatform",
                suggested_fix="pip install google-cloud-aiplatform"
            )
    
    def _init_qwen_client(self):
        """Initialize Qwen client via MaaS REST API."""
        # MaaS REST API client will be implemented here
        # For now, return a placeholder structure
        return {
            "type": "qwen",
            "endpoint": f"https://{self.region}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.region}/publishers/qwen/models/{self.model_id}:predict",
            "credentials": self.credentials,
        }
    
    @retry_with_backoff(max_retries=3)
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
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
        start_time = time.time()
        
        try:
            if stream:
                return self._generate_stream(messages, temperature, max_tokens)
            
            # Normalize messages
            normalized_messages = self._normalize_messages(messages)
            
            # Use default temperature from config if not provided
            if temperature is None and self.config:
                temperature = 1.0  # Default
            
            # Generate with circuit breaker protection
            def _generate():
                if self._model_client["type"] == "claude":
                    return self._generate_claude(normalized_messages, temperature, max_tokens)
                elif self._model_client["type"] == "gemini":
                    return self._generate_gemini(normalized_messages, temperature, max_tokens)
                elif self._model_client["type"] == "qwen":
                    return self._generate_qwen(normalized_messages, temperature, max_tokens)
                else:
                    raise APIError(f"Unsupported model type: {self._model_client['type']}")
            
            # Execute with circuit breaker
            response = self.circuit_breaker.call(_generate)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Track usage
            self._track_usage(response, latency_ms)
            
            return response.content
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._handle_error(e, latency_ms)
            raise
    
    def _generate_claude(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
    ) -> APIResponse:
        """Generate using Claude model."""
        client = self._model_client["client"]
        model_name = self._model_client["model_name"]
        
        # Convert messages to Claude format
        claude_messages = []
        system_message = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })
        
        # Prepare parameters
        params = {
            "model": model_name,
            "messages": claude_messages,
            "temperature": temperature,
        }
        if system_message:
            params["system"] = system_message
        if max_tokens:
            params["max_tokens"] = max_tokens
        
        # Make API call
        response = client.messages.create(**params)
        
        # Normalize response
        return APIResponse(
            content=response.content[0].text if response.content else "",
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model=model_name,
            finish_reason=response.stop_reason,
            metadata={"claude_response": response.model_dump()},
        )
    
    def _generate_gemini(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
    ) -> APIResponse:
        """Generate using Gemini model."""
        try:
            from vertexai.generative_models import GenerativeModel, Part
            
            model_name = self._model_client["model_name"]
            model = GenerativeModel(model_name)
            
            # Convert messages to Gemini format
            contents = []
            for msg in messages:
                contents.append({
                    "role": msg["role"],
                    "parts": [{"text": msg["content"]}],
                })
            
            # Generate
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = model.generate_content(
                contents=contents,
                generation_config=generation_config,
            )
            
            # Normalize response
            return APIResponse(
                content=response.text if response.text else "",
                input_tokens=getattr(response.usage_metadata, "prompt_token_count", 0),
                output_tokens=getattr(response.usage_metadata, "completion_token_count", 0),
                model=model_name,
                finish_reason=response.candidates[0].finish_reason if response.candidates else None,
                metadata={"gemini_response": str(response)},
            )
        except Exception as e:
            raise APIError(f"Gemini generation failed: {e}") from e
    
    def _generate_qwen(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
    ) -> APIResponse:
        """Generate using Qwen model via MaaS REST API."""
        # TODO: Implement MaaS REST API call
        # This is a placeholder implementation
        raise APIError(
            "Qwen MaaS REST API not yet implemented",
            suggested_fix="Qwen support will be available in a future update"
        )
    
    def _generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> Iterator[str]:
        """Generate with streaming response."""
        # TODO: Implement streaming
        # For now, return non-streaming result as iterator
        result = self.generate(messages, temperature, max_tokens, stream=False)
        yield result
    
    def _normalize_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Normalize messages to standard format."""
        normalized = []
        for msg in messages:
            role = msg.get("role", "user").lower()
            content = msg.get("content", "")
            if content:
                normalized.append({"role": role, "content": content})
        return normalized
    
    def _track_usage(self, response: APIResponse, latency_ms: float) -> None:
        """Track token usage and metrics."""
        # Update internal tracking
        self._token_usage["input_tokens"] += response.input_tokens
        self._token_usage["output_tokens"] += response.output_tokens
        self._token_usage["total_tokens"] += response.total_tokens
        
        # Track in usage tracker
        self.usage_tracker.track_request(
            model=self.model_id,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=latency_ms,
        )
        
        # Log API call
        log_api_call(
            model=self.model_id,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=latency_ms,
            success=True,
        )
    
    def _handle_error(self, error: Exception, latency_ms: float) -> None:
        """Handle errors and track them."""
        error_msg = str(error)
        
        # Track error in usage tracker
        self.usage_tracker.track_request(
            model=self.model_id,
            input_tokens=0,
            output_tokens=0,
            latency_ms=latency_ms,
            error=error,
        )
        
        # Log API call failure
        log_api_call(
            model=self.model_id,
            input_tokens=0,
            output_tokens=0,
            latency_ms=latency_ms,
            success=False,
            error=error_msg,
        )
    
    @property
    def token_usage(self) -> Dict[str, int]:
        """
        Get cumulative token usage for this client instance.
        
        Returns:
            Dict with 'input_tokens', 'output_tokens', 'total_tokens'
        """
        return self._token_usage.copy()
    
    def validate_model_availability(self, model_id: str, region: str) -> bool:
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
        return self.model_registry.validate_model_availability(model_id, region)

