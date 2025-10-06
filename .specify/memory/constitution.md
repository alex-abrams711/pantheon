<!--
Sync Impact Report - Constitution Update
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Version Change: [None] → 1.0.0 (Initial Constitution)
Ratified: 2025-10-06
Last Amended: 2025-10-06

Modified Principles: N/A (Initial creation)
Added Sections: All
Removed Sections: None

Template Consistency Status:
✅ plan-template.md - Aligned with constitution structure
✅ spec-template.md - Aligned with constitution principles
✅ tasks-template.md - Aligned with TDD and quality focus
✅ agent-file-template.md - Aligned with incremental context updates

Follow-up TODOs: None

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-->

# Pantheon Agents Library Constitution

## Core Principles

### I. Sub-Agent Architecture

**Rule**: Every workflow agent operates as a stateless, focused sub-agent with clear boundaries.

- Sub-agents MUST operate in separate context windows to preserve main conversation state
- Each agent invocation MUST be stateless—no memory between calls
- State management is the ORCHESTRATOR's responsibility, not the agent's
- Agents MUST have explicit tool scoping (only implementation tools: Read, Write, Edit, Bash, Glob, Grep)
- Context packages MUST be provided fresh on every invocation

**Rationale**: Stateless sub-agents ensure predictable behavior, prevent context pollution, and enable parallel execution. Clear tool scoping keeps agents focused on their domain.

### II. Minimal Integration

**Rule**: Integration with external frameworks MUST be minimal, non-invasive, and reversible.

- Integration MUST use directive insertion, NOT command rewrites
- All integrations MUST create timestamped backups before making changes
- Rollback capability MUST be available via simple CLI command
- Integration MUST preserve all existing framework logic and functionality
- Validation MUST verify structural integrity (YAML frontmatter, required sections)

**Rationale**: Minimal integration reduces complexity by 90%, preserves framework updates, simplifies maintenance, and respects user customizations. Reversibility ensures user confidence.

### III. Quality-First Execution (NON-NEGOTIABLE)

**Rule**: Every implementation MUST pass quality gates before completion.

- Test-Driven Development (TDD) is MANDATORY: Tests → Fail → Implement → Pass
- Quality verification MUST include: linting, type checking, tests, coverage requirements
- Subtasks MUST NOT be marked complete until acceptance criteria AND quality standards are met
- Partial implementations or "simplified" solutions are FORBIDDEN
- If quality verification fails after 3 attempts, STOP and report—do not proceed

**Rationale**: Quality gates enforce discipline, prevent technical debt, and ensure reliable implementations. TDD validates behavior before implementation.

### IV. Separation of Concerns

**Rule**: Clear boundaries between orchestration and execution.

- ORCHESTRATORS (commands like /implement) manage: task sequencing, context packaging, state tracking, commits, user communication
- EXECUTORS (agents like DEV) handle: implementation, testing, verification, decision logging
- Orchestrators MUST delegate to sub-agents via Task tool with complete context packages
- Sub-agents MUST NOT handle commits, user interaction, or multi-task orchestration
- Results MUST flow back to orchestrators for aggregation and next steps

**Rationale**: Separation enables reusability, simplifies debugging, allows independent evolution of orchestrators and executors, and maintains clear responsibility.

### V. Simplicity and KISS

**Rule**: Every component MUST be as simple as possible while achieving its purpose.

- Prefer simple text insertion over complex file merging
- Avoid heuristics, customization detection, and manifest tracking unless absolutely necessary
- Reject over-engineering, unnecessary abstractions, and scope creep
- 5 decision points are better than 21 decision points
- 300 lines of code are better than 2000+ lines if they achieve the same goal
- Implementation time should be hours, not days

**Rationale**: Simplicity reduces maintenance burden, lowers bug probability, accelerates delivery, and makes the codebase accessible to contributors.

### VI. Distribution and Accessibility

**Rule**: Libraries MUST be trivially installable and discoverable.

- Distribution MUST use `uvx` for one-command installation (following Spec Kit pattern)
- Installation MUST work without configuration: `uvx pantheon-agents init`
- Detection MUST be automatic (e.g., Spec Kit presence via `.specify/` directory)
- User prompts MUST be minimal (2-3 prompts maximum for full integration)
- Agents MUST be copied to user projects (`.claude/agents/`) for version control and customization

**Rationale**: Low friction enables adoption. Automatic detection reduces cognitive load. Local agent copies enable customization while maintaining upgradability.

### VII. Versioning and Backward Compatibility

**Rule**: Agent versions and library versions MUST be managed independently with semantic versioning.

- Library version (in `pyproject.toml`) follows semantic versioning: MAJOR.MINOR.PATCH
- Agent files MUST include version in YAML frontmatter
- MAJOR bump: Breaking changes to agent behavior or integration contract
- MINOR bump: New capabilities, additional agents, enhanced features
- PATCH bump: Bug fixes, documentation, clarifications
- Backward compatibility MUST be maintained within MAJOR versions
- Breaking changes MUST include migration guides

