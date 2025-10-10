# Pantheon Workflow Improvements - Final Proposal

**Created**: 2025-10-06
**Status**: Final Proposal (Ready for Implementation)
**Based on**: Benchmark Test-1 Analysis + User Feedback Iteration

---

## Executive Summary

This proposal defines the **multi-agent quality-first workflow** for Pantheon v0.2.0, addressing critical gaps identified in benchmark test-1 that resulted in 43 failing tests and 67.5/100 score.

**Key Improvements**:
1. ✅ **Multi-Agent Architecture**: DEV (builder) + QA (validator) with independent context windows
2. ✅ **Parallel Execution**: Up to 3 DEV agents execute independent tasks simultaneously
3. ✅ **Phase Gates**: Automatic user checkpoints between phases with quality validation
4. ✅ **Hook-Based Enforcement**: Deterministic quality gates (SubagentStop, PreCommit hooks)
5. ✅ **Orchestrator Commits**: Batch commits after QA validation (DEV agents don't commit)

**Expected Outcome**: Score improvement from 67.5 → 85+, 0 failing tests, ≥80% coverage

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Agent Roles & Responsibilities](#agent-roles--responsibilities)
3. [Workflow Phases](#workflow-phases)
4. [Hook-Based Quality Gates](#hook-based-phase-gates)
5. [Parallel Execution Strategy](#parallel-execution-strategy)
6. [Implementation Specifications](#implementation-specifications)
7. [Implementation Plan](#implementation-plan)
8. [Success Criteria](#success-criteria)

---

## Architecture Overview

### Multi-Agent Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Main Claude Code Agent (Orchestrator)                          │
│  Executes: /implement command                                   │
│  - Loads context (spec.md, plan.md, tasks.md)                   │
│  - Manages workflow state & phase transitions                   │
│  - Invokes DEV/QA sub-agents via Task tool                      │
│  - Creates git commits after QA validation                      │
│  - Enforces phase gates (user checkpoints)                      │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │  PHASE GATE (User Checkpoint) │
            │  - Present phase plan         │
            │  - Wait for user approval     │
            └───────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────────────┐
    │  Phase N: Parallel Task Execution                 │
    │  (Max 3 independent tasks in parallel)            │
    └───────────────────────────────────────────────────┘
                            │
    ┌───────────────────────┴───────────────────────┐
    ▼                       ▼                       ▼
┌────────┐             ┌────────┐             ┌────────┐
│ DEV    │             │ DEV    │             │ DEV    │
│ T001   │             │ T002   │             │ T003   │
│        │             │        │             │        │
│ Code   │             │ Code   │             │ Code   │
│ Test   │             │ Test   │             │ Test   │
│ Verify │             │ Verify │             │ Verify │
│        │             │        │             │        │
│ NO     │             │ NO     │             │ NO     │
│ COMMIT │             │ COMMIT │             │ COMMIT │
└────────┘             └────────┘             └────────┘
    │                       │                       │
    └───────────────────────┴───────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │ SubagentStop Hook (DEV & QA)          │
        │ - DEV: Verify quality checks passed   │
        │ - QA: Verify all checks completed     │
        │ - Run actual quality commands          │
        │ - BLOCKS if verification fails        │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  Orchestrator Collects Results        │
        │  - If any DEV BLOCKED → halt, report  │
        │  - If all DEV SUCCESS → invoke QA     │
        └───────────────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │  QA Agent (Batch Validation)  │
            │  - Run ALL tests              │
            │  - Check ALL coverage         │
            │  - Validate ALL quality       │
            │  - Generate detailed report   │
            │  - Return: PASS or issues[]   │
            └───────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
            ┌────────┐              ┌────────┐
            │ PASS   │              │ FAIL   │
            └────────┘              └────────┘
                │                       │
                ▼                       ▼
    ┌─────────────────────┐   ┌─────────────────────┐
    │ Orchestrator:       │   │ Orchestrator:       │
    │ - Mark complete     │   │ - Parse QA report   │
    │ - Git commit batch  │   │ - Re-invoke DEV     │
    │   (PreCommit hook)  │   │   with issues       │
    │ - Continue          │   │ - Loop QA validation│
    └─────────────────────┘   └─────────────────────┘
                │                       │
                │                       ▼
                │               (3 attempts max)
                │                       │
                │                       ▼
                │               HALT → User guidance
                │
                ▼
    ┌───────────────────────────────────┐
    │  PHASE GATE (User Checkpoint)     │
    │  - Present completion report      │
    │  - Show quality metrics           │
    │  - Wait for approval to proceed   │
    └───────────────────────────────────┘
                │
                ▼
        (Next Phase or Complete)
```

### Architecture Principles

1. **Orchestrator is Main Agent**: `/implement` command executed by main Claude Code agent, NOT a sub-agent
2. **Sub-Agents are Specialists**: DEV builds, QA validates - independent context windows
3. **Orchestrator Owns Commits**: Only orchestrator creates git commits, after QA validation
4. **Sequential Validation**: All DEV agents complete → QA validates → commit (no interleaving)
5. **Defense in Depth**: DEV self-checks → SubagentStop hook → QA validation → PreCommit hook
6. **Project-Agnostic**: All quality commands discovered from project structure, not hardcoded

### Project-Agnostic Quality Commands

**Key Innovation**: No hardcoded commands like "npm test" or "pytest". The orchestrator discovers quality commands based on project analysis.

**Discovery Process**:
1. **Orchestrator analyzes project** during Phase Setup (first time only)
2. **Checks plan.md first** for explicitly specified commands
3. **Auto-discovers if not specified**:
   - Node.js: Parse `package.json` scripts
   - Python: Check for `pytest`, `ruff`, `mypy` in pyproject.toml or poetry
   - Go: Check for `go test`, `golangci-lint`
   - Ruby: Check for `rspec`, `rubocop`
   - etc.
4. **Creates `.pantheon/quality-config.json`** with discovered commands
5. **All agents and hooks read from config** (not hardcoded)

**Benefits**:
- ✅ Works with **any tech stack** (Node, Python, Go, Ruby, Rust, etc.)
- ✅ Works with **any testing framework** (Jest, Vitest, pytest, go test, etc.)
- ✅ Works with **any linter** (ESLint, Ruff, golangci-lint, etc.)
- ✅ User can **override via plan.md** if auto-discovery insufficient
- ✅ **Single source of truth** (.pantheon/quality-config.json)

**Example Config** (created by orchestrator):
```json
{
  "test_command": "[discovered or from plan.md]",
  "coverage_command": "[discovered or from plan.md]",
  "lint_command": "[discovered or from plan.md]",
  "type_command": "[discovered or from plan.md]",
  "build_command": "[discovered or from plan.md]",
  "coverage_threshold": 80
}
```

---

## Agent Roles & Responsibilities

### 1. Orchestrator (Main Claude Code Agent)

**What It Is**: The main Claude Code agent executing the `/implement` slash command

**Responsibilities**:
- Load context (spec.md, plan.md, tasks.md)
- Extract quality standards from plan.md
- Analyze task dependencies
- Group independent tasks for parallel execution (max 3)
- Invoke DEV sub-agents via Task tool (parallel or sequential)
- Collect DEV results and handle BLOCKED status
- Invoke QA sub-agent for batch validation
- Process QA reports and re-invoke DEV for fixes if needed
- Create git commits at phase boundaries (after QA PASS)
- Enforce phase gates (present plan, wait for user approval)
- Report status to user

**Does NOT**:
- Write code directly
- Run tests directly (delegates to QA)
- Make architectural decisions without user approval

**Tools Available**:
- All Claude Code tools (Read, Write, Edit, Bash, Task, etc.)

---

### 2. DEV Agent (Implementation Specialist)

**What It Is**: Sub-agent with focused context for implementing a single task

**Responsibilities**:
- Receive single task + context package from orchestrator
- Implement code following TDD (test-first)
- Write comprehensive unit/integration tests
- Run verification commands (lint, type-check, test)
- Self-check against acceptance criteria
- Return: SUCCESS + summary OR BLOCKED + reason
- **Does NOT commit** - orchestrator handles commits

**Context Package Receives**:
```markdown
Task: T001 - Implement user authentication
Description: [Full task description]
Files: backend/src/services/UserService.ts
Acceptance Criteria:
  - [ ] Create user with valid email
  - [ ] Reject invalid email formats
  - [ ] Prevent duplicate emails
Quality Standards:
  - Test command: npm test
  - Lint command: npm run lint
  - Type check: npm run type-check
  - Coverage threshold: 80%
Related Requirements: FR-010, FR-011
Tech Stack: Node.js, TypeScript, Express, PostgreSQL
```

**Verification Workflow** (in agent):
```markdown
For each acceptance criterion:
1. Write test (TDD)
2. Implement code
3. Run verification:
   - npm test (must pass)
   - npm run lint (0 errors)
   - npm run type-check (0 errors)
4. If fails → fix immediately, re-verify
5. If passes → next criterion

After all criteria complete:
- Self-inspection (no console.log, no TODOs, no unused imports)
- Return SUCCESS to orchestrator
```

**Constraints**:
- ❌ Cannot mark task complete if tests fail
- ❌ Cannot skip acceptance criteria
- ❌ Cannot commit code
- ❌ Cannot modify other tasks
- ✅ Can return BLOCKED if needs clarification (max 3 attempts)

**Tools Available** (restricted):
- Read, Write, Edit, Bash, Glob, Grep
- MCP browser (for manual testing if needed)
- Playright MCP
- NO web search, NO Task tool (can't spawn more agents)

---

### 3. QA Agent (Verification Specialist)

**What It Is**: Sub-agent with focused context for comprehensive quality validation

**Responsibilities**:
- Receive batch of tasks claimed complete
- Run full test suite using commands from plan.md
- Analyze test results (parse failures, identify issues)
- Check coverage thresholds
- Validate linting and type checking
- Search for code smells (unused code, TODOs, console.log)
- Verify Definition of Done checklist
- Generate structured report with actionable recommendations
- Return: PASS or FAIL + detailed issue report
- **Does NOT fix issues** - only reports them

**Context Package Receives**:
```markdown
Tasks to Validate: T001, T002, T003
Quality Standards (from plan.md):
  - Test command: [project-specific]
  - Coverage command: [project-specific]
  - Lint command: [project-specific]
  - Type check: [project-specific]
  - Coverage threshold: 80% (branches, statements, functions)
Definition of Done (non-negotiable):
  - [ ] All acceptance criteria met
  - [ ] All tests pass
  - [ ] Coverage ≥80%
  - [ ] 0 lint errors
  - [ ] 0 type errors
  - [ ] [other relevant quality checks]
  - etc.
Project Root: /path/to/project
```

**Validation Workflow** (in agent):
```markdown
Phase 1: Run Automated Checks
- Execute test command → capture output
- Execute coverage command → parse metrics
- Execute lint command → identify errors
- Execute type check → identify errors

Phase 2: Run Manual Acceptance Criteria Checks
- Use any MCPs or tools necessary to run manual verification of features against live application
- If back end work, use the API, verify data flows, CRUD operations, etc.
- If front end work, use the running application, take screenshots, verify buttons, inputs, etc. all work

Phase 3: Analyze Results
- Parse test output for failures
- Extract coverage metrics (branches, statements, functions)
- Compare coverage to thresholds
- Identify specific failing tests, locations, errors

Phase 4: Code Quality Inspection
- Search for console.log in src/ (excluding tests)
- Search for TODO comments
- Check linting output for unused imports
- Identify files with 0% coverage (unused code)

Phase 5: Link Issues to Tasks
- Determine which task likely caused each issue
- Classify severity (CRITICAL, MAJOR, MINOR)
- Generate actionable recommendations

Phase 6: Report Generation
- Generate structured JSON report
- Clear PASS or FAIL determination
- Return to orchestrator
```

**Report Format**:
```json
{
  "status": "PASS" | "FAIL",
  "summary": {
    "tests_total": 245,
    "tests_passing": 245,
    "tests_failing": 0,
    "coverage_branches": 84.3,
    "coverage_statements": 86.7,
    "coverage_functions": 82.1,
    "coverage_threshold": 80.0,
    "lint_errors": 0,
    "type_errors": 0
  },
  "issues": [
    {
      "task": "T001",
      "severity": "CRITICAL",
      "type": "TEST_FAILURE",
      "count": 5,
      "description": "Auth edge cases failing",
      "location": "backend/tests/services/UserService.test.ts:45-82",
      "sample_error": "Expected user creation to fail, but succeeded",
      "recommendation": "Add email format validation before database insert"
    }
  ],
  "definition_of_done": {
    "all_tests_pass": true,
    "coverage_thresholds_met": true,
    "no_lint_errors": true,
    "no_type_errors": true,
    "no_console_statements": true,
    "no_todos": true,
    "no_unused_code": true
  }
}
```

**Constraints**:
- ❌ Cannot fix issues (only report)
- ❌ Cannot modify code
- ❌ Cannot mark PASS if any CRITICAL issue exists
- ✅ Can run read-only tools (test, lint, grep, coverage)
- ✅ Must provide specific file/line locations for issues
- ✅ Must include actionable recommendations

**Tools Available** (restricted):
- Read, Bash, Grep, Glob
- MCP browser (for manual feature testing)
- Playwright MCP (for manual feature testing)
- NO Write, NO Edit (read-only validation)

**Project-Agnostic Design**:
QA agent is a **template** - it doesn't hardcode commands like `npm test`. Instead, it receives commands from plan.md and executes whatever the project uses:
- Node.js project: `npm test`, `npm run lint`
- Python project: `pytest`, `ruff check`
- Go project: `go test`, `golangci-lint run`
- etc.

---

## Workflow Phases

### Phase Setup (Before Each Phase)

**Orchestrator Actions**:
```markdown
1. Load context (spec.md, plan.md, tasks.md)
2. Discover and configure quality commands (FIRST TIME ONLY):
   - Analyze project structure (package.json, pyproject.toml, Makefile, etc.)
   - Extract quality commands from plan.md if specified
   - Auto-discover commands if not in plan.md:
     - Node.js: check package.json scripts for test, lint, type-check
     - Python: check for pytest, ruff, mypy commands
     - Go: check for go test, golangci-lint
     - etc.
   - Create .pantheon/quality-config.json with discovered commands
   - Include coverage threshold from plan.md (default: 80%)
3. Identify current phase from plan.md
4. Extract tasks for this phase
5. Analyze task dependencies from tasks.md
6. Group tasks for parallel execution:
   - Independent tasks (no dependencies) → parallel batch
   - Dependent tasks → sequential execution
   - Max 3 parallel DEV agents per batch
7. Present phase plan to user
8. WAIT for user approval
```

**Example Quality Config Discovery**:

For a Node.js project with `package.json`:
```json
{
  "scripts": {
    "test": "jest",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/",
    "type-check": "tsc --noEmit",
    "build": "tsc"
  }
}
```

Orchestrator creates `.pantheon/quality-config.json`:
```json
{
  "test_command": "npm test",
  "coverage_command": "npm run test:coverage",
  "lint_command": "npm run lint",
  "type_command": "npm run type-check",
  "build_command": "npm run build",
  "coverage_threshold": 80
}
```

For a Python project with `pyproject.toml`:
```json
{
  "test_command": "pytest",
  "coverage_command": "pytest --cov=src --cov-report=term-missing",
  "lint_command": "ruff check .",
  "type_command": "mypy src/",
  "build_command": "python -m build",
  "coverage_threshold": 80
}
```

**Phase Plan Presentation** (orchestrator output):
```markdown
📋 **Phase 2 Plan: Core Features Implementation**

**Objective**: Implement user management, task CRUD, and tagging system

**Tasks in Phase**:
- T005: User authentication service
- T006: Task CRUD operations
- T007: Tag management
- T008: User-task associations
- T009: Task-tag associations

**Dependency Analysis**:
- T005: No dependencies
- T006: No dependencies
- T007: No dependencies
- T008: Depends on T005, T006
- T009: Depends on T006, T007

**Parallelization Strategy**:
- Batch 1 (parallel): T005, T006, T007 (3 DEV agents)
- Batch 2 (sequential): T008 (1 DEV agent, after batch 1 complete)
- Batch 3 (sequential): T009 (1 DEV agent, after batch 1 complete)

**Quality Standards** (from plan.md):
- Test command: npm test
- Coverage threshold: ≥80% (branches, statements, functions)
- Lint command: npm run lint (0 errors)
- Type check: npm run type-check (0 errors)

**Estimated Time**: ~45-60 minutes (with parallel execution)

**Proceed with this plan?** (yes/no)
```

**User Response**: User types "yes" → orchestrator proceeds

---

### Task Execution (Per Batch)

**Step 1: Parallel DEV Invocation**

Orchestrator invokes multiple DEV agents in **single message**:

```markdown
I'm now executing batch 1 (T005, T006, T007) with 3 parallel DEV agents.

[Uses Task tool 3 times in parallel:]

Task 1:
  subagent_type: "dev"
  description: "Implement T005"
  prompt: |
    Task: T005 - Implement user authentication service
    Files: backend/src/services/UserService.ts
    [Full context package here]

Task 2:
  subagent_type: "dev"
  description: "Implement T006"
  prompt: |
    Task: T006 - Implement task CRUD operations
    [Full context package here]

Task 3:
  subagent_type: "dev"
  description: "Implement T007"
  prompt: |
    Task: T007 - Implement tag management
    [Full context package here]
```

**Step 2: DEV Agents Execute**

Each DEV agent (in parallel, independent context windows):
1. Reads task context
2. Implements code + tests (TDD)
3. Runs verification (npm test, lint, type-check)
4. Self-checks (no console.log, no TODOs)
5. Returns SUCCESS or BLOCKED to orchestrator

**Step 3: SubagentStop Hook Validation**

When each DEV completes, SubagentStop hook runs automatically:
```bash
# .pantheon/hooks/subagent-validation.sh
- Check for console.log in src/ → BLOCK if found
- Check for TODO comments → BLOCK if found
- Check for unused imports (basic lint check) → BLOCK if found
- If any violation → DEV blocked, must fix
- If all pass → DEV output accepted
```

**Step 4: Orchestrator Collects Results**

```markdown
DEV T005: SUCCESS ✅
DEV T006: SUCCESS ✅
DEV T007: BLOCKED ❌ (SubagentStop hook found console.log in TagService.ts)

Action: Re-invoke DEV for T007 with error details.
```

If any DEV BLOCKED:
- Orchestrator re-invokes that specific DEV with blocker details
- Other successful DEVs' work is preserved
- Loop until all DEVs succeed (max 3 attempts per task)

**Step 5: QA Validation**

After all DEVs in batch succeed:

```markdown
All DEV agents completed successfully. Invoking QA agent for batch validation.

[Uses Task tool:]
Task:
  subagent_type: "qa"
  description: "Validate T005, T006, T007"
  prompt: |
    Validate the following tasks: T005, T006, T007
    Quality Standards:
      - Test command: npm test
      - Coverage command: npm run test:coverage
      - Coverage threshold: 80%
      - Lint command: npm run lint
      - Type check: npm run type-check
    Definition of Done:
      [Full checklist from plan.md]
    Project Root: /path/to/project
```

**Step 6: QA Agent Executes**

QA agent (in independent context window):
1. Runs `[project-specific test command]` → analyzes output
2. Runs `[project-specific test coverage command]` → checks thresholds
3. Runs `[project-specific lint command]` → identifies errors
4. Runs `[project-specific typecheck command]` → identifies errors
5. Searches for code smells (console.log, TODOs, unused code, etc.)
6. Links issues to specific tasks
7. Generates structured report
8. Returns PASS or FAIL to orchestrator

**Step 7: Process QA Results**

**Scenario A: QA Returns PASS**

```markdown
QA Validation: PASS ✅

Summary:
- Tests: 245/245 passing
- Coverage: 84.3% branches, 86.7% statements (threshold: 80%)
- Lint: 0 errors
- Type check: 0 errors
- No console.log, no TODOs, no unused code

Actions:
1. Mark tasks complete in tasks.md (T005 ✅, T006 ✅, T007 ✅)
2. Create git commit for batch
```

Orchestrator creates commit:
```bash
git add .
git commit -m "feat: Implement user auth, task CRUD, and tag management

Completed tasks: T005, T006, T007

[insert full description of compelted work here]

[insert small quality report here]
```

**Pre-commit hook runs automatically** before commit:
```bash
# .pantheon/hooks/pre-commit-gate.sh
- Run quality command which verifies linting, typechecking, tests, and test coverage
- If any fail → BLOCK commit, report to orchestrator
- If all pass → commit allowed
```

**Scenario B: QA Returns FAIL**

```markdown
QA Validation: FAIL ❌

Issues Found:
1. CRITICAL - T006: 5 tests failing in TaskService (edge cases not covered)
2. MAJOR - T007: Coverage 72% (below 80% threshold)
3. MINOR - T005: 2 unused imports in UserService

QA Report:
{
  "status": "FAIL",
  "issues": [
    {
      "task": "T006",
      "severity": "CRITICAL",
      "type": "TEST_FAILURE",
      "count": 5,
      "description": "Task deletion edge cases failing",
      "location": "backend/tests/services/TaskService.test.ts:120-145",
      "sample_error": "Expected error when deleting non-existent task, got success",
      "recommendation": "Add validation to check if task exists before deletion"
    },
    {
      "task": "T007",
      "severity": "MAJOR",
      "type": "COVERAGE",
      "description": "Branch coverage 72% (threshold: 80%)",
      "gap": -8.0,
      "recommendation": "Add tests for error paths in tag creation and update"
    }
  ]
}

Actions:
1. Do NOT mark tasks complete
2. Do NOT create git commit
3. Re-invoke DEV agents for failing tasks with QA findings
```

Orchestrator re-invokes specific DEV agents:

```markdown
Re-invoking DEV for T006 to fix QA issues.

[Uses Task tool:]
Task:
  subagent_type: "dev"
  description: "Fix T006 issues"
  prompt: |
    Fix issues in task T006 identified by QA:

    Original Task: T006 - Implement task CRUD operations

    QA Findings:
    - 5 tests failing: Task deletion edge cases
    - Location: backend/tests/services/TaskService.test.ts:120-145
    - Error: "Expected error when deleting non-existent task, got success"
    - Recommendation: Add validation to check if task exists before deletion

    Required Fixes:
    1. Add validation in TaskService.delete() to check task existence
    2. Ensure tests pass (npm test)
    3. Maintain coverage ≥80%
    4. Re-run all verification commands
```

**Step 8: Feedback Loop**

```
DEV fix → QA validate → (PASS → commit) or (FAIL → DEV fix again)
```

**Failure Threshold**: If 3 QA validation cycles fail on same task:
```markdown
❌ Task T006 failed QA validation 3 times.

Latest QA Report: [details]

HALTING execution. User guidance required.

Options:
1. Review QA report and provide clarification
2. Adjust acceptance criteria in tasks.md
3. Manually fix and resume
4. Skip task (mark as BLOCKED for later)

Please advise how to proceed.
```

---

### Phase Completion

After all tasks in phase complete and pass QA:

**Step 1: Final QA Validation**

Orchestrator runs final comprehensive check:
```bash
[run all project-specific quality checks]
[run project-specific build and run]  # Ensure production build works
```

**Step 2: Generate Phase Completion Report**

```markdown
✅ **Phase 2 Complete: Core Features Implementation**

**Completion Date**: 2025-10-06 14:32 PST

**Tasks Completed**:
- T005: User authentication service ✅
- T006: Task CRUD operations ✅
- T007: Tag management ✅
- T008: User-task associations ✅
- T009: Task-tag associations ✅

**Quality Metrics**:
- Tests: 245/245 passing ✅ (0 failures)
- Coverage: 84.3% branches, 86.7% statements, 82.1% functions ✅ (threshold: 80%)
- Linting: 0 errors ✅
- Type checking: 0 errors ✅
- Build: Success ✅

**Git Commits Created**:
- feat: Implement user auth, task CRUD, and tag management (abc123)
- feat: Implement user-task and task-tag associations (def456)

**Phase Statistics**:
- DEV agents invoked: 5
- QA validations: 2
- Rework cycles: 1 (T006 fixed after QA feedback)
- Total duration: 52 minutes

**Phase Status**: COMPLETE ✅

**Next Phase**: Phase 3 - API Endpoints Implementation

**Proceed to Phase 3?** (yes/no/review)
```

**Step 3: Phase Gate Hook** (Automatic)

When user responds, automatic phase gate validation runs:
```bash
# .pantheon/hooks/phase-gate.sh
# Triggered on user prompt containing "yes" or "proceed"
- Run project specific quality checks (lint, typecheck, tests, test coverage0)
- If any fail → BLOCK phase transition, report issues
- If all pass → allow proceeding to next phase
```

**Step 4: User Approval**

User types "yes" → orchestrator proceeds to Phase 3

User types "review" → orchestrator waits for user to review code, then ask again

User types "no" → orchestrator asks for clarification on what needs adjustment

---

## Hook-Based Quality Gates

### Hook Architecture: Defense in Depth

```
Layer 1: DEV Self-Check (soft)
   ↓ (DEV runs verification commands)
Layer 2: SubagentStop Hook (medium - fast sanity check)
   ↓ (Blocks DEV completion if obvious violations)
Layer 3: QA Agent Validation (deep - comprehensive analysis)
   ↓ (Detailed report with recommendations)
Layer 4: PreCommit Hook (hard - final gate before commit)
   ↓ (Blocks git commit if tests/lint fail)
Layer 5: Phase Gate Hook (automatic - phase transition validation)
   ↓ (Ensures phase complete before moving forward)
```

### Hook Specifications

#### Hook 1: SubagentStop Hook

**Purpose**: Verify sub-agent completed all required tasks before returning to orchestrator

**Event**: `SubagentStop`

**File**: `.pantheon/hooks/subagent-validation.sh`

**How Quality Commands are Discovered**:
The hook reads quality commands from `.pantheon/quality-config.json` which is created by the orchestrator during phase setup based on project analysis (package.json scripts, pyproject.toml, Makefile, etc.)

**Script**:
```bash
#!/bin/bash
# SubagentStop Hook - Verify sub-agent completed all required checks
# Runs when DEV or QA sub-agent finishes, before returning to orchestrator

set -e

echo "🔍 Validating $SUBAGENT_NAME agent completion..."

# Load quality commands from config (created by orchestrator)
CONFIG_FILE=".pantheon/quality-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "⚠️  Warning: Quality config not found, skipping validation"
  exit 0
fi

# Read commands from config
TEST_CMD=$(jq -r '.test_command // empty' "$CONFIG_FILE")
LINT_CMD=$(jq -r '.lint_command // empty' "$CONFIG_FILE")
TYPE_CMD=$(jq -r '.type_command // empty' "$CONFIG_FILE")

FAILED=0

# DEV Agent Validation
if [[ "$SUBAGENT_NAME" == "DEV" ]]; then
  echo "📋 Validating DEV agent completion..."

  # Check 1: Verify tests pass
  if [ -n "$TEST_CMD" ]; then
    echo "🧪 Verifying tests..."
    if ! eval "$TEST_CMD" > /tmp/subagent-test.log 2>&1; then
      echo "❌ Tests failing - DEV agent should have fixed these"
      tail -20 /tmp/subagent-test.log
      FAILED=1
    else
      echo "✅ Tests passing"
    fi
  fi

  # Check 2: Verify linting passes
  if [ -n "$LINT_CMD" ]; then
    echo "📋 Verifying linting..."
    if ! eval "$LINT_CMD" > /tmp/subagent-lint.log 2>&1; then
      echo "❌ Linting errors - DEV agent should have fixed these"
      tail -20 /tmp/subagent-lint.log
      FAILED=1
    else
      echo "✅ Linting passing"
    fi
  fi

  # Check 3: Verify type checking passes
  if [ -n "$TYPE_CMD" ]; then
    echo "🔤 Verifying type checking..."
    if ! eval "$TYPE_CMD" > /tmp/subagent-type.log 2>&1; then
      echo "❌ Type errors - DEV agent should have fixed these"
      tail -20 /tmp/subagent-type.log
      FAILED=1
    else
      echo "✅ Type checking passing"
    fi
  fi

  # Check 4: No console.log in production code
  if grep -r "console\.log\|console\.error\|console\.warn" src/ --exclude-dir=node_modules --exclude="*.test.*" --exclude="*.spec.*" 2>/dev/null; then
    echo "❌ Found console statements in production code"
    FAILED=1
  fi

  # Check 5: No TODO comments
  if grep -r "TODO\|FIXME\|XXX" src/ --exclude-dir=node_modules 2>/dev/null; then
    echo "❌ Found TODO/FIXME comments - track in tasks.md instead"
    FAILED=1
  fi

  # Check 6: No debugger statements
  if grep -r "debugger" src/ --exclude-dir=node_modules 2>/dev/null; then
    echo "❌ Found debugger statements"
    FAILED=1
  fi

  if [ $FAILED -eq 1 ]; then
    echo ""
    echo "❌ BLOCKED: DEV agent claims completion but quality checks failed"
    echo "DEV must fix all issues before completing task."
    echo ""
    exit 2  # Exit code 2 blocks the sub-agent completion
  fi

  echo "✅ DEV agent validation passed"
fi

# QA Agent Validation
if [[ "$SUBAGENT_NAME" == "QA" ]]; then
  echo "📊 Validating QA agent completion..."

  # Check 1: Verify QA ran test command
  if [ -n "$TEST_CMD" ] && [ ! -f "/tmp/qa-test-results.txt" ]; then
    echo "❌ QA agent didn't run tests (missing /tmp/qa-test-results.txt)"
    FAILED=1
  fi

  # Check 2: Verify QA ran coverage command
  if [ ! -f "/tmp/qa-coverage-results.txt" ]; then
    echo "❌ QA agent didn't run coverage (missing /tmp/qa-coverage-results.txt)"
    FAILED=1
  fi

  # Check 3: Verify QA ran lint command
  if [ -n "$LINT_CMD" ] && [ ! -f "/tmp/qa-lint-results.txt" ]; then
    echo "❌ QA agent didn't run linting (missing /tmp/qa-lint-results.txt)"
    FAILED=1
  fi

  # Check 4: Verify QA ran type check command
  if [ -n "$TYPE_CMD" ] && [ ! -f "/tmp/qa-type-results.txt" ]; then
    echo "❌ QA agent didn't run type checking (missing /tmp/qa-type-results.txt)"
    FAILED=1
  fi

  # Check 5: Verify QA generated report (check for JSON structure in output)
  # This is validated by orchestrator, but we can check for report keywords

  if [ $FAILED -eq 1 ]; then
    echo ""
    echo "❌ BLOCKED: QA agent didn't complete all required checks"
    echo "QA must run all quality commands before returning."
    echo ""
    exit 2
  fi

  echo "✅ QA agent validation passed"
fi

echo ""
exit 0  # Exit code 0 allows sub-agent to complete
```

**Configuration** (`.claude/settings.json`):
```json
{
  "hooks": {
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .pantheon/hooks/subagent-validation.sh",
            "timeout": 120000
          }
        ]
      }
    ]
  }
}
```

**Quality Config Format** (`.pantheon/quality-config.json`, created by orchestrator):
```json
{
  "test_command": "npm test",
  "coverage_command": "npm run test:coverage",
  "lint_command": "npm run lint",
  "type_command": "npm run type-check",
  "build_command": "npm run build"
}
```

**Characteristics**:
- 🧪 **Comprehensive**: Runs actual quality commands (tests, lint, typecheck)
- 🚫 **Blocking**: Agent can't complete if validation fails
- 🤖 **Deterministic**: No LLM interpretation, pure bash
- 🎯 **Agent-Specific**: Different validation for DEV vs QA
- 📋 **Project-Agnostic**: Uses commands from config file

**What It Catches**:

**For DEV Agent**:
- ✅ Tests failing (actual test run)
- ✅ Lint errors (actual lint run)
- ✅ Type errors (actual type check)
- ✅ console.log/error/warn in production code
- ✅ TODO/FIXME comments
- ✅ debugger statements

**For QA Agent**:
- ✅ QA skipped running tests
- ✅ QA skipped running coverage
- ✅ QA skipped running lint
- ✅ QA skipped running type check
- ✅ QA didn't generate report files

---

#### Hook 2: PreCommit Hook

**Purpose**: Final quality gate before git commit - ensures all quality checks pass

**Event**: `PreToolUse` on `Bash` tool matching `git commit`

**File**: `.pantheon/hooks/pre-commit-gate.sh`

**Script**:
```bash
#!/bin/bash
# PreCommit Hook - Final quality gate before git commit
# Blocks commits if quality checks fail

set -e

echo "🔍 Running pre-commit quality gate..."

# Load quality commands from config
CONFIG_FILE=".pantheon/quality-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "⚠️  Warning: Quality config not found, allowing commit"
  exit 0
fi

# Read commands from config
TEST_CMD=$(jq -r '.test_command // empty' "$CONFIG_FILE")
LINT_CMD=$(jq -r '.lint_command // empty' "$CONFIG_FILE")
TYPE_CMD=$(jq -r '.type_command // empty' "$CONFIG_FILE")
COVERAGE_CMD=$(jq -r '.coverage_command // empty' "$CONFIG_FILE")

FAILED=0

# Check 1: Tests must pass
if [ -n "$TEST_CMD" ]; then
  echo "🧪 Running tests..."
  if ! eval "$TEST_CMD" 2>&1 | tee /tmp/precommit-test.log; then
    echo "❌ BLOCKED: Tests are failing"
    echo "   Run '$TEST_CMD' to see failures and fix before committing"
    FAILED=1
  else
    echo "✅ Tests passed"
  fi
fi

# Check 2: Linting must pass
if [ -n "$LINT_CMD" ]; then
  echo "📋 Running linting..."
  if ! eval "$LINT_CMD" 2>&1 | tee /tmp/precommit-lint.log; then
    echo "❌ BLOCKED: Linting errors found"
    echo "   Run '$LINT_CMD' to see errors and fix before committing"
    FAILED=1
  else
    echo "✅ Linting passed"
  fi
fi

# Check 3: Type checking must pass
if [ -n "$TYPE_CMD" ]; then
  echo "🔤 Running type checking..."
  if ! eval "$TYPE_CMD" 2>&1 | tee /tmp/precommit-type.log; then
    echo "❌ BLOCKED: Type errors found"
    echo "   Run '$TYPE_CMD' to see errors and fix before committing"
    FAILED=1
  else
    echo "✅ Type checking passed"
  fi
fi

# Check 4: Coverage thresholds must be met (optional)
if [ -n "$COVERAGE_CMD" ]; then
  echo "📊 Checking coverage..."
  if ! eval "$COVERAGE_CMD" 2>&1 | tee /tmp/precommit-coverage.log; then
    echo "⚠️  Warning: Coverage check failed (not blocking)"
    # Not blocking on coverage for pre-commit, QA handles this
  fi
fi

# Exit with appropriate code
if [ $FAILED -eq 1 ]; then
  echo ""
  echo "❌ BLOCKED: Cannot commit - quality checks failed"
  echo "Fix issues above before committing."
  echo ""
  exit 2  # Exit code 2 blocks the tool use
fi

echo ""
echo "✅ All pre-commit checks passed. Commit allowed."
echo ""
exit 0  # Exit code 0 allows the commit
```

**Configuration** (`.claude/settings.json`):
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit*)",
        "hooks": [
          {
            "type": "command",
            "command": "bash .pantheon/hooks/pre-commit-gate.sh",
            "timeout": 120000
          }
        ]
      }
    ]
  }
}
```

**Characteristics**:
- 🔒 **Hard Gate**: Physically blocks git commit if checks fail
- 🧪 **Comprehensive**: Runs tests, lint, type-check
- ⏱️ **Slower**: 30-60 seconds (runs full test suite)
- 🎯 **Final Validation**: Last check before code committed

**What It Catches**:
- ✅ Failing tests (if they regressed since QA check)
- ✅ Lint errors introduced after QA
- ✅ Type errors introduced after QA
- ✅ Any quality degradation between QA and commit

---

#### Hook 3: Phase Gate Hook

**Purpose**: Automatic validation when transitioning between phases

**Event**: `UserPromptSubmit` (when user says "yes" to proceed to next phase)

**File**: `.pantheon/hooks/phase-gate.sh`

**Script**:
```bash
#!/bin/bash
# Phase Gate Hook - Validates phase completion before proceeding
# Runs automatically when user approves phase transition

set -e

# Extract phase number or "proceed" keyword from user prompt
USER_INPUT=$(echo "$USER_PROMPT" | tr '[:upper:]' '[:lower:]')

# Check if this is a phase transition (user said "yes", "proceed", or "phase X")
if ! echo "$USER_INPUT" | grep -qE "yes|proceed|phase [0-9]+"; then
  exit 0  # Not a phase transition, allow
fi

echo "🚪 Phase gate validation..."

# Load quality commands from config
CONFIG_FILE=".pantheon/quality-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "⚠️  Warning: Quality config not found, allowing phase transition"
  exit 0
fi

# Read commands and thresholds from config
TEST_CMD=$(jq -r '.test_command // empty' "$CONFIG_FILE")
LINT_CMD=$(jq -r '.lint_command // empty' "$CONFIG_FILE")
TYPE_CMD=$(jq -r '.type_command // empty' "$CONFIG_FILE")
COVERAGE_CMD=$(jq -r '.coverage_command // empty' "$CONFIG_FILE")
COVERAGE_THRESHOLD=$(jq -r '.coverage_threshold // 80' "$CONFIG_FILE")

FAILED=0

# Check 1: All tests must pass
if [ -n "$TEST_CMD" ]; then
  echo "🧪 Verifying tests..."
  if ! eval "$TEST_CMD" 2>&1 | tail -n 20; then
    echo "❌ BLOCKED: Cannot proceed - tests are failing"
    FAILED=1
  else
    echo "✅ All tests passing"
  fi
fi

# Check 2: Coverage must meet threshold
if [ -n "$COVERAGE_CMD" ]; then
  echo "📊 Verifying coverage (threshold: ${COVERAGE_THRESHOLD}%)..."
  COVERAGE_OUTPUT=$(eval "$COVERAGE_CMD" 2>&1 || true)
  echo "$COVERAGE_OUTPUT" | tail -n 10

  # Check if coverage meets threshold (looking for percentage >= threshold)
  # This is a simple check - actual parsing depends on coverage tool output format
  if ! echo "$COVERAGE_OUTPUT" | grep -qE "Branches.*[8-9][0-9]|100|${COVERAGE_THRESHOLD}"; then
    echo "⚠️  Warning: Coverage may be below ${COVERAGE_THRESHOLD}% threshold"
    # Not blocking on coverage for phase gate, QA handles enforcement
  else
    echo "✅ Coverage thresholds met"
  fi
fi

# Check 3: No linting errors
if [ -n "$LINT_CMD" ]; then
  echo "📋 Verifying linting..."
  if ! eval "$LINT_CMD" 2>&1; then
    echo "❌ BLOCKED: Linting errors found"
    FAILED=1
  else
    echo "✅ No linting errors"
  fi
fi

# Check 4: No type errors
if [ -n "$TYPE_CMD" ]; then
  echo "🔤 Verifying types..."
  if ! eval "$TYPE_CMD" 2>&1; then
    echo "❌ BLOCKED: Type errors found"
    FAILED=1
  else
    echo "✅ No type errors"
  fi
fi

# Exit with appropriate code
if [ $FAILED -eq 1 ]; then
  echo ""
  echo "❌ BLOCKED: Phase gate validation failed"
  echo "Current phase is not complete. Fix issues above before proceeding."
  echo ""
  exit 2  # Exit code 2 blocks the user prompt
fi

echo ""
echo "✅ Phase gate validation passed. Proceeding to next phase."
echo ""
exit 0  # Exit code 0 allows proceeding
```

**Configuration** (`.claude/settings.json`):
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .pantheon/hooks/phase-gate.sh",
            "timeout": 120000
          }
        ]
      }
    ]
  }
}
```

**Characteristics**:
- 🤖 **Automatic**: Runs when user says "yes"/"proceed"
- 🔒 **Blocking**: Prevents phase transition if validation fails
- 🧪 **Comprehensive**: Full quality suite
- 📊 **Coverage Check**: Ensures thresholds met

**What It Catches**:
- ✅ Phase completed with failing tests
- ✅ Phase completed with coverage below threshold
- ✅ Phase completed with lint/type errors
- ✅ Prevents moving to next phase prematurely

---

### Hook Installation

Hooks are installed automatically when user runs `pantheon integrate`:

```bash
pantheon integrate
```

Installation process:
1. Create `.pantheon/hooks/` directory
2. Copy hook scripts from package to project
3. Add hook configuration to `.claude/settings.json`
4. Make hook scripts executable (`chmod +x`)
5. Validate hook configuration
6. Report installation status

---

## Parallel Execution Strategy

### Execution Rules

1. **Max 3 Parallel DEV Agents**: Hard limit (configurable in future versions)
2. **Dependency-Aware**: Only execute tasks with satisfied dependencies
3. **Sequential Validation**: All DEV complete → then QA validates (no interleaving)
4. **Batch Commits**: Orchestrator commits after QA PASS for entire batch

### Dependency Analysis

Orchestrator analyzes tasks.md to determine parallelization strategy:

**Example tasks.md**:
```markdown
**T001** Setup database schema
- Dependencies: None

