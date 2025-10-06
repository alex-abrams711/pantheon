#!/bin/bash
# Phase Gate Hook - Validates quality on phase transitions
#
# This hook runs on UserPromptSubmit events to detect phase approvals.
# When user approves a phase transition (keywords: yes, proceed, phase N),
# it validates quality before allowing the transition.
#
# Exit codes:
#   0 - Not an approval or validation passed
#   2 - Approval detected but validation failed

set -euo pipefail

# Read user message from stdin
USER_MESSAGE=$(cat)

# Check if message contains approval keywords
if ! echo "$USER_MESSAGE" | grep -qiE '(^yes$|^proceed|phase [0-9]+)'; then
    # Not an approval message, allow to proceed
    exit 0
fi

echo "🚦 Phase approval detected - running quality validation..."

# Check if quality config exists
CONFIG_FILE=".pantheon/quality-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️  Warning: Quality config not found at $CONFIG_FILE"
    echo "Allowing phase transition (no quality gates configured)"
    exit 0
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

# Run tests
if [ -n "$TEST_CMD" ]; then
    echo "Running tests: $TEST_CMD"
    if eval "$TEST_CMD" > /tmp/phase-gate-test.log 2>&1; then
        echo "✅ Tests passed"
    else
        echo "❌ Tests failed"
        cat /tmp/phase-gate-test.log | head -20
        FAILURES=$((FAILURES + 1))
    fi
fi

# Run linting
if [ -n "$LINT_CMD" ]; then
    echo "Running linter: $LINT_CMD"
    if eval "$LINT_CMD" > /tmp/phase-gate-lint.log 2>&1; then
        echo "✅ Linting passed"
    else
        echo "❌ Linting failed"
        cat /tmp/phase-gate-lint.log | head -20
        FAILURES=$((FAILURES + 1))
    fi
fi

# Run type checking
if [ -n "$TYPE_CMD" ]; then
    echo "Running type checker: $TYPE_CMD"
    if eval "$TYPE_CMD" > /tmp/phase-gate-type.log 2>&1; then
        echo "✅ Type checking passed"
    else
        echo "❌ Type checking failed"
        cat /tmp/phase-gate-type.log | head -20
        FAILURES=$((FAILURES + 1))
    fi
fi

# Final verdict
if [ $FAILURES -gt 0 ]; then
    echo ""
    echo "❌ PHASE GATE BLOCKED"
    echo "   $FAILURES quality check(s) failed"
    echo "   Cannot proceed to next phase until issues are resolved"
    echo ""
    echo "   Fix the issues above and try again"
    exit 2  # Block phase transition
else
    echo ""
    echo "✅ PHASE GATE PASSED"
    echo "   All quality checks passed - proceeding to next phase"
    exit 0  # Allow phase transition
fi
