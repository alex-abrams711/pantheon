# Proposal: Option 2 - Wrapper Commands

**Status**: Draft
**Created**: 2025-10-09
**Author**: Pantheon Team
**Version**: 1.0

---

## Executive Summary

Create Pantheon-specific slash commands (`/pantheon:plan`, `/pantheon:tasks`, `/pantheon:implement`) that **wrap** Spec Kit commands and add Pantheon's **complete implementation workflow**. This ensures every task is fully implemented and verified through the DEV → QA → iterate cycle, with explicit user control.

**Core Value**: Guaranteed task completion through independent validation, not just code quality metrics. Explicit commands provide clear control over when Pantheon orchestration activates.

**Recommendation**: Implement if user feedback indicates Option 1 lacks discoverability or explicit control.

---

## Problem Statement

### User Need
Users want Pantheon's **complete implementation workflow** integrated with Spec Kit, with:
- **Explicit control**: Clear visibility into when Pantheon orchestration is active
- **Discoverability**: Easy to understand what Pantheon adds
- **Verified completion**: Tasks are actually complete, not just marked complete
- **Independent validation**: QA agent catches gaps and incomplete work
- **Fallback**: Ability to use vanilla Spec Kit if needed

**The core problem**: Too many cases where tasks are marked complete but have clear gaps upon testing. Quality metrics alone don't ensure functional completeness.

### Current State (v0.4.0)
- Users run `/implement` (Spec Kit only)
- Users manually invoke DEV agents
- No explicit "Pantheon mode" - orchestration happens implicitly via CLAUDE.md

### Challenge
How can we provide an explicit, discoverable integration without modifying Spec Kit files?

---

## Proposed Solution

### Approach
Create wrapper slash commands that orchestrate Spec Kit workflows with Pantheon enhancements.

### Core Principle
**Composition over modification**: Call Spec Kit commands, then add Pantheon value on top.

### Command Structure

```
Standard Spec Kit:
/plan → Creates plan.md
/tasks → Creates tasks.md
/implement → Implements tasks

Pantheon Wrappers:
/pantheon:plan → Calls /plan, adds quality standards
/pantheon:tasks → Calls /tasks, adds subtasks/gates
/pantheon:implement → Calls /implement logic, orchestrates with DEV/QA agents
```

---

## Implementation Details

### Phase 1: Command Creation (Week 1)

**Files to Create**:
- `.claude/commands/pantheon/plan.md`
- `.claude/commands/pantheon/tasks.md`
- `.claude/commands/pantheon/implement.md`

#### Command 1: `/pantheon:plan`

**Location**: `.claude/commands/pantheon/plan.md`

**Content**:
```markdown
---
description: Create implementation plan with Pantheon quality standards
---

# Pantheon Plan Command

Create an implementation plan with integrated quality standards.

## Workflow

### Step 1: Generate Base Plan
Run the Spec Kit /plan command to create plan.md with implementation approach.

### Step 2: Bootstrap or Load Quality Config

**If `.pantheon/quality-config.json` exists**:
- Load test/lint/type commands and thresholds
- Proceed to Step 3

**If `.pantheon/quality-config.json` DOES NOT exist** (early-stage projects):
- **Option A (Recommended)**: Bootstrap inline quality discovery
  - Analyze project structure (package.json, requirements.txt, go.mod, etc.)
  - Detect test framework (pytest, jest, go test, vitest, etc.)
  - Detect linter (ruff, eslint, golangci-lint, biome, etc.)
  - Detect type checker (mypy, tsc, built-in types, etc.)
  - Generate `.pantheon/quality-config.json` with discovered commands
  - Display discovered commands to user

- **Option B**: Prompt user to run `/pantheon:contextualize`
  - Present message: "Run /pantheon:contextualize for more accurate quality discovery"
  - User can choose to run contextualize or proceed with inline discovery

**Key Principle**: Make quality config optional and discoverable during planning, not a hard prerequisite

### Step 3: Enhance Plan
Add the following sections to plan.md (if not already present):

#### Quality Standards
```markdown
## Quality Standards

### Test Strategy
**Command**: [from quality-config.json]
**Coverage Threshold**: [from quality-config.json] branches
**Framework**: [detected from project]

### Code Quality
**Linting**: [from quality-config.json]
**Type Checking**: [from quality-config.json]

