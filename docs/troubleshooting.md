# Troubleshooting Guide

Common issues and solutions for the Vertex AI Spec Kit Adapter.

## Quick Diagnostics

### Enable Debug Mode

Get detailed diagnostic information:

```bash
vertex-spec --debug [command]
```

### Check Configuration

```bash
# View current configuration
vertex-spec config show

# Validate configuration
vertex-spec config validate
```

### Test Connection

```bash
# Test authentication and API access
vertex-spec test
```

## Common Issues

### Authentication Issues

#### "Authentication failed"

**Symptoms:**
- Error: "Authentication failed" or "Invalid credentials"

**Solutions:**
1. **Service Account:**
   - Verify credentials file exists: `ls -la /path/to/service-account.json`
   - Check file permissions: `chmod 600 /path/to/service-account.json`
   - Verify service account has `roles/aiplatform.user` role
   - Check credentials haven't expired

2. **User Credentials:**
   - Refresh credentials: `gcloud auth application-default login`
   - Verify login: `gcloud auth list`
   - Check project: `gcloud config get-value project`

3. **ADC:**
   - Verify running on GCP infrastructure
   - Check Workload Identity configuration (if using GKE)

**Debug:**
```bash
vertex-spec --debug test
```

#### "Permission denied"

**Symptoms:**
- Error: "Permission denied" or "Insufficient permissions"

**Solutions:**
1. Grant required role to service account:
   ```bash
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
     --role="roles/aiplatform.user"
   ```

2. Verify billing is enabled for project

3. Check Vertex AI API is enabled:
   ```bash
   gcloud services list --enabled | grep aiplatform
   ```

#### "Credentials not found"

**Symptoms:**
- Error: "Credentials file not found"

**Solutions:**
1. Verify path in configuration:
   ```bash
   vertex-spec config get authentication.credentials_path
   ```

2. Check file exists:
   ```bash
   ls -la $(vertex-spec config get authentication.credentials_path)
   ```

3. Use absolute path in configuration

### Configuration Issues

#### "Invalid configuration"

**Symptoms:**
- Error: "ConfigurationError" or "Invalid configuration"

**Solutions:**
1. Validate configuration:
   ```bash
   vertex-spec config validate
   ```

2. Check YAML syntax (use online YAML validator)

3. Verify required fields:
   - `project_id` (required)
   - `region` (required)
   - `model.id` (required)

4. Check for typos in field names

#### "Model not found"

**Symptoms:**
- Error: "ModelNotFoundError" or "Model not available"

**Solutions:**
1. List available models:
   ```bash
   vertex-spec models list
   ```

2. Check model is available in region:
   ```bash
   vertex-spec models list --region us-central1
   ```

3. Verify model ID spelling (case-sensitive)

4. Check model version format:
   - Claude: `@YYYYMMDD` (e.g., `@20250929`)
   - Gemini: `latest` or specific version
   - Qwen: `@YYYYMMDD`

#### "Region not available"

**Symptoms:**
- Error: "Model not available in region"

**Solutions:**
1. List available regions for model:
   ```bash
   vertex-spec models list --provider anthropic
   ```

2. Use model's default region or switch to available region

3. Update configuration:
   ```bash
   vertex-spec config set region us-east5
   ```

### API Issues

#### "Rate limit exceeded"

**Symptoms:**
- Error: "RateLimitError" or "429 Too Many Requests"

**Solutions:**
1. Wait before retrying (error message includes wait time)

2. Check quota limits in GCP Console:
   - Go to Vertex AI > Quotas
   - Check requests per minute/hour

3. Implement rate limiting in your code

4. Use exponential backoff (already implemented in adapter)

**Debug:**
```bash
vertex-spec --debug [command]
```

#### "Quota exceeded"

**Symptoms:**
- Error: "QuotaExceededError"

**Solutions:**
1. Check quota limits in GCP Console

2. Request quota increase if needed

3. Wait for quota reset (usually hourly/daily)

4. Use different project or region

#### "Server error" (500, 502, 503, 504)

**Symptoms:**
- Error: "APIError" with status code 5xx

**Solutions:**
1. This is a temporary GCP service issue
2. Wait a few seconds and retry
3. Check [GCP Status Page](https://status.cloud.google.com/)
4. Retry logic will automatically handle this

**Debug:**
```bash
vertex-spec --debug [command]
```

### Performance Issues

#### "Slow response times"

**Symptoms:**
- Commands taking longer than expected

**Solutions:**
1. Check network connectivity
2. Verify region is close to your location
3. Check GCP service status
4. Enable debug mode to see latency breakdown

**Debug:**
```bash
vertex-spec --debug [command]
```

#### "High memory usage"

**Symptoms:**
- Process using excessive memory

**Solutions:**
1. Check for memory leaks in your code
2. Reduce batch sizes if processing large files
3. Use streaming for large responses

### Spec Kit Integration Issues

#### "Spec Kit command failed"

**Symptoms:**
- Error when running `vertex-spec run [command]`

**Solutions:**
1. Verify Spec Kit is properly installed
2. Check project structure follows Spec Kit conventions
3. Review error message for specific issue
4. Enable debug mode for detailed diagnostics

#### "Checkpoint not found"

**Symptoms:**
- Error when resuming from checkpoint

**Solutions:**
1. Check checkpoint file exists: `.specify/.checkpoint.json`
2. Verify checkpoint file is valid JSON
3. Create new checkpoint if corrupted

## Getting More Help

### Error Messages

All errors include:
- Clear error message
- Suggested fix
- Troubleshooting steps (for API errors)

### Debug Mode

Enable detailed diagnostics:

```bash
vertex-spec --debug [command]
```

This shows:
- Authentication method used
- API request/response details
- Retry attempts
- Circuit breaker state
- Performance metrics

### Logs

Check log files (if configured):

```bash
# View logs
cat .specify/logs/vertex-spec.log

# Or if custom log path
cat $(vertex-spec config get logging.file)
```

### Community Support

- Check existing issues on GitHub
- Review documentation
- Enable debug mode and share output (sanitize credentials)

## Prevention Tips

1. **Validate Configuration Early:**
   ```bash
   vertex-spec config validate
   ```

2. **Test Connection Regularly:**
   ```bash
   vertex-spec test
   ```

3. **Use Service Accounts for Production:**
   - More secure than user credentials
   - Better for CI/CD
   - Easier to manage permissions

4. **Monitor Quotas:**
   - Set up alerts in GCP Console
   - Track usage regularly

5. **Keep Credentials Secure:**
   - Never commit to version control
   - Use secret manager for production
   - Rotate keys regularly

## Still Need Help?

If you've tried the solutions above and still have issues:

1. Enable debug mode and capture output
2. Check GCP service status
3. Review error messages carefully (they include troubleshooting steps)
4. Check logs for additional context
5. Open an issue with:
   - Error message
   - Debug output (sanitized)
   - Configuration (sanitized)
   - Steps to reproduce

