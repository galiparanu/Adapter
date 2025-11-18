"""Config command for managing configuration."""

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console

from vertex_spec_adapter.cli.utils import print_error, print_success, print_table
from vertex_spec_adapter.core.config import ConfigurationManager
from vertex_spec_adapter.core.exceptions import ConfigurationError

console = Console()


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


def config_show(ctx: typer.Context) -> None:
    """
    Display current configuration.
    """
    try:
        config_manager = get_config_manager(ctx)
        config = config_manager.load_config()
        
        # Format config as table
        rows = [
            ["Project ID", config.project_id],
            ["Model", config.model],
            ["Region", config.region or "Model-specific default"],
            ["Model Version", config.model_version or "Latest"],
            ["Auth Method", config.auth_method.value],
            ["Max Retries", str(config.max_retries)],
            ["Timeout", f"{config.timeout}s"],
            ["Log Level", config.log_level.value],
            ["Log Format", config.log_format.value],
        ]
        
        if config.model_regions:
            regions_str = ", ".join(f"{k}: {v}" for k, v in config.model_regions.items())
            rows.append(["Model Regions", regions_str])
        
        if config.service_account_path:
            rows.append(["Service Account", config.service_account_path])
        
        if config.log_file:
            rows.append(["Log File", config.log_file])
        
        rows.append(["Cost Tracking", "Enabled" if config.enable_cost_tracking else "Disabled"])
        
        print_table(
            headers=["Setting", "Value"],
            rows=rows,
            title="Current Configuration"
        )
        
    except ConfigurationError as e:
        print_error(e)
        raise typer.Exit(2)
    except Exception as e:
        print_error(e)
        raise typer.Exit(1)


def config_set(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="Configuration key to set"),
    value: str = typer.Argument(..., help="Value to set"),
) -> None:
    """
    Set a configuration value.
    
    Supported keys:
    - project_id, model, region, model_version
    - auth_method (service_account, user_credentials, adc, auto)
    - max_retries, timeout, retry_backoff_factor
    - log_level (DEBUG, INFO, WARNING, ERROR)
    - log_format (json, text)
    - enable_cost_tracking (true, false)
    """
    try:
        config_manager = get_config_manager(ctx)
        
        # Load existing config or create default
        try:
            config = config_manager.load_config()
        except ConfigurationError:
            # Config doesn't exist, create default
            config = config_manager.create_default_config()
        
        # Update config value
        key_lower = key.lower()
        
        # Handle boolean values
        if key_lower == "enable_cost_tracking":
            value = value.lower() in ("true", "1", "yes", "on")
        
        # Handle integer values
        elif key_lower in ("max_retries", "timeout"):
            try:
                value = int(value)
            except ValueError:
                console.print(f"[red]Error: {key} must be an integer[/red]")
                raise typer.Exit(1)
        
        # Handle float values
        elif key_lower == "retry_backoff_factor":
            try:
                value = float(value)
            except ValueError:
                console.print(f"[red]Error: {key} must be a number[/red]")
                raise typer.Exit(1)
        
        # Set attribute
        if hasattr(config, key_lower):
            setattr(config, key_lower, value)
        else:
            console.print(f"[red]Error: Unknown configuration key: {key}[/red]")
            console.print("[yellow]Supported keys: project_id, model, region, model_version, "
                        "auth_method, max_retries, timeout, log_level, log_format, "
                        "enable_cost_tracking[/yellow]")
            raise typer.Exit(1)
        
        # Validate updated config
        try:
            config_manager.validate_config(config.model_dump())
        except ConfigurationError as e:
            print_error(e)
            raise typer.Exit(2)
        
        # Save config
        config_manager.save_config(config)
        print_success(f"Set {key} = {value}")
        
    except ConfigurationError as e:
        print_error(e)
        raise typer.Exit(2)
    except Exception as e:
        print_error(e)
        raise typer.Exit(1)


def config_get(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="Configuration key to get"),
) -> None:
    """
    Get a configuration value.
    """
    try:
        config_manager = get_config_manager(ctx)
        config = config_manager.load_config()
        
        key_lower = key.lower()
        if hasattr(config, key_lower):
            value = getattr(config, key_lower)
            if value is None:
                console.print("(not set)")
            else:
                console.print(str(value))
        else:
            console.print(f"[red]Error: Unknown configuration key: {key}[/red]")
            raise typer.Exit(1)
        
    except ConfigurationError as e:
        print_error(e)
        raise typer.Exit(2)
    except Exception as e:
        print_error(e)
        raise typer.Exit(1)


def config_validate(ctx: typer.Context) -> None:
    """
    Validate configuration file.
    """
    try:
        config_manager = get_config_manager(ctx)
        config = config_manager.load_config()
        
        print_success("Configuration is valid")
        console.print(f"\n[cyan]Configuration file: {config_manager.config_path}[/cyan]")
        console.print(f"[cyan]Project ID: {config.project_id}[/cyan]")
        console.print(f"[cyan]Model: {config.model}[/cyan]")
        
    except ConfigurationError as e:
        print_error(e)
        raise typer.Exit(2)
    except Exception as e:
        print_error(e)
        raise typer.Exit(1)

