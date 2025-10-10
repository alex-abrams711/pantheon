# Proposal: Option 1 - Pure CLAUDE.md Integration

**Status**: Draft
**Created**: 2025-10-09
**Author**: Pantheon Team
**Version**: 1.0

---

## Executive Summary

Continue with the v0.4.0 approach of **zero Spec Kit integration**, relying entirely on comprehensive CLAUDE.md instructions and hook-based enforcement to orchestrate Pantheon's **complete implementation workflow** within Spec Kit commands. This ensures every task is fully implemented and verified through the DEV → QA → iterate cycle, not just quality-checked.

**Core Value**: Guaranteed task completion through independent validation, not just code quality metrics.

**Recommendation**: Adopt this as the primary approach, reinforced with PostToolUse and PreToolUse hooks for stronger enforcement.

---

## Problem Statement

### User Need
Users want Pantheon's **complete implementation workflow** to work seamlessly with GitHub's Spec Kit framework. This means:
- **Verified task completion**: Tasks are actually complete, not just marked complete
- **Independent validation**: QA agent catches gaps, incomplete work, and missing functionality
- **Iterative refinement**: DEV → QA → iterate cycle continues until work is truly done
- **No manual orchestration**: Workflow happens automatically when using Spec Kit commands

**The core problem**: Too many cases where tasks are marked complete but have clear gaps upon testing. Quality metrics alone don't ensure functional completeness.

### Current State
- Pantheon v0.4.0 removed all Spec Kit integration code (~2000+ lines)
- Users must manually invoke DEV agents: "Use the DEV agent to implement..."
- Spec Kit commands (`/implement`, `/plan`, `/tasks`) operate independently
- Orchestrator relies on CLAUDE.md instructions (soft enforcement)
- No guarantee that DEV → QA cycle actually happens

### Challenge
How can we ensure the **complete workflow** (not just quality checks) happens automatically with Spec Kit, without coupling Pantheon's codebase to Spec Kit's structure?

---

## Proposed Solution

### Approach
Enhance CLAUDE.md with comprehensive orchestration instructions that **automatically activate** when Spec Kit commands are detected.

### Core Principle
**The orchestrator is already reading CLAUDE.md**. We provide detailed, contextual instructions that trigger when Spec Kit workflows are in use.

### How It Works

```markdown
# CLAUDE.md (Enhanced Section)

## Spec Kit Integration (Automatic)

When the user runs Spec Kit commands (/implement, /plan, /tasks), automatically apply Pantheon's complete implementation workflow:

### When /plan is run:
1. Spec Kit generates plan.md with implementation approach
2. **Bootstrap quality configuration** (if .pantheon/quality-config.json doesn't exist):
   - Analyze project structure (package.json, requirements.txt, go.mod, etc.)
   - Detect test framework, linter, type checker
   - Discover or infer quality commands
   - Generate .pantheon/quality-config.json
   - OR offer to run /pantheon:contextualize
3. AFTER quality config exists, enhance plan.md with:
   - "Quality Standards" section (test/lint/type commands, thresholds)
   - "Tech Stack" section (languages, frameworks, tools)
   - "Verification Strategy" section (how QA will validate completion)
4. Present enhanced plan to user for approval

### When /tasks is run:
1. Spec Kit generates tasks.md with task list
2. AFTER tasks.md is created, enhance it with:
   - **Acceptance criteria as checkboxes** (what constitutes "done")
   - **Verification checklist** (tests, coverage, lint, type, functional testing)
   - Quality gates section (QA validated, User validated checkboxes)
   - Parallel execution markers [P] for independent tasks
3. Update tasks.md with enhancements

### When /implement is run:
1. Spec Kit loads spec.md, plan.md, tasks.md
2. Apply Pantheon **COMPLETE IMPLEMENTATION WORKFLOW**:
   - Analyze task dependencies from tasks.md
   - Group parallelizable tasks (max 3 agents)
   - For each task batch:
     a. Prepare DEV agent context packages (with acceptance criteria)
     b. Invoke DEV agents (parallel or sequential)
     c. Wait for all DEV completions
     d. **MANDATORY: Invoke QA agent for independent validation**
     e. QA verifies **functional completion** (not just quality metrics)
     f. If QA FAIL: prepare rework context with specific gaps, re-invoke DEV
     g. Iterate DEV → QA until PASS (max 3 cycles)
     h. If QA PASS: present phase completion report to user
     i. Wait for user approval ("yes")
     j. Create git commits with quality metrics
   - Continue until all tasks complete
3. Present final completion report

**KEY PRINCIPLE**: The DEV → QA → iterate cycle ensures tasks are ACTUALLY complete,
not just marked complete. QA validates functional requirements, not just code quality.
```

