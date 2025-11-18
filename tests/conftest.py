"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
import os


@pytest.fixture
def mock_vertex_response():
    """Fixture for mocked Vertex AI response."""
    response = Mock()
    response.content = [Mock(text="This is a test response")]
    response.usage = Mock(input_tokens=10, output_tokens=15)
    return response


@pytest.fixture
def mock_credentials():
    """Fixture for mocked Google credentials."""
    creds = MagicMock()
    creds.valid = True
    creds.expired = False
    creds.token = "mock_token_123"
    return creds


@pytest.fixture
def sample_config():
    """Fixture for sample configuration."""
    return {
        'project_id': 'test-project-123',
        'region': 'us-central1',
        'model': 'claude-4-5-sonnet',
        'max_tokens': 4096,
        'temperature': 0.7,
    }


@pytest.fixture
def mock_api_responses():
    """Fixture providing various API response scenarios."""
    return {
        'success': {
            'content': [{'text': 'Success response'}],
            'usage': {'input_tokens': 10, 'output_tokens': 20}
        },
        'rate_limit': {
            'error': {'code': 429, 'message': 'Rate limit exceeded'},
            'retry_after': 5
        },
        'auth_error': {
            'error': {'code': 401, 'message': 'Invalid credentials'}
        },
        'server_error': {
            'error': {'code': 500, 'message': 'Internal server error'}
        },
    }


@pytest.fixture
def temp_config_file(tmp_path):
    """Fixture for temporary configuration file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
project_id: test-project-123
region: us-central1
model: claude-4-5-sonnet
max_tokens: 4096
temperature: 0.7
""")
    return str(config_file)


@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture for temporary project directory."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Reset environment variables before each test."""
    # Remove GCP credentials from environment
    monkeypatch.delenv('GOOGLE_APPLICATION_CREDENTIALS', raising=False)
    yield
    # Cleanup after test

