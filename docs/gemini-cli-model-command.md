# Gemini CLI `/model` Command

Complete guide for using the custom `/model` command in Gemini CLI to manage Vertex AI models interactively.

## Overview

The custom `/model` command overrides Gemini CLI's default command with an interactive menu system that allows you to browse, view detailed information, and switch between Vertex AI models seamlessly.

## Features

- **Interactive Menu**: Rich-based terminal UI with keyboard navigation
- **Model Details**: View context window, pricing, capabilities, and description on hover
- **Quick Switching**: Switch models with a single selection
- **Current Model Indicator**: Always see which model is active
- **Error Handling**: Graceful error handling with helpful troubleshooting steps
- **Cross-Platform**: Works on Linux, macOS, and Windows (with fallback for unsupported terminals)

## Installation

### Prerequisites

1. **Gemini CLI installed**
   ```bash
   # Check if Gemini CLI is installed
   gemini --version
   ```

2. **Vertex Adapter installed**
   ```bash
   pip install -e ".[dev]"
   ```

3. **GCP Authentication configured**
   ```bash
   # Authenticate with gcloud
   gcloud auth login
   
   # Verify authentication
   gcloud auth print-access-token
   ```

### Install Custom Command

```bash
# Method 1: Use installer script (recommended)
python scripts/install_gemini_model_command.py

# Method 2: Use Python module
python -m vertex_spec_adapter.gemini_cli.command_installer
```

The installer will:
- Create `~/.gemini/commands/` directory if it doesn't exist
- Copy `model.toml` to `~/.gemini/commands/model.toml`
- Verify installation

### Verify Installation

```bash
# Check if command file exists
ls ~/.gemini/commands/model.toml

# Check file content
cat ~/.gemini/commands/model.toml
```

Expected content:
```toml
description = "Manage Vertex AI models with interactive menu"
prompt = """
Execute interactive model selection:
!{python -m vertex_spec_adapter.gemini_cli.model_command {{args}}}
"""
```

## Usage

### Basic Usage

1. **Start Gemini CLI**
   ```bash
   gemini
   ```

2. **Open Model Menu**
   ```
   > /model
   ```

3. **Navigate Menu**
   - Use `↑` / `↓` arrow keys to navigate
   - Use `Enter` to select a model
   - Use `Escape` to cancel
   - Use `Home` / `End` to jump to first/last model

4. **View Model Details**
   - Hover over a model (highlighted with arrow `▶`) to see details in the right panel
   - Details include:
     - Model Name & ID
     - Context Window
     - Pricing (Input/Output per 1K tokens)
     - Capabilities
     - Status (Active indicator if current model)
     - Description

5. **Switch Model**
   - Select a model with `Enter`
   - Wait for confirmation message
   - Model switch is immediate (< 500ms)
   - Configuration is automatically saved

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑` | Navigate up |
| `↓` | Navigate down |
| `Home` | Jump to first model |
| `End` | Jump to last model |
| `Enter` | Select current model |
| `Escape` | Cancel and exit |
| `Ctrl+C` | Cancel and exit (graceful) |

### Menu Layout

```
┌─ Current Model: Gemini 2.5 Pro ─────────────────────┐
│                                                      │
├─ Available Models ────────┬─ Model Information ────┤
│ ▶ Gemini 2.5 Pro           │ Model: Gemini 2.5 Pro  │
│   DeepSeek V3.1            │ ID: gemini-2.5-pro     │
│   Qwen Coder               │                         │
│   DeepSeek R1 0528         │ Context: 1M+ tokens     │
│   Kimi K2                  │                         │
│   GPT OSS 120B             │ Pricing:                │
│   Llama 3.1                │   Input: $0.50/1M       │
│                            │   Output: $1.50/1M       │
│                            │                         │
│                            │ Capabilities:           │
│                            │ • General-purpose       │
│                            │ • Code generation       │
│                            │ • Reasoning             │
│                            │                         │
│                            │ Status: ✓ Active        │
│                            │                         │
│                            │ Description:            │
│                            │ Advanced general-       │
│                            │ purpose model...        │
└────────────────────────────┴────────────────────────┘
```

## Supported Models

The menu displays only models from `vertex-config.md`:

1. **DeepSeek V3.1** (`deepseek-ai/deepseek-v3.1-maas`)
2. **Qwen Coder** (`qwen/qwen3-coder-480b-a35b-instruct-maas`)
3. **Gemini 2.5 Pro** (`gemini-2.5-pro`)
4. **DeepSeek R1 0528** (`deepseek-ai/deepseek-r1-0528-maas`)
5. **Kimi K2** (`moonshotai/kimi-k2-thinking-maas`)
6. **GPT OSS 120B** (`openai/gpt-oss-120b-maas`)
7. **Llama 3.1** (`meta/llama-3.1-405b-instruct-maas`)

Models are sorted alphabetically by name.

## Error Handling

### Common Errors and Solutions

#### 1. "No models available"

**Cause**: ModelRegistry connection failed or no models configured.

**Solution**:
```bash
# Check ModelRegistry connection
vertex-spec models list

