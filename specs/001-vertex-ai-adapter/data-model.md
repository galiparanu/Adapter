# Data Model: Vertex AI Spec Kit Adapter

**Feature**: Vertex AI Spec Kit Adapter  
**Date**: 2025-01-27

## Overview

This document defines the core entities, their attributes, relationships, and validation rules for the Vertex AI Spec Kit Adapter. All entities are designed to support both MaaS (Model-as-a-Service) REST API and Native SDK access patterns.

## Core Entities

### Configuration

Represents adapter settings including GCP project ID, model-specific default regions (with override capability), default model, authentication method, retry settings, and logging preferences.

**Attributes**:
- `project_id` (string, required): GCP project ID
  - Validation: Must match pattern `^[a-z][-a-z0-9]{4,28}[a-z0-9]$`
  - Example: `my-project-123`
  
- `region` (string, optional): Default region override
  - Validation: Must be valid GCP region format (e.g., `us-central1`, `us-east5`)
  - Default: Model-specific default
  
- `model` (string, required): Default model identifier
  - Validation: Must be one of supported models or valid model ID
  - Examples: `claude-4-5-sonnet`, `gemini-2-5-pro`, `qwen-coder`
  
- `model_version` (string, optional): Specific model version to pin
  - Validation: Must match version format (e.g., `@20250929`, `@20241022`)
  - Default: Latest available version
  
- `model_regions` (dict, optional): Model-specific region overrides
  - Format: `{model_id: region}`
  - Example: `{"claude-4-5-sonnet": "us-east5", "gemini-2-5-pro": "us-central1"}`
  
- `auth_method` (enum, optional): Preferred authentication method
  - Values: `service_account`, `user_credentials`, `adc`, `auto`
  - Default: `auto` (try all methods in priority order)
  
- `service_account_path` (string, optional): Path to service account key file
  - Validation: File must exist and be readable
  - Environment variable: `GOOGLE_APPLICATION_CREDENTIALS`
  
- `max_retries` (integer, optional): Maximum retry attempts
  - Validation: 0-5
  - Default: 3
  
- `retry_backoff_factor` (float, optional): Exponential backoff multiplier
  - Validation: > 0
  - Default: 1.0
  
- `timeout` (integer, optional): Request timeout in seconds
  - Validation: > 0
  - Default: 60
  
- `log_level` (enum, optional): Logging level
  - Values: `DEBUG`, `INFO`, `WARNING`, `ERROR`
  - Default: `INFO`
  
- `log_format` (enum, optional): Log output format
  - Values: `json`, `text`
  - Default: `text`
  
- `log_file` (string, optional): Path to log file
  - Default: None (stdout only)
  
- `enable_cost_tracking` (boolean, optional): Track token usage and costs
  - Default: `true`

**Relationships**:
- One-to-many with `ModelRequest`: Configuration used to create requests
- One-to-one with `AuthenticationCredentials`: Configuration determines auth method

**State Transitions**: None (immutable after load)

**Validation Rules**:
- All required fields must be present
- Project ID must be valid GCP format
- Region must be valid GCP region
- Model must be supported or valid model ID
- File paths must exist if specified
- Numeric values must be within valid ranges

### Authentication Credentials

Represents GCP authentication state including service account keys, user credentials, or Application Default Credentials. Cached with expiry tracking and validated before use.

**Attributes**:
- `type` (enum, required): Credential type
  - Values: `service_account`, `user_credentials`, `adc`, `workload_identity`
  
- `path` (string, optional): Path to credential file (for service account)
  - Validation: File must exist and be valid JSON
  
- `credentials` (object, optional): Credential object (from Google Auth library)
  - Internal use only, not serialized
  
- `valid` (boolean, required): Whether credentials are currently valid
  - Default: `false`
  
- `expired` (boolean, required): Whether credentials have expired
  - Default: `false`
  
- `expires_at` (datetime, optional): Credential expiration timestamp
  - Used for cache invalidation
  
- `token` (string, optional): Current access token
  - Internal use only, never logged
  
- `last_validated` (datetime, optional): Last validation timestamp
  - Used for cache TTL

**Relationships**:
- Many-to-one with `Configuration`: Multiple configs can use same credentials
- One-to-many with `ModelRequest`: Credentials used for all API calls