---

## Implementation Details

### Phase 1: Hook-Based Enforcement (Week 1)

**Purpose**: Strengthen LLM instruction-following with deterministic hooks that guide and validate workflow execution.

**Files to Create**:
- `.pantheon/hooks/post-slash-command.sh` - Inject workflow checklist after `/plan`, `/tasks`, `/implement`
- `.pantheon/hooks/pre-subagent-invocation.sh` - Validate DEV/QA context packages before invocation

**Hook Strategy**:
```
Layer 1: CLAUDE.md Instructions (baseline guidance)
    ↓
Layer 2: PostToolUse SlashCommand Hook (inject mandatory steps)
    ↓
Layer 3: PreToolUse Task Hook (validate & BLOCK incomplete context)
    ↓
Layer 4: Quality Gate Reports (validate results)
```

**See Appendix C** for complete hook implementations.

**Effort**: 8 hours (hook development + testing)

### Phase 2: CLAUDE.md Enhancement (Week 1)

**Files to Modify**:
- `CLAUDE.md`: Add "Spec Kit Integration (Automatic)" section

**Content Structure**:
```markdown
## Spec Kit Integration (Automatic)

### Detection
If any of the following are true, activate Spec Kit orchestration mode:
- User runs /plan, /tasks, or /implement
- Files exist: spec.md, plan.md, tasks.md in project root or specs/
- User mentions "Spec Kit" in their request

### /plan Enhancement
[Detailed instructions for orchestrator to enhance plan.md]

### /tasks Enhancement
[Detailed instructions for orchestrator to enhance tasks.md]

### /implement Orchestration
[Complete multi-agent workflow instructions]
```

**Effort**: 2-4 hours (mostly writing comprehensive instructions)

### Phase 3: Testing & Validation (Week 1-2)

**Manual Testing Checklist**:
- [ ] Run `/plan` in project with Spec Kit installed
  - [ ] Verify plan.md includes Quality Standards section
  - [ ] Verify quality commands pulled from quality-config.json
- [ ] Run `/tasks` with existing plan.md
  - [ ] Verify tasks.md includes subtask checkboxes
  - [ ] Verify quality gates section added
- [ ] Run `/implement` with existing tasks.md
  - [ ] Verify orchestrator invokes DEV agents
  - [ ] Verify QA validation occurs
  - [ ] Verify commits created after user approval

**Test Projects**:
- Python project with Spec Kit
- Node.js project with Spec Kit
- Go project with Spec Kit

### Phase 4: Documentation (Week 2)

**Update README.md**:
```markdown
## Spec Kit Integration

Pantheon automatically enhances Spec Kit workflows when detected:

1. Install both frameworks:
   ```bash
   uvx pantheon-agents init
   uvx spec-kit init
   ```

2. Generate quality config:
   ```
   /pantheon:contextualize
   ```

3. Use Spec Kit normally:
   ```
   /plan
   /tasks
   /implement
   ```

Pantheon automatically:
- Enhances plan.md with quality standards
- Enhances tasks.md with subtasks and gates
- Orchestrates multi-agent implementation
- Validates work with QA agent
- Creates quality-gated commits
```

**Create Integration Guide**:
- `docs/guides/spec-kit-integration.md`: Comprehensive workflow documentation
- Include examples, screenshots (if applicable), troubleshooting

---

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────┐
│  User runs /implement                               │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  Spec Kit Command                                   │
│  - Loads spec.md, plan.md, tasks.md                 │
│  - Presents to orchestrator                         │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  Orchestrator (reading CLAUDE.md)                   │
│  - Detects Spec Kit context                         │
│  - Activates Pantheon orchestration mode            │
│  - Applies multi-agent workflow                     │
└────────────────────┬────────────────────────────────┘
                     ↓
         ┌───────────┴───────────┐
         ↓                       ↓
    DEV Agents              QA Agent
         ↓                       ↓
    Implementation          Validation
         │                       │
         └───────────┬───────────┘
                     ↓
              Git Commits
