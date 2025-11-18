# Spec Kit Bridge API Contract

**Component**: Spec Kit Integration  
**Version**: 1.0.0  
**Date**: 2025-01-27

## Overview

This contract defines the interface for the Spec Kit bridge that enables all five Spec Kit commands to work with Vertex AI models.

## Interface: SpecKitBridge

### Class Definition

```python
class SpecKitBridge:
    """Bridge between Spec Kit commands and Vertex AI models."""
    
    def __init__(
        self,
        client: VertexAIClient,
        project_root: Optional[str] = None
    ) -> None:
        """
        Initialize Spec Kit bridge.
        
        Args:
            client: Configured VertexAIClient instance
            project_root: Optional project root directory (defaults to current)
        """
```

### Methods

#### handle_constitution

```python
def handle_constitution(
    self,
    principles: Optional[List[str]] = None
) -> SpecKitArtifact:
    """
    Handle /speckit.constitution command.
    
    Creates or updates project constitution using Vertex AI.
    
    Args:
        principles: Optional list of principles to include
    
    Returns:
        SpecKitArtifact for created constitution
    
    Raises:
        GitError: If Git operations fail
        FileError: If file operations fail
        APIError: If AI generation fails
    """
```

**Input**: User prompt or principles list  
**Output**: `.specify/memory/constitution.md` file  
**Git**: Creates/updates file, commits if Git repo exists

#### handle_specify

```python
def handle_specify(
    self,
    feature_description: str,
    branch_name: Optional[str] = None
) -> SpecKitArtifact:
    """
    Handle /speckit.specify command.
    
    Creates feature specification from description.
    
    Args:
        feature_description: Natural language feature description
        branch_name: Optional branch name (auto-generated if not provided)
    
    Returns:
        SpecKitArtifact for created spec
    
    Raises:
        GitError: If Git operations fail
        FileError: If file operations fail
        APIError: If AI generation fails
    """
```

**Input**: Feature description string  
**Output**: `specs/###-feature-name/spec.md` file  
**Git**: Creates branch, commits spec file

#### handle_plan

```python
def handle_plan(
    self,
    spec_path: str,
    technical_context: Optional[Dict[str, Any]] = None
) -> SpecKitArtifact:
    """
    Handle /speckit.plan command.
    
    Creates implementation plan from specification.
    
    Args:
        spec_path: Path to spec.md file
        technical_context: Optional technical context dict
    
    Returns:
        SpecKitArtifact for created plan
    
    Raises:
        FileError: If spec file not found
        ValidationError: If spec is invalid
        APIError: If AI generation fails
    """
```

**Input**: Path to spec.md  
**Output**: `specs/###-feature-name/plan.md` and supporting files  
**Git**: Commits plan files

#### handle_tasks

```python
def handle_tasks(
    self,
    plan_path: str
) -> SpecKitArtifact:
    """
    Handle /speckit.tasks command.
    
    Creates task list from implementation plan.
    
    Args:
        plan_path: Path to plan.md file
    
    Returns:
        SpecKitArtifact for created tasks
    
    Raises:
        FileError: If plan file not found
        ValidationError: If plan is invalid
        APIError: If AI generation fails
    """
```

**Input**: Path to plan.md  
**Output**: `specs/###-feature-name/tasks.md` file  
**Git**: Commits tasks file

#### handle_implement

```python
def handle_implement(
    self,
    tasks_path: str,
    checkpoint_path: Optional[str] = None,
    resume: bool = False
) -> List[SpecKitArtifact]:
    """
    Handle /speckit.implement command.
    
    Implements tasks from task list using Vertex AI.
    
    Args:
        tasks_path: Path to tasks.md file
        checkpoint_path: Optional path to checkpoint file
        resume: Whether to resume from checkpoint
    
    Returns:
        List of SpecKitArtifact for created files
    
    Raises:
        FileError: If tasks file not found
        ValidationError: If tasks are invalid
        APIError: If AI generation fails
        InterruptionError: If interrupted (creates checkpoint)
    """
```

**Input**: Path to tasks.md  
**Output**: Generated code files, test files, documentation  
**Git**: Commits implementation files  
**Checkpoint**: Creates checkpoint for resumable operations

## Git Operations

### Branch Management

```python
def create_feature_branch(
    self,
    feature_name: str
) -> str:
    """
    Create feature branch following Spec Kit conventions.
    
    Args:
        feature_name: Feature name (e.g., 'user-auth')
    
    Returns:
        Branch name (e.g., '001-user-auth')
    
    Raises:
        GitError: If branch creation fails
    """
```

### File Operations

```python
def create_speckit_file(
    self,
    file_path: str,
    content: str,
    template_type: str
) -> SpecKitArtifact:
    """
    Create Spec Kit file with proper structure.
    
    Args:
        file_path: Relative path to file
        content: File content
        template_type: Type of template (constitution, spec, plan, etc.)
    
    Returns:
        SpecKitArtifact for created file
    
    Raises:
        FileError: If file creation fails
        ValidationError: If content doesn't match template
    """
```

## Error Responses

### GitError

```json
{
  "error": {
    "type": "GitError",
    "message": "Git repository not initialized",
    "code": "GIT_001",
    "suggested_fix": "Run 'git init' to initialize repository"
  }
}
```

### FileError

```json
{
  "error": {
    "type": "FileError",
    "message": "Cannot write to file: permission denied",
    "code": "FILE_001",
    "file_path": "specs/001-feature/spec.md",
    "suggested_fix": "Check file permissions"
  }
}
```

### ValidationError

```json
{
  "error": {
    "type": "ValidationError",
    "message": "Spec file missing required sections",
    "code": "VAL_001",
    "file_path": "specs/001-feature/spec.md",
    "missing_sections": ["User Scenarios", "Requirements"],
    "suggested_fix": "Add missing sections to spec file"
  }
}
```

## Implementation Notes

1. **Template Compatibility**: All generated files must match Spec Kit template structure
2. **Git Integration**: Automatic branch creation and commits following Spec Kit conventions
3. **File Structure**: Maintains Spec Kit directory structure (`.specify/`, `specs/`)
4. **Checkpoint/Resume**: Long-running operations support interruption and resumption
5. **Error Recovery**: Graceful handling of Git and file system errors

## Testing Requirements

- Unit tests with mocked Git and file system
- Integration tests with real Git repository
- E2E tests for complete workflow
- Test template compatibility
- Test error scenarios (dirty Git, permission errors, etc.)

