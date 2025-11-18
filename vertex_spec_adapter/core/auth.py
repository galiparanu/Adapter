"""Authentication management for Vertex Spec Adapter."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from google.auth import default as google_auth_default
from google.auth.exceptions import DefaultCredentialsError
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from vertex_spec_adapter.core.exceptions import AuthenticationError
from vertex_spec_adapter.schemas.config import AuthMethod, VertexConfig
from vertex_spec_adapter.utils.logging import get_logger

logger = get_logger(__name__)


class CachedCredentials:
    """Wrapper around Google Auth Credentials with caching."""
    
    def __init__(
        self,
        credentials,
        credential_type: str,
        path: Optional[str] = None
    ):
        """
        Initialize cached credentials.
        
        Args:
            credentials: Google Auth credentials object
            credential_type: Type of credentials (service_account, user_credentials, adc, workload_identity)
            path: Optional path to credential file
        """
        self.credentials = credentials
        self.credential_type = credential_type
        self.path = path
        self.valid = False
        self.expired = False
        self.expires_at: Optional[datetime] = None
        self.last_validated: Optional[datetime] = None
        self.cached = True
        
        # Update expiry from credentials if available
        if hasattr(credentials, 'expiry') and credentials.expiry:
            self.expires_at = credentials.expiry
            self.expired = datetime.utcnow() >= credentials.expiry
    
    def is_valid(self) -> bool:
        """Check if credentials are currently valid."""
        if not self.credentials:
            return False
        
        # Check expiry
        if self.expires_at and datetime.utcnow() >= self.expires_at:
            self.expired = True
            return False
        
        # Check if credentials have expiry attribute
        if hasattr(self.credentials, 'expiry'):
            if self.credentials.expiry and datetime.utcnow() >= self.credentials.expiry:
                self.expired = True
                return False
        
        self.expired = False
        return True
    
    def needs_refresh(self) -> bool:
        """Check if credentials need refresh."""
        return self.expired or not self.is_valid()


class AuthenticationManager:
    """
    Manages GCP authentication with multiple methods and credential caching.
    
    Supports:
    - Service account key files
    - User credentials (gcloud auth login)
    - Application Default Credentials (ADC)
    - Automatic credential refresh
    - Credential caching with expiry tracking
    """
    
    def __init__(self, config: Optional[VertexConfig] = None):
        """
        Initialize authentication manager.
        
        Args:
            config: Optional configuration object
        """
        self.config = config
        self._cached_credentials: Optional[CachedCredentials] = None
        self._cache_ttl = timedelta(hours=1)  # Cache credentials for 1 hour
    
    def authenticate(
        self,
        credentials_path: Optional[str] = None,
        auth_method: Optional[AuthMethod] = None
    ):
        """
        Authenticate using available credentials in priority order.
        
        Priority order:
        1. Service account key file (via credentials_path or GOOGLE_APPLICATION_CREDENTIALS)
        2. User credentials (gcloud auth login)
        3. Application Default Credentials (ADC)
        
        Args:
            credentials_path: Optional path to service account key file
            auth_method: Optional preferred authentication method
        
        Returns:
            Valid Credentials object
        
        Raises:
            AuthenticationError: If no valid credentials found
        """
        # Use cached credentials if valid
        if self._cached_credentials and self._cached_credentials.is_valid():
            logger.debug("Using cached credentials", credential_type=self._cached_credentials.credential_type)
            return self._cached_credentials.credentials
        
        # Determine authentication method
        method = auth_method or (self.config.auth_method if self.config else AuthMethod.AUTO)
        
        if method == AuthMethod.AUTO:
            # Try methods in priority order
            credentials = self._try_service_account(credentials_path)
            if credentials:
                return credentials
            
            credentials = self._try_user_credentials()
            if credentials:
                return credentials
            
            credentials = self._try_adc()
            if credentials:
                return credentials
        else:
            # Try specific method
            if method == AuthMethod.SERVICE_ACCOUNT:
                credentials = self._try_service_account(credentials_path)
            elif method == AuthMethod.USER_CREDENTIALS:
                credentials = self._try_user_credentials()
            elif method == AuthMethod.ADC:
                credentials = self._try_adc()
            else:
                credentials = None
            
            if credentials:
                return credentials
        
        # No credentials found
        raise AuthenticationError(
            "No valid credentials found",
            code="AUTH_001",
            suggested_fix=(
                "Run 'gcloud auth login' to authenticate, "
                "set GOOGLE_APPLICATION_CREDENTIALS environment variable, "
                "or provide a service account key file"
            )
        )
    
    def _try_service_account(self, credentials_path: Optional[str] = None):
        """Try service account authentication."""
        try:
            path = credentials_path or self.get_credentials_path()
            if not path:
                return None
            
            path_obj = Path(path)
            if not path_obj.exists():
                logger.warning("Service account file not found", path=path)
                return None
            
            if not path_obj.is_file():
                raise AuthenticationError(
                    f"Service account path is not a file: {path}",
                    code="AUTH_002",
                    suggested_fix="Verify the path points to a valid service account key file"
                )
            
            # Load service account credentials
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
            except (json.JSONDecodeError, ValueError) as e:
                raise AuthenticationError(
                    f"Service account key file is invalid or corrupted: {e}",
                    code="AUTH_002",
                    suggested_fix="Verify service account key file is valid JSON"
                ) from e
            
            # Refresh if needed
            if credentials.expired:
                credentials.refresh(Request())
            
            # Cache credentials
            cached = CachedCredentials(credentials, "service_account", path=path)
            cached.valid = True
            cached.last_validated = datetime.utcnow()
            self._cached_credentials = cached
            
            logger.info("Authenticated with service account", path=path)
            return credentials
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.warning("Service account authentication failed", error=str(e))
            return None
    
    def _try_user_credentials(self):
        """Try user credentials authentication (gcloud auth login)."""
        try:
            # Try to get user credentials
            credentials, project = google_auth_default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
            
            # Check if these are user credentials (not service account)
            if hasattr(credentials, 'service_account_email'):
                # This is actually a service account, skip
                return None
            
            # Refresh if needed
            if credentials.expired:
                credentials.refresh(Request())
            
            # Cache credentials
            cached = CachedCredentials(credentials, "user_credentials")
            cached.valid = True
            cached.last_validated = datetime.utcnow()
            self._cached_credentials = cached
            
            logger.info("Authenticated with user credentials")
            return credentials
            
        except DefaultCredentialsError:
            return None
        except Exception as e:
            logger.warning("User credentials authentication failed", error=str(e))
            return None
    
    def _try_adc(self):
        """Try Application Default Credentials."""
        try:
            credentials, project = google_auth_default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
            
            # Refresh if needed
            if credentials.expired:
                credentials.refresh(Request())
            
            # Cache credentials
            cached = CachedCredentials(credentials, "adc")
            cached.valid = True
            cached.last_validated = datetime.utcnow()
            self._cached_credentials = cached
            
            logger.info("Authenticated with Application Default Credentials")
            return credentials
            
        except DefaultCredentialsError:
            return None
        except Exception as e:
            logger.warning("ADC authentication failed", error=str(e))
            return None
    
    def validate_credentials(self, credentials) -> bool:
        """
        Validate that credentials are valid and not expired.
        
        Args:
            credentials: Credentials object to validate
        
        Returns:
            bool: True if credentials are valid
        
        Raises:
            AuthenticationError: If credentials are invalid and cannot be refreshed
        """
        if not credentials:
            raise AuthenticationError(
                "Credentials are None",
                code="AUTH_003",
                suggested_fix="Re-authenticate using 'vertex-spec init' or set credentials"
            )
        
        # Check expiry
        if hasattr(credentials, 'expiry') and credentials.expiry:
            if datetime.utcnow() >= credentials.expiry:
                # Try to refresh
                try:
                    credentials.refresh(Request())
                    logger.debug("Credentials refreshed successfully")
                    return True
                except Exception as e:
                    raise AuthenticationError(
                        f"Credentials expired and refresh failed: {e}",
                        code="AUTH_003",
                        suggested_fix="Re-authenticate using 'gcloud auth login' or set new credentials"
                    ) from e
        
        return True
    
    def refresh_credentials(self, credentials):
        """
        Refresh expired credentials.
        
        Args:
            credentials: Expired credentials to refresh
        
        Returns:
            Refreshed Credentials object
        
        Raises:
            AuthenticationError: If refresh fails
        """
        try:
            if hasattr(credentials, 'refresh'):
                credentials.refresh(Request())
                logger.debug("Credentials refreshed successfully")
                
                # Update cache
                if self._cached_credentials:
                    self._cached_credentials.credentials = credentials
                    self._cached_credentials.valid = True
                    self._cached_credentials.expired = False
                    self._cached_credentials.last_validated = datetime.utcnow()
                    if hasattr(credentials, 'expiry'):
                        self._cached_credentials.expires_at = credentials.expiry
                
                return credentials
            else:
                raise AuthenticationError(
                    "Credentials do not support refresh",
                    code="AUTH_003",
                    suggested_fix="Re-authenticate with new credentials"
                )
        except Exception as e:
            raise AuthenticationError(
                f"Failed to refresh credentials: {e}",
                code="AUTH_003",
                suggested_fix="Re-authenticate using 'gcloud auth login' or set new credentials"
            ) from e
    
    def get_credentials_path(self) -> Optional[str]:
        """
        Get path to credentials file from environment or config.
        
        Returns:
            Path to credentials file, or None if not found
        """
        # Check environment variable first
        env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if env_path:
            return env_path
        
        # Check config
        if self.config and self.config.service_account_path:
            return self.config.service_account_path
        
        return None
    
    def clear_cache(self) -> None:
        """
        Clear cached credentials.
        
        Useful for testing or when credentials need to be reloaded.
        """
        self._cached_credentials = None
        logger.debug("Credential cache cleared")

