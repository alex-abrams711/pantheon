# Pantheon Agents Library

A quality-focused agents library for Claude Code with seamless Spec Kit integration.

Pantheon provides production-ready agents that implement structured, quality-first development workflows. The DEV agent ensures every implementation includes proper testing, quality verification, and atomic commits.

## Features

- 🎯 **Quality-First Workflow**: Built-in verification loops for acceptance criteria and quality standards
- 🔧 **Spec Kit Integration**: Seamless integration with GitHub's Spec Kit framework
- 🔄 **Safe Rollback**: Automatic backups and easy rollback capability
- 📦 **Simple Distribution**: Install via `uvx` - no configuration needed
- ✅ **Comprehensive Testing**: 25 tests with 91% coverage on core functionality

## Quick Start

### Installation

Install and initialize in one step using `uvx`:

```bash
uvx pantheon-agents init
```

Or install globally:

```bash
uv tool install pantheon-agents
pantheon init
```

### Basic Usage

#### 1. Initialize Agents

Copy the DEV agent to your project:

```bash
pantheon init
```

This creates `.claude/agents/dev.md` in your project.

#### 2. Integrate with Spec Kit (Optional)

If you have Spec Kit installed, integrate DEV agent with your commands:

```bash
pantheon integrate
```

This adds minimal directives to `/implement`, `/plan`, and `/tasks` commands.

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
- Copies DEV agent to your project
- Detects Spec Kit and offers integration

**Example:**
```bash
pantheon init --auto-integrate
```

### `pantheon integrate`

Integrate DEV agent with Spec Kit commands.

**Options:**
- `--dry-run` - Preview changes without applying them

**What it does:**
- Creates timestamped backup of command files
- Adds integration directives to `/implement`, `/plan`, `/tasks`
- Validates integration success

**Example:**
```bash
pantheon integrate --dry-run  # Preview changes
pantheon integrate            # Apply integration
```

### `pantheon rollback`

Rollback to the most recent backup.

**Options:**
- `--force` - Skip confirmation prompt

**What it does:**
- Finds most recent integration backup
- Restores original command files
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
Delegates task execution to DEV agent:
1. Prepares context package (task, requirements, quality standards)
2. Invokes DEV sub-agent using Task tool
3. Processes results and marks tasks complete
4. Creates commits at phase boundaries

## Architecture

Pantheon uses Claude Code's sub-agent architecture:

- **Separate Context Windows**: DEV operates independently, preserving main conversation
- **Stateless Invocation**: Each DEV call is fresh, state managed by orchestrator
- **Tool Scoping**: DEV has only implementation tools (Read, Write, Edit, Bash)
- **Quality Focus**: Built-in verification loops ensure standards are met

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
- Spec Kit (optional, for integration)

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

- **Test Coverage**: >80% on core modules (currently 91%)
- **Type Checking**: mypy strict mode, 0 errors
- **Linting**: ruff with pycodestyle, pyflakes, isort, pep8-naming
- **All Tests Pass**: 25/25 tests passing

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
