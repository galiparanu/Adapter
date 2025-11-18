"""Unit tests for init command."""

import shutil
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from vertex_spec_adapter.cli.commands import init
from vertex_spec_adapter.core.exceptions import ConfigurationError


class TestInitCommand:
    """Test init command."""
    
    def test_check_prerequisites_python_version(self):
        """Test prerequisite check for Python version."""
        all_met, missing = init.check_prerequisites()
        
        # Should pass if Python 3.9+
        if sys.version_info >= (3, 9):
            assert all_met is True
            assert len(missing) == 0
        else:
            assert all_met is False
            assert any("Python" in item for item in missing)
    
    @patch("shutil.which")
    def test_check_prerequisites_git_missing(self, mock_which):
        """Test prerequisite check when Git is missing."""
        mock_which.return_value = None
        
        all_met, missing = init.check_prerequisites()
        
        assert all_met is False
        assert any("Git" in item for item in missing)
    
    @patch("shutil.which")
    def test_check_prerequisites_git_present(self, mock_which):
        """Test prerequisite check when Git is present."""
        mock_which.return_value = "/usr/bin/git"
        
        all_met, missing = init.check_prerequisites()
        
        # Should pass if Python version is also OK
        if sys.version_info >= (3, 9):
            assert all_met is True
            assert len(missing) == 0