```

### Data Flow

**No file modification needed**:
- Spec Kit creates/manages spec.md, plan.md, tasks.md
- Orchestrator reads CLAUDE.md for instructions
- Orchestrator reads quality-config.json for commands
- Orchestrator orchestrates workflow based on instructions

**Optional enhancement flow**:
- Orchestrator can enhance plan.md and tasks.md after Spec Kit creates them
- Enhancements are additive (append sections)
- Idempotent (running /plan twice doesn't duplicate sections)

---

## Advantages

### 1. Zero Coupling
- **No Spec Kit dependencies**: Pantheon doesn't import, parse, or know about Spec Kit
- **Version independence**: Works with any Spec Kit version
- **Framework agnostic**: Same approach works with ANY framework (or no framework)

### 2. Zero Maintenance
- **No integration code**: Nothing to break when Spec Kit updates
- **No version matrix**: Don't need to test against multiple Spec Kit versions
- **No rollback logic**: Nothing to roll back

### 3. Maximum Flexibility
- **Works everywhere**: Claude Code + CLAUDE.md works in any project
- **Easy customization**: Users can modify CLAUDE.md for their needs
- **Progressive enhancement**: Users get Pantheon benefits even without Spec Kit

### 4. Proven Approach
- **Already working**: v0.4.0 uses this successfully
- **LLM strength**: Modern LLMs excel at following complex instructions
- **Validated**: Pantheon's entire orchestration relies on CLAUDE.md

### 5. Simple Distribution
- **No integration step**: `pantheon init` copies agents and commands, done
- **Clear separation**: Pantheon and Spec Kit are independent tools
- **Easy troubleshooting**: Issues clearly belong to one tool or the other

---

## Disadvantages

### 1. Relies on LLM Instruction-Following (Mitigated with Hooks)
- **Concern**: Orchestrator might not follow instructions perfectly
- **Mitigation**:
  - **PostToolUse hooks inject mandatory checklists** at exact right moment
  - **PreToolUse hooks BLOCK incomplete context packages** (deterministic)
  - Write extremely clear, specific instructions in CLAUDE.md
  - Use numbered steps, examples, and decision trees
  - Defense-in-depth: multiple validation layers
  - **Result**: Much stronger enforcement than CLAUDE.md alone

### 2. No "Automated" Feeling
- **Concern**: Doesn't feel like an "integration"
- **Mitigation**:
  - Frame as "automatic orchestration"
  - User experience is seamless (just run /implement)
  - Marketing: "Pantheon automatically enhances Spec Kit"

### 3. Harder to Debug Integration Issues
- **Concern**: User can't see "what Pantheon added"
- **Mitigation**:
  - Clear logging from orchestrator
  - Document expected behavior in guides
  - Orchestrator can explain its actions when asked

### 4. Quality Config Bootstrapping
- **Concern**: Early-stage projects may not have quality-config.json yet
- **Mitigation**:
  - Bootstrap during `/plan` if config missing
  - Orchestrator can run inline quality discovery
  - Offer to run `/pantheon:contextualize` if user prefers
  - Make config optional with sensible defaults

---

## Migration Path

### From v0.4.0 (Current)
**Effort**: Minimal

1. Enhance CLAUDE.md with Spec Kit orchestration section
2. Update README.md with integration documentation
3. Create integration guide
4. Test with sample projects

**User Impact**: None (additive enhancement)

### From v0.3.0 (Old Integration)
**Effort**: None needed (users already on v0.4.0)

Users who want Spec Kit integration:
1. Install Spec Kit separately: `uvx spec-kit init`
2. Use commands normally: `/plan`, `/tasks`, `/implement`
3. Pantheon orchestration happens automatically via CLAUDE.md

---

## Success Metrics

### Technical Metrics
- [ ] CLAUDE.md instructions <2000 lines (maintainable)
- [ ] Zero Spec Kit-specific code in Pantheon codebase
- [ ] Works with Spec Kit v0.0.50, v0.0.55, v0.1.0 (no changes needed)

### User Experience Metrics
- [ ] Users can run `/implement` and see Pantheon orchestration
- [ ] Quality gates activate automatically
- [ ] No manual "integration" step required
- [ ] Clear error messages if quality-config.json missing

### Quality Metrics
- [ ] 90% of test scenarios pass with sample projects
- [ ] User feedback indicates seamless experience
- [ ] No GitHub issues about "integration breaking"

---

## Open Questions

1. **Should orchestrator enhance plan.md/tasks.md or leave them untouched?**
   - Option A: Read-only, orchestrate without modification
   - Option B: Enhance files after Spec Kit creates them
   - Recommendation: Option A (less intrusive), Option B if user feedback demands it

2. **How aggressive should Spec Kit detection be?**
   - Activate on file presence alone?
   - Require explicit user trigger?
   - Recommendation: Activate when files present + user runs Spec Kit command

3. **Should we provide a "disable Spec Kit mode" flag in CLAUDE.md?**
   - For users who have spec.md but don't want orchestration
   - Recommendation: Yes, add `# Pantheon Settings: spec_kit_integration: false`

