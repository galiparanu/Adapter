"""Unit tests for SpecKitBridge."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vertex_spec_adapter.core.client import VertexAIClient
from vertex_spec_adapter.core.exceptions import ConfigurationError
from vertex_spec_adapter.speckit.bridge import SpecKitArtifact, SpecKitBridge


class TestSpecKitBridge:
    """Test SpecKitBridge class."""
    
    def test_init(self):
        """Test SpecKitBridge initialization."""
        mock_client = MagicMock(spec=VertexAIClient)
        bridge = SpecKitBridge(client=mock_client)
        
        assert bridge.client == mock_client
        assert isinstance(bridge.project_root, Path)
    
    def test_create_speckit_file(self, tmp_path):
        """Test creating Spec Kit file."""
        mock_client = MagicMock(spec=VertexAIClient)
        bridge = SpecKitBridge(client=mock_client, project_root=str(tmp_path))
        
        artifact = bridge.create_speckit_file(
            file_path="test.md",
            content="# Test\n\nContent",
            template_type="spec",
        )
        
        assert isinstance(artifact, SpecKitArtifact)
        assert artifact.file_path == "test.md"
        assert artifact.content == "# Test\n\nContent"
        assert artifact.artifact_type == "spec"
        
        # Verify file was created
        assert (tmp_path / "test.md").exists()
    
    def test_generate_branch_name(self):
        """Test branch name generation."""
        mock_client = MagicMock(spec=VertexAIClient)
        bridge = SpecKitBridge(client=mock_client)
        
        branch_name = bridge._generate_branch_name("User Authentication")
        
        assert branch_name.startswith("001-")
        assert "user-authentication" in branch_name.lower()
    
    def test_is_git_repo(self, tmp_path):
        """Test Git repository detection."""
        mock_client = MagicMock(spec=VertexAIClient)
        bridge = SpecKitBridge(client=mock_client, project_root=str(tmp_path))
        
        # Not a Git repo
        assert bridge._is_git_repo() is False
    
    @patch('subprocess.run')
    def test_create_feature_branch(self, mock_subprocess, tmp_path):
        """Test creating feature branch."""
        # Mock Git repo
        mock_subprocess.return_value.returncode = 0
        
        mock_client = MagicMock(spec=VertexAIClient)
        bridge = SpecKitBridge(client=mock_client, project_root=str(tmp_path))
        
        # This will fail because it's not a real Git repo, but tests the logic
        with pytest.raises(ConfigurationError):
            bridge.create_feature_branch("test-feature")


class TestSpecKitArtifact:
    """Test SpecKitArtifact class."""
    
    def test_init(self):
        """Test SpecKitArtifact initialization."""
        artifact = SpecKitArtifact(
            file_path="test.md",
            content="# Test",
            artifact_type="spec",
            git_branch="001-test",
            git_commit="abc123",
        )
        
        assert artifact.file_path == "test.md"
        assert artifact.content == "# Test"
        assert artifact.artifact_type == "spec"
        assert artifact.git_branch == "001-test"
        assert artifact.git_commit == "abc123"
        assert artifact.valid is True

