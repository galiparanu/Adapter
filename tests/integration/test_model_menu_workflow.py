"""Integration tests for model menu workflow."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vertex_spec_adapter.cli.commands.model_interactive import ModelInteractiveMenu
from vertex_spec_adapter.core.exceptions import ConfigurationError


class TestModelMenuWorkflow:
    """Test complete model menu workflow."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_full_menu_workflow(self, mock_config_manager, mock_registry):
        """Test complete menu workflow from initialization to model selection."""
        # Setup mocks
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config.region = "us-central1"
        mock_config.auth_method = "auto"
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_config_manager.return_value.save_config = Mock()
        
        # Create mock models
        mock_model1 = Mock()
        mock_model1.model_id = "model-1"
        mock_model1.name = "Model 1"
        mock_model1.default_region = "us-central1"
        mock_model1.available_regions = ["us-central1"]
        mock_model1.latest_version = "latest"
        mock_model1.context_window = "1M tokens"
        mock_model1.pricing = {"input": 0.5, "output": 1.5}
        mock_model1.capabilities = ["general-purpose"]
        mock_model1.description = "Test model 1"
        
        mock_model2 = Mock()
        mock_model2.model_id = "model-2"
        mock_model2.name = "Model 2"
        mock_model2.default_region = "us-central1"
        mock_model2.available_regions = ["us-central1"]
        mock_model2.latest_version = "latest"
        mock_model2.context_window = "2M tokens"
        mock_model2.pricing = {"input": 1.0, "output": 2.0}
        mock_model2.capabilities = ["code-generation"]
        mock_model2.description = "Test model 2"
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model-1", "name": "Model 1"},
            {"id": "model-2", "name": "Model 2"},
        ]
        mock_registry_instance.get_model_metadata.side_effect = lambda mid: {
            "model-1": mock_model1,
            "model-2": mock_model2,
        }.get(mid)
        mock_registry_instance.validate_model_availability.return_value = True
        mock_registry.return_value = mock_registry_instance
        
        # Create menu
        menu = ModelInteractiveMenu()
        
        # Verify initialization
        assert len(menu.models) == 2
        assert menu.selected_index == 0
        
        # Test navigation
        menu._handle_keypress("down")
        assert menu.selected_index == 1
        
        menu._handle_keypress("up")
        assert menu.selected_index == 0
        
        # Test hover details update
        menu._handle_keypress("down")
        assert menu.hover_details_model_id == "model-2"
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.subprocess.run')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.AuthenticationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.VertexAIClient')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_model_switching_workflow(
        self, mock_registry, mock_config_manager, mock_client, mock_auth, mock_subprocess
    ):
        """Test complete model switching workflow."""
        # Setup mocks
        mock_subprocess.run.return_value = Mock(returncode=0)  # gcloud exists
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config.region = "us-central1"
        mock_config.auth_method = "auto"
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_config_manager.return_value.save_config = Mock()
        
        mock_metadata = Mock()
        mock_metadata.model_id = "model-1"
        mock_metadata.name = "Model 1"
        mock_metadata.default_region = "us-central1"
        mock_metadata.available_regions = ["us-central1"]
        mock_metadata.latest_version = "latest"
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_model_metadata.return_value = mock_metadata
        mock_registry_instance.validate_model_availability.return_value = True
        mock_registry.return_value = mock_registry_instance
        
        mock_auth_instance = Mock()
        mock_auth_instance.get_credentials.return_value = Mock()
        mock_auth.return_value = mock_auth_instance
        
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Create menu
        menu = ModelInteractiveMenu()
        
        # Switch model
        success, message = menu._switch_model("model-1")
        
        # Verify switch succeeded
        assert success is True
        assert "Successfully switched" in message
        assert mock_config_manager.return_value.save_config.called


class TestConfigurationUpdates:
    """Test configuration update workflow."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.subprocess.run')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.AuthenticationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.VertexAIClient')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_config_persistence_after_switch(
        self, mock_registry, mock_config_manager, mock_client, mock_auth, mock_subprocess
    ):
        """Test that configuration is persisted after model switch."""
        # Setup mocks
        mock_subprocess.run.return_value = Mock(returncode=0)
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config.region = "us-central1"
        mock_config.auth_method = "auto"
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_config_manager.return_value.save_config = Mock()
        
        mock_metadata = Mock()
        mock_metadata.model_id = "new-model"
        mock_metadata.name = "New Model"
        mock_metadata.default_region = "us-west2"
        mock_metadata.available_regions = ["us-west2"]
        mock_metadata.latest_version = "latest"
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_model_metadata.return_value = mock_metadata
        mock_registry_instance.validate_model_availability.return_value = True
        mock_registry.return_value = mock_registry_instance
        
        mock_auth_instance = Mock()
        mock_auth_instance.get_credentials.return_value = Mock()
        mock_auth.return_value = mock_auth_instance
        
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Create menu
        menu = ModelInteractiveMenu()
        
        # Switch model
        success, _ = menu._switch_model("new-model")
        
        # Verify config was updated
        assert mock_config.model == "new-model"
        assert mock_config.region == "us-west2"
        assert mock_config.model_version == "latest"
        
        # Verify config was saved
        assert mock_config_manager.return_value.save_config.called

