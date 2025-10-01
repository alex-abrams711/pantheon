# Pantheon Implementation Tasks

**Project**: Pantheon Agents Library
**Goal**: Build a Python CLI tool for distributing quality-focused agents and integrating with Spec Kit
**Estimated Duration**: ~4-6 hours

---

## Phase 1: Project Foundation

### T001: Python Package Setup (`pyproject.toml`) ✅
- [x] Create pyproject.toml with package metadata
  - Package name: `pantheon-agents`
  - Version: 0.1.0
  - Entry point: `pantheon` CLI command
  - Dependencies: click, pyyaml, pathlib
- [x] Configure build system (hatchling or setuptools)
- [x] Add package description and repository URL
- [x] Verification: Run `uv build` successfully
- **Dependencies**: None
- **Quality Standards**:
  - [x] Valid TOML syntax
  - [x] All required fields present
  - [x] Builds without errors

### T002: Project Structure (`src/pantheon/`) ✅
- [x] Create directory structure:
  ```
  src/pantheon/
  ├── __init__.py
  ├── cli.py
  ├── agents/
  │   └── dev.md
  └── integrations/
      └── spec_kit.py
  ```
- [x] Create empty __init__.py files
- [x] Add version constant to __init__.py
- [x] Verification: Import package successfully
- **Dependencies**: T001
- **Quality Standards**:
  - [x] All directories created
  - [x] Package importable
  - [x] No import errors

---

## Phase 2: Agent Preparation

### T003: DEV Agent Adaptation (`src/pantheon/agents/dev.md`) ✅
- [x] Copy agents/dev.md to src/pantheon/agents/dev.md
- [x] Add YAML frontmatter with:
  - name: DEV
  - description: Senior Software Engineer
  - model: claude-sonnet-4-5
  - tools: [Read, Write, Edit, Bash, Glob, Grep, mcp__browser__*]
- [x] Remove Phase 1-4 (orchestrator responsibilities)
- [x] Update Phase 5: Remove commit logic (orchestrator handles)
- [x] Update Phase 7: Return results instead of waiting for user
- [x] Add "Context Package" section explaining orchestrator inputs
- [x] Verification: YAML frontmatter parses correctly
- **Dependencies**: T002
- **Quality Standards**:
  - [x] Valid YAML syntax (test with PyYAML)
  - [x] All required frontmatter fields present
  - [x] Markdown structure preserved
  - [x] No broken references

---

## Phase 3: CLI Implementation

### T004: CLI Entry Point (`src/pantheon/cli.py`) ✅
- [x] Import Click framework
- [x] Create main CLI group with --version flag
- [x] Add basic error handling
- [x] Add help text and descriptions
- [x] Verification: Run `pantheon --help` successfully
- **Dependencies**: T001
- **Quality Standards**:
  - [x] CLI command available
  - [x] Help text displays correctly
  - [x] Version displays correctly
  - [x] No runtime errors

### T005: Init Command (`src/pantheon/cli.py`) ✅
- [x] Implement `pantheon init` command
- [x] Check for/create `.claude/` directory
- [x] Check for/create `.claude/agents/` directory
- [x] Copy dev.md from package to `.claude/agents/dev.md`
- [x] Detect Spec Kit (.specify/ and .claude/commands/)
- [x] Prompt for integration if Spec Kit found
- [x] Add success/error messages
- [x] Verification: Run init in test directory, verify file copied
- **Dependencies**: T003, T004
- **Quality Standards**:
  - [x] File operations work correctly
  - [x] Handles existing files gracefully
  - [x] Clear user feedback
  - [x] No file corruption

### T006: List Command (`src/pantheon/cli.py`) ✅
- [x] Implement `pantheon list` command
- [x] List agents available in package
- [x] Check which agents installed locally
- [x] Display formatted output (table or list)
- [x] Verification: Run list, verify output correct
- **Dependencies**: T004
- **Quality Standards**:
  - [x] Accurate agent detection
  - [x] Clean, readable output
  - [x] No errors if .claude/ missing

---

## Phase 4: Spec Kit Integration

### T007: Integration Utilities (`src/pantheon/integrations/spec_kit.py`) ✅
- [x] Create verify_agents_installed() function
  - Check .claude/agents/dev.md exists
- [x] Create verify_spec_kit() function
  - Check .specify/ exists
  - Check .claude/commands/ exists
- [x] Create create_backup() function
  - Generate timestamped backup directory
  - Copy implement.md, plan.md, tasks.md
  - Return backup directory path
- [x] Create validate_integration() function
  - Parse modified files as markdown
  - Verify sections present
  - Return validation results
