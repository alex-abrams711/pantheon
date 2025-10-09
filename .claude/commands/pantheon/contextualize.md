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

9. Report findings to user with detailed explanations

10. Provide recommendations for verification or manual updates

Always prioritize plan.md commands when available. Use intelligent discovery to fill gaps or when plan.md doesn't exist.
