# Manual Test Checklist: /pantheon:contextualize

This checklist documents manual testing procedures for the `/pantheon:contextualize` slash command. These tests cannot be automated as they require Claude Code environment.

## Prerequisites

- Claude Code installed and running
- Test projects prepared in various languages
- `/pantheon:contextualize` command installed in `.claude/commands/pantheon/`

## Test Cases

### Test 1: Python Project with plan.md

**Setup:**
- Create Python project with `pyproject.toml`
- Create `plan.md` with Quality Standards section containing all commands
- Commands: pytest, ruff, mypy, coverage

**Steps:**
1. Open Claude Code in project directory
2. Run: `/pantheon:contextualize`
3. Observe command execution and output

**Expected Results:**
- ✅ Command analyzes project structure
- ✅ Detects plan.md and extracts commands
- ✅ Reports discovery source as "plan.md"
- ✅ Creates `.pantheon/quality-config.json`
- ✅ Config contains exact commands from plan.md
- ✅ Project type identified as "python"
- ✅ User receives detailed report with rationale

---

### Test 2: Node.js Project with Modern Tools

**Setup:**
- Create Node.js project with `package.json`
- Include scripts: `test`, `lint` (using biome), `type-check`, `build` (using vite)
- No plan.md

**Steps:**
1. Open Claude Code in project directory
2. Run: `/pantheon:contextualize`

**Expected Results:**
- ✅ Detects Node.js project from package.json
- ✅ Parses package.json scripts section
- ✅ Discovers test framework (vitest/jest)
- ✅ Discovers modern linter (biome/eslint)
- ✅ Creates config with npm/pnpm/bun commands
- ✅ Reports which tools detected and why
- ✅ Discovery source marked as "intelligent"

---

### Test 3: Rust Project

**Setup:**
- Create Rust project with `Cargo.toml`
- Include `tarpaulin` in dev-dependencies for coverage
- No plan.md

**Steps:**
1. Open Claude Code in project directory
2. Run: `/pantheon:contextualize`

**Expected Results:**
- ✅ Detects Rust project from Cargo.toml
- ✅ Discovers standard cargo commands (test, check, build)
- ✅ Detects clippy for linting
- ✅ Discovers tarpaulin for coverage
- ✅ Creates appropriate config
- ✅ Reports Rust-specific command rationale

---

### Test 4: Go Project

**Setup:**
- Create Go project with `go.mod`
- No plan.md

**Steps:**
1. Open Claude Code in project directory
2. Run: `/pantheon:contextualize`

**Expected Results:**
- ✅ Detects Go project from go.mod
- ✅ Discovers standard go commands
- ✅ Checks for golangci-lint
- ✅ Creates config with go test, go build, etc.
- ✅ Reports discovery rationale

---

### Test 5: Monorepo (Turborepo/Nx)

**Setup:**
- Create monorepo with `turbo.json` or `nx.json`
- Multiple packages (TypeScript, Python, Go)
- Workspace-level commands

**Steps:**
1. Open Claude Code in monorepo root
2. Run: `/pantheon:contextualize`

**Expected Results:**
- ✅ Detects monorepo structure
- ✅ Identifies workspace tool (turborepo/nx)
- ✅ Discovers workspace-level commands (turbo run test, nx test, etc.)
- ✅ Reports monorepo detection and strategy
- ✅ Warns about per-package vs workspace commands
- ✅ Creates config with workspace commands

---

### Test 6: Java/Kotlin with Gradle

**Setup:**
- Create Java/Kotlin project with `build.gradle.kts`
- Include test tasks, ktlint, spotless

**Steps:**
1. Open Claude Code in project directory
2. Run: `/pantheon:contextualize`

**Expected Results:**
- ✅ Detects Java/Kotlin from build files
- ✅ Parses Gradle tasks
- ✅ Discovers test command (gradle test)
- ✅ Discovers linting (ktlint/spotless)
- ✅ Creates config with gradle commands
- ✅ Reports Gradle task discovery

---

### Test 7: Unknown/Unsupported Language

