"""Pydantic schemas for API requests and responses."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, computed_field


class AccessPattern(str, Enum):
    """Model access pattern enum."""
    
    MAAS = "maas"  # Model-as-a-Service REST API
    NATIVE_SDK = "native_sdk"  # Native SDK


class MessageRole(str, Enum):
    """Message role enum."""
    
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class FinishReason(str, Enum):
    """Finish reason enum."""
    
    STOP = "stop"
    LENGTH = "length"
    CONTENT_FILTER = "content_filter"
    ERROR = "error"


class Message(BaseModel):
    """Message schema for conversation."""
    
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content", min_length=1)
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class ModelRequest(BaseModel):
    """Model request schema."""
    
    model_id: str = Field(..., description="Model identifier (e.g., 'claude-4-5-sonnet')")
    model_version: Optional[str] = Field(
        None,
        description="Specific version to use (e.g., '@20250929')"
    )
    region: str = Field(..., description="GCP region for the request")
    access_pattern: AccessPattern = Field(..., description="How to access the model")
    messages: List[Message] = Field(..., description="Conversation messages", min_length=1)
    temperature: float = Field(
        default=1.0,
        description="Sampling temperature",
        ge=0.0,
        le=2.0
    )
    max_tokens: Optional[int] = Field(
        None,
        description="Maximum tokens to generate",
        gt=0
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream response"
    )
    project_id: str = Field(..., description="GCP project ID")
    
    @field_validator('model_version')
    @classmethod
    def validate_model_version(cls, v: Optional[str]) -> Optional[str]:
        """Validate model version format."""
        if v is None:
            return v
        import re
        pattern = r'^@\d{8}$|^@[a-z0-9-]+$'
        if not re.match(pattern, v):
            raise ValueError(
                f"Invalid model version format: '{v}'. "
                "Must match pattern: @YYYYMMDD or @version-string"
            )
        return v
    
    @field_validator('region')
    @classmethod
    def validate_region(cls, v: str) -> str:
        """Validate GCP region format."""
        import re
        pattern = r'^[a-z]+-[a-z]+\d+$|^[a-z]+$'
        if not re.match(pattern, v):
            raise ValueError(
                f"Invalid region format: '{v}'. "
                "Must be a valid GCP region (e.g., 'us-central1', 'us-east5')"
            )
        return v
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        extra = "forbid"


class APIResponse(BaseModel):
    """API response schema with normalized format."""
    
    content: str = Field(..., description="Generated text content")
    input_tokens: int = Field(..., description="Number of input tokens used", ge=0)
    output_tokens: int = Field(..., description="Number of output tokens generated", ge=0)
    model: str = Field(..., description="Model identifier used")
    finish_reason: Optional[FinishReason] = Field(
        None,
        description="Why generation stopped"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional response metadata (model-specific)"
    )
    error: Optional[Dict[str, Any]] = Field(
        None,
        description="Error information if request failed"
    )
    latency_ms: Optional[float] = Field(
        None,
        description="Request latency in milliseconds",
        ge=0
    )
    
    @computed_field
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens (input + output)."""
        return self.input_tokens + self.output_tokens
    
    @field_validator('error')
    @classmethod
    def validate_error(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate error structure if present."""
        if v is None:
            return v
        if not isinstance(v, dict):
            raise ValueError("Error must be a dictionary")
        if 'code' not in v or 'message' not in v:
            raise ValueError("Error must contain 'code' and 'message' fields")
        return v
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        extra = "forbid"

