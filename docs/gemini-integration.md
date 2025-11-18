# Panduan Integrasi Gemini dengan Vertex AI Spec Kit Adapter

Panduan lengkap untuk menggunakan model Gemini (Gemini 2.5 Pro, Gemini 1.5 Pro, Gemini 1.5 Flash) dengan Vertex AI Spec Kit Adapter.

## Prerequisites

1. **GCP Project dengan Vertex AI API enabled**

   ```bash
   # Enable Vertex AI API
   gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
   ```

2. **Authentication Setup**

   - Service account dengan role `roles/aiplatform.user`
   - Atau user credentials via `gcloud auth login`

3. **Python Dependencies**
   ```bash
   pip install google-cloud-aiplatform
   ```

## Konfigurasi Gemini

### 1. Setup Konfigurasi Dasar

Buat file `.specify/config.yaml`:

```yaml
project_id: "your-gcp-project-id"
region: "us-central1" # Default region untuk Gemini

model:
  id: "gemini-2-5-pro" # atau "gemini-1-5-pro", "gemini-1-5-flash"
  version: "latest" # atau versi spesifik

authentication:
  method: "service_account" # atau "user_credentials", "adc"
  credentials_path: "/path/to/service-account.json"
```

### 2. Model Gemini yang Tersedia

| Model ID           | Nama             | Context Window   | Default Region |
| ------------------ | ---------------- | ---------------- | -------------- |
| `gemini-2-5-pro`   | Gemini 2.5 Pro   | 1,000,000 tokens | us-central1    |
| `gemini-1-5-pro`   | Gemini 1.5 Pro   | 1,000,000 tokens | us-central1    |
| `gemini-1-5-flash` | Gemini 1.5 Flash | 1,000,000 tokens | us-central1    |

### 3. Region yang Tersedia

Gemini tersedia di:

- `us-central1` (default)
- `us-east5`
- `asia-southeast1` (untuk beberapa model)

## Cara Menggunakan

### Metode 1: Via CLI (Recommended)

#### A. Setup Awal

```bash
# 1. Initialize project
vertex-spec init init-command

# Atau buat config manual
mkdir -p .specify
cp examples/gemini-config.yaml .specify/config.yaml
# Edit dengan project ID dan credentials Anda
```

#### B. Test Koneksi

```bash
# Test authentication dan koneksi ke Gemini
vertex-spec test
```

Expected output:

```
✓ Authentication successful
✓ Vertex AI API accessible
✓ Model 'gemini-2-5-pro' available in region 'us-central1'
```

#### C. List Available Models

```bash
# Lihat semua model Gemini yang tersedia
vertex-spec models list --provider google

# Atau filter by region
vertex-spec models list --region us-central1
```

#### D. Gunakan Spec Kit Commands dengan Gemini

```bash
# 1. Create constitution
vertex-spec run constitution

# 2. Create feature specification
vertex-spec run specify "Add user authentication feature"

# 3. Generate implementation plan
vertex-spec run plan specs/001-user-auth/spec.md

# 4. Generate tasks
vertex-spec run tasks specs/001-user-auth/plan.md

# 5. Implement feature
vertex-spec run implement specs/001-user-auth/tasks.md
```

### Metode 2: Via Python Code

```python
from vertex_spec_adapter.core.client import VertexAIClient
from vertex_spec_adapter.core.config import ConfigurationManager

# Load configuration
config_manager = ConfigurationManager()
config = config_manager.load_config()

# Initialize client dengan Gemini
client = VertexAIClient(
    project_id=config.project_id,
    region=config.region,
    model_id="gemini-2-5-pro",
    model_version="latest",
    config=config,
)

# Generate text
messages = [
    {"role": "user", "content": "Write a Python function to calculate factorial"}
]

response = client.generate(messages, temperature=0.7, max_tokens=500)
print(response)

# Check token usage
print(f"Input tokens: {client.token_usage['input_tokens']}")
print(f"Output tokens: {client.token_usage['output_tokens']}")
```

### Metode 3: Switch Model ke Gemini

Jika sudah menggunakan model lain, bisa switch ke Gemini:

```python
# Switch dari Claude ke Gemini
client.switch_model(
    new_model_id="gemini-2-5-pro",
    new_region="us-central1",  # Optional, akan gunakan default jika tidak diisi
    new_model_version="latest"  # Optional
)

# Generate dengan Gemini
response = client.generate(messages)
```

