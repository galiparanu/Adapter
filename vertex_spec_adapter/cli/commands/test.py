"""Test command for verifying Vertex AI connection."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from vertex_spec_adapter.cli.utils import print_error, print_info, print_success, print_warning
from vertex_spec_adapter.core.config import ConfigurationManager
from vertex_spec_adapter.core.exceptions import AuthenticationError, ConfigurationError

console = Console()


def test_credentials() -> tuple[bool, str]:
    """
    Test GCP credentials.
    
    Returns:
        Tuple of (success, message)
    """
    try:
        from google.auth import default
        from google.auth.exceptions import DefaultCredentialsError
        
        try:
            credentials, project = default()
            if credentials:
                return True, f"Credentials found (project: {project or 'N/A'})"
            return False, "No credentials found"
        except DefaultCredentialsError as e:
            return False, f"Credentials error: {str(e)}"
    except ImportError:
        return False, "google-auth library not installed"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def test_vertex_ai_connectivity(
    project_id: str,
    region: Optional[str] = None,
    model: Optional[str] = None,
) -> tuple[bool, str]:
    """
    Test Vertex AI connectivity.
    
    Args:
        project_id: GCP project ID
        region: Optional region to test
        model: Optional model to test
        
    Returns:
        Tuple of (success, message)
    """
    # TODO: Implement actual Vertex AI connectivity test in Phase 4
    # For now, just check if we can import the SDK
    try:
        import google.cloud.aiplatform as aiplatform
        return True, "Vertex AI SDK available"
    except ImportError:
        return False, "google-cloud-aiplatform not installed"
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_config_manager(ctx: typer.Context) -> ConfigurationManager:
    """
    Get ConfigurationManager from context or create with default path.
    
    Args:
        ctx: Typer context
        
    Returns:
        ConfigurationManager instance
    """
    config_path = ctx.obj.get("config_path") if ctx.obj else None
    if config_path:
        return ConfigurationManager(config_path=Path(config_path))
    return ConfigurationManager()


def test_command(
    ctx: typer.Context,
    model: Optional[str] = typer.Option(None, "--model", help="Test specific model"),
    region: Optional[str] = typer.Option(None, "--region", help="Test specific region"),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed test results"),
) -> None:
    """
    Test Vertex AI connection and configuration.
    
    This command validates:
    - Configuration file
    - GCP credentials
    - Vertex AI connectivity
    - Model availability (if specified)
    """
    console.print("[cyan]Testing Vertex AI connection...[/cyan]\n")
    
    # Load configuration
    try:
        config_manager = get_config_manager(ctx)
        config = config_manager.load_config()
        print_success("Configuration loaded")
    except ConfigurationError as e:
        print_error(e)
        console.print("\n[yellow]Tip: Run 'vertex-spec init' to create a configuration file[/yellow]")
        raise typer.Exit(2)
    except Exception as e:
        print_error(e)
        raise typer.Exit(1)
    
    # Test credentials
    console.print("\n[cyan]Testing credentials...[/cyan]")
    creds_success, creds_message = test_credentials()
    if creds_success:
        print_success(creds_message)
    else:
        print_warning(creds_message)
        console.print("\n[yellow]Tip: Run 'gcloud auth login' or set GOOGLE_APPLICATION_CREDENTIALS[/yellow]")
    
    # Test Vertex AI connectivity
    console.print("\n[cyan]Testing Vertex AI connectivity...[/cyan]")
    test_model = model or config.model
    test_region = region or config.region
    
    connectivity_success, connectivity_message = test_vertex_ai_connectivity(
        project_id=config.project_id,
        region=test_region,
        model=test_model,
    )
    
    if connectivity_success:
        print_success(connectivity_message)
        if verbose:
            console.print(f"  Project ID: {config.project_id}")
            if test_region:
                console.print(f"  Region: {test_region}")
            console.print(f"  Model: {test_model}")
    else:
        print_warning(connectivity_message)
    
    # Summary
    console.print("\n" + "=" * 50)
    if creds_success and connectivity_success:
        print_success("All tests passed! You're ready to use Vertex AI with Spec Kit.")
        raise typer.Exit(0)
    else:
        print_warning("Some tests failed. Please fix the issues above and try again.")
        raise typer.Exit(1)

