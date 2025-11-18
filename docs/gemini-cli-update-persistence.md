# Gemini CLI Update & Config Persistence

Dokumentasi tentang bagaimana Vertex Adapter config dan commands berperilaku setelah Gemini CLI update.

## Skenario: Gemini CLI Update

### Apa yang Terjadi?

Ketika Gemini CLI di-update, biasanya:
- ✅ **Gemini CLI config** (`~/.gemini/config.json`) - **PERSIST**
- ✅ **Vertex Adapter config** (`.specify/config.yaml`) - **PERSIST** (di project directory)
- ❌ **Custom commands** (`~/.gemini/commands/*.toml`) - **MUNGKIN TERHAPUS**

### Mengapa Commands Bisa Terhapus?

1. Gemini CLI update mungkin reset `~/.gemini/commands/` directory
2. Clean install bisa menghapus custom commands
3. Version conflict bisa menyebabkan commands di-overwrite

### Mengapa Config Persist?

1. **Vertex Adapter config** disimpan di **project directory** (`.specify/config.yaml`)
   - Tidak terpengaruh oleh Gemini CLI update
   - Tetap ada di setiap project

2. **Gemini CLI config** (`~/.gemini/config.json`) biasanya persist
   - Tools registration tetap ada
   - Hanya commands yang mungkin terpengaruh

## Solusi: Auto-Recovery

### Script Auto-Recovery

Kami menyediakan script untuk auto-recover commands:

```bash
# Run auto-recovery
python scripts/auto_recover_commands.py
```

Script ini akan:
1. ✅ Cek apakah commands masih ada
2. ✅ Auto-install jika tidak ada
3. ✅ Verifikasi installation

### Manual Recovery

Jika auto-recovery gagal:

```bash
# Recover /model command
python scripts/install_gemini_model_command.py

# Recover /model-direct command
python scripts/install_model_direct_command.py
```

## Simulasi Update

Test apakah config masih bisa digunakan:

```bash
# Run simulation
python scripts/simulate_gemini_update.py
```

Output akan menunjukkan:
- State sebelum update
- State sesudah update
- Apakah config persist
- Apakah commands bisa di-recover

## Best Practices

### 1. Backup Commands (Opsional)

```bash
# Backup commands sebelum update
cp ~/.gemini/commands/*.toml ~/.gemini/commands/.backup/
```

### 2. Auto-Recovery di Startup

Tambahkan ke shell profile (`.bashrc`, `.zshrc`):

```bash
# Auto-recover Gemini CLI commands
if command -v python3 &> /dev/null; then
    python3 -m vertex_spec_adapter.gemini_cli.auto_recover 2>/dev/null
fi
```

### 3. Version Control Config

```bash
# Commit config ke git (tanpa credentials)
git add .specify/config.yaml
git commit -m "Add Vertex Adapter config"
```

## FAQ

### Q: Apakah config perlu di-inject lagi setelah update?

**A: TIDAK!** Config di `.specify/config.yaml` **PERSIST** karena:
- Disimpan di project directory
- Tidak terpengaruh oleh Gemini CLI update
- Tetap bisa digunakan langsung

### Q: Apakah commands perlu di-install ulang?

**A: MUNGKIN!** Commands di `~/.gemini/commands/` bisa terhapus:
- Run `python scripts/auto_recover_commands.py` untuk auto-recover
- Atau install manual jika diperlukan

### Q: Bagaimana cara prevent commands terhapus?

**A:** Tidak ada cara prevent 100%, tapi:
- Backup commands sebelum update
- Gunakan auto-recovery script
- Version control config

### Q: Apakah model selection persist?

**A: YA!** Model selection di config **PERSIST**:
- Tersimpan di `.specify/config.yaml`
- Tidak perlu inject lagi
- Langsung bisa digunakan

## Kesimpulan

| Item | Persist? | Action Setelah Update |
|------|----------|----------------------|
| Vertex Config | ✅ YES | Tidak perlu action |
| Model Selection | ✅ YES | Tidak perlu inject lagi |
| Commands | ❌ NO | Run auto-recovery |
| Tools Registration | ✅ YES | Tidak perlu action |

**TL;DR:**
- ✅ Config **PERSIST** - tidak perlu inject lagi
- ❌ Commands **MUNGKIN TERHAPUS** - run auto-recovery
- ✅ Model selection **PERSIST** - langsung bisa digunakan