**Rationale**: Independent versioning enables agent evolution without forcing library upgrades. Semantic versioning communicates impact clearly.

## Agent Development Standards

### Testing Requirements

- Unit test coverage MUST be ≥80% on core modules
- Integration tests MUST verify: CLI commands, file operations, backup/rollback, Spec Kit detection
- Contract tests MUST validate: agent YAML frontmatter, template structure, integration directives
- All tests MUST pass before release
- Type checking (mypy strict mode) MUST show 0 errors
- Linting (ruff) MUST pass with 0 errors

### Documentation Requirements

- Every agent MUST include:
  - Clear description in YAML frontmatter
  - Core Principles section explaining competencies and standards
  - Context Package section documenting expected inputs
  - Workflow section detailing execution phases
  - Quality Standards section defining verification criteria
  - Guardrails section listing forbidden behaviors
- README MUST document: installation, basic usage, all CLI commands, integration workflow, rollback procedure
- Code MUST include inline comments explaining WHY, not WHAT

### Code Quality Standards

- Python code MUST pass `ruff check` with pycodestyle, pyflakes, isort, pep8-naming
- Type hints MUST be present on all function signatures
- Functions MUST be focused (single responsibility)
- Magic numbers and strings MUST be replaced with named constants
- Error handling MUST use specific exceptions with clear messages
- Logging MUST use structured output (not print statements in library code)

## Workflow Execution Rules

### Context Package Format

When orchestrators invoke DEV (or other agents), the context package MUST include:

**Required**:
- Task ID and description
- File paths (specific files to create/modify)
- Subtasks/acceptance criteria (granular checklist)

**Optional but Recommended**:
- Relevant spec requirements (FR-XXX references)
- Quality standards (lint, type, test commands; coverage %)
- Tech stack constraints (language, framework, patterns)
- Constitution/guardrails (project-specific rules)

### Sub-Agent Invocation Pattern

```
Orchestrator prepares context package
  ↓
Invoke DEV via Task tool with context
  ↓ (separate context window)
DEV executes: code → test → verify acceptance → verify quality
  ↓
DEV returns results (status, completed work, quality output, decisions)
  ↓
Orchestrator processes results, creates commits, continues
```

### Quality Verification Loop

For every subtask:
1. Implement or write test (depending on TDD mode)
2. Verify acceptance criteria met
3. Run quality standards: lint → type check → tests → coverage
4. If quality fails:
   - Analyze: Does fix require functional rewrite?
   - If yes: Mark incomplete, return to step 1
   - If no: Attempt in-place fix (max 3 tries, then report and stop)
5. Mark subtask complete only if acceptance AND quality both pass

### Commit Strategy

- Orchestrators MUST create commits, NOT sub-agents
- Commits MUST be atomic (one logical change per commit)
- Commit messages MUST follow format: `type(scope): description`
- Commits MUST occur at phase boundaries or after subtask completion
- Pre-commit hooks MUST be honored (no `--no-verify` unless explicit user request)

## Integration Protocol (Spec Kit)

### Detection

- Detect Spec Kit presence via `.specify/` directory existence
- Offer integration only if Spec Kit detected
- Respect user choice to skip integration

### Integration Directives

**For `/implement` command**:
- Add "Agent Integration" section after title
- Directive: delegate all task execution to DEV sub-agent
- Preserve all existing `/implement` logic

**For `/plan` command**:
- Add "Quality Standards" section
- Directive: include lint/type/test commands and coverage requirements in plan output

**For `/tasks` command**:
- Add "Task Format" section
- Directive: include subtasks as acceptance criteria in each task

### Backup and Rollback

- Backup directory format: `.integration-backup-YYYYMMDD-HHMMSS/`
- Backup MUST include all modified files
- Rollback MUST restore all files atomically (all or nothing)
- Rollback MUST report which files were restored

## Governance

### Constitution Authority

- This constitution supersedes all other practices and guidelines
- All PRs and code reviews MUST verify constitutional compliance
- Violations MUST be justified in writing or rejected
- Complexity MUST be justified against Principle V (Simplicity)

### Amendment Process

- Amendments require: clear rationale, version bump decision, compatibility analysis
- MAJOR version: Backward-incompatible governance changes, principle removals/redefinitions
- MINOR version: New principles, materially expanded guidance
- PATCH version: Clarifications, wording improvements, typo fixes

### Compliance Review

- Every feature plan MUST include Constitution Check gate
- Gate MUST be checked BEFORE research phase (Phase 0)
- Gate MUST be re-checked AFTER design phase (Phase 1)
- Violations MUST be documented in Complexity Tracking with justification
- If no justification possible, feature MUST be simplified or rejected

### Runtime Guidance

- For agent-specific guidance (e.g., Claude Code, GitHub Copilot), use `CLAUDE.md`, `.github/copilot-instructions.md`, etc.
- Runtime guidance files MUST reference constitution principles
- Runtime guidance MUST NOT contradict constitution
- Constitution amendments MUST trigger review of runtime guidance files

---

**Version**: 1.0.0 | **Ratified**: 2025-10-06 | **Last Amended**: 2025-10-06
