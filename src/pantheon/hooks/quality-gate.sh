#!/usr/bin/env bash
# Quality Gate Hook
# Runs quality-report.sh and displays results to orchestrator
# Used at multiple workflow checkpoints: SubagentStop, PreCommit, PhaseTransition

set -euo pipefail

# Find project root (go up from .pantheon/hooks/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
QUALITY_REPORT_SCRIPT="$PROJECT_ROOT/.pantheon/quality-report.sh"

# Check if quality-report.sh exists
if [[ ! -f "$QUALITY_REPORT_SCRIPT" ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  QUALITY GATE: quality-report.sh not found"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Expected location: $QUALITY_REPORT_SCRIPT"
    echo ""
    echo "To generate quality report script:"
    echo "  1. Run: /pantheon:contextualize"
    echo "  2. This will analyze your project and generate both:"
    echo "     - .pantheon/quality-config.json"
    echo "     - .pantheon/quality-report.sh"
    echo ""
    echo "Continuing without quality report..."
    echo ""
    exit 0  # Don't block if script missing
fi

# Check if jq is available (needed for parsing JSON)
if ! command -v jq &> /dev/null; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  QUALITY GATE: jq not found"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "The quality gate requires jq to parse JSON output."
    echo ""
    echo "Install jq:"
    echo "  macOS:   brew install jq"
    echo "  Ubuntu:  sudo apt-get install jq"
    echo "  Other:   https://stedolan.github.io/jq/download/"
    echo ""
    echo "Continuing without quality report..."
    echo ""
    exit 0  # Don't block if jq missing
fi

# Run quality report script
if ! REPORT_JSON=$("$QUALITY_REPORT_SCRIPT" 2>&1); then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ QUALITY GATE: quality-report.sh failed"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "$REPORT_JSON"
    echo ""
    echo "Fix the script and try again."
    echo ""
    exit 0  # Don't block - let orchestrator decide
fi

# Parse JSON report
TIMESTAMP=$(echo "$REPORT_JSON" | jq -r '.timestamp // "unknown"')
READY_FOR_COMMIT=$(echo "$REPORT_JSON" | jq -r '.summary.ready_for_commit // false')

# Parse quality results
LINT_STATUS=$(echo "$REPORT_JSON" | jq -r '.quality.linting.status // "unknown"')
LINT_ERRORS=$(echo "$REPORT_JSON" | jq -r '.quality.linting.errors // "N/A"')
TYPE_STATUS=$(echo "$REPORT_JSON" | jq -r '.quality.type_checking.status // "unknown"')
TYPE_ERRORS=$(echo "$REPORT_JSON" | jq -r '.quality.type_checking.errors // "N/A"')
TEST_STATUS=$(echo "$REPORT_JSON" | jq -r '.quality.tests.status // "unknown"')
TEST_PASSED=$(echo "$REPORT_JSON" | jq -r '.quality.tests.passed // 0')
TEST_FAILED=$(echo "$REPORT_JSON" | jq -r '.quality.tests.failed // 0')
TEST_TOTAL=$(echo "$REPORT_JSON" | jq -r '.quality.tests.total // 0')
COV_STATUS=$(echo "$REPORT_JSON" | jq -r '.quality.coverage.status // "unknown"')
COV_PCT=$(echo "$REPORT_JSON" | jq -r '.quality.coverage.percentage // 0')
COV_THRESHOLD=$(echo "$REPORT_JSON" | jq -r '.quality.coverage.threshold // 0')

# Parse phase status
TASKS_COMPLETE=$(echo "$REPORT_JSON" | jq -r '.phase.tasks_complete // 0')
TASKS_INCOMPLETE=$(echo "$REPORT_JSON" | jq -r '.phase.tasks_incomplete // 0')
TASKS_TOTAL=$(echo "$REPORT_JSON" | jq -r '.phase.tasks_total // 0')
QA_VALIDATED=$(echo "$REPORT_JSON" | jq -r '.phase.qa_validated // false')
USER_VALIDATED=$(echo "$REPORT_JSON" | jq -r '.phase.user_validated // false')

# Helper function to format status with color/emoji
format_status() {
    local status=$1
    case $status in
        "pass")
            echo "✅ PASS"
            ;;
        "fail")
            echo "❌ FAIL"
            ;;
        "skipped")
            echo "⏭️  SKIP"
            ;;
        *)
            echo "❓ UNKNOWN"
            ;;
    esac
}

format_boolean() {
    local value=$1
    if [[ "$value" == "true" ]]; then
        echo "✅ Yes"
    else
        echo "❌ No"
    fi
}

# Display formatted report
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 QUALITY GATE REPORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏰ Generated: $TIMESTAMP"
echo ""
echo "Quality Checks:"
echo "───────────────"
echo "  Linting:       $(format_status "$LINT_STATUS") ${LINT_ERRORS:+($LINT_ERRORS errors)}"
echo "  Type Checking: $(format_status "$TYPE_STATUS") ${TYPE_ERRORS:+($TYPE_ERRORS errors)}"
echo "  Tests:         $(format_status "$TEST_STATUS") ($TEST_PASSED/$TEST_TOTAL passing)"
echo "  Coverage:      $(format_status "$COV_STATUS") ($COV_PCT% / $COV_THRESHOLD% required)"
echo ""
echo "Phase Status:"
echo "─────────────"
echo "  Tasks:         $TASKS_COMPLETE/$TASKS_TOTAL completed"
echo "  QA Validated:  $(format_boolean "$QA_VALIDATED")"
echo "  User Validated: $(format_boolean "$USER_VALIDATED")"
echo ""

# Summary guidance
if [[ "$READY_FOR_COMMIT" == "true" ]]; then
    echo "✅ READY FOR COMMIT"
    echo ""
    echo "All quality checks passed and validations complete."
    echo "You may proceed with creating a commit."
else
    echo "⚠️  NOT READY FOR COMMIT"
    echo ""
    echo "Blocking issues:"

    # List specific blocking issues
    [[ "$LINT_STATUS" == "fail" ]] && echo "  • Linting failures ($LINT_ERRORS errors)"
    [[ "$TYPE_STATUS" == "fail" ]] && echo "  • Type checking failures ($TYPE_ERRORS errors)"
    [[ "$TEST_STATUS" == "fail" ]] && echo "  • Test failures ($TEST_FAILED/$TEST_TOTAL tests failing)"
    [[ "$COV_STATUS" == "fail" ]] && echo "  • Coverage below threshold ($COV_PCT% < $COV_THRESHOLD%)"
    [[ "$QA_VALIDATED" == "false" ]] && echo "  • QA validation not completed"
    [[ "$USER_VALIDATED" == "false" ]] && echo "  • User approval not received"

    echo ""
    echo "Recommended actions:"
    echo "  1. Review the issues above"
    echo "  2. Fix quality failures if present"
    echo "  3. Complete QA validation if needed"
    echo "  4. Obtain user approval before committing"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Always exit 0 - this is informational
# The orchestrator decides what to do based on the report
exit 0