- [x] Verification: Unit test each function
- **Dependencies**: T002
- **Quality Standards**:
  - [x] All functions have docstrings
  - [x] Error handling for missing files
  - [x] Returns clear success/failure status
  - [x] Unit tests pass

### T008: Command Integration Functions (`src/pantheon/integrations/spec_kit.py`) ✅
- [x] Create integrate_implement_command() function
  - Read .claude/commands/implement.md
  - Insert "Agent Integration" section after title
  - Write updated file
- [x] Create integrate_plan_command() function
  - Read .claude/commands/plan.md
  - Insert "Quality Standards" section
  - Write updated file
- [x] Create integrate_tasks_command() function
  - Read .claude/commands/tasks.md
  - Insert "Task Format" section
  - Write updated file
- [x] Verification: Test on sample Spec Kit files
- **Dependencies**: T007
- **Quality Standards**:
  - [x] Preserves existing content
  - [x] Inserts at correct location
  - [x] No content corruption
  - [x] Idempotent (can run safely twice)

### T009: Integration Directive Content (`src/pantheon/integrations/spec_kit.py`) ✅
- [x] Define IMPLEMENT_DIRECTIVE constant with markdown text
- [x] Define PLAN_DIRECTIVE constant with markdown text
- [x] Define TASKS_DIRECTIVE constant with markdown text
- [x] Add section markers for easy detection
- [x] Verification: Directives match design spec
- **Dependencies**: T008
- **Quality Standards**:
  - [x] Valid markdown syntax
  - [x] Clear, concise instructions
  - [x] Matches design document exactly

### T010: Main Integration Flow (`src/pantheon/integrations/spec_kit.py`) ✅
- [x] Create integrate_spec_kit() main function
- [x] Step 1: Call verify_agents_installed()
- [x] Step 2: Call verify_spec_kit()
- [x] Step 3: Call create_backup()
- [x] Step 4: Call integration functions
- [x] Step 5: Call validate_integration()
- [x] Step 6: Print summary report
- [x] Add error handling for each step
- [x] Verification: Integration test on sample project
- **Dependencies**: T007, T008, T009
- **Quality Standards**:
  - [x] All steps execute in order
  - [x] Rollback on any failure
  - [x] Clear status reporting
  - [x] Backup created successfully

### T011: Integrate Command (`src/pantheon/cli.py`) ✅
- [x] Implement `pantheon integrate` command
- [x] Import integrate_spec_kit from integrations
- [x] Call integrate_spec_kit() with error handling
- [x] Display results to user
- [x] Add --dry-run flag for preview
- [x] Verification: Run integrate on test project
- **Dependencies**: T010
- **Quality Standards**:
  - [x] Command works end-to-end
  - [x] User feedback clear
  - [x] Errors handled gracefully
  - [x] Dry-run shows changes without applying

---

## Phase 5: Rollback & Safety

### T012: Rollback Implementation (`src/pantheon/integrations/spec_kit.py`)
- [ ] Create find_latest_backup() function
  - Search for .integration-backup-* directories
  - Return most recent by timestamp
- [ ] Create restore_files() function
  - Copy files from backup to .claude/commands/
  - Verify restoration
- [ ] Create rollback_integration() function
  - Find latest backup
  - Restore files
  - Report results
- [ ] Verification: Test rollback after integration
- **Dependencies**: T007
- **Quality Standards**:
  - [ ] Finds correct backup
  - [ ] Restores all files
  - [ ] Verification step confirms restoration
  - [ ] No data loss

### T013: Rollback Command (`src/pantheon/cli.py`)
- [ ] Implement `pantheon rollback` command
- [ ] Import rollback_integration from integrations
- [ ] Add confirmation prompt (unless --force)
- [ ] Display backup location and files to restore
- [ ] Call rollback_integration()
- [ ] Show success/failure message
- [ ] Verification: Full integration → rollback cycle
- **Dependencies**: T012
- **Quality Standards**:
  - [ ] Confirmation prevents accidents
  - [ ] Clear messaging
  - [ ] Rollback successful
  - [ ] Files match pre-integration state

---

## Phase 6: Testing & Quality

### T014: Unit Tests (`tests/`)
- [ ] Create tests/ directory structure
- [ ] Write tests for verify_agents_installed()
- [ ] Write tests for verify_spec_kit()
- [ ] Write tests for create_backup()
- [ ] Write tests for validate_integration()
- [ ] Write tests for integration functions
- [ ] Write tests for rollback functions
- [ ] Verification: pytest runs all tests successfully
- **Dependencies**: T007, T008, T012
- **Quality Standards**:
  - [ ] Test coverage >80%
  - [ ] All edge cases covered
  - [ ] Tests use temporary directories
  - [ ] All tests pass

