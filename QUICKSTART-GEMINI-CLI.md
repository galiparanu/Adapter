# Quick Start: Vertex Adapter sebagai Tool untuk Gemini CLI

Panduan cepat untuk menambahkan Vertex Adapter sebagai tool ke Gemini CLI.

## Tujuan

Menambahkan Vertex Adapter sebagai **custom tool** ke Gemini CLI, sehingga Gemini CLI bisa menggunakan model-model dari Vertex AI (Claude, Gemini, Qwen) melalui adapter ini.

## Setup (3 Langkah)

### Langkah 1: Setup Vertex Adapter Config

```bash
# Buat config directory
mkdir -p .specify

# Copy example config
cp examples/gemini-config.yaml .specify/config.yaml

# Edit dengan project ID dan credentials Anda
nano .specify/config.yaml
```

**Minimal config:**
```yaml
project_id: "your-gcp-project-id"
region: "us-central1"
model:
  id: "gemini-2-5-pro"
authentication:
  method: "service_account"
  credentials_path: "/path/to/service-account.json"
```

### Langkah 2: Register Tool ke Gemini CLI

```bash
# Register tool
python scripts/register_gemini_tool.py
```

**Expected output:**
```
✓ Tool created: vertex_adapter
✓ Tool registered successfully
  Config saved to: ~/.gemini/config.json
🎉 Vertex Adapter Tool is now available in Gemini CLI!
```

### Langkah 3: Test & Gunakan

```bash
# Test di Gemini CLI
gemini "Use vertex_adapter to list available models"

# Generate dengan model spesifik
gemini "Use vertex_adapter to generate Python code for REST API using gemini-2-5-pro"
```

## Tool Actions

Tool `vertex_adapter` menyediakan 5 actions:

### 1. `generate` - Generate Text
```bash
gemini "Use vertex_adapter to generate code for a todo list app"
```

### 2. `list_models` - List Models
```bash
gemini "Use vertex_adapter to list all available models"
```

### 3. `switch_model` - Switch Model
```bash
gemini "Use vertex_adapter to switch to claude-4-5-sonnet"
```

### 4. `get_model_info` - Get Model Info
```bash
gemini "Use vertex_adapter to get information about gemini-2-5-pro"
```

### 5. `test_connection` - Test Connection
```bash
gemini "Use vertex_adapter to test connection to Vertex AI"
```

## Usage Examples

### Example 1: Generate Code
```bash
gemini "Use vertex_adapter tool to generate a Python class for managing users with gemini-2-5-pro model"
```

### Example 2: Compare Models
```bash
gemini "Use vertex_adapter to list all models and compare their capabilities"
```

### Example 3: Multi-Step Workflow
```bash
gemini "Use vertex_adapter to: 1) list models, 2) switch to gemini-2-5-pro, 3) generate code for authentication"
```

## Direct Python Usage

Anda juga bisa menggunakan tool langsung dari Python:

```python
from vertex_spec_adapter.tools.vertex_adapter_tool import VertexAdapterTool

# Create tool
tool = VertexAdapterTool()

# List models
result = tool.execute(action="list_models", provider="google")
print(f"Available models: {result['count']}")

# Generate
result = tool.execute(
    action="generate",
    prompt="Write a Python function to calculate factorial",
    model_id="gemini-2-5-pro",
    temperature=0.3,
)
print(result["content"])
```

## Troubleshooting

### Tool Not Found
```bash
# Re-register
python scripts/register_gemini_tool.py

# Check config
cat ~/.gemini/config.json
```

### Config Error
```bash
# Test Vertex Adapter
vertex-spec test

# Verify config
cat .specify/config.yaml
```

## Dokumentasi Lengkap

- [Gemini CLI Tool Integration](docs/gemini-cli-tool-integration.md) - Panduan lengkap
- [Gemini Integration](docs/gemini-integration.md) - Direct Gemini usage
- [Configuration](docs/configuration.md) - Config reference

## Next Steps

1. ✅ Setup config (`.specify/config.yaml`)
2. ✅ Register tool (`python scripts/register_gemini_tool.py`)
3. ✅ Test dengan Gemini CLI
4. ✅ Mulai gunakan untuk workflow Anda!

