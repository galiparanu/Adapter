# Authentication Guide

Complete guide to authenticating with Google Cloud Platform for the Vertex AI Spec Kit Adapter.

## Overview

The adapter supports three authentication methods, tried in priority order:

1. **Service Account** (recommended for production)
2. **User Credentials** (development)
3. **Application Default Credentials (ADC)** (GCP environments)

## Method 1: Service Account (Production)

Service accounts are recommended for production use, CI/CD pipelines, and automated systems.

### Step 1: Create Service Account

1. Go to [GCP Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** > **Service Accounts**
3. Click **Create Service Account**
4. Enter name and description
5. Click **Create and Continue**

### Step 2: Grant Permissions

Grant the following role:
- **Vertex AI User** (`roles/aiplatform.user`)

You can also grant more specific permissions if needed.

### Step 3: Create and Download Key

1. Click on the service account
2. Go to **Keys** tab
3. Click **Add Key** > **Create new key**
4. Choose **JSON** format
5. Download and securely store the key file

### Step 4: Configure Adapter

Set in `.specify/config.yaml`:

```yaml
authentication:
  method: "service_account"
  credentials_path: "/path/to/service-account.json"
```

Or use environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### Security Best Practices

- **Never commit** service account keys to version control
- Store keys in secure location (e.g., secret manager)
- Use least privilege principle (minimum required permissions)
- Rotate keys regularly
- Use separate service accounts for different environments

## Method 2: User Credentials (Development)

User credentials are convenient for local development and testing.

### Step 1: Install gcloud CLI

```bash
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash

# Windows
# Download from https://cloud.google.com/sdk/docs/install
```

### Step 2: Authenticate

```bash
# Login to GCP
gcloud auth login

# Set application default credentials
gcloud auth application-default login
```

### Step 3: Set Project

```bash
gcloud config set project YOUR_PROJECT_ID
```

### Step 4: Configure Adapter

Set in `.specify/config.yaml`:

```yaml
authentication:
  method: "user_credentials"
```

No credentials path needed - uses gcloud credentials automatically.

### Refreshing Credentials

If credentials expire:

```bash
gcloud auth application-default login
```

## Method 3: Application Default Credentials (ADC)

ADC is automatically used when running on GCP infrastructure (Cloud Run, Compute Engine, GKE, etc.).

### When ADC is Used

- Running on Google Cloud Run
- Running on Compute Engine
- Running on Google Kubernetes Engine (GKE)
- Running on Cloud Functions
- Using Workload Identity

### Configuration

Set in `.specify/config.yaml`:

```yaml
authentication:
  method: "adc"
```

No additional setup needed - GCP automatically provides credentials.

### Workload Identity (GKE)

If using Workload Identity in GKE:

1. Create Kubernetes service account
2. Bind to GCP service account with required permissions
3. ADC will automatically use Workload Identity

## Authentication Priority

The adapter tries authentication methods in this order:

1. Service account (if `credentials_path` provided)
2. User credentials (if `gcloud auth login` used)
3. ADC (if running on GCP)

## Verifying Authentication

### Test Authentication

```bash
vertex-spec test
```

Expected output:
```
✓ Authentication successful
✓ Vertex AI API accessible
```

### Check Current Credentials

```bash
# Check gcloud credentials
gcloud auth list

# Check application default credentials
gcloud auth application-default print-access-token
```

### Debug Authentication Issues

Enable debug mode:

```bash
vertex-spec --debug test
```

This will show:
- Which authentication method is being used
- Credential file paths
- Token expiration times
- Detailed error messages

## Common Issues

### Issue: "Authentication failed"

**Causes:**
- Invalid service account key
- Expired user credentials
- Missing permissions

**Solutions:**
1. Verify credentials file exists and is readable
2. Check service account has `roles/aiplatform.user` role
3. Refresh user credentials: `gcloud auth application-default login`
4. Verify project ID is correct

### Issue: "Permission denied"

**Causes:**
- Service account missing required permissions
- Wrong project ID

**Solutions:**
1. Grant `roles/aiplatform.user` to service account
2. Verify project ID in configuration
3. Check billing is enabled for project

### Issue: "Credentials not found"

**Causes:**
- Credentials path incorrect
- File doesn't exist
- File permissions issue

**Solutions:**
1. Verify path in configuration
2. Check file exists: `ls -la /path/to/credentials.json`
3. Check file permissions: `chmod 600 /path/to/credentials.json`

## Security Checklist

- [ ] Service account keys stored securely (not in version control)
- [ ] Keys have minimum required permissions
- [ ] Keys rotated regularly
- [ ] Different service accounts for different environments
- [ ] Credentials file permissions set to 600
- [ ] No credentials in logs or error messages
- [ ] Use secret manager for production deployments

## Next Steps

- [Configuration Guide](configuration.md)
- [Troubleshooting](troubleshooting.md)

