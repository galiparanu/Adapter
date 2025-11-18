"""Spec Kit bridge for integrating with Vertex AI models."""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from vertex_spec_adapter.core.client import VertexAIClient
from vertex_spec_adapter.core.exceptions import ConfigurationError
from vertex_spec_adapter.utils.logging import get_logger

logger = get_logger(__name__)


class SpecKitArtifact:
    """Represents a Spec Kit artifact file."""
    
    def __init__(
        self,
        file_path: str,
        content: str,
        artifact_type: str,
        git_branch: Optional[str] = None,
        git_commit: Optional[str] = None,
    ):
        """
        Initialize Spec Kit artifact.
        
        Args:
            file_path: Relative path to artifact file
            content: File content
            artifact_type: Type of artifact (constitution, spec, plan, tasks, implementation)
            git_branch: Optional Git branch where artifact was created
            git_commit: Optional Git commit SHA
        """
        self.file_path = file_path
        self.content = content
        self.artifact_type = artifact_type
        self.git_branch = git_branch
        self.git_commit = git_commit
        self.created_at = None
        self.valid = True


class SpecKitBridge:
    """
    Bridge between Spec Kit commands and Vertex AI models.
    
    Handles all five Spec Kit commands:
    - constitution: Create/update project constitution
    - specify: Create feature specification
    - plan: Create implementation plan
    - tasks: Create task list
    - implement: Execute implementation
    """
    
    def __init__(
        self,
        client: VertexAIClient,
        project_root: Optional[str] = None,
    ):
        """
        Initialize Spec Kit bridge.
        
        Args:
            client: Configured VertexAIClient instance
            project_root: Optional project root directory (defaults to current)
        """
        self.client = client
        self.project_root = Path(project_root) if project_root else Path.cwd()
        logger.info("SpecKitBridge initialized", project_root=str(self.project_root))
    
    def handle_constitution(self, principles: Optional[List[str]] = None) -> SpecKitArtifact:
        """
        Handle /speckit.constitution command.
        
        Creates or updates project constitution using Vertex AI.
        
        Args:
            principles: Optional list of principles to include
        
        Returns:
            SpecKitArtifact for created constitution
        """
        logger.info("Handling constitution command", principles=principles)
        
        # Build prompt
        prompt = self._build_constitution_prompt(principles)
        
        # Generate constitution
        messages = [{"role": "user", "content": prompt}]
        content = self.client.generate(messages, temperature=0.7)
        
        # Create file
        file_path = ".specify/memory/constitution.md"
        artifact = self.create_speckit_file(
            file_path=file_path,
            content=content,
            template_type="constitution",
        )
        
        # Commit if Git repo exists
        if self._is_git_repo():
            self._git_commit(file_path, "feat: Create/update project constitution")
        
        return artifact
    
    def handle_specify(
        self,
        feature_description: str,
        branch_name: Optional[str] = None,
    ) -> SpecKitArtifact:
        """
        Handle /speckit.specify command.
        
        Creates feature specification from description.
        
        Args:
            feature_description: Natural language feature description
            branch_name: Optional branch name (auto-generated if not provided)
        
        Returns:
            SpecKitArtifact for created spec
        """
        logger.info("Handling specify command", feature_description=feature_description[:100])
        
        # Generate branch name if not provided
        if not branch_name:
            branch_name = self._generate_branch_name(feature_description)
        
        # Create feature branch
        if self._is_git_repo():
            self.create_feature_branch(branch_name)
        
        # Build prompt
        prompt = self._build_specify_prompt(feature_description)
        
        # Generate spec
        messages = [{"role": "user", "content": prompt}]
        content = self.client.generate(messages, temperature=0.7)
        
        # Create file
        file_path = f"specs/{branch_name}/spec.md"
        artifact = self.create_speckit_file(
            file_path=file_path,
            content=content,
            template_type="spec",
        )
        
        # Commit if Git repo exists
        if self._is_git_repo():
            self._git_commit(file_path, f"feat: Add specification for {branch_name}")
        
        return artifact
    
    def handle_plan(
        self,
        spec_path: str,
        technical_context: Optional[Dict] = None,
    ) -> SpecKitArtifact:
        """
        Handle /speckit.plan command.
        
        Creates implementation plan from specification.
        
        Args:
            spec_path: Path to spec.md file
            technical_context: Optional technical context dict
        
        Returns:
            SpecKitArtifact for created plan
        """
        logger.info("Handling plan command", spec_path=spec_path)
        
        # Read spec file
        spec_file = self.project_root / spec_path
        if not spec_file.exists():
            raise ConfigurationError(f"Spec file not found: {spec_path}")
        
        spec_content = spec_file.read_text(encoding="utf-8")
        
        # Build prompt
        prompt = self._build_plan_prompt(spec_content, technical_context)
        
        # Generate plan
        messages = [{"role": "user", "content": prompt}]
        content = self.client.generate(messages, temperature=0.7)
        
        # Create file
        spec_dir = spec_file.parent
        file_path = spec_dir / "plan.md"
        artifact = self.create_speckit_file(
            file_path=str(file_path.relative_to(self.project_root)),
            content=content,
            template_type="plan",
        )
        
        # Commit if Git repo exists
        if self._is_git_repo():
            self._git_commit(str(file_path.relative_to(self.project_root)), "feat: Add implementation plan")
        
        return artifact
    
    def handle_tasks(self, plan_path: str) -> SpecKitArtifact:
        """
        Handle /speckit.tasks command.
        
        Creates task list from implementation plan.
        
        Args:
            plan_path: Path to plan.md file
        
        Returns:
            SpecKitArtifact for created tasks
        """
        logger.info("Handling tasks command", plan_path=plan_path)
        
        # Read plan file
        plan_file = self.project_root / plan_path
        if not plan_file.exists():
            raise ConfigurationError(f"Plan file not found: {plan_path}")
        
        plan_content = plan_file.read_text(encoding="utf-8")
        
        # Build prompt
        prompt = self._build_tasks_prompt(plan_content)
        
        # Generate tasks
        messages = [{"role": "user", "content": prompt}]
        content = self.client.generate(messages, temperature=0.7)
        
        # Create file
        plan_dir = plan_file.parent
        file_path = plan_dir / "tasks.md"
        artifact = self.create_speckit_file(
            file_path=str(file_path.relative_to(self.project_root)),
            content=content,
            template_type="tasks",
        )
        
        # Commit if Git repo exists
        if self._is_git_repo():
            self._git_commit(str(file_path.relative_to(self.project_root)), "feat: Add task list")
        
        return artifact
    
    def handle_implement(
        self,
        tasks_path: str,
        checkpoint_path: Optional[str] = None,
        resume: bool = False,
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
        """
        logger.info("Handling implement command", tasks_path=tasks_path)
        
        # Read tasks file
        tasks_file = self.project_root / tasks_path
        if not tasks_file.exists():
            raise ConfigurationError(f"Tasks file not found: {tasks_path}")
        
        tasks_content = tasks_file.read_text(encoding="utf-8")
        
        # Parse tasks (simplified - in full implementation would parse markdown)
        # For now, generate implementation based on tasks
        
        # Build prompt
        prompt = self._build_implement_prompt(tasks_content)
        
        # Generate implementation
        messages = [{"role": "user", "content": prompt}]
        content = self.client.generate(messages, temperature=0.7)
        
        # Parse and create files (simplified)
        artifacts = []
        # In full implementation, would parse generated content and create multiple files
        
        return artifacts
    
    def create_feature_branch(self, feature_name: str) -> str:
        """
        Create feature branch following Spec Kit conventions.
        
        Args:
            feature_name: Feature name (e.g., 'user-auth')
        
        Returns:
            Branch name (e.g., '001-user-auth')
        
        Raises:
            ConfigurationError: If branch creation fails
        """
        if not self._is_git_repo():
            raise ConfigurationError("Not a Git repository")
        
        # Generate branch name
        branch_name = self._generate_branch_name(feature_name)
        
        try:
            # Create and checkout branch
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.project_root,
                check=True,
                capture_output=True,
            )
            logger.info("Created feature branch", branch=branch_name)
            return branch_name
        except subprocess.CalledProcessError as e:
            raise ConfigurationError(f"Failed to create branch: {e}") from e
    
    def create_speckit_file(
        self,
        file_path: str,
        content: str,
        template_type: str,
    ) -> SpecKitArtifact:
        """
        Create Spec Kit file with proper structure.
        
        Args:
            file_path: Relative path to file
            content: File content
            template_type: Type of template (constitution, spec, plan, etc.)
        
        Returns:
            SpecKitArtifact for created file
        """
        full_path = self.project_root / file_path
        
        # Create parent directory if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        full_path.write_text(content, encoding="utf-8")
        
        logger.info("Created Spec Kit file", file_path=file_path, type=template_type)
        
        # Get Git info if available
        git_branch = None
        git_commit = None
        if self._is_git_repo():
            try:
                git_branch = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                git_commit = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            except Exception:
                pass
        
        return SpecKitArtifact(
            file_path=file_path,
            content=content,
            artifact_type=template_type,
            git_branch=git_branch,
            git_commit=git_commit,
        )
    
    def _build_constitution_prompt(self, principles: Optional[List[str]]) -> str:
        """Build prompt for constitution generation."""
        base_prompt = """Create a comprehensive project constitution following Spec Kit conventions.

The constitution should include:
- Core principles and values
- Code quality standards
- Testing requirements
- Security practices
- Documentation standards
- Team collaboration guidelines

Format the output as a Markdown document following Spec Kit constitution template."""
        
        if principles:
            base_prompt += f"\n\nInclude these specific principles: {', '.join(principles)}"
        
        return base_prompt
    
    def _build_specify_prompt(self, feature_description: str) -> str:
        """Build prompt for specification generation."""
        return f"""Create a comprehensive feature specification following Spec Kit conventions.

Feature Description:
{feature_description}

The specification should include:
- Problem Statement
- Target Users
- Core Features
- User Stories
- Acceptance Criteria
- Success Criteria
- Constraints
- Testing Strategy
- Exclusions

Format the output as a Markdown document following Spec Kit specification template."""
    
    def _build_plan_prompt(self, spec_content: str, technical_context: Optional[Dict]) -> str:
        """Build prompt for plan generation."""
        prompt = f"""Create a detailed implementation plan following Spec Kit conventions.

Specification:
{spec_content[:5000]}  # Truncate if too long

The plan should include:
- Technical Context
- Architecture
- Dependencies
- Implementation Phases
- Testing Strategy
- Quality Gates

Format the output as a Markdown document following Spec Kit plan template."""
        
        if technical_context:
            prompt += f"\n\nTechnical Context: {technical_context}"
        
        return prompt
    
    def _build_tasks_prompt(self, plan_content: str) -> str:
        """Build prompt for tasks generation."""
        return f"""Create a detailed task list following Spec Kit conventions.

Implementation Plan:
{plan_content[:5000]}  # Truncate if too long

The task list should:
- Break down the plan into executable tasks
- Organize tasks by phase
- Include task IDs, descriptions, and file paths
- Mark dependencies and parallel execution opportunities

Format the output as a Markdown document following Spec Kit tasks template."""
    
    def _build_implement_prompt(self, tasks_content: str) -> str:
        """Build prompt for implementation generation."""
        return f"""Implement the tasks from the task list following Spec Kit conventions.

Tasks:
{tasks_content[:5000]}  # Truncate if too long

Generate the implementation code, tests, and documentation as specified in the tasks.
Follow all coding standards and best practices."""
    
    def _generate_branch_name(self, feature_name: str) -> str:
        """Generate branch name from feature name."""
        # Clean feature name
        cleaned = re.sub(r'[^a-z0-9-]', '-', feature_name.lower())
        cleaned = re.sub(r'-+', '-', cleaned).strip('-')
        
        # Find next number
        if self._is_git_repo():
            try:
                branches = subprocess.run(
                    ["git", "branch", "--list", "*-*"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                ).stdout.strip().split('\n')
                
                # Extract numbers
                numbers = []
                for branch in branches:
                    match = re.match(r'(\d+)-', branch.strip('* '))
                    if match:
                        numbers.append(int(match.group(1)))
                
                next_num = max(numbers) + 1 if numbers else 1
            except Exception:
                next_num = 1
        else:
            next_num = 1
        
        return f"{next_num:03d}-{cleaned}"
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a Git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _git_commit(self, file_path: str, message: str) -> None:
        """Commit file to Git repository."""
        try:
            subprocess.run(
                ["git", "add", file_path],
                cwd=self.project_root,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.project_root,
                check=True,
                capture_output=True,
            )
            logger.info("Committed file to Git", file_path=file_path)
        except subprocess.CalledProcessError as e:
            logger.warning("Failed to commit file", file_path=file_path, error=str(e))

