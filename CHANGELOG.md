# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Phase Gate Enforcement**: Pre-commit hook now enforces BOTH QA validation AND user approval before commits
  - Added user validation check to `pre-commit-gate.sh` hook
  - Previously only checked "QA validated", allowing premature commits
  - Hook now blocks commits if either "QA validated" or "User validated" is missing
  - Error messages guide orchestrator through correct workflow
- **CLAUDE.md Orchestration Instructions**: Corrected workflow to prevent premature commits
  - QA Validation Workflow: Changed from "create commits after QA PASS" to "proceed to phase gate checkpoint"
  - Phase Gate Checkpoints: Added explicit 5-step mandatory workflow with numbered steps
  - Commit Strategy: Clarified that BOTH QA validation AND user approval are required
  - Removed ambiguity that allowed orchestrator to commit before user approval
- **README.md Commit Strategy**: Updated to reflect correct workflow requiring user approval

## [0.2.0] - 2025-10-06

### Added
- **QA Agent**: New validation-only agent for quality verification
  - Runs automated checks (tests, coverage, lint, type)
  - Performs manual testing for functional changes
  - Generates structured PASS/FAIL reports
  - Never modifies code (validation only)
- **Quality Discovery System**: Auto-detects project type and quality commands
  - Supports Python, Node.js, Go, Ruby
  - Parses commands from plan.md or auto-discovers
  - Generates `.pantheon/quality-config.json`
  - Module: `pantheon.quality.discovery`, `pantheon.quality.config`
- **Quality Gate Hooks**: Three validation hooks for Claude Code
  - **SubagentStop**: Validates DEV work before completion
  - **PreCommit**: Validates quality before git commits
  - **PhaseGate**: Validates quality at phase boundaries
  - Scripts in `.pantheon/hooks/` with execute permissions
  - Auto-configured in `.claude/settings.json`
- **Parallel Execution Support**: Run up to 3 DEV agents simultaneously
  - Tasks marked `[P]` in tasks.md can execute in parallel
  - Orchestrator invokes multiple agents in single message
  - Updated `/implement` directive with parallel execution guidance
- **Multi-Agent Orchestration Guide**: Added to `CLAUDE.md`
  - DEV agent context package format
  - QA agent context package format
  - Parallel execution strategy
  - Commit strategy (orchestrator only, after QA PASS)

### Changed
- **CLI `integrate` command**: Now installs hooks and QA integration
  - Calls `install_hooks()` after Spec Kit integration
  - Reports hook installation status with validation
  - Shows warnings if hooks partially installed
- **CLI `rollback` command**: Now uninstalls hooks
  - Calls `uninstall_hooks()` during rollback
  - Preserves `.pantheon/quality-config.json`
  - Reports hook removal status
- **`/implement` directive**: Enhanced with QA validation workflow
  - Includes QA agent delegation section
  - Parallel execution examples
  - Commit strategy (only after QA PASS)
  - Rework cycle guidance (DEV fixes, QA re-validates)
- **DEV agent spec**: Updated to v2.0 with quality hooks awareness
  - References quality-config.json for commands
  - SubagentStop hook documentation
  - Workflow enhancements for multi-agent coordination

### Technical
- **New Modules**:
  - `src/pantheon/quality/discovery.py` - Quality command discovery
  - `src/pantheon/quality/config.py` - Config generation and loading
  - `src/pantheon/integrations/hooks.py` - Hook installation management
  - `src/pantheon/hooks/` - Hook scripts (bash)
  - `src/pantheon/agents/qa.md` - QA agent specification
- **Tests**: Expanded from 27 to 109 tests (92% coverage maintained)
  - 42 contract tests for quality discovery, config, hooks
  - 26 integration tests (E2E workflows)
  - 41 unit tests for Spec Kit integration
- **Type Safety**: Added `py.typed` marker to quality module
- **Hook Scripts**: Bash scripts with proper shebangs and error handling

### Documentation
- Updated README.md with v0.2.0 features
  - Quality discovery section with examples
  - Multi-agent workflow section
  - Parallel execution examples
  - Hook system documentation
  - Updated test counts (109 tests)
- Added CHANGELOG.md entry for v0.2.0
- Updated CLAUDE.md with orchestration guide

### Quality Metrics
- **Tests**: 109/109 passing (83 unit/contract + 26 integration)
- **Coverage**: 92% on core modules
- **Type Checking**: 0 errors (mypy strict mode)
- **Linting**: 0 errors (ruff)

## [0.1.1] - 2025-10-01

### Fixed
- **Spec Kit v0.0.55+ Compatibility**: Updated integration logic to properly detect and handle YAML frontmatter in Spec Kit command files
  - Integration directives now correctly insert after frontmatter closing `---` instead of after markdown headings
  - Added fallback for command files without YAML frontmatter
  - Maintains idempotency (no duplicate sections when running `pantheon integrate` multiple times)
  - All integration validation tests updated to match Spec Kit v0.0.55 structure

### Changed
- Integration functions (`integrate_implement_command`, `integrate_plan_command`, `integrate_tasks_command`) now use YAML frontmatter detection instead of markdown heading detection
- Test fixtures updated to match real Spec Kit v0.0.55 command file structure
- Test coverage increased to 92% on `spec_kit.py` (27 tests total, up from 25)

### Technical
- Added edge case tests for files without frontmatter and malformed frontmatter
- Enhanced integration validation with more robust parsing
- Verified end-to-end workflow with actual Spec Kit v0.0.55 installation

## [0.1.0] - 2025-10-01

### Added
- Initial release of Pantheon agents library
- DEV agent with 8-phase quality-focused workflow
- CLI commands: `init`, `integrate`, `rollback`, `list`
- Spec Kit integration with minimal directives approach
- Automatic backup and rollback functionality
- Comprehensive test suite (25 tests, 91% coverage on core)
- Type checking with mypy (strict mode)
- Linting with ruff
- Python 3.9+ support

### Features
- **DEV Agent Workflow**:
  - Phase 1-3: Understand → Plan → Iterate
  - Phase 4: Document with quality standards
  - Phase 5: Implement with TDD support
  - Phase 6-8: Verify → Finalize → Iterate
- **Spec Kit Integration**:
  - `/plan` enhancement with quality standards
  - `/tasks` enhancement with subtask format
  - `/implement` enhancement with DEV delegation
- **Safety Features**:
  - Timestamped backups before integration
  - Easy rollback with `pantheon rollback`
  - Validation of integration success

### Technical
- Built on Claude Code's sub-agent architecture
- Stateless sub-agent invocation pattern
- Separate context windows for clean execution
- Tool scoping for focused agent behavior
- TypedDict for type-safe return values

### Documentation
- Comprehensive README with examples
- API documentation for all functions
- Development setup guide
- Contributing guidelines

[0.2.0]: https://github.com/alex-abrams711/pantheon/releases/tag/v0.2.0
[0.1.1]: https://github.com/alex-abrams711/pantheon/releases/tag/v0.1.1
[0.1.0]: https://github.com/alex-abrams711/pantheon/releases/tag/v0.1.0
