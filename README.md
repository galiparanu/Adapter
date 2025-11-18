# Vertex AI Spec Kit Adapter

A production-ready bridge tool that enables Spec Kit to work seamlessly with Google Vertex AI models.

## Overview

The Vertex AI Spec Kit Adapter provides a unified interface for using Spec Kit with Google Cloud Platform's Vertex AI Model Garden. It supports both Model-as-a-Service (MaaS) REST API and Native SDK access patterns, enabling you to use Claude, Gemini, and Qwen models through your existing GCP credits.

## Features

- **Multiple Model Support**: Claude 4.5 Sonnet, Gemini 2.5 Pro, Qwen Coder
- **Dual Access Patterns**: Both MaaS REST API and Native SDK
- **Enterprise Ready**: Service account authentication, audit logging, cost tracking
- **Full Spec Kit Integration**: All five commands (constitution, specify, plan, tasks, implement)
- **Developer Friendly**: 5-minute setup, interactive wizard, helpful error messages
- **Production Ready**: Comprehensive testing, error recovery, performance optimization

## Quick Start

### Prerequisites

- Python 3.9+
- Google Cloud Platform account with Vertex AI API enabled
- GCP credentials (service account, user credentials, or ADC)

### Installation

```bash
# From source (development)
pip install -e ".[dev]"

# Or install from PyPI (when published)
pip install vertex-spec-adapter
```

### Setup

```bash
# Initialize the adapter
vertex-spec init --interactive

# Test connection
vertex-spec test

# List available models
vertex-spec models
```

### Usage

```bash
# Create a feature specification
vertex-spec run specify "Add user authentication feature"

# Generate implementation plan
vertex-spec run plan specs/001-user-auth/spec.md

# Generate tasks
vertex-spec run tasks specs/001-user-auth/plan.md

# Implement the feature
vertex-spec run implement specs/001-user-auth/tasks.md
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Configuration](docs/configuration.md)
- [Authentication](docs/authentication.md)
- [Troubleshooting](docs/troubleshooting.md)

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd vertex-spec-adapter

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Project Structure

```
vertex_spec_adapter/
├── cli/              # CLI commands and interface
├── core/             # Core functionality (client, auth, config)
├── speckit/          # Spec Kit integration
├── utils/            # Utilities (logging, retry, metrics)
└── schemas/          # Pydantic schemas

tests/
├── unit/             # Unit tests
├── integration/      # Integration tests
└── e2e/              # End-to-end tests
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License

## Support

For issues and questions:
- Check [Troubleshooting Guide](docs/troubleshooting.md)
- Review error messages (they include suggested fixes)
- Enable debug mode: `vertex-spec --debug [command]`

