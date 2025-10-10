# Proposal: Option 3 - Two-Phase Installation (CLI + LLM)

**Status**: Draft
**Created**: 2025-10-10
**Author**: Pantheon Team
**Version**: 1.0

---

## Executive Summary

Pantheon uses a **two-phase installation** approach:
1. **CLI Phase** (`pantheon init`): Deterministic file copying and setup
2. **LLM Phase** (`/pantheon:init`): Intelligent modifications via Claude

This ensures every task is fully implemented and verified through the DEV → QA → iterate cycle, with optional planning framework for structured workflows.

**Core Value**: Guaranteed task completion through independent validation. Flexible installation (with or without planning framework).

**Recommendation**: Implement this streamlined approach for fast testing and iteration.

---

## Problem Statement

### User Need
- **Complete implementation workflow**: Tasks are actually complete, not just marked complete
- **Flexible complexity**: Choose structured planning OR lightweight workflow
- **Independent validation**: QA agent catches gaps and incomplete work
- **No external dependencies**: Pantheon owns all code
- **User control**: Review changes before applying

**The core problem**: Too many cases where tasks are marked complete but have clear gaps upon testing. Need a solution that works standalone OR with structured planning, without brittle external integrations.

---

## Proposed Solution

### Two-Phase Installation

#### **Phase 1: CLI (`pantheon init`)**
Deterministic operations - copy files, create directories, configure hooks.

#### **Phase 2: LLM (`/pantheon:init`)**
Intelligent operations - modify files, add workflow enhancements, get user approval.

### Installation Modes

```bash
# Mode 1: With Planning Framework (Spec Kit-compatible)
pantheon init --workflow spec-kit

# Mode 2: Lightweight (Direct workflow)
pantheon init
```

---

## Architecture

### Mode 1: With Planning Framework

```
CLI Phase (pantheon init --workflow spec-kit):
  ├─ Copy bundled planning commands → .claude/commands/
  │  ├─ plan.md (Pantheon's version, Spec Kit-compatible)
  │  ├─ tasks.md
  │  └─ implement.md
  ├─ Copy DEV/QA agents → .claude/agents/
  ├─ Copy hooks → .pantheon/hooks/
  ├─ Copy /pantheon:init command → .claude/commands/pantheon/
  ├─ Copy /pantheon:contextualize → .claude/commands/pantheon/
  ├─ Create base CLAUDE.md
  ├─ Create base constitution.md
  └─ Configure hooks in .claude/settings.json

LLM Phase (/pantheon:init in Claude):
  ├─ Detect: Planning framework installed
  ├─ Modify /plan command:
  │  └─ Add: Quality config bootstrap, verification strategy
  ├─ Modify /tasks command:
  │  └─ Add: Acceptance criteria format, quality gates
  ├─ Modify /implement command:
  │  └─ Add: Complete DEV → QA → iterate orchestration
  ├─ Modify CLAUDE.md:
  │  └─ Add: Planning framework workflow instructions
  ├─ Modify constitution.md:
  │  └─ Add: Quality standards, success criteria
  ├─ Show diffs for each file
  ├─ Wait for user approval
  ├─ Apply changes (insert with HTML comment markers)
  └─ Report: "Initialization complete"
```

### Mode 2: Lightweight

```
CLI Phase (pantheon init):
  ├─ Copy DEV/QA agents → .claude/agents/
  ├─ Copy hooks → .pantheon/hooks/
  ├─ Copy /pantheon:init command → .claude/commands/pantheon/
  ├─ Copy /pantheon:contextualize → .claude/commands/pantheon/
  ├─ Create base CLAUDE.md
  └─ Configure hooks in .claude/settings.json

LLM Phase (/pantheon:init in Claude):
  ├─ Detect: No planning framework
  ├─ Modify CLAUDE.md:
  │  └─ Add: Direct workflow instructions (conversation-based)
  ├─ Show diff
  ├─ Wait for user approval
  ├─ Apply changes
  └─ Report: "Initialization complete"
```

---

## Implementation Details

### Phase 1: CLI Implementation

#### Update `pantheon init` Command

**File**: `src/pantheon/cli.py`

