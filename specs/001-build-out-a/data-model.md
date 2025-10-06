# Data Model: Multi-Agent Quality-First Workflow

**Feature**: Multi-Agent Quality-First Workflow (Pantheon v0.2.0)
**Branch**: 001-build-out-a
**Date**: 2025-10-06

---

## Overview

This feature introduces several new data structures for quality configuration, hook management, agent context packages, and QA reports. The data model is intentionally simple and file-based (JSON/Markdown) to maintain the KISS principle.

---

## Entity: Quality Config

**Location**: `.pantheon/quality-config.json` (created in user project)

**Purpose**: Single source of truth for project-specific quality commands

**Schema**:
```json
{
  "version": "1.0",
  "project_type": "python" | "node" | "go" | "ruby" | "other",
  "commands": {
    "test": "pytest tests/",
    "lint": "ruff check src/ tests/",
    "type_check": "mypy src/",
    "coverage": "pytest --cov=src --cov-report=term-missing",
    "build": "python -m build"
  },
  "thresholds": {
    "coverage_branches": 80,
    "coverage_statements": 80
  },
  "discovery_source": "plan.md" | "auto" | "manual"
}
```

**Fields**:
- `version`: Config schema version (for future migrations)
- `project_type`: Detected project type (informational)
- `commands`: Quality commands discovered or specified
  - Any command can be empty string if not applicable
- `thresholds`: Coverage requirements
- `discovery_source`: How commands were determined

**Relationships**:
- Created by: Quality discovery module (during `/constitution`)
- Read by: All agents (DEV, QA), all hooks (SubagentStop, PreCommit, Phase Gate)

**Validation Rules**:
- Must be valid JSON
- `version` must be present and match expected format
- `commands` object must exist (can have empty values)
- `thresholds` values must be 0-100

**State Transitions**:
```
[Not Exists] → [Created] (on first `/constitution` run)
[Created] → [Updated] (on subsequent `/constitution` runs)
```

---

## Entity: Hook Configuration

**Location**: `.claude/settings.json` (updated by `pantheon integrate`)

**Purpose**: Configure Claude Code hooks for quality gates

**Schema** (partial - only hooks section):
```json
{
  "hooks": {
    "SubagentStop": ".pantheon/hooks/subagent-validation.sh",
    "PreCommit": ".pantheon/hooks/pre-commit-gate.sh",
    "UserPromptSubmit": ".pantheon/hooks/phase-gate.sh"
  }
}
```

**Fields**:
- `SubagentStop`: Path to validation hook (runs when agents complete)
- `PreCommit`: Path to commit gate hook (runs before commits)
- `UserPromptSubmit`: Path to phase gate hook (runs on user messages)

**Relationships**:
- Created/updated by: `pantheon integrate` command
- Read by: Claude Code runtime
- References: Hook script files in `.pantheon/hooks/`

**Validation Rules**:
- Must be valid JSON
- Hook paths must point to executable files
- Files must have execute permission (chmod +x)

**State Transitions**:
```
[Not Configured] → [Configured] (on `pantheon integrate`)
[Configured] → [Not Configured] (on `pantheon rollback`)
```

---

## Entity: DEV Agent Context Package

**Format**: Markdown text (passed via Task tool prompt parameter)

**Purpose**: Provide complete context to DEV agent for stateless task execution

**Structure**:
```markdown
# Task Context: T001

## Task Details
**ID**: T001
**Description**: Implement quality discovery module
**Files**: src/pantheon/quality/discovery.py, tests/unit/test_discovery.py

## Acceptance Criteria
- [ ] Detect project type from file structure (package.json, pyproject.toml, go.mod)
- [ ] Parse plan.md for explicit quality commands
- [ ] Auto-discover commands if not in plan.md
- [ ] Return QualityConfig object with all commands
- [ ] Handle projects with no discoverable commands (empty strings)

## Quality Standards
**Test Command**: pytest tests/unit/test_discovery.py -v
**Lint Command**: ruff check src/pantheon/quality/
**Type Command**: mypy src/pantheon/quality/
**Coverage Threshold**: 80% branches

## Related Requirements
- FR-050: Project-agnostic quality discovery
- FR-051: Check plan.md first
- FR-052: Auto-discover from project files
- FR-053: Create .pantheon/quality-config.json

## Tech Stack
**Language**: Python 3.9+
**Patterns**: Use existing file reading utilities, JSON serialization
**Testing**: pytest with mocks for file system access

## Constitution
- Principle III: TDD mandatory
- Principle V: Keep it simple (no complex heuristics)
```

