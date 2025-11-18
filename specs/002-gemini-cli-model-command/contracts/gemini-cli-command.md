# Gemini CLI Custom Command API Contract

**Component**: Gemini CLI Command Integration  
**Version**: 1.0.0  
**Date**: 2025-11-18

## Overview

This contract defines the API for integrating the interactive model menu as a custom command in Gemini CLI. The command overrides the default `/model` command with the Vertex Adapter implementation.

## Command File: model.toml

### Location

```
~/.gemini/commands/model.toml
```

### Format

```toml
description = "Manage Vertex AI models with interactive menu"
prompt = """
Execute interactive model selection:
!{python -m vertex_spec_adapter.cli.commands.model_interactive {{args}}}
"""
```

### Fields

- **description** (string, required): Command description shown in Gemini CLI help
- **prompt** (string, required): Command execution prompt with shell command

### Argument Handling

- `{{args}}`: Replaced with arguments passed to command
- If no arguments: Shows interactive menu
- If arguments provided: Can be used for non-interactive mode (future)

## Command Installer

### Class: GeminiCLICommandInstaller

```python
class GeminiCLICommandInstaller:
    def __init__(self) -> None
```

**Description**: Handles installation and management of Gemini CLI custom command.

### Method: install()

```python
def install(
    self,
    force: bool = False,
    command_file: Optional[Path] = None
) -> InstallationResult
```

**Description**: Installs the custom command file to Gemini CLI commands directory.

**Parameters**:
- `force` (bool): Overwrite existing command file if True
- `command_file` (Optional[Path]): Path to command TOML file. Defaults to package template.

**Returns**:
- `InstallationResult`: Result of installation operation

**Behavior**:
1. Creates `~/.gemini/commands/` directory if it doesn't exist
2. Copies command TOML file to `~/.gemini/commands/model.toml`
3. Verifies file was created successfully
4. Returns installation result

**Raises**:
- `FileNotFoundError`: If command template file not found
- `PermissionError`: If cannot write to commands directory
- `FileExistsError`: If file exists and force=False

### Method: uninstall()

```python
def uninstall(self) -> bool
```

**Description**: Removes the custom command file from Gemini CLI.

**Returns**:
- `bool`: True if successfully removed, False if file didn't exist

**Behavior**:
1. Checks if `~/.gemini/commands/model.toml` exists
2. Removes file if it exists
3. Returns True if removed, False if not found

**Raises**:
- `PermissionError`: If cannot remove file

### Method: is_installed()

```python
def is_installed(self) -> bool
```

**Description**: Checks if the custom command is installed.

**Returns**:
- `bool`: True if command file exists, False otherwise

**Behavior**:
1. Checks if `~/.gemini/commands/model.toml` exists
2. Optionally validates file content
3. Returns True if installed, False otherwise

### Method: get_command_path()

```python
def get_command_path(self) -> Path
```

**Description**: Gets the path to the Gemini CLI commands directory.

**Returns**:
- `Path`: Path to `~/.gemini/commands/`

**Behavior**:
1. Expands `~` to user home directory
2. Returns path to commands directory
3. Creates directory if it doesn't exist

## InstallationResult

### Attributes

```python
@dataclass
class InstallationResult:
    success: bool
    command_path: Path
    message: str
    error: Optional[str] = None
```

**Fields**:
- `success` (bool): Whether installation was successful
- `command_path` (Path): Path to installed command file
- `message` (str): Human-readable result message
- `error` (Optional[str]): Error message if installation failed

## Command Execution

### Entry Point

```python
# vertex_spec_adapter/cli/commands/model_interactive.py

def main(args: Optional[List[str]] = None) -> None:
    """Entry point for Gemini CLI command execution."""
    menu = ModelInteractiveMenu()
    result = menu.run()
    if result:
        sys.exit(0)
    else:
        sys.exit(1)
```

### Argument Parsing

```python
def parse_args(args: Optional[List[str]]) -> Dict[str, Any]
```

**Description**: Parses command arguments from Gemini CLI.

**Parameters**:
- `args` (Optional[List[str]]): Command arguments

**Returns**:
- `Dict[str, Any]`: Parsed arguments

**Current Behavior**:
- If no args: Show interactive menu
- If args provided: Can be used for future non-interactive mode

**Future Extensions**:
- `--list`: List all models
- `--switch MODEL_ID`: Switch to specific model (non-interactive)
- `--info MODEL_ID`: Show model information

## Command Template

### Template File Location

```
vertex_spec_adapter/gemini_cli/model.toml
```

### Template Content

```toml
description = "Manage Vertex AI models with interactive menu"
prompt = """
Execute interactive model selection:
!{python -m vertex_spec_adapter.cli.commands.model_interactive {{args}}}
"""
```

## Installation Script

### Script: install_gemini_model_command.py

```python
#!/usr/bin/env python3
"""Install Gemini CLI custom /model command."""

from vertex_spec_adapter.gemini_cli.command_installer import (
    GeminiCLICommandInstaller
)

def main():
    installer = GeminiCLICommandInstaller()
    result = installer.install()
    
    if result.success:
        print(f"✓ Command installed: {result.command_path}")
        print("Restart Gemini CLI to use the new command.")
    else:
        print(f"✗ Installation failed: {result.error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Usage

### Installation

```bash
# Install command
python -m vertex_spec_adapter.gemini_cli.command_installer

# Or use script
python scripts/install_gemini_model_command.py
```

### Verification

```bash
# Check if installed
ls ~/.gemini/commands/model.toml

# Test in Gemini CLI
gemini
> /model
```

### Uninstallation

```python
from vertex_spec_adapter.gemini_cli.command_installer import (
    GeminiCLICommandInstaller
)

installer = GeminiCLICommandInstaller()
installer.uninstall()
```

## Error Handling

### Installation Errors

- **FileNotFoundError**: Command template not found
  - **Solution**: Verify package installation
  - **Message**: "Command template not found. Please reinstall vertex-spec-adapter."

- **PermissionError**: Cannot write to commands directory
  - **Solution**: Check directory permissions
  - **Message**: "Cannot write to ~/.gemini/commands/. Check permissions."

- **FileExistsError**: Command already installed
  - **Solution**: Use `force=True` to overwrite
  - **Message**: "Command already installed. Use --force to overwrite."

### Execution Errors

- **ModuleNotFoundError**: Python module not found
  - **Solution**: Verify vertex-spec-adapter is installed
  - **Message**: "vertex-spec-adapter not found. Please install it."

- **ConfigurationError**: Config file not found
  - **Solution**: Run `vertex-spec init` first
  - **Message**: "Configuration not found. Run 'vertex-spec init' first."

## Testing Contract

### Unit Tests

- Test command file creation
- Test installation process
- Test uninstallation
- Test is_installed check
- Test error handling

### Integration Tests

- Test command registration in Gemini CLI
- Test command execution
- Test argument passing
- Test with real Gemini CLI

## Future Enhancements

### Non-Interactive Mode

```bash
# Future: Non-interactive model switching
gemini "/model --switch gemini-2-5-pro"

# Future: List models
gemini "/model --list"

# Future: Show model info
gemini "/model --info gemini-2-5-pro"
```

### Command Arguments

```toml
# Future: Support for arguments
prompt = """
!{python -m vertex_spec_adapter.cli.commands.model_interactive --args "{{args}}" --interactive}
"""
```

