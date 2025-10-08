#!/bin/bash
# Phase Transition Gate Hook - Validates phase transitions
#
# This hook runs on PreToolUse Task events before DEV agents are invoked.
# When orchestrator attempts to start a new phase, it validates:
#   1. Previous phase has "QA validated" checkbox checked
#   2. Previous phase has "User validated" checkbox checked
#
# Exit codes:
#   0 - Same phase or validation passed, allow task
#   2 - Phase transition blocked due to missing validation

set -euo pipefail

# Read task invocation context from stdin
TASK_CONTEXT=$(cat)

# Extract task ID from context (e.g., "T011", "T002")
TASK_ID=$(echo "$TASK_CONTEXT" | grep -oP 'T\d+' | head -1)

if [ -z "$TASK_ID" ]; then
    # No task ID found, allow to proceed (might be non-task invocation)
    exit 0
fi

# Check if tasks.md exists
TASKS_FILE="tasks.md"
if [ ! -f "$TASKS_FILE" ]; then
    # No tasks.md, allow to proceed
    exit 0
fi

# Find which phase this task belongs to
TASK_PHASE=$(grep -B 10 "^\*\*$TASK_ID\*\*" "$TASKS_FILE" 2>/dev/null | grep "^## Phase" | tail -1 | sed 's/## Phase //' || echo "")

if [ -z "$TASK_PHASE" ]; then
    # Could not determine task phase, allow to proceed
    exit 0
fi

# Find the current phase (first phase with unchecked "All tasks complete")
CURRENT_PHASE=$(grep -B 1 "^- \[ \] All tasks complete" "$TASKS_FILE" 2>/dev/null | grep "^## Phase" | head -1 | sed 's/## Phase //' || echo "")

if [ -z "$CURRENT_PHASE" ]; then
    # All phases complete or cannot determine, allow to proceed
    exit 0
fi

# Check if we're transitioning to a new phase
if [ "$TASK_PHASE" = "$CURRENT_PHASE" ]; then
    # Same phase, allow to proceed
    exit 0
fi

# We're transitioning to a new phase - validate previous phase checkboxes
echo "🚦 Phase transition detected: $CURRENT_PHASE → $TASK_PHASE"
echo "📋 Validating Phase $CURRENT_PHASE completion..."

# Extract current phase section
PHASE_SECTION=$(sed -n "/^## Phase $CURRENT_PHASE/,/^## Phase /p" "$TASKS_FILE" | head -n -1)
if [ -z "$PHASE_SECTION" ]; then
    # Handle last phase (no next phase header)
    PHASE_SECTION=$(sed -n "/^## Phase $CURRENT_PHASE/,\$p" "$TASKS_FILE")
fi

# Check if QA validated
if echo "$PHASE_SECTION" | grep -q "^- \[x\] QA validated"; then
    echo "✅ QA validated"
else
    echo ""
    echo "❌ PHASE TRANSITION BLOCKED"
    echo "   Cannot start Phase $TASK_PHASE (Task $TASK_ID)"
    echo "   Phase $CURRENT_PHASE is missing QA validation"
    echo ""
    echo "   Required action:"
    echo "   1. Invoke QA agent with all completed tasks from Phase $CURRENT_PHASE"
    echo "   2. After QA returns PASS, update tasks.md:"
    echo "      - [x] QA validated"
    echo "   3. Then retry executing Task $TASK_ID"
    echo ""
    exit 2
fi

# Check if User validated
if echo "$PHASE_SECTION" | grep -q "^- \[x\] User validated"; then
    echo "✅ User validated"
else
    echo ""
    echo "❌ PHASE TRANSITION BLOCKED"
    echo "   Cannot start Phase $TASK_PHASE (Task $TASK_ID)"
    echo "   Phase $CURRENT_PHASE is missing user approval"
    echo ""
    echo "   Required action:"
    echo "   1. Present phase completion report to user"
    echo "   2. After user types 'yes', update tasks.md:"
    echo "      - [x] User validated"
    echo "   3. Then retry executing Task $TASK_ID"
    echo ""
    exit 2
fi

# All validations passed
echo "✅ Phase $CURRENT_PHASE validated - allowing transition to Phase $TASK_PHASE"
exit 0
