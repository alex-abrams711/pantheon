# Pantheon Testing Guide

## Quick Test

Verify Spec Kit v0.0.57+ compatibility:

```bash
./scripts/test_spec_kit_integration.sh --cleanup
```

## Integration Tests

**Location:** `scripts/test_spec_kit_integration.sh`

**What it tests:**
- Format detection (old/new Spec Kit versions)
- Integration with Spec Kit commands
- Backup creation and restoration
- Rollback functionality  
- Quality hooks installation

**Usage:**
```bash
# Run with cleanup
./scripts/test_spec_kit_integration.sh --cleanup

# Run and keep test directory
./scripts/test_spec_kit_integration.sh --keep
```

## Unit Tests

```bash
# Run all tests
pytest tests/

# With coverage
pytest tests/ --cov=src/pantheon --cov-report=term-missing
```

## Quality Checks

```bash
# Linting
ruff check src/ tests/

# Type checking
mypy src/ --strict
```

## Manual Testing

See `scripts/README.md` for detailed manual testing procedures.

## Test Checklist

Before releasing:

- [ ] Integration test passes: `./scripts/test_spec_kit_integration.sh --cleanup`
- [ ] All unit tests pass: `pytest tests/`
- [ ] Coverage ≥92%
- [ ] Type checking passes: `mypy src/ --strict`
- [ ] Linting passes: `ruff check src/ tests/`
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
