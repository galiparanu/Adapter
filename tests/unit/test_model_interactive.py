"""Unit tests for interactive model menu component."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from rich.console import Console

from vertex_spec_adapter.cli.commands.model_interactive import ModelInteractiveMenu
from vertex_spec_adapter.core.exceptions import ConfigurationError, ModelNotFoundError
from vertex_spec_adapter.core.models import ModelMetadata, ModelRegistry


class TestModelInteractiveMenuInitialization:
    """Test ModelInteractiveMenu initialization."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_init_with_defaults(self, mock_registry, mock_config_manager):
        """Test initialization with default parameters."""
        # Mock dependencies
        mock_config = Mock()
        mock_config.model.id = "gemini-2.5-pro"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"}
        ]
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu()
        
        assert menu is not None
        assert isinstance(menu.console, Console)
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_init_with_custom_config_path(self, mock_registry, mock_config_manager):
        """Test initialization with custom config path."""
        config_path = Path("/custom/path/config.yaml")
        
        mock_config = Mock()
        mock_config.model.id = "gemini-2.5-pro"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = []
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu(config_path=config_path)
        
        mock_config_manager.assert_called_once_with(config_path=config_path)
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_init_with_custom_console(self, mock_registry, mock_config_manager):
        """Test initialization with custom console."""
        custom_console = Console()
        
        mock_config = Mock()
        mock_config.model.id = "gemini-2.5-pro"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = []
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu(console=custom_console)
        
        assert menu.console is custom_console
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_init_raises_on_config_error(self, mock_registry, mock_config_manager):
        """Test initialization raises ConfigurationError on config failure."""
        mock_config_manager.return_value.load_config.side_effect = ConfigurationError("Config error")
        
        with pytest.raises(ConfigurationError):
            ModelInteractiveMenu()


class TestModelInteractiveMenuRendering:
    """Test menu rendering functionality."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_render_menu_displays_models(self, mock_registry, mock_config_manager):
        """Test that menu renders model list."""
        # This test should FAIL initially (RED phase)
        mock_config = Mock()
        mock_config.model.id = "gemini-2.5-pro"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"}
        ]
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu()
        menu._render_menu()
        
        # Verify console was used for rendering
        assert menu.console is not None


class TestModelInteractiveMenuNavigation:
    """Test keyboard navigation."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_handle_keypress_up(self, mock_registry, mock_config_manager):
        """Test handling up arrow key."""
        # This test should FAIL initially (RED phase)
        mock_config = Mock()
        mock_config.model.id = "gemini-2.5-pro"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model1", "name": "Model 1"},
            {"id": "model2", "name": "Model 2"},
        ]
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu()
        initial_index = menu.selected_index
        menu._handle_keypress("up")
        
        # Should wrap to end or decrement
        assert menu.selected_index != initial_index or menu.selected_index == len(menu.models) - 1
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_handle_keypress_down(self, mock_registry, mock_config_manager):
        """Test handling down arrow key."""
        # This test should FAIL initially (RED phase)
        mock_config = Mock()
        mock_config.model.id = "model1"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model1", "name": "Model 1"},
            {"id": "model2", "name": "Model 2"},
        ]
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu()
        initial_index = menu.selected_index
        menu._handle_keypress("down")
        
        # Should increment or wrap to start
        assert menu.selected_index != initial_index or menu.selected_index == 0
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_handle_keypress_enter(self, mock_registry, mock_config_manager):
        """Test handling Enter key returns model ID."""
        # This test should FAIL initially (RED phase)
        mock_config = Mock()
        mock_config.model.id = "model1"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model1", "name": "Model 1"},
        ]
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu()
        result = menu._handle_keypress("enter")
        
        assert result == "model1"
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_handle_keypress_escape(self, mock_registry, mock_config_manager):
        """Test handling Escape key returns None."""
        # This test should FAIL initially (RED phase)
        mock_config = Mock()
        mock_config.model.id = "model1"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = []
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu()
        result = menu._handle_keypress("escape")
        
        assert result is None
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_handle_keypress_home(self, mock_registry, mock_config_manager):
        """Test handling Home key jumps to first model."""
        # This test should FAIL initially (RED phase)
        mock_config = Mock()
        mock_config.model.id = "model2"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model1", "name": "Model 1"},
            {"id": "model2", "name": "Model 2"},
        ]
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu()
        menu.selected_index = 1  # Set to second model
        menu._handle_keypress("home")
        
        assert menu.selected_index == 0
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_handle_keypress_end(self, mock_registry, mock_config_manager):
        """Test handling End key jumps to last model."""
        # This test should FAIL initially (RED phase)
        mock_config = Mock()
        mock_config.model.id = "model1"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model1", "name": "Model 1"},
            {"id": "model2", "name": "Model 2"},
        ]
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu()
        menu.selected_index = 0  # Set to first model
        menu._handle_keypress("end")
        
        assert menu.selected_index == len(menu.models) - 1


class TestModelInteractiveMenuHoverDetails:
    """Test hover details formatting."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_format_hover_details(self, mock_registry, mock_config_manager):
        """Test formatting hover details for a model."""
        # This test should FAIL initially (RED phase)
        mock_config = Mock()
        mock_config.model.id = "gemini-2.5-pro"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = []
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu()
        
        model = ModelMetadata(
            model_id="gemini-2.5-pro",
            name="Gemini 2.5 Pro",
            provider="google",
            access_pattern="native_sdk",
            available_regions=["global"],
            context_window="1M+ tokens",
            pricing={"input": 0.50, "output": 1.50},
            capabilities=["general-purpose", "code-generation"],
            description="Test description",
        )
        
        details = menu._format_hover_details(model)
        
        assert "Gemini 2.5 Pro" in details
        assert "gemini-2.5-pro" in details
        assert "1M+ tokens" in details
        assert "general-purpose" in details
        assert "Test description" in details
        # Should NOT include region, provider, access_pattern
        assert "global" not in details
        assert "google" not in details
        assert "native_sdk" not in details
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_format_hover_details_with_none_fields(self, mock_registry, mock_config_manager):
        """Test formatting hover details when some fields are None."""
        # This test should FAIL initially (RED phase)
        mock_config = Mock()
        mock_config.model.id = "model1"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = []
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu()
        
        model = ModelMetadata(
            model_id="model1",
            name="Model 1",
            provider="test",
            access_pattern="maas",
            available_regions=["us-east5"],
            context_window=None,
            pricing=None,
            capabilities=["coding"],
            description="Test",
        )
        
        details = menu._format_hover_details(model)
        
        # Should handle None fields gracefully
        assert "Model 1" in details
        assert "coding" in details


class TestModelInteractiveMenuCurrentModel:
    """Test current model display."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_get_current_model(self, mock_registry, mock_config_manager):
        """Test getting current model from config."""
        # This test should FAIL initially (RED phase)
        mock_config = Mock()
        mock_config.model.id = "gemini-2.5-pro"
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = []
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu()
        current = menu._get_current_model()
        
        assert current == "gemini-2.5-pro"
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_get_current_model_none(self, mock_registry, mock_config_manager):
        """Test getting current model when not set."""
        # This test should FAIL initially (RED phase)
        mock_config_manager.return_value.load_config.side_effect = ConfigurationError("No config")
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = []
        mock_registry.return_value = mock_registry_instance
        
        menu = ModelInteractiveMenu()
        current = menu._get_current_model()
        
        assert current is None

