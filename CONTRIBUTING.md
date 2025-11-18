# Contributing to Vertex AI Spec Kit Adapter

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- GCP account with Vertex AI API enabled (for testing)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/vertex-spec-adapter.git
   cd vertex-spec-adapter
   ```

2. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

4. **Run Tests**
   ```bash
   pytest
   ```

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions/updates

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

**Examples:**
```
feat(auth): Add service account authentication support

fix(client): Handle rate limit errors correctly

docs(readme): Update installation instructions
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following project style
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Quality Checks**
   ```bash
   # Run linters
   ruff check .
   ruff format .

   # Run type checker
   mypy vertex_spec_adapter

   # Run tests
   pytest

   # Check coverage
   pytest --cov=vertex_spec_adapter --cov-report=term --cov-report=html
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat(scope): Description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub.

6. **PR Requirements**
   - All tests pass
   - Code coverage maintained (80%+ overall, 90%+ critical paths)
   - Documentation updated
   - No linter errors
   - PR description explains changes

## Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use type hints for all functions
- Maximum line length: 100 characters
- Use `ruff` for formatting and linting

### Code Formatting

```bash
# Format code
ruff format .

# Check formatting
ruff format --check .

# Lint code
ruff check .
```

### Type Checking

```bash
# Run type checker
mypy vertex_spec_adapter
```

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is invalid
    """
    pass
```

## Testing

### Test Structure

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- E2E tests: `tests/e2e/`

### Writing Tests

- Follow AAA pattern (Arrange, Act, Assert)
- Use descriptive test names
- Mock external dependencies
- Test both success and failure cases

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_client.py

# Run with coverage
pytest --cov=vertex_spec_adapter --cov-report=html

# Run specific test
pytest tests/unit/test_client.py::TestVertexAIClient::test_generate
```

### Coverage Requirements

- Overall coverage: 80%+
- Critical paths: 90%+
- New code should maintain or improve coverage

## Documentation

### Documentation Structure

- `README.md` - Project overview and quick start
- `docs/getting-started.md` - Detailed setup guide
- `docs/configuration.md` - Configuration reference
- `docs/authentication.md` - Authentication guide
- `docs/troubleshooting.md` - Common issues and solutions

### Updating Documentation

- Update relevant docs when adding features
- Include code examples
- Keep examples up-to-date
- Test all code examples

## Project Structure

```
vertex_spec_adapter/
├── cli/              # CLI commands and interface
├── core/             # Core functionality
├── speckit/          # Spec Kit integration
├── utils/            # Utilities
└── schemas/          # Pydantic schemas

tests/
├── unit/             # Unit tests
├── integration/      # Integration tests
└── e2e/              # End-to-end tests

docs/                 # Documentation
examples/             # Example configurations
```

## Adding New Features

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement Feature**
   - Write code following style guide
   - Add comprehensive tests
   - Update documentation

3. **Test Thoroughly**
   ```bash
   pytest
   ruff check .
   mypy vertex_spec_adapter
   ```

4. **Update Documentation**
   - Update relevant docs
   - Add examples if applicable

5. **Create Pull Request**
   - Clear description
   - Link to related issues
   - Request review

## Reporting Bugs

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. ...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11]
- Adapter version: [e.g., 0.1.0]

**Additional Context**
Any other relevant information
```

## Requesting Features

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Any other relevant information
```

## Questions?

- Check [Documentation](docs/)
- Review [Troubleshooting Guide](docs/troubleshooting.md)
- Open an issue for discussion

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

