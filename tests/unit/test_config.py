"""Unit tests for ConfigurationManager."""

import json
import os
import tempfile
from pathlib import Path

import pytest
import yaml

from vertex_spec_adapter.core.config import ConfigurationManager
from vertex_spec_adapter.core.exceptions import ConfigurationError
from vertex_spec_adapter.schemas.config import AuthMethod, LogFormat, LogLevel


class TestConfigurationManager:
    """Test ConfigurationManager class."""
    
    def test_create_default_config(self):
        """Test creating default configuration."""
        manager = ConfigurationManager()
        config = manager.create_default_config()
        
        assert config.project_id == "your-project-id"
        assert config.model == "claude-4-5-sonnet"
        assert config.region == "us-east5"
        assert config.auth_method == AuthMethod.AUTO
        assert config.max_retries == 3
        assert config.timeout == 60
    
    def test_create_default_config_with_overrides(self):
        """Test creating default config with custom values."""
        manager = ConfigurationManager()
        config = manager.create_default_config(
            project_id="my-project",
            model="gemini-2-5-pro",
            region="us-central1",
        )
        
        assert config.project_id == "my-project"
        assert config.model == "gemini-2-5-pro"
        assert config.region == "us-central1"
    
    def test_load_config_from_yaml(self, tmp_path):
        """Test loading configuration from YAML file."""
        config_file = tmp_path / "config.yaml"
        config_data = {
            "project_id": "test-project",
            "model": "claude-4-5-sonnet",
            "region": "us-east5",
        }
        
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        manager = ConfigurationManager(config_path=config_file)
        config = manager.load_config()
        
        assert config.project_id == "test-project"
        assert config.model == "claude-4-5-sonnet"
        assert config.region == "us-east5"
    
    def test_load_config_from_json(self, tmp_path):
        """Test loading configuration from JSON file."""
        config_file = tmp_path / "config.json"
        config_data = {
            "project_id": "test-project",
            "model": "gemini-2-5-pro",
            "region": "us-central1",
        }
        
        with open(config_file, "w") as f:
            json.dump(config_data, f)
        
        manager = ConfigurationManager(config_path=config_file)
        config = manager.load_config()
        
        assert config.project_id == "test-project"
        assert config.model == "gemini-2-5-pro"
        assert config.region == "us-central1"
    
    def test_load_config_missing_file(self, tmp_path):
        """Test loading config when file doesn't exist."""
        config_file = tmp_path / "nonexistent.yaml"
        manager = ConfigurationManager(config_path=config_file)
        
        # Should raise ConfigurationError because required fields are missing
        with pytest.raises(ConfigurationError):
            manager.load_config()
    
    def test_load_config_invalid_yaml(self, tmp_path):
        """Test loading config with invalid YAML."""
        config_file = tmp_path / "config.yaml"
        with open(config_file, "w") as f:
            f.write("invalid: yaml: content: [")
        
        manager = ConfigurationManager(config_path=config_file)
        
        with pytest.raises(ConfigurationError) as exc_info:
            manager.load_config()
        
        assert "Failed to parse config file" in str(exc_info.value)
    
    def test_load_config_invalid_json(self, tmp_path):
        """Test loading config with invalid JSON."""
        config_file = tmp_path / "config.json"
        with open(config_file, "w") as f:
            f.write("{ invalid json }")
        
        manager = ConfigurationManager(config_path=config_file)
        
        with pytest.raises(ConfigurationError) as exc_info:
            manager.load_config()
        
        assert "Failed to parse config file" in str(exc_info.value)
    
    def test_validate_config_valid(self):
        """Test validating valid configuration."""
        manager = ConfigurationManager()
        config_data = {
            "project_id": "test-project",
            "model": "claude-4-5-sonnet",
        }
        
        config = manager.validate_config(config_data)
        assert config.project_id == "test-project"
        assert config.model == "claude-4-5-sonnet"
    
    def test_validate_config_invalid_project_id(self):
        """Test validating config with invalid project ID."""
        manager = ConfigurationManager()
        config_data = {
            "project_id": "INVALID-PROJECT-ID",  # Invalid format
            "model": "claude-4-5-sonnet",
        }
        
        with pytest.raises(ConfigurationError) as exc_info:
            manager.validate_config(config_data)
        
        assert "Configuration validation failed" in str(exc_info.value)
    
    def test_validate_config_missing_required(self):
        """Test validating config with missing required fields."""
        manager = ConfigurationManager()
        config_data = {
            "project_id": "test-project",
            # Missing required 'model' field
        }
        
        with pytest.raises(ConfigurationError) as exc_info:
            manager.validate_config(config_data)
        
        assert "Configuration validation failed" in str(exc_info.value)
    
    def test_save_config_yaml(self, tmp_path):
        """Test saving configuration to YAML file."""
        config_file = tmp_path / "config.yaml"
        manager = ConfigurationManager(config_path=config_file)
        config = manager.create_default_config(
            project_id="test-project",
            model="claude-4-5-sonnet",
        )
        
        manager.save_config(config)
        
        assert config_file.exists()
        with open(config_file) as f:
            loaded = yaml.safe_load(f)
        
        assert loaded["project_id"] == "test-project"
        assert loaded["model"] == "claude-4-5-sonnet"
    
    def test_save_config_json(self, tmp_path):
        """Test saving configuration to JSON file."""
        config_file = tmp_path / "config.json"
        manager = ConfigurationManager(config_path=config_file)
        config = manager.create_default_config(
            project_id="test-project",
            model="gemini-2-5-pro",
        )
        
        manager.save_config(config)
        
        assert config_file.exists()
        with open(config_file) as f:
            loaded = json.load(f)
        
        assert loaded["project_id"] == "test-project"
        assert loaded["model"] == "gemini-2-5-pro"
    
    def test_save_config_creates_directory(self, tmp_path):
        """Test that save_config creates parent directory if needed."""
        config_file = tmp_path / "subdir" / "config.yaml"
        manager = ConfigurationManager(config_path=config_file)
        config = manager.create_default_config()
        
        manager.save_config(config)
        
        assert config_file.exists()
        assert config_file.parent.exists()
    
    def test_environment_variable_overrides(self, tmp_path, monkeypatch):
        """Test environment variable overrides."""
        config_file = tmp_path / "config.yaml"
        config_data = {
            "project_id": "file-project",
            "model": "file-model",
        }
        
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        # Set environment variables
        monkeypatch.setenv("VERTEX_SPEC_PROJECT_ID", "env-project")
        monkeypatch.setenv("VERTEX_SPEC_MODEL", "env-model")
        monkeypatch.setenv("VERTEX_SPEC_MAX_RETRIES", "5")
        monkeypatch.setenv("VERTEX_SPEC_ENABLE_COST_TRACKING", "false")
        
        manager = ConfigurationManager(config_path=config_file)
        
        # Should raise error because env overrides still need valid config
        # But we can test that env vars are applied
        with pytest.raises(ConfigurationError):
            # This will fail because env-project might not match project_id pattern
            manager.load_config()
        
        # Test with valid env values
        monkeypatch.setenv("VERTEX_SPEC_PROJECT_ID", "valid-project-id")
        config = manager.load_config()
        
        assert config.project_id == "valid-project-id"
        assert config.model == "env-model"
        assert config.max_retries == 5
        assert config.enable_cost_tracking is False
    
    def test_environment_variable_type_conversion(self, tmp_path, monkeypatch):
        """Test environment variable type conversion."""
        config_file = tmp_path / "config.yaml"
        config_data = {
            "project_id": "test-project",
            "model": "claude-4-5-sonnet",
        }
        
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        monkeypatch.setenv("VERTEX_SPEC_MAX_RETRIES", "5")
        monkeypatch.setenv("VERTEX_SPEC_TIMEOUT", "120")
        monkeypatch.setenv("VERTEX_SPEC_RETRY_BACKOFF_FACTOR", "2.5")
        
        manager = ConfigurationManager(config_path=config_file)
        config = manager.load_config()
        
        assert config.max_retries == 5
        assert config.timeout == 120
        assert config.retry_backoff_factor == 2.5
    
    def test_reload_config(self, tmp_path):
        """Test reloading configuration."""
        config_file = tmp_path / "config.yaml"
        config_data = {
            "project_id": "test-project",
            "model": "claude-4-5-sonnet",
        }
        
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        manager = ConfigurationManager(config_path=config_file)
        config1 = manager.load_config()
        
        # Modify file
        config_data["model"] = "gemini-2-5-pro"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        # Reload
        config2 = manager.reload()
        
        assert config1.model == "claude-4-5-sonnet"
        assert config2.model == "gemini-2-5-pro"
    
    def test_config_property(self):
        """Test config property access."""
        manager = ConfigurationManager()
        
        # Initially None
        assert manager.config is None
        
        # After loading
        config = manager.create_default_config()
        manager._config = config
        
        assert manager.config == config

