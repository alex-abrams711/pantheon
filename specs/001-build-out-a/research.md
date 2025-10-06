# Phase 0: Research - Multi-Agent Quality-First Workflow

**Feature**: Multi-Agent Quality-First Workflow (Pantheon v0.2.0)
**Branch**: 001-build-out-a
**Date**: 2025-10-06

---

## Research Areas

### 1. Claude Code Hook System

**Question**: How do Claude Code hooks work, and what are the technical constraints for SubagentStop, PreCommit, and Phase Gate hooks?

**Decision**: Use Claude Code's hook system with shell scripts configured in .claude/settings.json

**Rationale**:
- Claude Code supports event-based hooks (SubagentStop, PreCommit, UserPromptSubmit)
- Hooks are shell scripts that receive context via stdin/env variables
- Exit code 2 blocks the action (agent completion, commit, phase transition)
- Exit code 0 allows action to proceed
- Hooks can output messages that are shown to the agent/user

**Alternatives Considered**:
- Python-based hooks: Rejected (adds Python runtime dependency to user projects)
- Agent-only validation: Rejected (agents can work around soft suggestions)
- Manual validation prompts: Rejected (requires user intervention every time)

**Implementation Notes**:
- SubagentStop hook runs when DEV/QA agents complete (validates work before returning to orchestrator)
- PreCommit hook runs before git commits (final quality gate)
- Phase Gate hook triggered by UserPromptSubmit when user approves phase transition
- All hooks read from .pantheon/quality-config.json for project-specific commands

---

### 2. Parallel Sub-Agent Invocation

**Question**: How do we invoke multiple DEV agents in parallel using Claude Code's Task tool?

**Decision**: Use single message with multiple Task tool calls

**Rationale**:
- Claude Code documentation states: "If you intend to call multiple tools and there are no dependencies between them, make all independent tool calls in parallel"
- Single message with 3 Task tool invocations = 3 parallel DEV agents
- Orchestrator waits for all agents to complete before processing results
- Results come back when all agents finish (sequential validation)

**Alternatives Considered**:
- Sequential invocation: Rejected (no performance benefit)
- Background agents with polling: Rejected (adds complexity, unclear termination)
- Async/await pattern: Rejected (not supported in Claude Code sub-agent model)

**Implementation Notes**:
- Orchestrator analyzes task dependencies from tasks.md
- Groups independent tasks (no "Dependencies:" links) into batches of max 3
- Invokes batch with single message containing multiple Task tool calls
- Waits for all to complete, preserves successful work, retries only failures

---

### 3. Project-Agnostic Quality Discovery

**Question**: How do we discover quality commands (test, lint, type-check) for any tech stack without hardcoding technology-specific logic?

**Decision**: Two-tier discovery: plan.md explicit commands first, then auto-discovery from project files

**Rationale**:
- Spec Kit's /plan command can include quality standards section
- If commands specified in plan.md, use those (explicit trumps implicit)
- If not in plan.md, analyze project structure:
  - Node.js: Parse package.json "scripts" for test/lint/build
  - Python: Check pyproject.toml for pytest/ruff/mypy, or detect installed tools
  - Go: Look for go.mod, use standard commands (go test, golangci-lint)
  - Ruby: Look for Gemfile, check for rspec/rubocop
- Single source of truth: .pantheon/quality-config.json
- All agents and hooks read from this config

**Alternatives Considered**:
- Hardcoded per-language commands: Rejected (not extensible, breaks KISS)
- User-provided config file: Rejected (adds setup friction)
- Ask user via prompts: Rejected (manual intervention, poor UX)

**Implementation Notes**:
- Discovery runs when `/constitution` command executes (aligns with project setup)
- Config format: JSON with keys (test_command, lint_command, type_command, coverage_command, build_command)
- Default coverage threshold: 80%
- If discovery fails, create config with empty commands and warn user

---

### 4. QA Agent Manual Testing Scope

**Question**: When should QA agent perform manual testing (browser-based UI validation, API testing)?

**Decision**: Always required for functional changes (frontend/backend code), skip only for non-functional tasks (docs, config-only)