# Verify vertex-config.md contains valid models
cat vertex-config.md
```

#### 2. "gcloud CLI not installed"

**Cause**: gcloud CLI is not in PATH.

**Solution**:
```bash
# macOS
brew install google-cloud-sdk

# Linux
# See: https://cloud.google.com/sdk/docs/install

# After installation
gcloud auth login
```

#### 3. "Authentication failed"

**Cause**: GCP credentials are invalid or expired.

**Solution**:
```bash
# Re-authenticate
gcloud auth login

# Verify token
gcloud auth print-access-token
```

#### 4. "Terminal doesn't support interactive mode"

**Cause**: Terminal is too small or doesn't support alternate screen mode.

**Solution**: The menu automatically falls back to a simple text menu. You can still select models by number.

#### 5. "Model not available in region"

**Cause**: Selected model is not available in the configured region.

**Solution**: Check available regions for the model:
```bash
vertex-spec models list --region <region>
```

## Advanced Usage

### Non-Interactive Mode (Future)

Future versions will support non-interactive mode:

```bash
# List models
gemini "/model --list"

# Switch model
gemini "/model --switch gemini-2.5-pro"

# Get model info
gemini "/model --info gemini-2.5-pro"
```

### Uninstall Command

```python
from vertex_spec_adapter.gemini_cli.command_installer import GeminiCLICommandInstaller

installer = GeminiCLICommandInstaller()
installer.uninstall()
```

Or manually:
```bash
rm ~/.gemini/commands/model.toml
```

## Troubleshooting

### Menu doesn't appear

1. **Check installation**:
   ```bash
   ls ~/.gemini/commands/model.toml
   ```

2. **Restart Gemini CLI**: Close and reopen Gemini CLI after installation.

3. **Check Python path**: Ensure `python -m vertex_spec_adapter.gemini_cli.model_command` works.

### Menu is slow or unresponsive

1. **Check terminal size**: Minimum recommended is 80x24.
2. **Check network**: ModelRegistry queries require network access.
3. **Enable debug mode**: Check logs for issues.

### Model switch fails

1. **Check authentication**: Run `gcloud auth print-access-token`.
2. **Check permissions**: Verify service account has `roles/aiplatform.user`.
3. **Check region**: Verify model is available in selected region.

## Performance

- **Menu rendering**: < 50ms
- **Hover detail update**: < 10ms
- **Keyboard response**: < 100ms
- **Model switch**: < 500ms

## Examples

### Example 1: Switch to Gemini 2.5 Pro

```
> /model
[Interactive menu appears]
[Navigate to "Gemini 2.5 Pro"]
[Press Enter]
✓ Successfully switched to 'Gemini 2.5 Pro' (gemini-2.5-pro) in region 'global'
```

### Example 2: View Model Details

```
> /model
[Interactive menu appears]
[Navigate to "Qwen Coder"]
[Hover shows details in right panel]
[See context window, pricing, capabilities]
```

### Example 3: Cancel Selection

```
> /model
[Interactive menu appears]
[Press Escape or Ctrl+C]
Selection cancelled by user
```

## Best Practices

1. **Always verify authentication** before using the menu:
   ```bash
   gcloud auth print-access-token
   ```

2. **Check model availability** in your region:
   ```bash
   vertex-spec models list --region <region>
   ```

3. **Use interactive menu** for exploration, direct commands for automation (when available).

4. **Keep gcloud CLI updated**:
   ```bash
   gcloud components update
   ```

## Related Documentation

- [Configuration Guide](configuration.md)
- [Authentication Guide](authentication.md)
- [Troubleshooting Guide](troubleshooting.md)
- [Gemini CLI Integration](gemini-cli-integration.md)

## Support

For issues and questions:
- Check error messages (they include troubleshooting steps)
- Review [Troubleshooting Guide](troubleshooting.md)
- Enable debug mode: `vertex-spec --debug [command]`

