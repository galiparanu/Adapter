# Integrasi Vertex Adapter ke Gemini CLI

Panduan lengkap untuk menggunakan Vertex AI Spec Kit Adapter sebagai CLI tool untuk mengakses Gemini models.

## Overview

Vertex AI Spec Kit Adapter menyediakan CLI tool (`vertex-spec`) yang memungkinkan Anda menggunakan Gemini models melalui command line, terintegrasi dengan Spec Kit workflow.

## Setup Awal

### 1. Install Adapter

```bash
# Install dari source (development)
cd /path/to/vertex-spec-adapter
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Verify installation
vertex-spec --version
```

### 2. Setup Konfigurasi untuk Gemini

```bash
# Buat direktori config
mkdir -p .specify

# Copy example config
cp examples/gemini-config.yaml .specify/config.yaml

# Edit dengan project ID dan credentials Anda
nano .specify/config.yaml
```

**Minimal config untuk Gemini:**
```yaml
project_id: "your-gcp-project-id"
region: "us-central1"
model:
  id: "gemini-2-5-pro"
authentication:
  method: "service_account"
  credentials_path: "/path/to/service-account.json"
```

### 3. Setup Authentication

**Opsi A: Service Account (Recommended)**
```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# Atau set di config.yaml
# credentials_path: "/path/to/service-account.json"
```

**Opsi B: User Credentials**
```bash
# Login dengan gcloud
gcloud auth application-default login

# Set method di config.yaml
# method: "user_credentials"
```

### 4. Test Koneksi

```bash
# Test authentication dan koneksi
vertex-spec test

# Expected output:
# ✓ Authentication successful
# ✓ Vertex AI API accessible
# ✓ Model 'gemini-2-5-pro' available in region 'us-central1'
```

## Command Reference

### 1. List Available Models

```bash
# List semua model Gemini
vertex-spec models list --provider google

# List dengan format JSON
vertex-spec models list --provider google --format json

# Filter by region
vertex-spec models list --region us-central1
```

**Output:**
```
┏━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Model ID ┃ Name     ┃ Provider ┃ Region    ┃
┡━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ gemini-… │ Gemini   │ google   │ us-centr… │
│          │ 2.5 Pro  │          │           │
└──────────┴──────────┴──────────┴───────────┘
```

### 2. Configuration Management

```bash
# Show current configuration
vertex-spec config show

# Get specific value
vertex-spec config get project_id
vertex-spec config get model.id

# Set configuration value
vertex-spec config set project_id "new-project-id"
vertex-spec config set model.id "gemini-1-5-pro"

# Validate configuration
vertex-spec config validate
```

### 3. Spec Kit Commands dengan Gemini

#### A. Create Constitution

```bash
# Create project constitution
vertex-spec run constitution

# Dengan custom principles
vertex-spec run constitution \
  --principle "Code Quality" \
  --principle "Testing" \
  --principle "Security"
```

#### B. Create Feature Specification

```bash
# Create specification dari description
vertex-spec run specify "Add user authentication feature"

# Dengan custom branch
vertex-spec run specify "Add payment integration" \
  --branch "feature/payment"
```

#### C. Generate Implementation Plan

```bash
# Generate plan dari spec
vertex-spec run plan specs/001-user-auth/spec.md
```

#### D. Generate Task List

```bash
# Generate tasks dari plan
vertex-spec run tasks specs/001-user-auth/plan.md
```

#### E. Implement Features

```bash
# Implement dari tasks
vertex-spec run implement specs/001-user-auth/tasks.md

# Dengan checkpoint/resume
vertex-spec run implement specs/001-user-auth/tasks.md \
  --checkpoint .checkpoint.json \
  --resume
```

## Advanced Usage

### 1. Switch Model ke Gemini

Jika sudah menggunakan model lain, bisa switch:

```bash
# Update config untuk menggunakan Gemini
vertex-spec config set model.id "gemini-2-5-pro"
vertex-spec config set region "us-central1"

# Verify
vertex-spec config show
```

### 2. Debug Mode

Enable debug mode untuk detail lebih:

```bash
# Debug mode untuk semua commands
vertex-spec --debug test

# Debug mode untuk specific command
vertex-spec --debug run specify "Test feature"
```

### 3. Verbose Output

```bash
# Verbose mode
vertex-spec --verbose test

# Quiet mode (hanya errors)
vertex-spec --quiet test
```

### 4. Custom Config Path

```bash
# Gunakan config file custom
vertex-spec --config /path/to/custom-config.yaml test

# Atau via environment variable
export VERTEX_SPEC_CONFIG_PATH="/path/to/config.yaml"
vertex-spec test
```

## Workflow Lengkap dengan Gemini

### Contoh: Membuat Feature Baru