**State Transitions**:
- `uninitialized` → `valid`: After successful authentication
- `valid` → `expired`: When token expires
- `expired` → `valid`: After successful refresh
- `valid` → `invalid`: When validation fails

**Validation Rules**:
- Credentials must be valid before use
- Expired credentials must be refreshed
- Service account files must be valid JSON with required fields
- Tokens must not be logged or exposed

### Model Request

Represents a request to Vertex AI including model identifier (with optional version pinning), region, input content, parameters (temperature, max_tokens), streaming preference, and access pattern (MaaS or Native SDK). Validated for model availability, version format, and region compatibility.

**Attributes**:
- `model_id` (string, required): Model identifier
  - Examples: `claude-4-5-sonnet`, `gemini-2-5-pro`, `qwen-coder`
  
- `model_version` (string, optional): Specific version to use
  - Format: `@YYYYMMDD` or full version string
  - Default: Latest available
  
- `region` (string, required): GCP region for the request
  - Validation: Must be valid region where model is available
  
- `access_pattern` (enum, required): How to access the model
  - Values: `maas` (REST API), `native_sdk` (SDK)
  - Determined automatically based on model
  
- `messages` (list, required): Conversation messages
  - Format: `[{"role": "user|assistant|system", "content": "..."}]`
  - Validation: Must have at least one message
  
- `temperature` (float, optional): Sampling temperature
  - Validation: 0.0-2.0
  - Default: 1.0
  
- `max_tokens` (integer, optional): Maximum tokens to generate
  - Validation: > 0, model-specific max
  - Default: Model default
  
- `stream` (boolean, optional): Whether to stream response
  - Default: `false`
  
- `project_id` (string, required): GCP project ID
  - Inherited from Configuration

**Relationships**:
- Many-to-one with `Configuration`: Request uses config settings
- Many-to-one with `AuthenticationCredentials`: Request uses credentials
- One-to-one with `APIResponse`: Request generates response

**State Transitions**:
- `pending` → `validated`: After validation passes
- `validated` → `sending`: When API call starts
- `sending` → `completed`: On successful response
- `sending` → `failed`: On error
- `failed` → `retrying`: When retry logic triggers
- `retrying` → `completed` or `failed`: After retry

**Validation Rules**:
- Model must be available in specified region
- Version format must be valid if specified
- Messages must be non-empty
- Temperature must be in valid range
- Max tokens must not exceed model limit

### API Response

Represents Vertex AI API response including generated content, token counts (input/output), metadata, and error information. Normalized across different model types.

**Attributes**:
- `content` (string, required): Generated text content
  - Normalized from different response formats
  
- `input_tokens` (integer, required): Number of input tokens used
  - Used for cost calculation
  
- `output_tokens` (integer, required): Number of output tokens generated
  - Used for cost calculation
  
- `total_tokens` (integer, required): Total tokens (input + output)
  - Calculated field
  
- `model` (string, required): Model identifier used
  - Matches request model_id
  
- `finish_reason` (enum, optional): Why generation stopped
  - Values: `stop`, `length`, `content_filter`, `error`
  
- `metadata` (dict, optional): Additional response metadata
  - Model-specific fields
  
- `error` (dict, optional): Error information if request failed
  - Format: `{"code": int, "message": str, "retry_after": int}`
  
- `latency_ms` (float, optional): Request latency in milliseconds
  - Used for performance tracking

**Relationships**:
- One-to-one with `ModelRequest`: Response to a request
- One-to-many with `Session`: Response contributes to session metrics

**State Transitions**: None (immutable)

**Validation Rules**:
- Content must be present on success
- Token counts must be non-negative
- Error must be present if request failed
- Model must match request model

### Session

Represents a user session including start time, commands executed, total tokens used, estimated cost, and performance metrics. Used for logging and reporting.

**Attributes**:
- `session_id` (string, required): Unique session identifier
  - Format: UUID or timestamp-based
  
- `start_time` (datetime, required): Session start timestamp
  
- `end_time` (datetime, optional): Session end timestamp
  - None if session is active
  
- `commands_executed` (list, required): List of Spec Kit commands run
  - Format: `[{"command": "constitution", "timestamp": datetime, "success": bool}]`
  
