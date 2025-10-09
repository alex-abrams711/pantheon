## Development Workflow

### Overview

Uses DEV and QA agents for quality-first development.
Workflow: Implement tasks using DEV agents -> Validate task implementation using
QA agents -> Iterate -> Present results to user

_When to use each agent?_

- DEV - Use this agent when you need to implement a specific feature, fix a bug,
  or write code
- QA - Use this agent when you need to validate code quality after development
  work is complete

**Critical Rules**:
1. DEV agent is responsible for implementing tasks and self-verifying
2. QA agent is responsible for double-checking and verifying DEV's results
3. Main agent is responsible for managing workflow (NOT ALLOWED to work on
   tasks or verification)

### DEV Agent Context Package

```markdown
# Task Context: [Task ID]

## Task Details
**ID**: [Task ID]
**Description**: [Task description]
**Files**: [Comma-separated file paths]

## Acceptance Criteria
- [ ] [Specific acceptance criterion 1]
- [ ] [Specific acceptance criterion 2]

## Quality Standards
**Test Command**: [from plan.md]
**Lint Command**: [from plan.md]
**Type Command**: [from plan.md]
**Coverage Threshold**: [from plan.md]

## Related Requirements
[FR-XXX references from tasks.md]

## Tech Stack
**Language**: [from plan.md]
**Patterns**: [Architecture patterns to follow]
**Testing**: [Testing approach]
```

### QA Agent Context Package

```markdown
# QA Validation Context

## Task to Validate
- **T001**: [Task description]
  - Files: [file paths]

## Quality Standards
**Test Command**: [from plan.md]
**Coverage Command**: [test command with --cov flags]
**Coverage Threshold**: [from plan.md]
**Lint Command**: [from plan.md]
**Type Command**: [from plan.md]

## Definition of Done
- [ ] All tests pass (0 failures)
- [ ] Coverage >=[threshold]% branches
- [ ] No linting errors
- [ ] No type errors
- [ ] No code smells
- [ ] Manual testing passed (if functional changes)

## Project Root
[Absolute path to project root]

## Manual Testing Required
[YES/NO] - [Description if YES]
```

**Processing QA Report**:
- **PASS**: Present results to user
- **FAIL**: Re-execute the failed task with another DEV agent, providing
  updated context based on the QA Report

### Parallel Execution

For tasks marked `[P]` in tasks.md, invoke parallel agents in SINGLE message

### Phase Gate Checkpoints

At phase boundaries:
1. Present phase completion report with quality metrics
2. Wait for user approval ("yes" to proceed)
3. Only proceed after user confirms

**Phase Checkbox Management** (tasks.md):

Each phase has three checkboxes that MUST be updated:

```markdown
## Phase 3.1: Setup
- [ ] All tasks complete
- [ ] QA validated
- [ ] User validated
```

**Update Workflow**:

1. **After all DEV agents complete** -> Check "All tasks complete":
   ```bash
   # Update tasks.md
   sed -i '' '/^## Phase 3.1/,/^## Phase/ \
     s/- \[ \] All tasks complete/- [x] All tasks complete/' tasks.md
   ```

2. **After QA agent returns PASS** -> Check "QA validated":
   ```bash
   # Update tasks.md with timestamp
   DATE=$(date +%Y-%m-%d)
   sed -i '' '/^## Phase 3.1/,/^## Phase/ \
     s/- \[ \] QA validated/- [x] QA validated (PASS - '"$DATE"')/' tasks.md
   ```

3. **After user types "yes"** -> Check "User validated":
   ```bash
   # Update tasks.md with timestamp
   DATE=$(date +%Y-%m-%d)
   sed -i '' '/^## Phase 3.1/,/^## Phase/ \
     s/- \[ \] User validated/- [x] User validated ('"$DATE"')/' tasks.md
   ```

### Commit Strategy

Format:
```
[type]: [Task IDs] [Brief description]

[Detailed changes]
```
