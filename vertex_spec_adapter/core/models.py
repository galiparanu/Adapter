"""Model registry for managing model metadata, availability, and versions."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from vertex_spec_adapter.core.exceptions import ModelNotFoundError
from vertex_spec_adapter.utils.logging import get_logger

logger = get_logger(__name__)


class ModelMetadata:
    """Metadata for a single model."""
    
    def __init__(
        self,
        model_id: str,
        name: str,
        provider: str,
        access_pattern: str,
        available_regions: List[str],
        default_region: Optional[str] = None,
        latest_version: Optional[str] = None,
        versions: Optional[List[str]] = None,
    ):
        """
        Initialize model metadata.
        
        Args:
            model_id: Model identifier
            name: Human-readable model name
            provider: Provider name (anthropic, google, qwen)
            access_pattern: Access pattern (native_sdk, maas)
            available_regions: List of regions where model is available
            default_region: Default region for this model
            latest_version: Latest version identifier
            versions: List of available versions
        """
        self.model_id = model_id
        self.name = name
        self.provider = provider
        self.access_pattern = access_pattern
        self.available_regions = available_regions
        self.default_region = default_region or (available_regions[0] if available_regions else None)
        self.latest_version = latest_version
        self.versions = versions or []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.model_id,
            "name": self.name,
            "provider": self.provider,
            "access_pattern": self.access_pattern,
            "available_regions": self.available_regions,
            "default_region": self.default_region,
            "latest_version": self.latest_version,
            "versions": self.versions,
        }


class ModelRegistry:
    """
    Registry for managing model metadata, availability, and versions.
    
    Provides:
    - Model metadata storage
    - Availability validation
    - Region handling with model-specific defaults
    - Version pinning and latest version detection
    - Caching for performance
    """
    
    # Model metadata (static for now, could be loaded from API)
    MODEL_METADATA: Dict[str, ModelMetadata] = {
        "claude-4-5-sonnet": ModelMetadata(
            model_id="claude-4-5-sonnet",
            name="Claude 4.5 Sonnet",
            provider="anthropic",
            access_pattern="native_sdk",
            available_regions=["us-east5", "europe-west1"],
            default_region="us-east5",
            latest_version="@20250929",
            versions=["@20250929", "@20241022"],
        ),
        "claude-3-5-sonnet": ModelMetadata(
            model_id="claude-3-5-sonnet",
            name="Claude 3.5 Sonnet",
            provider="anthropic",
            access_pattern="native_sdk",
            available_regions=["us-east5", "europe-west1"],
            default_region="us-east5",
            latest_version="@20241022",
            versions=["@20241022"],
        ),
        "claude-3-opus": ModelMetadata(
            model_id="claude-3-opus",
            name="Claude 3 Opus",
            provider="anthropic",
            access_pattern="native_sdk",
            available_regions=["us-east5"],
            default_region="us-east5",
            latest_version="@20241022",
            versions=["@20241022"],
        ),
        "gemini-2-5-pro": ModelMetadata(
            model_id="gemini-2-5-pro",
            name="Gemini 2.5 Pro",
            provider="google",
            access_pattern="native_sdk",
            available_regions=["us-central1", "us-east5"],
            default_region="us-central1",
            latest_version="latest",
            versions=["latest"],
        ),
        "gemini-1-5-pro": ModelMetadata(
            model_id="gemini-1-5-pro",
            name="Gemini 1.5 Pro",
            provider="google",
            access_pattern="native_sdk",
            available_regions=["us-central1", "us-east5"],
            default_region="us-central1",
            latest_version="latest",
            versions=["latest"],
        ),
        "gemini-1-5-flash": ModelMetadata(
            model_id="gemini-1-5-flash",
            name="Gemini 1.5 Flash",
            provider="google",
            access_pattern="native_sdk",
            available_regions=["us-central1", "us-east5"],
            default_region="us-central1",
            latest_version="latest",
            versions=["latest"],
        ),
        "qwen-coder": ModelMetadata(
            model_id="qwen-coder",
            name="Qwen Coder",
            provider="qwen",
            access_pattern="maas",
            available_regions=["us-south1"],
            default_region="us-south1",
            latest_version="@20241022",
            versions=["@20241022"],
        ),
        "qwen-2-5-coder": ModelMetadata(
            model_id="qwen-2-5-coder",
            name="Qwen 2.5 Coder",
            provider="qwen",
            access_pattern="maas",
            available_regions=["us-south1"],
            default_region="us-south1",
            latest_version="@20241022",
            versions=["@20241022"],
        ),
    }
    
    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize model registry.
        
        Args:
            cache_ttl: Cache TTL in seconds (default: 1 hour)
        """
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        logger.info("ModelRegistry initialized")
    
    def get_available_models(
        self,
        project_id: str,
        region: Optional[str] = None,
        use_cache: bool = True,
    ) -> List[Dict]:
        """
        Get list of available models.
        
        Args:
            project_id: GCP project ID (for future API calls)
            region: Optional region filter
            use_cache: Whether to use cached results
        
        Returns:
            List of model dictionaries
        """
        cache_key = f"{project_id}:{region or 'all'}"
        
        # Check cache
        if use_cache and cache_key in self._cache:
            cache_time = self._cache_timestamp.get(cache_key)
            if cache_time and datetime.utcnow() - cache_time < timedelta(seconds=self.cache_ttl):
                logger.debug("Returning cached model list", cache_key=cache_key)
                return self._cache[cache_key]
        
        # Build model list
        models = []
        for model_id, metadata in self.MODEL_METADATA.items():
            model_dict = metadata.to_dict()
            
            # Filter by region if specified
            if region:
                if region not in metadata.available_regions:
                    continue
                model_dict["available_in_region"] = True
            else:
                model_dict["available_in_region"] = None
            
            models.append(model_dict)
        
        # Cache results
        if use_cache:
            self._cache[cache_key] = models
            self._cache_timestamp[cache_key] = datetime.utcnow()
        
        logger.info("Retrieved available models", count=len(models), region=region)
        return models
    
    def get_model_metadata(self, model_id: str) -> Optional[ModelMetadata]:
        """
        Get metadata for a specific model.
        
        Args:
            model_id: Model identifier
        
        Returns:
            ModelMetadata if found, None otherwise
        """
        return self.MODEL_METADATA.get(model_id.lower())
    
    def validate_model_availability(
        self,
        model_id: str,
        region: str,
    ) -> bool:
        """
        Validate that a model is available in the specified region.
        
        Args:
            model_id: Model identifier
            region: GCP region
        
        Returns:
            bool: True if model is available
        
        Raises:
            ModelNotFoundError: If model is not available with details
        """
        model_id_lower = model_id.lower()
        metadata = self.get_model_metadata(model_id_lower)
        
        if not metadata:
            raise ModelNotFoundError(
                f"Model '{model_id}' not found",
                model_id=model_id,
                region=region,
                available_regions=None,
            )
        
        if region not in metadata.available_regions:
            raise ModelNotFoundError(
                f"Model '{model_id}' not available in region '{region}'",
                model_id=model_id,
                region=region,
                available_regions=metadata.available_regions,
            )
        
        logger.debug("Model availability validated", model=model_id, region=region)
        return True
    
    def get_default_region(self, model_id: str) -> Optional[str]:
        """
        Get default region for a model.
        
        Args:
            model_id: Model identifier
        
        Returns:
            Default region if found, None otherwise
        """
        metadata = self.get_model_metadata(model_id)
        if metadata:
            return metadata.default_region
        return None
    
    def get_available_regions(self, model_id: str) -> List[str]:
        """
        Get available regions for a model.
        
        Args:
            model_id: Model identifier
        
        Returns:
            List of available regions
        """
        metadata = self.get_model_metadata(model_id)
        if metadata:
            return metadata.available_regions
        return []
    
    def detect_access_pattern(self, model_id: str) -> str:
        """
        Detect access pattern for a model.
        
        Args:
            model_id: Model identifier
        
        Returns:
            'native_sdk' or 'maas'
        """
        metadata = self.get_model_metadata(model_id)
        if metadata:
            return metadata.access_pattern
        
        # Fallback to prefix detection
        if model_id.lower().startswith("claude") or model_id.lower().startswith("gemini"):
            return "native_sdk"
        elif model_id.lower().startswith("qwen"):
            return "maas"
        
        # Default to native SDK
        return "native_sdk"
    
    def get_latest_version(self, model_id: str) -> Optional[str]:
        """
        Get latest version for a model.
        
        Args:
            model_id: Model identifier
        
        Returns:
            Latest version identifier if found, None otherwise
        """
        metadata = self.get_model_metadata(model_id)
        if metadata:
            return metadata.latest_version
        return None
    
    def validate_version(self, model_id: str, version: str) -> bool:
        """
        Validate that a version is available for a model.
        
        Args:
            model_id: Model identifier
            version: Version identifier
        
        Returns:
            bool: True if version is valid
        
        Raises:
            ModelNotFoundError: If version is not valid
        """
        metadata = self.get_model_metadata(model_id)
        if not metadata:
            raise ModelNotFoundError(
                f"Model '{model_id}' not found",
                model_id=model_id,
                region=None,
            )
        
        if version not in metadata.versions and metadata.versions:
            raise ModelNotFoundError(
                f"Version '{version}' not available for model '{model_id}'. "
                f"Available versions: {', '.join(metadata.versions)}",
                model_id=model_id,
                region=None,
            )
        
        return True
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._cache_timestamp.clear()
        logger.debug("Model registry cache cleared")