### Definition of Done
- [ ] All tests pass (0 failures)
- [ ] Coverage ≥ [threshold]% branches
- [ ] No linting errors
- [ ] No type errors
- [ ] No code smells (console.log, TODO, unused imports)
```

#### Tech Stack
```markdown
## Tech Stack

**Language**: [from quality-config.json project_type]
**Framework**: [detected from package.json, requirements.txt, etc.]
**Testing**: [detected test framework]
**Build Tool**: [detected build tool]

## Verification Strategy
**Implementation**: DEV agents implement with TDD, verify against acceptance criteria
**Validation**: QA agent validates functional completion (not just quality metrics)
**Iteration**: DEV → QA → iterate until all acceptance criteria met
**Principle**: Tasks are complete when they WORK correctly, not just when tests pass
```

### Step 4: Present to User
Show the enhanced plan.md and confirm it's ready for /pantheon:tasks.

## Usage Example
```
User: /pantheon:plan
Orchestrator: Running Spec Kit /plan...
[Spec Kit creates plan.md]
Orchestrator: Enhancing with quality standards...
Orchestrator: Plan created with quality standards. Ready for /pantheon:tasks
```
```

#### Command 2: `/pantheon:tasks`

**Location**: `.claude/commands/pantheon/tasks.md`

**Content**:
```markdown
---
description: Create task breakdown with Pantheon subtasks and quality gates
---

# Pantheon Tasks Command

Create task breakdown with detailed subtasks and quality gates.

## Prerequisites
- plan.md must exist (run /pantheon:plan first)
- .pantheon/quality-config.json must exist (run /pantheon:contextualize first)

## Workflow

### Step 1: Generate Base Tasks
Run the Spec Kit /tasks command to create tasks.md with task breakdown.

### Step 2: Enhance Each Task
For each task in tasks.md, add subtasks in acceptance criteria format:

**Original** (Spec Kit format):
```markdown
### T001: Implement user authentication
**Files**: auth.ts, auth.test.ts
**Dependencies**: None
```

**Enhanced** (Pantheon format):
```markdown
### T001: Implement user authentication
**Files**: auth.ts, auth.test.ts
**Dependencies**: None
**Acceptance Criteria**:
- [ ] [Criterion 1 from plan.md]
- [ ] [Criterion 2 from plan.md]
- [ ] [Criterion 3 from plan.md]
**Quality Verification**:
- [ ] Tests pass
- [ ] Coverage ≥ threshold
- [ ] Linting passes
- [ ] Type checking passes
```

### Step 3: Add Quality Gates Section
Add quality gates tracking section at the end of tasks.md:

```markdown
## Quality Gates

### Implementation Phase
- [ ] All tasks complete

### Validation Phase
- [ ] QA validated

### Approval Phase
- [ ] User validated

### Commit Phase
- [ ] Git commits created
```

### Step 4: Mark Parallel Tasks
Analyze task dependencies and mark parallelizable tasks with [P]:

```markdown
- [P] T001: Setup database (no dependencies)
- [P] T002: Configure logging (no dependencies)
- [ ] T003: User service (depends on T001)
```

### Step 5: Present to User
Show enhanced tasks.md and confirm it's ready for /pantheon:implement.

## Usage Example
```
User: /pantheon:tasks
Orchestrator: Running Spec Kit /tasks...
[Spec Kit creates tasks.md]
Orchestrator: Adding subtasks and quality gates...
Orchestrator: Analyzing dependencies for parallel execution...
Orchestrator: Tasks created. Found 5 tasks, 2 can run in parallel. Ready for /pantheon:implement
```
```

#### Command 3: `/pantheon:implement`

**Location**: `.claude/commands/pantheon/implement.md`

**Content**:
```markdown
---
description: Implement tasks using Pantheon multi-agent orchestration
---

# Pantheon Implement Command

Execute implementation using DEV agents, QA validation, and quality gates.

## Prerequisites
- spec.md must exist
- plan.md must exist (run /pantheon:plan first)
- tasks.md must exist (run /pantheon:tasks first)
- .pantheon/quality-config.json must exist (run /pantheon:contextualize first)

## Workflow

### Step 1: Load Context
Read the following files:
- spec.md: Feature specification
- plan.md: Implementation approach, quality standards
- tasks.md: Task breakdown, dependencies, acceptance criteria
- .pantheon/quality-config.json: Quality commands

### Step 2: Analyze Dependencies
Parse tasks.md and create execution plan:
- Identify tasks marked [P] (parallel-safe)
- Identify task dependencies
- Group into batches (max 3 parallel agents per batch)
- Present execution plan to user for approval

**Example**:
```
Execution Plan:
Batch 1 (parallel): T001, T002, T004 (3 agents)
Batch 2 (sequential): T003 (depends on T001)
Batch 3 (parallel): T005, T006 (depends on T002, T003)