```python
@cli.command()
@click.option(
    '--workflow',
    type=click.Choice(['spec-kit']),
    help='Install with planning framework (spec-kit compatible)'
)
def init(workflow: Optional[str] = None):
    """Initialize Pantheon in your project."""
    project_root = Path.cwd()

    print("🎯 Initializing Pantheon...")

    # Always install these
    install_agents(project_root)
    install_hooks(project_root)
    install_pantheon_commands(project_root)  # /pantheon:init, /pantheon:contextualize
    create_base_claude_md(project_root)

    # Optionally install planning framework
    if workflow == 'spec-kit':
        install_planning_framework(project_root)
        create_base_constitution(project_root)
        print("  ✓ Planning framework installed")

    print("\n✅ Pantheon installed successfully!")
    print("\nNext steps:")
    print("  1. Open your project in Claude Code")
    print("  2. Run: /pantheon:init")
    print("  3. Review and approve the workflow enhancements")
```

#### New Functions

**install_planning_framework()**:
```python
def install_planning_framework(project_root: Path) -> None:
    """Install Spec Kit-compatible planning commands."""
    commands_dir = project_root / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Copy bundled planning commands
    planning_commands = ["plan.md", "tasks.md", "implement.md"]
    for cmd in planning_commands:
        src = PACKAGE_ROOT / "templates" / "planning" / cmd
        dst = commands_dir / cmd
        shutil.copy(src, dst)
        print(f"  ✓ Installed /{cmd.replace('.md', '')}")
```

**create_base_constitution()**:
```python
def create_base_constitution(project_root: Path) -> None:
    """Create base constitution.md file."""
    constitution_path = project_root / "constitution.md"

    if constitution_path.exists():
        print("  ⚠ constitution.md already exists, skipping")
        return

    base_content = """# Project Constitution

## Principles
[Your project principles here]

<!-- PANTHEON:QUALITY_STANDARDS:START -->
<!-- This section will be populated by /pantheon:init -->
<!-- PANTHEON:QUALITY_STANDARDS:END -->

<!-- PANTHEON:SUCCESS_CRITERIA:START -->
<!-- This section will be populated by /pantheon:init -->
<!-- PANTHEON:SUCCESS_CRITERIA:END -->
"""

    constitution_path.write_text(base_content)
    print("  ✓ Created constitution.md")
```

**install_pantheon_commands()**:
```python
def install_pantheon_commands(project_root: Path) -> None:
    """Install /pantheon:* slash commands."""
    pantheon_dir = project_root / ".claude" / "commands" / "pantheon"
    pantheon_dir.mkdir(parents=True, exist_ok=True)

    # Copy init and contextualize commands
    commands = ["init.md", "contextualize.md"]
    for cmd in commands:
        src = PACKAGE_ROOT / "commands" / cmd
        dst = pantheon_dir / cmd
        shutil.copy(src, dst)
        print(f"  ✓ Installed /pantheon:{cmd.replace('.md', '')}")
```

#### Bundle Planning Commands

**Create**: `src/pantheon/templates/planning/`

Copy minimal Spec Kit-compatible versions of:
- `plan.md` - Create implementation plan
- `tasks.md` - Break down into tasks
- `implement.md` - Execute implementation

These are Pantheon-owned, bundled in the package, versioned with Pantheon releases.

**Note**: Will need to ensure licensing/attribution is appropriate. Consider renaming to "Pantheon Planning Framework" if needed.

---

### Phase 2: LLM Command Implementation

#### Create `/pantheon:init` Slash Command

**File**: `src/pantheon/commands/init.md`

```markdown
---
description: Initialize Pantheon workflow enhancements
---

# Pantheon Initialization

Apply Pantheon workflow enhancements to your project.

## Detection

Check which mode is installed:
- **Planning Framework Mode**: `.claude/commands/implement.md` exists
- **Lightweight Mode**: Only `.claude/agents/` and `.pantheon/hooks/` exist

## Planning Framework Mode

Enhance the following files with Pantheon workflow:

### 1. Enhance /plan Command

**File**: `.claude/commands/plan.md`

**Insert Location**: After main content, before examples (if any)

**Content to Add**:
```markdown
<!-- PANTHEON:ENHANCEMENTS:START -->

