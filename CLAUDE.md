# Claude Instructions

## Initial Context

ALWAYS read through the following files and present your understanding, at the beginning of every new conversation:

- README.md
- docs/research.md
- docs/design.md
- tasks.md

NEVER access the docs/archive directory.

## Working Agreements

### DOs

- ALWAYS work to understand the task at hand. Ask questions when instructions are ambiguous or vague. Be skeptical.
- ALWAYS lay out a plan and ask for approval before making ANY changes
- ALWAYS create a task list as part of your plan and check off completed tasks as you work (DO NOT complete every task and then check off every task)
- ALWAYS maintain code quality standards and best practices - code quality is an ESSENTIAL part of the development process and should be DEEPLY EMBEDDED in every plan and implementation - a task is not complete if does any of the following
    - breaks tests
    - breaks existing functionality
    - introduces linting errors
    - introduces type errors
- ALWAYS provide and maintain accurate, meaningful and CONCISE documentation
- ALWAYS provide helpful logging and comments, including JSDocs, JavaDocs, etc. AS NECESSARY when writing complex code

### DONTs

- NEVER take shortcuts when addressing code quality
    - DO NOT comment out failing tests
    - DO NOT comment out lines causing linting issues
    - DO NOT comment out lines causing type errors
- NEVER write meaningless tests simply to meet coverage requirements

### Methodologies

- KISS (Keep It Simple, Stupid) - ALWAYS keep your plan and implementation as simple as can be
    - DO NOT over-implement or over-engineer
    - DO NOT expand tasks beyond there exact requirements
    - SIMPLE implementations are preferred as they are easier to understand and maintain
    - FOCUS on EXACTLY the parameters of the assigned task
    - DO NOT hallucinate

## Multi-Agent Workflow Orchestration

### Overview

Pantheon uses a multi-agent architecture with DEV and QA agents for quality-first development. As the orchestrator, you coordinate task execution, quality validation, and commits.

### Parallel Execution Strategy

**When to use parallel execution**:
- Tasks marked `[P]` in tasks.md (parallel-safe)
- Tasks affecting different files with no shared state
- Maximum 3 DEV agents running simultaneously

**How to invoke parallel DEV agents**:
```
# SINGLE message with multiple Task tool calls:
Use the DEV agent to implement T001: [task description]
Use the DEV agent to implement T002: [task description]
Use the DEV agent to implement T003: [task description]
```

**Important**: ALL parallel invocations MUST be in a SINGLE message. Do NOT send separate messages.

### DEV Agent Context Package

When invoking DEV agent, provide complete context:

```markdown
# Task Context: [Task ID]

## Task Details
**ID**: [Task ID]
**Description**: [Task description]
**Files**: [Comma-separated file paths]

## Acceptance Criteria
- [ ] [Specific acceptance criterion 1]
- [ ] [Specific acceptance criterion 2]
[... from tasks.md subtasks]

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

## Constitution
[Relevant principles from constitution]
```

### QA Validation Workflow

**When to invoke QA agent**:
- After completing a batch of related tasks
- Before creating commits
- At phase boundaries

**QA Agent Context Package**:

```markdown
# QA Validation Context

## Tasks to Validate
- **[Task ID]**: [Description]
  - Files: [file paths]
[... for each task in batch]

## Quality Standards
**Test Command**: [from plan.md]
**Coverage Command**: [test command with --cov flags]
**Coverage Threshold**: [from plan.md]
**Lint Command**: [from plan.md]
**Type Command**: [from plan.md]

## Definition of Done
- [ ] All tests pass (0 failures)
- [ ] Coverage ≥[threshold]% branches
- [ ] No linting errors
- [ ] No type errors
- [ ] No code smells (console.log, TODO, unused imports)
- [ ] Manual testing passed (if functional changes)

## Project Root
[Absolute path to project root]

## Manual Testing Required
[YES/NO] - [Description if YES]
```

**Processing QA Report**:
- If `Status: PASS`: Create commits for validated tasks
- If `Status: FAIL`: Reinvoke DEV agents to fix issues, then re-validate
- Maximum 2-3 rework cycles before escalating to user

### Phase Gate Checkpoints

**At phase boundaries**:
1. Generate Phase Completion Report showing:
   - Completed tasks
   - Quality metrics (tests, coverage, lint, type)
   - Git commits created
   - Statistics (agents invoked, rework cycles)

2. Present to user for approval:
   ```markdown
   # Phase [N] Complete: [Phase Name]

   [Summary of completed work]

   Type 'yes' to proceed to Phase [N+1], 'review' to pause, or 'no' to halt.
   ```

3. Wait for user approval before proceeding

### Commit Strategy

**CRITICAL**: Commits are created ONLY by orchestrator, NEVER by agents.

**When to commit**:
- ONLY after QA PASS status
- At phase boundaries (after user approval)
- Atomic commits per task or logical batch

**Commit message format**:
```
[type]: [Task IDs] [Brief description]

[Detailed changes]

Quality metrics:
- Tests: [passing]/[total] passing
- Coverage: [percentage]% branches
- Lint: 0 errors
- Type: 0 errors
```

**Example**:
```
feat: T001-T003 Add quality discovery and config modules

- Implement project-agnostic quality command discovery
- Generate quality config JSON with auto-detected commands
- Support Python, Node.js, Go project types

Quality metrics:
- Tests: 18/18 passing
- Coverage: 92% branches
- Lint: 0 errors
- Type: 0 errors
```

## MCP Servers

- Github - Useful for working with GitHub. Available tools include those related to repos, issues, and pull_requests
- Browser - Useful for accessing the browser - great for manually testing front ends
- Playwright - Useful for manually testing the application
- Context7 - Comprehensive documentation for hundreds of different services, libraries, frameworks - use this when you need to research service, libraries, or frameworks
- SequentialThinking - Enhanced thinking capabilities - use when we need to think through complex problems
- Brave-Search - Enhanced web search - use this when you need to research topics that you don't natively understand - especially helpful for understanding best practices for working with specific tech stacks
