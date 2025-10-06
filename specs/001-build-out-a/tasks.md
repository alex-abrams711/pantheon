# Tasks: Multi-Agent Quality-First Workflow

**Feature**: Pantheon v0.2.0 - Multi-Agent Quality-First Workflow
**Branch**: `001-build-out-a`
**Input**: Design documents from `/Users/alexabrams/Workspace/pantheon/specs/001-build-out-a/`

---

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
   → Tech stack: Python 3.9+, pytest, mypy, ruff
   → Structure: Single package (src/pantheon/)
2. Load design documents ✓
   → data-model.md: 7 entities (Quality Config, Hook Config, Context Packages, Reports)
   → contracts/: 3 API contracts (discovery, config, hooks)
   → research.md: 9 technical decisions
   → quickstart.md: 8-step validation workflow
3. Generate tasks by category ✓
   → Setup: Dependencies, structure
   → Tests: 3 contract tests, integration tests
   → Core: Quality modules, hook scripts, agent updates
   → Integration: CLI, Spec Kit integration, CLAUDE.md
   → Polish: Docs, validation
4. Apply task rules ✓
   → Different files = [P] for parallel
   → TDD: Tests before implementation
5. Number tasks sequentially (T001-T019) ✓
6. Generate dependency graph ✓
7. Create parallel execution examples ✓
8. Validate completeness ✓
   → All 3 contracts have tests ✓
   → All hook scripts included ✓
   → Agent updates included ✓
