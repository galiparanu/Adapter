"""Integration tests for Gemini CLI integration."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vertex_spec_adapter.gemini_cli.command_installer import (
    GeminiCLICommandInstaller,
    InstallationResult,
)
from vertex_spec_adapter.gemini_cli.model_command import main, parse_args


class TestGeminiCLICommandInstallation:
    """Test Gemini CLI command installation workflow."""
    
    @patch('vertex_spec_adapter.gemini_cli.command_installer.shutil.copy2')
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.exists')
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.mkdir')
    def test_install_command_workflow(self, mock_mkdir, mock_exists, mock_copy):
        """Test complete installation workflow."""
        # Setup mocks
        mock_exists.return_value = True  # Template exists
        installer = GeminiCLICommandInstaller()
        installer.command_file = Path("/tmp/test/model.toml")
        installer.command_file.exists = Mock(return_value=True)  # After install
        
        # Install command
        result = installer.install(force=False)
        
        # Verify installation
        assert result.success is True
        assert "installed successfully" in result.message.lower()
        mock_copy.assert_called_once()
    
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.unlink')
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.exists')
    def test_uninstall_command_workflow(self, mock_exists, mock_unlink):
        """Test uninstallation workflow."""
        # Setup mocks
        mock_exists.return_value = True
        
        installer = GeminiCLICommandInstaller()
        result = installer.uninstall()
        
        # Verify uninstallation
        assert result is True
        mock_unlink.assert_called_once()


class TestGeminiCLICommandExecution:
    """Test Gemini CLI command execution."""
    
    @patch('vertex_spec_adapter.gemini_cli.model_command.ModelInteractiveMenu')
    @patch('vertex_spec_adapter.gemini_cli.model_command.sys.exit')
    def test_command_execution_with_no_args(self, mock_exit, mock_menu_class):
        """Test command execution with no arguments (interactive mode)."""
        mock_menu = Mock()
        mock_menu.run_with_switch.return_value = "selected-model"
        mock_menu_class.return_value = mock_menu
        
        # Execute command
        main(None)
        
        # Verify interactive mode was used
        mock_menu.run_with_switch.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('vertex_spec_adapter.gemini_cli.model_command.ModelInteractiveMenu')
    @patch('vertex_spec_adapter.gemini_cli.model_command.sys.exit')
    def test_command_execution_with_list_flag(self, mock_exit, mock_menu_class):
        """Test command execution with --list flag."""
        mock_menu = Mock()
        mock_menu.run_with_switch.return_value = "selected-model"
        mock_menu_class.return_value = mock_menu
        
        # Execute command with --list
        main(["--list"])
        
        # Verify menu was called
        mock_menu.run_with_switch.assert_called_once()
        mock_exit.assert_called_once_with(0)


class TestArgumentParsing:
    """Test argument parsing for Gemini CLI command."""
    
    def test_parse_args_no_args(self):
        """Test parsing with no arguments."""
        result = parse_args(None)
        
        assert result["interactive"] is True
    
    def test_parse_args_list_flag(self):
        """Test parsing --list flag."""
        result = parse_args(["--list"])
        
        assert result["list"] is True
        assert result["interactive"] is False
    
    def test_parse_args_switch_flag(self):
        """Test parsing --switch flag."""
        result = parse_args(["--switch", "gemini-2.5-pro"])
        
        assert result["switch"] == "gemini-2.5-pro"
        assert result["interactive"] is False
    
    def test_parse_args_info_flag(self):
        """Test parsing --info flag."""
        result = parse_args(["--info", "gemini-2.5-pro"])
        
        assert result["info"] == "gemini-2.5-pro"
        assert result["interactive"] is False