Estimated: 3 batches, 6 tasks total
```

### Step 3: Execute Task Batches
For each batch:

#### 3a. Prepare DEV Agent Context Packages
For each task in batch, create context package:

```markdown
# Task Context: [Task ID]

## Task Details
**ID**: [from tasks.md]
**Description**: [from tasks.md]
**Files**: [from tasks.md]

## Acceptance Criteria
[From tasks.md acceptance criteria section]

## Quality Standards
**Test Command**: [from quality-config.json]
**Lint Command**: [from quality-config.json]
**Type Command**: [from quality-config.json]
**Coverage Threshold**: [from quality-config.json]

## Related Requirements
[From spec.md, linked to this task in plan.md]

## Tech Stack
[From plan.md Tech Stack section]

## Constitution
[Relevant principles from constitution if present]
```

#### 3b. Invoke DEV Agents
**CRITICAL**: All parallel agents must be invoked in a SINGLE message.

**Example**:
```
Use the DEV agent to implement T001: [context package]
Use the DEV agent to implement T002: [context package]
Use the DEV agent to implement T004: [context package]
```

Wait for all DEV agents to complete before proceeding.

#### 3c. Handle DEV Results
- If any DEV returns BLOCKED: Address blocker, re-invoke (max 3 attempts)
- If all DEV return SUCCESS: Continue to QA validation
- Mark tasks as complete in tasks.md (check boxes)

#### 3d. Invoke QA Agent
Create QA validation context package:

```markdown
# QA Validation Context

## Tasks to Validate
[List all tasks from this batch with their files]

## Quality Standards
**Test Command**: [from quality-config.json]
**Coverage Command**: [test command with --cov flags]
**Coverage Threshold**: [from quality-config.json]
**Lint Command**: [from quality-config.json]
**Type Command**: [from quality-config.json]

## Definition of Done
[From plan.md]

## Project Root
[Absolute path]

## Manual Testing Required
[YES/NO based on whether tasks include functional changes]
```

Invoke QA agent with context package.

#### 3e. Process QA Results
**If QA returns PASS**:
- Mark "QA validated" checkbox in tasks.md
- Continue to Phase Gate Checkpoint

**If QA returns FAIL**:
- Parse QA report for issues by task
- Prepare DEV rework context packages:
  ```markdown
  # Task Context: [Task ID] - REWORK (Attempt [N])

  ## Original Task
  [Original context package]

  ## QA Findings
  **Status**: FAIL
  **Issues Found**:
  [Specific issues from QA report]

  **QA Recommendations**:
  [Specific recommendations from QA report]

  ## Required Fixes
  [Checklist of fixes needed]
  ```
- Re-invoke DEV agents with rework context
- Re-invoke QA agent (max 3 rework cycles)
- If still FAIL after 3 cycles: Stop and ask user for guidance

#### 3f. Phase Gate Checkpoint
After QA PASS:

1. **Generate Phase Completion Report**:
   ```markdown
   # Phase [N] Complete: [Phase Name]

   ## Completed Tasks
   - T001: [description] ✅
   - T002: [description] ✅

   ## Quality Metrics
   - Tests: [passing]/[total] passing
   - Coverage: [percentage]% branches (≥ [threshold]% required)
   - Linting: 0 errors
   - Type Checking: 0 errors

   ## Deliverables
   [What was implemented in this batch]

   ## Ready For
   [Next phase or "Final review"]
   ```

2. **Present to User**:
   ```
   Type 'yes' to proceed and create commits, 'review' to pause, or 'no' to halt.
   ```

3. **Wait for User Response**

4. **After "yes"**:
   - Mark "User validated" in tasks.md
   - Create git commits (see step 3g)
   - Continue to next batch

#### 3g. Create Git Commits
**CRITICAL**: Only orchestrator creates commits, never DEV agents.

For the batch of completed tasks:

**Commit Message Format**:
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
feat: T001-T003 Add user authentication

- Implement JWT-based authentication service
- Add login, logout, and token refresh endpoints
- Create comprehensive test suite with edge cases

Quality metrics:
- Tests: 42/42 passing
- Coverage: 94% branches
- Lint: 0 errors
- Type: 0 errors
```

