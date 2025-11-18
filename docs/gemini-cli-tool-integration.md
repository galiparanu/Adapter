# Integrasi Vertex Adapter sebagai Tool ke Gemini CLI

Panduan lengkap untuk menambahkan Vertex Adapter sebagai custom tool ke Gemini CLI, memungkinkan Gemini CLI menggunakan model-model dari Vertex AI (Claude, Gemini, Qwen).

## Overview

Vertex Adapter dapat diintegrasikan sebagai tool ke Gemini CLI, memberikan akses ke:
- **Claude models** (4.5 Sonnet, 3.5 Sonnet, 3 Opus)
- **Gemini models** (2.5 Pro, 1.5 Pro, 1.5 Flash)
- **Qwen models** (Coder, 2.5 Coder)

Melalui Vertex AI dengan fitur:
- Model switching
- Region selection
- Token usage tracking
- Error recovery dengan retry logic

## Prerequisites

1. **Gemini CLI terinstall**
   ```bash
   # Install Gemini CLI (jika belum)
   npm install -g @google/gemini-cli
   # atau
   pip install google-gemini-cli
   ```

2. **Vertex Adapter terinstall**
   ```bash
   cd /path/to/vertex-spec-adapter
   pip install -e ".[dev]"
   ```

3. **GCP Configuration**
   - Project dengan Vertex AI API enabled
   - Service account atau user credentials
   - Config file: `.specify/config.yaml`

## Setup Integration

### Metode 1: Automatic Registration (Recommended)

```bash
# Install wrapper script
python -m vertex_spec_adapter.tools.gemini_cli_integration

# Atau gunakan helper script
python scripts/register_gemini_tool.py
```

### Metode 2: Manual Registration

**1. Create Tool Instance:**

```python
from vertex_spec_adapter.tools.vertex_adapter_tool import VertexAdapterTool

tool = VertexAdapterTool()
```

**2. Register ke Gemini CLI:**

```python
from vertex_spec_adapter.tools.gemini_cli_integration import register_tool_to_gemini_cli

result = register_tool_to_gemini_cli(tool)
print(result)
```

**3. Verify Registration:**

```bash
# Check Gemini CLI config
cat ~/.gemini/config.json
```

## Tool Schema

Vertex Adapter Tool menyediakan actions berikut:

### 1. `generate` - Generate Text

Generate text menggunakan Vertex AI model.

**Parameters:**
- `prompt` (required): Prompt untuk generation
- `model_id` (optional): Model ID (default: dari config)
- `region` (optional): GCP region (default: dari config)
- `temperature` (optional): 0.0-2.0 (default: 0.7)
- `max_tokens` (optional): Maximum tokens

**Example:**
```python
result = tool.execute(
    action="generate",
    prompt="Write a Python function to calculate factorial",
    model_id="gemini-2-5-pro",
    temperature=0.3,
)
```

### 2. `list_models` - List Available Models

List semua available models.

**Parameters:**
- `provider` (optional): Filter by provider ('google', 'anthropic', 'qwen')
- `region` (optional): Filter by region

**Example:**
```python
result = tool.execute(
    action="list_models",
    provider="google",
)
```

### 3. `switch_model` - Switch Model

Switch ke model yang berbeda.

**Parameters:**
- `model_id` (required): Model ID untuk switch
- `region` (optional): Region untuk model

**Example:**
```python
result = tool.execute(
    action="switch_model",
    model_id="claude-4-5-sonnet",
    region="us-east5",
)
```

### 4. `get_model_info` - Get Model Information

Get detailed information tentang model.

**Parameters:**
- `model_id` (required): Model ID

**Example:**
```python
result = tool.execute(
    action="get_model_info",
    model_id="gemini-2-5-pro",
)
```

### 5. `test_connection` - Test Connection

Test koneksi ke Vertex AI.

**Example:**
```python
result = tool.execute(action="test_connection")
```

## Usage dengan Gemini CLI

### Setup Script

Buat file `setup_gemini_tool.py`:

```python
#!/usr/bin/env python3
"""Setup Vertex Adapter Tool untuk Gemini CLI."""

from vertex_spec_adapter.tools.vertex_adapter_tool import VertexAdapterTool
from vertex_spec_adapter.tools.gemini_cli_integration import register_tool_to_gemini_cli

def main():
    # Create tool
    tool = VertexAdapterTool()
    
    # Register
    result = register_tool_to_gemini_cli(tool)
    
    print(f"✓ {result['message']}")
    print(f"  Config saved to: {result['config_path']}")
    print(f"\nTool '{tool.name}' is now available in Gemini CLI!")
    print("\nUsage examples:")
    print("  gemini 'Use vertex_adapter to list available models'")
    print("  gemini 'Generate code using vertex_adapter with gemini-2-5-pro'")

if __name__ == "__main__":
    main()
```

**Run setup:**
```bash
python setup_gemini_tool.py
```

