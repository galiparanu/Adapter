# CLI Commands API Contract

**Component**: CLI Interface  
**Version**: 1.0.0  
**Date**: 2025-01-27

## Overview

This contract defines the CLI command interface using Typer framework.

## Command Structure

```
vertex-spec [OPTIONS] COMMAND [ARGS]
```

### Global Options

- `--config PATH`: Path to config file (default: `.specify/config.yaml`)
- `--verbose`: Enable verbose output
- `--quiet`: Suppress all output except errors
- `--debug`: Enable debug mode
- `--version`: Show version and exit
- `--help`: Show help message

## Commands

### init

Initialize a new Spec Kit project with Vertex AI adapter.

```bash
vertex-spec init [OPTIONS] [PROJECT_DIR]
```

**Options**:
- `--project-id TEXT`: GCP project ID
- `--region TEXT`: Default region
- `--model TEXT`: Default model
- `--interactive`: Run interactive setup wizard (default)
- `--non-interactive`: Skip interactive prompts

**Behavior**:
- Creates `.specify/` directory structure
- Creates `config.yaml` with user-provided or default values
- Validates GCP credentials
- Tests Vertex AI connectivity
- Initializes Git repository if not present

**Output**: Success message with next steps

### config

Manage configuration.

```bash
vertex-spec config [COMMAND]
```

**Subcommands**:
- `show`: Display current configuration
- `set KEY VALUE`: Set configuration value
- `get KEY`: Get configuration value
- `validate`: Validate configuration file
- `edit`: Open config file in editor

**Examples**:
```bash
vertex-spec config set model claude-4-5-sonnet
vertex-spec config set region us-east5
vertex-spec config validate
```

### test

Test Vertex AI connection and configuration.

```bash
vertex-spec test [OPTIONS]
```

**Options**:
- `--model TEXT`: Test specific model
- `--region TEXT`: Test specific region
- `--verbose`: Show detailed test results

**Behavior**:
- Validates credentials
- Tests authentication
- Checks model availability
- Sends test request to Vertex AI
- Displays connection status and latency

**Output**: Test results with success/failure status

### models

List available models and their information.

```bash
vertex-spec models [OPTIONS]
```

**Options**:
- `--region TEXT`: Filter by region
- `--provider TEXT`: Filter by provider (anthropic, google, qwen)
- `--format TEXT`: Output format (table, json, yaml)

**Output**: Table or structured data listing:
- Model ID
- Model name
- Provider
- Access pattern (MaaS/Native SDK)
- Available regions
- Latest version
- Cost per 1M tokens (if available)

### run

Execute Spec Kit command with Vertex AI.

```bash
vertex-spec run COMMAND [ARGS]
```

**Commands**:
- `constitution [PRINCIPLES...]`: Run /speckit.constitution
- `specify DESCRIPTION`: Run /speckit.specify
- `plan [SPEC_PATH]`: Run /speckit.plan
- `tasks [PLAN_PATH]`: Run /speckit.tasks
- `implement [TASKS_PATH]`: Run /speckit.implement

**Options**:
- `--model TEXT`: Override default model
- `--region TEXT`: Override default region
- `--stream`: Stream response
- `--checkpoint PATH`: Checkpoint file path

**Examples**:
```bash
vertex-spec run specify "Add user authentication"
vertex-spec run plan specs/001-user-auth/spec.md
vertex-spec run implement specs/001-user-auth/tasks.md
```

## Output Format

### Success Output

```
✓ Configuration loaded successfully
✓ Authenticated with GCP
✓ Model 'claude-4-5-sonnet' available in 'us-east5'
✓ Spec created: specs/001-user-auth/spec.md
```

### Error Output

```
✗ Authentication failed
  → Run 'gcloud auth login' or set GOOGLE_APPLICATION_CREDENTIALS
  → See docs/authentication.md for more help
```

### Progress Indicators

For long-running operations:

```
Generating specification... [████████████████████] 100%
Creating files... [████████████████████] 100%
Committing changes... [████████████████████] 100%
```

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Configuration error
- `3`: Authentication error
- `4`: API error
- `5`: File/Git error

## Implementation Notes

1. **Interactive Mode**: Default to interactive for better UX
2. **Progress Bars**: Use rich library for progress indicators
3. **Colored Output**: Use rich for success (green), error (red), warning (yellow)
4. **Error Messages**: Always include suggested fixes
5. **Help Text**: Comprehensive help with examples for each command

## Testing Requirements

- Unit tests for each command
- Integration tests with real CLI execution
- Test error handling and exit codes
- Test interactive prompts (mocked input)
- Test output formatting
- Test on all platforms (Linux, macOS, Windows)

