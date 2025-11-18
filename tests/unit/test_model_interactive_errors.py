"""Unit tests for error handling in ModelInteractiveMenu."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vertex_spec_adapter.cli.commands.model_interactive import ModelInteractiveMenu
from vertex_spec_adapter.core.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ModelNotFoundError,
)


class TestMissingModelsHandling:
    """Test T033: Handle Missing Models Gracefully."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_no_models_available(self, mock_config_manager, mock_registry):
        """Test handling when no models are available."""
        # Setup mocks
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = []
        mock_registry.return_value = mock_registry_instance
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config_manager.return_value.load_config.side_effect = ConfigurationError("No config")
        mock_config_manager.return_value.create_default_config.return_value = mock_config
        
        # Create menu
        menu = ModelInteractiveMenu()
        
        # Should have empty models list
        assert len(menu.models) == 0
        
        # run() should show error and return None
        result = menu.run()
        assert result is None
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_model_registry_unavailable(self, mock_config_manager, mock_registry):
        """Test handling when ModelRegistry is unavailable."""
        # Setup mocks
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.side_effect = Exception("Connection failed")
        mock_registry.return_value = mock_registry_instance
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config_manager.return_value.load_config.side_effect = ConfigurationError("No config")
        mock_config_manager.return_value.create_default_config.return_value = mock_config
        
        # Create menu - should not crash
        menu = ModelInteractiveMenu()
        
        # Should have empty models list
        assert len(menu.models) == 0
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_switch_model_not_found(self, mock_config_manager, mock_registry):
        """Test switching to non-existent model."""
        # Setup mocks
        mock_registry_instance = Mock()
        mock_registry_instance.get_model_metadata.return_value = None
        mock_registry.return_value = mock_registry_instance
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config_manager.return_value.load_config.side_effect = ConfigurationError("No config")
        mock_config_manager.return_value.create_default_config.return_value = mock_config
        
        # Create menu with some models
        menu = ModelInteractiveMenu()
        menu.models = [Mock(model_id="model-1", name="Model 1")]
        
        # Try to switch to non-existent model
        success, message = menu._switch_model("non-existent-model")
        
        assert success is False
        assert "not found" in message.lower()
        assert "available models" in message.lower()