**T002** Implement UserService
- Dependencies: T001

**T003** Implement TaskService
- Dependencies: T001

**T004** Implement TagService
- Dependencies: None

**T005** Implement user-task associations
- Dependencies: T002, T003

**T006** Implement task-tag associations
- Dependencies: T003, T004
```

**Orchestrator Analysis**:
```markdown
Phase: Core Services Implementation

Batch 1 (parallel, 3 agents):
- T001: Setup database schema (no deps)
- T004: Implement TagService (no deps)
- [Only 2 tasks with no deps, so 2 parallel agents]

Batch 2 (parallel, 3 agents):
- T002: Implement UserService (T001 complete ✅)
- T003: Implement TaskService (T001 complete ✅)
- [Only 2 tasks with satisfied deps]

Batch 3 (parallel, 2 agents):
- T005: User-task associations (T002 ✅, T003 ✅)
- T006: Task-tag associations (T003 ✅, T004 ✅)
```

### Execution Pattern

**No Interleaving** (rejected Pattern 2):
```
❌ WRONG: DEV on T002 while QA validates T001
```

**Sequential Validation** (correct):
```
✅ CORRECT:
1. DEV T001, T004 (parallel) → both complete
2. QA validates T001, T004 batch
3. If PASS → commit, proceed to batch 2
4. DEV T002, T003 (parallel) → both complete
5. QA validates T002, T003 batch
6. If PASS → commit, proceed to batch 3
```

### Benefits

- ⚡ **3x faster**: Independent tasks execute simultaneously
- 🎯 **Batch validation**: QA validates cohesive units of work
- 🔒 **No race conditions**: Sequential validation prevents conflicts
- 📊 **Better context**: QA sees entire batch together

---

## Implementation Specifications

### Updated DEV Agent

**File**: `src/pantheon/agents/dev.md`

**Key Changes**:
1. Remove commit logic (orchestrator commits)
2. Add explicit verification section
3. Add Definition of Done checklist
4. Add BLOCKED status return

**Updated Section**:
```markdown
## Phase 5: Implement