## Pantheon Quality Bootstrap

After creating the base plan:

### Step 1: Bootstrap Quality Configuration

**If `.pantheon/quality-config.json` does NOT exist:**
- Analyze project structure (package.json, requirements.txt, go.mod, etc.)
- Detect test framework (pytest, jest, go test, vitest, etc.)
- Detect linter (ruff, eslint, golangci-lint, biome, etc.)
- Detect type checker (mypy, tsc, built-in types, etc.)
- Generate `.pantheon/quality-config.json`
- OR prompt user: "Run /pantheon:contextualize for more accurate discovery"

**If quality-config.json exists:**
- Load existing configuration

### Step 2: Enhance plan.md

Add these sections to plan.md:

#### Quality Standards
```markdown
## Quality Standards
**Test**: [from quality-config.json]
**Lint**: [from quality-config.json]
**Type**: [from quality-config.json]
**Coverage**: [threshold from quality-config.json or 80% default]
```

#### Tech Stack
```markdown
## Tech Stack
**Language**: [detected]
**Framework**: [detected]
**Testing**: [detected]
**Build**: [detected]
```

#### Verification Strategy
```markdown
## Verification Strategy
- DEV agents implement with TDD
- QA agent validates functional completion
- Iterate DEV → QA until acceptance criteria met
- Tasks complete when they WORK correctly, not just when tests pass
```

### Step 3: Update Constitution

Add quality standards to constitution.md (see constitution.md enhancement section below).

<!-- PANTHEON:ENHANCEMENTS:END -->
```

**Show user the diff**, wait for approval, then apply.

---

### 2. Enhance /tasks Command

**File**: `.claude/commands/tasks.md`

**Insert Location**: After main content

**Content to Add**:
```markdown
<!-- PANTHEON:ENHANCEMENTS:START -->

## Pantheon Task Enhancement

After creating base tasks:

### Format Each Task

For EVERY task, add:

**Acceptance Criteria** (what makes this functionally complete):
```markdown
**Acceptance Criteria**:
- [ ] [Functional requirement 1]
- [ ] [Functional requirement 2]
- [ ] [Functional requirement 3]
```

**Verification Checklist**:
```markdown
**Verification**:
- [ ] Tests pass
- [ ] Coverage ≥ threshold
- [ ] Linting passes
- [ ] Type checking passes
- [ ] QA validates functional completion
```

### Add Quality Gates

At end of tasks.md:
```markdown
## Quality Gates
- [ ] All tasks complete
- [ ] QA validated
- [ ] User validated
```

### Mark Parallel Tasks

Analyze dependencies, mark parallel-safe tasks with `[P]`.

<!-- PANTHEON:ENHANCEMENTS:END -->
```

**Show user the diff**, wait for approval, then apply.

---

### 3. Enhance /implement Command

**File**: `.claude/commands/implement.md`

**Insert Location**: After main content

**Content to Add**:
```markdown
<!-- PANTHEON:ORCHESTRATION:START -->

## Pantheon Complete Implementation Workflow

Execute the following workflow in strict order:

### PHASE 1: CONTEXT LOADING
1. Read spec.md, plan.md, tasks.md
2. Read .pantheon/quality-config.json
3. Verify all files exist

### PHASE 2: DEPENDENCY ANALYSIS
4. Parse tasks.md for dependencies
5. Identify parallel-safe tasks (marked [P])
6. Create execution plan (batches, max 3 parallel)
7. Present plan to user for approval
8. WAIT for user approval

### PHASE 3: BATCH EXECUTION

For each batch:

9. **Prepare DEV Context Packages**:
   - Task Details (ID, description, files)
   - Acceptance Criteria (from tasks.md)
   - Quality Standards (from quality-config.json)
   - Tech Stack (from plan.md)

10. **Invoke DEV Agents** (parallel if independent):
    - All parallel invocations in SINGLE message
    - Wait for ALL to complete

11. **Handle DEV Results**:
    - If BLOCKED: address issue, re-invoke (max 3 attempts)
    - If SUCCESS: mark complete, continue

