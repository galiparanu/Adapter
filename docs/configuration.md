# Configuration Reference

Complete reference for all configuration options in the Vertex AI Spec Kit Adapter.

## Configuration File Location

Configuration is stored in `.specify/config.yaml` in your project root.

## Configuration Schema

### Top-Level Fields

```yaml
project_id: string          # Required: GCP project ID
region: string              # Required: Default region for Vertex AI
model: ModelConfig          # Model configuration
authentication: AuthConfig   # Authentication settings
retry: RetryConfig          # Retry and circuit breaker settings
logging: LoggingConfig      # Logging configuration
```

### Model Configuration

```yaml
model:
  id: string                # Model ID (e.g., "claude-4-5-sonnet")
  version: string           # Optional: Model version (e.g., "@20250929")
                            # Omit to use latest version
```

**Available Models:**
- `claude-4-5-sonnet` - Claude 4.5 Sonnet (Anthropic)
- `gemini-2-5-pro` - Gemini 2.5 Pro (Google)
- `qwen-coder` - Qwen Coder (Alibaba)

**Model Versions:**
- Claude: `@YYYYMMDD` format (e.g., `@20250929`)
- Gemini: `latest` or specific version
- Qwen: `@YYYYMMDD` format

### Authentication Configuration

```yaml
authentication:
  method: string            # "service_account" | "user_credentials" | "adc"
  credentials_path: string  # Path to service account JSON (if method=service_account)
```

**Priority Order:**
1. Service account (if `credentials_path` provided)
2. User credentials (if `gcloud auth login` used)
3. Application Default Credentials (ADC)

### Retry Configuration

```yaml
retry:
  max_retries: int          # Maximum retry attempts (default: 3)
  initial_wait: float       # Initial wait time in seconds (default: 1.0)
  max_wait: float           # Maximum wait time in seconds (default: 60.0)
  exponential_base: float   # Exponential backoff base (default: 2.0)
  circuit_breaker:
    failure_threshold: int   # Failures before opening circuit (default: 5)
    recovery_timeout: int    # Seconds before recovery attempt (default: 60)
```

### Logging Configuration

```yaml
logging:
  level: string             # "DEBUG" | "INFO" | "WARNING" | "ERROR" (default: "INFO")
  format: string            # "text" | "json" (default: "text")
  file: string              # Optional: Path to log file
```

## Environment Variables

You can override configuration with environment variables:

```bash
export VERTEX_SPEC_PROJECT_ID="my-project"
export VERTEX_SPEC_REGION="us-central1"
export VERTEX_SPEC_MODEL_ID="claude-4-5-sonnet"
export VERTEX_SPEC_CONFIG_PATH="/custom/path/config.yaml"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

## Configuration Management Commands

### View Current Configuration

```bash
vertex-spec config show
```

### Get Specific Value

```bash
vertex-spec config get project_id
vertex-spec config get model.id
```

### Set Configuration Value

```bash
vertex-spec config set project_id "new-project-id"
vertex-spec config set model.id "gemini-2-5-pro"
```

### Validate Configuration

```bash
vertex-spec config validate
```

## Example Configurations

### Minimal Configuration

```yaml
project_id: "my-gcp-project"
region: "us-central1"
model:
  id: "claude-4-5-sonnet"
```

### Production Configuration

```yaml
project_id: "production-project"
region: "us-central1"
model:
  id: "claude-4-5-sonnet"
  version: "@20250929"
authentication:
  method: "service_account"
  credentials_path: "/secure/path/service-account.json"
retry:
  max_retries: 5
  initial_wait: 2.0
  max_wait: 120.0
logging:
  level: "INFO"
  format: "json"
  file: "/var/log/vertex-spec.log"
```

### Development Configuration

```yaml
project_id: "dev-project"
region: "us-central1"
model:
  id: "gemini-2-5-pro"
authentication:
  method: "user_credentials"
retry:
  max_retries: 3
logging:
  level: "DEBUG"
  format: "text"
```

See [Example Configurations](../examples/) for model-specific examples.

## Configuration Validation

The adapter validates configuration on load:

- **Project ID**: Must be valid GCP project ID format
- **Region**: Must be valid GCP region (e.g., `us-central1`)
- **Model ID**: Must be supported model
- **Model Version**: Must match model's version format
- **Credentials Path**: File must exist and be readable (if provided)

## Configuration Precedence

1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration file (`.specify/config.yaml`)
4. Default values (lowest priority)

## Troubleshooting

### Invalid Configuration

If you see configuration errors:

1. Run `vertex-spec config validate` to check for issues
2. Check YAML syntax (use a YAML validator)
3. Verify all required fields are present
4. Check file permissions for credentials path

### Configuration Not Found

If the adapter can't find your config:

1. Ensure `.specify/config.yaml` exists in project root
2. Use `--config` flag to specify custom path
3. Set `VERTEX_SPEC_CONFIG_PATH` environment variable