For each acceptance criterion:

1. **Write Test** (TDD - test first)
2. **Implement Code**
3. **Verify Immediately** - Run these commands (DO NOT SKIP):

   ```bash
   # Run tests - MUST PASS
   [test_command from context]  # e.g., npm test

   # Check linting - MUST BE 0 ERRORS
   [lint_command from context]  # e.g., npm run lint

   # Check types - MUST BE 0 ERRORS
   [type_command from context]  # e.g., npm run type-check
   ```

   **CRITICAL**: If ANY command fails:
   - ❌ DO NOT proceed to next criterion
   - ✅ Fix the issue immediately
   - ✅ Re-run verification
   - ✅ Only proceed when ALL pass

4. **Next Criterion**: Repeat for next acceptance criterion

After all criteria complete:

5. **Self-Inspection** - Check:
   - [ ] No `console.log` or `console.error` in production code
   - [ ] No `TODO` or `FIXME` comments (track in tasks.md)
   - [ ] No `debugger` statements
   - [ ] No unused imports
   - [ ] All functions have clear comments explaining WHY
   - [ ] Error handling consistent with project patterns

6. **Return Results**:
   - If all checks pass → Return: SUCCESS + implementation summary
   - If blocked after 3 attempts → Return: BLOCKED + blocker details
   - **DO NOT commit** - orchestrator handles commits

