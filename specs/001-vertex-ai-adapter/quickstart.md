# Quickstart Guide: Vertex AI Spec Kit Adapter

**Feature**: Vertex AI Spec Kit Adapter  
**Date**: 2025-01-27

## Overview

This guide provides key validation scenarios for testing the Vertex AI Spec Kit Adapter. Use these scenarios to verify the implementation meets the specification requirements.

## Prerequisites

1. Python 3.9+ installed
2. GCP project with Vertex AI API enabled
3. GCP credentials configured (one of):
   - Service account key file
   - User credentials (`gcloud auth login`)
   - Application Default Credentials

## Installation

```bash
# Install from source (development)
pip install -e ".[dev]"

# Or install from PyPI (when published)
pip install vertex-spec-adapter
```

## Quick Validation Scenarios

### Scenario 1: Initial Setup (5 minutes)

**Goal**: Verify 5-minute setup process (SC-001)

**Steps**:
1. Run `vertex-spec init --interactive`
2. Follow interactive wizard:
   - Enter GCP project ID
   - Select default region
   - Select default model
3. Verify configuration created at `.specify/config.yaml`
4. Run `vertex-spec test` to verify connection

**Expected Result**:
- Setup completes in under 5 minutes
- Configuration file created with valid values
- Test command succeeds with "Connection successful" message

**Success Criteria**: SC-001 - Setup completes in under 5 minutes

---

### Scenario 2: Authentication Methods

**Goal**: Verify all three authentication methods work (SC-002)

