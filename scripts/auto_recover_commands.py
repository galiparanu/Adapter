#!/usr/bin/env python3
"""
Auto-recovery script untuk restore Gemini CLI commands setelah update.

Script ini:
1. Cek apakah commands masih ada
2. Jika tidak, auto-install dari template
3. Verifikasi installation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vertex_spec_adapter.gemini_cli.command_installer import (
    GeminiCLICommandInstaller,
    InstallationResult,
)


def check_and_recover() -> bool:
    """
    Check dan recover commands jika diperlukan.
    
    Returns:
        True jika recovery berhasil atau tidak diperlukan
    """
    installer = GeminiCLICommandInstaller()
    
    # Check /model command
    model_installed = installer.is_installed()
    
    # Check /model-direct command
    direct_file = installer.commands_dir / "model_direct.toml"
    direct_installed = direct_file.exists()
    
    recovered = False
    
    # Recover /model command
    if not model_installed:
        print("⚠ /model command not found, recovering...")
        result: InstallationResult = installer.install(force=False)
        if result.success:
            print(f"✓ /model command recovered: {result.message}")
            recovered = True
        else:
            print(f"✗ Failed to recover /model: {result.error}")
            return False
    
    # Recover /model-direct command
    if not direct_installed:
        print("⚠ /model-direct command not found, recovering...")
        direct_template = (
            Path(__file__).parent.parent
            / "vertex_spec_adapter"
            / "gemini_cli"
            / "model_direct.toml"
        )
        
        if direct_template.exists():
            import shutil
            try:
                shutil.copy2(direct_template, direct_file)
                print(f"✓ /model-direct command recovered")
                recovered = True
            except Exception as e:
                print(f"✗ Failed to recover /model-direct: {e}")
                return False
        else:
            print(f"✗ Template not found: {direct_template}")
            return False
    
    if not recovered:
        print("✓ All commands already installed")
    
    return True


def main() -> None:
    """Main entry point."""
    print("🔧 Auto-Recovery: Gemini CLI Commands")
    print("-" * 50)
    print()
    
    success = check_and_recover()
    
    if success:
        print()
        print("✓ Recovery complete!")
        print("  Commands available:")
        print("    - /model (interactive menu)")
        print("    - /model-direct (direct injection)")
        sys.exit(0)
    else:
        print()
        print("✗ Recovery failed")
        print("  Please run installer manually:")
        print("    python scripts/install_gemini_model_command.py")
        sys.exit(1)


if __name__ == "__main__":
    main()

