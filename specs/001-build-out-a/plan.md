
# Implementation Plan: Multi-Agent Quality-First Workflow

**Branch**: `001-build-out-a` | **Date**: 2025-10-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/alexabrams/Workspace/pantheon/specs/001-build-out-a/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

Pantheon v0.2.0 introduces a multi-agent quality-first workflow with parallel execution and deterministic quality enforcement. The system implements independent DEV and QA agents orchestrated through Claude Code's sub-agent architecture, supporting up to 3 parallel DEV agents for independent tasks. Quality gates enforce verification through SubagentStop, PreCommit, and Phase Gate hooks, preventing code quality compromises. The system is project-agnostic, auto-discovering quality commands from project structure. Target: 85+/100 benchmark score with 0 failing tests (up from 67.5/100 with 43 failures).

## Technical Context
**Language/Version**: Python 3.9+
**Primary Dependencies**: click (CLI), pyyaml (config), Claude Code sub-agent APIs
**Storage**: File system (.pantheon/quality-config.json, .claude/settings.json, .claude/agents/*.md)
**Testing**: pytest (27 tests, 92% coverage), mypy (strict mode), ruff (linting)
**Target Platform**: Cross-platform CLI (macOS, Linux, Windows), installable via uvx
**Project Type**: Single Python package (CLI tool + agents library)
**Performance Goals**: <1s CLI response time, parallel DEV agent execution (up to 3), hook validation <5s
**Constraints**: Keep Spec Kit integration minimal (directive insertion only), maintain backward compatibility with Pantheon v0.1.x projects, support project-agnostic quality discovery
**Scale/Scope**: Library supporting unlimited projects, 2 agents (DEV + QA), 3 hooks, benchmark score 85+/100

**User Guidance**: Keep plan clear, concise, and simple. This library implements a workflow but should not drastically change the already very useful Spec Kit workflow.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Sub-Agent Architecture**: ✅ PASS
- QA agent operates in separate context window alongside DEV agent
- Both agents are stateless (receive context packages on each invocation)
- State managed by orchestrator (main Claude agent)
- Tool scoping: DEV and QA have only implementation/validation tools (no web access)

**II. Minimal Integration**: ✅ PASS
- Updates to /implement use existing "## Agent Integration" section (minimal directive insertion)
- Workflow orchestration moves to CLAUDE.md (not Spec Kit commands)
- Integration still creates timestamped backups and supports rollback
- Preserves all existing Spec Kit functionality

**III. Quality-First Execution**: ✅ PASS
- QA agent enforces independent validation after DEV completion
- Hooks provide deterministic quality gates (SubagentStop, PreCommit, Phase Gate)
- TDD methodology maintained in DEV agent
- Verification loops prevent partial implementations
- Max 3 attempts before halting and reporting to user

**IV. Separation of Concerns**: ✅ PASS
- Orchestrator: task analysis, parallel execution, QA invocation, commits, user checkpoints
- DEV agents: implementation, testing, self-verification
- QA agent: independent validation, manual testing, issue reporting
- Sub-agents do NOT create commits (orchestrator only)

**V. Simplicity and KISS**: ✅ PASS
- Hook scripts are simple shell scripts reading from quality-config.json
- Quality discovery uses straightforward file analysis (package.json, pyproject.toml)
- Parallel execution limited to 3 agents (prevents complexity)
- Agent integration preserves minimal directive approach
- CLAUDE.md contains orchestration guide (keeps Spec Kit simple)

**VI. Distribution and Accessibility**: ✅ PASS
- Continues using uvx distribution model
- `pantheon integrate` installs hooks automatically
- Quality discovery is automatic (no manual configuration)
- Hook installation in .pantheon/ keeps project organized

**VII. Versioning and Backward Compatibility**: ✅ PASS
- QA agent is new (qa.md) with version in YAML frontmatter
- DEV agent update (remove commits) is minor version compatible
- Hook installation is opt-in via `pantheon integrate`
- v0.1.x projects continue working without migration

**Gate Result**: ✅ PASS - No constitutional violations. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/pantheon/
├── cli.py                    # Main CLI entry point (existing)
├── integrations/
│   ├── __init__.py
│   ├── spec_kit.py          # Existing Spec Kit integration
│   └── hooks.py             # New: Hook installation logic
├── agents/
│   ├── dev.md               # Existing DEV agent (to be updated)
│   └── qa.md                # New: QA agent specification
├── hooks/
│   ├── subagent-validation.sh   # New: SubagentStop hook
│   ├── pre-commit-gate.sh       # New: PreCommit hook
│   └── phase-gate.sh            # New: Phase Gate hook
└── quality/
    ├── __init__.py
    ├── discovery.py         # New: Project-agnostic quality command discovery
    └── config.py            # New: Quality config generation

tests/
├── unit/
│   ├── test_hooks.py        # New: Hook installation tests
│   ├── test_discovery.py    # New: Quality discovery tests
│   └── test_config.py       # New: Config generation tests
├── integration/
│   └── test_qa_workflow.py  # New: End-to-end QA workflow test
└── contract/
    └── test_agent_specs.py  # New: Agent specification validation
```

**Structure Decision**: Single Python package. This feature adds new modules (quality/, hooks in agents/) and updates existing integration logic. Tests follow existing unit/integration/contract structure. Agent files (.md) are in src/pantheon/agents/ for packaging, installed to user projects via CLI.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:

1. **Contract Test Tasks** (from contracts/):
   - T001: Contract tests for quality discovery API [P]
   - T002: Contract tests for quality config API [P]
   - T003: Contract tests for hook installation API [P]
   - Each contract → one task with failing tests
   - Mark [P] for parallel (independent modules)

2. **Core Implementation Tasks** (TDD order):
   - T004: Implement quality discovery module (make T001 pass)
   - T005: Implement quality config module (make T002 pass)
   - T006: Implement hook installation module (make T003 pass)
   - Sequential after contract tests complete

3. **Hook Script Tasks**:
   - T007: Create SubagentStop hook script [P]
   - T008: Create PreCommit hook script [P]
   - T009: Create Phase Gate hook script [P]
   - Parallel (independent bash scripts)

4. **Agent Update Tasks**:
   - T010: Update DEV agent (dev.md) - remove commit logic
   - T011: Create QA agent specification (qa.md)
   - Sequential (T011 may reference T010 patterns)

5. **Integration Tasks**:
   - T012: Update CLI integrate command for hook installation
   - T013: Update /implement integration directive (minimal change)
   - T014: Add orchestration guide to CLAUDE.md
   - Sequential (build on each other)

6. **Integration Test Tasks**:
   - T015: End-to-end quality discovery test
   - T016: End-to-end hook installation test
   - T017: End-to-end QA workflow test (from quickstart.md)
   - Can run in parallel after implementation complete

7. **Documentation Tasks**:
   - T018: Update README.md with v0.2.0 features [P]
   - T019: Update CHANGELOG.md [P]
   - Parallel (independent docs)

**Ordering Strategy**:
- **Phase/Wave 1** (Parallel): T001-T003 (contract tests)
- **Phase/Wave 2** (Sequential): T004-T006 (implementations)
- **Phase/Wave 3** (Parallel): T007-T009 (hook scripts)
- **Phase/Wave 4** (Sequential): T010-T011 (agent updates)
- **Phase/Wave 5** (Sequential): T012-T014 (integration)
- **Phase/Wave 6** (Parallel): T015-T017 (integration tests)
- **Phase/Wave 7** (Parallel): T018-T019 (docs)

**TDD Principles**:
- Contract tests written first (T001-T003)
- Tests must fail initially (no implementation yet)
- Implementation tasks make tests pass (T004-T006)
- Integration tests validate end-to-end (T015-T017)

**Parallelization Opportunities**:
- Wave 1: 3 parallel tasks (contract tests)
- Wave 3: 3 parallel tasks (hook scripts)
- Wave 6: 3 parallel tasks (integration tests)
- Wave 7: 2 parallel tasks (docs)
- Total: 11 tasks can run in parallel across 4 waves

**Estimated Output**: ~19 tasks in tasks.md, organized into 7 sequential waves/phases

**Dependencies**:
- T004 depends on T001 (contract tests exist)
- T005 depends on T002 (contract tests exist)
- T006 depends on T003 (contract tests exist)
- T012 depends on T006 (hook installation logic exists)
- T015-T017 depend on all implementation tasks (T004-T014)

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command) - 19 tasks, 11 parallelizable
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS (re-evaluated after Phase 1 design)
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none - no violations)

**Post-Design Review**:
- Design maintains constitutional compliance
- Data model is simple (JSON/Markdown files, no database)
- API contracts follow single-responsibility principle
- Hook installation is reversible with clear rollback
- Quality discovery uses straightforward file analysis (no complex heuristics)
- All components follow KISS principle

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