9. Return: SUCCESS (19 tasks ready)
```

---

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Exact file paths included in all task descriptions

---

## Phase 3.1: Setup

- [ ] **T001** Create project structure for v0.2.0 modules
  - Create `src/pantheon/quality/` directory
  - Create `src/pantheon/hooks/` directory
  - Create `tests/unit/` subdirectories for new modules
  - Create `tests/contract/` directory
  - Create `tests/integration/` directory
  - **Files**: Directory structure only
  - **Dependencies**: None

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [ ] **T002** [P] Contract tests for quality discovery API in `tests/contract/test_quality_discovery.py`
  - Implement all test cases from `contracts/quality-discovery-api.md`
  - Test `discover_quality_commands()` with plan.md, Node.js, Python, Go projects
  - Test `detect_project_type()` for all supported types
  - Test `parse_plan_quality_commands()` success and error cases
  - Tests MUST FAIL (no implementation yet)
  - **Files**: `tests/contract/test_quality_discovery.py`
  - **Dependencies**: T001

- [ ] **T003** [P] Contract tests for quality config API in `tests/contract/test_quality_config.py`
  - Implement all test cases from `contracts/quality-config-api.md`
  - Test `generate_quality_config()` creates directory, valid JSON, threshold validation
  - Test `load_quality_config()` success and error cases
  - Test `validate_quality_config()` for valid and invalid configs
  - Tests MUST FAIL (no implementation yet)
  - **Files**: `tests/contract/test_quality_config.py`
  - **Dependencies**: T001

- [ ] **T004** [P] Contract tests for hook installation API in `tests/contract/test_hook_installation.py`
  - Implement all test cases from `contracts/hook-installation-api.md`
  - Test `install_hooks()` creates directory, copies scripts, makes executable, updates settings.json
  - Test `uninstall_hooks()` removes entries, deletes directory, preserves config
  - Test `validate_hook_installation()` for valid and invalid installations
  - Tests MUST FAIL (no implementation yet)
  - **Files**: `tests/contract/test_hook_installation.py`
  - **Dependencies**: T001

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [ ] **T005** Implement quality discovery module in `src/pantheon/quality/discovery.py`
  - Implement `discover_quality_commands(project_root, plan_path)` function
  - Implement `detect_project_type(project_root)` function
  - Implement `parse_plan_quality_commands(plan_path)` function
  - Follow contract specifications exactly
  - Make T002 tests pass
  - **Files**: `src/pantheon/quality/discovery.py`, `src/pantheon/quality/__init__.py`
  - **Dependencies**: T002 (tests must exist and fail first)

- [ ] **T006** Implement quality config module in `src/pantheon/quality/config.py`
  - Implement `generate_quality_config(project_root, plan_path, coverage_threshold)` function
  - Implement `load_quality_config(project_root)` function
  - Implement `validate_quality_config(config)` function
  - Uses `discovery.py` for command discovery
  - Make T003 tests pass
  - **Files**: `src/pantheon/quality/config.py`
  - **Dependencies**: T003, T005 (tests exist, discovery implemented)

- [ ] **T007** Implement hook installation module in `src/pantheon/integrations/hooks.py`
  - Implement `install_hooks(project_root)` function
  - Implement `uninstall_hooks(project_root)` function
  - Implement `validate_hook_installation(project_root)` function
  - Copy hook scripts from package to project
  - Update .claude/settings.json with hook paths
  - Make T004 tests pass
  - **Files**: `src/pantheon/integrations/hooks.py`
  - **Dependencies**: T004 (tests exist and fail first)

---

## Phase 3.4: Hook Scripts

- [ ] **T008** [P] Create SubagentStop hook script in `src/pantheon/hooks/subagent-validation.sh`
  - Read quality config from `.pantheon/quality-config.json`
  - Validate DEV agents: tests pass, lint pass, type-check pass, no code smells
  - Validate QA agents: all quality checks executed, results files exist
  - Exit 0 if validation passes, exit 2 if fails
  - Output clear error messages for failures
  - **Files**: `src/pantheon/hooks/subagent-validation.sh`
  - **Dependencies**: T006 (quality config structure defined)

- [ ] **T009** [P] Create PreCommit hook script in `src/pantheon/hooks/pre-commit-gate.sh`
  - Read quality config from `.pantheon/quality-config.json`
  - Run tests, lint, type-check from config
  - Exit 0 if all pass, exit 2 if any fail
  - Output clear error messages with specific failures
  - **Files**: `src/pantheon/hooks/pre-commit-gate.sh`
  - **Dependencies**: T006 (quality config structure defined)

- [ ] **T010** [P] Create Phase Gate hook script in `src/pantheon/hooks/phase-gate.sh`
  - Read user message from stdin
  - Detect approval keywords (yes, proceed, phase N)
  - If approval detected, run quality validation
  - Exit 0 if validation passes or not approval, exit 2 if approval + validation fails
  - **Files**: `src/pantheon/hooks/phase-gate.sh`
  - **Dependencies**: T006 (quality config structure defined)

---

## Phase 3.5: Agent Updates

- [ ] **T011** Update DEV agent specification in `src/pantheon/agents/dev.md`
  - Version the existing `src/pantheon/agents/dev.md` document as `src/pantheon/agents/dev-v1.md`
  - Copy over `src/pantheon/agents/dev.md` as a new version to be updated
  - Remove commit logic from Phase 5 (orchestrator handles commits)
  - Update Phase 7 to return results instead of waiting for user
  - Add "Context Package" section documenting expected inputs from orchestrator
  - Ensure YAML frontmatter includes all required fields
  - Maintain existing quality-first workflow
  - **Files**: `src/pantheon/agents/dev.md`
  - **Dependencies**: None (agent update, no code dependencies)

- [ ] **T012** Create QA agent specification in `src/pantheon/agents/qa.md`
  - Create YAML frontmatter (name, description, model, tools)
  - Define Core Principles (validation-only, no code modification)
  - Document Context Package format (from data-model.md)
  - Define Workflow phases (automated checks, manual testing, report generation)
  - Define QA Report structure (from data-model.md)
  - Include Quality Standards and Guardrails sections
  - **Files**: `src/pantheon/agents/qa.md`
  - **Dependencies**: T011 (reference DEV patterns)

---

## Phase 3.6: Integration

- [ ] **T013** Update CLI integrate command in `src/pantheon/cli.py`
  - Add hook installation to `integrate` command using `hooks.install_hooks()`
  - Add hook validation reporting
  - Add error handling for hook installation failures
  - Maintain backward compatibility with existing integration logic
  - **Files**: `src/pantheon/cli.py`
  - **Dependencies**: T007 (hook installation module exists)

- [ ] **T014** Update /implement integration directive (minimal change)
  - Read existing `.claude/commands/implement.md` (if user has Spec Kit)
  - Update "## Agent Integration" section with QA agent delegation
  - Add parallel execution guidance (single message, multiple Task tools)
  - Preserve all existing Spec Kit logic
  - **Files**: Updates to Spec Kit integration in `src/pantheon/integrations/spec_kit.py`
  - **Dependencies**: T012 (QA agent spec exists)

- [ ] **T015** Add multi-agent workflow orchestration guide to `CLAUDE.md`
  - Document parallel execution strategy (max 3 DEV agents, single message)
  - Document QA validation workflow (when to invoke, context package format)
  - Document phase gate procedures (checkpoints, validation)
  - Document commit strategy (orchestrator only, after QA PASS)
  - Include context package formats for DEV and QA agents
  - Keep concise (follows user guidance: clear, simple)
  - **Files**: `CLAUDE.md`
  - **Dependencies**: T011, T012 (agent specs finalized)

---

## Phase 3.7: Integration Tests

- [ ] **T016** [P] End-to-end quality discovery test in `tests/integration/test_quality_discovery_e2e.py`
  - Create temp project with different structures (Node.js, Python, Go)
  - Test discovery with plan.md explicit commands
  - Test auto-discovery without plan.md
  - Validate quality config JSON structure
  - **Files**: `tests/integration/test_quality_discovery_e2e.py`
  - **Dependencies**: T005, T006 (discovery and config implemented)

- [ ] **T017** [P] End-to-end hook installation test in `tests/integration/test_hook_installation_e2e.py`
  - Create temp project with .claude/ directory
  - Test full install workflow
  - Validate hooks are executable
  - Validate settings.json updated
  - Test rollback/uninstall
  - **Files**: `tests/integration/test_hook_installation_e2e.py`
  - **Dependencies**: T007, T008, T009, T010 (hooks module and scripts exist)

- [ ] **T018** [P] End-to-end QA workflow test in `tests/integration/test_qa_workflow_e2e.py`
  - Simulate orchestrator invoking QA agent (from quickstart.md)
  - Provide QA context package
  - Validate QA report structure
  - Test PASS and FAIL scenarios
  - Validate manual testing logic
  - **Files**: `tests/integration/test_qa_workflow_e2e.py`
  - **Dependencies**: T012 (QA agent spec defines workflow)

---

## Phase 3.8: Polish

- [ ] **T019** [P] Update documentation for v0.2.0
  - Update `README.md` with QA agent, parallel execution, hooks
  - Add section on quality discovery
  - Update examples to show multi-agent workflow
  - Create `CHANGELOG.md` entry for v0.2.0
  - Keep changes concise (follows user guidance)
  - **Files**: `README.md`, `CHANGELOG.md`
  - **Dependencies**: All implementation complete (T005-T015)

---

## Dependencies Graph

```
Setup Phase:
T001 (structure)
  ↓
