#!/usr/bin/env python3
"""Install Gemini CLI custom /model command."""

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
    
    # Install command
    result: InstallationResult = installer.install(force=force)
    
    if result.success:
        print(f"✓ {result.message}")
        print("\nNext steps:")
        print("1. Restart Gemini CLI to use the new command")
        print("2. Type '/model' in Gemini CLI to open the interactive menu")
        sys.exit(0)
    else:
        print(f"✗ Installation failed: {result.error}")
        print(f"  {result.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()

