# Pantheon Architecture

**Purpose**: Comprehensive architectural documentation for developers
**Audience**: Contributors, maintainers, architects

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Multi-Agent Workflow](#multi-agent-workflow)
4. [Data Model](#data-model)
5. [Integration System](#integration-system)
6. [Quality Hooks](#quality-hooks)
7. [Design Decisions](#design-decisions)

---

## System Overview

Pantheon is a **quality-focused agents library for Claude Code** that implements a multi-agent architecture with enforced quality gates. The system enables developers to implement features with guaranteed quality through independent validation, parallel execution, and deterministic enforcement.

### Architecture Principles

1. **Separation of Concerns**: Orchestrator coordinates, DEV implements, QA validates
2. **Defense in Depth**: Multiple quality gates (self-check → hook → QA → hook)
3. **Stateless Sub-Agents**: Each invocation is fresh; orchestrator manages state
4. **Hook-Based Enforcement**: Quality gates enforced automatically, not just documented
5. **KISS (Keep It Simple)**: Minimal directives over complex rewrites

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Claude Code Main Agent (Orchestrator)                      │
│  - Loads context (spec.md, plan.md, tasks.md)              │
│  - Analyzes dependencies and parallelization strategy      │
│  - Invokes DEV/QA sub-agents via Task tool                 │
│  - Creates commits after QA validation + user approval     │
│  - Enforces phase gates with user checkpoints              │
└─────────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    ┌────────┐      ┌────────┐      ┌────────┐
    │  DEV   │      │  DEV   │      │  DEV   │
    │ Agent  │      │ Agent  │      │ Agent  │
    │ (T001) │      │ (T002) │      │ (T003) │
    └────────┘      └────────┘      └────────┘
        │                │                │
        └────────────────┼────────────────┘
                         ▼
            ┌─────────────────────────┐
            │ SubagentStop Hook       │
            │ - Validates quality     │
            │ - Blocks if issues      │
            └─────────────────────────┘
                         │
                         ▼
            ┌─────────────────────────┐
            │  QA Agent               │
            │  - Runs all checks      │
            │  - Generates report     │
            │  - Returns PASS/FAIL    │
            └─────────────────────────┘
                         │
                ┌────────┴────────┐
                ▼                 ▼
            [PASS]            [FAIL]
                │                 │
                ▼                 └──→ Re-invoke DEV with fixes
        ┌──────────────┐
        │ PreCommit    │
        │ Hook         │
        │ - Final gate │
        └──────────────┘
                │
                ▼
          Git Commit Created
```

---

## Core Components

### 1. Sub-Agents

**What Are Sub-Agents?**

Sub-agents are specialized AI assistants within Claude Code that:
- Operate in **separate context windows** (preserves main conversation)
- Handle **specific types of tasks** with focused expertise
- Are **stateless** (no memory between invocations)
- Receive **context packages** from orchestrator with all needed information

**Agent Lifecycle**:
```
1. Orchestrator prepares context package
2. Orchestrator invokes sub-agent via Task tool
3. Sub-agent executes in separate context window
4. SubagentStop hook validates work before completion
5. Sub-agent returns results to orchestrator
6. Orchestrator processes results and continues workflow
```

#### DEV Agent

**Location**: `src/pantheon/agents/dev.md`

**Purpose**: Implementation specialist focused on quality-first development

**Responsibilities**:
- Receive task + context package from orchestrator
- Implement code following TDD (test-first)
- Write comprehensive tests
- Run verification (tests, lint, type-check)
- Self-check against acceptance criteria
- Return SUCCESS or BLOCKED status

**Tools Available**: Read, Write, Edit, Bash, Glob, Grep, Browser MCP

**Constraints**:
- ❌ Cannot commit code (orchestrator handles commits)
- ❌ Cannot skip quality checks
- ❌ Cannot mark task complete with failing tests
- ✅ Can return BLOCKED if needs clarification (max 3 attempts)

**Key Workflow**:
```markdown
For each acceptance criterion:
1. Write test (TDD)
2. Implement code
3. Run verification (test + lint + type-check)
4. If fails → fix immediately, re-verify
5. If passes → next criterion

After all criteria:
- Self-inspection (no console.log, TODO, debugger)
- Return SUCCESS to orchestrator
```

#### QA Agent

**Location**: `src/pantheon/agents/qa.md`

**Purpose**: Validation specialist focused on comprehensive quality verification

**Responsibilities**:
- Receive batch of tasks from orchestrator
- Run full test suite
- Analyze test results, coverage, lint, type errors
- Search for code smells
- Perform manual testing (frontend/backend)
- Link issues to specific tasks
- Generate structured PASS/FAIL report

**Tools Available**: Read, Bash, Grep, Glob, Browser MCP, Playwright MCP

**Constraints**:
- ❌ Cannot fix issues (read-only)
- ❌ Cannot modify code
- ❌ Cannot mark PASS with any critical issues
- ✅ Must provide specific file/line locations
- ✅ Must include actionable recommendations

**Report Structure**:
```json
{
  "status": "PASS" | "FAIL",
  "summary": { "tests_total": 245, "tests_passing": 245, ... },
  "issues": [
    {
      "task": "T001",
      "severity": "CRITICAL",
      "type": "TEST_FAILURE",
      "description": "...",
      "location": "file.ts:45",
      "recommendation": "..."
    }
  ],
  "definition_of_done": { "all_tests_pass": true, ... }
}
```

### 2. Orchestrator (Main Agent)

**Identity**: The main Claude Code agent executing commands like `/implement`

**Responsibilities**:
- Load context (spec.md, plan.md, tasks.md)
- Analyze task dependencies
- Group independent tasks for parallel execution (max 3)
- Invoke DEV sub-agents (parallel or sequential)
- Collect DEV results and handle BLOCKED status
- Invoke QA sub-agent for batch validation
- Process QA reports and re-invoke DEV if FAIL
- Create git commits after QA PASS + user approval
- Enforce phase gates (present plan → wait → execute → present report → wait)

**Does NOT**:
- ❌ Write code directly (OrchestratorCodeGate hook blocks this)
- ❌ Run tests directly (delegates to QA)
- ❌ Make architectural decisions without user approval

---

## Multi-Agent Workflow

### Context Package Design

Context packages provide complete information to stateless sub-agents.

**DEV Agent Context Package**:
```markdown
# Task Context: T001

## Task Details
**ID**: T001
**Description**: Implement user authentication service
**Files**: backend/src/services/UserService.ts, tests/test_user.ts

## Acceptance Criteria
- [ ] Create user with valid email
- [ ] Reject invalid email formats
- [ ] Prevent duplicate emails
- [ ] Hash passwords securely

## Quality Standards
**Test Command**: npm test
**Lint Command**: npm run lint
**Type Command**: npm run type-check
**Coverage Threshold**: 80% branches

## Related Requirements
FR-010, FR-011, FR-012

## Tech Stack
**Language**: TypeScript
**Framework**: Express.js
**Database**: PostgreSQL
**Patterns**: Service layer, repository pattern
```

**QA Agent Context Package**:
```markdown
# QA Validation Context

## Tasks to Validate
- **T001**: User authentication service
  - Files: UserService.ts, test_user.ts
- **T002**: Task CRUD operations
  - Files: TaskService.ts, test_task.ts

## Quality Standards
**Test Command**: npm test
**Coverage Command**: npm test -- --coverage
**Coverage Threshold**: 80% branches
**Lint Command**: npm run lint
**Type Command**: npm run type-check

## Definition of Done
- [ ] All tests pass (0 failures)
- [ ] Coverage ≥80% branches
- [ ] No linting errors
- [ ] No type errors
- [ ] No console.log in production code
- [ ] No TODO comments

## Project Root
/Users/developer/project
```

### Parallel Execution Strategy

**Rules**:
1. **Max 3 parallel DEV agents** (hard limit)
2. **Dependency-aware**: Only execute tasks with satisfied dependencies
3. **Sequential validation**: All DEV complete → then QA validates
4. **Batch commits**: Orchestrator commits after QA PASS

**Example Dependency Analysis**:
```markdown
Tasks:
- T001: Setup database (no deps)
- T002: UserService (depends on T001)
- T003: TaskService (depends on T001)
- T004: TagService (no deps)
- T005: User-Task associations (depends on T002, T003)

Execution Plan:
Batch 1 (parallel): T001, T004 (2 agents)
Batch 2 (parallel): T002, T003 (2 agents, after T001 complete)
Batch 3 (sequential): T005 (1 agent, after T002+T003 complete)
```

### QA Feedback Loop

```
DEV agents complete → QA validates
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                 [PASS]      [FAIL]
                    │           │
                    │           ├─→ Parse issues
                    │           ├─→ Prepare DEV rework context
                    │           ├─→ Re-invoke DEV with fixes
                    │           └─→ Loop back to QA (max 3 cycles)
                    │
                    ├─→ Mark tasks complete
                    ├─→ Create git commit
                    └─→ Continue workflow
```

**Rework Context Package** (when QA returns FAIL):
```markdown
# Task Context: T001 - REWORK (Attempt 2)

## Original Task
[Original context package]

## QA Findings
**Status**: FAIL

**Issues Found**:
1. CRITICAL: 5 tests failing in UserService
   - Location: test_user.ts:45-82
   - Error: "Expected validation error, but got success"
   - Recommendation: Add email format validation before DB insert

2. MAJOR: Coverage 72% (threshold: 80%)
   - Recommendation: Add tests for error paths

## Required Fixes
- [ ] Fix email validation tests
- [ ] Add error path tests
- [ ] Ensure coverage ≥80%
- [ ] Re-run all verification commands

## Quality Standards
[Same as original]
```

---

## Data Model

### Quality Configuration

**File**: `.pantheon/quality-config.json` (created in user project)

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
  "discovery_source": "slash_command" | "plan.md" | "manual",
  "contextualized_at": "2025-10-08T12:34:56Z"
}
```

**Discovery**: Generated by `/pantheon:contextualize` slash command using LLM-based analysis

**Consumers**: All agents (DEV, QA), all hooks (SubagentStop, PreCommit, PhaseGate)

### Hook Configuration

**File**: `.claude/settings.json` (updated by `pantheon integrate`)

**Purpose**: Configure Claude Code hooks for quality gates

**Schema**:
```json
{
  "hooks": {
    "SubagentStop": ".pantheon/hooks/subagent-validation.sh",
    "PreCommit": ".pantheon/hooks/pre-commit-gate.sh",
    "PhaseGate": ".pantheon/hooks/phase-transition-gate.sh",
    "PreToolUse": [
      {
        "matcher": "Bash(git commit*)",
        "hooks": [
          {
            "type": "command",
            "command": "bash .pantheon/hooks/pre-commit-gate.sh"
          }
        ]
      },
      {
        "matcher": "Write(*) | Edit(*)",
        "hooks": [
          {
            "type": "command",
            "command": "bash .pantheon/hooks/orchestrator-code-gate.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Integration System

### Minimal Directives Approach

Pantheon integrates with Spec Kit using **minimal directives** rather than rewriting commands.

**Philosophy**: Don't modify Spec Kit's logic—just tell it to use agents.

**Integration Files**:
```
src/pantheon/integrations/spec_kit/directives/content/
├── implement.md      # Multi-agent workflow instructions
├── plan.md           # Quality standards guidance
├── tasks.md          # Subtask format guidance
└── claude_md.md      # Orchestration instructions for CLAUDE.md
```

**Example Integration** (`implement.md` directive):
```markdown
## Sub-Agent Integration

**Workflow**: DEV agents → QA validation → Repeat

### 1. Execute Tasks (DEV Agents)
For each task in tasks.md:
- Invoke DEV agent with context package
- For parallel tasks marked `[P]`: Invoke in parallel

### 2. Validate Quality (QA Agent)
After DEV completes:
1. DO NOT commit yet
2. Invoke QA agent with task IDs
3. Process QA report:
   - PASS: Present to user → commit after approval
   - FAIL: Re-invoke DEV with fixes

See `.claude/agents/dev.md` and `.claude/agents/qa.md` for details.
```

**Insertion Point**: After YAML frontmatter (not after markdown headings)

**Benefits**:
- ✅ Preserves all Spec Kit functionality
- ✅ Easy to rollback (remove directive section)
- ✅ Clear separation with `---` divider
- ✅ ~300 LOC vs ~2000 LOC (complex rewrite approach)

---

## Quality Hooks

### Hook Architecture

**Defense in Depth Strategy**:
```
Layer 1: DEV Self-Check (soft)
    ↓
Layer 2: SubagentStop Hook (medium - fast sanity check)
    ↓
Layer 3: QA Agent Validation (deep - comprehensive analysis)
    ↓
Layer 4: PreCommit Hook (hard - final gate before commit)
    ↓
Layer 5: PhaseGate Hook (automatic phase transition validation)
```

### SubagentStop Hook

**Purpose**: Verify sub-agent completed all required tasks before returning

**Event**: `SubagentStop` (runs when DEV or QA completes)

**File**: `.pantheon/hooks/subagent-validation.sh`

**Validation (DEV)**:
- Tests pass
- Linting passes
- Type checking passes
- No console.log in production code
- No TODO/FIXME comments
- No debugger statements

**Validation (QA)**:
- Verified test results file exists
- Verified coverage results file exists
- Verified lint results file exists
- Verified type check results file exists

**Exit Codes**:
- `0`: Validation passed, allow completion
- `2`: Validation failed, block completion

### PreCommit Hook

**Purpose**: Final quality gate before git commit

**Event**: `PreToolUse Bash(git commit*)`

**File**: `.pantheon/hooks/pre-commit-gate.sh`

**Validation**:
- Run full test suite → must pass
- Run linting → must pass
- Run type checking → must pass
- Check coverage → informational only

**Exit Codes**:
- `0`: All checks passed, allow commit
- `2`: Checks failed, block commit

### PhaseGate Hook

**Purpose**: Validate phase completion before transition

**Event**: `PreToolUse Task` (when transitioning to new phase without QA validation)

**File**: `.pantheon/hooks/phase-transition-gate.sh`

**Validation**:
- Check tasks.md for "QA validated" marker
- Check tasks.md for "User validated" marker
- Block if either missing

**Exit Codes**:
- `0`: Validation complete and approved, allow transition
- `2`: Missing validation/approval, block transition

### OrchestratorCodeGate Hook

**Purpose**: Prevent orchestrator from editing source code

**Event**: `PreToolUse Write(*) | Edit(*)`

**File**: `.pantheon/hooks/orchestrator-code-gate.sh`

**Logic**:
- **Allow**: Documentation files (tasks.md, README.md, CHANGELOG.md, docs/, .claude/)
- **Block**: All source code, tests, configuration files

**Purpose**: Enforces separation of concerns—orchestrator coordinates, DEV implements

---

## Design Decisions

### Why Sub-Agents?

**Decision**: Use Claude Code's sub-agent architecture for DEV and QA

**Rationale**:
- **Separate context windows** preserve main conversation (no pollution)
- **Stateless invocation** easier to reason about (no hidden state)
- **Tool scoping** ensures focused behavior (DEV can't spawn more agents)
- **Independent execution** enables parallel workflows

**Alternative Considered**: Single agent with different "modes"

**Why Rejected**: Mode-switching pollutes context, harder to enforce constraints

### Why Minimal Directives (Not Command Rewrites)?

**Decision**: Add integration sections to Spec Kit commands, don't rewrite them

**Rationale**:
- **90% less complexity**: ~300 LOC vs ~2000 LOC
- **Preserves existing logic**: All Spec Kit functionality remains
- **Easier maintenance**: Updates don't require merging algorithms
- **Faster implementation**: ~4 hours vs multiple days
- **Clear boundaries**: Integration sections clearly marked with `---`

**Evolution**: Original design used complex file merging with heuristic customization detection

**Learning**: Complexity ≠ value. Simplest solution that works is best.

### Why Hook-Based Enforcement?

**Decision**: Use Claude Code hooks to enforce quality gates deterministically

**Rationale**:
- **Deterministic**: No LLM interpretation, pure bash validation
- **Unskippable**: Agent cannot bypass hook validation
- **Fast feedback**: Immediate error messages with actionable guidance
- **Defense in depth**: Multiple layers catch different classes of issues

**Alternative Considered**: Rely on agent instructions only

**Why Rejected**: Benchmark Test-1 showed soft enforcement fails under pressure

### Why LLM-Based Quality Discovery?

**Decision**: Use `/pantheon:contextualize` slash command for quality discovery, not hardcoded rules

**Rationale**:
- **Supports ANY language/framework**: Python, Node.js, Go, Rust, Java, etc.
- **Adapts to project conventions**: Reads README/docs for custom setups
- **Future-proof**: Works with new tools as they emerge (Bun, Deno, Biome, etc.)
- **Handles edge cases**: Monorepos, multi-language projects, non-standard structures

**Alternative Considered**: Hardcoded detection rules per language

**Why Rejected**: Maintenance burden, doesn't handle custom configurations

### Why Python + uvx Distribution?

**Decision**: Distribute as Python package installable via `uvx`

**Rationale**:
- **Familiar pattern**: Same as Spec Kit (`uvx spec-kit`)
- **Rich CLI libraries**: Click, Typer provide excellent UX
- **Excellent file manipulation**: Python great for markdown/YAML/JSON parsing
- **Seamless integration**: Works with existing Claude Code + Spec Kit setup

**Alternative Considered**: Shell scripts or Node.js package

**Why Rejected**: Less robust file parsing, harder cross-platform support

### Why Sequential Validation (Not Interleaved)?

**Decision**: All DEV agents complete → then QA validates (no interleaving)

**Rationale**:
- **Simpler workflow**: Easier to reason about
- **Batch context**: QA sees entire batch together for better analysis
- **No race conditions**: Sequential validation prevents conflicts
- **Clear checkpoints**: User knows when batch is complete

**Alternative Considered**: DEV on next task while QA validates previous

**Why Rejected**: Complex error handling, confusing user feedback, race conditions

### Why Orchestrator Creates Commits?

**Decision**: Only orchestrator creates git commits, never DEV agents

**Rationale**:
- **Centralized control**: Single source of commit authority
- **QA enforcement**: Commits only after QA validation passes
- **User approval**: Commits only after user approves phase completion
- **Atomic batches**: Batch commits reflect complete logical units

**Alternative Considered**: DEV agents create commits after self-validation

**Why Rejected**: Benchmark Test-1 showed self-validation insufficient

---

## Key Abstractions

### Context Package

**Purpose**: Provide complete information to stateless sub-agents

**Pattern**:
```
Orchestrator:
  1. Analyzes current state
  2. Prepares context package with all needed info
  3. Invokes sub-agent via Task tool
  4. Processes results
```

**Benefit**: Sub-agent doesn't need memory—everything provided upfront

### Quality Config as Single Source of Truth

**Purpose**: Centralize project-specific quality commands

**Pattern**:
```
/pantheon:contextualize (LLM analysis)
    ↓
.pantheon/quality-config.json
    ↓
┌───────────┬─────────────┬──────────────┐
│ DEV Agent │  QA Agent   │  All Hooks   │
└───────────┴─────────────┴──────────────┘
```

**Benefit**: Change commands once, affects all agents and hooks

### Orchestrator as Coordinator

**Purpose**: Clear separation between coordination and execution

**Pattern**:
```
Orchestrator (main agent):
  - Analyzes dependencies
  - Prepares context packages
  - Invokes specialists
  - Manages workflow state
  - Creates commits

DEV/QA (sub-agents):
  - Execute specialized tasks
  - Return results
  - No coordination logic
```

**Benefit**: Single responsibility, easier to test and maintain

---

## References

- **Research Findings**: `docs/archive/design.md`, `docs/archive/research.md`
- **v0.2.0 Feature Spec**: `docs/archive/v0.2-feature-spec/spec.md`
- **Benchmark Test-1**: `docs/BENCHMARK-TEST-1.md`
- **Hook Scripts**: `.pantheon/hooks/` (in user projects)
- **Agent Specifications**: `src/pantheon/agents/dev.md`, `src/pantheon/agents/qa.md`