class TestAuthenticationErrors:
    """Test T034: Handle Authentication Errors."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.subprocess.run')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.AuthenticationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.VertexAIClient')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_gcloud_cli_not_installed(self, mock_registry, mock_config_manager, mock_client, mock_auth, mock_subprocess):
        """Test handling when gcloud CLI is not installed."""
        # Setup mocks
        mock_subprocess.run.side_effect = FileNotFoundError("gcloud not found")
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config.region = "us-central1"
        mock_config.auth_method = "auto"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_metadata = Mock()
        mock_metadata.model_id = "test-model"
        mock_metadata.name = "Test Model"
        mock_metadata.default_region = "us-central1"
        mock_metadata.available_regions = ["us-central1"]
        mock_metadata.latest_version = "latest"
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_model_metadata.return_value = mock_metadata
        mock_registry_instance.validate_model_availability.return_value = True
        mock_registry.return_value = mock_registry_instance
        
        # Create menu
        menu = ModelInteractiveMenu()
        
        # Try to switch model
        success, message = menu._switch_model("test-model")
        
        assert success is False
        assert "gcloud CLI not installed" in message
        assert "Installation instructions" in message
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.subprocess.run')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.AuthenticationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.VertexAIClient')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_authentication_failed(self, mock_registry, mock_config_manager, mock_client, mock_auth, mock_subprocess):
        """Test handling authentication failures."""
        # Setup mocks
        mock_subprocess.run.return_value = Mock(returncode=0)  # gcloud exists
        
        mock_auth_instance = Mock()
        mock_auth_instance.get_credentials.side_effect = AuthenticationError(
            "Invalid credentials",
            suggested_fix="Run 'gcloud auth login'"
        )
        mock_auth.return_value = mock_auth_instance
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config.region = "us-central1"
        mock_config.auth_method = "auto"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_metadata = Mock()
        mock_metadata.model_id = "test-model"
        mock_metadata.name = "Test Model"
        mock_metadata.default_region = "us-central1"
        mock_metadata.available_regions = ["us-central1"]
        mock_metadata.latest_version = "latest"
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_model_metadata.return_value = mock_metadata
        mock_registry_instance.validate_model_availability.return_value = True
        mock_registry.return_value = mock_registry_instance
        
        # Create menu
        menu = ModelInteractiveMenu()
        
        # Try to switch model
        success, message = menu._switch_model("test-model")
        
        assert success is False
        assert "Authentication failed" in message
        assert "gcloud auth login" in message
        assert "Troubleshooting steps" in message


class TestUnsupportedTerminals:
    """Test T035: Handle Unsupported Terminals."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_terminal_size_too_small(self, mock_config_manager, mock_registry):
        """Test fallback when terminal size is too small."""
        # Setup mocks
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model-1", "name": "Model 1"}
        ]
        mock_registry.return_value = mock_registry_instance
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config_manager.return_value.load_config.side_effect = ConfigurationError("No config")
        mock_config_manager.return_value.create_default_config.return_value = mock_config
        
        # Create menu with small terminal
        mock_console = Mock()
        mock_console.is_terminal = True
        mock_console.size = Mock(width=60, height=20)  # Too small
        
        menu = ModelInteractiveMenu(console=mock_console)
        menu.models = [Mock(model_id="model-1", name="Model 1", model_id="model-1")]
        
        # Should fall back to simple menu
        result = menu.run()
        
        # Should show warning about terminal
        assert any("interactive mode" in str(call) for call in mock_console.print.call_args_list)
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_terminal_not_supported(self, mock_config_manager, mock_registry):
        """Test fallback when terminal doesn't support features."""
        # Setup mocks
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model-1", "name": "Model 1"}
        ]
        mock_registry.return_value = mock_registry_instance
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config_manager.return_value.load_config.side_effect = ConfigurationError("No config")
        mock_config_manager.return_value.create_default_config.return_value = mock_config
        
        # Create menu with non-terminal console
        mock_console = Mock()
        mock_console.is_terminal = False
        
        menu = ModelInteractiveMenu(console=mock_console)
        menu.models = [Mock(model_id="model-1", name="Model 1", model_id="model-1")]
        
        # Should fall back to simple menu
        result = menu.run()
        
        # Should show warning
        assert any("interactive mode" in str(call) for call in mock_console.print.call_args_list)


