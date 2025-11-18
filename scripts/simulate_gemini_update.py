#!/usr/bin/env python3
"""
Simulasi Gemini CLI Update - Test apakah config masih bisa digunakan.

Skenario:
1. Simulasikan Gemini CLI update (hapus config/commands)
2. Cek apakah Vertex Adapter config masih ada
3. Test apakah bisa auto-recover
4. Verifikasi command masih berfungsi
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List


def simulate_gemini_cli_update() -> Dict[str, bool]:
    """
    Simulasikan Gemini CLI update yang menghapus config.
    
    Returns:
        Dictionary dengan status sebelum dan sesudah
    """
    gemini_config = Path.home() / ".gemini" / "config.json"
    commands_dir = Path.home() / ".gemini" / "commands"
    model_toml = commands_dir / "model.toml"
    model_direct_toml = commands_dir / "model_direct.toml"
    
    # State sebelum update
    state_before = {
        "gemini_config_exists": gemini_config.exists(),
        "commands_dir_exists": commands_dir.exists(),
        "model_command_exists": model_toml.exists(),
        "model_direct_command_exists": model_direct_toml.exists(),
    }
    
    # Backup jika ada
    backup_dir = Path.home() / ".gemini" / ".backup_before_update"
    if commands_dir.exists() and not backup_dir.exists():
        backup_dir.mkdir(parents=True, exist_ok=True)
        if model_toml.exists():
            shutil.copy2(model_toml, backup_dir / "model.toml")
        if model_direct_toml.exists():
            shutil.copy2(model_direct_toml, backup_dir / "model_direct.toml")
    
    # Simulasikan update: Hapus commands (biasanya Gemini CLI update bisa reset ini)
    if commands_dir.exists():
        # Simulasi: Hapus commands tapi keep config
        for cmd_file in commands_dir.glob("*.toml"):
            cmd_file.unlink()
            print(f"  ✗ Removed: {cmd_file.name}")
    
    # State sesudah update
    state_after = {
        "gemini_config_exists": gemini_config.exists(),
        "commands_dir_exists": commands_dir.exists(),
        "model_command_exists": model_toml.exists(),
        "model_direct_command_exists": model_direct_toml.exists(),
    }
    
    return {
        "before": state_before,
        "after": state_after,
        "backup_dir": str(backup_dir) if backup_dir.exists() else None,
    }


def check_vertex_config() -> Dict[str, any]:
    """Cek apakah Vertex Adapter config masih ada."""
    config_path = Path.cwd() / ".specify" / "config.yaml"
    
    if not config_path.exists():
        # Try parent directories
        for parent in Path.cwd().parents:
            test_config = parent / ".specify" / "config.yaml"
            if test_config.exists():
                config_path = test_config
                break
    
    return {
        "exists": config_path.exists(),
        "path": str(config_path) if config_path.exists() else None,
        "readable": config_path.exists() and config_path.is_file(),
    }


def auto_recover_commands() -> Dict[str, bool]:
    """
    Auto-recover commands setelah Gemini CLI update.
    
    Returns:
        Dictionary dengan status recovery
    """
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from vertex_spec_adapter.gemini_cli.command_installer import GeminiCLICommandInstaller
    
    installer = GeminiCLICommandInstaller()
    
    # Recover /model command
    model_recovered = False
    if not installer.is_installed():
        result = installer.install(force=False)
        model_recovered = result.success
    
    # Recover /model-direct command
    direct_recovered = False
    direct_template = Path(__file__).parent.parent / "vertex_spec_adapter" / "gemini_cli" / "model_direct.toml"
    if direct_template.exists():
        direct_installer = GeminiCLICommandInstaller()
        # Install to different file name
        direct_file = direct_installer.commands_dir / "model_direct.toml"
        if not direct_file.exists():
            try:
                shutil.copy2(direct_template, direct_file)
                direct_recovered = True
            except Exception:
                pass
    
    return {
        "model_command_recovered": model_recovered or installer.is_installed(),
        "model_direct_command_recovered": direct_recovered or direct_file.exists(),
    }


def main() -> None:
    """Main simulation."""
    print("=" * 60)
    print("SIMULASI: Gemini CLI Update")
    print("=" * 60)
    print()
    
    # Step 1: Check state sebelum update
    print("📋 Step 1: State Sebelum Update")
    print("-" * 60)
    vertex_config = check_vertex_config()
    print(f"✓ Vertex config exists: {vertex_config['exists']}")
    if vertex_config['exists']:
        print(f"  Path: {vertex_config['path']}")
    print()
    
    # Step 2: Simulasikan update
    print("🔄 Step 2: Simulasi Gemini CLI Update")
    print("-" * 60)
    print("Simulating: Gemini CLI update removes custom commands...")
    update_result = simulate_gemini_cli_update()
    
    print("\nState sebelum update:")
    for key, value in update_result["before"].items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {value}")
    
    print("\nState sesudah update:")
    for key, value in update_result["after"].items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {value}")
    print()
    
    # Step 3: Check apakah config masih ada
    print("🔍 Step 3: Verifikasi Config")
    print("-" * 60)
    vertex_config_after = check_vertex_config()
    if vertex_config_after["exists"]:
        print("✓ Vertex Adapter config MASIH ADA!")
        print(f"  Path: {vertex_config_after['path']}")
        print("  → Config persist karena disimpan di project directory")
    else:
        print("✗ Vertex Adapter config TIDAK DITEMUKAN")
        print("  → Perlu setup ulang")
    print()
    
    # Step 4: Auto-recover
    print("🔧 Step 4: Auto-Recovery")
    print("-" * 60)
    recovery = auto_recover_commands()
    
    if recovery["model_command_recovered"]:
        print("✓ /model command recovered")
    else:
        print("✗ /model command recovery failed")
    
    if recovery["model_direct_command_recovered"]:
        print("✓ /model-direct command recovered")
    else:
        print("✗ /model-direct command recovery failed")
    print()
    
    # Step 5: Kesimpulan
    print("📊 Kesimpulan")
    print("-" * 60)
    if vertex_config_after["exists"]:
        print("✓ Vertex Adapter config PERSIST setelah Gemini CLI update")
        print("  → Config disimpan di .specify/config.yaml (project directory)")
        print("  → Tidak terpengaruh oleh Gemini CLI update")
    else:
        print("✗ Config tidak ditemukan")
    
    if recovery["model_command_recovered"] or recovery["model_direct_command_recovered"]:
        print("✓ Commands bisa di-recover otomatis")
        print("  → Run installer script untuk restore commands")
    else:
        print("✗ Commands perlu di-install ulang")
    
    print()
    print("💡 Rekomendasi:")
    print("  1. Vertex config PERSIST (tidak perlu inject lagi)")
    print("  2. Commands perlu di-install ulang setelah update")
    print("  3. Buat script auto-recovery untuk otomatis restore")
    print()


if __name__ == "__main__":
    main()

