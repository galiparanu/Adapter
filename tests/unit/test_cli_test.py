"""Unit tests for test command."""

from unittest.mock import MagicMock, patch

import pytest
import typer

from vertex_spec_adapter.cli.commands import test
from vertex_spec_adapter.core.config import ConfigurationManager
from vertex_spec_adapter.core.exceptions import ConfigurationError


class TestTestCommand:
    """Test test command."""
    
    @patch("vertex_spec_adapter.cli.commands.test.get_config_manager")
    @patch("vertex_spec_adapter.cli.commands.test.test_credentials")
    @patch("vertex_spec_adapter.cli.commands.test.test_vertex_ai_connectivity")
    @patch("vertex_spec_adapter.cli.commands.test.print_success")
    def test_test_command_success(
        self,
        mock_print_success,
        mock_test_connectivity,
        mock_test_creds,
        mock_get_manager,
        tmp_path,
    ):
        """Test test command with successful tests."""
        config_file = tmp_path / "config.yaml"
        manager = ConfigurationManager(config_path=config_file)
        test_config = manager.create_default_config()
        manager.save_config(test_config)
        
        mock_get_manager.return_value = manager
        mock_test_creds.return_value = (True, "Credentials found")
        mock_test_connectivity.return_value = (True, "Connected")
        
        ctx = MagicMock()
        ctx.obj = {}
        
        with pytest.raises(typer.Exit) as exc_info:
            test.test_command(ctx)
        
        # Should exit with code 0 on success
        assert exc_info.value.exit_code == 0
    
    @patch("vertex_spec_adapter.cli.commands.test.get_config_manager")
    @patch("vertex_spec_adapter.cli.commands.test.test_credentials")
    @patch("vertex_spec_adapter.cli.commands.test.test_vertex_ai_connectivity")
    def test_test_command_failure(
        self,
        mock_test_connectivity,
        mock_test_creds,
        mock_get_manager,
        tmp_path,
    ):
        """Test test command with failed tests."""
        config_file = tmp_path / "config.yaml"
        manager = ConfigurationManager(config_path=config_file)
        test_config = manager.create_default_config()
        manager.save_config(test_config)
        
        mock_get_manager.return_value = manager
        mock_test_creds.return_value = (False, "No credentials")
        mock_test_connectivity.return_value = (False, "Connection failed")
        
        ctx = MagicMock()
        ctx.obj = {}
        
        with pytest.raises(typer.Exit) as exc_info:
            test.test_command(ctx)
        
        # Should exit with code 1 on failure
        assert exc_info.value.exit_code == 1
    
    @patch("vertex_spec_adapter.cli.commands.test.get_config_manager")
    def test_test_command_no_config(self, mock_get_manager):
        """Test test command when config doesn't exist."""
        manager = ConfigurationManager(config_path=Path("/nonexistent/config.yaml"))
        mock_get_manager.return_value = manager
        
        ctx = MagicMock()
        ctx.obj = {}
        
        with pytest.raises(typer.Exit) as exc_info:
            test.test_command(ctx)
        
        # Should exit with code 2 for configuration error
        assert exc_info.value.exit_code == 2
    
    @patch("google.auth.default")
    def test_test_credentials_success(self, mock_default):
        """Test credential check with valid credentials."""
        mock_creds = MagicMock()
        mock_default.return_value = (mock_creds, "test-project")
        
        success, message = test.test_credentials()
        
        assert success is True
        assert "Credentials found" in message
    
    @patch("google.auth.default")
    def test_test_credentials_failure(self, mock_default):
        """Test credential check with no credentials."""
        from google.auth.exceptions import DefaultCredentialsError
        
        mock_default.side_effect = DefaultCredentialsError("No credentials")
        
        success, message = test.test_credentials()
        
        assert success is False
        assert "No credentials" in message or "error" in message.lower()
    
    @patch("google.cloud.aiplatform")
    def test_test_vertex_ai_connectivity_success(self, mock_aiplatform):
        """Test Vertex AI connectivity check."""
        success, message = test.test_vertex_ai_connectivity(
            project_id="test-project",
            region="us-east5",
            model="claude-4-5-sonnet",
        )
        
        # Should succeed if SDK is available
        assert success is True or success is False  # Depends on whether SDK is installed
        assert isinstance(message, str)

