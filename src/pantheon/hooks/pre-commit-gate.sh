#!/bin/bash
# PreCommit Hook - Quality gate before git commits
#
# This hook runs before git commits to ensure code quality.
# It validates:
#   1. Current phase has QA validated checkbox checked (if tasks.md exists)
#   2. Quality standards from .pantheon/quality-config.json pass
#
# Exit codes:
#   0 - Quality checks passed, allow commit
#   2 - Quality checks failed, block commit

set -euo pipefail

echo "🚦 Running pre-commit quality gates..."

# Check if tasks.md exists and validate QA and User validation checkboxes
TASKS_FILE="tasks.md"
if [ -f "$TASKS_FILE" ]; then
    # Find the current phase (first phase with unchecked "All tasks complete")
    CURRENT_PHASE=$(grep -B 1 "^- \[ \] All tasks complete" "$TASKS_FILE" 2>/dev/null | grep "^## Phase" | head -1 | sed 's/## Phase //' || echo "")

    if [ -n "$CURRENT_PHASE" ]; then
        # Extract phase section
        PHASE_SECTION=$(sed -n "/^## Phase $CURRENT_PHASE/,/^## Phase /p" "$TASKS_FILE" | head -n -1)
        if [ -z "$PHASE_SECTION" ]; then
            # Handle last phase (no next phase header)
            PHASE_SECTION=$(sed -n "/^## Phase $CURRENT_PHASE/,\$p" "$TASKS_FILE")
        fi

        # Check if QA validated
        if ! echo "$PHASE_SECTION" | grep -q "^- \[x\] QA validated"; then
            echo ""
            echo "❌ COMMIT BLOCKED"
            echo "   Phase $CURRENT_PHASE is missing QA validation"
            echo ""
            echo "   Required action:"
            echo "   1. Invoke QA agent with all completed tasks from Phase $CURRENT_PHASE"
            echo "   2. After QA returns PASS, update tasks.md:"
            echo "      - [x] QA validated"
            echo "   3. Present phase completion report to user and get approval"
            echo "   4. After user approves, update tasks.md:"
            echo "      - [x] User validated"
            echo "   5. Then retry commit"
            echo ""
            exit 2
        fi
        echo "✅ QA validation confirmed for Phase $CURRENT_PHASE"

        # Check if User validated
        if ! echo "$PHASE_SECTION" | grep -q "^- \[x\] User validated"; then
            echo ""
            echo "❌ COMMIT BLOCKED"
            echo "   Phase $CURRENT_PHASE is missing user approval"
            echo ""
            echo "   Required action:"
            echo "   1. Present phase completion report to user"
            echo "   2. Wait for user to type 'yes'"
            echo "   3. After user approves, update tasks.md:"
            echo "      - [x] User validated"
            echo "   4. Then retry commit"
            echo ""
            exit 2
        fi
        echo "✅ User validation confirmed for Phase $CURRENT_PHASE"
    fi
fi

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