**Relationships**:
- Created by: Orchestrator (main Claude agent)
- Consumed by: DEV agent sub-agent
- Based on: tasks.md (task details), plan.md (quality standards), spec.md (requirements)

**Validation**: Informal (orchestrator assembles from validated sources)

---

## Entity: QA Agent Context Package

**Format**: Markdown text (passed via Task tool prompt parameter)

**Purpose**: Provide validation context to QA agent

**Structure**:
```markdown
# QA Validation Context

## Tasks to Validate
- **T001**: Implement quality discovery module
  - Files: src/pantheon/quality/discovery.py, tests/unit/test_discovery.py
- **T002**: Create quality config generation
  - Files: src/pantheon/quality/config.py, tests/unit/test_config.py

## Quality Standards
**Test Command**: pytest tests/unit/ -v
**Coverage Command**: pytest tests/unit/ --cov=src/pantheon/quality --cov-report=term-missing
**Coverage Threshold**: 80% branches
**Lint Command**: ruff check src/pantheon/quality/ tests/unit/
**Type Command**: mypy src/pantheon/quality/

## Definition of Done
- [ ] All tests pass (0 failures)
- [ ] Coverage ≥80% branches
- [ ] No linting errors (ruff)
- [ ] No type errors (mypy)
- [ ] No code smells (console.log/print in non-CLI, TODO comments, unused imports)
- [ ] Manual testing passed (if functional changes)

## Project Root
/Users/alexabrams/Workspace/pantheon

## Manual Testing Required
YES - These are new modules that affect CLI behavior
**Frontend**: N/A (no frontend)
**Backend**: Run `pantheon integrate` and verify hooks installed correctly
```

**Relationships**:
- Created by: Orchestrator
- Consumed by: QA agent sub-agent
- Based on: Batch of completed tasks, quality-config.json, plan.md

**Validation**: Informal (orchestrator assembles)

---

## Entity: QA Report

**Format**: Markdown document (returned by QA agent to orchestrator)

**Purpose**: Structured validation results for orchestrator decisions

**Schema**:
```markdown
# QA Validation Report

**Status**: PASS | FAIL
**Batch**: [Task IDs]
**Date**: [ISO 8601 timestamp]
**Duration**: [seconds]

## Summary Metrics
- **Tests**: [total] total, [passing] passing, [failing] failing
- **Coverage**: [percentage]% branches (threshold: [threshold]%) [✓ or ✗]
- **Lint**: [count] errors [✓ or ✗]
- **Type**: [count] errors [✓ or ✗]
- **Code Smells**: [count] found [✓ or ✗]
- **Manual Testing**: PASS | FAIL | SKIPPED

## Issues
[If PASS, state "No issues found."]
[If FAIL, list issues grouped by severity:]

### CRITICAL
[Issues that block PASS status]
- **[Task ID]**: [Issue description]
  - Location: [file:line]
  - Error: [specific error message]
  - Recommendation: [actionable fix]

### MAJOR
[Issues that should be fixed but don't block]

### MINOR
[Nice-to-have fixes]

## Definition of Done
- [x] All tests pass
- [ ] Coverage meets threshold
- [x] No linting errors
- [x] No type errors
- [x] No code smells
- [x] Manual testing passed

## Recommendations
1. [Specific action for orchestrator/DEV agents]
2. [...]

## Detailed Results
[Optional: Full test output, coverage report, etc.]
```

**Fields**:
- `Status`: PASS (all checks passed) or FAIL (one or more CRITICAL issues)
- `Batch`: List of task IDs validated
- `Summary Metrics`: Quick overview of all quality dimensions
- `Issues`: Categorized problems with specific locations and fixes
- `Definition of Done`: Checklist showing what passed/failed
- `Recommendations`: Actionable next steps
- `Detailed Results`: Optional full output for debugging