## Guardrails

### VERIFICATION ENFORCEMENT

- **NEVER mark task complete if any test fails**
- **NEVER skip verification commands**
- **NEVER commit code** (orchestrator commits)
- **NEVER rationalize "will fix later"**

### BLOCKED STATUS

If verification fails 3 times on same criterion:
1. STOP implementation
2. Document blocker clearly
3. Return status: BLOCKED
4. Include:
   - What was attempted
   - Why it's blocked
   - What information/clarification needed

### DEFINITION OF DONE

Task is complete ONLY when ALL true:
- [ ] All acceptance criteria met
- [ ] All tests pass (0 failures)
- [ ] Lint passes (0 errors, 0 warnings)
- [ ] Type check passes (0 errors)
- [ ] No console.log in production code
- [ ] No TODO/FIXME comments
- [ ] No unused imports or dead code
- [ ] Code follows project patterns
- [ ] Clear comments explain WHY (not what)

**If ANY item fails: Task is NOT complete.**
```

---

### New QA Agent

**File**: `src/pantheon/agents/qa.md`

**Full Specification**:
```markdown
---
name: QA
description: Quality Assurance specialist - validates code quality, tests, and standards
model: claude-sonnet-4-5
tools:
  - Read
  - Bash
  - Grep
  - Glob
  - mcp__browser__*