12. **MANDATORY: Invoke QA Agent**:
    - QA validates FUNCTIONAL COMPLETION (not just metrics)
    - QA checks acceptance criteria MET
    - QA performs manual testing if needed

13. **Process QA Results**:
    - IF PASS: Mark "QA validated", continue to checkpoint
    - IF FAIL: Prepare rework context, re-invoke DEV, re-invoke QA (max 3 cycles)

14. **Phase Gate Checkpoint** (after QA PASS):
    - Generate phase completion report
    - Present to user
    - Prompt: "Type 'yes' to create commits"
    - WAIT for user to type "yes"

15. **Create Commits** (only after user approval):
    - Mark "User validated"
    - Create atomic commits
    - Include quality metrics

### PHASE 4: CONTINUATION
16. If more batches: return to PHASE 3
17. If complete: generate final report

**CRITICAL**: DEV → QA → iterate ensures tasks are ACTUALLY complete.

<!-- PANTHEON:ORCHESTRATION:END -->
```

**Show user the diff**, wait for approval, then apply.

---

### 4. Enhance CLAUDE.md

**File**: `CLAUDE.md`

**Insert Location**: End of file (or after Working Agreements section)

**Content to Add**:
```markdown
<!-- PANTHEON:WORKFLOW:START -->

## Pantheon Planning Framework Integration

When using planning commands (/plan, /tasks, /implement), follow the Pantheon workflow enhancements embedded in those commands.

Key principles:
- Quality config bootstrapped during /plan
- Acceptance criteria define functional completeness
- DEV → QA → iterate ensures tasks ACTUALLY complete
- User approval required before commits
- QA validates functional requirements, not just quality metrics

See command files for detailed workflow steps.

<!-- PANTHEON:WORKFLOW:END -->
```

**Show user the diff**, wait for approval, then apply.

---

### 5. Enhance constitution.md

**File**: `constitution.md`

**Insert Location**: Replace placeholder sections with actual content

**Content to Add**:
```markdown
<!-- PANTHEON:QUALITY_STANDARDS:START -->
## Quality Standards

**Test Command**: [from quality-config.json or detected]
**Lint Command**: [from quality-config.json or detected]
**Type Check**: [from quality-config.json or detected]
**Coverage Threshold**: [from quality-config.json or 80% default]

**Verification Approach**:
- DEV agents implement with test-driven development
- QA agent validates functional completion independently
- Iterate until all acceptance criteria met
<!-- PANTHEON:QUALITY_STANDARDS:END -->

<!-- PANTHEON:SUCCESS_CRITERIA:START -->
## Success Criteria

### Task Completion
- All acceptance criteria met (functional requirements satisfied)
- QA validation passed (independent verification)
- All quality gates cleared (tests, coverage, lint, type)

### Quality Assurance
- No failing tests
- Coverage meets or exceeds threshold
- No linting errors
- No type errors
- No code smells (TODO, console.log, unused imports)

### Workflow Completion
- User approval obtained before commits
- Commits include quality metrics
- All tasks marked complete in tasks.md
<!-- PANTHEON:SUCCESS_CRITERIA:END -->
```

**Show user the diff**, wait for approval, then apply.

---

## Lightweight Mode

If planning framework NOT detected:

### Enhance CLAUDE.md Only

**Content to Add**:
```markdown
<!-- PANTHEON:DIRECT_WORKFLOW:START -->

## Pantheon Direct Workflow

When user requests implementation work:

### 1. Clarify Requirements
Ask clarifying questions to understand:
- What functionality is needed
- Acceptance criteria (what makes it "complete")
- Success measures (how to verify it works)

### 2. Bootstrap Quality Config
If `.pantheon/quality-config.json` doesn't exist:
- Analyze project structure
- Detect test/lint/type commands
- Generate quality-config.json
- OR prompt: "Run /pantheon:contextualize"

### 3. Create Work Tracking
Create `.pantheon/work.md`:
```markdown
## Current Work: [Feature name]

### Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

### Tasks
- [ ] [Task 1]
- [ ] [Task 2]

### Quality Gates
- [ ] QA validated
- [ ] User validated
```