**Test 2a: Service Account**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
vertex-spec test
```

**Test 2b: User Credentials**
```bash
gcloud auth login
unset GOOGLE_APPLICATION_CREDENTIALS
vertex-spec test
```

**Test 2c: Application Default Credentials**
```bash
gcloud auth application-default login
unset GOOGLE_APPLICATION_CREDENTIALS
vertex-spec test
```

**Expected Result**: All three methods authenticate successfully

**Success Criteria**: SC-002 - 100% success rate for valid credential scenarios

---

### Scenario 3: Spec Kit Commands

**Goal**: Verify all five Spec Kit commands work (SC-003)

**Test 3a: Constitution**
```bash
vertex-spec run constitution
# Verify: .specify/memory/constitution.md created
```

**Test 3b: Specify**
```bash
vertex-spec run specify "Add user authentication feature"
# Verify: specs/001-user-auth/spec.md created with proper structure
```

**Test 3c: Plan**
```bash
vertex-spec run plan specs/001-user-auth/spec.md
# Verify: plan.md, data-model.md, contracts/ created
```

**Test 3d: Tasks**
```bash
vertex-spec run tasks specs/001-user-auth/plan.md
# Verify: tasks.md created with structured task list
```

**Test 3e: Implement**
```bash
vertex-spec run implement specs/001-user-auth/tasks.md
# Verify: Code files generated, tests created
```

**Expected Result**: All commands execute successfully, creating properly structured artifacts

**Success Criteria**: SC-003 - 95% success rate for Spec Kit commands

---

### Scenario 4: Model Switching

**Goal**: Verify model flexibility (SC-010)

**Steps**:
1. Create spec with Claude: `vertex-spec run specify "Test feature" --model claude-4-5-sonnet`
2. Switch to Gemini: `vertex-spec run plan specs/001-test-feature/spec.md --model gemini-2-5-pro`
3. Switch to Qwen: `vertex-spec run tasks specs/001-test-feature/plan.md --model qwen-coder`

**Expected Result**: 
- Each command uses specified model
- Project context maintained across model switches
- No errors or workflow breaks

**Success Criteria**: SC-010 - Model switching works without losing context

---

### Scenario 5: Error Handling

**Goal**: Verify error messages are helpful (SC-005)

**Test 5a: Invalid Credentials**
```bash
# Remove credentials
unset GOOGLE_APPLICATION_CREDENTIALS
gcloud auth revoke
vertex-spec test
```

**Expected Error**: Clear message with steps to fix (e.g., "Run 'gcloud auth login'")

**Test 5b: Invalid Model/Region**
```bash
vertex-spec run specify "Test" --model invalid-model --region invalid-region
```

**Expected Error**: Lists available models/regions with suggestions

**Test 5c: Rate Limit (if possible)**
```bash
# Make many rapid requests
for i in {1..100}; do vertex-spec run specify "Test $i"; done
```

**Expected Behavior**: Automatic retry with backoff, or clear message about when to retry

**Success Criteria**: SC-005 - 90% of users can resolve issues without documentation

---

### Scenario 6: Performance

**Goal**: Verify performance targets (SC-007, SC-008)

**Test 6a: API Overhead**
```bash
time vertex-spec run specify "Test feature"
# Compare with direct Vertex AI API call
```

**Expected Result**: Overhead < 500ms

**Test 6b: CLI Response Time**
```bash
time vertex-spec config show
time vertex-spec models
```

**Expected Result**: Response time < 100ms for non-API commands

**Success Criteria**: SC-007, SC-008 - Performance targets met

---

### Scenario 7: Token Tracking

**Goal**: Verify token usage tracking (SC-011, SC-012)

**Steps**:
1. Run several Spec Kit commands
2. Check session summary: `vertex-spec config get session_summary`
3. Compare with GCP billing (if available)

**Expected Result**:
- Token counts tracked accurately
- Cost estimates within 10% of actual billing
- Session summary shows totals

**Success Criteria**: SC-011, SC-012 - Token tracking accurate, cost estimates within 10%

---

### Scenario 8: Cross-Platform

**Goal**: Verify cross-platform compatibility (SC-015)

**Test on**:
- Linux (Ubuntu/Debian)
- macOS
- Windows

**Steps** (same on all platforms):
1. Install adapter
2. Run `vertex-spec init`
3. Run `vertex-spec test`
4. Run `vertex-spec run specify "Test"`

**Expected Result**: Identical behavior on all platforms

**Success Criteria**: SC-015 - No platform-specific failures

---

### Scenario 9: Error Recovery

**Goal**: Verify automatic error recovery (SC-004)

**Test 9a: Network Interruption**
1. Start long-running command: `vertex-spec run implement tasks.md`
2. Interrupt with Ctrl+C
3. Verify checkpoint created
4. Resume: `vertex-spec run implement tasks.md --resume`

**Expected Result**: Operation resumes from checkpoint

**Test 9b: Transient Errors**
```bash
# Simulate network issues or rate limits
vertex-spec run specify "Test" --model claude-4-5-sonnet
```

**Expected Result**: Automatic retry with exponential backoff

**Success Criteria**: SC-004 - 95% automatic recovery from transient errors

---

### Scenario 10: Complete Workflow

**Goal**: End-to-end validation (SC-014)

**Steps**:
1. Initialize project: `vertex-spec init`
2. Create constitution: `vertex-spec run constitution`
3. Create spec: `vertex-spec run specify "User authentication system"`
4. Create plan: `vertex-spec run plan specs/001-user-auth/spec.md`
5. Create tasks: `vertex-spec run tasks specs/001-user-auth/plan.md`
6. Implement: `vertex-spec run implement specs/001-user-auth/tasks.md`

**Expected Result**:
- All commands succeed
- All artifacts created with proper structure
- Git branches and commits created correctly
- Generated code follows Spec Kit conventions

**Success Criteria**: SC-014 - Complete workflow executes successfully

---

## Validation Checklist

Use this checklist to verify all success criteria:

- [ ] SC-001: Setup completes in under 5 minutes
- [ ] SC-002: All authentication methods work (100% success)
- [ ] SC-003: All Spec Kit commands work (95% success)
- [ ] SC-004: Automatic error recovery (95% success)
- [ ] SC-005: Error messages helpful (90% user resolution)
- [ ] SC-006: Code coverage ≥ 80% (90%+ for critical paths)
- [ ] SC-007: API overhead < 500ms
- [ ] SC-008: CLI response < 100ms (non-API)
- [ ] SC-009: Handles 1000+ files without degradation
- [ ] SC-010: Model switching works without context loss
- [ ] SC-011: Token tracking accurate (within 1%)
- [ ] SC-012: Cost estimates accurate (within 10%)
- [ ] SC-013: Integration tests pass
- [ ] SC-014: E2E workflow works
- [ ] SC-015: Cross-platform compatibility
- [ ] SC-016: Security scans pass
- [ ] SC-017: No credentials in logs/errors
- [ ] SC-018: Documentation enables 90% self-service setup

## Troubleshooting

### Common Issues

**Issue**: "Authentication failed"
- **Fix**: Run `gcloud auth login` or set `GOOGLE_APPLICATION_CREDENTIALS`

**Issue**: "Model not available in region"
- **Fix**: Use `vertex-spec models` to see available models/regions

**Issue**: "Configuration file not found"
- **Fix**: Run `vertex-spec init` to create configuration

**Issue**: "Git repository not initialized"
- **Fix**: Run `git init` or let adapter initialize automatically

## Next Steps

After validating these scenarios:

1. Review generated artifacts for quality
2. Test with real project workflows
3. Verify performance under load
4. Test error scenarios thoroughly
5. Validate security (no credentials in logs)

## Support

For issues or questions:
- Check `docs/troubleshooting.md`
- Review error messages (they include suggested fixes)
- Enable debug mode: `vertex-spec --debug [command]`

