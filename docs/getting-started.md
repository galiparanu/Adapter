# Getting Started with Vertex AI Spec Kit Adapter

This guide will help you get up and running with the Vertex AI Spec Kit Adapter in minutes.

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.9 or higher**
   ```bash
   python --version  # Should show 3.9+
   ```

2. **Google Cloud Platform Account**
   - Active GCP account with billing enabled
   - Vertex AI API enabled in your project

3. **GCP Credentials** (choose one):
   - Service account key file (recommended for production)
   - User credentials via `gcloud auth login`
   - Application Default Credentials (ADC) for local development

## Installation

### Option 1: Install from Source (Development)

```bash
# Clone the repository
git clone <repository-url>
cd vertex-spec-adapter

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Verify installation
vertex-spec --version
```

### Option 2: Install from PyPI (Production)

```bash
pip install vertex-spec-adapter
```

## Quick Setup

### Step 1: Initialize the Adapter

Run the interactive setup wizard:

```bash
vertex-spec init --interactive
```

The wizard will prompt you for:
- **GCP Project ID**: Your Google Cloud project ID
- **Default Region**: Region for Vertex AI (e.g., `us-central1`)
- **Default Model**: Choose from Claude, Gemini, or Qwen
- **Authentication Method**: Service account, user credentials, or ADC

### Step 2: Verify Configuration

Check your configuration:

```bash
vertex-spec config show
```

### Step 3: Test Connection

Verify that authentication and API access work:

```bash
vertex-spec test
```

You should see:
```
✓ Authentication successful
✓ Vertex AI API accessible
✓ Model 'claude-4-5-sonnet' available in region 'us-east5'
```

### Step 4: List Available Models

See all available models and their information:

```bash
vertex-spec models list
```

## Basic Usage

### Using Spec Kit Commands

The adapter integrates with all Spec Kit commands:

```bash
# Create a project constitution
vertex-spec run constitution

# Create a feature specification
vertex-spec run specify "Add user authentication feature"

# Generate implementation plan
vertex-spec run plan specs/001-user-auth/spec.md

# Generate task list
vertex-spec run tasks specs/001-user-auth/plan.md

# Implement the feature
vertex-spec run implement specs/001-user-auth/tasks.md
```

### Direct Model Interaction

You can also interact with Vertex AI models directly:

```bash
# Test a simple prompt
vertex-spec run implement --prompt "Write a Python function to calculate factorial"
```

## Configuration Files

Configuration is stored in `.specify/config.yaml`:

```yaml
project_id: "my-gcp-project"
region: "us-central1"
model:
  id: "claude-4-5-sonnet"
  version: "@20250929"  # Optional, uses latest if omitted
authentication:
  method: "service_account"
  credentials_path: "/path/to/service-account.json"
retry:
  max_retries: 3
  initial_wait: 1.0
  max_wait: 60.0
logging:
  level: "INFO"
  format: "text"
```

See [Configuration Reference](configuration.md) for all options.

## Authentication Methods

### Method 1: Service Account (Recommended for Production)

1. Create a service account in GCP Console
2. Grant `roles/aiplatform.user` role
3. Download JSON key file
4. Set in config:

```yaml
authentication:
  method: "service_account"
  credentials_path: "/path/to/service-account.json"
```

### Method 2: User Credentials (Development)

```bash
# Authenticate with gcloud
gcloud auth login

# Set application default credentials
gcloud auth application-default login
```

Then in config:

```yaml
authentication:
  method: "user_credentials"
```

### Method 3: Application Default Credentials (ADC)

If running on GCP (Cloud Run, Compute Engine, etc.), ADC is automatically used:

```yaml
authentication:
  method: "adc"
```

See [Authentication Guide](authentication.md) for detailed instructions.

## Next Steps

- Read the [Configuration Guide](configuration.md) for advanced settings
- Check [Troubleshooting](troubleshooting.md) if you encounter issues
- Explore [Example Configurations](../examples/) for model-specific setups

## Getting Help

- **Error Messages**: All errors include troubleshooting steps
- **Debug Mode**: Run with `--debug` flag for detailed diagnostics
- **Logs**: Check `.specify/logs/` for detailed operation logs

