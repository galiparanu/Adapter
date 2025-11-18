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


class TestExtendedModelMetadata:
    """Test extended ModelMetadata with new fields (context_window, pricing, capabilities, description)."""
    
    def test_init_with_context_window(self):
        """Test ModelMetadata initialization with context_window field."""
        # This test should FAIL initially (RED phase)
        metadata = ModelMetadata(
            model_id="test-model",
            name="Test Model",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
            context_window="1M tokens",  # New field
        )
        
        assert metadata.context_window == "1M tokens"
    
    def test_init_with_pricing(self):
        """Test ModelMetadata initialization with pricing field."""
        # This test should FAIL initially (RED phase)
        metadata = ModelMetadata(
            model_id="test-model",
            name="Test Model",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
            pricing={"input": 0.0001, "output": 0.0002},  # New field
        )
        
        assert metadata.pricing == {"input": 0.0001, "output": 0.0002}
        assert metadata.pricing["input"] == 0.0001
        assert metadata.pricing["output"] == 0.0002
    
    def test_init_with_capabilities(self):
        """Test ModelMetadata initialization with capabilities field."""
        # This test should FAIL initially (RED phase)
        metadata = ModelMetadata(
            model_id="test-model",
            name="Test Model",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
            capabilities=["coding", "reasoning"],  # New field
        )
        
        assert metadata.capabilities == ["coding", "reasoning"]
        assert len(metadata.capabilities) == 2
    
    def test_init_with_description(self):
        """Test ModelMetadata initialization with description field."""
        # This test should FAIL initially (RED phase)
        metadata = ModelMetadata(
            model_id="test-model",
            name="Test Model",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
            description="Test model for unit testing",  # New field
        )
        
        assert metadata.description == "Test model for unit testing"
    
    def test_init_with_all_new_fields(self):
        """Test ModelMetadata initialization with all new fields."""
        # This test should FAIL initially (RED phase)
        metadata = ModelMetadata(
            model_id="test-model",
            name="Test Model",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
            context_window="1M tokens",
            pricing={"input": 0.0001, "output": 0.0002},
            capabilities=["coding", "reasoning", "general-purpose"],
            description="Test model for unit testing",
        )
        
        assert metadata.context_window == "1M tokens"
        assert metadata.pricing == {"input": 0.0001, "output": 0.0002}
        assert metadata.capabilities == ["coding", "reasoning", "general-purpose"]
        assert metadata.description == "Test model for unit testing"
    
    def test_init_without_new_fields_backward_compatible(self):
        """Test ModelMetadata initialization without new fields (backward compatibility)."""
        # This test should PASS (backward compatibility)
        metadata = ModelMetadata(
            model_id="test-model",
            name="Test Model",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
        )
        
        # New fields should be None or have default values
        assert metadata.context_window is None
        assert metadata.pricing is None
        assert metadata.capabilities is None
        assert metadata.description is None
    
    def test_to_dict_with_new_fields(self):
        """Test to_dict() method includes new fields."""
        # This test should FAIL initially (RED phase)
        metadata = ModelMetadata(
            model_id="test-model",
            name="Test Model",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
            context_window="1M tokens",
            pricing={"input": 0.0001, "output": 0.0002},
            capabilities=["coding", "reasoning"],
            description="Test model",
        )
        
        result = metadata.to_dict()
        
        assert "context_window" in result
        assert result["context_window"] == "1M tokens"
        assert "pricing" in result
        assert result["pricing"] == {"input": 0.0001, "output": 0.0002}
        assert "capabilities" in result
        assert result["capabilities"] == ["coding", "reasoning"]
        assert "description" in result
        assert result["description"] == "Test model"
    
    def test_to_dict_without_new_fields_backward_compatible(self):
        """Test to_dict() without new fields (backward compatibility)."""
        # This test should PASS (backward compatibility)
        metadata = ModelMetadata(
            model_id="test-model",
            name="Test Model",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
        )
        
        result = metadata.to_dict()
        
        # New fields should not be in dict if None (omitted, not included as None)
        assert "id" in result
        assert "name" in result
        assert "provider" in result
        assert "context_window" not in result  # Should be omitted if None
        assert "pricing" not in result  # Should be omitted if None
        assert "capabilities" not in result  # Should be omitted if None
        assert "description" not in result  # Should be omitted if None
    
    def test_validation_context_window_empty_string(self):
        """Test validation fails for empty context_window string."""
        with pytest.raises(ValueError, match="non-empty"):
            ModelMetadata(
                model_id="test",
                name="Test",
                provider="test",
                access_pattern="native_sdk",
                available_regions=["us-east5"],
                context_window="",  # Empty string should fail
            )
    
    def test_validation_pricing_invalid_keys(self):
        """Test validation fails for pricing with invalid keys."""
        with pytest.raises(ValueError, match="invalid key"):
            ModelMetadata(
                model_id="test",
                name="Test",
                provider="test",
                access_pattern="native_sdk",
                available_regions=["us-east5"],
                pricing={"invalid_key": 0.1},  # Invalid key
            )
    
    def test_validation_pricing_negative_value(self):
        """Test validation fails for negative pricing values."""
        with pytest.raises(ValueError, match="non-negative"):
            ModelMetadata(
                model_id="test",
                name="Test",
                provider="test",
                access_pattern="native_sdk",
                available_regions=["us-east5"],
                pricing={"input": -0.1},  # Negative value should fail
            )
    
    def test_validation_capabilities_empty_list(self):
        """Test validation fails for empty capabilities list."""
        with pytest.raises(ValueError, match="non-empty"):
            ModelMetadata(
                model_id="test",
                name="Test",
                provider="test",
                access_pattern="native_sdk",
                available_regions=["us-east5"],
                capabilities=[],  # Empty list should fail
            )
    
    def test_validation_description_empty_string(self):
        """Test validation fails for empty description string."""
        with pytest.raises(ValueError, match="non-empty"):
            ModelMetadata(
                model_id="test",
                name="Test",
                provider="test",
                access_pattern="native_sdk",
                available_regions=["us-east5"],
                description="",  # Empty string should fail
            )
    
    def test_pricing_only_input(self):
        """Test pricing with only input key."""
        metadata = ModelMetadata(
            model_id="test",
            name="Test",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
            pricing={"input": 0.1},  # Only input
        )
        
        assert metadata.pricing == {"input": 0.1}
    
    def test_pricing_only_output(self):
        """Test pricing with only output key."""
        metadata = ModelMetadata(
            model_id="test",
            name="Test",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
            pricing={"output": 0.2},  # Only output
        )
        
        assert metadata.pricing == {"output": 0.2}
    
    def test_capabilities_single_item(self):
        """Test capabilities with single item."""
        metadata = ModelMetadata(
            model_id="test",
            name="Test",
            provider="test",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
            capabilities=["coding"],  # Single item
        )
        
        assert metadata.capabilities == ["coding"]
        assert len(metadata.capabilities) == 1


