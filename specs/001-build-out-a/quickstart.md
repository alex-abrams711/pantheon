# Quickstart: Multi-Agent Quality-First Workflow

**Feature**: Multi-Agent Quality-First Workflow (Pantheon v0.2.0)
**Branch**: 001-build-out-a
**Purpose**: End-to-end validation that all components work together

---

## Prerequisites

- Pantheon v0.1.1 installed: `uv tool list | grep pantheon-agents`
- Test project with .claude/ directory
- Git repository initialized

---

## Test Scenario: Complete Workflow Validation

This quickstart validates the full multi-agent workflow from quality discovery through parallel execution and QA validation.

---

### Step 1: Quality Discovery and Config Generation

**Action**: Run quality discovery (simulating `/constitution` command behavior)

```bash
cd /path/to/test-project

# Simulate /constitution creating quality config
python -c "
from pathlib import Path
from pantheon.quality.config import generate_quality_config

project_root = Path.cwd()
plan_path = project_root / 'specs' / 'feature' / 'plan.md' if (project_root / 'specs').exists() else None

config_path = generate_quality_config(project_root, plan_path)
print(f'Config created: {config_path}')
"
```

**Expected Result**:
- `.pantheon/quality-config.json` created
- File contains valid JSON with all required keys
- Commands discovered based on project type

**Validation**:
```bash
cat .pantheon/quality-config.json

# Should show:
# {
#   "version": "1.0",
#   "project_type": "python",  # or node, go, etc.
#   "commands": { ... },
#   "thresholds": { ... },
#   "discovery_source": "plan.md" or "auto"
# }
```

---

### Step 2: Hook Installation

**Action**: Install quality gate hooks

```bash
pantheon integrate
```

**Expected Result**:
- `.pantheon/hooks/` directory created with 3 scripts
- All scripts are executable
- `.claude/settings.json` updated with hook configuration
- Success message: "Hooks installed successfully"

**Validation**:
```bash
# Check hooks exist and are executable
ls -la .pantheon/hooks/
# Should show: subagent-validation.sh, pre-commit-gate.sh, phase-gate.sh (all with x permission)

# Check settings.json updated
cat .claude/settings.json | grep -A 5 '"hooks"'
# Should show hook paths
```

---

### Step 3: DEV Agent Invocation (Simulated)

**Action**: Simulate orchestrator invoking DEV agent with context package

```bash
# In Claude Code conversation:
# "Use the DEV agent to implement task T001: Add hello() function"
```

**Context Package** (what orchestrator provides):
```markdown
# Task Context: T001

## Task Details
**ID**: T001
**Description**: Add hello() function to greet users
**Files**: src/hello.py, tests/test_hello.py

## Acceptance Criteria
- [ ] Function accepts name parameter
- [ ] Returns greeting message
- [ ] Has unit tests with 100% coverage

## Quality Standards
**Test Command**: pytest tests/test_hello.py -v
**Lint Command**: ruff check src/ tests/
**Type Command**: mypy src/
**Coverage Threshold**: 80% branches
```

**Expected Result**:
- DEV agent creates src/hello.py with implementation
- DEV agent creates tests/test_hello.py with tests
- DEV agent runs quality checks (tests, lint, type)
- SubagentStop hook validates work before completion
- DEV returns SUCCESS with summary

**Validation**:
```bash
# Check files created
ls src/hello.py tests/test_hello.py

# Run quality checks manually
pytest tests/test_hello.py -v  # Should pass
ruff check src/ tests/          # Should pass
mypy src/                       # Should pass
```

---

### Step 4: QA Agent Invocation (Simulated)

**Action**: Simulate orchestrator invoking QA agent after DEV completion

```bash
# In Claude Code conversation:
# "Use the QA agent to validate batch: T001"
```

**Context Package** (what orchestrator provides):
```markdown
# QA Validation Context

## Tasks to Validate
- **T001**: Add hello() function
  - Files: src/hello.py, tests/test_hello.py

## Quality Standards
**Test Command**: pytest tests/ -v
**Coverage Command**: pytest tests/ --cov=src --cov-report=term-missing
**Coverage Threshold**: 80% branches
**Lint Command**: ruff check src/ tests/
**Type Command**: mypy src/

## Definition of Done
- [ ] All tests pass (0 failures)
- [ ] Coverage ≥80% branches
- [ ] No linting errors
- [ ] No type errors
- [ ] No code smells
- [ ] Manual testing passed (if functional)

## Project Root
/path/to/test-project
```

**Expected Result**:
- QA agent runs all automated checks
- QA agent performs manual testing (if functional changes)
- QA agent generates structured report
- Report status: PASS (if all checks pass) or FAIL (if issues found)

**Expected Report**:
```markdown
# QA Validation Report

**Status**: PASS
**Batch**: T001
**Date**: 2025-10-06T14:30:00Z

## Summary Metrics
- **Tests**: 3 total, 3 passing, 0 failing ✓
- **Coverage**: 100% branches (threshold: 80%) ✓
- **Lint**: 0 errors ✓
- **Type**: 0 errors ✓
- **Code Smells**: 0 found ✓
- **Manual Testing**: SKIPPED (non-functional change)

## Issues
No issues found.

## Definition of Done
- [x] All tests pass
- [x] Coverage meets threshold
- [x] No linting errors
- [x] No type errors
- [x] No code smells
- [x] Manual testing passed

## Recommendations
Batch T001 ready for commit.
```

