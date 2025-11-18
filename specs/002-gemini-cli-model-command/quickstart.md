# Quick Start Guide: Gemini CLI Custom `/model` Command

**Feature**: Gemini CLI Custom `/model` Command  
**Date**: 2025-11-18

## Overview

This quick start guide helps you get started with the custom `/model` command for Gemini CLI. You'll learn how to install, configure, and use the interactive model selection menu.

## Prerequisites

1. **Gemini CLI installed**
   ```bash
   npm install -g @google/gemini-cli
   # or
   brew install gemini-cli
   ```

2. **Vertex Adapter installed**
   ```bash
   cd /path/to/vertex-spec-adapter
   pip install -e ".[dev]"
   ```

3. **GCP Authentication**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

4. **Vertex Adapter configured**
   ```bash
   vertex-spec init
   ```

## Installation

### Step 1: Install Custom Command

```bash
# Install the custom /model command
python -m vertex_spec_adapter.gemini_cli.command_installer

# Or use the installation script
python scripts/install_gemini_model_command.py
```

**Expected Output**:
```
✓ Command installed: ~/.gemini/commands/model.toml
Restart Gemini CLI to use the new command.
```

### Step 2: Verify Installation

```bash
# Check if command file exists
ls ~/.gemini/commands/model.toml

# Should show: /home/user/.gemini/commands/model.toml
```

### Step 3: Restart Gemini CLI

```bash
# Exit and restart Gemini CLI
gemini
```

## Usage

### Basic Usage

1. **Start Gemini CLI**
   ```bash
   gemini
   ```

2. **Run the /model command**
   ```
   > /model
   ```

3. **Interactive Menu Appears**
   - Use ↑/↓ arrow keys to navigate
   - Hover details appear automatically
   - Press Enter to select a model
   - Press Escape to cancel

### Menu Navigation

**Keyboard Shortcuts**:
- `↑` / `↓`: Navigate up/down through models
- `Enter`: Select highlighted model
- `Escape`: Cancel and exit
- `Home`: Jump to first model
- `End`: Jump to last model

### Model Selection

1. Navigate to desired model using arrow keys
2. View hover details (shown automatically)
3. Press Enter to select
4. Model switches and configuration updates
5. Success message displayed

### Example Workflow

```
> /model

┌─ Current Model: gemini-2-5-pro ─────────────┐
│                                              │
│ ┌─ Available Models ─┐  ┌─ Model Info ────┐ │
│ │ > Gemini 2.5 Pro   │  │ Gemini 2.5 Pro  │ │
│ │   DeepSeek V3.1    │  │ ID: gemini-2-5  │ │
│ │   Qwen Coder       │  │                 │ │
│ │   DeepSeek R1      │  │ Context: 1M     │ │
│ │   Kimi K2          │  │ Pricing: ...     │ │
│ │   GPT OSS 120B     │  │ Capabilities:   │ │
│ │   Llama 3.1        │  │ • General       │ │
│ └────────────────────┘  │ • Coding        │ │
│                          │                 │ │
│                          │ Description:    │ │
│                          │ Best for...     │ │
│                          └─────────────────┘ │
└──────────────────────────────────────────────┘

[Press Enter to select, Escape to cancel]
```

## Configuration

### Model Configuration

The selected model is automatically saved to `.specify/config.yaml`:

```yaml
model:
  id: "gemini-2-5-pro"  # Updated automatically
```

### View Current Model

```bash
# In Gemini CLI
> /model
# Current model shown at top of menu

# Or via Vertex Adapter CLI
vertex-spec config get model.id
```

## Troubleshooting

### Command Not Found

**Problem**: `/model` command not recognized in Gemini CLI

**Solutions**:
1. Verify installation:
   ```bash
   ls ~/.gemini/commands/model.toml
   ```

2. Reinstall command:
   ```bash
   python -m vertex_spec_adapter.gemini_cli.command_installer --force
   ```

3. Restart Gemini CLI

### Authentication Error

**Problem**: "Authentication failed" error

**Solutions**:
1. Check gcloud authentication:
   ```bash
   gcloud auth list
   ```

2. Re-authenticate:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

3. Verify credentials:
   ```bash
   gcloud auth print-access-token
   ```

### Terminal Not Supported

**Problem**: Menu doesn't display correctly

**Solutions**:
1. Check terminal support:
   ```bash
   echo $TERM
   ```

2. Use supported terminal:
   - macOS: Terminal.app, iTerm2
   - Linux: gnome-terminal, konsole, xterm
   - Windows: Windows Terminal, PowerShell

3. Fallback mode: Simple text menu will be used automatically

### Model Not Available

**Problem**: Selected model not available

**Solutions**:
1. Check model availability:
   ```bash
   vertex-spec models list
   ```

2. Verify GCP project has access to model

3. Check region configuration:
   ```bash
   vertex-spec config get region
   ```

## Advanced Usage

### Non-Interactive Mode (Future)

```bash
# Future: Direct model switch
gemini "/model --switch gemini-2-5-pro"

# Future: List models
gemini "/model --list"

# Future: Show model info
gemini "/model --info gemini-2-5-pro"
```

### Custom Configuration

Edit `.specify/config.yaml` to customize:

```yaml
model:
  id: "gemini-2-5-pro"  # Default model
  version: "latest"     # Model version

region: "us-central1"   # Default region
```

## Uninstallation

### Remove Custom Command

```python
from vertex_spec_adapter.gemini_cli.command_installer import (
    GeminiCLICommandInstaller
)

installer = GeminiCLICommandInstaller()
installer.uninstall()
```

Or manually:
```bash
rm ~/.gemini/commands/model.toml
```

## Next Steps

1. **Explore Models**: Try different models to find the best fit
2. **Read Documentation**: See full documentation in `docs/`
3. **Customize**: Adjust configuration for your needs
4. **Report Issues**: Open issues on GitHub if you encounter problems

## Support

- **Documentation**: `docs/gemini-cli-model-command.md`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## Examples

### Example 1: Switch to Coding Model

```
> /model
[Navigate to Qwen Coder]
[Press Enter]
✓ Model switched to qwen/qwen3-coder-480b-a35b-instruct-maas
```

### Example 2: View Model Details

```
> /model
[Navigate to any model]
[View hover details automatically]
[See context window, pricing, capabilities]
```

### Example 3: Cancel Selection

```
> /model
[Navigate through models]
[Press Escape]
Selection cancelled
```

## Validation Scenarios

### Scenario 1: First-Time Setup

1. Install Vertex Adapter
2. Run `vertex-spec init`
3. Install Gemini CLI command
4. Run `/model` in Gemini CLI
5. Select a model
6. Verify config updated

**Expected**: Model switches successfully, config persists

### Scenario 2: Model Switching

1. Current model: gemini-2-5-pro
2. Run `/model`
3. Navigate to DeepSeek V3.1
4. Select model
5. Verify switch

**Expected**: Model switches, config updated, success message shown

### Scenario 3: Error Handling

1. Run `/model` without authentication
2. See error message
3. Authenticate with gcloud
4. Run `/model` again
5. Success

**Expected**: Clear error message, easy recovery

## Performance Targets

- Menu rendering: < 50ms
- Hover update: < 10ms
- Model switch: < 500ms
- Keyboard response: < 100ms

## Security Notes

- Uses existing gcloud authentication
- No credentials stored in command file
- Safe shell command execution
- Input validation on all user inputs