### Step 4: Continue to Next Batch
Repeat Step 3 for each batch in execution plan.

### Step 5: Final Completion Report
After all batches complete:

```markdown
# Implementation Complete

## Summary
All [N] tasks completed successfully.

## Final Quality Metrics
- Total Tests: [passing]/[total] passing
- Overall Coverage: [percentage]% branches
- Linting: 0 errors
- Type Checking: 0 errors

## Commits Created
- [commit 1 SHA]: [description]
- [commit 2 SHA]: [description]

## Next Steps
[Suggestions for deployment, documentation updates, etc.]
```

## Usage Example
```
User: /pantheon:implement
Orchestrator: Loading context from spec.md, plan.md, tasks.md...
Orchestrator: Analyzing 6 tasks, creating execution plan...
Orchestrator:
  Batch 1 (parallel): T001, T002 (2 agents)
  Batch 2 (sequential): T003 (1 agent, depends on T001)
  Batch 3 (parallel): T004, T005, T006 (3 agents)
Orchestrator: Proceed with this plan? (yes/no)
User: yes
Orchestrator: Invoking 2 DEV agents for Batch 1...
[DEV agents work...]
Orchestrator: DEV agents complete. Invoking QA agent...
[QA validates...]
QA Agent: STATUS: PASS
Orchestrator: Phase 1 Complete. [shows metrics]
Orchestrator: Type 'yes' to create commits and continue
User: yes
Orchestrator: Commits created. Proceeding to Batch 2...
[continues through all batches]
Orchestrator: Implementation complete! [shows final report]
```
```

### Phase 2: CLI Integration (Week 1)

**Update `pantheon init` command** to install wrapper commands.

**File**: `src/pantheon/commands/install.py` (new module)

```python
def install_wrapper_commands(project_root: Path) -> None:
    """Install Pantheon wrapper commands for Spec Kit integration."""
    commands_dir = project_root / ".claude" / "commands" / "pantheon"
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Copy wrapper command files
    wrapper_commands = ["plan.md", "tasks.md", "implement.md"]
    for cmd in wrapper_commands:
        src = PACKAGE_ROOT / "commands" / cmd
        dst = commands_dir / cmd
        shutil.copy(src, dst)
        print(f"  ✓ Installed /pantheon:{cmd.replace('.md', '')}")
```

**Update `pantheon init`**:
```python
def init_command(project_root: Path, with_spec_kit: bool = False) -> None:
    """Initialize Pantheon in project."""
    # Existing: Copy agents
    install_agents(project_root)

    # Existing: Copy contextualize command
    install_contextualize_command(project_root)

    # New: Install wrapper commands if requested
    if with_spec_kit:
        install_wrapper_commands(project_root)
        print("\n✓ Spec Kit wrapper commands installed")
        print("  Use /pantheon:plan, /pantheon:tasks, /pantheon:implement")
```

**CLI Usage**:
```bash
# Standard installation
pantheon init

# With Spec Kit wrappers
pantheon init --with-spec-kit
```

### Phase 3: Testing (Week 2)

**Manual Test Checklist**:
- [ ] `/pantheon:plan` creates plan.md with quality standards
- [ ] `/pantheon:tasks` enhances tasks.md with subtasks
- [ ] `/pantheon:implement` orchestrates full workflow
- [ ] Commands work without Spec Kit installed (graceful degradation)
- [ ] Commands work with Spec Kit installed (composition)
- [ ] User can fall back to vanilla `/implement` if needed

**Test Projects**:
- Python project with Spec Kit
- Node.js project with Spec Kit
- Project without Spec Kit (commands should guide user)

### Phase 4: Documentation (Week 2)

**Update README.md**:
```markdown
## Spec Kit Integration (Optional)

Pantheon provides wrapper commands for enhanced Spec Kit workflows.

### Installation
```bash
# Install Pantheon with Spec Kit wrappers
pantheon init --with-spec-kit

# Or add wrappers to existing installation
pantheon add spec-kit-wrappers
```

### Usage
Use Pantheon commands instead of standard Spec Kit commands:

| Standard Spec Kit | Pantheon Wrapper | Enhancement |
|-------------------|------------------|-------------|
| `/plan` | `/pantheon:plan` | Adds quality standards, tech stack |
| `/tasks` | `/pantheon:tasks` | Adds subtasks, quality gates, parallel markers |
| `/implement` | `/pantheon:implement` | Multi-agent orchestration, QA validation |

### Workflow
```
1. /pantheon:plan → Creates plan with quality standards
2. /pantheon:tasks → Creates tasks with subtasks and gates
3. /pantheon:implement → Orchestrates implementation with DEV/QA agents
```

### Fallback
You can still use standard Spec Kit commands if needed:
```
/plan → Standard Spec Kit plan (no Pantheon enhancements)
/implement → Standard Spec Kit implement (no orchestration)
```
```

---

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────┐
│  User runs /pantheon:implement                      │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  Pantheon Wrapper Command                           │
│  - Executes Spec Kit logic (file creation/loading)  │
│  - Adds Pantheon enhancements                       │
│  - Activates multi-agent orchestration              │
└────────────────────┬────────────────────────────────┘
                     ↓
         ┌───────────┴───────────┐
         ↓                       ↓
┌──────────────────┐    ┌──────────────────┐
│  Spec Kit Logic  │    │  Pantheon Logic  │
│  (via SlashCmd)  │    │  (orchestration) │
└──────────────────┘    └──────────────────┘
         │                       │
         ↓                       ↓
    spec.md, plan.md,      DEV Agents
    tasks.md created       QA Agent
                           Git Commits
```

### Data Flow

**Sequential enhancement**:
1. Wrapper command invokes Spec Kit command (via SlashCommand tool or logic replication)
2. Spec Kit creates/loads spec.md, plan.md, tasks.md
3. Wrapper adds Pantheon enhancements (quality standards, subtasks, gates)
4. Wrapper activates orchestration (DEV/QA agents, commits)

**Clean separation**:
- Spec Kit commands remain unmodified
- Pantheon commands are separate files
- User chooses which to use

---

## Advantages

### 1. Explicit Control
- **User choice**: `/implement` vs `/pantheon:implement`
- **Clear separation**: Easy to understand what each command does
- **Fallback**: Can use vanilla Spec Kit if Pantheon has issues

### 2. Discoverability
- **Auto-complete**: `/pantheon:` prefix groups all Pantheon commands
- **Self-documenting**: Command names clearly indicate purpose
- **Onboarding**: New users see Pantheon commands in command palette

### 3. No Spec Kit Modification
- **Zero coupling**: Pantheon doesn't modify Spec Kit files
- **Version independence**: Works with any Spec Kit version
- **Safe**: Can't corrupt Spec Kit installation

### 4. Progressive Enhancement
- **Works without Spec Kit**: Commands can guide users to install it
- **Flexible**: Users choose level of integration
- **Testable**: Each command can be tested independently

### 5. Clear Ownership
- **Debugging**: Issues clearly belong to Pantheon or Spec Kit
- **Support**: Users know which tool to report issues to
- **Maintenance**: Pantheon team controls wrapper logic

---

## Disadvantages

### 1. Namespace Divergence
- **Concern**: Users must remember `/pantheon:implement` vs `/implement`
- **Mitigation**:
  - Document clearly in README
  - Provide aliases if possible
  - Add reminders in command output

### 2. Duplication Feeling
- **Concern**: Feels like duplicate commands
- **Mitigation**:
  - Frame as "enhanced" versions, not duplicates
  - Clearly document what each adds
  - Show value in examples

### 3. Spec Kit Logic Coupling (Partial)
- **Concern**: Wrappers must replicate or call Spec Kit logic
- **Mitigation**:
  - Option A: Use SlashCommand tool to invoke Spec Kit commands
  - Option B: Replicate minimal logic (file creation)
  - Option A preferred (less coupling)

### 4. Requires Installation Flag
- **Concern**: Users must opt-in with `--with-spec-kit`
- **Mitigation**:
  - Detect Spec Kit presence and offer installation
  - Provide `pantheon add spec-kit-wrappers` command
  - Document clearly in setup guide

### 5. Not True "Integration"
- **Concern**: Doesn't feel like frameworks are "integrated"
- **Mitigation**:
  - Market as "Pantheon-enhanced Spec Kit workflow"
  - Show seamless user experience in examples
  - Emphasize composition benefits

---

## Migration Path

### From v0.4.0 (Current)
**Effort**: Moderate (1-2 weeks)