### T015: Integration Tests (`tests/`)
- [ ] Create mock Spec Kit project structure
- [ ] Test full init flow
- [ ] Test full integrate flow
- [ ] Test full rollback flow
- [ ] Test error scenarios (missing files, invalid YAML)
- [ ] Test idempotency (run twice, same result)
- [ ] Verification: All integration tests pass
- **Dependencies**: T014
- **Quality Standards**:
  - [ ] End-to-end scenarios covered
  - [ ] Tests clean up after themselves
  - [ ] No test pollution
  - [ ] All tests pass

### T016: Code Quality Checks
- [ ] Add ruff or black for formatting
- [ ] Add mypy for type checking
- [ ] Add configuration files (.ruff.toml or pyproject.toml)
- [ ] Run formatter on all code
- [ ] Run type checker on all code
- [ ] Fix all issues
- [ ] Verification: No linting/type errors
- **Dependencies**: T015
- **Quality Standards**:
  - [ ] Ruff/Black: 0 errors
  - [ ] Mypy: 0 errors
  - [ ] Consistent code style
  - [ ] Type hints on all functions

---

## Phase 7: Documentation & Distribution

### T017: README Documentation (`README.md`)
- [ ] Create README.md with:
  - Project description
  - Installation instructions (uvx)
  - Usage examples for each command
  - Integration workflow explanation
  - Troubleshooting section
- [ ] Add badges (if applicable)
- [ ] Include link to DEV agent methodology
- [ ] Verification: README is clear and complete
- **Dependencies**: T016
- **Quality Standards**:
  - [ ] All commands documented
  - [ ] Examples are accurate
  - [ ] Links work
  - [ ] Markdown renders correctly

### T018: Package Publishing Prep
- [ ] Verify pyproject.toml completeness
- [ ] Add LICENSE file (MIT or Apache 2.0)
- [ ] Add CHANGELOG.md with v0.1.0 notes
- [ ] Test build: `uv build`
- [ ] Test local install: `uv pip install dist/*.whl`
- [ ] Test CLI after install
- [ ] Verification: Package installs and works
- **Dependencies**: T017
- **Quality Standards**:
  - [ ] Build succeeds
  - [ ] Install succeeds
  - [ ] All commands work after install
  - [ ] No missing files

### T019: Repository Documentation
- [ ] Update CLAUDE.md with implementation notes
- [ ] Create CONTRIBUTING.md guidelines
- [ ] Add examples/ directory with sample integration
- [ ] Document architecture decisions
- [ ] Verification: Documentation complete
- **Dependencies**: T018
- **Quality Standards**:
  - [ ] Clear contribution guidelines
  - [ ] Architecture documented
  - [ ] Examples work correctly
  - [ ] No TODOs left

---

## Phase 8: Final Verification

### T020: End-to-End Validation
- [ ] Create fresh test project
- [ ] Install Spec Kit in test project
- [ ] Run `uvx pantheon init`
- [ ] Run `pantheon integrate`
- [ ] Verify directives in all command files
- [ ] Test /implement with sample task
- [ ] Verify DEV agent invoked
- [ ] Test rollback
- [ ] Verification: Complete workflow successful
- **Dependencies**: T019
- **Quality Standards**:
  - [ ] All commands work
  - [ ] Integration successful
  - [ ] DEV agent invokes correctly
  - [ ] Rollback restores correctly

### T021: Release Preparation
- [ ] Tag version v0.1.0 in git
- [ ] Create GitHub release with notes
- [ ] Test PyPI test upload (optional)
- [ ] Document release process
- [ ] Verification: Ready for distribution
- **Dependencies**: T020
- **Quality Standards**:
  - [ ] Git tag created
  - [ ] Release notes accurate
  - [ ] Package ready for distribution
  - [ ] All docs updated

---

## Success Criteria

- ✅ `pantheon init` installs DEV agent successfully
- ✅ `pantheon integrate` adds directives to Spec Kit commands
- ✅ `pantheon rollback` restores pre-integration state
- ✅ `pantheon list` shows available agents
- ✅ DEV agent has valid YAML frontmatter
- ✅ Integration directives match design specification
- ✅ All tests pass (unit + integration)
- ✅ Code quality: 0 lint errors, 0 type errors
- ✅ Documentation complete and accurate
- ✅ Package builds and installs correctly
- ✅ End-to-end workflow validated

---

## Notes & Decisions

_This section will be updated during implementation to record key decisions and learnings._
