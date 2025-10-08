# Pantheon Agents Library

A quality-focused agents library for Claude Code with seamless Spec Kit integration.

Pantheon provides production-ready agents that implement structured, quality-first development workflows. The DEV agent ensures every implementation includes proper testing, quality verification, and atomic commits. The QA agent validates all changes before commits are created.

## Features

- 🎯 **Multi-Agent Quality Workflow**: DEV + QA agents with built-in validation loops
- 🔍 **Auto Quality Discovery**: Detects project type and discovers test/lint/type commands
- 🪝 **Quality Gate Hooks**: SubagentStop, PreCommit, and PhaseGate validation
- ⚡ **Parallel Execution**: Run up to 3 DEV agents simultaneously for independent tasks
- 🔧 **Spec Kit Integration**: Seamless integration with GitHub's Spec Kit framework
- 🔄 **Safe Rollback**: Automatic backups and easy rollback capability
- 📦 **Simple Distribution**: Install via `uvx` - no configuration needed
- ✅ **Comprehensive Testing**: 109 tests with 92% coverage on core functionality

## Quick Start

### Installation

Install and initialize in one step using `uvx`:

```bash
# Once published to PyPI
uvx pantheon-agents init
```

For local development, install from source:

```bash
# Clone and install
git clone https://github.com/alex-abrams711/pantheon.git
cd pantheon
uv tool install .

# Initialize in your project
pantheon init
```

### Basic Usage

#### 1. Initialize Agents

Copy the DEV and QA agents to your project:

```bash
pantheon init
```

This creates `.claude/agents/dev.md` and `.claude/agents/qa.md` in your project.

#### 2. Integrate with Spec Kit (Optional)

If you have Spec Kit installed, integrate DEV + QA agents and install quality hooks:

```bash
pantheon integrate
```

This:
- Adds minimal directives to `/implement`, `/plan`, and `/tasks` commands
- Installs quality gate hooks (SubagentStop, PreCommit, PhaseGate)
- Updates `.claude/settings.json` with hook configuration

#### 3. Use DEV Agent

In Claude Code, DEV will be automatically available:

```
Use the DEV agent to implement the authentication feature
```

Or with Spec Kit:

```
/implement
```

## Commands

### `pantheon init`

Initialize Pantheon agents in your project.

**Options:**
- `--auto-integrate` - Automatically integrate with Spec Kit if detected (skip prompt)

**What it does:**
- Creates `.claude/agents/` directory
- Copies DEV and QA agents to your project
- Detects Spec Kit and offers integration

**Example:**
```bash
pantheon init --auto-integrate
```

### `pantheon integrate`

Integrate DEV + QA agents with Spec Kit commands and install quality hooks.

**Options:**
- `--dry-run` - Preview changes without applying them

**What it does:**
- Creates timestamped backup of command files
- Adds integration directives to `/implement`, `/plan`, `/tasks`
- Installs quality gate hooks in `.pantheon/hooks/`
- Updates `.claude/settings.json` with hook paths
- Validates integration success

**Example:**
```bash
pantheon integrate --dry-run  # Preview changes
pantheon integrate            # Apply integration
```

### `pantheon rollback`

Rollback to the most recent backup and uninstall quality hooks.

**Options:**
- `--force` - Skip confirmation prompt

**What it does:**
- Finds most recent integration backup
- Restores original command files
- Removes quality gate hooks from `.pantheon/hooks/`
- Cleans up `.claude/settings.json`
- Preserves `.pantheon/quality-config.json`
- Reports restored files

**Example:**
```bash
pantheon rollback --force
```

### `pantheon list`

List available agents and their installation status.

**Example:**
```bash
pantheon list
```

## Quality Discovery

Pantheon automatically discovers quality commands for your project type:

### Supported Project Types
- **Python**: pytest, ruff, mypy
- **Node.js**: npm test, eslint, tsc
- **Go**: go test, golangci-lint
- **Ruby**: rspec, rubocop

### Discovery Process
1. Detects project type from files (package.json, pyproject.toml, go.mod)
2. Extracts commands from plan.md if available
3. Auto-discovers common commands if plan.md not found
4. Generates `.pantheon/quality-config.json` with discovered commands

### Example Quality Config
```json
{
  "version": "1.0",
  "project_type": "python",
  "commands": {
    "test": "pytest tests/ -v",
    "lint": "ruff check src/ tests/",
    "type_check": "mypy src/ --strict",
    "coverage": "pytest --cov=src --cov-report=term-missing"
  },
  "thresholds": {
    "coverage_branches": 80
  },
  "discovery_source": "plan.md"
}
```

## Multi-Agent Workflow

Pantheon uses a two-agent architecture with orchestration:

### DEV Agent
Implements features with quality-first approach:
- Writes code and tests
- Runs quality checks locally
- Iterates until all checks pass
- Returns SUCCESS/FAIL to orchestrator

### QA Agent
Validates completed work before commits:
- Runs all automated checks (tests, coverage, lint, type)
- Performs manual testing if functional changes
- Generates structured PASS/FAIL reports
- Never modifies code (validation only)

