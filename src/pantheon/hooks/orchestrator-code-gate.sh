#!/bin/bash
# Orchestrator Code Gate Hook - Prevents orchestrator from editing source code
#
# This hook runs on PreToolUse Write/Edit to enforce separation of concerns:
# - Orchestrator: Coordinates workflow, edits documentation only
# - DEV agents: Write ALL source code and tests
#
# Rationale: If QA finds issues, orchestrator must re-invoke DEV agents
# rather than fixing code directly. This ensures proper workflow adherence.
#
# Exit codes:
#   0 - Edit allowed (documentation files)
#   2 - Edit blocked (source code files)

set -euo pipefail

# Read tool invocation context from stdin
TOOL_CONTEXT=$(cat)

# Extract file path from Write/Edit tool invocation
# Format: "file_path": "/path/to/file"
FILE_PATH=$(echo "$TOOL_CONTEXT" | grep -oP '"file_path"\s*:\s*"\K[^"]+' || echo "")

if [ -z "$FILE_PATH" ]; then
    # Cannot determine file path, allow (fail open for safety)
    exit 0
fi

# Normalize path (remove leading ./)
FILE_PATH="${FILE_PATH#./}"

echo "🚦 Orchestrator Code Gate checking: $FILE_PATH"

# Allow documentation and workflow files
ALLOWED_PATTERNS=(
    "^tasks\.md$"
    "^README\.md$"
    "^CHANGELOG\.md$"
    "^docs/"
    "^\.claude/"
    "^\.pantheon/quality-config\.json$"
    "^\.integration-backup-"
    "^specs/"
)

for pattern in "${ALLOWED_PATTERNS[@]}"; do
    if [[ "$FILE_PATH" =~ $pattern ]]; then
        echo "✅ Documentation/workflow file - edit allowed"
        exit 0
    fi
done

# Block all source code, tests, and configuration files
echo ""
echo "❌ ORCHESTRATOR CODE GATE BLOCKED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   You attempted to edit: $FILE_PATH"
echo ""
echo "   ⚠️  As the orchestrator, you must NEVER edit source code directly."
echo ""
echo "   Your role:"
echo "   ✓ Coordinate workflow (invoke DEV/QA agents)"
echo "   ✓ Update tasks.md checkboxes"
echo "   ✓ Create commits after user approval"
echo "   ✗ Write or fix source code"
echo ""
echo "   Required action:"
echo ""
echo "   If QA found issues:"
echo "     1. Parse QA report for specific issues and recommendations"
echo "     2. Prepare DEV rework context package with QA findings"
echo "     3. Re-invoke DEV agent using Task tool"
echo "     4. Wait for DEV to fix issues"
echo "     5. Re-invoke QA agent to validate fixes"
echo ""
echo "   If implementing new work:"
echo "     1. Prepare DEV context package from tasks.md"
echo "     2. Invoke DEV agent using Task tool"
echo "     3. Wait for DEV completion"
echo "     4. Invoke QA agent to validate"
echo ""
echo "   Remember: DEV agents handle ALL code changes. You coordinate."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
exit 2  # Block the edit