- `total_requests` (integer, required): Total API requests made
  - Default: 0
  
- `total_input_tokens` (integer, required): Total input tokens used
  - Default: 0
  
- `total_output_tokens` (integer, required): Total output tokens generated
  - Default: 0
  
- `total_tokens` (integer, required): Total tokens (calculated)
  - Default: 0
  
- `estimated_cost_usd` (float, required): Estimated cost in USD
  - Calculated from token usage and model pricing
  - Default: 0.0
  
- `requests_by_model` (dict, required): Request count per model
  - Format: `{model_id: count}`
  - Default: `{}`
  
- `average_latency_ms` (float, optional): Average request latency
  - Calculated from all requests
  
- `errors` (list, optional): List of errors encountered
  - Format: `[{"timestamp": datetime, "error": str, "command": str}]`

**Relationships**:
- One-to-many with `APIResponse`: Session aggregates responses
- One-to-one with `Configuration`: Session uses config

**State Transitions**:
- `active` → `completed`: When session ends normally
- `active` → `error`: When session ends with error
- `active` → `interrupted`: When session is interrupted (Ctrl+C)

**Validation Rules**:
- Session ID must be unique
- Token counts must be non-negative
- Cost must be non-negative
- Commands list must be chronological

### Spec Kit Artifact

Represents files created by Spec Kit commands (spec.md, plan.md, tasks.md, etc.) including their structure, content, and Git integration state.

**Attributes**:
- `artifact_type` (enum, required): Type of artifact
  - Values: `constitution`, `spec`, `plan`, `tasks`, `implementation`
  
- `file_path` (string, required): Relative path to artifact file
  - Format: `.specify/memory/constitution.md` or `specs/###-feature-name/spec.md`
  
- `content` (string, optional): File content
  - Not always loaded into memory
  
- `git_branch` (string, optional): Git branch where artifact was created
  - Format: `###-feature-name`
  
- `git_commit` (string, optional): Git commit SHA where artifact was created
  
- `created_at` (datetime, required): When artifact was created
  
- `updated_at` (datetime, optional): When artifact was last updated
  
- `valid` (boolean, required): Whether artifact structure is valid
  - Default: `true`
  
- `validation_errors` (list, optional): List of validation errors
  - Format: `[{"field": str, "error": str}]`

**Relationships**:
- Many-to-one with `Session`: Artifacts created during session
- One-to-many with `ModelRequest`: Artifacts may trigger multiple requests

**State Transitions**:
- `creating` → `created`: After file is written
- `created` → `validated`: After validation passes
- `validated` → `invalid`: If validation fails
- `created` → `committed`: After Git commit

**Validation Rules**:
- File path must follow Spec Kit conventions
- Content must match Spec Kit template structure
- Git branch must follow naming convention
- Artifact type must match file location

## Entity Relationships Diagram

```
Configuration
    │
    ├───> AuthenticationCredentials (1:1)
    │
    └───> ModelRequest (1:many)
            │
            └───> APIResponse (1:1)
                    │
                    └───> Session (many:1)
                            │
                            └───> SpecKitArtifact (1:many)
```

## Data Flow

1. **Configuration Load**: User config → Configuration entity → Validation
2. **Authentication**: Configuration → AuthenticationCredentials → Token cache
3. **Request Creation**: Configuration + User input → ModelRequest → Validation
4. **API Call**: ModelRequest + AuthenticationCredentials → Vertex AI API
5. **Response Processing**: API response → APIResponse → Normalization
6. **Session Tracking**: APIResponse → Session → Metrics aggregation
7. **Artifact Creation**: Session + ModelRequest → SpecKitArtifact → File system + Git

## Validation Summary

All entities include comprehensive validation:
- **Type validation**: Pydantic schemas ensure correct types
- **Format validation**: Regex patterns for IDs, regions, versions
- **Range validation**: Numeric values within acceptable ranges
- **Existence validation**: Files, models, regions must exist
- **Business rule validation**: Model availability, version compatibility

## Error Handling

Validation errors are captured in entity attributes:
- `validation_errors` list on entities
- Custom exceptions for different error types
- Clear error messages with troubleshooting steps
- No sensitive data in error messages