### Menggunakan Tool di Gemini CLI

Setelah tool ter-register, Anda bisa menggunakannya di Gemini CLI:

```bash
# List models
gemini "Use vertex_adapter tool to list all available models"

# Generate dengan specific model
gemini "Use vertex_adapter to generate Python code for a REST API using gemini-2-5-pro model"

# Switch model dan generate
gemini "Switch to claude-4-5-sonnet using vertex_adapter and generate a function"

# Get model info
gemini "Get information about gemini-2-5-pro model using vertex_adapter"
```

## Advanced Usage

### Custom Config Path

```python
from vertex_spec_adapter.tools.vertex_adapter_tool import VertexAdapterTool

# Use custom config
tool = VertexAdapterTool(config_path="/path/to/custom-config.yaml")
```

### Direct Tool Execution

```python
from vertex_spec_adapter.tools.vertex_adapter_tool import VertexAdapterTool

tool = VertexAdapterTool()

# Generate
result = tool.execute(
    action="generate",
    prompt="Your prompt here",
    model_id="gemini-2-5-pro",
    temperature=0.7,
)

print(result["content"])
print(f"Tokens used: {result['token_usage']}")
```

### Integration dengan Script

```python
#!/usr/bin/env python3
"""Script yang menggunakan Vertex Adapter Tool."""

from vertex_spec_adapter.tools.vertex_adapter_tool import VertexAdapterTool

def main():
    tool = VertexAdapterTool()
    
    # List models
    models = tool.execute(action="list_models", provider="google")
    print(f"Available Gemini models: {models['count']}")
    
    # Generate
    result = tool.execute(
        action="generate",
        prompt="Explain quantum computing in simple terms",
        model_id="gemini-2-5-pro",
    )
    
    print(result["content"])

if __name__ == "__main__":
    main()
```

## Configuration

### Vertex Adapter Config

Pastikan `.specify/config.yaml` sudah dikonfigurasi:

```yaml
project_id: "your-gcp-project-id"
region: "us-central1"
model:
  id: "gemini-2-5-pro"
authentication:
  method: "service_account"
  credentials_path: "/path/to/service-account.json"
```

### Gemini CLI Config

Tool akan otomatis ter-register di `~/.gemini/config.json`:

```json
{
  "tools": [
    {
      "name": "vertex_adapter",
      "type": "function",
      "schema": {
        "name": "vertex_adapter",
        "description": "Access Vertex AI models...",
        "parameters": {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "enum": ["generate", "list_models", "switch_model", ...]
            },
            ...
          }
        }
      }
    }
  ]
}
```

## Troubleshooting

### Tool Not Found

```bash
# Verify registration
cat ~/.gemini/config.json | grep vertex_adapter

# Re-register if needed
python setup_gemini_tool.py
```

### Configuration Error

```bash
# Test Vertex Adapter config
vertex-spec test

# Check config file
cat .specify/config.yaml
```

### Authentication Error

```bash
# Test authentication
vertex-spec test

# Refresh credentials
gcloud auth application-default login
```

## Best Practices

1. **Setup Once, Use Everywhere**
   - Register tool sekali setelah setup
   - Tool akan tersedia untuk semua Gemini CLI sessions

2. **Use Appropriate Models**
   - Gemini untuk general tasks
   - Claude untuk complex reasoning
   - Qwen untuk code generation

3. **Monitor Token Usage**
   - Check `token_usage` di response
   - Track costs dengan usage tracker

4. **Error Handling**
   - Tool automatically handles retries
   - Check `success` field di response
   - Handle errors gracefully

## Example Workflows

### Workflow 1: Code Generation

```bash
# Via Gemini CLI
gemini "Use vertex_adapter to generate a Python class for user management using gemini-2-5-pro"

# Via Python
tool = VertexAdapterTool()
result = tool.execute(
    action="generate",
    prompt="Create a Python class for user management",
    model_id="gemini-2-5-pro",
    temperature=0.3,
)
```

### Workflow 2: Model Comparison

```bash
# Compare models
gemini "Use vertex_adapter to list all models and compare their context windows"
```

### Workflow 3: Multi-Model Workflow

```python
tool = VertexAdapterTool()

# Generate dengan Gemini
result1 = tool.execute(
    action="generate",
    prompt="Generate code",
    model_id="gemini-2-5-pro",
)

# Switch ke Claude untuk review
result2 = tool.execute(
    action="switch_model",
    model_id="claude-4-5-sonnet",
)

result3 = tool.execute(
    action="generate",
    prompt=f"Review this code: {result1['content']}",
)
```

## Next Steps

- [Gemini CLI Integration](gemini-cli-integration.md) - Using adapter as CLI
- [Gemini Integration](gemini-integration.md) - Direct Gemini usage
- [Configuration Reference](configuration.md) - Config options
- [Authentication Guide](authentication.md) - Auth setup

