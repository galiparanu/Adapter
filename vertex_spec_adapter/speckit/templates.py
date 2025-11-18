"""Template management for Spec Kit artifacts."""

from pathlib import Path
from typing import Dict, Optional

from vertex_spec_adapter.utils.logging import get_logger

logger = get_logger(__name__)


class TemplateManager:
    """Manages Spec Kit templates."""
    
    TEMPLATES_DIR = Path(__file__).parent / "templates"
    
    def __init__(self):
        """Initialize template manager."""
        self._templates: Dict[str, str] = {}
    
    def load_template(self, template_type: str) -> str:
        """
        Load Spec Kit template.
        
        Args:
            template_type: Type of template (constitution, spec, plan, tasks)
        
        Returns:
            Template content
        """
        if template_type in self._templates:
            return self._templates[template_type]
        
        # Try to load from file
        template_file = self.TEMPLATES_DIR / f"{template_type}.md"
        if template_file.exists():
            content = template_file.read_text(encoding="utf-8")
            self._templates[template_type] = content
            return content
        
        # Return default template structure
        return self._get_default_template(template_type)
    
    def _get_default_template(self, template_type: str) -> str:
        """Get default template structure."""
        templates = {
            "constitution": """# Project Constitution

## Core Principles

[Generated content will be here]

## Code Quality Standards

[Generated content will be here]

## Testing Requirements

[Generated content will be here]
""",
            "spec": """# Feature Specification

## Problem Statement

[Generated content will be here]

## Target Users

[Generated content will be here]

## Core Features

[Generated content will be here]
""",
            "plan": """# Implementation Plan

## Technical Context

[Generated content will be here]

## Architecture

[Generated content will be here]

## Implementation Phases

[Generated content will be here]
""",
            "tasks": """# Tasks

## Phase 1: Setup

- [ ] Task 1
- [ ] Task 2

## Phase 2: Implementation

- [ ] Task 3
- [ ] Task 4
""",
        }
        
        return templates.get(template_type, "")