### Parallel Execution
For independent tasks marked `[P]` in tasks.md:
- Invoke up to 3 DEV agents in a single message
- All agents execute simultaneously
- Orchestrator waits for all completions
- Example:
  ```
  Use DEV agent to implement T001: Add login endpoint
  Use DEV agent to implement T002: Add logout endpoint
  Use DEV agent to implement T003: Add password reset
  ```

### Commit Strategy
- QA validates batch of completed tasks
- If QA returns PASS: orchestrator presents phase completion report to user
- User approves phase completion (types "yes")
- After user approval: orchestrator creates commit
- If QA returns FAIL: DEV agents fix issues, QA re-validates
- Atomic commits with quality metrics in message

**Quality Gates**: Pre-commit hook enforces both QA validation AND user approval before allowing commits.

## DEV Agent Workflow

The DEV agent implements an 8-phase quality-focused workflow:

### Phase 1-3: Understand → Plan → Iterate
- Asks clarifying questions
- Creates comprehensive implementation plan
- Refines plan based on feedback

### Phase 4: Document
Creates task documentation with:
- Detailed implementation plan
- Quality standards (lint, type check, test commands)
- Task list with verification steps
- Success criteria

### Phase 5: Implement
For each subtask:
1. **Code**: Write implementation
2. **Test**: Write unit tests
3. **Verify Acceptance**: Ensure criteria met
4. **Verify Quality**: Check linting, types, tests
5. **Commit**: Atomic commit with clear message

### Phase 6-8: Verify → Finalize → Iterate
- Final verification of all success criteria
- Present results to user
- Handle feedback and rework if needed

## Integration with Spec Kit

When integrated with Spec Kit, the DEV agent enhances your workflow:

### `/plan` Enhancement
Includes quality standards in plan output:
- Lint command (e.g., `npm run lint`)
- Type check command (e.g., `tsc --noEmit`)
- Test command (e.g., `npm test`)
- Coverage requirement

### `/tasks` Enhancement
Task format includes subtasks as acceptance criteria:
```markdown
**T001** [Task Description] (`path/to/file.ext`)
- [ ] Subtask 1: [Specific acceptance criterion]
- [ ] Subtask 2: [Specific acceptance criterion]
- Dependencies: [Task IDs or "None"]
- Implements: [FR-XXX references]
```

### `/implement` Enhancement
Delegates task execution to DEV and QA agents:
1. **DEV Execution**: Prepares context package and invokes DEV for each task
2. **Parallel Support**: Runs up to 3 DEV agents simultaneously for `[P]` tasks
3. **QA Validation**: Invokes QA agent to validate batch of completed tasks
4. **Commit on PASS**: Creates commits only after QA returns PASS status
5. **Rework on FAIL**: Re-invokes DEV to fix issues if QA returns FAIL

## Architecture

Pantheon uses Claude Code's sub-agent architecture:

- **Separate Context Windows**: DEV and QA operate independently, preserving main conversation
- **Stateless Invocation**: Each agent call is fresh, state managed by orchestrator
- **Tool Scoping**:
  - DEV has implementation tools (Read, Write, Edit, Bash)
  - QA has validation tools (Read, Bash, Glob, Grep, Browser, Playwright)
- **Quality Focus**: Built-in verification loops and quality gates ensure standards are met
- **Hook System**: SubagentStop, PreCommit, and PhaseGate hooks validate work automatically

## Safety & Rollback

Every integration creates a timestamped backup:

```
.integration-backup-20251001-143000/
├── implement.md
├── plan.md
└── tasks.md
```

Rollback is always available:
```bash
pantheon rollback
```

## Requirements

- Python 3.9+
- Claude Code (for using agents)
- Spec Kit v0.0.55+ (optional, for integration)

### Spec Kit Compatibility

Pantheon supports both Spec Kit command formats:

- **Pre-v0.0.57**: `implement.md`, `plan.md`, `tasks.md`
- **v0.0.57+**: `speckit.implement.md`, `speckit.plan.md`, `speckit.tasks.md`

Format detection is automatic - Pantheon will detect which version you have installed and integrate accordingly.

**Tested versions:** v0.0.55, v0.0.56, v0.0.57, v0.0.58

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/alex-abrams711/pantheon.git
cd pantheon

# Create virtual environment
uv venv
source .venv/bin/activate

# Install with dev dependencies
uv pip install -e ".[dev]"
```

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/pantheon --cov-report=term-missing

# Type checking
mypy src/

# Linting
ruff check src/ tests/
```

### Quality Standards

- **Test Coverage**: >80% on core modules (currently 92%)
- **Type Checking**: mypy strict mode, 0 errors
- **Linting**: ruff with pycodestyle, pyflakes, isort, pep8-naming
- **All Tests Pass**: 109/109 tests passing (83 unit/contract + 26 integration)

## Contributing

Contributions welcome! Please:

1. Follow existing code style (ruff + mypy)
2. Add tests for new functionality
3. Ensure all quality checks pass
4. Update documentation as needed

## License

MIT License - see LICENSE file for details

## Links

- **Repository**: https://github.com/alex-abrams711/pantheon
- **Issues**: https://github.com/alex-abrams711/pantheon/issues
- **Claude Code**: https://docs.claude.com/en/docs/claude-code
- **Spec Kit**: https://github.com/github/spec-kit

## Acknowledgments

Built on Claude Code's sub-agent architecture and designed to integrate seamlessly with GitHub's Spec Kit framework.
