---
description: Analyze project and gather context for Pantheon (quality commands, architecture, etc.)
argument-hint: [--quality-only | --full]
allowed-tools: Read(*), Glob(*), Bash(cat:*), Bash(ls:*), Bash(jq:*), Bash(grep:*)
---

Analyze the project structure and gather context needed for Pantheon workflows.

User arguments: $ARGUMENTS

## Overview

This command performs intelligent project contextualization to discover project-specific information needed by Pantheon agents and workflows. Currently implements quality discovery with a modular design for future extensions.

## Current Implementation: Quality Discovery (Module 1)

### Purpose

Intelligently discover quality commands (test, lint, type-check, coverage, build) for ANY language, framework, or build system through LLM-based analysis.

### Execution Strategy

1. **Check plan.md First (Authoritative Source)**
   - Look for "## Quality Standards" section in plan.md
   - Extract explicitly defined commands:
     - Test command: <command>
     - Lint command: <command>
     - Type command: <command>
     - Coverage command: <command>
     - Build command: <command>
   - If all commands found in plan.md, use those and skip discovery
   - If partial commands found, use those and discover missing ones

2. **Analyze Project Structure**
   - Use Glob to find configuration files
   - Identify languages and frameworks from file presence:
     - `package.json`, `bun.lockb`, `deno.json` → JavaScript/TypeScript
     - `pyproject.toml`, `setup.py`, `requirements.txt` → Python
     - `Cargo.toml` → Rust
     - `go.mod` → Go
     - `pom.xml`, `build.gradle`, `build.gradle.kts` → Java/Kotlin
     - `Gemfile` → Ruby
     - `composer.json` → PHP
     - `*.csproj`, `*.fsproj` → .NET (C#/F#)
     - `mix.exs` → Elixir
     - `pubspec.yaml` → Dart/Flutter
     - `swift package.swift`, `*.xcodeproj` → Swift
     - Multiple files → Multi-language monorepo

3. **Read Configuration Files Intelligently**
   - For each detected language, read relevant config files:
     - **Node.js**: Read package.json scripts section, detect test framework (jest, vitest, mocha), linter (eslint, biome), type checker (tsc)
     - **Python**: Read pyproject.toml for tool configs, detect pytest, ruff, mypy, black, coverage
     - **Rust**: Parse Cargo.toml for test setup, detect clippy for linting
     - **Go**: Standard go commands, check for golangci-lint config
     - **Java/Kotlin**: Parse build files for test tasks, linting (spotless, ktlint), build tasks
     - **Ruby**: Check Gemfile for rspec, rubocop, bundler
     - **PHP**: Check composer.json for phpunit, phpstan, psalm
     - **.NET**: Check project files for test frameworks, analyzers
     - **Elixir**: Standard mix commands (mix test, mix format, mix credo)
     - **Dart/Flutter**: Standard dart/flutter commands
     - **Swift**: Standard swift commands, swiftlint

4. **Understand Project Conventions**
   - Read README.md or CONTRIBUTING.md for custom commands
   - Look for Makefile, justfile, or task runners (package.json scripts, npm run, etc.)
   - Detect CI/CD configuration files (.github/workflows, .gitlab-ci.yml) for quality commands
   - Check for monorepo tools (turborepo, nx, lerna, pnpm workspaces, yarn workspaces)

5. **Discover Commands Contextually**
   - For each command type (test, lint, type-check, coverage, build):
     - Check if explicitly defined in package manager scripts
     - Look for standard command patterns for the language
     - Consider modern alternatives (e.g., vitest vs jest, biome vs eslint, bun vs npm)
     - Verify commands are likely to work (tools referenced exist in dependencies)
     - Prefer workspace-aware commands in monorepos
   - Use reasoning to select the most appropriate command
   - Provide empty string "" if no command found (don't guess)

6. **Generate `.pantheon/quality-config.json`**
   - Create `.pantheon/` directory if it doesn't exist
   - Write config file with structure:
     ```json
     {
       "version": "1.0",
       "project_type": "<primary-language>",
       "framework": "<detected-framework>",
       "commands": {
         "test": "<discovered-command>",
         "lint": "<discovered-command>",
         "type_check": "<discovered-command>",
         "coverage": "<discovered-command>",
         "build": "<discovered-command>"
       },
       "thresholds": {
         "coverage_branches": 80,
         "coverage_statements": 80
       },
       "discovery_source": "plan.md | intelligent | mixed",
       "contextualized_at": "<ISO-8601-timestamp>"
     }
     ```

7. **Report Findings to User**
   - Show project type and framework identified
   - List each discovered command with brief rationale
   - Indicate discovery source (plan.md, intelligent, or mixed)
   - Flag any uncertainties or missing commands
   - Suggest manual verification steps if needed
   - Recommend adding commands to plan.md for future consistency

## Example Outputs

### Example 1: Node.js Project with Modern Tools
```
✓ Project analyzed successfully

Project Type: Node.js (JavaScript/TypeScript)
Framework: React (detected from package.json dependencies)
Package Manager: pnpm (detected from pnpm-lock.yaml)

Discovered Quality Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
test         → pnpm test
             Rationale: Found "test" script in package.json using vitest

lint         → pnpm run lint
             Rationale: Found "lint" script using biome (modern linter)

type_check   → pnpm run type-check
             Rationale: Found "type-check" script running tsc --noEmit

coverage     → pnpm test -- --coverage
             Rationale: Vitest supports --coverage flag for coverage reports

build        → pnpm run build
             Rationale: Found "build" script using vite
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Discovery Source: intelligent (no plan.md found)
Config written to: .pantheon/quality-config.json

✓ Recommendation: Add these commands to plan.md for consistency
```

### Example 2: Python Project
```
✓ Project analyzed successfully

Project Type: Python
Framework: FastAPI (detected from pyproject.toml dependencies)
Package Manager: uv (detected from uv.lock)

Discovered Quality Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
test         → pytest tests/ -v
             Rationale: From plan.md (authoritative)

lint         → ruff check src/ tests/
             Rationale: From plan.md (authoritative)

type_check   → mypy src/ --strict
             Rationale: From plan.md (authoritative)

coverage     → pytest tests/ --cov=src --cov-report=term-missing
             Rationale: Discovered from pytest-cov in dependencies

build        → uv build
             Rationale: Discovered uv as package manager
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Discovery Source: mixed (plan.md + intelligent)
Config written to: .pantheon/quality-config.json

✓ All commands validated against plan.md
```

### Example 3: Rust Project
```
✓ Project analyzed successfully

Project Type: Rust
Framework: None (binary crate)

Discovered Quality Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
test         → cargo test
             Rationale: Standard Rust test command

lint         → cargo clippy -- -D warnings
             Rationale: Clippy detected in CI workflow, strict mode

type_check   → cargo check
             Rationale: Standard Rust type checking (implicit via compiler)

coverage     → cargo tarpaulin --out Html
             Rationale: Detected tarpaulin in dev-dependencies

build        → cargo build --release
             Rationale: Standard Rust build command
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Discovery Source: intelligent
Config written to: .pantheon/quality-config.json
```

### Example 4: Monorepo with Multiple Languages
```
✓ Project analyzed successfully

Project Type: Multi-language monorepo
Framework: Turborepo (detected from turbo.json)
Languages: TypeScript, Python, Go

Discovered Quality Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
test         → turbo run test
             Rationale: Turborepo workspace command runs tests across all packages

lint         → turbo run lint
             Rationale: Workspace-level lint task defined in turbo.json

type_check   → turbo run type-check
             Rationale: Workspace-level type-check task

coverage     → turbo run test:coverage
             Rationale: Found coverage task in turbo.json pipeline

build        → turbo run build
             Rationale: Workspace-level build task
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Discovery Source: intelligent
Config written to: .pantheon/quality-config.json

⚠ Note: Monorepo detected. Commands run across all workspaces.
   For per-package commands, update config manually or use --filter flags.
```

## Error Handling

**Missing plan.md**: Proceed with intelligent discovery

**Partial plan.md**: Use explicit commands, discover missing ones

**Uncertain commands**: Report uncertainty, suggest alternatives, allow user to choose

**Commands don't exist**: Use empty string "" in config, flag for manual setup

**Unsupported language**: Report as "other" project type, suggest manual configuration, still create config with empty commands

**Multiple package managers**: Detect primary one (e.g., pnpm-lock.yaml vs package-lock.json), report in findings

## Implementation Instructions

Execute the quality discovery workflow:

1. Determine project root (current working directory)

2. Check for plan.md in common locations:
   - `./plan.md`
   - `./specs/*/plan.md` (if using Spec Kit)
   - `.specify/*/plan.md`

3. If plan.md found, parse Quality Standards section

4. Use Glob to discover project structure:
   - Configuration files (package.json, pyproject.toml, etc.)
   - README, CONTRIBUTING files
   - CI/CD configurations

5. For each detected language, read relevant config files and intelligently discover commands

6. Generate config object with discovered commands

7. Create `.pantheon/` directory if needed

8. Write `.pantheon/quality-config.json`

9. **Generate `.pantheon/quality-report.sh`**
   - Create executable bash script that reads quality-config.json
   - Generate language-specific command execution and output parsing
   - Include phase status parsing logic (tasks.md markers)
   - Output structured JSON report with all quality metrics
   - See Quality Report Script Generation section below for details

10. Report findings to user with detailed explanations

11. Provide recommendations for verification or manual updates

Always prioritize plan.md commands when available. Use intelligent discovery to fill gaps or when plan.md doesn't exist.

---

## Quality Report Script Generation

After generating `quality-config.json`, create `.pantheon/quality-report.sh` as an executable bash script that provides comprehensive quality and phase status reporting.

### Script Structure

The script should:
1. Read commands from `quality-config.json`
2. Execute each quality command and parse output
3. Parse phase status from `tasks.md`
4. Return structured JSON report
5. Always exit with code 0 (informational only)

### Script Template

Generate the script with this structure (adapt based on detected project type):

```bash
#!/usr/bin/env bash
# Quality Report Script
# Auto-generated by /pantheon:contextualize on <timestamp>
# Project type: <detected-type>

set -euo pipefail

# Determine project root (where this script lives)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Read quality config
CONFIG_FILE="$PROJECT_ROOT/.pantheon/quality-config.json"
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo '{"error": "quality-config.json not found"}' >&2
    exit 1
fi

# Extract commands from config (requires jq)
TEST_CMD=$(jq -r '.commands.test // ""' "$CONFIG_FILE")
LINT_CMD=$(jq -r '.commands.lint // ""' "$CONFIG_FILE")
TYPE_CMD=$(jq -r '.commands.type_check // ""' "$CONFIG_FILE")
COVERAGE_CMD=$(jq -r '.commands.coverage // ""' "$CONFIG_FILE")
COVERAGE_THRESHOLD=$(jq -r '.thresholds.coverage_branches // 80' "$CONFIG_FILE")

# === QUALITY CHECK FUNCTIONS ===

run_lint() {
    if [[ -z "$LINT_CMD" ]]; then
        echo '{"status": "skipped", "reason": "no lint command configured"}'
        return
    fi

    # Run lint command, capture output
    if LINT_OUTPUT=$(eval "$LINT_CMD" 2>&1); then
        echo '{"status": "pass", "errors": 0}'
    else
        # Parse error count (language-specific)
        ERROR_COUNT=$(echo "$LINT_OUTPUT" | <language-specific-parsing> || echo "unknown")
        echo "{\"status\": \"fail\", \"errors\": $ERROR_COUNT}"
    fi
}

run_type_check() {
    if [[ -z "$TYPE_CMD" ]]; then
        echo '{"status": "skipped", "reason": "no type check command configured"}'
        return
    fi

    if TYPE_OUTPUT=$(eval "$TYPE_CMD" 2>&1); then
        echo '{"status": "pass", "errors": 0}'
    else
        ERROR_COUNT=$(echo "$TYPE_OUTPUT" | <language-specific-parsing> || echo "unknown")
        echo "{\"status\": \"fail\", \"errors\": $ERROR_COUNT}"
    fi
}

run_tests() {
    if [[ -z "$TEST_CMD" ]]; then
        echo '{"status": "skipped", "reason": "no test command configured"}'
        return
    fi

    TEST_OUTPUT=$(eval "$TEST_CMD" 2>&1 || true)

    # Parse test results (language-specific)
    PASSED=$(echo "$TEST_OUTPUT" | <language-specific-parsing-for-passed> || echo 0)
    FAILED=$(echo "$TEST_OUTPUT" | <language-specific-parsing-for-failed> || echo 0)
    TOTAL=$((PASSED + FAILED))

    if [[ $FAILED -eq 0 && $TOTAL -gt 0 ]]; then
        echo "{\"status\": \"pass\", \"total\": $TOTAL, \"passed\": $PASSED, \"failed\": $FAILED}"
    else
        echo "{\"status\": \"fail\", \"total\": $TOTAL, \"passed\": $PASSED, \"failed\": $FAILED}"
    fi
}

run_coverage() {
    if [[ -z "$COVERAGE_CMD" ]]; then
        echo '{"status": "skipped", "reason": "no coverage command configured"}'
        return
    fi

    eval "$COVERAGE_CMD" &>/dev/null || true

    # Parse coverage (language-specific)
    COVERAGE_PCT=$(<language-specific-coverage-parsing> || echo 0)

    if (( $(echo "$COVERAGE_PCT >= $COVERAGE_THRESHOLD" | bc -l 2>/dev/null || echo 0) )); then
        echo "{\"status\": \"pass\", \"percentage\": $COVERAGE_PCT, \"threshold\": $COVERAGE_THRESHOLD}"
    else
        echo "{\"status\": \"fail\", \"percentage\": $COVERAGE_PCT, \"threshold\": $COVERAGE_THRESHOLD}"
    fi
}

# === PHASE STATUS PARSING ===

parse_phase_status() {
    local tasks_file="$PROJECT_ROOT/tasks.md"

    if [[ ! -f "$tasks_file" ]]; then
        echo '{"tasks_complete": 0, "tasks_incomplete": 0, "tasks_total": 0, "qa_validated": false, "user_validated": false}'
        return
    fi

    # Count completed and incomplete tasks
    local complete=$(grep -c "^- \[x\]" "$tasks_file" 2>/dev/null || echo 0)
    local incomplete=$(grep -c "^- \[ \]" "$tasks_file" 2>/dev/null || echo 0)
    local total=$((complete + incomplete))

    # Check for validation markers
    local qa_validated="false"
    local user_validated="false"

    if grep -q "^- \[x\] QA validated" "$tasks_file" 2>/dev/null; then
        qa_validated="true"
    fi

    if grep -q "^- \[x\] User validated" "$tasks_file" 2>/dev/null; then
        user_validated="true"
    fi

    echo "{\"tasks_complete\": $complete, \"tasks_incomplete\": $incomplete, \"tasks_total\": $total, \"qa_validated\": $qa_validated, \"user_validated\": $user_validated}"
}

# === READINESS EVALUATION ===

evaluate_readiness() {
    # All quality checks must pass
    local lint_status=$(run_lint | jq -r '.status')
    local type_status=$(run_type_check | jq -r '.status')
    local test_status=$(run_tests | jq -r '.status')
    local cov_status=$(run_coverage | jq -r '.status')

    # Parse phase status
    local phase_json=$(parse_phase_status)
    local qa_validated=$(echo "$phase_json" | jq -r '.qa_validated')
    local user_validated=$(echo "$phase_json" | jq -r '.user_validated')

    # Ready if all pass/skip AND validations complete
    local ready="true"

    [[ "$lint_status" == "fail" ]] && ready="false"
    [[ "$type_status" == "fail" ]] && ready="false"
    [[ "$test_status" == "fail" ]] && ready="false"
    [[ "$cov_status" == "fail" ]] && ready="false"
    [[ "$qa_validated" == "false" ]] && ready="false"
    [[ "$user_validated" == "false" ]] && ready="false"

    echo "$ready"
}

# === GENERATE REPORT ===

cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_root": "$PROJECT_ROOT",
  "quality": {
    "linting": $(run_lint),
    "type_checking": $(run_type_check),
    "tests": $(run_tests),
    "coverage": $(run_coverage)
  },
  "phase": $(parse_phase_status),
  "summary": {
    "ready_for_commit": $(evaluate_readiness)
  }
}
EOF

exit 0
```

### Language-Specific Parsing

**Python (pytest, ruff, mypy):**
- Test parsing: `grep -oP '\d+(?= passed)' or grep "passed"`
- Lint errors: `grep -c "error"`
- Type errors: `grep -c "error"`
- Coverage: Parse `coverage.json` with jq or `--cov-report=term` output

**Node.js (jest/vitest, eslint, tsc):**
- Test parsing: `grep -oP '\d+(?= passing)'` or jest JSON output
- Lint errors: `grep -c "error"` or eslint JSON format
- Type errors: `grep -c "error"` from tsc output
- Coverage: Parse `coverage/coverage-summary.json` with jq

**Go (go test, golangci-lint):**
- Test parsing: `grep "PASS\|FAIL"`, count occurrences
- Lint errors: `golangci-lint run --out-format=json | jq`
- Coverage: Parse `go test -coverprofile` output

### Script Permissions

After writing the script, make it executable:
```bash
chmod +x .pantheon/quality-report.sh
```

### Implementation Steps

When generating the quality-report.sh:

1. Use the detected project_type from quality-config.json
2. Insert appropriate language-specific parsing logic
3. Ensure jq is available (most systems have it, warn if missing)
4. Handle edge cases (no tasks.md, missing commands, etc.)
5. Make script executable with chmod +x
6. Report script location to user

### Example: Python Project Script

For a Python project with pytest, ruff, mypy:

```bash
run_lint() {
    if [[ -z "$LINT_CMD" ]]; then
        echo '{"status": "skipped", "reason": "no lint command configured"}'
        return
    fi

    if LINT_OUTPUT=$(eval "$LINT_CMD" 2>&1); then
        echo '{"status": "pass", "errors": 0}'
    else
        ERROR_COUNT=$(echo "$LINT_OUTPUT" | grep -c "error" || echo "unknown")
        echo "{\"status\": \"fail\", \"errors\": $ERROR_COUNT}"
    fi
}

run_coverage() {
    if [[ -z "$COVERAGE_CMD" ]]; then
        echo '{"status": "skipped", "reason": "no coverage command configured"}'
        return
    fi

    eval "$COVERAGE_CMD" &>/dev/null || true

    # Parse coverage from pytest output or coverage.json
    if [[ -f "coverage.json" ]]; then
        COVERAGE_PCT=$(jq -r '.totals.percent_covered' coverage.json 2>/dev/null || echo 0)
    else
        # Parse from terminal output: "TOTAL ... 85%"
        COVERAGE_PCT=$(cat .coverage-output.txt 2>/dev/null | grep "TOTAL" | awk '{print $NF}' | tr -d '%' || echo 0)
    fi

    if (( $(echo "$COVERAGE_PCT >= $COVERAGE_THRESHOLD" | bc -l) )); then
        echo "{\"status\": \"pass\", \"percentage\": $COVERAGE_PCT, \"threshold\": $COVERAGE_THRESHOLD}"
    else
        echo "{\"status\": \"fail\", \"percentage\": $COVERAGE_PCT, \"threshold\": $COVERAGE_THRESHOLD}"
    fi
}
```

### Error Handling

The script should:
- Check if quality-config.json exists before reading
- Handle missing jq gracefully (report error if needed)
- Return valid JSON even if commands fail
- Use "skipped" status for unconfigured commands
- Never crash - always exit 0 with structured output
