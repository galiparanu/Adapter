"""Run command for executing Spec Kit commands with Vertex AI."""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

from vertex_spec_adapter.cli.utils import print_error, print_success
from vertex_spec_adapter.core.auth import AuthenticationManager
from vertex_spec_adapter.core.client import VertexAIClient
from vertex_spec_adapter.core.config import ConfigurationManager
from vertex_spec_adapter.core.exceptions import ConfigurationError
from vertex_spec_adapter.speckit.bridge import SpecKitBridge

console = Console()


def get_client_and_bridge(ctx: typer.Context) -> tuple[VertexAIClient, SpecKitBridge]:
    """Get configured client and bridge."""
    config_manager = get_config_manager(ctx)
    config = config_manager.load_config()
    
    # Authenticate
    auth_manager = AuthenticationManager(config=config)
    credentials = auth_manager.authenticate()
    
    # Create client
    client = VertexAIClient(
        project_id=config.project_id,
        region=config.region or "us-east5",
        model_id=config.model,
        model_version=config.model_version,
        credentials=credentials,
        config=config,
    )
    
    # Create bridge
    bridge = SpecKitBridge(client=client)
    
    return client, bridge


def get_config_manager(ctx: typer.Context) -> ConfigurationManager:
    """Get ConfigurationManager from context."""
    config_path = ctx.obj.get("config_path") if ctx.obj else None
    if config_path:
        return ConfigurationManager(config_path=Path(config_path))
    return ConfigurationManager()


def run_constitution(
    ctx: typer.Context,
    principles: Optional[List[str]] = typer.Option(None, "--principle", help="Principles to include"),
) -> None:
    """Run /speckit.constitution command."""
    try:
        client, bridge = get_client_and_bridge(ctx)
        
        console.print("[cyan]Generating project constitution...[/cyan]")
        artifact = bridge.handle_constitution(principles=principles)
        
        print_success(f"Constitution created: {artifact.file_path}")
        
    except Exception as e:
        print_error(e)
        raise typer.Exit(1)


def run_specify(
    ctx: typer.Context,
    description: str = typer.Argument(..., help="Feature description"),
    branch: Optional[str] = typer.Option(None, "--branch", help="Branch name"),
) -> None:
    """Run /speckit.specify command."""
    try:
        client, bridge = get_client_and_bridge(ctx)
        
        console.print(f"[cyan]Generating specification for: {description[:50]}...[/cyan]")
        artifact = bridge.handle_specify(
            feature_description=description,
            branch_name=branch,
        )
        
        print_success(f"Specification created: {artifact.file_path}")
        if artifact.git_branch:
            console.print(f"[green]Branch: {artifact.git_branch}[/green]")
        
    except Exception as e:
        print_error(e)
        raise typer.Exit(1)


def run_plan(
    ctx: typer.Context,
    spec_path: str = typer.Argument(..., help="Path to spec.md file"),
) -> None:
    """Run /speckit.plan command."""
    try:
        client, bridge = get_client_and_bridge(ctx)
        
        console.print(f"[cyan]Generating implementation plan for: {spec_path}...[/cyan]")
        artifact = bridge.handle_plan(spec_path=spec_path)
        
        print_success(f"Plan created: {artifact.file_path}")
        
    except Exception as e:
        print_error(e)
        raise typer.Exit(1)


def run_tasks(
    ctx: typer.Context,
    plan_path: str = typer.Argument(..., help="Path to plan.md file"),
) -> None:
    """Run /speckit.tasks command."""
    try:
        client, bridge = get_client_and_bridge(ctx)
        
        console.print(f"[cyan]Generating task list for: {plan_path}...[/cyan]")
        artifact = bridge.handle_tasks(plan_path=plan_path)
        
        print_success(f"Tasks created: {artifact.file_path}")
        
    except Exception as e:
        print_error(e)
        raise typer.Exit(1)


def run_implement(
    ctx: typer.Context,
    tasks_path: str = typer.Argument(..., help="Path to tasks.md file"),
    checkpoint: Optional[str] = typer.Option(None, "--checkpoint", help="Checkpoint file path"),
    resume: bool = typer.Option(False, "--resume", help="Resume from checkpoint"),
) -> None:
    """Run /speckit.implement command."""
    try:
        client, bridge = get_client_and_bridge(ctx)
        
        console.print(f"[cyan]Implementing tasks from: {tasks_path}...[/cyan]")
        artifacts = bridge.handle_implement(
            tasks_path=tasks_path,
            checkpoint_path=checkpoint,
            resume=resume,
        )
        
        print_success(f"Implementation complete: {len(artifacts)} files created")
        
    except Exception as e:
        print_error(e)
        raise typer.Exit(1)

