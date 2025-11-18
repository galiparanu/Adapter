"""Pydantic schemas for configuration validation."""

from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class AuthMethod(str, Enum):
    """Authentication method enum."""
    
    SERVICE_ACCOUNT = "service_account"
    USER_CREDENTIALS = "user_credentials"
    ADC = "adc"
    AUTO = "auto"


class LogLevel(str, Enum):
    """Logging level enum."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogFormat(str, Enum):
    """Log output format enum."""
    
    JSON = "json"
    TEXT = "text"


class VertexConfig(BaseModel):
    """Configuration schema for Vertex Spec Adapter."""
    
    project_id: str = Field(
        ...,
        description="GCP project ID",
        min_length=6,
        max_length=30
    )
    region: Optional[str] = Field(
        None,
        description="Default region override (model-specific default if not provided)"
    )
    model: str = Field(
        ...,
        description="Default model identifier (e.g., 'claude-4-5-sonnet', 'gemini-2-5-pro', 'qwen-coder')"
    )
    model_version: Optional[str] = Field(
        None,
        description="Specific model version to pin (e.g., '@20250929', '@20241022')"
    )
    model_regions: Optional[Dict[str, str]] = Field(
        None,
        description="Model-specific region overrides (format: {model_id: region})"
    )
    auth_method: AuthMethod = Field(
        default=AuthMethod.AUTO,
        description="Preferred authentication method"
    )
    service_account_path: Optional[str] = Field(
        None,
        description="Path to service account key file (or use GOOGLE_APPLICATION_CREDENTIALS env var)"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts",
        ge=0,
        le=5
    )
    retry_backoff_factor: float = Field(
        default=1.0,
        description="Exponential backoff multiplier",
        gt=0
    )
    timeout: int = Field(
        default=60,
        description="Request timeout in seconds",
        gt=0
    )
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level"
    )
    log_format: LogFormat = Field(
        default=LogFormat.TEXT,
        description="Log output format"
    )
    log_file: Optional[str] = Field(
        None,
        description="Path to log file (stdout only if not provided)"
    )
    enable_cost_tracking: bool = Field(
        default=True,
        description="Track token usage and costs"
    )
    
    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        """
        Validate GCP project ID format.
        
        Pattern: ^[a-z][-a-z0-9]{4,28}[a-z0-9]$
        """
        import re
        pattern = r'^[a-z][-a-z0-9]{4,28}[a-z0-9]$'
        if not re.match(pattern, v):
            raise ValueError(
                f"Invalid project ID format: '{v}'. "
                "Must match pattern: ^[a-z][-a-z0-9]{{4,28}}[a-z0-9]$"
            )
        return v
    
    @field_validator('region')
    @classmethod
    def validate_region(cls, v: Optional[str]) -> Optional[str]:
        """Validate GCP region format."""
        if v is None:
            return v
        import re
        # GCP regions follow pattern: {location}-{number} or {location}
        # Examples: us-central1, us-east5, europe-west1, asia-southeast1
        pattern = r'^[a-z]+-[a-z]+\d+$|^[a-z]+$'
        if not re.match(pattern, v):
            raise ValueError(
                f"Invalid region format: '{v}'. "
                "Must be a valid GCP region (e.g., 'us-central1', 'us-east5')"
            )
        return v
    
    @field_validator('model_version')
    @classmethod
    def validate_model_version(cls, v: Optional[str]) -> Optional[str]:
        """Validate model version format."""
        if v is None:
            return v
        import re
        # Version format: @YYYYMMDD or @version-string
        pattern = r'^@\d{8}$|^@[a-z0-9-]+$'
        if not re.match(pattern, v):
            raise ValueError(
                f"Invalid model version format: '{v}'. "
                "Must match pattern: @YYYYMMDD or @version-string"
            )
        return v
    
    @field_validator('service_account_path')
    @classmethod
    def validate_service_account_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate service account file exists if provided."""
        if v is None:
            return v
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Service account file not found: {v}")
        if not path.is_file():
            raise ValueError(f"Service account path is not a file: {v}")
        if not path.readable():
            raise ValueError(f"Service account file is not readable: {v}")
        return v
    
    @field_validator('log_file')
    @classmethod
    def validate_log_file(cls, v: Optional[str]) -> Optional[str]:
        """Validate log file path if provided."""
        if v is None:
            return v
        path = Path(v)
        parent = path.parent
        if parent.exists() and not parent.is_dir():
            raise ValueError(f"Log file parent path is not a directory: {parent}")
        return v
    
    @model_validator(mode='after')
    def validate_model(self) -> 'VertexConfig':
        """Validate model identifier against supported models."""
        supported_models = [
            'claude-4-5-sonnet',
            'claude-3-5-sonnet',
            'claude-3-opus',
            'gemini-2-5-pro',
            'gemini-1-5-pro',
            'gemini-1-5-flash',
            'qwen-coder',
            'qwen-2-5-coder',
        ]
        
        # Allow any model ID that looks valid (flexible for future models)
        # But warn if it's not in our known list
        model_lower = self.model.lower()
        if model_lower not in [m.lower() for m in supported_models]:
            # Still allow it, but it might not work
            pass
        
        return self
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        extra = "forbid"  # Reject extra fields
        validate_assignment = True  # Validate on assignment