## Konfigurasi Lanjutan

### Custom Temperature dan Max Tokens

```yaml
# .specify/config.yaml
model:
  id: "gemini-2-5-pro"
  version: "latest"
  temperature: 0.7 # 0.0 - 2.0
  max_tokens: 2048 # Optional
```

### Retry Configuration untuk Gemini

```yaml
retry:
  max_retries: 5
  initial_wait: 1.0
  max_wait: 120.0
  exponential_base: 2.0
  circuit_breaker:
    failure_threshold: 5
    recovery_timeout: 60
```

### Logging Configuration

```yaml
logging:
  level: "INFO" # DEBUG untuk detail lebih
  format: "json" # atau "text"
  file: "/var/log/vertex-spec-gemini.log" # Optional
```

## Contoh Use Cases

### 1. Code Generation

```python
messages = [
    {
        "role": "user",
        "content": """
        Write a Python class for managing a todo list with the following features:
        - Add todo items
        - Mark items as complete
        - List all todos
        - Filter by status
        """
    }
]

response = client.generate(messages, temperature=0.3)  # Lower temperature untuk code
print(response)
```

### 2. Documentation Generation

```python
messages = [
    {
        "role": "user",
        "content": "Generate API documentation for a REST endpoint: POST /api/users"
    }
]

response = client.generate(messages, temperature=0.7)
print(response)
```

### 3. Code Review

```python
code_snippet = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
"""

messages = [
    {
        "role": "user",
        "content": f"Review this code and suggest improvements:\n\n{code_snippet}"
    }
]

response = client.generate(messages, temperature=0.5)
print(response)
```

## Troubleshooting

### Error: "Model not found"

**Solusi:**

```bash
# Verify model tersedia
vertex-spec models list --provider google

# Check region
vertex-spec models list --region us-central1
```

### Error: "Authentication failed"

**Solusi:**

```bash
# Test authentication
vertex-spec test

# Refresh credentials jika menggunakan user credentials
gcloud auth application-default login

# Verify service account permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:YOUR_SA@YOUR_PROJECT.iam.gserviceaccount.com"
```

### Error: "Permission denied"

**Solusi:**

```bash
# Grant required role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_SA@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Error: "Rate limit exceeded"

**Solusi:**

- Wait beberapa detik sebelum retry
- Check quota di GCP Console
- Adapter akan otomatis retry dengan exponential backoff

### Debug Mode

Enable debug mode untuk detail lebih:

```bash
vertex-spec --debug test
```

Atau di Python:

```python
from vertex_spec_adapter.utils.logging import configure_logging

configure_logging(log_level="DEBUG", debug=True)
```

## Best Practices

1. **Gunakan Service Account untuk Production**

   - Lebih secure
   - Better untuk CI/CD
   - Easier permission management

2. **Pilih Model yang Sesuai**

   - `gemini-2-5-pro`: Best quality, untuk complex tasks
   - `gemini-1-5-pro`: Balanced quality dan speed
   - `gemini-1-5-flash`: Fastest, untuk simple tasks

3. **Optimize Temperature**

   - 0.0-0.3: Deterministic, untuk code generation
   - 0.4-0.7: Balanced, untuk general tasks
   - 0.8-2.0: Creative, untuk brainstorming

4. **Monitor Token Usage**

   ```python
   # Track usage
   print(client.usage_tracker.generate_report())
   ```

5. **Handle Errors Gracefully**

   ```python
   from vertex_spec_adapter.core.exceptions import APIError, RateLimitError

   try:
       response = client.generate(messages)
   except RateLimitError as e:
       print(f"Rate limited. Wait {e.retry_after} seconds")
   except APIError as e:
       print(f"Error: {e}")
       print(f"Troubleshooting: {e.troubleshooting_steps}")
   ```

## Cost Estimation

Gemini pricing (per 1M tokens):

- **Input**: $3.50
- **Output**: $10.50

Track usage:

```python
tracker = client.usage_tracker
print(tracker.generate_report())
```

## Next Steps

- [Configuration Reference](configuration.md)
- [Authentication Guide](authentication.md)
- [Troubleshooting Guide](troubleshooting.md)
- [Example Configurations](../examples/gemini-config.yaml)
