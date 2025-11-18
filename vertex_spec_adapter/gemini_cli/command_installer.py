"""Installer for Gemini CLI custom /model command."""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from vertex_spec_adapter.core.exceptions import ConfigurationError


@dataclass
class InstallationResult:
    """Result of command installation operation."""
    
    success: bool
    command_path: Path
    message: str
    error: Optional[str] = None


class GeminiCLICommandInstaller:
    """
    Handles installation and management of Gemini CLI custom command.
    
    Installs the custom /model command to override Gemini CLI's default command
    with the Vertex Adapter interactive menu.
    """
    
    def __init__(self) -> None:
        """Initialize installer."""
        self.commands_dir = self.get_command_path()
        self.command_file = self.commands_dir / "model.toml"
        
        # Get template file path (in package)
        import vertex_spec_adapter
        package_dir = Path(vertex_spec_adapter.__file__).parent
        self.template_file = package_dir / "gemini_cli" / "model.toml"
    
    def get_command_path(self) -> Path:
        """
        Get the path to the Gemini CLI commands directory.
        
        Returns:
            Path to ~/.gemini/commands/
        """
        home_dir = Path.home()
        commands_dir = home_dir / ".gemini" / "commands"
        
        # Create directory if it doesn't exist
        commands_dir.mkdir(parents=True, exist_ok=True)
        
        return commands_dir
    
    def is_installed(self) -> bool:
        """
        Check if the custom command is installed.
        
        Returns:
            True if command file exists, False otherwise
        """
        return self.command_file.exists()
    
    def install(
        self,
        force: bool = False,
        command_file: Optional[Path] = None,
    ) -> InstallationResult:
        """
        Install the custom command file to Gemini CLI commands directory.
        
        Args:
            force: Overwrite existing command file if True
            command_file: Path to command TOML file. Defaults to package template.
        
        Returns:
            InstallationResult with installation status
        
        Raises:
            FileNotFoundError: If command template file not found
            PermissionError: If cannot write to commands directory
            FileExistsError: If file exists and force=False
        """
        # Determine source file
        source_file = command_file or self.template_file
        
        # Check if template exists
        if not source_file.exists():
            return InstallationResult(
                success=False,
                command_path=self.command_file,
                message="Command template not found",
                error=f"Template file not found: {source_file}. Please reinstall vertex-spec-adapter.",
            )
        
        # Check if already installed
        if self.command_file.exists() and not force:
            return InstallationResult(
                success=False,
                command_path=self.command_file,
                message="Command already installed",
                error=f"Command already installed at {self.command_file}. Use force=True to overwrite.",
            )
        
        try:
            # Copy template to commands directory
            shutil.copy2(source_file, self.command_file)
            
            # Verify file was created
            if not self.command_file.exists():
                return InstallationResult(
                    success=False,
                    command_path=self.command_file,
                    message="Installation verification failed",
                    error="Command file was not created after installation.",
                )
            
            return InstallationResult(
                success=True,
                command_path=self.command_file,
                message=f"Command installed successfully at {self.command_file}",
            )
        
        except PermissionError as e:
            return InstallationResult(
                success=False,
                command_path=self.command_file,
                message="Permission denied",
                error=f"Cannot write to {self.commands_dir}. Check permissions: {e}",
            )
        except Exception as e:
            return InstallationResult(
                success=False,
                command_path=self.command_file,
                message="Installation failed",
                error=f"Unexpected error during installation: {e}",
            )
    
    def uninstall(self) -> bool:
        """
        Remove the custom command file from Gemini CLI.
        
        Returns:
            True if successfully removed, False if file didn't exist
        """
        if not self.command_file.exists():
            return False
        
        try:
            self.command_file.unlink()
            return True
        except PermissionError:
            raise PermissionError(
                f"Cannot remove {self.command_file}. Check permissions."
            )
        except Exception:
            return False