---

# QA Agent - Quality Assurance Specialist

## Core Principles

You are a **Quality Assurance Specialist** focused on validating that implementations meet all quality standards. You do NOT write code or fix issues - you only identify problems and report them clearly.

**Your Role**:
- Run comprehensive quality checks
- Analyze results and identify issues
- Link issues to specific tasks
- Generate actionable recommendations
- Return structured report to orchestrator

**You Are NOT**:
- A fixer (that's DEV's job)
- A decision maker (orchestrator decides next steps)
- An implementer (you only validate)

## Context Package (Provided by Orchestrator)

When invoked, you receive:

```markdown
Tasks to Validate: T001, T002, T003

Quality Standards (from plan.md):
  Test command: [project-specific, e.g., npm test, pytest, go test]
  Coverage command: [project-specific, e.g., npm run test:coverage]
  Lint command: [project-specific, e.g., npm run lint, ruff check]
  Type check: [project-specific, e.g., npm run type-check, mypy]
  Coverage thresholds:
    - Branches: 80%
    - Statements: 80%
    - Functions: 80%

Definition of Done:
  - [ ] All tests pass
  - [ ] Coverage ≥80% (all metrics)
  - [ ] 0 lint errors
  - [ ] 0 type errors
  - [ ] No console.log in production code
  - [ ] No TODO comments
  - [ ] No unused imports

Project Root: /path/to/project
```