**Setup:**
- Create project with no recognizable config files
- Or a language not explicitly supported (e.g., Lua, Zig)
- Only README.md exists

**Steps:**
1. Open Claude Code in project directory
2. Run: `/pantheon:contextualize`

**Expected Results:**
- ✅ Attempts intelligent discovery
- ✅ Reads README for custom commands
- ✅ Reports as "other" or specific language if detected
- ✅ May return empty commands or suggest manual configuration
- ✅ Creates config file even with empty commands
- ✅ Provides clear guidance to user

---

### Test 8: Partial plan.md (Mixed Discovery)

**Setup:**
- Create Python project with pyproject.toml
- Create plan.md with only test and lint commands (missing type-check, coverage, build)

**Steps:**
1. Open Claude Code in project directory
2. Run: `/pantheon:contextualize`

**Expected Results:**
- ✅ Detects plan.md and extracts specified commands
- ✅ Fills missing commands via intelligent discovery
- ✅ Reports discovery source as "mixed"
- ✅ Clearly indicates which commands from plan.md vs discovered
- ✅ plan.md commands take precedence over discovered
- ✅ Config contains all 5 command types

---

### Test 9: Project with Multiple Package Managers

**Setup:**
- Node.js project with both `package-lock.json` and `pnpm-lock.yaml`
- (simulates migration scenario)

**Steps:**
1. Open Claude Code in project directory
2. Run: `/pantheon:contextualize`

**Expected Results:**
- ✅ Detects multiple package managers
- ✅ Chooses primary package manager (prefer pnpm over npm)
- ✅ Reports which package manager selected and why
- ✅ Commands use selected package manager (pnpm test vs npm test)

---

### Test 10: CI/CD Config as Fallback

**Setup:**
- Create project with `.github/workflows/ci.yml`
- No plan.md
- CI file contains quality commands

**Steps:**
1. Open Claude Code in project directory
2. Run: `/pantheon:contextualize`

**Expected Results:**
- ✅ Attempts to read CI/CD config
- ✅ Extracts quality commands from workflow
- ✅ Uses discovered commands
- ✅ Reports CI/CD as discovery source
- ✅ Suggests adding to plan.md for consistency

---

### Test 11: Re-contextualization (Config Exists)

**Setup:**
- Project with existing `.pantheon/quality-config.json`
- Modify project structure (add new tools, change package manager)

**Steps:**
1. Open Claude Code in project directory
2. Run: `/pantheon:contextualize`
3. Observe behavior with existing config

**Expected Results:**
- ✅ Detects existing config
- ✅ Asks user if they want to regenerate or update
- ✅ If regenerating: backs up old config, creates new one
- ✅ Reports what changed (old vs new commands)
- ✅ Updates timestamp in config

---

### Test 12: Error Handling

**Setup:**
- Test various error scenarios:
  - Invalid project directory (no write permissions)
  - Malformed config files (invalid JSON in package.json)
  - Missing dependencies for discovery

**Steps:**
1. Create error scenario
2. Run: `/pantheon:contextualize`

**Expected Results:**
- ✅ Graceful error handling
- ✅ Clear error messages
- ✅ Suggests remediation steps
- ✅ Partial success when possible (e.g., some commands discovered despite errors)
- ✅ Does not crash or leave invalid state

---

## Validation Checklist

After each test, verify:

- [ ] `.pantheon/quality-config.json` created
- [ ] Config file is valid JSON
- [ ] All required fields present (version, project_type, commands, thresholds, discovery_source, contextualized_at)
- [ ] Commands are appropriate for project type
- [ ] User received detailed, helpful output
- [ ] No errors or warnings (unless expected)
- [ ] Config can be loaded by Python module (`load_quality_config()`)

## Reporting

For each failed test:
1. Document the issue
2. Capture error messages
3. Save the generated config (if any)
4. Note expected vs actual behavior
5. Create GitHub issue with reproduction steps

## Notes

- These tests require Claude Code environment and cannot be automated
- Run full test suite before each release
- Update checklist as new languages/tools are supported
- Test on multiple operating systems (macOS, Linux, Windows)
