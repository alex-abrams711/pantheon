# Contributing to Pantheon

Thank you for your interest in contributing to Pantheon! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## Getting Started

### Prerequisites

- Python 3.9 or higher
- `uv` package manager
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/pantheon.git
   cd pantheon
   ```

2. **Create a virtual environment**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   uv pip install -e ".[dev]"
   ```

4. **Verify setup**
   ```bash
   pytest tests/
   mypy src/
   ruff check src/ tests/
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

Follow these guidelines:

- **Code Style**: Follow existing patterns and conventions
- **Type Hints**: Add type hints to all functions
- **Documentation**: Update docstrings and README as needed
- **Tests**: Add tests for new functionality

### 3. Run Quality Checks

Before committing, ensure all checks pass:

```bash
# Run tests
pytest tests/

# Check test coverage (should be >80%)
pytest tests/ --cov=src/pantheon --cov-report=term-missing

# Type checking
mypy src/

# Linting
ruff check src/ tests/

# Auto-fix linting issues
ruff check --fix src/ tests/
```

### 4. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: brief description

- Detailed point 1
- Detailed point 2
- Fixes #123"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Quality Standards

All contributions must meet these standards:

### Code Quality

- ✅ **Linting**: `ruff check src/ tests/` passes with 0 errors
- ✅ **Type Checking**: `mypy src/` passes with 0 errors
- ✅ **Tests**: All tests pass (`pytest tests/`)
- ✅ **Coverage**: >80% coverage on new code

### Code Style

- Use **type hints** on all function parameters and return values
- Follow **PEP 8** naming conventions
- Maximum **line length: 88 characters**
- Use **docstrings** for all public functions and classes
- Keep functions **focused and small**

### Testing

- Write **unit tests** for all new functions
- Write **integration tests** for workflows
- Use **fixtures** for test setup (see `tests/conftest.py`)
- Ensure tests are **isolated** and **repeatable**
- Mock external dependencies

### Documentation

- Update **README.md** if adding features
- Update **CHANGELOG.md** with your changes
- Add **docstrings** following Google or NumPy style
- Include **usage examples** where helpful

## Pull Request Process

### PR Checklist

Before submitting, ensure:

- [ ] All quality checks pass
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commits are clear and descriptive
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Code follows project style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All checks pass
```

## Project Structure

```
pantheon/
├── src/pantheon/          # Main package
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # CLI commands
│   ├── agents/            # Agent definitions
│   │   └── dev.md         # DEV agent
│   └── integrations/      # Integration modules
│       └── spec_kit.py    # Spec Kit integration
├── tests/                 # Test suite
│   ├── conftest.py        # Test fixtures
│   ├── test_spec_kit.py   # Unit tests
│   └── test_integration.py # Integration tests
├── docs/                  # Documentation
│   ├── research.md        # Research findings
│   └── design.md          # Design documentation
├── pyproject.toml         # Package configuration
└── README.md              # Project documentation
```

## Adding New Features

### Adding a New Agent

1. Create agent file in `src/pantheon/agents/`
2. Add YAML frontmatter with metadata
3. Document agent workflow and capabilities
4. Update `cli.py` to include in `pantheon list`
5. Add tests in `tests/`

### Adding a New Integration

1. Create module in `src/pantheon/integrations/`
2. Implement integration functions with type hints
3. Add CLI command if needed
4. Write comprehensive tests
5. Update README with integration guide

### Adding a New CLI Command

1. Add command function in `cli.py`
2. Use Click decorators for options
3. Add type hints
4. Write help text
5. Add tests for command functionality

## Testing Guidelines

### Unit Tests

Test individual functions in isolation:

```python
def test_verify_agents_installed(mock_claude_dir: Path):
    """Test when DEV agent is installed."""
    dev_file = mock_claude_dir / "agents" / "dev.md"
    dev_file.write_text("# DEV Agent")

    os.chdir(mock_claude_dir.parent)
    assert verify_agents_installed() is True
```

### Integration Tests

Test complete workflows:

```python
def test_full_integration_cycle(mock_spec_kit_project: Path):
    """Test init → integrate → verify → rollback cycle."""
    os.chdir(mock_spec_kit_project)

    # Setup
    # ... setup code ...

    # Integrate
    integrate_spec_kit()

    # Verify
    # ... verification ...

    # Rollback
    rollback_integration()
```

### Test Fixtures

Use fixtures for common setup:

```python
@pytest.fixture
def mock_spec_kit_project(mock_claude_dir: Path, mock_specify_dir: Path) -> Path:
    """Create a complete mock Spec Kit project."""
    # ... setup code ...
    return mock_claude_dir.parent
```

## Release Process

Maintainers follow this process for releases:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release commit
4. Tag release: `git tag -a v0.x.0 -m "Release v0.x.0"`
5. Push tag: `git push origin v0.x.0`
6. Build and publish: `uv build && uv publish`
7. Create GitHub release with notes

## Getting Help

- 📖 Read the [README](README.md)
- 🐛 Check [Issues](https://github.com/alex-abrams711/pantheon/issues)
- 💬 Start a [Discussion](https://github.com/alex-abrams711/pantheon/discussions)

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to Pantheon! 🎉
