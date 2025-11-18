"""Performance tests for menu rendering and operations."""

import time
from unittest.mock import Mock, patch

import pytest

from vertex_spec_adapter.cli.commands.model_interactive import ModelInteractiveMenu


class TestMenuRenderingPerformance:
    """Test T045: Menu rendering performance (< 50ms target)."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_render_menu_performance(self, mock_config_manager, mock_registry):
        """Test menu rendering completes in < 50ms."""
        # Setup mocks
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        # Create mock models
        mock_models = []
        for i in range(7):  # 7 models from vertex-config.md
            mock_model = Mock()
            mock_model.model_id = f"model-{i}"
            mock_model.name = f"Model {i}"
            mock_model.default_region = "us-central1"
            mock_model.available_regions = ["us-central1"]
            mock_model.latest_version = "latest"
            mock_model.context_window = "1M tokens"
            mock_model.pricing = {"input": 0.5, "output": 1.5}
            mock_model.capabilities = ["general-purpose"]
            mock_model.description = f"Test model {i}"
            mock_models.append(mock_model)
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": f"model-{i}", "name": f"Model {i}"} for i in range(7)
        ]
        mock_registry_instance.get_model_metadata.side_effect = lambda mid: {
            f"model-{i}": mock_models[i] for i in range(7)
        }.get(mid)
        mock_registry.return_value = mock_registry_instance
        
        # Create menu
        menu = ModelInteractiveMenu()
        menu.models = mock_models
        
        # Benchmark rendering
        start_time = time.perf_counter()
        layout = menu._render_menu()
        end_time = time.perf_counter()
        
        render_time_ms = (end_time - start_time) * 1000
        
        # Verify performance target (T045: < 50ms)
        assert render_time_ms < 50, f"Menu rendering took {render_time_ms:.2f}ms, target is < 50ms"
        assert layout is not None


class TestHoverDetailUpdatePerformance:
    """Test T046: Hover detail update performance (< 10ms target)."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_hover_detail_update_performance(self, mock_config_manager, mock_registry):
        """Test hover detail update completes in < 10ms."""
        # Setup mocks
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_model = Mock()
        mock_model.model_id = "model-1"
        mock_model.name = "Model 1"
        mock_model.context_window = "1M tokens"
        mock_model.pricing = {"input": 0.5, "output": 1.5}
        mock_model.capabilities = ["general-purpose"]
        mock_model.description = "Test model description"
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": "model-1", "name": "Model 1"}
        ]
        mock_registry_instance.get_model_metadata.return_value = mock_model
        mock_registry.return_value = mock_registry_instance
        
        # Create menu
        menu = ModelInteractiveMenu()
        menu.models = [mock_model]
        menu.hover_details_model_id = "model-1"
        
        # Benchmark first format (no cache)
        start_time = time.perf_counter()
        text1 = menu._format_hover_details()
        end_time = time.perf_counter()
        first_format_time_ms = (end_time - start_time) * 1000
        
        # Benchmark cached format (should be faster)
        start_time = time.perf_counter()
        text2 = menu._format_hover_details()
        end_time = time.perf_counter()
        cached_format_time_ms = (end_time - start_time) * 1000
        
        # Verify performance targets (T046: < 10ms)
        assert first_format_time_ms < 10, f"First hover format took {first_format_time_ms:.2f}ms, target is < 10ms"
        assert cached_format_time_ms < 10, f"Cached hover format took {cached_format_time_ms:.2f}ms, target is < 10ms"
        assert cached_format_time_ms < first_format_time_ms, "Cached format should be faster"
        assert text1 is not None
        assert text2 is not None


class TestModelSwitchingPerformance:
    """Test model switching performance (< 500ms target)."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.subprocess.run')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.AuthenticationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.VertexAIClient')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    def test_model_switch_performance(
        self, mock_registry, mock_config_manager, mock_client, mock_auth, mock_subprocess
    ):
        """Test model switching completes in < 500ms."""
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
        
        # Benchmark model switch
        start_time = time.perf_counter()
        success, _ = menu._switch_model("model-1")
        end_time = time.perf_counter()
        
        switch_time_ms = (end_time - start_time) * 1000
        
        # Verify performance target (< 500ms)
        assert switch_time_ms < 500, f"Model switch took {switch_time_ms:.2f}ms, target is < 500ms"
        assert success is True


class TestKeyboardResponsePerformance:
    """Test keyboard response performance (< 100ms target)."""
    
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ModelRegistry')
    @patch('vertex_spec_adapter.cli.commands.model_interactive.ConfigurationManager')
    def test_keyboard_navigation_performance(self, mock_config_manager, mock_registry):
        """Test keyboard navigation response < 100ms."""
        # Setup mocks
        mock_config = Mock()
        mock_config.project_id = "test-project"
        mock_config.model = None
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        mock_models = [Mock(model_id=f"model-{i}", name=f"Model {i}") for i in range(7)]
        
        mock_registry_instance = Mock()
        mock_registry_instance.get_available_models.return_value = [
            {"id": f"model-{i}", "name": f"Model {i}"} for i in range(7)
        ]
        mock_registry.return_value = mock_registry_instance
        
        # Create menu
        menu = ModelInteractiveMenu()
        menu.models = mock_models
        
        # Benchmark keyboard navigation
        start_time = time.perf_counter()
        menu._handle_keypress("down")
        end_time = time.perf_counter()
        
        nav_time_ms = (end_time - start_time) * 1000
        
        # Verify performance target (< 100ms)
        assert nav_time_ms < 100, f"Keyboard navigation took {nav_time_ms:.2f}ms, target is < 100ms"
        assert menu.selected_index == 1  # Should have moved down

