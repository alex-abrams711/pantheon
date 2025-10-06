#!/bin/bash
# SubagentStop Hook - Validates DEV/QA agent work before completion
#
# This hook runs when sub-agents (DEV/QA) complete their work.
# It validates quality standards from .pantheon/quality-config.json
#
# Exit codes:
#   0 - Validation passed, allow agent to complete
#   2 - Validation failed, block agent completion

set -euo pipefail

# Check if quality config exists
CONFIG_FILE=".pantheon/quality-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️  Warning: Quality config not found at $CONFIG_FILE"
    echo "Run 'pantheon integrate' to set up quality gates"
    exit 0  # Don't block if config missing
fi

# Parse quality config using Python (reliable JSON parsing)
# Extract commands and thresholds
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

echo "🔍 Validating agent work against quality standards..."

# Run tests if test command exists
if [ -n "$TEST_CMD" ]; then
    echo "Running tests: $TEST_CMD"
    if eval "$TEST_CMD" > /tmp/test-output.log 2>&1; then
        echo "✅ Tests passed"
    else
        echo "❌ Tests failed"
        cat /tmp/test-output.log
        FAILURES=$((FAILURES + 1))
    fi
else
    echo "⚠️  No test command configured, skipping tests"
fi

# Run linting if lint command exists
if [ -n "$LINT_CMD" ]; then
    echo "Running linter: $LINT_CMD"
    if eval "$LINT_CMD" > /tmp/lint-output.log 2>&1; then
        echo "✅ Linting passed"
    else
        echo "❌ Linting failed"
        cat /tmp/lint-output.log
        FAILURES=$((FAILURES + 1))
    fi
else
    echo "⚠️  No lint command configured, skipping linting"
fi

# Run type checking if type command exists
if [ -n "$TYPE_CMD" ]; then
    echo "Running type checker: $TYPE_CMD"
    if eval "$TYPE_CMD" > /tmp/type-output.log 2>&1; then
        echo "✅ Type checking passed"
    else
        echo "❌ Type checking failed"
        cat /tmp/type-output.log
        FAILURES=$((FAILURES + 1))
    fi
else
    echo "⚠️  No type check command configured, skipping type checking"
fi

# Check for code smells (basic checks)
echo "Checking for code smells..."
SMELLS=0

# Check for console.log/print in non-test files
if git diff --cached --name-only | grep -E '\.(js|ts|py)$' | grep -v test | \
   xargs grep -l -E '(console\.log|print\()' 2>/dev/null; then
    echo "⚠️  Found console.log/print statements in non-test files"
    SMELLS=$((SMELLS + 1))
fi

# Check for TODO comments
if git diff --cached --name-only | xargs grep -l 'TODO' 2>/dev/null; then
    echo "⚠️  Found TODO comments in staged files"
    SMELLS=$((SMELLS + 1))
fi

if [ $SMELLS -eq 0 ]; then
    echo "✅ No code smells detected"
fi

# Final verdict
if [ $FAILURES -gt 0 ]; then
    echo ""
    echo "❌ SubagentStop validation FAILED"
    echo "   $FAILURES quality check(s) failed"
    echo "   Fix the issues above before proceeding"
    exit 2  # Block agent completion
else
    echo ""
    echo "✅ SubagentStop validation PASSED"
    echo "   All quality checks passed"
    exit 0  # Allow agent to complete
fi
