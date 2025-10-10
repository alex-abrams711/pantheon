# Pantheon Agents Library

A quality-focused agents library for Claude Code.

Pantheon provides production-ready DEV and QA agents that implement structured, quality-first development workflows. The DEV agent ensures every implementation includes proper testing and quality verification. The QA agent validates all changes independently.

## Features

- 🎯 **Multi-Agent Quality Workflow**: DEV + QA agents with built-in validation loops
- 🔍 **Intelligent Quality Discovery**: LLM-based discovery for ANY language/framework via `/pantheon:contextualize`
- 📊 **Quality Gate Reports**: Automated quality dashboards at key workflow checkpoints
- 🛡️ **Enforced Separation of Concerns**: Hooks prevent orchestrator from editing source code
- ⚡ **Parallel Execution**: Run up to 3 DEV agents simultaneously for independent tasks
- 📦 **Simple Distribution**: Install via `uvx` - no configuration needed
- ✅ **Comprehensive Testing**: 111+ tests with 92% coverage on core functionality

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

This creates:
- `.claude/agents/dev.md` - DEV agent for implementation
- `.claude/agents/qa.md` - QA agent for validation
- `.claude/commands/pantheon/contextualize.md` - `/pantheon:contextualize` slash command for quality discovery
- `.pantheon/hooks/` - Quality gate hooks for workflow automation

#### 2. Discover Quality Commands

In Claude Code, run the contextualize command to discover your project's quality commands:

```
/pantheon:contextualize
```

This analyzes your project and generates:
- `.pantheon/quality-config.json` - Quality commands configuration
- `.pantheon/quality-report.sh` - Executable quality status script

#### 3. Use DEV Agent

In Claude Code, invoke the DEV agent directly:

```
Use the DEV agent to implement the authentication feature
```

## Commands

### `pantheon init`

Initialize Pantheon agents in your project.

**What it does:**
- Creates `.claude/agents/` directory
- Copies DEV and QA agents to your project
- Installs `/pantheon:contextualize` slash command for quality discovery
- Installs quality gate hooks (phase-gate.sh, orchestrator-code-gate.sh)
- Configures `.claude/settings.json` with hook paths

**Example:**
```bash
pantheon init
```

## Quality Discovery

Pantheon intelligently discovers quality commands for your project using the `/pantheon:contextualize` slash command.

### Intelligent Discovery (Recommended)

In Claude Code, run:
```
/pantheon:contextualize
```

This uses LLM-based analysis to discover quality commands for **ANY language and framework**:
- Analyzes project structure (config files, package managers, build tools)
- Understands project conventions from README/docs
- Detects modern tools automatically (Bun, Deno, uv, vitest, Biome, etc.)
- Handles monorepos and multi-language projects
- Works with: Python, Node.js, Go, Rust, Java, Kotlin, Ruby, PHP, .NET, Elixir, Dart, Swift, and more

**Example output:**
```
✓ Project analyzed successfully

Project Type: Node.js (TypeScript)
Framework: React (Vite)
Package Manager: pnpm

Discovered Quality Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
test         → pnpm test
             Rationale: Found "test" script using vitest

lint         → pnpm run lint
             Rationale: Found "lint" script using biome

type_check   → pnpm run type-check
             Rationale: Found "type-check" script using tsc

coverage     → pnpm test -- --coverage
             Rationale: Vitest supports --coverage flag

build        → pnpm run build
             Rationale: Found "build" script using vite
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Config written to: .pantheon/quality-config.json
```

### Example Quality Config
```json
{
  "version": "1.0",
  "project_type": "python",
  "framework": "fastapi",
  "commands": {
    "test": "pytest tests/ -v",
    "lint": "ruff check src/ tests/",
    "type_check": "mypy src/ --strict",
    "coverage": "pytest --cov=src --cov-report=term-missing",
    "build": "uv build"
  },
  "thresholds": {
    "coverage_branches": 80
  },
  "discovery_source": "intelligent",
  "contextualized_at": "2025-10-08T12:34:56Z"
}
```

## Quality Gate System

Pantheon provides automated quality reporting at key workflow checkpoints to give the orchestrator full visibility into project status.

### How It Works

When you run `/pantheon:contextualize`, it generates two files:

1. **`.pantheon/quality-config.json`**: Quality commands configuration
2. **`.pantheon/quality-report.sh`**: Executable script that runs quality checks

The quality gate hook (`phase-gate.sh`) automatically runs at these checkpoints:
- After DEV/QA agent completion
- Before git commits
- Before phase transitions

### Quality Report Example

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 QUALITY GATE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quality Checks:
  Linting:       ✅ PASS
  Type Checking: ✅ PASS
  Tests:         ✅ PASS (50/50 passing)
  Coverage:      ✅ PASS (92% / 80% required)

Phase Status:
  Tasks:         5/5 completed
  QA Validated:  ✅ Yes
  User Validated: ❌ No

⚠️ NOT READY FOR COMMIT

Blocking issues:
  • User approval not received

Recommended actions:
  1. Present phase completion report to user
  2. Obtain user approval before committing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Manual Quality Check

You can run the quality report manually anytime:

```bash
.pantheon/quality-report.sh
```

This outputs structured JSON with complete quality status, which the orchestrator uses to make informed decisions.

### Philosophy

Quality reports are **informational, not blocking**:
- They provide context to the orchestrator
- The orchestrator interprets reports and decides appropriate actions
- Flexible approach that accounts for edge cases and project context
- Single source of truth (one script vs. multiple separate hooks)

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

**Quality Gates**: Quality report shows status at commit time, providing orchestrator with full context to make informed decisions.

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

## Architecture

Pantheon uses a multi-agent architecture with three key roles:
- **Orchestrator**: Coordinates workflow, creates commits (main Claude agent)
- **DEV Agent**: Implements features with TDD approach
- **QA Agent**: Validates quality independently

Quality is enforced through **defense in depth**: agent self-checks → hooks → independent QA → final hooks.

**For detailed architecture documentation**, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## Requirements

- Python 3.9+
- Claude Code (for using agents)

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

## Acknowledgments

Built on Claude Code's sub-agent architecture.
