"""Integration tests for authentication flow."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vertex_spec_adapter.core.auth import AuthenticationManager
from vertex_spec_adapter.core.exceptions import AuthenticationError
from vertex_spec_adapter.schemas.config import AuthMethod, VertexConfig


@pytest.mark.integration
class TestAuthenticationFlow:
    """Integration tests for authentication flow."""
    
    def test_service_account_authentication_flow(self, tmp_path, monkeypatch):
        """Test complete service account authentication flow."""
        # Create a mock service account key file
        key_file = tmp_path / "service-account-key.json"
        key_data = {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMOCK_KEY\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "123456789",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        key_file.write_text(json.dumps(key_data))
        
        # Set environment variable
        monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(key_file))
        
        config = VertexConfig(
            project_id="test-project",
            model="claude-4-5-sonnet",
            auth_method=AuthMethod.SERVICE_ACCOUNT,
        )
        
        manager = AuthenticationManager(config=config)
        
        # Test getting credentials path
        path = manager.get_credentials_path()
        assert path == str(key_file)
        
        # Note: Actual authentication would require valid credentials
        # This test verifies the flow structure
    
    def test_user_credentials_authentication_flow(self, monkeypatch):
        """Test user credentials authentication flow."""
        config = VertexConfig(
            project_id="test-project",
            model="claude-4-5-sonnet",
            auth_method=AuthMethod.USER_CREDENTIALS,
        )
        
        manager = AuthenticationManager(config=config)
        
        # Test that manager is initialized correctly
        assert manager.config == config
        assert manager.config.auth_method == AuthMethod.USER_CREDENTIALS
    
    def test_adc_authentication_flow(self):
        """Test ADC authentication flow."""
        config = VertexConfig(
            project_id="test-project",
            model="claude-4-5-sonnet",
            auth_method=AuthMethod.ADC,
        )
        
        manager = AuthenticationManager(config=config)
        
        # Test that manager is initialized correctly
        assert manager.config == config
        assert manager.config.auth_method == AuthMethod.ADC
    
    def test_auto_authentication_flow(self):
        """Test AUTO authentication method flow."""
        config = VertexConfig(
            project_id="test-project",
            model="claude-4-5-sonnet",
            auth_method=AuthMethod.AUTO,
        )
        
        manager = AuthenticationManager(config=config)
        
        # Test that manager is initialized correctly
        assert manager.config == config
        assert manager.config.auth_method == AuthMethod.AUTO
    
    def test_credential_caching(self, tmp_path):
        """Test credential caching behavior."""
        key_file = tmp_path / "service-account-key.json"
        key_data = {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMOCK_KEY\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
        }
        key_file.write_text(json.dumps(key_data))
        
        config = VertexConfig(
            project_id="test-project",
            model="claude-4-5-sonnet",
            service_account_path=str(key_file),
            auth_method=AuthMethod.SERVICE_ACCOUNT,
        )
        
        manager = AuthenticationManager(config=config)
        
        # Initially no cache
        assert manager._cached_credentials is None
        
        # Clear cache should work
        manager.clear_cache()
        assert manager._cached_credentials is None
    
    def test_credential_path_priority(self, tmp_path, monkeypatch):
        """Test credential path priority (env var over config)."""
        # Create config with path
        config_path = tmp_path / "config-key.json"
        config_path.write_text(json.dumps({"type": "service_account"}))
        
        config = VertexConfig(
            project_id="test-project",
            model="claude-4-5-sonnet",
            service_account_path=str(config_path),
        )
        
        # Set environment variable (should take priority)
        env_path = tmp_path / "env-key.json"
        env_path.write_text(json.dumps({"type": "service_account"}))
        monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(env_path))
        
        manager = AuthenticationManager(config=config)
        path = manager.get_credentials_path()
        
        # Environment variable should take priority
        assert path == str(env_path)
    
    def test_authentication_error_handling(self):
        """Test authentication error handling."""
        config = VertexConfig(
            project_id="test-project",
            model="claude-4-5-sonnet",
            auth_method=AuthMethod.SERVICE_ACCOUNT,
            service_account_path="/nonexistent/key.json",
        )
        
        manager = AuthenticationManager(config=config)
        
        # Should handle missing file gracefully
        path = manager.get_credentials_path()
        assert path == "/nonexistent/key.json"
        
        # Actual authentication would raise error, but path retrieval should work