**Relationships**:
- Created by: QA agent
- Consumed by: Orchestrator
- Influences: Next actions (commit vs rework)

**Validation Rules**:
- Status must be PASS or FAIL
- PASS requires all Definition of Done items checked
- CRITICAL issues must be present if Status is FAIL
- Each issue must have: task ID, description, location, recommendation

**State Transitions**:
```
[Generated] → [Processed by Orchestrator]
  ↓ if PASS
  [Tasks Marked Complete] → [Commit Created]
  ↓ if FAIL
  [DEV Agents Re-invoked] → [New QA Report Generated]
```

---

## Entity: Phase Plan

**Format**: Markdown document (generated by orchestrator)

**Purpose**: Pre-phase checkpoint for user approval

**Schema**:
```markdown
# Phase [N] Plan: [Phase Name]

**Objective**: [Phase goal]
**Tasks**: [Count] tasks ([independent] independent, [dependent] dependent)
**Estimated Duration**: [minutes]

## Task List
- **T001**: [Description] ([files]) [Dependencies: None | Task IDs]
- **T002**: [Description] ([files]) [Dependencies: T001]
- ...

## Parallelization Strategy
**Batch 1** (parallel): T001, T003, T005 (3 DEV agents)
**Batch 2** (parallel): T002, T004 (2 DEV agents - T001 dependency met)
**Batch 3** (sequential): T006 (depends on T002, T004)

## Quality Standards
- Test: [command]
- Lint: [command]
- Type: [command]
- Coverage: [threshold]%

## Approval Required
Type 'yes' to proceed, 'review' to pause, or 'no' to halt.
```

**Relationships**:
- Created by: Orchestrator
- Consumed by: User (for decision)
- Based on: tasks.md

**Validation**: Informal (orchestrator generates)

---

## Entity: Phase Completion Report

**Format**: Markdown document (generated by orchestrator)

**Purpose**: Post-phase checkpoint for user approval

**Schema**:
```markdown
# Phase [N] Complete: [Phase Name]

**Completed**: [ISO 8601 timestamp]
**Duration**: [minutes]
**Tasks**: [Count] completed

## Tasks Completed
- **T001**: [Description] ✓
- **T002**: [Description] ✓
- ...

## Quality Metrics
- Tests: [passing]/[total] passing (100%)
- Coverage: [percentage]% branches (≥[threshold]%)
- Lint: 0 errors
- Type: 0 errors
- Code Smells: 0 found

## Git Commits
- `[hash]` - [commit message]
- `[hash]` - [commit message]

## Phase Statistics
- DEV agents invoked: [count]
- QA validations: [count]
- Rework cycles: [count]
- Average task duration: [minutes]

## Approval Required
Type 'yes' to proceed to Phase [N+1], 'review' to pause, or 'no' to halt.
```

**Relationships**:
- Created by: Orchestrator
- Consumed by: User (for decision), Phase Gate hook (for validation)

---

## Summary

**New Entities**: 7 data structures
- Quality Config (JSON file)
- Hook Configuration (JSON in settings.json)
- DEV Context Package (Markdown)
- QA Context Package (Markdown)
- QA Report (Markdown)
- Phase Plan (Markdown)
- Phase Completion Report (Markdown)

**Key Characteristics**:
- Simple formats (JSON, Markdown)
- File-based (no database)
- Stateless (all context provided explicitly)
- Single source of truth (quality-config.json)
- Structured but human-readable

**Relationships**:
```
Quality Config ←─ read by ─── DEV/QA Agents, Hooks
Hook Configuration ←─ read by ─── Claude Code Runtime
DEV Context Package ─→ consumed by ─→ DEV Agent ─→ generates code
QA Context Package ─→ consumed by ─→ QA Agent ─→ generates QA Report
QA Report ─→ consumed by ─→ Orchestrator ─→ decides commit/rework
Phase Plan ─→ consumed by ─→ User ─→ approves/rejects
Phase Completion Report ─→ consumed by ─→ User + Phase Gate Hook
```

All entities follow constitution principles: simple, stateless, single-responsibility, file-based.
