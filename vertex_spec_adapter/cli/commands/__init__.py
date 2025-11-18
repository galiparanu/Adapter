"""CLI commands for Vertex Spec Adapter."""

import typer

from vertex_spec_adapter.cli.commands import config, init, test

# Create Typer apps for each command group
init_app = typer.Typer(name="init", help="Initialize a new Spec Kit project")
config_app = typer.Typer(name="config", help="Manage configuration")
test_app = typer.Typer(name="test", help="Test Vertex AI connection")

# Register command handlers
init_app.command()(init.init_command)
config_app.command("show")(config.config_show)
config_app.command("set")(config.config_set)
config_app.command("get")(config.config_get)
config_app.command("validate")(config.config_validate)
test_app.command()(test.test_command)