class TestKeyboardInterrupts:
    """Test T036: Handle Keyboard Interrupts."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_keyboard_interrupt_in_menu(self, mock_config_manager, mock_registry):
        """Test handling KeyboardInterrupt in interactive menu."""
        # Setup mocks
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model-1", "name": "Model 1"}
        ]
        mock_registry.return_value = mock_registry_instance
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config_manager.return_value.load_config.side_effect = ConfigurationError("No config")
        mock_config_manager.return_value.create_default_config.return_value = mock_config
        
        # Create menu
        menu = ModelInteractiveMenu()
        menu.models = [Mock(model_id="model-1", name="Model 1")]
        
        # Mock _get_key to raise KeyboardInterrupt
        menu._get_key = Mock(side_effect=KeyboardInterrupt())
        
        # Should handle gracefully
        result = menu.run()
        
        assert result is None
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_keyboard_interrupt_in_simple_menu(self, mock_config_manager, mock_registry):
        """Test handling KeyboardInterrupt in simple text menu."""
        # Setup mocks
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model-1", "name": "Model 1"}
        ]
        mock_registry.return_value = mock_registry_instance
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config_manager.return_value.load_config.side_effect = ConfigurationError("No config")
        mock_config_manager.return_value.create_default_config.return_value = mock_config
        
        # Create menu
        menu = ModelInteractiveMenu()
        menu.models = [Mock(model_id="model-1", name="Model 1")]
        
        # Mock console.input to raise KeyboardInterrupt
        menu.console.input = Mock(side_effect=KeyboardInterrupt())
        
        # Should handle gracefully
        result = menu._simple_text_menu()
        
        assert result is None
        # Should show cancellation message
        assert any("cancelled" in str(call).lower() for call in menu.console.print.call_args_list)


class TestHelpfulErrorMessages:
    """Test T037: Add Helpful Error Messages."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_api_error_with_troubleshooting(self, mock_config_manager, mock_registry):
        """Test APIError shows troubleshooting steps."""
        # Setup mocks
        mock_subprocess = Mock()
        mock_subprocess.run.return_value = Mock(returncode=0)
        
        mock_auth_instance = Mock()
        mock_auth_instance.get_credentials.return_value = Mock()
        mock_auth = Mock(return_value=mock_auth_instance)
        
        mock_client_instance = Mock()
        mock_client = Mock(side_effect=APIError(
            "API call failed",
            status_code=404,
            troubleshooting_steps=["Step 1", "Step 2"]
        ))
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config.region = "us-central1"
        mock_config.auth_method = "auto"
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_config_manager.return_value.save_config = Mock()
        
        mock_metadata = Mock()
        mock_metadata.model_id = "test-model"
        mock_metadata.name = "Test Model"
        mock_metadata.default_region = "us-central1"
        mock_metadata.available_regions = ["us-central1"]
        mock_metadata.latest_version = "latest"
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_model_metadata.return_value = mock_metadata
        mock_registry_instance.validate_model_availability.return_value = True
        mock_registry.return_value = mock_registry_instance
        
        # Create menu
        with patch('vertex_spec_adapter.cli.commands.model_interactive.subprocess.run', mock_subprocess):
            with patch('vertex_spec_adapter.cli.commands.model_interactive.AuthenticationManager', mock_auth):
                with patch('vertex_spec_adapter.cli.commands.model_interactive.VertexAIClient', mock_client):
                    menu = ModelInteractiveMenu()
                    
                    # Try to switch model
                    success, message = menu._switch_model("test-model")
                    
                    assert success is False
                    assert "Failed to switch model" in message
                    assert "Troubleshooting steps" in message
                    assert "Step 1" in message
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_config_error_with_troubleshooting(self, mock_config_manager, mock_registry):
        """Test ConfigurationError shows troubleshooting steps."""
        # Setup mocks
        mock_subprocess = Mock()
        mock_subprocess.run.return_value = Mock(returncode=0)
        
        mock_auth_instance = Mock()
        mock_auth_instance.get_credentials.return_value = Mock()
        mock_auth = Mock(return_value=mock_auth_instance)
        
        mock_client_instance = Mock()
        mock_client = Mock(return_value=mock_client_instance)
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config.region = "us-central1"
        mock_config.auth_method = "auto"
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_config_manager.return_value.save_config.side_effect = ConfigurationError(
            "Permission denied",
            suggested_fix="Check file permissions"
        )
        mock_config_manager.return_value.config_path = Path("/tmp/test/config.yaml")
        
        mock_metadata = Mock()
        mock_metadata.model_id = "test-model"
        mock_metadata.name = "Test Model"
        mock_metadata.default_region = "us-central1"
        mock_metadata.available_regions = ["us-central1"]
        mock_metadata.latest_version = "latest"
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_model_metadata.return_value = mock_metadata
        mock_registry_instance.validate_model_availability.return_value = True
        mock_registry.return_value = mock_registry_instance
        
        # Create menu
        with patch('vertex_spec_adapter.cli.commands.model_interactive.subprocess.run', mock_subprocess):
            with patch('vertex_spec_adapter.cli.commands.model_interactive.AuthenticationManager', mock_auth):
                with patch('vertex_spec_adapter.cli.commands.model_interactive.VertexAIClient', mock_client):
                    menu = ModelInteractiveMenu()
                    
                    # Try to switch model
                    success, message = menu._switch_model("test-model")
                    
                    assert success is False
                    assert "Failed to save configuration" in message
                    assert "Troubleshooting steps" in message
                    assert "file permissions" in message.lower()