---

## Alternatives Considered

### Alternative 1: Python Integration (v0.3.0 approach)
**Rejected**: Maintenance burden, tight coupling, removed in v0.4.0

### Alternative 2: Wrapper Commands
**See**: `option-2-wrapper-commands.md`

### Alternative 3: Slash Command Integration
**Deferred**: Complexity, brittleness, non-deterministic

---

## Recommendation

**Adopt Option 1 (Pure CLAUDE.md)** as the primary approach for Spec Kit integration.

**Rationale**:
- Aligns with v0.4.0 architectural direction (decoupling)
- Minimal implementation effort (mostly documentation)
- Zero maintenance burden
- Maximum flexibility
- Proven approach (already working)

**Next Steps**:
1. Approve proposal
2. Enhance CLAUDE.md with Spec Kit orchestration section (2-4 hours)
3. Test with sample projects (4-8 hours)
4. Update documentation (2-4 hours)
5. Release as part of v0.4.1 or v0.5.0

**Timeline**: 1-2 weeks from approval to release

---

## Appendix A: Sample CLAUDE.md Enhancement

```markdown
## Spec Kit Integration (Automatic)

### Detection
Pantheon automatically activates Spec Kit orchestration when:
- User runs `/implement`, `/plan`, or `/tasks` commands
- Files exist: spec.md, plan.md, or tasks.md in project root or specs/

### Orchestration Mode

#### When /plan is run:

**Context Setup**:
- spec.md exists (Spec Kit creates this)

**Pantheon Workflow**:

1. **Bootstrap Quality Configuration** (if .pantheon/quality-config.json doesn't exist):
   - Check for package.json, requirements.txt, go.mod, Cargo.toml, etc.
   - Detect test framework (pytest, jest, go test, cargo test, etc.)
   - Detect linter (ruff, eslint, golangci-lint, clippy, etc.)
   - Detect type checker (mypy, tsc, go types built-in, etc.)
   - Generate .pantheon/quality-config.json with discovered commands
   - OR prompt user: "Run /pantheon:contextualize for more accurate discovery?"

2. **Enhance plan.md**:
   Add these sections if not already present:

   ```markdown
   ## Quality Standards
   **Test Command**: [from quality-config.json or discovered]
   **Lint Command**: [from quality-config.json or discovered]
   **Type Check**: [from quality-config.json or discovered]
   **Coverage Threshold**: 80% branches (default, adjustable)

   ## Tech Stack
   **Language**: [detected from project]
   **Framework**: [detected from dependencies]
   **Testing**: [detected test framework]
   **Build Tool**: [detected build tool]

   ## Verification Strategy
   - DEV agents implement with TDD
   - QA agent validates functional completion
   - Independent verification of acceptance criteria
   - Iterate until all criteria met
   ```

3. **Present enhanced plan** to user for approval

#### When /tasks is run:

**Prerequisites**: plan.md exists with Quality Standards section

**Pantheon Workflow**:

1. **Parse plan.md** for acceptance criteria per task
2. **Enhance each task** in tasks.md:
   ```markdown
   ### T001: [Task name]
   **Files**: [files to modify]
   **Dependencies**: [task dependencies]
   **Acceptance Criteria**:
   - [ ] [Criterion 1 - what makes this task complete]
   - [ ] [Criterion 2]
   - [ ] [Criterion 3]
   **Verification**:
   - [ ] Tests pass
   - [ ] Coverage ≥ threshold
   - [ ] Linting passes
   - [ ] Type checking passes
   - [ ] QA validates functional completion
   ```
3. **Add Quality Gates** section at end:
   ```markdown
   ## Quality Gates
   - [ ] All tasks complete
   - [ ] QA validated
   - [ ] User validated
   ```
4. **Mark parallel tasks** with [P] based on dependency analysis

#### When /implement is run:

**Context Loading** (Spec Kit handles this):
- spec.md: Feature specification
- plan.md: Implementation approach, quality standards
- tasks.md: Task breakdown with dependencies

**Pantheon Orchestration** (You handle this):

1. **Load Context**:
   - Read quality-config.json for test/lint/type commands
   - Parse tasks.md for task list and dependencies
   - Parse plan.md for quality thresholds

2. **Analyze Dependencies**:
   - Identify tasks with no dependencies (can run in parallel)
   - Identify tasks with dependencies (must run sequentially)
   - Group tasks into batches (max 3 parallel)

3. **Execute Task Batches**:
   For each batch:

   a. **Prepare DEV Context Packages**:
      ```markdown
      # Task Context: [Task ID]

      ## Task Details
      **ID**: [from tasks.md]
      **Description**: [from tasks.md]
      **Files**: [from tasks.md]

      ## Acceptance Criteria
      [Subtasks from tasks.md as checkboxes]

      ## Quality Standards
      **Test Command**: [from quality-config.json]
      **Lint Command**: [from quality-config.json]
      **Type Command**: [from quality-config.json]
      **Coverage Threshold**: [from quality-config.json]

      ## Tech Stack
      [From plan.md or quality-config.json project_type]
      ```

   b. **Invoke DEV Agents** (parallel if independent):
      - Use Task tool with DEV agent
      - Provide complete context package
      - Wait for all agents to complete

   c. **Invoke QA Agent**:
      ```markdown
      # QA Validation Context

      ## Tasks to Validate
      [List all tasks from this batch]

      ## Quality Standards
      [From quality-config.json]

      ## Definition of Done
      - [ ] All tests pass
      - [ ] Coverage ≥ threshold
      - [ ] No linting errors
      - [ ] No type errors
      ```

   d. **Process QA Results**:
      - If PASS: Continue to step e
      - If FAIL: Re-invoke DEV with rework context, return to step c (max 3 cycles)

   e. **Phase Gate Checkpoint**:
      - Mark "QA validated" in tasks.md
      - Generate phase completion report
      - Present to user: "Type 'yes' to proceed"
      - Wait for user approval

   f. **Create Commits** (after user approval):
      - Mark "User validated" in tasks.md
      - Create atomic commits for batch
      - Include quality metrics in commit message

4. **Continue to Next Batch**: Repeat step 3 until all tasks complete

5. **Final Report**: Present completion summary with quality metrics
```