---

### Step 5: Orchestrator Commit with PreCommit Hook

**Action**: Orchestrator creates git commit after QA PASS

```bash
# In Claude Code conversation:
# Orchestrator: "All quality checks passed. Creating commit..."

git add src/hello.py tests/test_hello.py
git commit -m "feat: Add hello() function (T001)

- Accepts name parameter
- Returns greeting message
- 100% test coverage

Quality metrics: 3/3 tests passing, 0 lint errors, 0 type errors"
```

**Expected Result**:
- PreCommit hook runs before commit is created
- Hook validates tests, lint, type checks
- If all pass: commit created successfully
- If any fail: commit blocked with error message

**Validation**:
```bash
# Check commit created
git log -1 --oneline
# Should show: feat: Add hello() function (T001)

# Verify commit has changes
git show HEAD --stat
# Should show: src/hello.py, tests/test_hello.py
```

---

### Step 6: Phase Gate Checkpoint

**Action**: User approves phase transition

```bash
# In Claude Code conversation:
# Orchestrator: "Phase 1 complete. Proceed to Phase 2? (yes/no)"
# User: "yes"
```

**Expected Result**:
- Phase Gate hook (UserPromptSubmit) detects "yes" keyword
- Hook runs quality validation
- If all pass: phase transition allowed
- If any fail: phase transition blocked with error message

**Validation**:
```bash
# No direct file validation - hook runs in Claude Code runtime
# Success = conversation continues to Phase 2
# Failure = user sees error: "Phase gate validation failed: ..."
```

---

### Step 7: Parallel DEV Agent Execution (Simulated)

**Action**: Orchestrator invokes 3 DEV agents in parallel

```bash
# In Claude Code conversation (single message with 3 Task tool calls):
# Task 1: Implement goodbye() function
# Task 2: Implement greet_all() function
# Task 3: Update documentation
```

**Expected Result**:
- All 3 DEV agents work simultaneously
- Orchestrator waits for all to complete
- If some fail: preserve successful work, retry failures
- Once all succeed: proceed to QA validation

**Validation**:
```bash
# After all agents complete:
ls src/goodbye.py src/greet_all.py docs/usage.md
# All files should exist

# Quality checks should pass for all
pytest tests/ -v
ruff check src/ tests/
mypy src/
```

---

### Step 8: Rollback Test

**Action**: Uninstall hooks and validate removal

```bash
pantheon rollback
```

**Expected Result**:
- Hook entries removed from `.claude/settings.json`
- `.pantheon/hooks/` directory deleted
- `.pantheon/quality-config.json` preserved
- Success message: "Hooks removed successfully"

**Validation**:
```bash
# Check hooks removed
ls .pantheon/hooks/ 2>&1
# Should show: No such file or directory

# Check settings.json cleaned
cat .claude/settings.json | grep hooks
# Should show nothing or empty hooks object

# Check config preserved
cat .pantheon/quality-config.json
# Should still exist with content
```

---

## Success Criteria

This quickstart is successful when:

1. ✅ Quality config generated correctly for project type
2. ✅ Hooks installed and configured in .claude/settings.json
3. ✅ DEV agent can complete task with SubagentStop validation
4. ✅ QA agent can validate batch and generate structured report
5. ✅ PreCommit hook blocks bad commits, allows good commits
6. ✅ Phase Gate hook validates quality on user approval
7. ✅ Parallel DEV agents can execute simultaneously
8. ✅ Rollback cleanly removes hooks, preserves config

---

## Troubleshooting

### Issue: Quality config has empty commands

**Cause**: Project type not detected or no discoverable commands

**Fix**:
- Manually edit `.pantheon/quality-config.json`
- Add commands explicitly in plan.md Quality Standards section
- Re-run quality discovery

### Issue: Hooks not executing

**Cause**: Scripts not executable or settings.json not updated

**Fix**:
```bash
chmod +x .pantheon/hooks/*.sh
# Check settings.json has correct paths
```

### Issue: SubagentStop hook blocks DEV even when quality passes

**Cause**: Hook script has bug or incorrect quality config

**Fix**:
- Check hook script logs: `.pantheon/hooks/subagent-validation.sh` output
- Validate quality config: `cat .pantheon/quality-config.json`
- Test commands manually: `pytest tests/`, `ruff check src/`

---

## Cleanup

After quickstart completion:

```bash
# Remove test files
rm -rf src/hello.py src/goodbye.py src/greet_all.py
rm -rf tests/test_hello.py tests/test_goodbye.py tests/test_greet_all.py

# Keep hooks installed for further testing or remove
pantheon rollback  # Optional
```

---

## Next Steps

After successful quickstart:

1. Review generated QA report format
2. Test with different project types (Node.js, Go)
3. Validate error cases (failing tests, lint errors)
4. Benchmark parallel vs sequential execution time
5. Test backward compatibility with v0.1.x projects