Test Phase (Parallel):
T002, T003, T004 (contract tests) [all depend on T001]
  ↓
Core Phase (Sequential):
T005 (discovery) ← T002
T006 (config) ← T003, T005
T007 (hooks module) ← T004
  ↓
Hook Scripts Phase (Parallel):
T008, T009, T010 (hook scripts) [all depend on T006]
  ↓
Agent Phase (Sequential):
T011 (update DEV)
T012 (create QA) ← T011
  ↓
Integration Phase (Sequential):
T013 (CLI) ← T007
T014 (Spec Kit) ← T012
T015 (CLAUDE.md) ← T011, T012
  ↓
Integration Tests Phase (Parallel):
T016 (discovery e2e) ← T005, T006
T017 (hooks e2e) ← T007, T008, T009, T010
T018 (QA e2e) ← T012
  ↓
Polish Phase:
T019 (docs) ← All implementation complete
```

---

## Parallel Execution Examples

### Wave 1: Contract Tests (3 parallel)
```
# In Claude Code, invoke 3 DEV agents in single message:
Use the DEV agent to implement T002: Contract tests for quality discovery API
Use the DEV agent to implement T003: Contract tests for quality config API
Use the DEV agent to implement T004: Contract tests for hook installation API
```

### Wave 2: Hook Scripts (3 parallel)
```
# After T006 complete:
Use the DEV agent to implement T008: SubagentStop hook script
Use the DEV agent to implement T009: PreCommit hook script
Use the DEV agent to implement T010: Phase Gate hook script
```

### Wave 3: Integration Tests (3 parallel)
```
# After all implementation complete:
Use the DEV agent to implement T016: Quality discovery e2e test
Use the DEV agent to implement T017: Hook installation e2e test
Use the DEV agent to implement T018: QA workflow e2e test
```

---

## Notes

- **[P] Tasks**: 11 tasks can run in parallel (T002-T004, T008-T010, T016-T018, T019)
- **TDD Enforcement**: Tests (T002-T004) MUST fail before implementation (T005-T007)
- **Quality Standards**: All tasks must pass pytest, mypy, ruff before completion
- **Commit Strategy**: Atomic commits after each task or logical batch
- **User Guidance**: Keep implementation clear, concise, simple - minimal changes to Spec Kit

---

## Validation Checklist

- [x] All 3 contracts have corresponding tests (T002-T004 → T005-T007)
- [x] All hook scripts included (T008-T010)
- [x] All agent updates included (T011-T012)
- [x] All tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks are truly independent (different files, no shared state)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] Integration tests validate end-to-end workflows (quickstart.md scenarios)

---

## Success Criteria

All 19 tasks complete when:
- 27+ tests passing (existing) + new tests for quality modules and hooks
- Coverage ≥92% (maintain current level)
- 0 mypy errors (strict mode)
- 0 ruff errors
- All contract tests pass
- All integration tests pass (quickstart scenarios)
- Benchmark Test-2 target: 85+/100 score, 0 failing tests

---

**Ready for `/implement` command to execute tasks with DEV agents**