**Rationale**:
- Automated tests don't catch: visual regressions, broken UI flows, API integration issues
- Manual testing validates: frontend (UI elements render, user flows work), backend (API responses correct, data flows validate)
- Non-functional tasks (documentation updates, configuration-only changes with no code behavior) don't need manual testing
- QA agent has access to browser MCP and Playwright MCP for manual validation

**Alternatives Considered**:
- Always skip manual testing: Rejected (misses functional regressions)
- Always require manual testing: Rejected (wastes time on docs/config)
- User decides per task: Rejected (adds friction, inconsistent)

**Implementation Notes**:
- QA agent receives task descriptions in context package
- Agent determines if functional changes present (looks for code file changes vs docs/config)
- For frontend: Use browser/Playwright MCP to verify UI renders, test user flows
- For backend: Use bash to call APIs, verify responses, check data flow
- Manual testing results included in QA report

---

### 5. Hook Installation and Configuration

**Question**: How do we install hook scripts and configure Claude Code settings.json automatically?

**Decision**: `pantheon integrate` command copies hooks to .pantheon/hooks/ and updates .claude/settings.json

**Rationale**:
- Hooks must be in user project (not in Pantheon package) to be executable
- .claude/settings.json is Claude Code's configuration file for hooks
- JSON format allows programmatic updates
- Hook scripts must be executable (chmod +x)

**Alternatives Considered**:
- Manual installation: Rejected (error-prone, poor UX)
- Git hooks (.git/hooks/): Rejected (not Claude Code specific, different event model)
- Symbolic links to package: Rejected (breaks on package updates)

**Implementation Notes**:
- Integration creates .pantheon/hooks/ directory
- Copies 3 hook scripts from package to project
- Makes scripts executable (chmod +x)
- Updates .claude/settings.json with hook configuration:
  ```json
  {
    "hooks": {
      "SubagentStop": ".pantheon/hooks/subagent-validation.sh",
      "PreCommit": ".pantheon/hooks/pre-commit-gate.sh",
      "UserPromptSubmit": ".pantheon/hooks/phase-gate.sh"
    }
  }
  ```
- Validates installation by checking files exist and are executable

---

### 6. QA Agent Context Package Design

**Question**: What context does the QA agent need to validate a batch of tasks?

**Decision**: Minimal, focused context package with tasks, quality standards, and Definition of Done

**Rationale**:
- QA agent should be stateless (each invocation independent)
- Agent needs: what to validate (tasks), how to validate (quality commands), what defines success (Definition of Done)
- Keep context small to avoid token bloat

**Context Package Format**:
```markdown
## Tasks to Validate
- T001: Task description (files: src/foo.py, tests/test_foo.py)
- T002: Task description (files: src/bar.py, tests/test_bar.py)

## Quality Standards
- Test command: pytest tests/
- Coverage threshold: 80% branches
- Lint command: ruff check src/ tests/
- Type command: mypy src/

## Definition of Done
- [ ] All tests pass (0 failures)
- [ ] Coverage meets threshold (branches ≥80%)
- [ ] No linting errors
- [ ] No type errors
- [ ] No code smells (console.log, TODO, debugger)
- [ ] Manual testing passed (if functional changes)

## Project Root
/Users/user/project
```

**Alternatives Considered**:
- Full spec.md + plan.md: Rejected (token waste, unnecessary context)
- Only test command: Rejected (incomplete validation)
- Agent discovers quality commands: Rejected (duplication, potential inconsistency)

---

### 7. QA Report Structure

**Question**: What format should the QA agent use for reporting results?

**Decision**: Structured markdown report with status, metrics, issues, and recommendations