---

## Appendix B: Example User Journey

**Setup** (one-time):
```bash
# Install Pantheon
uvx pantheon-agents init

# Install Spec Kit
uvx spec-kit init

# Discover quality commands
# In Claude Code:
/pantheon:contextualize
```

**Development Workflow**:
```
User: /plan
Spec Kit: Creates plan.md with implementation approach
Orchestrator: (reads CLAUDE.md, sees Spec Kit mode active)
Orchestrator: Enhances plan.md with quality standards section
Orchestrator: Presents enhanced plan to user

User: /tasks
Spec Kit: Creates tasks.md with task breakdown
Orchestrator: Enhances tasks.md with subtasks and quality gates
Orchestrator: Presents enhanced tasks to user

User: /implement
Spec Kit: Loads spec.md, plan.md, tasks.md
Orchestrator: (reads CLAUDE.md, activates orchestration mode)
Orchestrator: Analyzes 5 tasks, identifies 2 parallel batches
Orchestrator: "I'll implement T001-T003 in parallel, then T004-T005"
Orchestrator: Invokes 3 DEV agents simultaneously
[DEV agents work...]
Orchestrator: "All DEV agents complete, invoking QA agent"
[QA agent validates...]
QA Agent: "STATUS: PASS - All quality checks passed"
Orchestrator: Presents phase completion report
Orchestrator: "Type 'yes' to proceed and create commits"
User: yes
Orchestrator: Creates commits, continues to next batch
```

**User Experience**: Seamless, automated, quality-focused

---

## Appendix C: Hook Implementations

### Hook 1: PostToolUse SlashCommand Hook

**File**: `.pantheon/hooks/post-slash-command.sh`

**Purpose**: Inject mandatory workflow checklists immediately after `/plan`, `/tasks`, or `/implement` runs.

