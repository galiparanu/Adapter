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
        context_window: Optional[str] = None,
        pricing: Optional[Dict[str, float]] = None,
        capabilities: Optional[List[str]] = None,
        description: Optional[str] = None,
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
            context_window: Context window size in human-readable format (e.g., "1M tokens")
            pricing: Pricing per token as dict with "input" and/or "output" keys (per 1K tokens)
            capabilities: List of model capabilities and specializations
            description: Model description and use cases
        """
        self.model_id = model_id
        self.name = name
        self.provider = provider
        self.access_pattern = access_pattern
        self.available_regions = available_regions
        self.default_region = default_region or (available_regions[0] if available_regions else None)
        self.latest_version = latest_version
        self.versions = versions or []
        
        # Extended fields for interactive menu
        self.context_window = context_window
        self.pricing = pricing
        self.capabilities = capabilities
        self.description = description
        
        # Validate new fields if provided
        self._validate_extended_fields()
    
    def _validate_extended_fields(self) -> None:
        """
        Validate extended fields according to data-model.md specifications.
        
        Raises:
            ValueError: If validation fails
        """
        # Validate context_window: Must be non-empty string if provided
        if self.context_window is not None and not isinstance(self.context_window, str):
            raise ValueError("context_window must be a string or None")
        if self.context_window is not None and len(self.context_window.strip()) == 0:
            raise ValueError("context_window must be non-empty if provided")
        
        # Validate pricing: Must have "input" and/or "output" keys, values must be >= 0
        if self.pricing is not None:
            if not isinstance(self.pricing, dict):
                raise ValueError("pricing must be a dictionary or None")
            if not any(key in self.pricing for key in ["input", "output"]):
                raise ValueError("pricing must have 'input' and/or 'output' keys")
            for key, value in self.pricing.items():
                if key not in ["input", "output"]:
                    raise ValueError(f"pricing contains invalid key: {key}. Only 'input' and 'output' allowed")
                if not isinstance(value, (int, float)) or value < 0:
                    raise ValueError(f"pricing.{key} must be a non-negative number")
        
        # Validate capabilities: Must be non-empty list if provided
        if self.capabilities is not None:
            if not isinstance(self.capabilities, list):
                raise ValueError("capabilities must be a list or None")
            if len(self.capabilities) == 0:
                raise ValueError("capabilities must be non-empty if provided")
            if not all(isinstance(cap, str) for cap in self.capabilities):
                raise ValueError("all capabilities must be strings")
        
        # Validate description: Must be non-empty string if provided
        if self.description is not None and not isinstance(self.description, str):
            raise ValueError("description must be a string or None")
        if self.description is not None and len(self.description.strip()) == 0:
            raise ValueError("description must be non-empty if provided")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        result = {
            "id": self.model_id,
            "name": self.name,
            "provider": self.provider,
            "access_pattern": self.access_pattern,
            "available_regions": self.available_regions,
            "default_region": self.default_region,
            "latest_version": self.latest_version,
            "versions": self.versions,
        }
        
        # Add extended fields if they are not None
        if self.context_window is not None:
            result["context_window"] = self.context_window
        if self.pricing is not None:
            result["pricing"] = self.pricing
        if self.capabilities is not None:
            result["capabilities"] = self.capabilities
        if self.description is not None:
            result["description"] = self.description
        
        return result


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
    # Only 7 models from vertex-config.md are supported (per spec FR-004)
    MODEL_METADATA: Dict[str, ModelMetadata] = {
        # 1. DeepSeek V3.1
        "deepseek-ai/deepseek-v3.1-maas": ModelMetadata(
            model_id="deepseek-ai/deepseek-v3.1-maas",
            name="DeepSeek V3.1",
            provider="deepseek",
            access_pattern="maas",
            available_regions=["us-west2"],
            default_region="us-west2",
            latest_version="latest",
            versions=["latest"],
            # Extended fields (estimated values from research.md T003a)
            context_window=None,  # TBD - research required
            pricing=None,  # TBD - research required
            capabilities=["general-purpose", "code-generation", "reasoning"],
            description="Advanced general-purpose model optimized for code generation and complex reasoning tasks",
        ),
        # 2. Qwen Coder
        "qwen/qwen3-coder-480b-a35b-instruct-maas": ModelMetadata(
            model_id="qwen/qwen3-coder-480b-a35b-instruct-maas",
            name="Qwen Coder",
            provider="qwen",
            access_pattern="maas",
            available_regions=["us-south1"],
            default_region="us-south1",
            latest_version="latest",
            versions=["latest"],
            # Extended fields (estimated values from research.md T003a)
            context_window=None,  # TBD - research required
            pricing={"input": 0.10, "output": 0.40},  # Per 1M tokens (from existing metrics.py, verify)
            capabilities=["code-generation", "debugging", "code-analysis"],
            description="Specialized code generation model optimized for programming tasks, debugging, and code analysis",
        ),
        # 3. Gemini 2.5 Pro
        "gemini-2.5-pro": ModelMetadata(
            model_id="gemini-2.5-pro",
            name="Gemini 2.5 Pro",
            provider="google",
            access_pattern="native_sdk",
            available_regions=["global"],
            default_region="global",
            latest_version="latest",
            versions=["latest"],
            # Extended fields (estimated values from research.md T003a)
            context_window="1M+ tokens",  # Estimated - verify from official docs
            pricing={"input": 0.50, "output": 1.50},  # Per 1M tokens (from existing metrics.py, verify)
            capabilities=["general-purpose", "code-generation", "reasoning", "multimodal"],
            description="Advanced general-purpose model with strong reasoning capabilities, code generation, and multimodal support",
        ),
        # 4. DeepSeek R1 0528
        "deepseek-ai/deepseek-r1-0528-maas": ModelMetadata(
            model_id="deepseek-ai/deepseek-r1-0528-maas",
            name="DeepSeek R1 0528",
            provider="deepseek",
            access_pattern="maas",
            available_regions=["us-central1"],
            default_region="us-central1",
            latest_version="latest",
            versions=["latest"],
            # Extended fields (estimated values from research.md T003a)
            context_window=None,  # TBD - research required
            pricing=None,  # TBD - research required
            capabilities=["reasoning", "problem-solving", "chain-of-thought"],
            description="Reasoning-focused model with advanced chain-of-thought capabilities for complex problem-solving",
        ),
        # 5. Kimi K2
        "moonshotai/kimi-k2-thinking-maas": ModelMetadata(
            model_id="moonshotai/kimi-k2-thinking-maas",
            name="Kimi K2",
            provider="moonshotai",
            access_pattern="maas",
            available_regions=["global"],
            default_region="global",
            latest_version="latest",
            versions=["latest"],
            # Extended fields (estimated values from research.md T003a)
            context_window=None,  # TBD - research required (may be 200K+ tokens)
            pricing=None,  # TBD - research required
            capabilities=["reasoning", "thinking", "analysis"],
            description="Thinking-focused model optimized for complex reasoning and analysis tasks",
        ),
        # 6. GPT OSS 120B
        "openai/gpt-oss-120b-maas": ModelMetadata(
            model_id="openai/gpt-oss-120b-maas",
            name="GPT OSS 120B",
            provider="openai",
            access_pattern="maas",
            available_regions=["us-central1"],
            default_region="us-central1",
            latest_version="latest",
            versions=["latest"],
            # Extended fields (estimated values from research.md T003a)
            context_window=None,  # TBD - research required
            pricing=None,  # TBD - research required
            capabilities=["general-purpose", "large-scale"],
            description="Large-scale open-source model for general-purpose tasks",
        ),
        # 7. Llama 3.1
        "meta/llama-3.1-405b-instruct-maas": ModelMetadata(
            model_id="meta/llama-3.1-405b-instruct-maas",
            name="Llama 3.1",
            provider="meta",
            access_pattern="maas",
            available_regions=["us-central1"],
            default_region="us-central1",
            latest_version="latest",
            versions=["latest"],
            # Extended fields (estimated values from research.md T003a)
            context_window=None,  # TBD - research required (may be 128K+ tokens)
            pricing=None,  # TBD - research required
            capabilities=["general-purpose", "instruction-following", "conversation"],
            description="Large-scale instruction-tuned model optimized for following instructions and general conversation",
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
        
        # Fallback to prefix detection (for backward compatibility)
        model_id_lower = model_id.lower()
        if model_id_lower.startswith("claude") or model_id_lower.startswith("gemini"):
            return "native_sdk"
        elif model_id_lower.startswith("qwen") or model_id_lower.startswith("deepseek") or model_id_lower.startswith("kimi") or model_id_lower.startswith("gpt-oss") or model_id_lower.startswith("llama"):
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

