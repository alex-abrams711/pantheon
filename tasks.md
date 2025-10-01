# Pantheon Implementation Tasks

**Project**: Pantheon Agents Library
**Goal**: Build a Python CLI tool for distributing quality-focused agents and integrating with Spec Kit
**Estimated Duration**: ~4-6 hours

---

## Phase 1: Project Foundation

### T001: Python Package Setup (`pyproject.toml`)
- [ ] Create pyproject.toml with package metadata
  - Package name: `pantheon-agents`
  - Version: 0.1.0
  - Entry point: `pantheon` CLI command
  - Dependencies: click, pyyaml, pathlib
- [ ] Configure build system (hatchling or setuptools)
- [ ] Add package description and repository URL
- [ ] Verification: Run `uv build` successfully
- **Dependencies**: None
- **Quality Standards**:
  - [ ] Valid TOML syntax
  - [ ] All required fields present
  - [ ] Builds without errors

### T002: Project Structure (`src/pantheon/`)
- [ ] Create directory structure:
  ```
  src/pantheon/
  ├── __init__.py
  ├── cli.py
  ├── agents/
  │   └── dev.md
  └── integrations/
      └── spec_kit.py
  ```
- [ ] Create empty __init__.py files
- [ ] Add version constant to __init__.py
- [ ] Verification: Import package successfully
- **Dependencies**: T001
- **Quality Standards**:
  - [ ] All directories created
  - [ ] Package importable
  - [ ] No import errors

---

## Phase 2: Agent Preparation

### T003: DEV Agent Adaptation (`src/pantheon/agents/dev.md`)
- [ ] Copy agents/dev.md to src/pantheon/agents/dev.md
- [ ] Add YAML frontmatter with:
  - name: DEV
  - description: Senior Software Engineer
  - model: claude-sonnet-4-5
  - tools: [Read, Write, Edit, Bash, Glob, Grep, mcp__browser__*]
- [ ] Remove Phase 1-4 (orchestrator responsibilities)
- [ ] Update Phase 5: Remove commit logic (orchestrator handles)
- [ ] Update Phase 7: Return results instead of waiting for user
- [ ] Add "Context Package" section explaining orchestrator inputs
- [ ] Verification: YAML frontmatter parses correctly
- **Dependencies**: T002
- **Quality Standards**:
  - [ ] Valid YAML syntax (test with PyYAML)
  - [ ] All required frontmatter fields present
  - [ ] Markdown structure preserved
  - [ ] No broken references

---

## Phase 3: CLI Implementation

### T004: CLI Entry Point (`src/pantheon/cli.py`)
- [ ] Import Click framework
- [ ] Create main CLI group with --version flag
- [ ] Add basic error handling
- [ ] Add help text and descriptions
- [ ] Verification: Run `pantheon --help` successfully
- **Dependencies**: T001
- **Quality Standards**:
  - [ ] CLI command available
  - [ ] Help text displays correctly
  - [ ] Version displays correctly
  - [ ] No runtime errors

### T005: Init Command (`src/pantheon/cli.py`)
- [ ] Implement `pantheon init` command
- [ ] Check for/create `.claude/` directory
- [ ] Check for/create `.claude/agents/` directory
- [ ] Copy dev.md from package to `.claude/agents/dev.md`
- [ ] Detect Spec Kit (.specify/ and .claude/commands/)
- [ ] Prompt for integration if Spec Kit found
- [ ] Add success/error messages
- [ ] Verification: Run init in test directory, verify file copied
- **Dependencies**: T003, T004
- **Quality Standards**:
  - [ ] File operations work correctly
  - [ ] Handles existing files gracefully
  - [ ] Clear user feedback
  - [ ] No file corruption

### T006: List Command (`src/pantheon/cli.py`)
- [ ] Implement `pantheon list` command
- [ ] List agents available in package
- [ ] Check which agents installed locally
- [ ] Display formatted output (table or list)
- [ ] Verification: Run list, verify output correct
- **Dependencies**: T004
- **Quality Standards**:
  - [ ] Accurate agent detection
  - [ ] Clean, readable output
  - [ ] No errors if .claude/ missing

---

## Phase 4: Spec Kit Integration

### T007: Integration Utilities (`src/pantheon/integrations/spec_kit.py`)
- [ ] Create verify_agents_installed() function
  - Check .claude/agents/dev.md exists
- [ ] Create verify_spec_kit() function
  - Check .specify/ exists
  - Check .claude/commands/ exists
- [ ] Create create_backup() function
  - Generate timestamped backup directory
  - Copy implement.md, plan.md, tasks.md
  - Return backup directory path
- [ ] Create validate_integration() function
  - Parse modified files as markdown
  - Verify sections present
  - Return validation results
- [ ] Verification: Unit test each function
- **Dependencies**: T002
- **Quality Standards**:
  - [ ] All functions have docstrings
  - [ ] Error handling for missing files
  - [ ] Returns clear success/failure status
  - [ ] Unit tests pass

### T008: Command Integration Functions (`src/pantheon/integrations/spec_kit.py`)
- [ ] Create integrate_implement_command() function
  - Read .claude/commands/implement.md
  - Insert "Agent Integration" section after title
  - Write updated file
- [ ] Create integrate_plan_command() function
  - Read .claude/commands/plan.md
  - Insert "Quality Standards" section
  - Write updated file
- [ ] Create integrate_tasks_command() function
  - Read .claude/commands/tasks.md
  - Insert "Task Format" section
  - Write updated file
- [ ] Verification: Test on sample Spec Kit files
- **Dependencies**: T007
- **Quality Standards**:
  - [ ] Preserves existing content
  - [ ] Inserts at correct location
  - [ ] No content corruption
  - [ ] Idempotent (can run safely twice)

### T009: Integration Directive Content (`src/pantheon/integrations/spec_kit.py`)
- [ ] Define IMPLEMENT_DIRECTIVE constant with markdown text
- [ ] Define PLAN_DIRECTIVE constant with markdown text
- [ ] Define TASKS_DIRECTIVE constant with markdown text
- [ ] Add section markers for easy detection
- [ ] Verification: Directives match design spec
- **Dependencies**: T008
- **Quality Standards**:
  - [ ] Valid markdown syntax
  - [ ] Clear, concise instructions
  - [ ] Matches design document exactly

### T010: Main Integration Flow (`src/pantheon/integrations/spec_kit.py`)
- [ ] Create integrate_spec_kit() main function
- [ ] Step 1: Call verify_agents_installed()
- [ ] Step 2: Call verify_spec_kit()
- [ ] Step 3: Call create_backup()
- [ ] Step 4: Call integration functions
- [ ] Step 5: Call validate_integration()
- [ ] Step 6: Print summary report
- [ ] Add error handling for each step
- [ ] Verification: Integration test on sample project
- **Dependencies**: T007, T008, T009
- **Quality Standards**:
  - [ ] All steps execute in order
  - [ ] Rollback on any failure
  - [ ] Clear status reporting
  - [ ] Backup created successfully

### T011: Integrate Command (`src/pantheon/cli.py`)
- [ ] Implement `pantheon integrate` command
- [ ] Import integrate_spec_kit from integrations
- [ ] Call integrate_spec_kit() with error handling
- [ ] Display results to user
- [ ] Add --dry-run flag for preview
- [ ] Verification: Run integrate on test project
- **Dependencies**: T010
- **Quality Standards**:
  - [ ] Command works end-to-end
  - [ ] User feedback clear
  - [ ] Errors handled gracefully
  - [ ] Dry-run shows changes without applying

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