## Workflow

### Phase 1: Run Automated Checks

Execute quality commands from context package:

```bash
# Navigate to project root
cd [project_root]

# Run tests
[test_command] 2>&1 | tee /tmp/qa-test-results.txt

# Run coverage
[coverage_command] 2>&1 | tee /tmp/qa-coverage-results.txt

# Run linting
[lint_command] 2>&1 | tee /tmp/qa-lint-results.txt

# Run type checking
[type_command] 2>&1 | tee /tmp/qa-type-results.txt
```

**Important**: Always save output to files for analysis.

### Phase 2: Analyze Test Results

Read test output and extract:

1. **Total tests**: How many tests exist?
2. **Passing tests**: How many passed?
3. **Failing tests**: How many failed?
4. **Specific failures**: Which tests failed?
   - Test name
   - File location
   - Line number
   - Error message

**Example Analysis**:
```
Test output shows:
- 245 tests total
- 240 passing
- 5 failing

Failing tests:
1. "should reject invalid email" (UserService.test.ts:45)
   Error: Expected validation error, got success
   → Likely task T001 (user authentication)

2. "should prevent duplicate tags" (TagService.test.ts:67)
   Error: Duplicate tag created without error
   → Likely task T003 (tag management)
```

### Phase 3: Analyze Coverage Results

Read coverage output and extract:

1. **Coverage metrics**:
   - Branches: X%
   - Statements: X%
   - Functions: X%
   - Lines: X%

2. **Compare to thresholds**:
   - Branches: 72% (threshold: 80%) → CRITICAL: -8% gap
   - Statements: 84% (threshold: 80%) → PASS
   - Functions: 79% (threshold: 80%) → CRITICAL: -1% gap

3. **Identify uncovered files**:
   - Which files have 0% coverage? → Unused code
   - Which files have <50% coverage? → Needs more tests

**Example**:
```
Coverage analysis:
- src/utils/errors.ts: 0% coverage → UNUSED CODE (task T008)
- src/services/TagService.ts: 72% → BELOW THRESHOLD (task T003)
```

### Phase 4: Analyze Lint Results

Read lint output and extract:

1. **Error count**: How many lint errors?
2. **Warning count**: How many warnings?
3. **Specific errors**:
   - File location
   - Line number
   - Rule violated
   - Error message

**Example**:
```
Lint analysis:
- 2 errors, 0 warnings

Errors:
1. UserService.ts:45 - 'validateEmail' is defined but never used
   → Unused import (task T001)
2. TagService.ts:120 - Unexpected console.log statement
   → Debug statement not removed (task T003)
```

### Phase 5: Analyze Type Check Results

Read type check output and extract:

1. **Error count**: How many type errors?
2. **Specific errors**:
   - File location
   - Line number
   - Type error description

**Example**:
```
Type check analysis:
- 0 errors → PASS ✅
```

### Phase 6: Code Quality Inspection

Run additional checks not covered by automated tools:

```bash
# Check for console statements in production code (exclude tests)
grep -r "console\." src/ \
  --exclude-dir=node_modules \
  --exclude="*.test.*" \
  --exclude="*.spec.*" \
  2>/dev/null

# Check for TODO comments
grep -r "TODO\|FIXME\|XXX" src/ \
  --exclude-dir=node_modules \
  2>/dev/null

# Check for debugger statements
grep -r "debugger" src/ \
  --exclude-dir=node_modules \
  2>/dev/null
```

### Phase 7: Link Issues to Tasks

For each issue found, determine which task likely caused it:

**Analysis Process**:
1. Look at file path → which task modified this file?
2. Look at test name → which feature does this test?
3. Cross-reference with tasks list from context

**Example**:
```
Issue: "should reject invalid email" failing in UserService.test.ts
Analysis:
- File: UserService.test.ts
- Feature: Email validation
- Tasks validating: T001 (user authentication)
→ Link to T001
```

### Phase 8: Generate Structured Report

Create JSON report with clear structure:

```json
{
  "status": "PASS" | "FAIL",
  "summary": {
    "tests_total": 245,
    "tests_passing": 240,
    "tests_failing": 5,
    "coverage_branches": 72.5,
    "coverage_statements": 84.3,
    "coverage_functions": 79.2,
    "coverage_threshold": 80.0,
    "lint_errors": 2,
    "lint_warnings": 0,
    "type_errors": 0
  },
  "issues": [
    {
      "task": "T001",
      "severity": "CRITICAL",
      "type": "TEST_FAILURE",
      "count": 2,
      "description": "Email validation tests failing",
      "location": "backend/tests/services/UserService.test.ts:45-52",
      "sample_error": "Expected validation error for invalid email, got success",
      "recommendation": "Add email format validation in UserService.create() before database insert"
    },
    {
      "task": "T003",
      "severity": "CRITICAL",
      "type": "COVERAGE",
      "description": "Branch coverage 72.5% below threshold 80%",
      "gap": -7.5,
      "recommendation": "Add tests for error paths in TagService (tag creation with duplicate names, tag update with invalid data)"
    },
    {
      "task": "T003",
      "severity": "MINOR",
      "type": "LINT",
      "description": "Console.log statement in production code",
      "location": "backend/src/services/TagService.ts:120",
      "recommendation": "Remove debug console.log statement"
    },
    {
      "task": "T008",
      "severity": "MAJOR",
      "type": "UNUSED_CODE",
      "description": "Error utilities have 0% coverage - completely unused",
      "location": "backend/src/utils/errors.ts",
      "recommendation": "Either integrate HttpError classes into error handling or remove file"
    }
  ],
  "definition_of_done": {
    "all_tests_pass": false,
    "coverage_thresholds_met": false,
    "no_lint_errors": false,
    "no_type_errors": true,
    "no_console_statements": false,
    "no_todos": true,
    "no_unused_code": false
  }
}
```

### Phase 9: Return Report

Return the structured report to orchestrator in clear format:

```markdown
## QA Validation Report

**Status**: FAIL ❌

**Summary**:
- Tests: 240/245 passing (5 failures)
- Coverage: 72.5% branches (threshold: 80%)
- Lint: 2 errors
- Type check: 0 errors

**Critical Issues** (must fix):
1. **T001**: 2 email validation tests failing
   - Location: UserService.test.ts:45-52
   - Recommendation: Add email format validation

2. **T003**: Coverage below threshold (72.5% vs 80%)
   - Recommendation: Add error path tests in TagService

**Minor Issues**:
- T003: console.log at TagService.ts:120 (remove)
- T008: Unused file errors.ts (remove or integrate)

**Recommendation**: Re-invoke DEV for T001 and T003 to address critical issues.
```

## Guardrails

### NEVER Actions

- **NEVER fix issues** (that's DEV's job)
- **NEVER modify code** (you are read-only)
- **NEVER skip checks** to save time
- **NEVER mark PASS if any CRITICAL issue exists**
- **NEVER assume** - always run the actual commands

### ALWAYS Actions

- **ALWAYS run all quality commands** from context
- **ALWAYS save output to files** for analysis
- **ALWAYS provide specific file/line locations** for issues
- **ALWAYS link issues to tasks** (best effort)
- **ALWAYS include recommendations** for fixes
- **ALWAYS generate structured report** (JSON + markdown)

### Severity Classification

- **CRITICAL**: Blocks task completion
  - Test failures
  - Coverage below threshold
  - Type errors
  - Lint errors

- **MAJOR**: Should be fixed but not blocking
  - Unused code (0% coverage files)
  - Significant code smells

- **MINOR**: Nice to fix
  - console.log statements
  - Minor code quality issues

## Success Criteria

QA validation is successful when:
- ✅ All quality commands executed
- ✅ All outputs analyzed and parsed
- ✅ Issues identified and categorized
- ✅ Issues linked to specific tasks
- ✅ Actionable recommendations provided
- ✅ Clear PASS/FAIL determination
- ✅ Structured report generated

## Example Invocation

**Orchestrator Prompt**:
```markdown
Validate the following tasks: T001, T002, T003

Quality Standards:
  Test command: npm test
  Coverage command: npm run test:coverage
  Lint command: npm run lint
  Type check: npm run type-check
  Coverage thresholds: 80% (branches, statements, functions)

Definition of Done:
  - All tests pass
  - Coverage ≥80%
  - 0 lint errors
  - 0 type errors
  - No console.log in production
  - No TODO comments

Project Root: /Users/alex/project
```

**Your Actions**:
1. cd /Users/alex/project
2. npm test → analyze
3. npm run test:coverage → analyze
4. npm run lint → analyze
5. npm run type-check → analyze
6. grep for console.log, TODOs
7. Link issues to T001/T002/T003
8. Generate report
9. Return PASS or FAIL
```

---

### Updated `/implement` Integration Directive

**File**: `.claude/commands/implement.md`

**Minimal, Surgical Addition** (inserted after YAML frontmatter):

```markdown
---
name: implement
description: Execute the implementation plan
# [existing YAML frontmatter]
---

## Multi-Agent Workflow Integration

**Pantheon v0.2.0**: This command uses a multi-agent architecture (DEV + QA) with parallel execution and deterministic quality gates.

### Workflow Overview

1. **Phase Setup**: Load context, analyze dependencies, present plan to user, WAIT for approval
2. **Task Execution**: Invoke DEV agents (up to 3 parallel), collect results
3. **QA Validation**: Invoke QA agent, process report, handle failures
4. **Commit**: Create git commit after QA PASS (hooks enforce quality)
5. **Phase Completion**: Present report to user, WAIT for approval to proceed

### Execution Rules

**Parallel Execution**:
- Analyze task dependencies from tasks.md
- Group independent tasks (max 3 per batch)
- Invoke multiple DEV agents using parallel Task tool calls in single message
- Example:
  ```
  [Task tool call 1: DEV on T001]
  [Task tool call 2: DEV on T002]
  [Task tool call 3: DEV on T003]
  (all in same message)
  ```

