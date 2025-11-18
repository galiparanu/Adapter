"""CLI main entry point for Vertex Spec Adapter."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from vertex_spec_adapter.cli import commands
from vertex_spec_adapter.cli.utils import print_error
from vertex_spec_adapter.core.exceptions import ConfigurationError

# Initialize Typer app
app = typer.Typer(
    name="vertex-spec",
    help="Vertex AI Spec Kit Adapter - Bridge tool for using Spec Kit with Google Vertex AI models",
    add_completion=False,
)

# Initialize console
console = Console()

# Register commands
app.add_typer(commands.init_app, name="init", help="Initialize a new Spec Kit project")
app.add_typer(commands.config_app, name="config", help="Manage configuration")
app.add_typer(commands.test_app, name="test", help="Test Vertex AI connection")


@app.callback()
def main(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file (default: .specify/config.yaml)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress all output except errors",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit",
    ),
) -> None:
    """
    Vertex AI Spec Kit Adapter - Bridge tool for using Spec Kit with Google Vertex AI models.
    
    This tool enables seamless integration between Spec Kit and Google Vertex AI,
    supporting multiple models (Claude, Gemini, Qwen) with flexible configuration.
    """
    # Handle version flag
    if version:
        try:
            from importlib.metadata import version
            v = version("vertex-spec-adapter")
            console.print(f"vertex-spec version {v}")
        except Exception:
            console.print("vertex-spec version 0.1.0")
        raise typer.Exit(0)
    
    # Store options in context for subcommands to access
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["debug"] = debug


# Import models command
from vertex_spec_adapter.cli.commands import models

# Create models command group
models_app = typer.Typer(name="models", help="List and manage available models")
models_app.command("list")(models.models_list)

app.add_typer(models_app)


# Import run commands
from vertex_spec_adapter.cli.commands import run

# Create run command group
run_app = typer.Typer(name="run", help="Execute Spec Kit commands with Vertex AI")
run_app.command("constitution")(run.run_constitution)
run_app.command("specify")(run.run_specify)
run_app.command("plan")(run.run_plan)
run_app.command("tasks")(run.run_tasks)
run_app.command("implement")(run.run_implement)

app.add_typer(run_app)


def cli() -> None:
    """
    CLI entry point.
    
    This function is called by the console script defined in pyproject.toml.
    """
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        console.print("[cyan]Checkpoint saved (if applicable). You can resume with --resume flag.[/cyan]")
        sys.exit(130)
    except ConfigurationError as e:
        print_error(e)
        sys.exit(2)
    except Exception as e:
        if "--debug" in sys.argv or "-d" in sys.argv:
            console.print_exception()
        else:
            print_error(e)
        sys.exit(1)


if __name__ == "__main__":
    cli()

