# Feature Specification: Multi-Agent Quality-First Workflow (Pantheon v0.2.0)

**Feature Branch**: `001-build-out-a`
**Created**: 2025-10-06
**Status**: Draft
**Input**: User description: "build out a spec for the proposal(s) in @docs/benchmarks/test-1/workflow-improvements-proposal.md"

## Execution Flow (main)
```
1. Parse user description from Input
   → ✅ Feature description provided (workflow improvements proposal)
2. Extract key concepts from description
   → ✅ Identify: actors (DEV/QA agents, orchestrator), actions (parallel execution, validation), data (quality reports), constraints (max 3 parallel)
3. For each unclear aspect:
   → All aspects clearly defined in proposal document
4. Fill User Scenarios & Testing section
   → ✅ User workflows defined (developer using Pantheon with Spec Kit)
5. Generate Functional Requirements
   → ✅ Each requirement testable and derived from proposal
6. Identify Key Entities (if data involved)
   → ✅ Entities: QA Agent, Quality Config, Hook Scripts, Phase Gates
7. Run Review Checklist
   → ✅ No [NEEDS CLARIFICATION] markers
   → ✅ No implementation details in requirements
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## Project Context

**Current State** (Pantheon v0.1.x):
- Single DEV agent executes tasks sequentially
- No independent quality validation
- Soft quality enforcement (suggestions, not requirements)
- No user checkpoints between phases
- Benchmark Test-1 Score: **67.5/100** with 43 failing tests

**Target State** (Pantheon v0.2.0):
- Multi-agent architecture with independent DEV and QA agents
- Parallel task execution (up to 3 simultaneous DEV agents)
- Deterministic quality enforcement via hooks
- Automatic user checkpoints with validation
- Benchmark Test-2 Target Score: **85+/100** with 0 failing tests

---

## Clarifications

### Session 2025-10-06

- Q: The current spec describes updating `/implement` command integration with "multi-agent workflow guidance" but your clarification emphasizes keeping Spec Kit changes minimal. Which integration approach should we take? → A: Use existing "## Agent Integration" section in /implement command (minimal updates only). Add orchestrator workflow instructions to CLAUDE.md instead of expanding Spec Kit command directives.

- Q: When should the system discover and create `.pantheon/quality-config.json`? → A: Run quality discovery when `/constitution` command executes (aligns with project setup and constitution creation).

- Q: Where should hook script files be installed? → A: Hook scripts in .pantheon/hooks/, configuration references in .claude/settings.json

- Q: When should the QA agent perform manual testing? → A: Always required for functional changes (frontend/backend). Skip only for non-functional tasks (documentation, config-only).

- Q: When executing 3 DEV agents in parallel, what should happen if one fails/blocks while others succeed? → A: Wait for all to complete, accept successful ones, retry only failed agent(s), then proceed to QA once all succeed.

---

## User Scenarios & Testing

### Primary User Story

As a **software developer using Pantheon with GitHub Spec Kit**, I need the system to implement features with guaranteed quality, parallel efficiency, and phase-by-phase validation so that I can confidently deliver production-ready code without accumulating technical debt or silent test failures.

### Acceptance Scenarios

#### Scenario 1: Parallel Task Execution
**Given** I have a phase with 5 independent tasks with no dependencies
**When** the orchestrator analyzes the task list
**Then** the system groups tasks into batches of maximum 3 parallel executions
**And** invokes multiple DEV agents simultaneously in a single message
**And** waits for all DEV agents to complete before proceeding to validation

#### Scenario 2: Quality Validation with QA Agent
**Given** all DEV agents in a batch have completed their tasks (with functional code changes)
**When** the orchestrator invokes the QA agent
**Then** the QA agent runs all automated quality checks (tests, coverage, linting, type checking)
**And** performs manual functional testing (UI verification for frontend, API/data flow testing for backend)
**And** analyzes results to identify failures, coverage gaps, code smells, and functional issues
**And** links issues to specific tasks
**And** returns a structured report with PASS or FAIL status and actionable recommendations

#### Scenario 3: Quality Gate Enforcement via Hooks
**Given** a DEV agent claims task completion
**When** the SubagentStop hook executes
**Then** the hook runs actual quality commands (tests, lint, type check)
**And** searches for code smells (console.log, TODO comments, debugger statements)
**And** blocks the agent completion if any violations found
**And** provides clear error messages for the agent to fix

#### Scenario 4: QA Feedback Loop
**Given** the QA agent returns FAIL with specific issues
**When** the orchestrator processes the QA report
**Then** the system re-invokes specific DEV agents with issue details
**And** DEV agents fix the identified problems
**And** the QA agent validates again
**And** the loop continues until PASS or 3 attempts reached

#### Scenario 5: Phase Gate with User Checkpoint
**Given** all tasks in a phase have been completed and validated
**When** the orchestrator presents a phase completion report
**Then** the system waits for user approval before proceeding
**And** when the user approves, the phase gate hook automatically validates quality
**And** if validation fails, the system blocks phase transition and reports issues
**And** if validation passes, the system proceeds to the next phase

#### Scenario 6: Orchestrator Commits After Validation
**Given** the QA agent returns PASS for a batch of tasks
**When** the orchestrator creates a git commit
**Then** the PreCommit hook runs all quality checks before allowing the commit
**And** if checks fail, the commit is blocked with clear error messages
**And** if checks pass, the commit is created with a descriptive message including quality metrics

#### Scenario 7: Project-Agnostic Quality Discovery
**Given** a new project initialized with Pantheon (Node.js, Python, Go, or other tech stack)
**When** the orchestrator runs for the first time
**Then** the system analyzes the project structure (package.json, pyproject.toml, go.mod, etc.)
**And** discovers quality commands from plan.md if specified
**And** auto-discovers commands if not in plan.md
**And** creates .pantheon/quality-config.json with discovered commands
**And** all agents and hooks read from this config file

#### Scenario 8: DEV Agent Blocked Status
**Given** a DEV agent attempts a subtask 3 times but verification keeps failing
**When** the agent reaches the failure threshold
**Then** the agent stops implementation
**And** documents the blocker clearly (what was attempted, why it's blocked, what's needed)
**And** returns status BLOCKED to the orchestrator
**And** the orchestrator halts execution and reports to the user for guidance

### Edge Cases

#### Edge Case 1: All DEV Agents Complete but QA Fails
**What happens when** all DEV agents report SUCCESS but QA identifies critical failures?
- System does NOT mark tasks complete
- System does NOT create commits
- System re-invokes specific DEV agents with QA findings
- Loop continues until PASS (max 3 QA validation cycles)
- After 3 failures, system halts and waits for user guidance

#### Edge Case 2: SubagentStop Hook Blocks DEV Completion
**What happens when** DEV agent claims completion but hook finds violations (console.log, failing tests)?
- Hook blocks the agent with exit code 2
- Agent receives clear error message about specific violations
- Agent must fix issues before completion accepted
- Hook runs again after fixes until pass

#### Edge Case 3: Phase Gate Hook Blocks Phase Transition
**What happens when** user approves phase transition but automated validation fails?
- Phase gate hook blocks with exit code 2
- User sees error message: "Phase gate validation failed - tests/lint/coverage not passing"
- Phase does NOT transition
- User must review and fix issues before proceeding

#### Edge Case 4: Dependency Chain Requires Sequential Execution
**What happens when** tasks have dependencies that prevent full parallelization?
- Orchestrator analyzes dependency graph from tasks.md
- Groups only independent tasks for parallel execution
- Executes dependent tasks sequentially after prerequisites complete
- Example: T001 (no deps) + T004 (no deps) parallel, then T002 (depends on T001) sequentially

#### Edge Case 5: PreCommit Hook Fails After QA Pass
**What happens when** code passes QA validation but fails PreCommit hook (e.g., tests regressed between QA and commit)?
- PreCommit hook blocks commit with exit code 2
- Orchestrator sees commit blocked with error details
- System must re-run QA validation to identify new issues
- Prevents degraded code from being committed

#### Edge Case 6: Quality Config Discovery Fails
**What happens when** project structure is ambiguous and plan.md doesn't specify quality commands?
- System creates .pantheon/quality-config.json with empty commands
- Hooks and QA agent skip checks that have no command specified
- User receives warning: "Quality commands not discovered - specify in plan.md"
- Workflow continues but with reduced validation coverage

#### Edge Case 7: No Independent Tasks for Parallelization
**What happens when** all tasks in a phase have dependencies (no parallel opportunities)?
- Orchestrator executes tasks sequentially (1 DEV agent at a time)
- QA validation still runs after each task or small batches
- No performance benefit from parallelization in this phase
- Workflow correctness maintained

#### Edge Case 8: Partial Batch Failure (Mixed Success/Failure)
**What happens when** 3 DEV agents run in parallel but 1 fails/blocks while 2 succeed?
- Orchestrator waits for all 3 agents to complete
- Preserves successful work from the 2 passing agents (no re-execution)
- Re-invokes only the 1 failed agent with error details
- Failed agent attempts fix (up to 3 total attempts)
- Once failed agent succeeds, proceeds to QA validation for entire batch
- If failed agent reaches 3 failures, halts and reports to user for guidance

---

## Requirements

### Functional Requirements

#### Core Multi-Agent Architecture

- **FR-001**: System MUST support a multi-agent architecture with three distinct roles: Orchestrator (main Claude agent), DEV agents (implementation specialists), and QA agent (validation specialist)

- **FR-002**: Orchestrator MUST load context from spec.md, plan.md, and tasks.md before beginning workflow execution

- **FR-003**: Orchestrator MUST analyze task dependencies from tasks.md to determine which tasks can execute in parallel

- **FR-004**: System MUST support parallel execution of up to 3 DEV agents simultaneously for independent tasks

- **FR-005**: Orchestrator MUST invoke multiple DEV agents using parallel Task tool calls in a single message

- **FR-006**: System MUST wait for all DEV agents in a batch to complete before processing results (sequential validation, no interleaving)

- **FR-006a**: When some DEV agents in a batch fail/block while others succeed, orchestrator MUST preserve successful agents' work, retry only failed agents, and proceed to QA only once all agents in batch succeed

#### DEV Agent Capabilities

- **FR-007**: DEV agent MUST receive a context package containing task ID, description, file paths, acceptance criteria, quality standards, related requirements, and tech stack constraints

- **FR-008**: DEV agent MUST implement code following Test-Driven Development (TDD) methodology

- **FR-009**: DEV agent MUST run verification commands (test, lint, type-check) after each acceptance criterion

- **FR-010**: DEV agent MUST perform self-inspection for code smells (console.log, TODO comments, debugger statements, unused imports)

- **FR-011**: DEV agent MUST return SUCCESS status with implementation summary when all checks pass

- **FR-012**: DEV agent MUST return BLOCKED status with blocker details when verification fails 3 times on the same criterion

- **FR-013**: DEV agent MUST NOT create git commits (orchestrator handles commits)

#### QA Agent Capabilities

- **FR-014**: System MUST provide a QA agent that validates code quality independently from DEV agents

- **FR-015**: QA agent MUST receive a context package containing tasks to validate, quality standards, coverage thresholds, Definition of Done checklist, and project root path

- **FR-016**: QA agent MUST run all automated quality checks (tests, coverage, linting, type checking) AND perform manual functional testing for all tasks involving code changes (frontend or backend verification)

- **FR-017**: QA agent MUST analyze test results to extract total tests, passing tests, failing tests, and specific failure details (test name, file, line, error message)

- **FR-018**: QA agent MUST analyze coverage results and compare to thresholds (branches, statements, functions)

- **FR-019**: QA agent MUST search for code smells not covered by automated tools (console statements in production code, TODO comments, unused code with 0% coverage)

- **FR-020**: QA agent MUST link each issue to the specific task that likely caused it

- **FR-021**: QA agent MUST classify issues by severity (CRITICAL, MAJOR, MINOR)

- **FR-022**: QA agent MUST generate a structured report with status (PASS/FAIL), summary metrics, detailed issues list, and actionable recommendations

- **FR-023**: QA agent MUST NOT fix issues or modify code (validation only)

- **FR-024**: QA agent MUST NOT mark status as PASS if any CRITICAL issue exists

- **FR-024a**: QA agent MAY skip manual testing for non-functional tasks (documentation updates, configuration-only changes with no code behavior impact)

#### Hook-Based Quality Gates

- **FR-025**: System MUST support installation of three quality gate hooks: SubagentStop, PreCommit, and Phase Gate

- **FR-026**: SubagentStop hook MUST run when DEV or QA agents complete, before returning results to orchestrator

- **FR-027**: SubagentStop hook for DEV agents MUST verify tests pass, linting passes, type checking passes, and no code smells exist (console.log, TODO, debugger)

- **FR-028**: SubagentStop hook for QA agents MUST verify all quality checks were executed and results files exist

- **FR-029**: SubagentStop hook MUST block agent completion with exit code 2 if any validation fails

- **FR-030**: PreCommit hook MUST run before every git commit to validate tests, linting, and type checking

- **FR-031**: PreCommit hook MUST block commits with exit code 2 if any quality check fails

- **FR-032**: Phase Gate hook MUST run automatically when user approves phase transition (user prompt contains "yes", "proceed", or "phase N")

- **FR-033**: Phase Gate hook MUST validate all quality checks pass before allowing phase transition

- **FR-034**: Phase Gate hook MUST block phase transition with exit code 2 if validation fails

#### QA Feedback Loop

- **FR-035**: Orchestrator MUST invoke QA agent after all DEV agents in a batch complete successfully

- **FR-036**: When QA agent returns PASS, orchestrator MUST mark tasks complete, create git commit, and continue to next batch

- **FR-037**: When QA agent returns FAIL, orchestrator MUST parse issue report and re-invoke specific DEV agents with issue details and recommendations

- **FR-038**: System MUST support up to 3 QA validation cycles per task before halting for user guidance

- **FR-039**: When QA feedback loop reaches 3 failures, orchestrator MUST halt execution, present full QA report to user, and wait for guidance

#### Phase Gates and User Checkpoints

- **FR-040**: Orchestrator MUST present a phase plan to the user before starting each phase, including objective, tasks list, parallelization strategy, quality standards, and estimated time

- **FR-041**: Orchestrator MUST wait for explicit user approval (user types "yes") before executing phase

- **FR-042**: Orchestrator MUST present a phase completion report after all tasks in phase complete, including completion date, tasks completed, quality metrics, git commits, and phase statistics

- **FR-043**: Orchestrator MUST wait for user approval before proceeding to next phase

- **FR-044**: User MUST be able to respond with "yes" (proceed), "review" (pause for code review), or "no" (halt for adjustments)

#### Orchestrator Commit Strategy

- **FR-045**: Orchestrator MUST create git commits only after QA validation returns PASS (batch commits)

- **FR-046**: Orchestrator MUST create commits with descriptive messages including completed tasks, description of work, and quality metrics summary

- **FR-047**: Orchestrator MUST create phase-level commits after all tasks in phase complete and pass final validation

- **FR-048**: Git commits MUST be atomic (one logical unit of work per commit)

- **FR-049**: PreCommit hook MUST run before every orchestrator commit to enforce final quality gate

#### Project-Agnostic Quality Discovery

- **FR-050**: System MUST discover quality commands based on project structure rather than hardcoding technology-specific commands

- **FR-051**: Orchestrator MUST check plan.md first for explicitly specified quality commands (test_command, lint_command, type_command, coverage_command, build_command)

- **FR-052**: When plan.md doesn't specify commands, orchestrator MUST auto-discover based on project files:
  - Node.js: Parse package.json scripts for test, lint, type-check, build
  - Python: Check for pytest, ruff, mypy in pyproject.toml or detect installed tools
  - Go: Check for go test, golangci-lint
  - Ruby: Check for rspec, rubocop
  - Other languages as applicable

- **FR-053**: System MUST create .pantheon/quality-config.json with discovered commands and coverage threshold (default: 80%) when `/constitution` command executes

- **FR-054**: All agents (DEV, QA) and all hooks MUST read quality commands from .pantheon/quality-config.json (single source of truth)

- **FR-055**: Quality config MUST be regenerated each time `/constitution` runs to ensure it stays synchronized with project changes

#### Integration and Installation

- **FR-056**: System MUST provide `pantheon integrate` command that installs hooks automatically

- **FR-057**: Integration process MUST create .pantheon/hooks/ directory in user project

- **FR-058**: Integration process MUST copy hook scripts (subagent-validation.sh, pre-commit-gate.sh, phase-gate.sh) from package to project

- **FR-059**: Integration process MUST add hook configuration to .claude/settings.json with proper event bindings

- **FR-060**: Integration process MUST make hook scripts executable (chmod +x)

- **FR-061**: Integration process MUST validate hook installation and report success or errors

- **FR-062**: System MUST support rollback via `pantheon rollback` command that removes hooks and restores original settings

#### Updated Agent Specifications

- **FR-063**: DEV agent specification (dev.md) MUST be updated to remove commit logic and add explicit verification sections

- **FR-064**: DEV agent MUST include Definition of Done checklist in specification

- **FR-065**: System MUST provide new QA agent specification (qa.md) with complete workflow, context package format, report structure, and guardrails

- **FR-066**: QA agent specification MUST be project-agnostic (no hardcoded commands like "npm test")

#### Spec Kit Integration

- **FR-067**: System MUST update existing "## Agent Integration" section in /implement command with minimal directive about using DEV and QA agents

- **FR-068**: Updates to /implement command MUST be minimal (only enhance existing Agent Integration section, no new sections or structural changes)

- **FR-069**: Integration MUST preserve all existing Spec Kit functionality and command logic

- **FR-070**: System MUST add comprehensive workflow orchestration instructions to CLAUDE.md (not in Spec Kit commands) covering: parallel execution strategy, QA validation workflow, phase gates, commit strategy, and context package formats

---

### Key Entities

- **QA Agent**: Independent validation specialist sub-agent with focused context for comprehensive quality validation. Receives batch of completed tasks, runs all automated quality checks (tests, coverage, lint, type-check), performs manual functional testing (frontend UI verification, backend API/data flow validation), analyzes results, links issues to tasks, generates structured reports, returns PASS/FAIL status. Has read-only access (no code modification). Manual testing required for all functional changes (code); may be skipped for non-functional tasks (documentation). Uses tools: Read, Bash, Grep, Glob, MCP browser, Playwright MCP.

- **Quality Config**: Project-specific configuration file (.pantheon/quality-config.json) containing discovered quality commands for tests, coverage, linting, type checking, and build. Single source of truth for all agents and hooks. Created by orchestrator during first execution. Supports any tech stack (Node.js, Python, Go, Ruby, etc.).

- **SubagentStop Hook**: Shell script (.pantheon/hooks/subagent-validation.sh) that executes when DEV or QA agents complete. Validates agent output before returning to orchestrator. For DEV: verifies tests pass, linting passes, type checking passes, no console.log/TODO/debugger. For QA: verifies all quality checks executed. Blocks with exit code 2 if validation fails.

- **PreCommit Hook**: Shell script (.pantheon/hooks/pre-commit-gate.sh) that executes before every git commit. Runs comprehensive quality suite (tests, lint, type-check, coverage). Blocks commits with exit code 2 if any check fails. Final quality gate before code committed.

- **Phase Gate Hook**: Shell script (.pantheon/hooks/phase-gate.sh) that executes automatically when user approves phase transition. Validates all quality checks pass before allowing phase to proceed. Blocks with exit code 2 if validation fails. Ensures phases don't transition with incomplete work.

- **Context Package**: Structured data bundle passed from orchestrator to DEV or QA agents. For DEV: includes task ID, description, files, acceptance criteria, quality standards, requirements, tech stack. For QA: includes tasks to validate, quality standards, thresholds, Definition of Done, project root. Enables stateless agent invocation with complete context.

- **QA Report**: Structured JSON report generated by QA agent containing status (PASS/FAIL), summary metrics (tests, coverage, lint, type errors), detailed issues list (task, severity, type, description, location, recommendation), and Definition of Done checklist. Consumed by orchestrator to determine next actions (commit or rework).

- **Phase Plan**: Document presented by orchestrator before each phase execution containing objective, task list, dependency analysis, parallelization strategy, quality standards, and estimated time. Requires user approval before proceeding. Provides transparency and control over workflow execution.

- **Phase Completion Report**: Document presented by orchestrator after phase completes containing completion date, completed tasks, quality metrics, git commits, phase statistics (DEV agents invoked, QA validations, rework cycles, duration). Requires user approval before proceeding to next phase.

- **Workflow Orchestration Guide**: Section in CLAUDE.md providing detailed instructions to the main Claude agent on how to orchestrate the multi-agent workflow. Includes parallel execution strategy, dependency analysis, QA validation workflow, phase gate procedures, commit strategy, and context package formats. Supplements minimal Spec Kit integration directives.

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked (none - proposal fully specified)
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---

## Success Metrics

### Quantitative Targets (Benchmark Test-2)

| Metric | Baseline (Test-1) | Target (Test-2) | Measurement Method |
|--------|-------------------|-----------------|-------------------|
| Overall Score | 67.5/100 | ≥85/100 | Weighted average of quality categories |
| Test Failures | 43 failures | 0 failures | Count of failing tests after implementation |
| Branch Coverage | 63.26% | ≥80% | Coverage report branch percentage |
| Code Quality Score | 78/100 | ≥90/100 | Static analysis + adherence to standards |
| Testing Score | 45/100 | ≥95/100 | Test completeness + all tests passing |
| Acceptance Score | 62/100 | ≥90/100 | Requirements met + features validated |
| Unused Code | 1 file (0% cov) | 0 files | Files with 0% coverage |
| Execution Speed | Baseline | 2-3x faster | Time to complete with parallelization |

### Qualitative Outcomes

**Process Improvements**:
- Phase-by-phase user validation prevents runaway execution
- Automated quality gates provide deterministic enforcement (no agent workarounds)
- Parallel execution reduces development cycle time for independent tasks
- Explicit verification loops eliminate silent test failures
- Clear separation of concerns (DEV builds, QA validates, orchestrator commits)

**Quality Guarantees**:
- Zero failing tests (enforced by hooks + QA agent)
- Coverage thresholds met (enforced by QA agent validation)
- No code smells (console.log, TODOs, unused code validated by QA + hooks)
- Consistent code patterns (enforced by Definition of Done checklist)
- Complete implementations (no partial work accepted by quality gates)

**Developer Experience**:
- Clear, actionable feedback when quality fails (QA detailed reports)
- Recommendations included in every issue (not just "test failed")
- Confidence in phase completion (quality gates passed)
- Faster iteration for parallel-safe tasks
- No surprise commits (orchestrator commits only after validation)
- Control over workflow (phase gate checkpoints)

---
