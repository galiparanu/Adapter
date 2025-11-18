"""Vertex Adapter Tool for Gemini CLI integration."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from vertex_spec_adapter.core.client import VertexAIClient
from vertex_spec_adapter.core.config import ConfigurationManager
from vertex_spec_adapter.core.exceptions import ConfigurationError
from vertex_spec_adapter.core.models import ModelRegistry
from vertex_spec_adapter.utils.logging import get_logger

logger = get_logger(__name__)


class VertexAdapterTool:
    """
    Tool wrapper untuk mengintegrasikan Vertex Adapter ke Gemini CLI.
    
    Tool ini memungkinkan Gemini CLI untuk menggunakan Vertex AI models
    (Claude, Gemini, Qwen) melalui Vertex Adapter.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Vertex Adapter Tool.
        
        Args:
            config_path: Optional path to config file
        """
        self.config_manager = ConfigurationManager(
            config_path=Path(config_path) if config_path else None
        )
        # REMOVED: Client caching to ensure always using latest config
        # self._client: Optional[VertexAIClient] = None
        self._model_registry = ModelRegistry()
        
        logger.info("VertexAdapterTool initialized", config_path=config_path)
    
    @property
    def name(self) -> str:
        """Tool name for Gemini CLI."""
        return "vertex_adapter"
    
    @property
    def description(self) -> str:
        """Tool description for Gemini CLI."""
        return (
            "Access Vertex AI models (Claude, Gemini, Qwen) through Vertex Adapter. "
            "Supports model switching, generation, and model information queries."
        )
    
    @property
    def schema(self) -> Dict[str, Any]:
        """
        Tool schema untuk Gemini CLI (Function Calling format).
        
        Returns:
            Tool schema dalam format Gemini Function Calling
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": [
                            "generate",
                            "list_models",
                            "switch_model",
                            "get_model_info",
                            "test_connection",
                        ],
                        "description": "Action to perform",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Prompt for generation (required for 'generate' action)",
                    },
                    "model_id": {
                        "type": "string",
                        "description": "Model ID (e.g., 'gemini-2-5-pro', 'claude-4-5-sonnet')",
                    },
                    "region": {
                        "type": "string",
                        "description": "GCP region (e.g., 'us-central1', 'us-east5')",
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperature for generation (0.0-2.0, default: 0.7)",
                        "minimum": 0.0,
                        "maximum": 2.0,
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum tokens to generate",
                    },
                    "provider": {
                        "type": "string",
                        "description": "Filter models by provider (e.g., 'google', 'anthropic')",
                    },
                },
                "required": ["action"],
            },
        }
    
    def _get_client(self, model_id: Optional[str] = None, region: Optional[str] = None) -> VertexAIClient:
        """
        Get or create VertexAIClient instance.
        
        ALWAYS creates a fresh client from the latest config to ensure model selection
        is always up-to-date, even if tool instance is cached by Gemini CLI.
        
        Args:
            model_id: Optional model ID to use (overrides config)
            region: Optional region to use (overrides config)
        
        Returns:
            Fresh VertexAIClient instance with latest config
        """
        try:
            # Always reload config to get latest model selection
            config = self.config_manager.reload()
        except ConfigurationError:
            raise ConfigurationError(
                "Configuration not found. Run 'vertex-spec init' or create .specify/config.yaml"
            )
        
        # Use provided model/region or config defaults
        use_model_id = model_id or config.model if config.model else "gemini-2-5-pro"
        use_region = region or config.region or "us-central1"
        
        # ALWAYS create a fresh client - no caching to ensure latest model is used
        # This is critical when Gemini CLI caches tool instances
        from vertex_spec_adapter.core.auth import AuthenticationManager
        
        auth_manager = AuthenticationManager(config=config)
        credentials = auth_manager.authenticate(auth_method=config.auth_method)
        
        client = VertexAIClient(
            project_id=config.project_id,
            region=use_region,
            model_id=use_model_id,
            model_version=config.model_version,
            credentials=credentials,
            config=config,
        )
        
        logger.info(
            "Fresh client created from latest config",
            model=use_model_id,
            region=use_region,
            config_model=config.model,
        )
        
        return client
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute tool action.
        
        Args:
            action: Action to perform
            **kwargs: Action-specific parameters
        
        Returns:
            Result dictionary
        """
        try:
            if action == "generate":
                return self._action_generate(**kwargs)
            elif action == "list_models":
                return self._action_list_models(**kwargs)
            elif action == "switch_model":
                return self._action_switch_model(**kwargs)
            elif action == "get_model_info":
                return self._action_get_model_info(**kwargs)
            elif action == "test_connection":
                return self._action_test_connection(**kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                }
        except Exception as e:
            logger.error("Tool execution failed", action=action, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }
    
    def _action_generate(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        region: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Vertex AI model."""
        if not prompt:
            return {"success": False, "error": "Prompt is required for generate action"}
        
        client = self._get_client(model_id=model_id, region=region)
        
        messages = [{"role": "user", "content": prompt}]
        response = client.generate(
            messages=messages,
            temperature=temperature or 0.7,
            max_tokens=max_tokens,
        )
        
        return {
            "success": True,
            "content": response,
            "model": client.model_id,
            "region": client.region,
            "token_usage": client.token_usage,
        }
    
    def _action_list_models(
        self,
        provider: Optional[str] = None,
        region: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """List available models."""
        try:
            config = self.config_manager.load_config()
            project_id = config.project_id
        except ConfigurationError:
            project_id = "default-project"  # Fallback
        
        models = self._model_registry.get_available_models(
            project_id=project_id,
            region=region,
            provider=provider,
        )
        
        return {
            "success": True,
            "models": [
                {
                    "id": model.get("id"),
                    "name": model.get("name"),
                    "provider": model.get("provider"),
                    "access_pattern": model.get("access_pattern"),
                    "default_region": model.get("default_region"),
                    "available_regions": model.get("available_regions", []),
                    "latest_version": model.get("latest_version"),
                }
                for model in models
            ],
            "count": len(models),
        }
    
    def _action_switch_model(
        self,
        model_id: str,
        region: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Switch to different model."""
        if not model_id:
            return {"success": False, "error": "model_id is required"}
        
        client = self._get_client(model_id=model_id, region=region)
        
        return {
            "success": True,
            "model": client.model_id,
            "region": client.region,
            "message": f"Switched to {client.model_id} in {client.region}",
        }
    
    def _action_get_model_info(
        self,
        model_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get information about a specific model."""
        if not model_id:
            return {"success": False, "error": "model_id is required"}
        
        metadata = self._model_registry.get_model_metadata(model_id.lower())
        if not metadata:
            return {
                "success": False,
                "error": f"Model '{model_id}' not found",
            }
        
        return {
            "success": True,
            "model": {
                "id": metadata.model_id,
                "name": metadata.name,
                "provider": metadata.provider,
                "access_pattern": metadata.access_pattern,
                "default_region": metadata.default_region,
                "available_regions": metadata.available_regions,
                "latest_version": metadata.latest_version,
                "versions": metadata.versions,
            },
        }
    
    def _action_test_connection(self, **kwargs) -> Dict[str, Any]:
        """Test connection to Vertex AI."""
        try:
            client = self._get_client()
            
            # Test dengan simple prompt
            test_response = client.generate(
                [{"role": "user", "content": "Hello"}],
                temperature=0.1,
                max_tokens=10,
            )
            
            return {
                "success": True,
                "message": "Connection successful",
                "model": client.model_id,
                "region": client.region,
                "test_response": test_response[:50] if test_response else "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }


def create_tool(config_path: Optional[str] = None) -> VertexAdapterTool:
    """
    Factory function untuk create VertexAdapterTool.
    
    Always creates a fresh instance to ensure latest config is used.
    
    Args:
        config_path: Optional path to config file
    
    Returns:
        Fresh VertexAdapterTool instance
    """
    return VertexAdapterTool(config_path=config_path)


def execute_tool_action(action: str, **kwargs) -> Dict[str, Any]:
    """
    Static wrapper for tool execution that always uses fresh instance.
    
    This ensures that even if Gemini CLI caches tool instances, we always
    use the latest config and create fresh clients.
    
    Args:
        action: Action to perform
        **kwargs: Action-specific parameters
    
    Returns:
        Result dictionary
    """
    # Always create fresh tool instance
    tool = create_tool()
    return tool.execute(action, **kwargs)

