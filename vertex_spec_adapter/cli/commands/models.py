"""Models command for listing and managing available models."""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from vertex_spec_adapter.cli.utils import print_error
from vertex_spec_adapter.core.config import ConfigurationManager
from vertex_spec_adapter.core.exceptions import ConfigurationError
from vertex_spec_adapter.core.models import ModelRegistry

console = Console()


def _get_config_manager(ctx: typer.Context) -> ConfigurationManager:
    """Get ConfigurationManager from context."""
    config_path = ctx.obj.get("config_path") if ctx.obj else None
    if config_path:
        return ConfigurationManager(config_path=Path(config_path))
    return ConfigurationManager()


def models_list(
    ctx: typer.Context,
    region: Optional[str] = typer.Option(None, "--region", help="Filter by region"),
    provider: Optional[str] = typer.Option(None, "--provider", help="Filter by provider"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json, yaml)"),
) -> None:
    """
    List available models and their information.
    """
    try:
        # Get config for project ID
        config_manager = _get_config_manager(ctx)
        try:
            config = config_manager.load_config()
            project_id = config.project_id
        except ConfigurationError:
            # Use default if config not available
            project_id = "default-project"
        
        # Get model registry
        registry = ModelRegistry()
        models = registry.get_available_models(
            project_id=project_id,
            region=region,
            use_cache=True,
        )
        
        # Filter by provider if specified
        if provider:
            models = [m for m in models if m.get("provider", "").lower() == provider.lower()]
        
        # Format output
        if format == "json":
            import json
            console.print(json.dumps(models, indent=2))
        elif format == "yaml":
            import yaml
            console.print(yaml.dump(models, default_flow_style=False))
        else:
            # Table format
            _display_models_table(models)
        
    except Exception as e:
        print_error(e)
        raise typer.Exit(1)


def _display_models_table(models: List[dict]) -> None:
    """Display models in a formatted table."""
    table = Table(title="Available Models", show_header=True, header_style="bold magenta")
    
    table.add_column("Model ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Provider", style="yellow")
    table.add_column("Access Pattern", style="green")
    table.add_column("Default Region", style="blue")
    table.add_column("Available Regions", style="blue")
    table.add_column("Latest Version", style="magenta")
    
    for model in models:
        regions_str = ", ".join(model.get("available_regions", []))
        table.add_row(
            model.get("id", ""),
            model.get("name", ""),
            model.get("provider", ""),
            model.get("access_pattern", ""),
            model.get("default_region", ""),
            regions_str,
            model.get("latest_version", ""),
        )
    
    console.print(table)
    console.print(f"\n[cyan]Total: {len(models)} models[/cyan]")