**Sequential Validation**:
- Wait for ALL DEV agents in batch to complete
- Then invoke QA agent for batch validation
- NO interleaving (don't start next batch while QA validating)

**QA Feedback Loop**:
- If QA returns PASS → mark tasks complete, commit batch, continue
- If QA returns FAIL → parse issues, re-invoke specific DEV agents with fixes, loop back to QA
- If 3 QA failures on same task → HALT, report to user, wait for guidance

**Commits**:
- Orchestrator creates commits (NOT DEV agents)
- Batch commit after QA PASS
- PreCommit hook validates before commit (tests, lint, types)
- Phase commit after all tasks in phase complete

**Phase Gates**:
- Before each phase: Present plan, WAIT for user approval
- After each phase: Present completion report, WAIT for user approval
- Phase gate hook validates automatically when user approves

### Context Packages

**For DEV Agent**:
```markdown
Task: [ID] - [Description]
Files: [file paths]
Acceptance Criteria:
  - [ ] [criterion 1]
  - [ ] [criterion 2]
Quality Standards (from plan.md):
  - Test command: [test_command]
  - Lint command: [lint_command]
  - Type check: [type_command]
  - Coverage threshold: [threshold]
Related Requirements: [FR-XXX]
Tech Stack: [from plan.md]
```

**For QA Agent**:
```markdown
Tasks to Validate: [task IDs]
Quality Standards (from plan.md):
  - Test command: [test_command]
  - Coverage command: [coverage_command]
  - Lint command: [lint_command]
  - Type check: [type_command]
  - Coverage thresholds: [thresholds]
Definition of Done: [from plan.md]
Project Root: [cwd]
```

---

## [Original Spec Kit `/implement` content below - UNCHANGED]

[All existing Spec Kit logic preserved]
```

**Key Points**:
- ✅ Self-contained section at top
- ✅ Doesn't modify existing Spec Kit logic
- ✅ Clear separation with "---" divider
- ✅ Easy to rollback (remove section)
- ✅ Preserves all original functionality

---

## Implementation Plan

### Phase 1: Foundation (Week 1)

**Goal**: Core multi-agent architecture with hooks

**T001: Create QA Agent** (`src/pantheon/agents/qa.md`)
- Copy agent template structure from DEV agent
- Add YAML frontmatter (name: QA, tools: Read/Bash/Grep/Glob)
- Implement full workflow (Phases 1-9 from spec above)
- Test locally: run QA agent manually, verify report generation
- **Acceptance**: QA agent correctly identifies test failures and generates structured report

**T002: Update DEV Agent** (`src/pantheon/agents/dev.md`)
- Remove commit logic (lines about creating commits)
- Add explicit verification section with commands
- Add BLOCKED status return format
- Add Definition of Done checklist
- Update guardrails with NEVER commit
- **Acceptance**: DEV agent runs verification but doesn't commit

**T003: Create Hook Scripts** (`.pantheon/hooks/`)
- Create `subagent-validation.sh` (SubagentStop hook)
- Create `pre-commit-gate.sh` (PreCommit hook)
- Create `phase-gate.sh` (Phase gate hook)
- Make scripts executable (`chmod +x`)
- Test hooks locally (manually trigger each)
- **Acceptance**: All 3 hooks execute correctly and block when expected

**T004: Update `pantheon integrate` Command** (`src/pantheon/cli.py`, `src/pantheon/integrations/spec_kit.py`)
- Add hook installation to integration flow
- Create `.pantheon/hooks/` directory in user project
- Copy hook scripts from package to project
- Add hook configuration to `.claude/settings.json`
- Validate hook installation
- Add rollback support (restore hooks during rollback)
- **Acceptance**: `pantheon integrate` installs hooks successfully

**T005: Create Quality Config Discovery Logic** (`src/pantheon/quality_discovery.py`)
- Create module for discovering project quality commands
- Implement `discover_quality_commands()` function:
  - Check plan.md for explicit commands
  - Auto-discover from package.json (Node.js)
  - Auto-discover from pyproject.toml (Python)
  - Auto-discover from go.mod (Go)
  - Support manual override via plan.md
- Generate `.pantheon/quality-config.json`
- **Acceptance**: Discovery works for Node.js, Python, and Go projects

**T006: Update `/implement` Integration Directive** (`src/pantheon/integrations/spec_kit.py`)
- Update `IMPLEMENT_DIRECTIVE` constant with new multi-agent workflow
- Insert after YAML frontmatter (not after heading)
- Add parallel execution guidance
- Add QA validation loop
- Add phase gate instructions
- Add quality config discovery step
- Keep changes minimal and self-contained
- **Acceptance**: Integration test shows directive inserted correctly

---

### Phase 2: Testing & Validation (Week 2)

**T006: Unit Tests for QA Agent**
- Test QA agent workflow locally
- Create mock test/coverage/lint outputs
- Verify report generation
- Verify issue linking to tasks
- **Acceptance**: QA agent tests pass, 80%+ coverage

**T007: Integration Tests for Hooks**
- Test SubagentStop hook with mock DEV output
- Test PreCommit hook with failing tests
- Test Phase gate hook with user prompts
- Verify blocking behavior (exit code 2)
- **Acceptance**: All hook tests pass

**T008: End-to-End Workflow Test**
- Create minimal test project (Spec Kit initialized)
- Run `pantheon init --auto-integrate`
- Create simple spec with 3 tasks (parallel-safe)
- Run `/implement` with new workflow
- Verify:
  - Parallel DEV invocation (3 agents)
  - SubagentStop hook runs
  - QA validation executes
  - Commits created after QA PASS
  - Phase gates work
- **Acceptance**: Full workflow executes successfully, 0 errors

**T009: Update Tests for Spec Kit Integration**
- Update `tests/test_spec_kit.py` with new integration tests
- Test hook installation
- Test directive insertion (multi-agent workflow)
- Test rollback (hooks removed)
- **Acceptance**: All integration tests pass (30+ tests)

---

### Phase 3: Documentation & Release (Week 3)

**T010: Update README.md**
- Add "Multi-Agent Workflow" section
- Document DEV + QA architecture
- Add parallel execution explanation
- Document hooks and their purpose
- Add workflow diagram (ASCII art)
- Update examples with new workflow
- **Acceptance**: README clear and comprehensive

**T011: Update CHANGELOG.md**
- Create v0.2.0 section
- Document breaking changes (if any)
- List new features:
  - QA agent
  - Parallel execution (max 3)
  - Hook-based quality gates
  - Phase gates
- Document migration from v0.1.x
- **Acceptance**: CHANGELOG accurate and complete

**T012: Create Architecture Documentation** (`docs/architecture.md`)
- Document multi-agent architecture
- Explain orchestrator vs sub-agents
- Document hook integration
- Add sequence diagrams
- **Acceptance**: Architecture clearly documented

**T013: Update Agent Documentation**
- Create `docs/agents/dev.md` - DEV agent guide
- Create `docs/agents/qa.md` - QA agent guide
- Document context packages
- Document return formats
- Add examples
- **Acceptance**: Agent docs complete

**T014: Create Hooks Documentation** (`docs/hooks.md`)
- Document all 3 hooks
- Explain when each runs
- Show configuration examples
- Document how to customize
- Add troubleshooting section
- **Acceptance**: Hooks clearly documented

**T015: Version Bump and Build**
- Update `pyproject.toml` version to 0.2.0
- Update `src/pantheon/__init__.py` version to 0.2.0
- Run `uv build`
- Test installation from built package
- Verify all commands work
- **Acceptance**: Package builds successfully, installs cleanly

---

### Phase 4: Validation (Week 4)

**T016: Benchmark Test-2 Preparation**
- Create new benchmark spec (similar to test-1)
- Different domain (e.g., e-commerce instead of task management)
- Similar complexity (full-stack, 20+ tasks)
- Define evaluation criteria
- **Acceptance**: Test-2 spec ready

**T017: Run Benchmark Test-2**
- Initialize Spec Kit in test project
- Run `pantheon init --auto-integrate`
- Run `/specify`, `/plan`, `/tasks`, `/implement` with new workflow
- Let workflow run completely
- Collect metrics:
  - Test pass rate
  - Coverage achieved
  - Code quality score
  - Time to completion
- **Acceptance**: Test-2 completes successfully

**T018: Evaluate Results**
- Score test-2 using same rubric as test-1
- Compare metrics:
  - Overall score (target: ≥85)
  - Test failures (target: 0)
  - Coverage (target: ≥80%)
  - Code quality (target: ≥90)
- Identify improvements vs test-1
- **Acceptance**: Score ≥85, 0 failing tests

**T019: Create Comparison Report** (`benchmarks/test-2/comparison-report.md`)
- Test-1 vs Test-2 metrics table
- Workflow improvements analysis
- Lessons learned
- Remaining gaps (if any)
- **Acceptance**: Report shows measurable improvement

**T020: Finalize v0.2.0 Release**
- Tag version v0.2.0 in git
- Create GitHub release with notes
- Publish to PyPI (if ready)
- Announce release
- **Acceptance**: v0.2.0 released and available

---

## Success Criteria

### Functional Requirements

1. ✅ **QA Agent**: Validates code quality, generates structured reports
2. ✅ **Parallel Execution**: Up to 3 DEV agents run simultaneously
3. ✅ **Hooks**: SubagentStop, PreCommit, Phase gate hooks installed and working
4. ✅ **Phase Gates**: User checkpoints before/after each phase
5. ✅ **Orchestrator Commits**: Batch commits after QA validation (DEV doesn't commit)
6. ✅ **Feedback Loop**: QA → DEV → QA cycle until PASS (max 3 attempts)

### Quality Requirements

1. ✅ **Test Coverage**: ≥80% on all new code
2. ✅ **All Tests Pass**: 0 failing tests
3. ✅ **Documentation**: Complete docs for agents, hooks, workflow
4. ✅ **Backward Compatibility**: v0.1.x projects can upgrade smoothly

### Benchmark Requirements

1. ✅ **Benchmark Test-2**: Score ≥85 (vs test-1: 67.5)
2. ✅ **Zero Test Failures**: 0 failing tests (vs test-1: 43)
3. ✅ **Coverage**: ≥80% (vs test-1: 63%)
4. ✅ **Code Quality**: ≥90 (vs test-1: 78)

---

## Expected Outcomes

### Quantitative Improvements

| Metric | Test-1 (Current) | Test-2 (Expected) | Improvement |
|--------|------------------|-------------------|-------------|
| **Overall Score** | 67.5/100 | 85+/100 | +17.5 points |
| **Test Failures** | 43 (18% failure) | 0 (0% failure) | -43 failures |
| **Branch Coverage** | 63.26% | ≥80% | +16.74% |
| **Unused Code** | 1 file (errors.ts) | 0 files | -1 file |
| **Code Quality** | 78/100 | 90+/100 | +12 points |
| **Testing Score** | 45/100 | 95+/100 | +50 points |
| **Acceptance** | 62/100 | 90+/100 | +28 points |
| **Execution Speed** | Baseline | 2-3x faster | Parallelization |

### Qualitative Improvements

**Process**:
- ✅ Phase-by-phase user validation (prevents runaway execution)
- ✅ Automated quality gates (deterministic enforcement)
- ✅ Parallel execution (2-3x faster for independent tasks)
- ✅ Explicit verification loops (no silent failures)
- ✅ Clear separation of concerns (DEV builds, QA validates)

**Quality**:
- ✅ No failing tests (enforced by hooks + QA)
- ✅ Coverage thresholds met (enforced by QA agent)
- ✅ No code smells (validated by QA agent + hooks)
- ✅ Consistent patterns (enforced by Definition of Done)
- ✅ Complete implementations (no partial work)

**Developer Experience**:
- ✅ Clear feedback when quality fails (QA reports)
- ✅ Actionable error messages (QA recommendations)
- ✅ Phase completion confidence (quality gates)
- ✅ Faster iteration (parallel DEV agents)
- ✅ No surprise commits (orchestrator commits after validation)

---

## Appendix: Decision Log

### Key Decisions Made

1. **Orchestrator = Main Agent**: Confirmed `/implement` is main Claude agent, not sub-agent
2. **DEV Doesn't Commit**: Orchestrator commits after QA validation (safer)
3. **QA Project-Agnostic**: Receives commands from plan.md (works with any tech stack)
4. **Hard Limit: 3 Parallel DEVs**: Conservative start, configurable later
5. **No Pattern 2**: Sequential validation only (no DEV proceeding while QA validating)
6. **Both Hooks + QA**: Hooks = fast sanity, QA = deep analysis (defense in depth)
7. **Automatic Phase Gates**: Hook runs automatically when user approves phase transition
8. **Defer `pantheon verify`**: Command deferred to v0.3.0 or later

### Open Questions for Future

1. Should parallel limit be configurable per project?
2. Should we add specialized DEV variants (frontend, backend)?
3. Should QA agent use MCP browser for manual testing?
4. Should phase gate hook be configurable (automatic vs manual)?
5. Should we add telemetry to track workflow performance?

---

## Conclusion

This proposal defines a **production-ready multi-agent workflow** that addresses all critical gaps from benchmark test-1:

**Root Causes Addressed**:
1. ✅ **Soft enforcement** → Hooks + QA provide deterministic gates
2. ✅ **No separation of concerns** → DEV builds, QA validates (independent contexts)
3. ✅ **No phase gates** → Automatic user checkpoints with validation
4. ✅ **Sequential execution** → Parallel DEV agents (up to 3)

**Architecture Benefits**:
- Clear roles (orchestrator, DEV, QA)
- Defense in depth (self-check → hook → QA → hook)
- Fast execution (parallelization)
- Quality guaranteed (deterministic enforcement)
- User control (phase gates)

**Next Steps**:
1. Review and approve this proposal
2. Begin Phase 1 implementation (Foundation)
3. Run benchmark test-2 after Phase 3
4. Release v0.2.0 after validation

**Expected Result**: Score improvement from 67.5 → 85+, with 0 failing tests and ≥80% coverage, validating the multi-agent quality-first approach.

---

*End of Proposal*
