# Workflow Analysis (Based on CLAUDE.md)

  The Required Workflow

  PHASE N EXECUTION:
  ├─ 1. Execute DEV agents for tasks (T001-T010)
  │  └─ Multiple DEV agents can run in parallel [P]
  │
  ├─ 2. QA VALIDATION (MANDATORY) ◄── I SKIPPED THIS
  │  ├─ Invoke QA agent with ALL completed task IDs
  │  ├─ QA runs: tests, coverage, lint, type-check, manual testing
  │  └─ QA returns: PASS or FAIL
  │
  ├─ 3. Process QA Report
  │  ├─ If FAIL: Fix with DEV agents → Re-run QA (max 2-3 cycles)
  │  └─ If PASS: Create commits with quality metrics
  │
  ├─ 4. PHASE GATE CHECKPOINT ◄── I SKIPPED THIS
  │  ├─ Present phase completion report with quality metrics
  │  ├─ WAIT for user approval
  │  └─ User types "yes" to proceed
  │
  └─ 5. Only after approval → PHASE N+1

  Where I Failed

  1. Missing QA validation: Went from step 1 → step 5 (skipped 2, 3, 4)
  2. Missing phase gate: Never waited for approval before Phase 3.2

  Proposed Hooks to Enforce Workflow

  Hook 1: Block New Phase Without QA Validation

  {
    "name": "enforce-qa-before-phase-transition",
    "description": "Blocks starting new phase tasks without QA validation of previous phase",
    "event": "before:tool:use",
    "toolPattern": "Task",
    "script": ".claude/hooks/check-qa-validation.sh",
    "blocking": true
  }

  Script: .claude/hooks/check-qa-validation.sh
  #!/bin/bash
  # Check if we're about to execute a task from a new phase
  # without QA validation of the previous phase

  TASK_PROMPT="$1"

  # Extract phase from task description (e.g., "T011" is Phase 3.2)
  TASK_ID=$(echo "$TASK_PROMPT" | grep -oP 'T\d+' | head -1)

  # Check if this is a new phase
  CURRENT_PHASE=$(cat .claude/state/current-phase 2>/dev/null || echo "3.1")
  TASK_PHASE=$(get_phase_from_task "$TASK_ID")

  if [ "$TASK_PHASE" != "$CURRENT_PHASE" ]; then
    # Check if QA was run for current phase
    QA_FILE=".claude/state/qa-validated-$CURRENT_PHASE"

    if [ ! -f "$QA_FILE" ]; then
      echo "❌ BLOCKED: Cannot start Phase $TASK_PHASE without QA validation of Phase $CURRENT_PHASE"
      echo ""
      echo "Required action: Run QA agent for Phase $CURRENT_PHASE tasks first"
      echo "Example: Invoke QA agent with tasks from Phase $CURRENT_PHASE"
      exit 1
    fi
  fi

  Hook 2: Require Phase Approval Before Transition

  {
    "name": "require-phase-approval",
    "description": "Blocks phase transition without explicit user approval",
    "event": "before:tool:use",
    "toolPattern": "Task",
    "script": ".claude/hooks/check-phase-approval.sh",
    "blocking": true
  }

  Script: .claude/hooks/check-phase-approval.sh
  #!/bin/bash
  TASK_PROMPT="$1"
  TASK_ID=$(echo "$TASK_PROMPT" | grep -oP 'T\d+' | head -1)

  CURRENT_PHASE=$(cat .claude/state/current-phase 2>/dev/null || echo "3.1")
  TASK_PHASE=$(get_phase_from_task "$TASK_ID")

  if [ "$TASK_PHASE" != "$CURRENT_PHASE" ]; then
    APPROVAL_FILE=".claude/state/phase-approved-$CURRENT_PHASE"

    if [ ! -f "$APPROVAL_FILE" ]; then
      echo "❌ BLOCKED: Cannot start Phase $TASK_PHASE without user approval for Phase $CURRENT_PHASE"
      echo ""
      echo "Required action:"
      echo "1. Present phase completion report to user"
      echo "2. Wait for user to type 'yes' to approve"
      echo "3. Only then proceed to Phase $TASK_PHASE"
      exit 1
    fi
  fi

  Hook 3: Remind to Run QA After DEV Agents

  {
    "name": "remind-qa-after-dev",
    "description": "Reminds to run QA agent after DEV agents complete",
    "event": "after:tool:use",
    "toolPattern": "Task",
    "script": ".claude/hooks/remind-qa.sh",
    "blocking": false
  }

  Script: .claude/hooks/remind-qa.sh
  #!/bin/bash
  TOOL_OUTPUT="$1"

  # Check if this was a DEV agent completion
  if echo "$TOOL_OUTPUT" | grep -q "subagent_type.*dev"; then
    # Increment DEV agent counter
    DEV_COUNT=$(cat .claude/state/dev-count 2>/dev/null || echo "0")
    DEV_COUNT=$((DEV_COUNT + 1))
    echo "$DEV_COUNT" > .claude/state/dev-count

    # Get expected DEV agents for current phase
    CURRENT_PHASE=$(cat .claude/state/current-phase 2>/dev/null || echo "3.1")
    EXPECTED=$(get_dev_agents_for_phase "$CURRENT_PHASE")

    if [ "$DEV_COUNT" -eq "$EXPECTED" ]; then
      echo ""
      echo "⚠️  REMINDER: All DEV agents for Phase $CURRENT_PHASE complete"
      echo "📋 REQUIRED NEXT STEP: Run QA agent before proceeding"
      echo ""
      echo "Invoke QA agent with:"
      echo "  - All completed task IDs: $(get_phase_tasks "$CURRENT_PHASE")"
      echo "  - Quality standards from plan.md"
      echo "  - Definition of Done checklist"
      echo ""
    fi
  fi

  Hook 4: Block Commits Without QA PASS

  {
    "name": "block-commits-without-qa-pass",
    "description": "Prevents creating commits without QA validation passing",
    "event": "before:tool:use",
    "toolPattern": "Bash",
    "script": ".claude/hooks/check-commit-allowed.sh",
    "blocking": true
  }

  Script: .claude/hooks/check-commit-allowed.sh
  #!/bin/bash
  BASH_COMMAND="$1"

  # Check if this is a git commit command
  if echo "$BASH_COMMAND" | grep -q "git commit"; then
    CURRENT_PHASE=$(cat .claude/state/current-phase 2>/dev/null || echo "3.1")
    QA_STATUS=$(cat ".claude/state/qa-status-$CURRENT_PHASE" 2>/dev/null)

    if [ "$QA_STATUS" != "PASS" ]; then
      echo "❌ BLOCKED: Cannot create commits without QA PASS status"
      echo ""
      echo "Current QA status: ${QA_STATUS:-NOT RUN}"
      echo ""
      echo "Required action: Run QA agent and get PASS status first"
      exit 1
    fi
  fi

  Hook 5: State Management for Phase Tracking

  {
    "name": "track-phase-state",
    "description": "Updates phase state files when QA completes or approval given",
    "event": "after:tool:use",
    "toolPattern": "Task",
    "script": ".claude/hooks/update-phase-state.sh",
    "blocking": false
  }

  Script: .claude/hooks/update-phase-state.sh
  #!/bin/bash
  TOOL_OUTPUT="$1"

  # If QA agent completed
  if echo "$TOOL_OUTPUT" | grep -q "subagent_type.*qa"; then
    CURRENT_PHASE=$(cat .claude/state/current-phase 2>/dev/null || echo "3.1")

    # Check if QA PASSED
    if echo "$TOOL_OUTPUT" | grep -q "Status.*PASS"; then
      echo "PASS" > ".claude/state/qa-status-$CURRENT_PHASE"
      touch ".claude/state/qa-validated-$CURRENT_PHASE"
      echo "✅ QA validation PASSED for Phase $CURRENT_PHASE"
    else
      echo "FAIL" > ".claude/state/qa-status-$CURRENT_PHASE"
      echo "❌ QA validation FAILED - fix issues before proceeding"
    fi
  fi

  Hook 6: User Approval Capture

  {
    "name": "capture-phase-approval",
    "description": "Captures user 'yes' approval for phase transition",
    "event": "user-prompt-submit",
    "script": ".claude/hooks/capture-approval.sh",
    "blocking": false
  }

  Script: .claude/hooks/capture-approval.sh
  #!/bin/bash
  USER_MESSAGE="$1"

  # Check if user typed "yes" and we're at a phase gate
  if echo "$USER_MESSAGE" | grep -iqE "^yes$"; then
    CURRENT_PHASE=$(cat .claude/state/current-phase 2>/dev/null || echo "3.1")
    QA_STATUS=$(cat ".claude/state/qa-status-$CURRENT_PHASE" 2>/dev/null)

    if [ "$QA_STATUS" = "PASS" ]; then
      touch ".claude/state/phase-approved-$CURRENT_PHASE"

      # Advance to next phase
      NEXT_PHASE=$(get_next_phase "$CURRENT_PHASE")
      echo "$NEXT_PHASE" > .claude/state/current-phase

      # Reset counters for next phase
      echo "0" > .claude/state/dev-count
      rm -f ".claude/state/qa-status-$NEXT_PHASE" 2>/dev/null

      echo "✅ Phase $CURRENT_PHASE approved - proceeding to Phase $NEXT_PHASE"
    fi
  fi

  Recommended Hook Configuration File

  .claude/settings.json:
  {
    "hooks": [
      {
        "name": "enforce-qa-before-phase-transition",
        "event": "before:tool:use",
        "toolPattern": "Task",
        "script": ".claude/hooks/check-qa-validation.sh",
        "blocking": true
      },
      {
        "name": "require-phase-approval",
        "event": "before:tool:use",
        "toolPattern": "Task",
        "script": ".claude/hooks/check-phase-approval.sh",
        "blocking": true
      },
      {
        "name": "remind-qa-after-dev",
        "event": "after:tool:use",
        "toolPattern": "Task",
        "script": ".claude/hooks/remind-qa.sh",
        "blocking": false
      },
      {
        "name": "block-commits-without-qa-pass",
        "event": "before:tool:use",
        "toolPattern": "Bash",
        "script": ".claude/hooks/check-commit-allowed.sh",
        "blocking": true
      },
      {
        "name": "track-phase-state",
        "event": "after:tool:use",
        "toolPattern": "Task",
        "script": ".claude/hooks/update-phase-state.sh",
        "blocking": false
      },
      {
        "name": "capture-phase-approval",
        "event": "user-prompt-submit",
        "script": ".claude/hooks/capture-approval.sh",
        "blocking": false
      }
    ]
  }

  How This Enforces Workflow

  1. Cannot skip QA: Hook 1 blocks starting Phase 3.2 tasks if Phase 3.1 wasn't QA-validated
  2. Cannot skip approval: Hook 2 blocks starting Phase 3.2 without user "yes"
  3. Reminded to run QA: Hook 3 shows reminder after all DEV agents complete
  4. Cannot commit without QA: Hook 4 blocks git commits until QA passes
  5. State tracking: Hooks 5-6 maintain state files to track progress

  State Directory Structure

  .claude/state/
  ├── current-phase           # Current phase number (e.g., "3.1")
  ├── dev-count               # Number of completed DEV agents
  ├── qa-validated-3.1        # Marker file: QA ran for phase 3.1
  ├── qa-status-3.1          # QA status: "PASS" or "FAIL"
  ├── phase-approved-3.1     # Marker file: User approved phase 3.1
  └── ...

  This would have 100% prevented my mistakes because the hooks would have blocked me from executing T011 without QA validation and user approval.