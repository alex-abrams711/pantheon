# Pantheon Test Scripts

This directory contains test scripts for validating Pantheon functionality.

## Available Scripts

### `test_spec_kit_integration.sh`

**Purpose:** Comprehensive integration test for Spec Kit v0.0.57+ compatibility

**What it tests:**
- Format detection (old vs new Spec Kit versions)
- Pantheon integration with Spec Kit commands
- Backup creation with correct filenames
- Integration directive insertion
- Quality hooks installation
- Rollback functionality
- Re-integration after rollback

**Usage:**

```bash
# Run with cleanup (removes test directory after)
./scripts/test_spec_kit_integration.sh --cleanup

# Run without cleanup (keeps test directory)
./scripts/test_spec_kit_integration.sh --keep

# Default (keeps test directory)
./scripts/test_spec_kit_integration.sh
```

**Expected Output:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tests Run:    30+
Tests Passed: 30+
Tests Failed: 0
Success Rate: 100%

╔════════════════════════════════════════════════════════════════╗
║                   ✓ ALL TESTS PASSED ✓                        ║
║                                                                ║
║  Pantheon Spec Kit v0.0.57+ compatibility verified!           ║
╚════════════════════════════════════════════════════════════════╝
```

**Test Coverage:**
- ✅ Pantheon installation
- ✅ Spec Kit v0.0.57+ format detection
- ✅ Format detection (Python functions)
- ✅ Integration command execution
- ✅ Integration directives added to correct files
- ✅ Backup creation with new format filenames
- ✅ Quality hooks installation
- ✅ Rollback removes directives
- ✅ Re-integration works after rollback
- ✅ Multiple backups created (idempotent)

**Requirements:**
- Python 3.9+
- `uv` package manager
- Internet connection (for Spec Kit installation)
- ~2 minutes runtime

**Troubleshooting:**

If tests fail:

1. Check Pantheon installation:
   ```bash
   which pantheon
   pantheon --version
   ```

2. Review test output for specific failures

3. Inspect test directory (if kept):
   ```bash
   ls -la /tmp/pantheon-integration-test-*/
   ```

4. Check for conflicting installations:
   ```bash
   uv tool list | grep pantheon
   ```

**When to Run:**

- Before committing changes to `spec_kit.py`
- After modifying integration logic
- Before releasing new versions
- When Spec Kit updates to new versions
- As part of CI/CD pipeline (future)

## Creating New Test Scripts

When adding new test scripts to this directory:

1. **Make executable:**
   ```bash
   chmod +x scripts/your_script.sh
   ```

2. **Add shebang:**
   ```bash
   #!/bin/bash
   ```

3. **Include header documentation:**
   ```bash
   # Script Name
   # Purpose: What this script tests
   # Usage: How to run it
   ```

4. **Use consistent output:**
   - Green ✓ for passing tests
   - Red ✗ for failing tests
   - Yellow ⚠ for warnings/skips

5. **Exit codes:**
   - `0` for success
   - `1` for failure
   - Non-zero for errors

6. **Document in this README**

## Future Scripts

Potential future test scripts:

- `test_quality_discovery.sh` - Test quality command discovery for different project types
- `test_hooks.sh` - Test quality gate hooks (SubagentStop, PreCommit, PhaseGate)
- `test_cli.sh` - Test CLI commands (init, integrate, rollback, list)
- `test_backward_compat.sh` - Test with Spec Kit pre-v0.0.57 (old format)
- `test_multiplatform.sh` - Test on Linux, macOS, Windows

## CI/CD Integration

To integrate these scripts into CI/CD:

**GitHub Actions example:**

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test-spec-kit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install uv
        run: pip install uv
      - name: Run Spec Kit integration test
        run: ./scripts/test_spec_kit_integration.sh --cleanup
```

## Contributing

When modifying test scripts:

1. Test locally before committing
2. Update this README if adding new scripts
3. Ensure scripts are idempotent (can run multiple times)
4. Add cleanup options for CI/CD environments
5. Use meaningful exit codes
6. Provide clear error messages
