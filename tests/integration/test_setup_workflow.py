"""Integration tests for complete setup workflow."""

import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from vertex_spec_adapter.core.config import ConfigurationManager


@pytest.mark.integration
class TestSetupWorkflow:
    """Integration tests for complete setup workflow."""
    
    def test_complete_setup_workflow(self, tmp_path):
        """
        Test complete setup workflow:
        1. Initialize project
        2. Create configuration
        3. Validate configuration
        4. Test connection
        """
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        
        config_dir = project_dir / ".specify"
        config_file = config_dir / "config.yaml"
        
        # Step 1: Create configuration
        manager = ConfigurationManager(config_path=config_file)
        config = manager.create_default_config(
            project_id="test-project-id",
            model="claude-4-5-sonnet",
            region="us-east5",
        )
        
        # Step 2: Save configuration
        manager.save_config(config)
        assert config_file.exists()
        
        # Step 3: Load and validate configuration
        loaded_config = manager.load_config()
        assert loaded_config.project_id == "test-project-id"
        assert loaded_config.model == "claude-4-5-sonnet"
        assert loaded_config.region == "us-east5"
        
        # Step 4: Validate configuration
        validated_config = manager.validate_config(loaded_config.model_dump())
        assert validated_config.project_id == "test-project-id"
    
    def test_config_file_roundtrip(self, tmp_path):
        """Test saving and loading configuration maintains all fields."""
        config_file = tmp_path / "config.yaml"
        
        manager = ConfigurationManager(config_path=config_file)
        original_config = manager.create_default_config(
            project_id="test-project",
            model="gemini-2-5-pro",
            region="us-central1",
        )
        
        # Save
        manager.save_config(original_config)
        
        # Load
        loaded_config = manager.load_config()
        
        # Compare key fields
        assert loaded_config.project_id == original_config.project_id
        assert loaded_config.model == original_config.model
        assert loaded_config.region == original_config.region
        assert loaded_config.max_retries == original_config.max_retries
        assert loaded_config.timeout == original_config.timeout
    
    def test_environment_variable_override_workflow(self, tmp_path, monkeypatch):
        """Test that environment variables override file configuration."""
        config_file = tmp_path / "config.yaml"
        
        # Create base config
        manager = ConfigurationManager(config_path=config_file)
        config = manager.create_default_config(
            project_id="file-project",
            model="file-model",
        )
        manager.save_config(config)
        
        # Set environment variables
        monkeypatch.setenv("VERTEX_SPEC_PROJECT_ID", "env-project-id")
        monkeypatch.setenv("VERTEX_SPEC_MODEL", "env-model")
        
        # Load should use env overrides
        loaded = manager.load_config()
        
        assert loaded.project_id == "env-project-id"
        assert loaded.model == "env-model"

