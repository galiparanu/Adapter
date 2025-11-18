# Changelog

All notable changes to the Vertex AI Spec Kit Adapter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of Vertex AI Spec Kit Adapter
- Support for Claude 4.5 Sonnet, Gemini 2.5 Pro, and Qwen Coder models
- Dual access pattern support (MaaS REST API and Native SDK)
- Multiple authentication methods (Service Account, User Credentials, ADC)
- Comprehensive error handling with retry logic and circuit breaker
- Full Spec Kit integration (constitution, specify, plan, tasks, implement commands)
- Interactive setup wizard
- Model registry with availability validation
- Token usage tracking and cost estimation
- Structured logging with debug mode
- Checkpoint/resume functionality for long-running operations
- Comprehensive documentation

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- Secure credential handling (no credentials in logs or version control)
- Input validation via Pydantic schemas
- Security scanning with bandit

## [0.1.0] - 2025-01-27

### Added
- Core functionality implementation
- CLI interface with Typer
- Configuration management
- Authentication manager
- Vertex AI client with model support
- Spec Kit bridge integration
- Error recovery mechanisms
- Comprehensive test suite

[Unreleased]: https://github.com/galiparanu/Adapter/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/galiparanu/Adapter/releases/tag/v0.1.0

