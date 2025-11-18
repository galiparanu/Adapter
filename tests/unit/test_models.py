"""Unit tests for ModelRegistry."""

import pytest

from vertex_spec_adapter.core.exceptions import ModelNotFoundError
from vertex_spec_adapter.core.models import ModelMetadata, ModelRegistry


class TestModelMetadata:
    """Test ModelMetadata class."""
    
    def test_init(self):
        """Test ModelMetadata initialization."""
        metadata = ModelMetadata(
            model_id="test-model",
            name="Test Model",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
            default_region="us-east5",
            latest_version="@20250101",
        )
        
        assert metadata.model_id == "test-model"
        assert metadata.name == "Test Model"
        assert metadata.provider == "test"
        assert metadata.access_pattern == "native_sdk"
        assert metadata.available_regions == ["us-east5"]
        assert metadata.default_region == "us-east5"
        assert metadata.latest_version == "@20250101"
    
    def test_to_dict(self):
        """Test ModelMetadata to_dict method."""
        metadata = ModelMetadata(
            model_id="test-model",
            name="Test Model",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
        )
        
        result = metadata.to_dict()
        
        assert result["id"] == "test-model"
        assert result["name"] == "Test Model"
        assert result["provider"] == "test"
        assert "available_regions" in result


class TestModelRegistry:
    """Test ModelRegistry class."""
    
    def test_init(self):
        """Test ModelRegistry initialization."""
        registry = ModelRegistry()
        
        assert registry.cache_ttl == 3600
        assert len(registry._cache) == 0
    
    def test_get_model_metadata(self):
        """Test getting model metadata."""
        registry = ModelRegistry()
        
        metadata = registry.get_model_metadata("claude-4-5-sonnet")
        
        assert metadata is not None
        assert metadata.model_id == "claude-4-5-sonnet"
        assert metadata.name == "Claude 4.5 Sonnet"
        assert metadata.provider == "anthropic"
    
    def test_get_model_metadata_not_found(self):
        """Test getting metadata for unknown model."""
        registry = ModelRegistry()
        
        metadata = registry.get_model_metadata("unknown-model")
        
        assert metadata is None
    
    def test_get_available_models(self):
        """Test getting available models list."""
        registry = ModelRegistry()
        
        models = registry.get_available_models("test-project")
        
        assert len(models) > 0
        assert all("id" in m for m in models)
        assert all("name" in m for m in models)
        assert all("provider" in m for m in models)
    
    def test_get_available_models_with_region_filter(self):
        """Test getting models filtered by region."""
        registry = ModelRegistry()
        
        models = registry.get_available_models("test-project", region="us-east5")
        
        assert len(models) > 0
        # All models should be available in us-east5
        for model in models:
            assert "us-east5" in model.get("available_regions", [])
    
    def test_validate_model_availability_success(self):
        """Test validating model availability."""
        registry = ModelRegistry()
        
        result = registry.validate_model_availability("claude-4-5-sonnet", "us-east5")
        
        assert result is True
    
    def test_validate_model_availability_not_found(self):
        """Test validating unknown model."""
        registry = ModelRegistry()
        
        with pytest.raises(ModelNotFoundError) as exc_info:
            registry.validate_model_availability("unknown-model", "us-east5")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_validate_model_availability_wrong_region(self):
        """Test validating model in unavailable region."""
        registry = ModelRegistry()
        
        with pytest.raises(ModelNotFoundError) as exc_info:
            registry.validate_model_availability("claude-4-5-sonnet", "us-west1")
        
        assert "not available" in str(exc_info.value).lower()
        assert exc_info.value.available_regions is not None
    
    def test_get_default_region(self):
        """Test getting default region for model."""
        registry = ModelRegistry()
        
        region = registry.get_default_region("claude-4-5-sonnet")
        
        assert region == "us-east5"
    
    def test_get_default_region_not_found(self):
        """Test getting default region for unknown model."""
        registry = ModelRegistry()
        
        region = registry.get_default_region("unknown-model")
        
        assert region is None
    
    def test_get_available_regions(self):
        """Test getting available regions for model."""
        registry = ModelRegistry()
        
        regions = registry.get_available_regions("claude-4-5-sonnet")
        
        assert len(regions) > 0
        assert "us-east5" in regions
    
    def test_detect_access_pattern(self):
        """Test detecting access pattern."""
        registry = ModelRegistry()
        
        pattern = registry.detect_access_pattern("claude-4-5-sonnet")
        
        assert pattern == "native_sdk"
    
    def test_detect_access_pattern_maas(self):
        """Test detecting MaaS access pattern."""
        registry = ModelRegistry()
        
        pattern = registry.detect_access_pattern("qwen-coder")
        
        assert pattern == "maas"
    
    def test_get_latest_version(self):
        """Test getting latest version."""
        registry = ModelRegistry()
        
        version = registry.get_latest_version("claude-4-5-sonnet")
        
        assert version is not None
        assert version.startswith("@")
    
    def test_validate_version_success(self):
        """Test validating valid version."""
        registry = ModelRegistry()
        
        result = registry.validate_version("claude-4-5-sonnet", "@20250929")
        
        assert result is True
    
    def test_validate_version_invalid(self):
        """Test validating invalid version."""
        registry = ModelRegistry()
        
        with pytest.raises(ModelNotFoundError) as exc_info:
            registry.validate_version("claude-4-5-sonnet", "@99999999")
        
        assert "not available" in str(exc_info.value).lower()
    
    def test_clear_cache(self):
        """Test clearing cache."""
        registry = ModelRegistry()
        
        # Populate cache
        registry.get_available_models("test-project")
        assert len(registry._cache) > 0
        
        # Clear cache
        registry.clear_cache()
        
        assert len(registry._cache) == 0
        assert len(registry._cache_timestamp) == 0

