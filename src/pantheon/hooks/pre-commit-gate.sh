#!/bin/bash
# PreCommit Hook - Quality gate before git commits
#
# This hook runs before git commits to ensure code quality.
# It validates against quality standards from .pantheon/quality-config.json
#
# Exit codes:
#   0 - Quality checks passed, allow commit
#   2 - Quality checks failed, block commit

set -euo pipefail

# Check if quality config exists
CONFIG_FILE=".pantheon/quality-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️  Warning: Quality config not found at $CONFIG_FILE"
    echo "Run 'pantheon integrate' to set up quality gates"
    exit 0  # Don't block if config missing
fi

# Parse quality config
COMMANDS=$(python3 -c "
import json
import sys
try:
    with open('$CONFIG_FILE') as f:
        config = json.load(f)
    cmds = config.get('commands', {})
    print(f\"{cmds.get('test', '')}|{cmds.get('lint', '')}|{cmds.get('type_check', '')}\")
except Exception as e:
    print('||')
    sys.exit(0)
")

IFS='|' read -r TEST_CMD LINT_CMD TYPE_CMD <<< "$COMMANDS"

# Track failures
FAILURES=0

echo "🚦 Running pre-commit quality gates..."

# Run tests
if [ -n "$TEST_CMD" ]; then
    echo "Running tests: $TEST_CMD"
    if eval "$TEST_CMD" 2>&1 | tee /tmp/pre-commit-test.log; then
        echo "✅ Tests passed"
    else
        echo "❌ Tests failed - commit blocked"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo "⚠️  No test command configured"
fi

# Run linting
if [ -n "$LINT_CMD" ]; then
    echo "Running linter: $LINT_CMD"
    if eval "$LINT_CMD" 2>&1 | tee /tmp/pre-commit-lint.log; then
        echo "✅ Linting passed"
    else
        echo "❌ Linting failed - commit blocked"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo "⚠️  No lint command configured"
fi

# Run type checking
if [ -n "$TYPE_CMD" ]; then
    echo "Running type checker: $TYPE_CMD"
    if eval "$TYPE_CMD" 2>&1 | tee /tmp/pre-commit-type.log; then
        echo "✅ Type checking passed"
    else
        echo "❌ Type checking failed - commit blocked"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo "⚠️  No type check command configured"
fi

# Final verdict
if [ $FAILURES -gt 0 ]; then
    echo ""
    echo "❌ PRE-COMMIT BLOCKED"
    echo "   $FAILURES quality check(s) failed"
    echo "   Fix the issues above before committing"
    echo ""
    echo "   To bypass this hook (not recommended):"
    echo "   git commit --no-verify"
    exit 2  # Block commit
else
    echo ""
    echo "✅ PRE-COMMIT PASSED"
    echo "   All quality checks passed - proceeding with commit"
    exit 0  # Allow commit
fi
