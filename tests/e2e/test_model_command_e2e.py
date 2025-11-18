"""End-to-end tests for model command feature."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vertex_spec_adapter.cli.commands.model_interactive import ModelInteractiveMenu
from vertex_spec_adapter.gemini_cli.command_installer import GeminiCLICommandInstaller
from vertex_spec_adapter.gemini_cli.model_command import main


class TestCompleteUserJourney:
    """Test complete user journey from installation to model switching."""
    
    @patch('vertex_spec_adapter.gemini_cli.command_installer.shutil.copy2')
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.exists')
    def test_user_journey_install_to_switch(self, mock_exists, mock_copy):
        """Test complete user journey: install command -> use menu -> switch model."""
        # Step 1: Install command
        mock_exists.return_value = True
        installer = GeminiCLICommandInstaller()
        installer.command_file = Path("/tmp/test/model.toml")
        installer.command_file.exists = Mock(return_value=True)
        
        install_result = installer.install()
        assert install_result.success is True
        
        # Step 2: Use menu (simulated)
        with patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry') as mock_registry:
            with patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager') as mock_config:
                mock_config_instance = Mock()
                mock_config_instance.load_config.return_value = Mock(
                    project_id="test-project",
                    model=None,
                )
                mock_config.return_value = mock_config_instance
                
                mock_registry_instance = Mock()
                mock_registry_instance.get_available_models.return_value = [
                    {"id": "model-1", "name": "Model 1"}
                ]
                mock_registry.return_value = mock_registry_instance
                
                menu = ModelInteractiveMenu()
                assert len(menu.models) > 0
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.subprocess.run')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.AuthenticationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.VertexAIClient')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_error_recovery_journey(
        self, mock_registry, mock_config_manager, mock_client, mock_auth, mock_subprocess
    ):
        """Test user journey with error recovery."""
        # Setup: gcloud not installed
        mock_subprocess.run.side_effect = FileNotFoundError("gcloud not found")
        
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config.region = "us-central1"
        mock_config.auth_method = "auto"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
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
        
        # Create menu
        menu = ModelInteractiveMenu()
        
        # Try to switch model (should fail gracefully)
        success, message = menu._switch_model("model-1")
        
        # Verify error is handled gracefully
        assert success is False
        assert "gcloud CLI not installed" in message
        assert "Installation instructions" in message


class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_windows_terminal_fallback(self, mock_config_manager, mock_registry):
        """Test Windows terminal fallback to simple menu."""
        # Setup mocks
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model-1", "name": "Model 1"}
        ]
        mock_registry.return_value = mock_registry_instance
        
        # Create menu with non-terminal console (simulating Windows)
        mock_console = Mock()
        mock_console.is_terminal = False
        
        menu = ModelInteractiveMenu(console=mock_console)
        menu.models = [Mock(model_id="model-1", name="Model 1")]
        
        # Should fall back to simple menu
        result = menu.run()
        
        # Verify fallback was used
        assert any("interactive mode" in str(call) for call in mock_console.print.call_args_list)
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_small_terminal_fallback(self, mock_config_manager, mock_registry):
        """Test small terminal fallback."""
        # Setup mocks
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model-1", "name": "Model 1"}
        ]
        mock_registry.return_value = mock_registry_instance
        
        # Create menu with small terminal
        mock_console = Mock()
        mock_console.is_terminal = True
        mock_console.size = Mock(width=60, height=20)  # Too small
        
        menu = ModelInteractiveMenu(console=mock_console)
        menu.models = [Mock(model_id="model-1", name="Model 1")]
        
        # Should fall back to simple menu
        result = menu.run()
        
        # Verify fallback was used
        assert any("interactive mode" in str(call) for call in mock_console.print.call_args_list)