### 4. Implement with DEV → QA Cycle
- Invoke DEV agent with context (acceptance criteria, quality standards)
- Invoke QA agent to validate functional completion
- If QA FAIL: re-invoke DEV with specific issues
- Iterate until QA PASS

### 5. Get User Approval & Commit
- Present completion report
- Wait for user "yes"
- Create commits with quality metrics

**CRITICAL**: Tasks complete when they WORK correctly, validated by QA.

<!-- PANTHEON:DIRECT_WORKFLOW:END -->
```

---

## User Experience

### Workflow: Planning Framework Mode

```bash
# Installation
$ cd my-project
$ pantheon init --workflow spec-kit
🎯 Initializing Pantheon...
  ✓ Installed DEV agent
  ✓ Installed QA agent
  ✓ Installed /plan
  ✓ Installed /tasks
  ✓ Installed /implement
  ✓ Installed /pantheon:init
  ✓ Installed /pantheon:contextualize
  ✓ Planning framework installed
  ✓ Configured hooks

✅ Pantheon installed successfully!

Next steps:
  1. Open your project in Claude Code
  2. Run: /pantheon:init
  3. Review and approve the workflow enhancements

$ code .
```

```
# In Claude Code

User: /pantheon:init

Orchestrator: Initializing Pantheon workflow enhancements...

Orchestrator: I'll enhance the following files with Pantheon workflow:
  1. /plan command → Quality bootstrap, verification strategy
  2. /tasks command → Acceptance criteria, quality gates
  3. /implement command → DEV → QA orchestration
  4. CLAUDE.md → Workflow instructions
  5. constitution.md → Quality standards, success criteria

Let me show you what I'll add to each file:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE: .claude/commands/plan.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
+ <!-- PANTHEON:ENHANCEMENTS:START -->
+
+ ## Pantheon Quality Bootstrap
+
+ After creating the base plan:
+ ...
+ <!-- PANTHEON:ENHANCEMENTS:END -->
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Shows diffs for all 5 files...]

Orchestrator: Do you approve these changes? (Type 'yes' to apply, 'no' to cancel)

User: yes

Orchestrator: Applying changes...
  ✓ Enhanced plan.md
  ✓ Enhanced tasks.md
  ✓ Enhanced implement.md
  ✓ Enhanced CLAUDE.md
  ✓ Enhanced constitution.md

✅ Pantheon initialization complete!

You can now use:
  /plan → Create plan with quality standards
  /tasks → Break down with acceptance criteria
  /implement → Complete DEV → QA workflow
```

### Workflow: Lightweight Mode

```bash
# Installation
$ cd my-project
$ pantheon init
🎯 Initializing Pantheon...
  ✓ Installed DEV agent
  ✓ Installed QA agent
  ✓ Installed /pantheon:init
  ✓ Installed /pantheon:contextualize
  ✓ Configured hooks

✅ Pantheon installed successfully!
```

```
# In Claude Code

User: /pantheon:init

Orchestrator: Initializing Pantheon direct workflow...

I'll enhance CLAUDE.md with direct workflow instructions.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE: CLAUDE.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
+ <!-- PANTHEON:DIRECT_WORKFLOW:START -->
+
+ ## Pantheon Direct Workflow
+ ...
+ <!-- PANTHEON:DIRECT_WORKFLOW:END -->
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Approve changes? (yes/no)

User: yes

Orchestrator:
  ✓ Enhanced CLAUDE.md

✅ Initialization complete!

