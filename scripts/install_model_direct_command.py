#!/usr/bin/env python3
"""Install direct model injection command for Gemini CLI (bypasses adapter)."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vertex_spec_adapter.gemini_cli.command_installer import (
    GeminiCLICommandInstaller,
    InstallationResult,
)


def main() -> None:
    """Main entry point for installer script."""
    installer = GeminiCLICommandInstaller()
    
    # Use direct injection template
    direct_template = Path(__file__).parent.parent / "vertex_spec_adapter" / "gemini_cli" / "model_direct.toml"
    
    if not direct_template.exists():
        print(f"✗ Template not found: {direct_template}")
        sys.exit(1)
    
    # Check if already installed
    if installer.is_installed():
        print(f"⚠ Command already installed at {installer.command_file}")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response not in ("y", "yes"):
            print("Installation cancelled.")
            sys.exit(0)
        force = True
    else:
        force = False
    
    # Install command with direct template
    result: InstallationResult = installer.install(force=force, command_file=direct_template)
    
    if result.success:
        print(f"✓ {result.message}")
        print("\nDirect model injection command installed!")
        print("This command bypasses the adapter layer and directly reads from config.")
        print("\nUsage in Gemini CLI:")
        print("  /model-direct  # Inject model from .specify/config.yaml")
        sys.exit(0)
    else:
        print(f"✗ Installation failed: {result.error}")
        print(f"  {result.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()