```bash
#!/bin/bash
# Post-slash-command hook: Inject complete workflow steps after Spec Kit commands

TOOL_NAME="$1"
TOOL_ARGS="$2"

# Only trigger for SlashCommand tool
if [ "$TOOL_NAME" != "SlashCommand" ]; then
    exit 0
fi

# Extract command from args
COMMAND=$(echo "$TOOL_ARGS" | jq -r '.command // empty')

case "$COMMAND" in
    "/plan")
        cat << 'WORKFLOW'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 PANTHEON: /plan COMPLETE WORKFLOW ACTIVATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MANDATORY NEXT STEPS (execute in order):

STEP 1: Quality Configuration Bootstrap
□ Check if .pantheon/quality-config.json exists
  → If missing:
    □ Analyze project structure (package.json, requirements.txt, go.mod, etc.)
    □ Detect test framework (pytest, jest, go test, vitest, etc.)
    □ Detect linter (ruff, eslint, golangci-lint, biome, etc.)
    □ Detect type checker (mypy, tsc, built-in types, etc.)
    □ Generate .pantheon/quality-config.json
    □ OR prompt user: "Run /pantheon:contextualize for better discovery?"

STEP 2: Enhance plan.md
□ Add "Quality Standards" section:
  - Test command
  - Lint command
  - Type check command
  - Coverage threshold
□ Add "Tech Stack" section:
  - Language(s)
  - Framework(s)
  - Testing framework
  - Build tool
□ Add "Verification Strategy" section:
  - How DEV agents will implement
  - How QA agent will validate COMPLETE functionality
  - Criteria for task completion (not just passing tests)

STEP 3: Present Enhanced Plan
□ Show user the complete plan with all enhancements
□ Confirm ready for /tasks

**KEY PRINCIPLE**: This ensures we have quality standards AND verification
strategy BEFORE tasks are defined. This is about ensuring complete implementation,
not just code quality metrics.

DO NOT proceed to /tasks until these steps are complete.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WORKFLOW
        exit 0
        ;;
        
    "/tasks")
        cat << 'WORKFLOW'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 PANTHEON: /tasks COMPLETE WORKFLOW ACTIVATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MANDATORY NEXT STEPS (execute in order):

STEP 1: Parse plan.md
□ Extract acceptance criteria for each task
□ Extract quality standards
□ Extract verification strategy

STEP 2: Enhance each task in tasks.md
For EVERY task, add:

□ **Acceptance Criteria** section (as checkboxes):
  - [ ] Criterion 1 (WHAT makes this task functionally complete)
  - [ ] Criterion 2
  - [ ] Criterion 3
  (These are FUNCTIONAL requirements, not just "tests pass")

□ **Verification** section (as checkboxes):
  - [ ] Tests pass (all tests for this task)
  - [ ] Coverage ≥ threshold
  - [ ] Linting passes (no new errors)
  - [ ] Type checking passes (no new errors)
  - [ ] QA validates functional completion

STEP 3: Analyze Dependencies & Mark Parallel Tasks
□ Review task dependencies
□ Mark tasks with no dependencies as [P] (parallel-safe)
□ Mark tasks with dependencies as [ ] (sequential)

STEP 4: Add Quality Gates Section
□ Add at end of tasks.md:
  ```
  ## Quality Gates
  - [ ] All tasks complete
  - [ ] QA validated
  - [ ] User validated
  ```

STEP 5: Present Enhanced Tasks
□ Show user the complete tasks with all enhancements
□ Explain parallel execution plan
□ Confirm ready for /implement

**KEY PRINCIPLE**: Acceptance criteria define FUNCTIONAL completeness.
QA agent will verify these criteria are met, not just that tests pass.

DO NOT proceed to /implement until these steps are complete.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WORKFLOW
        exit 0
        ;;
        
    "/implement")
        cat << 'WORKFLOW'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 PANTHEON: /implement COMPLETE ORCHESTRATION ACTIVATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MANDATORY WORKFLOW - Execute in strict order:

═══════════════════════════════════════════════
PHASE 1: CONTEXT LOADING
═══════════════════════════════════════════════
1. □ Read spec.md (feature specification)
2. □ Read plan.md (approach, quality standards, verification strategy)
3. □ Read tasks.md (tasks, acceptance criteria, dependencies)
4. □ Read .pantheon/quality-config.json (test/lint/type commands)
5. □ Verify all files exist (error if missing)

═══════════════════════════════════════════════
PHASE 2: DEPENDENCY ANALYSIS  
═══════════════════════════════════════════════
6. □ Parse tasks.md for task dependencies
7. □ Identify parallel-safe tasks (marked [P] or no dependencies)
8. □ Create execution plan:
     - Group into batches
     - Max 3 parallel DEV agents per batch
     - Sequential batches based on dependencies
9. □ Present execution plan to user
10. □ WAIT for user approval before proceeding

═══════════════════════════════════════════════
PHASE 3: BATCH EXECUTION (repeat for each batch)
═══════════════════════════════════════════════

For each batch of tasks:

11. □ Prepare complete DEV agent context packages
      → PreToolUse Task hook will validate completeness
      → MUST include: Task Details, Acceptance Criteria, Quality Standards, Tech Stack

12. □ Invoke DEV agents (parallel if independent)
      → All parallel invocations in SINGLE message
      → WAIT for ALL agents to complete before continuing

13. □ Handle DEV completions:
      → If any BLOCKED: address issue, re-invoke (max 3 attempts)
      → If all SUCCESS: mark tasks complete, continue to QA

14. □ **MANDATORY: Invoke QA agent for independent validation**
      → QA validates FUNCTIONAL COMPLETION (not just quality metrics)
      → QA checks acceptance criteria are MET
      → QA performs manual testing if needed
      → QA reports PASS or FAIL with specific issues

15. □ Process QA results:
      IF QA PASS:
        → Mark "QA validated" in tasks.md
        → Continue to Phase Gate Checkpoint (step 16)
      
      IF QA FAIL:
        → Parse specific issues and gaps from QA report
        → Prepare DEV rework context packages with QA findings
        → Re-invoke DEV agents with rework context
        → Re-invoke QA agent
        → Iterate max 3 cycles
        → If still FAIL after 3 cycles: stop, ask user for guidance

16. □ **Phase Gate Checkpoint** (after QA PASS):
      □ Generate phase completion report:
        - Completed tasks (IDs, descriptions)
        - Quality metrics (tests, coverage, lint, type)
        - Deliverables (what was functionally implemented)
        - Ready for: [Next phase or final review]
      □ Present report to user
      □ Prompt: "Type 'yes' to create commits and proceed"
      □ WAIT for user to type "yes" (do NOT proceed otherwise)

17. □ Create Git Commits (ONLY after user types "yes"):
      □ Mark "User validated" in tasks.md
      □ Create atomic commits for batch
      □ Include quality metrics in commit message
      □ Include functional deliverables summary

═══════════════════════════════════════════════
PHASE 4: CONTINUATION
═══════════════════════════════════════════════
18. □ If more batches remain: return to PHASE 3 for next batch
19. □ If all batches complete: generate final completion report

═══════════════════════════════════════════════
CRITICAL PRINCIPLES
═══════════════════════════════════════════════
✓ DEV → QA → iterate cycle is MANDATORY (not optional)
✓ QA validates FUNCTIONAL COMPLETION (tasks actually work, not just tests pass)
✓ User approval required BEFORE commits
✓ Complete acceptance criteria verification, not just quality metrics

YOU MUST COMPLETE ALL PHASES IN ORDER.
Quality gate hooks will validate your work at key checkpoints.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WORKFLOW
        exit 0
        ;;
esac

exit 0
```

