"""Integration tests for Vertex AI API calls."""

import pytest

from vertex_spec_adapter.core.models import ModelRegistry


@pytest.mark.integration
class TestVertexAPIIntegration:
    """Integration tests for Vertex AI API."""
    
    def test_model_availability_check(self):
        """Test checking model availability."""
        registry = ModelRegistry()
        
        # Test with known model
        result = registry.validate_model_availability("claude-4-5-sonnet", "us-east5")
        assert result is True
    
    def test_get_available_models_integration(self):
        """Test getting available models (integration)."""
        registry = ModelRegistry()
        
        models = registry.get_available_models("test-project", use_cache=False)
        
        assert len(models) > 0
        assert all("id" in m for m in models)
        assert all("available_regions" in m for m in models)