class TestModelRegistryWithExtendedMetadata:
    """Test ModelRegistry with extended ModelMetadata."""
    
    def test_get_model_metadata_with_extended_fields(self):
        """Test getting model metadata with extended fields."""
        registry = ModelRegistry()
        
        # Test with one of the new models
        metadata = registry.get_model_metadata("gemini-2.5-pro")
        
        assert metadata is not None
        assert metadata.model_id == "gemini-2.5-pro"
        assert metadata.context_window == "1M+ tokens"
        assert metadata.pricing == {"input": 0.50, "output": 1.50}
        assert "general-purpose" in metadata.capabilities
        assert metadata.description is not None
    
    def test_get_available_models_includes_extended_fields(self):
        """Test get_available_models includes extended fields in dict."""
        registry = ModelRegistry()
        
        models = registry.get_available_models("test-project")
        
        # Find a model with extended fields
        gemini_model = next((m for m in models if m["id"] == "gemini-2.5-pro"), None)
        
        assert gemini_model is not None
        assert "context_window" in gemini_model
        assert "pricing" in gemini_model
        assert "capabilities" in gemini_model
        assert "description" in gemini_model
    
    def test_get_available_models_omits_none_fields(self):
        """Test get_available_models omits None extended fields."""
        registry = ModelRegistry()
        
        models = registry.get_available_models("test-project")
        
        # Find a model without some extended fields
        deepseek_model = next((m for m in models if m["id"] == "deepseek-ai/deepseek-v3.1-maas"), None)
        
        assert deepseek_model is not None
        # context_window and pricing are None, so they should be omitted
        # But capabilities and description are set, so they should be included
        assert "capabilities" in deepseek_model
        assert "description" in deepseek_model
    
    def test_only_7_models_in_registry(self):
        """Test that only 7 models from vertex-config.md are in registry."""
        registry = ModelRegistry()
        
        models = registry.get_available_models("test-project")
        
        # Should have exactly 7 models
        assert len(models) == 7
        
        # Verify all 7 models are present
        model_ids = {m["id"] for m in models}
        expected_models = {
            "deepseek-ai/deepseek-v3.1-maas",
            "qwen/qwen3-coder-480b-a35b-instruct-maas",
            "gemini-2.5-pro",
            "deepseek-ai/deepseek-r1-0528-maas",
            "moonshotai/kimi-k2-thinking-maas",
            "openai/gpt-oss-120b-maas",
            "meta/llama-3.1-405b-instruct-maas",
        }
        
        assert model_ids == expected_models
    
    def test_get_model_metadata_case_insensitive(self):
        """Test get_model_metadata is case-insensitive."""
        registry = ModelRegistry()
        
        # Test with different cases
        metadata1 = registry.get_model_metadata("GEMINI-2.5-PRO")
        metadata2 = registry.get_model_metadata("gemini-2.5-pro")
        metadata3 = registry.get_model_metadata("Gemini-2.5-Pro")
        
        assert metadata1 is not None
        assert metadata2 is not None
        assert metadata3 is not None
        assert metadata1.model_id == metadata2.model_id == metadata3.model_id

