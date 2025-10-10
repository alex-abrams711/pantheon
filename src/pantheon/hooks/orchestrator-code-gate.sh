#!/usr/bin/env bash
# Orchestrator Code Gate Hook
# Prevents orchestrator from editing source code (separation of concerns)
# Orchestrator coordinates; DEV agents implement.

set -euo pipefail

# Get the file path from tool call (Claude Code provides this via environment or stdin)
# This may need adjustment based on how Claude Code actually passes file paths to hooks
FILE_PATH="${CLAUDE_TOOL_FILE_PATH:-${1:-}}"

if [[ -z "$FILE_PATH" ]]; then
    # No file path provided - allow by default
    exit 0
fi

# Allowed patterns (documentation files orchestrator CAN edit)
ALLOWED_PATTERNS=(
    "tasks.md"
    "README.md"
    "CHANGELOG.md"
    "docs/"
    ".claude/"
    "*.md"
)

# Check if file matches allowed patterns
for pattern in "${ALLOWED_PATTERNS[@]}"; do
    if [[ "$FILE_PATH" == *"$pattern"* ]]; then
        exit 0  # Allow edit
    fi
done

# If we get here, file is not in allowed list - block it
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "❌ ORCHESTRATOR CODE GATE BLOCKED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "File: $FILE_PATH"
echo ""
echo "As orchestrator, you coordinate work but don't implement."
echo "Source code and tests must be edited by DEV agents."
echo ""
echo "If QA found issues:"
echo "  1. Parse the QA report"
echo "  2. Prepare DEV rework context with QA findings"
echo "  3. Re-invoke DEV agent with: Use Task tool, subagent_type: 'dev'"
echo ""
echo "Allowed files: tasks.md, README.md, CHANGELOG.md, docs/, .claude/"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

exit 2  # Block edit