**Installation**:
```json
{
  "hooks": {
    "PostToolUse SlashCommand(*)": [
      ".pantheon/hooks/post-slash-command.sh"
    ]
  }
}
```

---

### Hook 2: PreToolUse Task Hook

**File**: `.pantheon/hooks/pre-subagent-invocation.sh`

**Purpose**: Validate DEV/QA context packages BEFORE invocation. Block incomplete packages (deterministic enforcement).

```bash
#!/bin/bash
# Pre-subagent invocation hook: Validate context packages

TOOL_NAME="$1"
TOOL_ARGS="$2"

# Only trigger for Task tool (subagent invocations)
if [ "$TOOL_NAME" != "Task" ]; then
    exit 0
fi

SUBAGENT_TYPE=$(echo "$TOOL_ARGS" | jq -r '.subagent_type // empty')
PROMPT=$(echo "$TOOL_ARGS" | jq -r '.prompt // empty')

# Validate DEV agent context package
if [ "$SUBAGENT_TYPE" = "general-purpose" ] && echo "$PROMPT" | grep -qi "DEV agent"; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔍 Validating DEV Agent Context Package..."
    
    # Check required sections
    MISSING=""
    
    if ! echo "$PROMPT" | grep -q "## Task Details"; then
        MISSING="${MISSING}\n  - ## Task Details (ID, description, files)"
    fi
    
    if ! echo "$PROMPT" | grep -q "## Acceptance Criteria"; then
        MISSING="${MISSING}\n  - ## Acceptance Criteria (functional requirements as checkboxes)"
    fi
    
    if ! echo "$PROMPT" | grep -q "## Quality Standards"; then
        MISSING="${MISSING}\n  - ## Quality Standards (test/lint/type commands, thresholds)"
    fi
    
    if ! echo "$PROMPT" | grep -q "## Tech Stack"; then
        MISSING="${MISSING}\n  - ## Tech Stack (language, framework, tools)"
    fi
    
    if [ -n "$MISSING" ]; then
        echo "❌ BLOCKED: Incomplete DEV agent context package"
        echo ""
        echo "Missing required sections:${MISSING}"
        echo ""
        echo "A complete context package ensures the DEV agent has ALL information"
        echo "needed to implement the task AND verify it meets acceptance criteria."
        echo ""
        echo "Re-prepare the context package with all required sections."
        echo "Refer to CLAUDE.md Spec Kit Integration section for format."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        exit 2  # Block the invocation
    fi
    
    echo "✅ DEV context package validation passed"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# Validate QA agent context package
if [ "$SUBAGENT_TYPE" = "general-purpose" ] && echo "$PROMPT" | grep -qi "QA agent"; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔍 Validating QA Agent Context Package..."
    
    MISSING=""
    
    if ! echo "$PROMPT" | grep -q "## Tasks to Validate"; then
        MISSING="${MISSING}\n  - ## Tasks to Validate (task IDs, files, acceptance criteria)"
    fi
    
    if ! echo "$PROMPT" | grep -q "## Quality Standards"; then
        MISSING="${MISSING}\n  - ## Quality Standards (commands, thresholds)"
    fi
    
    if ! echo "$PROMPT" | grep -q "## Definition of Done"; then
        MISSING="${MISSING}\n  - ## Definition of Done (completion criteria)"
    fi
    
    if [ -n "$MISSING" ]; then
        echo "❌ BLOCKED: Incomplete QA agent context package"
        echo ""
        echo "Missing required sections:${MISSING}"
        echo ""
        echo "A complete QA context package ensures independent validation of"
        echo "FUNCTIONAL COMPLETION, not just quality metrics."
        echo ""
        echo "The QA agent needs:"
        echo "  - Tasks to Validate: What was implemented and what to verify"
        echo "  - Quality Standards: How to run quality checks"
        echo "  - Definition of Done: Criteria for COMPLETE implementation"
        echo ""
        echo "Re-prepare the context package with all required sections."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        exit 2  # Block the invocation
    fi
    
    echo "✅ QA context package validation passed"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

exit 0
```