**Report Format**:
```markdown
# QA Validation Report

**Status**: PASS | FAIL
**Batch**: T001, T002
**Date**: 2025-10-06

## Summary Metrics
- Tests: 45 total, 45 passing, 0 failing
- Coverage: 87.3% branches (threshold: 80%) ✓
- Lint: 0 errors ✓
- Type: 0 errors ✓
- Code Smells: 0 found ✓
- Manual Testing: PASS ✓

## Issues
[Empty if PASS, or:]

### CRITICAL
- **T001**: Test failure in test_foo.py::test_bar
  - Location: tests/test_foo.py:45
  - Error: AssertionError: expected 5, got 3
  - Recommendation: Review calculation logic in src/foo.py:calculate()

### MAJOR
- **T002**: Coverage below threshold on src/bar.py
  - Coverage: 65% branches (need: 80%)
  - Recommendation: Add test cases for error handling paths

### MINOR
- **T001**: TODO comment in src/foo.py:67
  - Recommendation: Complete implementation or remove TODO

## Definition of Done
- [x] All tests pass
- [ ] Coverage meets threshold (T002 fails)
- [x] No linting errors
- [x] No type errors
- [ ] No code smells (T001 TODO)
- [x] Manual testing passed

## Recommendations
1. Fix critical test failure in T001 (blocking)
2. Add test coverage for T002 error paths
3. Remove TODO comment in T001
```

**Rationale**:
- Status at top (PASS/FAIL) for quick decision
- Metrics provide overview
- Issues categorized by severity (CRITICAL blocks PASS)
- Each issue linked to task for targeted rework
- Recommendations are actionable (not just "fix it")
- Definition of Done checklist shows what passed/failed

---

### 8. Phase Gate Trigger Mechanism

**Question**: How does the Phase Gate hook know when user approves a phase transition?

**Decision**: UserPromptSubmit hook detects approval keywords in user messages

**Rationale**:
- UserPromptSubmit hook runs on every user message
- Hook checks message for approval keywords: "yes", "proceed", "phase [N]"
- If detected, runs quality validation and blocks if fails
- Orchestrator presents phase completion report and waits for approval

**Implementation**:
```bash
# In phase-gate.sh
USER_MESSAGE=$(cat)  # Read user message from stdin

# Check for approval keywords
if echo "$USER_MESSAGE" | grep -iE '(yes|proceed|phase [0-9]+)'; then
  # User approved, run quality validation
  source .pantheon/quality-config.json
  # Run tests, lint, type-check
  # Exit 2 if any fail (blocks transition)
  # Exit 0 if all pass (allows transition)
else
  # Not an approval message, allow to proceed
  exit 0
fi
```

**Alternatives Considered**:
- Explicit `/phase-next` command: Rejected (requires custom command, friction)
- Orchestrator validation only: Rejected (soft gate, can be bypassed)
- PreCommit hook only: Rejected (too late, work already marked complete)

---

### 9. Backward Compatibility Strategy

**Question**: How do we ensure Pantheon v0.2.0 doesn't break existing v0.1.x projects?

**Decision**: Opt-in hook installation, DEV agent backward compatible, QA agent is new feature

**Rationale**:
- v0.1.x projects have DEV agent but no hooks
- `pantheon integrate` must be run to install hooks (opt-in)
- Updated DEV agent removes commit logic but otherwise compatible
- QA agent is new file (qa.md), doesn't affect existing workflows
- Projects without hooks simply don't have quality gates (degrades gracefully)

**Migration Path**:
1. Update Pantheon package: `uv tool upgrade pantheon-agents`
2. Update agents in project: `pantheon init` (overwrites dev.md with updated version)
3. Install hooks (optional): `pantheon integrate`

**Testing**:
- Test v0.1.x project workflow still works after package upgrade (without integrate)
- Test v0.2.0 workflow with hooks installed
- Test rollback removes hooks and restores v0.1.x behavior

---

## Summary

All technical decisions made:
- ✅ Hook system: Shell scripts in .pantheon/hooks/, configured in .claude/settings.json
- ✅ Parallel agents: Single message with multiple Task tool calls (max 3)
- ✅ Quality discovery: Two-tier (plan.md explicit, then auto-discovery)
- ✅ Manual testing: Required for functional changes, skip for non-functional
- ✅ Hook installation: `pantheon integrate` command
- ✅ QA context package: Minimal (tasks, standards, Definition of Done)
- ✅ QA report: Structured markdown with status/metrics/issues/recommendations
- ✅ Phase gate: UserPromptSubmit hook detects approval keywords
- ✅ Backward compatibility: Opt-in hooks, graceful degradation

No NEEDS CLARIFICATION remaining. Ready for Phase 1 (Design & Contracts).