```bash
# 1. Setup (sekali saja)
vertex-spec init init-command
# Atau setup manual:
mkdir -p .specify
cp examples/gemini-config.yaml .specify/config.yaml
# Edit config.yaml dengan project ID dan credentials

# 2. Test koneksi
vertex-spec test

# 3. Create constitution (jika belum ada)
vertex-spec run constitution

# 4. Create feature specification
vertex-spec run specify "Add user authentication with JWT tokens"

# 5. Generate implementation plan
vertex-spec run plan specs/001-user-auth/spec.md

# 6. Generate task list
vertex-spec run tasks specs/001-user-auth/plan.md

# 7. Implement feature
vertex-spec run implement specs/001-user-auth/tasks.md
```

## Integration dengan Scripts

### Bash Script Example

```bash
#!/bin/bash
# generate-feature.sh

FEATURE_DESC="$1"
FEATURE_NUM=$(ls specs/ | wc -l | xargs printf "%03d")
FEATURE_DIR="specs/${FEATURE_NUM}-$(echo $FEATURE_DESC | tr ' ' '-')"

echo "Creating feature: $FEATURE_DESC"

# Create specification
vertex-spec run specify "$FEATURE_DESC" --branch "feature/${FEATURE_NUM}"

# Generate plan
vertex-spec run plan "${FEATURE_DIR}/spec.md"

# Generate tasks
vertex-spec run tasks "${FEATURE_DIR}/plan.md"

echo "Feature created in: $FEATURE_DIR"
```

**Usage:**
```bash
chmod +x generate-feature.sh
./generate-feature.sh "Add payment gateway integration"
```

### Python Script Example

```python
#!/usr/bin/env python3
"""Script untuk generate feature menggunakan Gemini."""

import subprocess
import sys

def run_command(cmd):
    """Run CLI command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def generate_feature(description):
    """Generate feature specification."""
    print(f"Generating specification for: {description}")
    run_command(f'vertex-spec run specify "{description}"')
    
    # Get latest spec
    # ... (implementasi untuk get latest spec path)
    
    print("Feature specification created!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_feature.py 'Feature description'")
        sys.exit(1)
    
    generate_feature(sys.argv[1])
```

## Environment Variables

Anda bisa override config dengan environment variables:

```bash
# Override project ID
export VERTEX_SPEC_PROJECT_ID="my-project-id"

# Override region
export VERTEX_SPEC_REGION="us-central1"

# Override model
export VERTEX_SPEC_MODEL_ID="gemini-2-5-pro"

# Override config path
export VERTEX_SPEC_CONFIG_PATH="/path/to/config.yaml"

# GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

## Troubleshooting

### Error: "Configuration not found"

```bash
# Check config file exists
ls -la .specify/config.yaml

# Create jika belum ada
mkdir -p .specify
cp examples/gemini-config.yaml .specify/config.yaml
```

### Error: "Model not found"

```bash
# Verify model tersedia
vertex-spec models list --provider google

# Check region
vertex-spec models list --region us-central1
```

### Error: "Authentication failed"

```bash
# Test authentication
vertex-spec test

# Refresh credentials (jika user credentials)
gcloud auth application-default login

# Verify service account permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:YOUR_SA@PROJECT.iam.gserviceaccount.com"
```

### Debug Issues

```bash
# Enable debug mode
vertex-spec --debug test

# Check logs (jika configured)
cat .specify/logs/vertex-spec.log
```

## Best Practices

1. **Gunakan Service Account untuk Production**
   ```bash
   # Set di config.yaml
   authentication:
     method: "service_account"
     credentials_path: "/secure/path/service-account.json"
   ```

2. **Version Control Config Template**
   ```bash
   # Commit example config
   git add examples/gemini-config.yaml
   
   # Jangan commit actual config dengan credentials
   echo ".specify/config.yaml" >> .gitignore
   ```

3. **Use Checkpoints untuk Long Operations**
   ```bash
   # Implement dengan checkpoint
   vertex-spec run implement tasks.md --checkpoint .checkpoint.json
   
   # Resume jika interrupted
   vertex-spec run implement tasks.md --checkpoint .checkpoint.json --resume
   ```

4. **Monitor Token Usage**
   ```bash
   # Check usage setelah operations
   # (akan ditampilkan di output jika verbose mode)
   vertex-spec --verbose run specify "Feature description"
   ```

## Quick Reference

```bash
# Setup
vertex-spec init init-command
vertex-spec test

# Models
vertex-spec models list
vertex-spec models list --provider google

# Config
vertex-spec config show
vertex-spec config set model.id "gemini-2-5-pro"

# Spec Kit Commands
vertex-spec run constitution
vertex-spec run specify "Description"
vertex-spec run plan spec.md
vertex-spec run tasks plan.md
vertex-spec run implement tasks.md

# Options
vertex-spec --debug [command]
vertex-spec --verbose [command]
vertex-spec --quiet [command]
vertex-spec --config /path/to/config.yaml [command]
```

## Next Steps

- [Gemini Integration Guide](gemini-integration.md) - Detail tentang Gemini models
- [Configuration Reference](configuration.md) - Semua config options
- [Authentication Guide](authentication.md) - Setup authentication
- [Troubleshooting Guide](troubleshooting.md) - Common issues

