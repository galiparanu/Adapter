"""Unit tests for configuration schema."""

import pytest
from pydantic import ValidationError

from vertex_spec_adapter.schemas.config import (
    AuthMethod,
    LogFormat,
    LogLevel,
    VertexConfig,
)


class TestVertexConfig:
    """Test VertexConfig schema."""
    
    def test_valid_config(self):
        """Test valid configuration."""
        config = VertexConfig(
            project_id="my-project-123",
            model="claude-4-5-sonnet"
        )
        assert config.project_id == "my-project-123"
        assert config.model == "claude-4-5-sonnet"
        assert config.auth_method == AuthMethod.AUTO
        assert config.max_retries == 3
        assert config.log_level == LogLevel.INFO
    
    def test_config_with_all_fields(self):
        """Test configuration with all fields."""
        config = VertexConfig(
            project_id="my-project-123",
            region="us-central1",
            model="gemini-2-5-pro",
            model_version="@20250929",
            model_regions={"claude-4-5-sonnet": "us-east5"},
            auth_method=AuthMethod.SERVICE_ACCOUNT,
            max_retries=5,
            retry_backoff_factor=2.0,
            timeout=120,
            log_level=LogLevel.DEBUG,
            log_format=LogFormat.JSON,
            enable_cost_tracking=False
        )
        assert config.region == "us-central1"
        assert config.model_version == "@20250929"
        assert config.model_regions == {"claude-4-5-sonnet": "us-east5"}
        assert config.auth_method == AuthMethod.SERVICE_ACCOUNT
    
    def test_invalid_project_id_format(self):
        """Test invalid project ID format."""
        with pytest.raises(ValidationError) as exc_info:
            VertexConfig(
                project_id="INVALID_PROJECT",  # Must be lowercase
                model="claude-4-5-sonnet"
            )
        assert "project_id" in str(exc_info.value).lower()
        assert "invalid" in str(exc_info.value).lower()
    
    def test_invalid_project_id_too_short(self):
        """Test project ID that's too short."""
        with pytest.raises(ValidationError):
            VertexConfig(
                project_id="abc",
                model="claude-4-5-sonnet"
            )
    
    def test_invalid_region_format(self):
        """Test invalid region format."""
        with pytest.raises(ValidationError) as exc_info:
            VertexConfig(
                project_id="my-project-123",
                model="claude-4-5-sonnet",
                region="invalid-region-format"
            )
        assert "region" in str(exc_info.value).lower()
    
    def test_valid_region_formats(self):
        """Test valid region formats."""
        valid_regions = ["us-central1", "us-east5", "europe-west1", "global"]
        for region in valid_regions:
            config = VertexConfig(
                project_id="my-project-123",
                model="claude-4-5-sonnet",
                region=region
            )
            assert config.region == region
    
    def test_invalid_model_version_format(self):
        """Test invalid model version format."""
        with pytest.raises(ValidationError) as exc_info:
            VertexConfig(
                project_id="my-project-123",
                model="claude-4-5-sonnet",
                model_version="invalid-version"
            )
        assert "model_version" in str(exc_info.value).lower()
    
    def test_valid_model_version_formats(self):
        """Test valid model version formats."""
        valid_versions = ["@20250929", "@20241022", "@latest"]
        for version in valid_versions:
            config = VertexConfig(
                project_id="my-project-123",
                model="claude-4-5-sonnet",
                model_version=version
            )
            assert config.model_version == version
    
    def test_invalid_max_retries_range(self):
        """Test invalid max_retries range."""
        with pytest.raises(ValidationError):
            VertexConfig(
                project_id="my-project-123",
                model="claude-4-5-sonnet",
                max_retries=10  # Must be 0-5
            )
    
    def test_invalid_retry_backoff_factor(self):
        """Test invalid retry_backoff_factor."""
        with pytest.raises(ValidationError):
            VertexConfig(
                project_id="my-project-123",
                model="claude-4-5-sonnet",
                retry_backoff_factor=-1.0  # Must be > 0
            )
    
    def test_invalid_timeout(self):
        """Test invalid timeout."""
        with pytest.raises(ValidationError):
            VertexConfig(
                project_id="my-project-123",
                model="claude-4-5-sonnet",
                timeout=0  # Must be > 0
            )
    
    def test_service_account_path_validation(self, tmp_path):
        """Test service account path validation."""
        # Test with non-existent file
        with pytest.raises(ValidationError) as exc_info:
            VertexConfig(
                project_id="my-project-123",
                model="claude-4-5-sonnet",
                service_account_path="/nonexistent/path.json"
            )
        assert "not found" in str(exc_info.value).lower()
        
        # Test with existing file
        sa_file = tmp_path / "sa.json"
        sa_file.write_text('{"type": "service_account"}')
        
        config = VertexConfig(
            project_id="my-project-123",
            model="claude-4-5-sonnet",
            service_account_path=str(sa_file)
        )
        assert config.service_account_path == str(sa_file)
    
    def test_default_values(self):
        """Test default values."""
        config = VertexConfig(
            project_id="my-project-123",
            model="claude-4-5-sonnet"
        )
        assert config.auth_method == AuthMethod.AUTO
        assert config.max_retries == 3
        assert config.retry_backoff_factor == 1.0
        assert config.timeout == 60
        assert config.log_level == LogLevel.INFO
        assert config.log_format == LogFormat.TEXT
        assert config.enable_cost_tracking is True
    
    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VertexConfig(
                project_id="my-project-123",
                model="claude-4-5-sonnet",
                extra_field="not allowed"
            )
        assert "extra" in str(exc_info.value).lower() or "forbidden" in str(exc_info.value).lower()

