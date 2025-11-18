"""Unit tests for Gemini CLI integration."""

import shutil
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vertex_spec_adapter.gemini_cli.command_installer import (
    GeminiCLICommandInstaller,
    InstallationResult,
)


class TestGeminiCLICommandInstaller:
    """Test GeminiCLICommandInstaller class."""
    
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.home')
    def test_get_command_path(self, mock_home):
        """Test getting command path."""
        mock_home.return_value = Path("/home/test")
        
        installer = GeminiCLICommandInstaller()
        path = installer.get_command_path()
        
        assert path == Path("/home/test/.gemini/commands")
        mock_home.assert_called_once()
    
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.exists')
    def test_is_installed_true(self, mock_exists):
        """Test is_installed returns True when file exists."""
        mock_exists.return_value = True
        
        installer = GeminiCLICommandInstaller()
        result = installer.is_installed()
        
        assert result is True
    
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.exists')
    def test_is_installed_false(self, mock_exists):
        """Test is_installed returns False when file doesn't exist."""
        mock_exists.return_value = False
        
        installer = GeminiCLICommandInstaller()
        result = installer.is_installed()
        
        assert result is False
    
    @patch('vertex_spec_adapter.gemini_cli.command_installer.shutil.copy2')
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.exists')
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.mkdir')
    def test_install_success(self, mock_mkdir, mock_exists, mock_copy):
        """Test successful installation."""
        mock_exists.return_value = True  # Template exists
        installer = GeminiCLICommandInstaller()
        installer.command_file = Path("/tmp/test/model.toml")
        installer.command_file.exists = Mock(return_value=True)  # After install
        
        result = installer.install(force=False)
        
        assert result.success is True
        assert "installed successfully" in result.message.lower()
        mock_copy.assert_called_once()
    
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.exists')
    def test_install_template_not_found(self, mock_exists):
        """Test installation fails when template not found."""
        mock_exists.return_value = False  # Template doesn't exist
        
        installer = GeminiCLICommandInstaller()
        result = installer.install()
        
        assert result.success is False
        assert "not found" in result.error.lower()
    
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.exists')
    def test_install_already_installed(self, mock_exists):
        """Test installation fails when already installed and force=False."""
        def exists_side_effect(path):
            if str(path).endswith("model.toml"):
                return True  # Command file exists
            return True  # Template exists
        
        mock_exists.side_effect = exists_side_effect
        
        installer = GeminiCLICommandInstaller()
        result = installer.install(force=False)
        
        assert result.success is False
        assert "already installed" in result.error.lower()
    
    @patch('vertex_spec_adapter.gemini_cli.command_installer.shutil.copy2')
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.exists')
    def test_install_with_force(self, mock_exists, mock_copy):
        """Test installation with force=True overwrites existing file."""
        def exists_side_effect(path):
            if str(path).endswith("model.toml"):
                return True  # Command file exists
            return True  # Template exists
        
        mock_exists.side_effect = exists_side_effect
        
        installer = GeminiCLICommandInstaller()
        installer.command_file = Path("/tmp/test/model.toml")
        installer.command_file.exists = Mock(return_value=True)  # After install
        
        result = installer.install(force=True)
        
        assert result.success is True
        mock_copy.assert_called_once()
    
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.unlink')
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.exists')
    def test_uninstall_success(self, mock_exists, mock_unlink):
        """Test successful uninstallation."""
        mock_exists.return_value = True
        
        installer = GeminiCLICommandInstaller()
        result = installer.uninstall()
        
        assert result is True
        mock_unlink.assert_called_once()
    
    @patch('vertex_spec_adapter.gemini_cli.command_installer.Path.exists')
    def test_uninstall_not_installed(self, mock_exists):
        """Test uninstall returns False when file doesn't exist."""
        mock_exists.return_value = False
        
        installer = GeminiCLICommandInstaller()
        result = installer.uninstall()
        
        assert result is False


