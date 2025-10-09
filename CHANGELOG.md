# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-10-08

### Added
- **`/pantheon:contextualize` Slash Command**: Intelligent LLM-based quality discovery for ANY language/framework
  - Created `.claude/commands/pantheon/contextualize.md` slash command
  - Analyzes project structure using LLM reasoning (not hardcoded rules)
  - Supports unlimited languages: Python, Node.js, Go, Rust, Java, Kotlin, Ruby, PHP, .NET, Elixir, Dart, Swift, and more
  - Detects modern tools automatically (Bun, Deno, uv, vitest, Biome, etc.)
  - Handles monorepos and multi-language projects intelligently
  - Reads README/docs for custom conventions
  - Provides detailed reports with command rationale
  - Extensible module design for future contextualization (architecture, dependencies, conventions)
- **Manual Test Checklist**: Comprehensive testing guide for slash command
  - `tests/manual/test-contextualize-command.md` with 12 test scenarios
  - Covers diverse project types, edge cases, and error handling
  - Cannot be automated (requires Claude Code environment)
- **Quality Config Generation in `pantheon integrate`**: Automatically creates `.pantheon/quality-config.json`
  - Generated during `pantheon integrate` command, before hook installation
  - Auto-discovers test, lint, and type-check commands from project structure
  - Looks for plan.md in project root or specs/ subdirectories
  - Falls back to auto-discovery if no plan.md found
  - Displays discovered commands and project type to user
  - Ensures hooks have quality commands available immediately after installation
- **Orchestrator Code Gate Hook**: New hook prevents orchestrator from editing source code
  - `orchestrator-code-gate.sh` installed as PreToolUse Write/Edit hook
  - Allows: documentation files (tasks.md, README.md, CHANGELOG.md, docs/, .claude/)
  - Blocks: all source code, tests, and configuration files
  - Enforces separation of concerns: orchestrator coordinates, DEV agents implement
  - Error messages guide orchestrator to re-invoke DEV agents instead of fixing code
  - Prevents issue where orchestrator fixes QA failures directly instead of delegating to DEV

### Changed
- **Quality Discovery**: REMOVED entire `src/pantheon/quality/` module
  - Quality discovery now exclusively through `/pantheon:contextualize` slash command
  - Removed discovery.py, config.py, and all Python-based discovery logic
  - `pantheon integrate` no longer generates quality-config.json
  - Users must use `/pantheon:contextualize` in Claude Code for quality config generation
- **CLI integrate command**: Removed quality config generation
  - No longer generates .pantheon/quality-config.json during integration
  - Added reminder to use `/pantheon:contextualize` slash command
  - Updated dry-run output to reflect removal
  - Integration still installs quality hooks and updates CLAUDE.md
- **Tests**: Deleted quality discovery test files
  - Removed `tests/contract/test_quality_config.py` (22 tests)
  - Removed `tests/contract/test_quality_discovery.py` (8 tests)
  - Removed `tests/integration/test_quality_discovery_e2e.py` (7 tests)
  - Updated `test_qa_workflow_e2e.py` to remove quality module imports
- **README.md**: Updated to reflect quality module removal
  - Emphasizes `/pantheon:contextualize` as ONLY method for quality discovery
  - `pantheon integrate` no longer auto-generates quality config
  - Updated integration workflow to direct users to slash command
- **CLAUDE.md Orchestrator Role**: Added comprehensive role definition section
  - Explicit "Your Responsibilities" (✅) and "NOT Your Responsibilities" (❌) lists
  - Clear guidance: orchestrator coordinates, never implements
  - Write/Edit hooks referenced as enforcement mechanism
- **CLAUDE.md QA Validation Workflow**: Enhanced with explicit rework workflow
  - 7-step mandatory rework process when QA returns FAIL
  - DEV rework context package format with QA findings
  - Rework cycle tracking (max 3 attempts)
  - Visual workflow diagram showing orchestrator never enters "fix" box
  - Prevents orchestrator from fixing code when QA finds issues
- **hooks.py**: Updated to install orchestrator code gate hook
  - Added orchestrator-code-gate.sh to hook_mappings
  - Configured PreToolUse Write and PreToolUse Edit hooks
  - Updated validation and uninstall logic

### Removed
- **Entire `src/pantheon/quality/` module** (~500 lines total)
  - `discovery.py` - quality command discovery module
  - `config.py` - quality config generation and loading
  - `__init__.py` and `py.typed` marker files
- **Quality discovery test files** (37 tests total)
  - `tests/contract/test_quality_config.py` (22 tests)
  - `tests/contract/test_quality_discovery.py` (8 tests)
  - `tests/integration/test_quality_discovery_e2e.py` (7 tests)
- **Quality config generation from CLI**
  - Removed from `pantheon integrate` command
  - No longer auto-generates .pantheon/quality-config.json
  - All references to `generate_quality_config()` and `load_quality_config()`

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

### Migration
**BREAKING CHANGE**: Quality module has been completely removed.

**Action Required**:
1. The `src/pantheon/quality/` module no longer exists
2. `pantheon integrate` no longer auto-generates quality-config.json
3. **You MUST use `/pantheon:contextualize` in Claude Code to generate quality config**
4. Any code importing from `pantheon.quality` will fail - update imports
5. If you have existing quality-config.json, it will continue to work (hooks read it directly)

**New Workflow**:
1. Run `pantheon integrate` to install hooks and Spec Kit integration
2. Open Claude Code and run `/pantheon:contextualize` to generate quality config
3. Proceed with normal development using `/implement`

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

[0.3.0]: https://github.com/alex-abrams711/pantheon/releases/tag/v0.3.0
[0.2.0]: https://github.com/alex-abrams711/pantheon/releases/tag/v0.2.0
[0.1.1]: https://github.com/alex-abrams711/pantheon/releases/tag/v0.1.1
[0.1.0]: https://github.com/alex-abrams711/pantheon/releases/tag/v0.1.0
