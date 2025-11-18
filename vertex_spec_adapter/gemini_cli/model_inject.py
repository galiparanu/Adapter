#!/usr/bin/env python3
"""
Direct model injection for Gemini CLI - bypasses adapter layer.

This script directly reads the model from config and injects it into
Gemini CLI's context, allowing direct model usage without adapter.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import yaml


def get_model_from_config(config_path: Optional[Path] = None) -> dict:
    """
    Get model configuration directly from config file.
    
    Args:
        config_path: Path to config file (default: .specify/config.yaml)
    
    Returns:
        Dictionary with model, region, and project_id
    """
    if config_path is None:
        config_path = Path(".specify/config.yaml")
    
    if not config_path.exists():
        # Try absolute path from current working directory
        cwd = Path.cwd()
        config_path = cwd / ".specify" / "config.yaml"
    
    if not config_path.exists():
        return {
            "model": "gemini-2.5-pro",
            "region": "us-central1",
            "project_id": "default-project",
        }
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}
        
        return {
            "model": config.get("model", "gemini-2.5-pro"),
            "region": config.get("region", "us-central1"),
            "project_id": config.get("project_id", "default-project"),
        }
    except Exception as e:
        print(f"Error reading config: {e}", file=sys.stderr)
        return {
            "model": "gemini-2.5-pro",
            "region": "us-central1",
            "project_id": "default-project",
        }


def inject_model_to_gemini_cli() -> None:
    """
    Inject model configuration directly into Gemini CLI context.
    
    This function:
    1. Reads model from .specify/config.yaml
    2. Sets environment variables
    3. Outputs JSON that Gemini CLI can use
    """
    config = get_model_from_config()
    
    # Set environment variables for direct access
    os.environ["VERTEX_MODEL"] = config["model"]
    os.environ["VERTEX_REGION"] = config["region"]
    os.environ["VERTEX_PROJECT_ID"] = config["project_id"]
    
    # Output JSON for Gemini CLI to parse
    output = {
        "model": config["model"],
        "region": config["region"],
        "project_id": config["project_id"],
        "message": f"Model set to {config['model']} in region {config['region']}",
    }
    
    print(json.dumps(output, indent=2))


def main() -> None:
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # JSON output mode for programmatic access
        config = get_model_from_config()
        print(json.dumps(config, indent=2))
    else:
        # Human-readable output
        inject_model_to_gemini_cli()


if __name__ == "__main__":
    main()