**Steps**:
1. Create wrapper command files (plan.md, tasks.md, implement.md)
2. Add `install_wrapper_commands()` to CLI
3. Update `pantheon init` with `--with-spec-kit` flag
4. Test with sample projects
5. Document in README and guides

**User Impact**:
- Opt-in feature (doesn't affect existing users)
- Users who want integration run `pantheon init --with-spec-kit`
- Commands available immediately after installation

### From Option 1 (Pure CLAUDE.md)
**Effort**: Low (additive)

If Option 1 is implemented first, Option 2 can be added later:
- Option 1 provides automatic integration
- Option 2 provides explicit control
- Both can coexist (user chooses preference)

---

## Success Metrics

### Technical Metrics
- [ ] Commands successfully invoke Spec Kit logic (or replicate it)
- [ ] Commands successfully add Pantheon enhancements
- [ ] Commands work with Spec Kit v0.0.50, v0.0.55, v0.1.0
- [ ] Zero modification of Spec Kit files

### User Experience Metrics
- [ ] Users can discover commands via auto-complete
- [ ] Users understand difference between `/implement` and `/pantheon:implement`
- [ ] Users successfully complete full workflow (plan → tasks → implement)
- [ ] Clear error messages if prerequisites missing

### Quality Metrics
- [ ] 90% of test scenarios pass
- [ ] Commands produce correct enhancements
- [ ] No conflicts with vanilla Spec Kit usage

---

## Open Questions

### 1. How to Invoke Spec Kit Logic?

**Option A: SlashCommand Tool** (Preferred)
```markdown
# In /pantheon:plan command
Run the /plan slash command to create plan.md
```
- Pros: No logic duplication, always compatible with Spec Kit updates
- Cons: Requires SlashCommand tool, adds dependency

**Option B: Logic Replication**
```markdown
# In /pantheon:plan command
Create plan.md based on spec.md (replicate /plan logic)
```
- Pros: No dependency on Spec Kit
- Cons: Duplicates logic, breaks if Spec Kit changes approach

**Recommendation**: Option A (SlashCommand tool)

### 2. Should Wrappers Be Default?

**Option A: Opt-in** (Current proposal)
- `pantheon init` → Installs agents only
- `pantheon init --with-spec-kit` → Installs agents + wrappers

**Option B: Auto-detect and offer**
```bash
pantheon init
# Detects Spec Kit installation
"Spec Kit detected. Install wrapper commands? (y/n)"
```

**Recommendation**: Option B (better UX)

### 3. What if Spec Kit Not Installed?

**Behavior when user runs `/pantheon:implement` without Spec Kit**:
```
Error: Spec Kit not detected

Pantheon wrapper commands require Spec Kit to be installed.

Install Spec Kit:
  uvx spec-kit init

Or use direct DEV agent invocation:
  "Use the DEV agent to implement [task]"
```

**Alternative**: Commands degrade gracefully and work without Spec Kit
- `/pantheon:plan` → Creates plan.md using generic template
- `/pantheon:tasks` → Creates tasks.md using generic template
- `/pantheon:implement` → Orchestrates without Spec Kit structure

**Recommendation**: Graceful degradation (more flexible)

---

## Alternatives Considered

### Alternative 1: Pure CLAUDE.md
**See**: `option-1-pure-claude-md.md`

### Alternative 2: Modify Spec Kit Files (v0.3.0 approach)
**Rejected**: Maintenance burden, tight coupling, removed in v0.4.0

### Alternative 3: Slash Command Integration
**Deferred**: Complexity, non-deterministic, harder to test

---

## Recommendation

**Implement Option 2 (Wrapper Commands) IF**:
- User feedback indicates Option 1 lacks discoverability
- Users want explicit control over when Pantheon activates
- Users want fallback to vanilla Spec Kit

**Otherwise, prefer Option 1** (simpler, less code, more flexible)

**Hybrid Approach**:
- Implement Option 1 first (CLAUDE.md automatic integration)
- Add Option 2 later if users request it
- Both can coexist (automatic + explicit modes)

---

## Next Steps (If Approved)

1. **Week 1**: Create wrapper command files
   - Write plan.md wrapper (4 hours)
   - Write tasks.md wrapper (4 hours)
   - Write implement.md wrapper (8 hours)

2. **Week 1**: Update CLI
   - Add `install_wrapper_commands()` (2 hours)
   - Add `--with-spec-kit` flag (1 hour)
   - Add auto-detection logic (2 hours)

3. **Week 2**: Testing
   - Manual testing with sample projects (8 hours)
   - Edge case validation (4 hours)

4. **Week 2**: Documentation
   - Update README.md (2 hours)
   - Create integration guide (4 hours)
   - Add troubleshooting section (2 hours)

5. **Release**: v0.5.0 or v0.4.1

**Total Effort**: 2 weeks (40-50 hours)

---

## Appendix A: Command Comparison

### /plan vs /pantheon:plan

**Standard /plan**:
```markdown
# Implementation Plan

## Approach
[Implementation approach]

## Architecture
[System design]

## Tasks
[High-level task breakdown]
```

**Enhanced /pantheon:plan**:
```markdown
# Implementation Plan

## Approach
[Implementation approach]

## Architecture
[System design]

## Tasks
[High-level task breakdown]

## Quality Standards ← ADDED BY PANTHEON
**Test Command**: pytest tests/ -v
**Lint Command**: ruff check src/ tests/
**Type Command**: mypy src/ --strict
**Coverage Threshold**: 80% branches

## Tech Stack ← ADDED BY PANTHEON
**Language**: Python 3.11
**Framework**: FastAPI
**Testing**: pytest + pytest-cov
**Build**: uv
```

### /tasks vs /pantheon:tasks

**Standard /tasks**:
```markdown
## Tasks

### T001: Setup database
**Files**: db.py
**Dependencies**: None
```

**Enhanced /pantheon:tasks**:
```markdown
## Tasks

### T001: Setup database
**Files**: db.py
**Dependencies**: None
**Acceptance Criteria**: ← ADDED BY PANTHEON
- [ ] Initialize PostgreSQL connection pool
- [ ] Create schema migration system
- [ ] Add connection health checks
**Quality Verification**: ← ADDED BY PANTHEON
- [ ] Tests pass
- [ ] Coverage ≥ 80%
- [ ] Linting passes
- [ ] Type checking passes

## Quality Gates ← ADDED BY PANTHEON
- [ ] All tasks complete
- [ ] QA validated
- [ ] User validated
```

---

## Appendix B: Example User Journey

**Setup** (one-time):
```bash
# Install Pantheon with Spec Kit wrappers
uvx pantheon-agents init --with-spec-kit

# Spec Kit should already be installed
# If not: uvx spec-kit init

# Discover quality commands
# In Claude Code:
/pantheon:contextualize
```

**Development Workflow**:
```
User: /pantheon:plan
Orchestrator: Running Spec Kit /plan command...
[Spec Kit creates plan.md]
Orchestrator: Enhancing with quality standards from quality-config.json...
Orchestrator: Plan created:
  - Implementation approach ✓
  - Quality standards ✓
  - Tech stack ✓
Orchestrator: Ready for /pantheon:tasks

User: /pantheon:tasks
Orchestrator: Running Spec Kit /tasks command...
[Spec Kit creates tasks.md]
Orchestrator: Adding acceptance criteria and quality gates...
Orchestrator: Tasks created:
  - 6 tasks identified
  - Acceptance criteria added ✓
  - Quality gates added ✓
  - 3 tasks can run in parallel [P]
Orchestrator: Ready for /pantheon:implement

User: /pantheon:implement
Orchestrator: Loading context...
Orchestrator: Execution plan:
  Batch 1 (parallel): T001, T002, T003 (3 agents)
  Batch 2 (sequential): T004 (depends on T001)
  Batch 3 (parallel): T005, T006 (2 agents)
Orchestrator: Proceed? (yes/no)
User: yes
Orchestrator: Invoking 3 DEV agents...
[DEV agents implement T001, T002, T003...]
Orchestrator: All DEV agents complete. Invoking QA agent...
[QA agent validates...]
QA: STATUS: PASS - All quality checks passed
Orchestrator: Phase 1 Complete
  - Tests: 42/42 passing
  - Coverage: 94% branches
  - Linting: 0 errors
  - Type checking: 0 errors
Orchestrator: Type 'yes' to create commits and continue
User: yes
Orchestrator: Commits created:
  - abc123f: feat: T001-T003 Add core database functionality
Orchestrator: Proceeding to Batch 2...
[continues through all batches...]
Orchestrator: Implementation complete! All 6 tasks finished.
```

**User Experience**: Explicit, controlled, transparent