**Installation**:
```json
{
  "hooks": {
    "PreToolUse Task(*)": [
      ".pantheon/hooks/pre-subagent-invocation.sh"
    ]
  }
}
```

---

### Combined Hook Installation

**File**: `.claude/settings.json` (updated)

```json
{
  "hooks": {
    "PostToolUse SlashCommand(*)": [
      ".pantheon/hooks/post-slash-command.sh"
    ],
    "PreToolUse Task(*)": [
      ".pantheon/hooks/pre-subagent-invocation.sh"
    ],
    "PostToolUse Write(*) | Edit(*)": [
      ".pantheon/hooks/quality-gate.sh"
    ],
    "PreToolUse Write(*) | Edit(*)": [
      ".pantheon/hooks/orchestrator-code-gate.sh"
    ]
  }
}
```

---

### What These Hooks Achieve

**PostToolUse SlashCommand Hook**:
- ✅ Appears as system message immediately after `/implement` runs
- ✅ Provides numbered checklist (easier for LLM to follow)
- ✅ Explicit "DO NOT proceed until..." warnings
- ✅ Contextual guidance at exact right moment
- ✅ Non-blocking (informational, high priority)

**PreToolUse Task Hook**:
- ✅ **Blocks invocation** if context package incomplete (enforced)
- ✅ Fast feedback with specific errors
- ✅ Ensures DEV/QA agents always have complete context
- ✅ Prevents common failure mode (incomplete context → poor results)
- ✅ Same enforcement approach as orchestrator-code-gate.sh

**Combined Effect**:
- **Much stronger than CLAUDE.md alone**: Hooks provide deterministic enforcement at critical points
- **Defense in depth**: Multiple layers catch different failure modes
- **Still flexible**: PostToolUse hooks guide, PreToolUse hooks enforce minimum standards
- **User-visible**: Clear error messages explain what's wrong and how to fix it

**Reliability Improvement**: Estimated 70-80% reduction in workflow deviations compared to CLAUDE.md alone.
