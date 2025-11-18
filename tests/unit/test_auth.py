"""Unit tests for AuthenticationManager."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account

from vertex_spec_adapter.core.auth import AuthenticationManager, CachedCredentials
from vertex_spec_adapter.core.exceptions import AuthenticationError
from vertex_spec_adapter.schemas.config import AuthMethod, VertexConfig


class TestCachedCredentials:
    """Test CachedCredentials class."""
    
    def test_cached_credentials_init(self):
        """Test CachedCredentials initialization."""
        mock_creds = MagicMock()
        mock_creds.expiry = None
        
        cached = CachedCredentials(mock_creds, "service_account", path="/path/to/key.json")
        
        assert cached.credentials == mock_creds
        assert cached.credential_type == "service_account"
        assert cached.path == "/path/to/key.json"
        assert cached.valid is False
        assert cached.expired is False
    
    def test_cached_credentials_with_expiry(self):
        """Test CachedCredentials with expiry."""
        mock_creds = MagicMock()
        future_time = datetime.utcnow() + timedelta(hours=1)
        mock_creds.expiry = future_time
        
        cached = CachedCredentials(mock_creds, "service_account")
        
        assert cached.expires_at == future_time
        assert cached.expired is False
    
    def test_cached_credentials_expired(self):
        """Test CachedCredentials with expired credentials."""
        mock_creds = MagicMock()
        past_time = datetime.utcnow() - timedelta(hours=1)
        mock_creds.expiry = past_time
        
        cached = CachedCredentials(mock_creds, "service_account")
        
        assert cached.expired is True
        assert cached.is_valid() is False
    
    def test_cached_credentials_needs_refresh(self):
        """Test needs_refresh method."""
        mock_creds = MagicMock()
        past_time = datetime.utcnow() - timedelta(hours=1)
        mock_creds.expiry = past_time
        
        cached = CachedCredentials(mock_creds, "service_account")
        
        assert cached.needs_refresh() is True


class TestAuthenticationManager:
    """Test AuthenticationManager class."""
    
    def test_init_without_config(self):
        """Test AuthenticationManager initialization without config."""
        manager = AuthenticationManager()
        
        assert manager.config is None
        assert manager._cached_credentials is None
    
    def test_init_with_config(self):
        """Test AuthenticationManager initialization with config."""
        config = VertexConfig(
            project_id="test-project",
            model="claude-4-5-sonnet",
            auth_method=AuthMethod.SERVICE_ACCOUNT,
        )
        manager = AuthenticationManager(config=config)
        
        assert manager.config == config
    
    def test_get_credentials_path_from_env(self, monkeypatch):
        """Test getting credentials path from environment variable."""
        monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/env/path/key.json")
        
        manager = AuthenticationManager()
        path = manager.get_credentials_path()
        
        assert path == "/env/path/key.json"
    
    def test_get_credentials_path_from_config(self):
        """Test getting credentials path from config."""
        config = VertexConfig(
            project_id="test-project",
            model="claude-4-5-sonnet",
            service_account_path="/config/path/key.json",
        )
        manager = AuthenticationManager(config=config)
        path = manager.get_credentials_path()
        
        assert path == "/config/path/key.json"
    
    def test_get_credentials_path_none(self):
        """Test getting credentials path when not set."""
        manager = AuthenticationManager()
        path = manager.get_credentials_path()
        
        assert path is None
    
    def test_clear_cache(self):
        """Test clearing credential cache."""
        manager = AuthenticationManager()
        manager._cached_credentials = CachedCredentials(MagicMock(), "service_account")
        
        manager.clear_cache()
        
        assert manager._cached_credentials is None
    
    @patch("vertex_spec_adapter.core.auth.service_account.Credentials.from_service_account_file")
    def test_try_service_account_success(self, mock_from_file, tmp_path):
        """Test successful service account authentication."""
        key_file = tmp_path / "key.json"
        key_file.write_text(json.dumps({
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
        }))
        
        mock_creds = MagicMock()
        mock_creds.expired = False
        mock_creds.expiry = None
        mock_from_file.return_value = mock_creds
        
        manager = AuthenticationManager()
        credentials = manager._try_service_account(str(key_file))
        
        assert credentials == mock_creds
        assert manager._cached_credentials is not None
        assert manager._cached_credentials.credential_type == "service_account"
    
    def test_try_service_account_file_not_found(self):
        """Test service account authentication with file not found."""
        manager = AuthenticationManager()
        credentials = manager._try_service_account("/nonexistent/key.json")
        
        assert credentials is None
    
    def test_try_service_account_invalid_file(self, tmp_path):
        """Test service account authentication with invalid file."""
        key_file = tmp_path / "key.json"
        key_file.write_text("invalid json")
        
        manager = AuthenticationManager()
        
        with pytest.raises(AuthenticationError) as exc_info:
            manager._try_service_account(str(key_file))
        
        assert "invalid or corrupted" in str(exc_info.value).lower()
    
    @patch("vertex_spec_adapter.core.auth.google_auth_default")
    def test_try_user_credentials_success(self, mock_default):
        """Test successful user credentials authentication."""
        mock_creds = MagicMock()
        mock_creds.expired = False
        mock_creds.expiry = None
        # User credentials don't have service_account_email
        mock_default.return_value = (mock_creds, "test-project")
        
        manager = AuthenticationManager()
        credentials = manager._try_user_credentials()
        
        assert credentials == mock_creds
        assert manager._cached_credentials is not None
        assert manager._cached_credentials.credential_type == "user_credentials"
    
    @patch("vertex_spec_adapter.core.auth.google_auth_default")
    def test_try_user_credentials_service_account(self, mock_default):
        """Test user credentials authentication when service account is returned."""
        mock_creds = MagicMock()
        mock_creds.service_account_email = "test@test-project.iam.gserviceaccount.com"
        mock_default.return_value = (mock_creds, "test-project")
        
        manager = AuthenticationManager()
        credentials = manager._try_user_credentials()
        
        # Should return None because it's actually a service account
        assert credentials is None
    
    @patch("vertex_spec_adapter.core.auth.google_auth_default")
    def test_try_user_credentials_failure(self, mock_default):
        """Test user credentials authentication failure."""
        mock_default.side_effect = DefaultCredentialsError("No credentials")
        
        manager = AuthenticationManager()
        credentials = manager._try_user_credentials()
        
        assert credentials is None
    
    @patch("vertex_spec_adapter.core.auth.google_auth_default")
    def test_try_adc_success(self, mock_default):
        """Test successful ADC authentication."""
        mock_creds = MagicMock()
        mock_creds.expired = False
        mock_creds.expiry = None
        mock_default.return_value = (mock_creds, "test-project")
        
        manager = AuthenticationManager()
        credentials = manager._try_adc()
        
        assert credentials == mock_creds
        assert manager._cached_credentials is not None
        assert manager._cached_credentials.credential_type == "adc"
    
    @patch("vertex_spec_adapter.core.auth.google_auth_default")
    def test_try_adc_failure(self, mock_default):
        """Test ADC authentication failure."""
        mock_default.side_effect = DefaultCredentialsError("No credentials")
        
        manager = AuthenticationManager()
        credentials = manager._try_adc()
        
        assert credentials is None
    
    @patch.object(AuthenticationManager, "_try_service_account")
    @patch.object(AuthenticationManager, "_try_user_credentials")
    @patch.object(AuthenticationManager, "_try_adc")
    def test_authenticate_auto_success(self, mock_adc, mock_user, mock_sa):
        """Test authenticate with AUTO method and successful service account."""
        mock_creds = MagicMock()
        mock_sa.return_value = mock_creds
        
        manager = AuthenticationManager()
        credentials = manager.authenticate(auth_method=AuthMethod.AUTO)
        
        assert credentials == mock_creds
        mock_sa.assert_called_once()
        # Should not try other methods if service account succeeds
        mock_user.assert_not_called()
        mock_adc.assert_not_called()
    
    @patch.object(AuthenticationManager, "_try_service_account")
    @patch.object(AuthenticationManager, "_try_user_credentials")
    @patch.object(AuthenticationManager, "_try_adc")
    def test_authenticate_auto_fallback(self, mock_adc, mock_user, mock_sa):
        """Test authenticate with AUTO method and fallback to user credentials."""
        mock_creds = MagicMock()
        mock_sa.return_value = None
        mock_user.return_value = mock_creds
        
        manager = AuthenticationManager()
        credentials = manager.authenticate(auth_method=AuthMethod.AUTO)
        
        assert credentials == mock_creds
        mock_sa.assert_called_once()
        mock_user.assert_called_once()
        mock_adc.assert_called_once()
    
    @patch.object(AuthenticationManager, "_try_service_account")
    @patch.object(AuthenticationManager, "_try_user_credentials")
    @patch.object(AuthenticationManager, "_try_adc")
    def test_authenticate_auto_all_fail(self, mock_adc, mock_user, mock_sa):
        """Test authenticate with AUTO method when all methods fail."""
        mock_sa.return_value = None
        mock_user.return_value = None
        mock_adc.return_value = None
        
        manager = AuthenticationManager()
        
        with pytest.raises(AuthenticationError) as exc_info:
            manager.authenticate(auth_method=AuthMethod.AUTO)
        
        assert "No valid credentials found" in str(exc_info.value)
        assert exc_info.value.code == "AUTH_001"
    
    def test_validate_credentials_valid(self):
        """Test validating valid credentials."""
        mock_creds = MagicMock()
        future_time = datetime.utcnow() + timedelta(hours=1)
        mock_creds.expiry = future_time
        
        manager = AuthenticationManager()
        is_valid = manager.validate_credentials(mock_creds)
        
        assert is_valid is True
    
    def test_validate_credentials_expired_refresh_success(self):
        """Test validating expired credentials that can be refreshed."""
        mock_creds = MagicMock()
        past_time = datetime.utcnow() - timedelta(hours=1)
        mock_creds.expiry = past_time
        mock_creds.refresh = MagicMock()
        
        manager = AuthenticationManager()
        is_valid = manager.validate_credentials(mock_creds)
        
        assert is_valid is True
        mock_creds.refresh.assert_called_once()
    
    def test_validate_credentials_expired_refresh_failure(self):
        """Test validating expired credentials that cannot be refreshed."""
        mock_creds = MagicMock()
        past_time = datetime.utcnow() - timedelta(hours=1)
        mock_creds.expiry = past_time
        mock_creds.refresh = MagicMock(side_effect=Exception("Refresh failed"))
        
        manager = AuthenticationManager()
        
        with pytest.raises(AuthenticationError) as exc_info:
            manager.validate_credentials(mock_creds)
        
        assert "expired and refresh failed" in str(exc_info.value).lower()
    
    def test_validate_credentials_none(self):
        """Test validating None credentials."""
        manager = AuthenticationManager()
        
        with pytest.raises(AuthenticationError) as exc_info:
            manager.validate_credentials(None)
        
        assert "Credentials are None" in str(exc_info.value)
    
    def test_refresh_credentials_success(self):
        """Test refreshing credentials successfully."""
        mock_creds = MagicMock()
        mock_creds.refresh = MagicMock()
        future_time = datetime.utcnow() + timedelta(hours=1)
        mock_creds.expiry = future_time
        
        manager = AuthenticationManager()
        refreshed = manager.refresh_credentials(mock_creds)
        
        assert refreshed == mock_creds
        mock_creds.refresh.assert_called_once()
        assert manager._cached_credentials is not None
    
    def test_refresh_credentials_failure(self):
        """Test refreshing credentials that fail."""
        mock_creds = MagicMock()
        mock_creds.refresh = MagicMock(side_effect=Exception("Refresh failed"))
        
        manager = AuthenticationManager()
        
        with pytest.raises(AuthenticationError) as exc_info:
            manager.refresh_credentials(mock_creds)
        
        assert "Failed to refresh credentials" in str(exc_info.value)
    
    def test_refresh_credentials_no_refresh_method(self):
        """Test refreshing credentials without refresh method."""
        mock_creds = MagicMock()
        del mock_creds.refresh
        
        manager = AuthenticationManager()
        
        with pytest.raises(AuthenticationError) as exc_info:
            manager.refresh_credentials(mock_creds)
        
        assert "do not support refresh" in str(exc_info.value).lower()