class TestModelCommandArgumentParsing:
    """Test model command argument parsing."""
    
    def test_parse_args_no_args(self):
        """Test parsing with no arguments."""
        from vertex_spec_adapter.gemini_cli.model_command import parse_args
        
        result = parse_args(None)
        
        assert result["interactive"] is True
    
    def test_parse_args_empty_list(self):
        """Test parsing with empty list."""
        from vertex_spec_adapter.gemini_cli.model_command import parse_args
        
        result = parse_args([])
        
        assert result["interactive"] is True
    
    def test_parse_args_with_args(self):
        """Test parsing with arguments (defaults to interactive)."""
        from vertex_spec_adapter.gemini_cli.model_command import parse_args
        
        result = parse_args(["some", "args"])
        
        assert result["interactive"] is True
    
    def test_parse_args_list_flag(self):
        """Test parsing --list flag."""
        from vertex_spec_adapter.gemini_cli.model_command import parse_args
        
        result = parse_args(["--list"])
        
        assert result["list"] is True
        assert result["interactive"] is False
    
    def test_parse_args_switch_flag(self):
        """Test parsing --switch flag."""
        from vertex_spec_adapter.gemini_cli.model_command import parse_args
        
        result = parse_args(["--switch", "gemini-2.5-pro"])
        
        assert result["switch"] == "gemini-2.5-pro"
        assert result["interactive"] is False
    
    def test_parse_args_info_flag(self):
        """Test parsing --info flag."""
        from vertex_spec_adapter.gemini_cli.model_command import parse_args
        
        result = parse_args(["--info", "gemini-2.5-pro"])
        
        assert result["info"] == "gemini-2.5-pro"
        assert result["interactive"] is False


class TestModelCommandMain:
    """Test model command main entry point."""
    
    @patch('vertex_spec_adapter.gemini_cli.model_command.ModelInteractiveMenu')
    @patch('vertex_spec_adapter.gemini_cli.model_command.sys.exit')
    def test_main_interactive_success(self, mock_exit, mock_menu_class):
        """Test main with interactive mode success."""
        mock_menu = Mock()
        mock_menu.run_with_switch.return_value = "selected-model"
        mock_menu_class.return_value = mock_menu
        
        from vertex_spec_adapter.gemini_cli.model_command import main
        
        main(None)
        
        mock_menu.run_with_switch.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('vertex_spec_adapter.gemini_cli.model_command.ModelInteractiveMenu')
    @patch('vertex_spec_adapter.gemini_cli.model_command.sys.exit')
    def test_main_interactive_cancelled(self, mock_exit, mock_menu_class):
        """Test main with interactive mode cancelled."""
        mock_menu = Mock()
        mock_menu.run_with_switch.return_value = None
        mock_menu_class.return_value = mock_menu
        
        from vertex_spec_adapter.gemini_cli.model_command import main
        
        main(None)
        
        mock_menu.run_with_switch.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('vertex_spec_adapter.gemini_cli.model_command.ModelInteractiveMenu')
    @patch('vertex_spec_adapter.gemini_cli.model_command.sys.exit')
    def test_main_keyboard_interrupt(self, mock_exit, mock_menu_class):
        """Test main handles KeyboardInterrupt."""
        mock_menu = Mock()
        mock_menu.run_with_switch.side_effect = KeyboardInterrupt()
        mock_menu_class.return_value = mock_menu
        
        from vertex_spec_adapter.gemini_cli.model_command import main
        
        main(None)
        
        mock_exit.assert_called_once_with(130)
    
    @patch('vertex_spec_adapter.gemini_cli.model_command.ModelInteractiveMenu')
    @patch('vertex_spec_adapter.gemini_cli.model_command.sys.exit')
    def test_main_exception(self, mock_exit, mock_menu_class):
        """Test main handles exceptions."""
        mock_menu = Mock()
        mock_menu.run_with_switch.side_effect = Exception("Test error")
        mock_menu_class.return_value = mock_menu
        
        from vertex_spec_adapter.gemini_cli.model_command import main
        
        main(None)
        
        mock_exit.assert_called_once_with(1)