You can now directly request implementation work, and I'll follow
the Pantheon DEV → QA workflow automatically.
```

---

## Implementation Phases

### Phase 1: Core CLI (Week 1)
- [ ] Create `src/pantheon/templates/planning/` directory
- [ ] Bundle minimal plan.md, tasks.md, implement.md
- [ ] Update `pantheon init` with `--workflow` flag
- [ ] Implement `install_planning_framework()`
- [ ] Implement `create_base_constitution()`
- [ ] Implement `install_pantheon_commands()`

**Effort**: 8-12 hours

### Phase 2: /pantheon:init Command (Week 1)
- [ ] Create `src/pantheon/commands/init.md`
- [ ] Write detection logic (planning vs lightweight)
- [ ] Write enhancement logic for each file
- [ ] Write diff presentation logic
- [ ] Write approval wait logic
- [ ] Test with sample project

**Effort**: 12-16 hours

### Phase 3: Testing (Week 2)
- [ ] Test planning framework mode end-to-end
- [ ] Test lightweight mode end-to-end
- [ ] Test idempotency (run /pantheon:init twice)
- [ ] Test with different project types (Python, Node, Go)
- [ ] Manual QA

**Effort**: 8-12 hours

### Phase 4: Documentation (Week 2)
- [ ] Update README.md with two modes
- [ ] Create quick start guide
- [ ] Document /pantheon:init command
- [ ] Add troubleshooting section

**Effort**: 4-6 hours

**Total Effort**: 32-46 hours (~1-1.5 weeks)

---

## Advantages

### 1. Clean Separation
- ✅ CLI does deterministic work (copy files, configure)
- ✅ LLM does intelligent work (modify, enhance, adapt)
- ✅ Each phase does what it's best at

### 2. User Control
- ✅ Review every change before applying
- ✅ See exact diffs
- ✅ Approve or reject
- ✅ Transparent process

### 3. No External Dependencies
- ✅ Bundle planning commands in Pantheon
- ✅ Version together
- ✅ No Spec Kit package dependency
- ✅ Full control over updates

### 4. Flexibility
- ✅ Choose complexity level (planning vs lightweight)
- ✅ Same quality guarantee in both modes
- ✅ Easy to test different modes

### 5. Idempotent
- ✅ HTML markers detect existing enhancements
- ✅ Can re-run /pantheon:init safely
- ✅ Updates within markers only

### 6. Fast to Test
- ✅ Simple, focused implementation
- ✅ Can iterate quickly
- ✅ Easy to add features later

---

## Disadvantages

### 1. LLM Non-Determinism
- Running /pantheon:init multiple times may produce slight variations
- **Mitigation**: Specific instructions, markers, user reviews each change

### 2. Manual Approval Required
- User must approve changes (not fully automated)
- **Mitigation**: This is actually a feature (user control)

### 3. Bundled Commands Maintenance
- Need to maintain bundled plan/tasks/implement commands
- **Mitigation**: Simple files, rarely change, full control

---

## Success Metrics

### Technical
- [ ] `pantheon init --workflow spec-kit` creates all files correctly
- [ ] `/pantheon:init` successfully enhances all 5 files
- [ ] Markers allow idempotent re-runs
- [ ] Works in both modes (planning and lightweight)

### User Experience
- [ ] Clear diff presentation
- [ ] Easy approval process
- [ ] Workflow executes as documented
- [ ] Quality gates function correctly

### Quality
- [ ] 90% of test scenarios pass
- [ ] No file corruption or errors
- [ ] Clean, maintainable code

---

## Open Questions (Deferred for Later)

1. **Backup/Rollback**: Add later if needed
2. **More commands**: Can add /pantheon:status, /pantheon:validate later
3. **Constitution format**: Start with markdown, can optimize later
4. **Spec Kit branding**: Decide attribution/renaming as we finalize
5. **Version detection**: Handle updates to bundled commands (later)

---

## Next Steps

1. **Approve proposal**
2. **Phase 1**: Implement core CLI (1 week)
3. **Phase 2**: Implement /pantheon:init (1 week)
4. **Phase 3**: Test with real projects
5. **Phase 4**: Document and release

**Timeline**: 2-3 weeks from approval to release

---

## Recommendation

**Adopt Option 3 (Two-Phase Installation)** as the implementation strategy.

**Rationale**:
- ✅ Clean architecture (CLI + LLM separation)
- ✅ User control (review before apply)
- ✅ No external dependencies (bundle commands)
- ✅ Flexible (planning or lightweight)
- ✅ Fast to implement and test
- ✅ Easy to iterate and enhance

This approach solves all the challenges from Options 1 and 2 while remaining simple enough to ship quickly and iterate based on real usage.
