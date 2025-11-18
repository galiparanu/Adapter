"""Configuration management for Vertex Spec Adapter."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import ValidationError

from vertex_spec_adapter.core.exceptions import ConfigurationError
from vertex_spec_adapter.schemas.config import VertexConfig


class ConfigurationManager:
    """
    Manages configuration loading, validation, and environment variable overrides.
    
    Supports loading from YAML/JSON files, environment variable overrides,
    and creating default configurations.
    """
    
    DEFAULT_CONFIG_PATH = Path(".specify/config.yaml")
    DEFAULT_PROJECT_ID = "your-project-id"
    DEFAULT_MODEL = "claude-4-5-sonnet"
    DEFAULT_REGION = "us-east5"
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize ConfigurationManager.
        
        Args:
            config_path: Path to configuration file. If None, uses default path.
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config: Optional[VertexConfig] = None
    
    def load_config(self) -> VertexConfig:
        """
        Load configuration from file with environment variable overrides.
        
        Returns:
            Validated VertexConfig instance
            
        Raises:
            ConfigurationError: If config file is invalid or missing required fields
        """
        # Load from file if exists
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    if self.config_path.suffix in [".yaml", ".yml"]:
                        data = yaml.safe_load(f)
                    elif self.config_path.suffix == ".json":
                        data = json.load(f)
                    else:
                        raise ConfigurationError(
                            f"Unsupported config file format: {self.config_path.suffix}. "
                            "Supported formats: .yaml, .yml, .json"
                        )
            except (yaml.YAMLError, json.JSONDecodeError) as e:
                raise ConfigurationError(
                    f"Failed to parse config file {self.config_path}: {e}"
                ) from e
            except OSError as e:
                raise ConfigurationError(
                    f"Failed to read config file {self.config_path}: {e}"
                ) from e
        else:
            # Start with empty dict if file doesn't exist
            data = {}
        
        # Apply environment variable overrides
        data = self._apply_env_overrides(data)
        
        # Validate and create config
        try:
            self._config = VertexConfig(**data)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                msg = error["msg"]
                errors.append(f"{field}: {msg}")
            
            raise ConfigurationError(
                f"Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors),
                suggested_fix=(
                    "Check your configuration file and ensure all required fields are present "
                    "and valid. See docs/configuration.md for details."
                )
            ) from e
        
        return self._config
    
    def validate_config(self, config_data: Optional[Dict] = None) -> VertexConfig:
        """
        Validate configuration data without loading from file.
        
        Args:
            config_data: Configuration dictionary to validate. If None, validates current config.
            
        Returns:
            Validated VertexConfig instance
            
        Raises:
            ConfigurationError: If validation fails
        """
        if config_data is None:
            if self._config is None:
                raise ConfigurationError(
                    "No configuration to validate. Load config first or provide config_data."
                )
            return self._config
        
        # Apply environment variable overrides
        config_data = self._apply_env_overrides(config_data)
        
        try:
            return VertexConfig(**config_data)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                msg = error["msg"]
                errors.append(f"{field}: {msg}")
            
            raise ConfigurationError(
                f"Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors),
                suggested_fix=(
                    "Check your configuration data and ensure all required fields are present "
                    "and valid. See docs/configuration.md for details."
                )
            ) from e
    
    def create_default_config(
        self,
        project_id: Optional[str] = None,
        model: Optional[str] = None,
        region: Optional[str] = None,
        **kwargs
    ) -> VertexConfig:
        """
        Create a default configuration with sensible defaults.
        
        Args:
            project_id: GCP project ID (default: DEFAULT_PROJECT_ID)
            model: Default model (default: DEFAULT_MODEL)
            region: Default region (default: DEFAULT_REGION)
            **kwargs: Additional configuration fields
            
        Returns:
            VertexConfig instance with defaults
        """
        defaults = {
            "project_id": project_id or self.DEFAULT_PROJECT_ID,
            "model": model or self.DEFAULT_MODEL,
            "region": region or self.DEFAULT_REGION,
        }
        
        # Merge with any additional kwargs
        defaults.update(kwargs)
        
        # Apply environment variable overrides
        defaults = self._apply_env_overrides(defaults)
        
        try:
            return VertexConfig(**defaults)
        except ValidationError as e:
            # This shouldn't happen with defaults, but handle it gracefully
            raise ConfigurationError(
                f"Failed to create default configuration: {e}",
                suggested_fix="Check default values in ConfigurationManager"
            ) from e
    
    def save_config(self, config: VertexConfig, path: Optional[Path] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config: VertexConfig instance to save
            path: Path to save config file. If None, uses self.config_path.
            
        Raises:
            ConfigurationError: If save fails
        """
        save_path = path or self.config_path
        
        # Create parent directory if it doesn't exist
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict (exclude None values for cleaner YAML)
        config_dict = config.model_dump(exclude_none=True, exclude_unset=True)
        
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                if save_path.suffix in [".yaml", ".yml"]:
                    yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
                elif save_path.suffix == ".json":
                    json.dump(config_dict, f, indent=2, sort_keys=False)
                else:
                    raise ConfigurationError(
                        f"Unsupported config file format: {save_path.suffix}. "
                        "Supported formats: .yaml, .yml, .json"
                    )
        except OSError as e:
            raise ConfigurationError(
                f"Failed to write config file {save_path}: {e}"
            ) from e
    
    def _apply_env_overrides(self, data: Dict) -> Dict:
        """
        Apply environment variable overrides to configuration data.
        
        Environment variables follow pattern: VERTEX_SPEC_<FIELD_NAME>
        Field names are converted to UPPER_SNAKE_CASE.
        
        Examples:
            VERTEX_SPEC_PROJECT_ID -> project_id
            VERTEX_SPEC_MODEL -> model
            VERTEX_SPEC_MAX_RETRIES -> max_retries
            VERTEX_SPEC_SERVICE_ACCOUNT_PATH -> service_account_path
        
        Args:
            data: Configuration dictionary
            
        Returns:
            Updated configuration dictionary with env overrides
        """
        # Field name mapping (config field -> env var name)
        env_mappings = {
            "project_id": "VERTEX_SPEC_PROJECT_ID",
            "region": "VERTEX_SPEC_REGION",
            "model": "VERTEX_SPEC_MODEL",
            "model_version": "VERTEX_SPEC_MODEL_VERSION",
            "auth_method": "VERTEX_SPEC_AUTH_METHOD",
            "service_account_path": "VERTEX_SPEC_SERVICE_ACCOUNT_PATH",
            "max_retries": "VERTEX_SPEC_MAX_RETRIES",
            "retry_backoff_factor": "VERTEX_SPEC_RETRY_BACKOFF_FACTOR",
            "timeout": "VERTEX_SPEC_TIMEOUT",
            "log_level": "VERTEX_SPEC_LOG_LEVEL",
            "log_format": "VERTEX_SPEC_LOG_FORMAT",
            "log_file": "VERTEX_SPEC_LOG_FILE",
            "enable_cost_tracking": "VERTEX_SPEC_ENABLE_COST_TRACKING",
        }
        
        # Apply environment variable overrides
        for field_name, env_var in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Type conversion based on field type
                if field_name in ["max_retries", "timeout"]:
                    try:
                        data[field_name] = int(env_value)
                    except ValueError:
                        # Skip invalid values, let Pydantic validation catch it
                        pass
                elif field_name in ["retry_backoff_factor"]:
                    try:
                        data[field_name] = float(env_value)
                    except ValueError:
                        pass
                elif field_name in ["enable_cost_tracking"]:
                    # Boolean conversion
                    data[field_name] = env_value.lower() in ("true", "1", "yes", "on")
                else:
                    # String values
                    data[field_name] = env_value
        
        # Handle model_regions as JSON string
        model_regions_env = os.getenv("VERTEX_SPEC_MODEL_REGIONS")
        if model_regions_env:
            try:
                data["model_regions"] = json.loads(model_regions_env)
            except json.JSONDecodeError:
                # Skip invalid JSON, let Pydantic validation catch it
                pass
        
        return data
    
    @property
    def config(self) -> Optional[VertexConfig]:
        """Get current configuration (None if not loaded)."""
        return self._config
    
    def reload(self) -> VertexConfig:
        """
        Reload configuration from file.
        
        Returns:
            Reloaded VertexConfig instance
        """
        self._config = None
        return self.load_config()

