"""Init command for setting up a new Spec Kit project."""

import sys
from pathlib import Path
from typing import List, Optional, Tuple

import typer
from rich.console import Console

from vertex_spec_adapter.cli.utils import (
    confirm,
    print_error,
    print_info,
    print_step,
    print_success,
    prompt_input,
)
from vertex_spec_adapter.core.config import ConfigurationManager
from vertex_spec_adapter.core.exceptions import ConfigurationError

console = Console()


def check_prerequisites() -> Tuple[bool, List[str]]:
    """
    Check if prerequisites are met.
    
    Returns:
        Tuple of (all_met, missing_items)
    """
    missing = []
    
    # Check Python version
    if sys.version_info < (3, 9):
        missing.append(f"Python 3.9+ (current: {sys.version_info.major}.{sys.version_info.minor})")
    
    # Check Git
    import shutil
    if not shutil.which("git"):
        missing.append("Git (not found in PATH)")
    
    return len(missing) == 0, missing


def init_command(
    project_dir: Optional[Path] = typer.Argument(
        None,
        help="Project directory (default: current directory)",
    ),
    project_id: Optional[str] = typer.Option(
        None,
        "--project-id",
        help="GCP project ID",
    ),
    region: Optional[str] = typer.Option(
        None,
        "--region",
        help="Default region",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        help="Default model",
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--non-interactive",
        help="Run interactive setup wizard",
    ),
) -> None:
    """
    Initialize a new Spec Kit project with Vertex AI adapter.
    
    This command creates the necessary directory structure and configuration file
    for using Spec Kit with Google Vertex AI models.
    """
    # Determine project directory
    if project_dir is None:
        project_dir = Path.cwd()
    else:
        project_dir = Path(project_dir).resolve()
    
    if not project_dir.exists():
        console.print(f"[red]Error: Directory does not exist: {project_dir}[/red]")
        raise typer.Exit(1)
    
    # Check prerequisites
    console.print("[cyan]Checking prerequisites...[/cyan]")
    all_met, missing = check_prerequisites()
    
    if not all_met:
        console.print("[red]Missing prerequisites:[/red]")
        for item in missing:
            console.print(f"  - {item}")
        console.print("\n[yellow]Please install missing prerequisites and try again.[/yellow]")
        raise typer.Exit(1)
    
    print_success("All prerequisites met")
    
    # Determine config path
    config_dir = project_dir / ".specify"
    config_path = config_dir / "config.yaml"
    
    # Check if config already exists
    if config_path.exists() and interactive:
        if not confirm(
            f"Configuration file already exists at {config_path}. Overwrite?",
            default=False
        ):
            console.print("[yellow]Initialization cancelled.[/yellow]")
            raise typer.Exit(0)
    
    # Interactive setup wizard
    if interactive:
        console.print("\n[bold cyan]Vertex AI Spec Kit Adapter Setup[/bold cyan]")
        console.print("=" * 50)
        
        print_step(1, 4, "GCP Project Configuration")
        if not project_id:
            project_id = prompt_input(
                "GCP Project ID",
                default="your-project-id",
                required=True
            )
        
        print_step(2, 4, "Model Configuration")
        if not model:
            model = prompt_input(
                "Default model",
                default="claude-4-5-sonnet",
                required=True
            )
        
        print_step(3, 4, "Region Configuration")
        if not region:
            region = prompt_input(
                "Default region",
                default="us-east5",
                required=False
            )
            if not region:
                region = None
        
        print_step(4, 4, "Creating configuration...")
    else:
        # Non-interactive mode - use defaults if not provided
        if not project_id:
            project_id = "your-project-id"
        if not model:
            model = "claude-4-5-sonnet"
        if not region:
            region = "us-east5"
    
    # Create configuration
    try:
        config_manager = ConfigurationManager(config_path=config_path)
        config = config_manager.create_default_config(
            project_id=project_id,
            model=model,
            region=region,
        )
        
        # Save configuration
        config_manager.save_config(config)
        
        print_success(f"Configuration created at {config_path}")
        
        # Initialize Git repository if not present
        git_dir = project_dir / ".git"
        if not git_dir.exists():
            if interactive:
                if confirm("Initialize Git repository?", default=True):
                    import subprocess
                    try:
                        subprocess.run(
                            ["git", "init"],
                            cwd=project_dir,
                            check=True,
                            capture_output=True,
                        )
                        print_success("Git repository initialized")
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        print_info("Could not initialize Git repository (git not found)")
            else:
                # Non-interactive: try to init git silently
                import subprocess
                try:
                    subprocess.run(
                        ["git", "init"],
                        cwd=project_dir,
                        check=False,
                        capture_output=True,
                    )
                except FileNotFoundError:
                    pass
        
        # Print next steps
        console.print("\n[bold green]Setup complete![/bold green]")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("  1. Update your GCP project ID in .specify/config.yaml")
        console.print("  2. Configure authentication (see docs/authentication.md)")
        console.print("  3. Run 'vertex-spec test' to verify your setup")
        console.print("  4. Start using Spec Kit with 'vertex-spec run <command>'")
        
    except ConfigurationError as e:
        print_error(e)
        raise typer.Exit(2)
    except Exception as e:
        print_error(e)
        raise typer.Exit(1)

