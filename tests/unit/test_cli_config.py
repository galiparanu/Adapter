"""Unit tests for config command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from vertex_spec_adapter.cli.commands import config
from vertex_spec_adapter.core.config import ConfigurationManager
from vertex_spec_adapter.core.exceptions import ConfigurationError
from vertex_spec_adapter.schemas.config import VertexConfig


class TestConfigCommand:
    """Test config command."""
    
    @patch("vertex_spec_adapter.cli.commands.config.get_config_manager")
    @patch("vertex_spec_adapter.cli.commands.config.print_table")
    def test_config_show(self, mock_print_table, mock_get_manager, tmp_path):
        """Test config show command."""
        config_file = tmp_path / "config.yaml"
        manager = ConfigurationManager(config_path=config_file)
        test_config = manager.create_default_config(
            project_id="test-project",
            model="claude-4-5-sonnet",
        )
        manager.save_config(test_config)
        
        mock_get_manager.return_value = manager
        
        ctx = MagicMock()
        ctx.obj = {}
        
        config.config_show(ctx)
        
        # Verify table was printed
        assert mock_print_table.called
    
    @patch("vertex_spec_adapter.cli.commands.config.get_config_manager")
    @patch("vertex_spec_adapter.cli.commands.config.print_success")
    def test_config_set(self, mock_print_success, mock_get_manager, tmp_path):
        """Test config set command."""
        config_file = tmp_path / "config.yaml"
        manager = ConfigurationManager(config_path=config_file)
        test_config = manager.create_default_config()
        manager.save_config(test_config)
        
        mock_get_manager.return_value = manager
        
        ctx = MagicMock()
        ctx.obj = {}
        
        config.config_set(ctx, "model", "gemini-2-5-pro")
        
        # Verify success message
        assert mock_print_success.called
        
        # Verify config was updated
        loaded = manager.load_config()
        assert loaded.model == "gemini-2-5-pro"
    
    @patch("vertex_spec_adapter.cli.commands.config.get_config_manager")
    def test_config_set_invalid_key(self, mock_get_manager, tmp_path):
        """Test config set with invalid key."""
        config_file = tmp_path / "config.yaml"
        manager = ConfigurationManager(config_path=config_file)
        test_config = manager.create_default_config()
        manager.save_config(test_config)
        
        mock_get_manager.return_value = manager
        
        ctx = MagicMock()
        ctx.obj = {}
        
        with pytest.raises(typer.Exit):
            config.config_set(ctx, "invalid_key", "value")
    
    @patch("vertex_spec_adapter.cli.commands.config.get_config_manager")
    @patch("vertex_spec_adapter.cli.commands.config.console")
    def test_config_get(self, mock_console, mock_get_manager, tmp_path):
        """Test config get command."""
        config_file = tmp_path / "config.yaml"
        manager = ConfigurationManager(config_path=config_file)
        test_config = manager.create_default_config(
            project_id="test-project",
            model="claude-4-5-sonnet",
        )
        manager.save_config(test_config)
        
        mock_get_manager.return_value = manager
        
        ctx = MagicMock()
        ctx.obj = {}
        
        config.config_get(ctx, "model")
        
        # Verify console.print was called with model value
        assert mock_console.print.called
    
    @patch("vertex_spec_adapter.cli.commands.config.get_config_manager")
    @patch("vertex_spec_adapter.cli.commands.config.print_success")
    def test_config_validate(self, mock_print_success, mock_get_manager, tmp_path):
        """Test config validate command."""
        config_file = tmp_path / "config.yaml"
        manager = ConfigurationManager(config_path=config_file)
        test_config = manager.create_default_config()
        manager.save_config(test_config)
        
        mock_get_manager.return_value = manager
        
        ctx = MagicMock()
        ctx.obj = {}
        
        config.config_validate(ctx)
        
        # Verify success message
        assert mock_print_success.called

