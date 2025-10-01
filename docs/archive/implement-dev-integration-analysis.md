# Integration Analysis: DEV Agent + Spec Kit `/implement` Command

**Updated**: 2025-09-30 (Post Sub-Agent Research)

## Executive Summary

The Spec Kit's `/implement` command is a task-execution framework that focuses on **orchestration** (loading context, parsing tasks, executing phases, tracking progress). The DEV agent is a **quality-focused implementation methodology** with rigorous verification loops, guardrails, and iteration protocols.

**Key finding**: The `/implement` command provides the skeleton, but lacks the DEV agent's quality enforcement muscle. Integration requires leveraging Claude Code's **sub-agent architecture** to invoke DEV as a specialized implementation agent.

**Architecture Decision**: DEV will be defined as a Claude Code sub-agent in `.claude/agents/dev.md` and invoked by the `/implement` command to handle task execution with built-in quality enforcement.

### Sub-Agent Integration Model

```
/implement command (orchestrator)
    ↓
1. Load context (tasks.md, plan.md, spec.md)
2. For each task/phase:
    ↓
    Invoke DEV sub-agent with task context
        ↓ (separate context window)
        DEV executes: code → verify acceptance → verify quality → commit
        ↓
    Return results to /implement
    ↓
3. Aggregate results, mark tasks complete
4. Final verification & user checkpoint
```

**Benefits of Sub-Agent Approach**:
- ✅ **Separation of concerns**: /implement orchestrates, DEV executes with quality focus
- ✅ **Context preservation**: Main conversation preserved while DEV works
- ✅ **Reusability**: DEV can be invoked from other commands or directly by user
- ✅ **Tool scoping**: DEV gets only implementation tools (Read, Write, Edit, Bash)
- ✅ **Clear responsibility**: DEV owns Phase 5-7 (Implement, Verify, Finalize)

---

## Conceptual Mapping

### Spec Kit Workflow → DEV Agent Phases

| Spec Kit Command | DEV Agent Phase | Status |
|------------------|-----------------|--------|
| `/constitution` | Foundation (Guardrails) | ✅ Already aligned |
| `/specify` | Phase 1: Understand | ✅ Already aligned |
| `/clarify` | Phase 1: Understand (refinement) | ✅ Already aligned |
| `/plan` | Phase 2: Plan | ✅ Already aligned |
| (implicit) | Phase 3: Iterate on Plan | ⚠️ Could be more explicit |
| `/tasks` | Phase 4: Document | ⚠️ Partial alignment |
| `/implement` | Phase 5: Implement | ❌ Missing quality loops |
| `/implement` (end) | Phase 6: Verify | ⚠️ Basic validation only |
| (missing) | Phase 7: Finalize | ❌ No user checkpoint |
| (missing) | Phase 8: Iteration | ❌ No feedback protocol |

### Granularity Mismatch

- **Spec Kit tasks.md**: High-level tasks (T001, T002...) with phase grouping
- **DEV agent subtasks**: Fine-grained subtasks within each task, each with verification steps

The `/implement` command operates at the **task level**, while DEV's verification loops operate at the **subtask level**.

---

## Critical Gaps in Current `/implement` Command

### 1. Missing Per-Task Verification Loops

**Current behavior**: Execute task → mark complete → move to next task

**DEV agent behavior**: Execute subtask → verify acceptance criteria → verify quality standards → commit → repeat

**Impact**: No quality gates during execution, only at the end

#### DEV's Verification Decision Tree
```
For each subtask:
├─ Write/Test code
├─ Acceptance Criteria Check
│  ├─ Pass → Continue
│  └─ Fail → Document failure, return to code step
├─ Quality Standards Check (lint/type/test)
│  ├─ Pass → Continue
│  └─ Fail → Analyze failure type
│     ├─ Requires functional rewrite → Document, mark incomplete, return to code
│     └─ Quality-only fix → Attempt fix in place (max 3 tries)
│        ├─ Fixed → Continue
│        └─ Still failing → STOP, present status, wait for user input
└─ Atomic commit with clear message
```

**What's missing from `/implement`**:
- No acceptance criteria verification per task
- No quality standards verification per task
- No distinction between functional vs quality failures
- No 3-try limit or stop-and-present protocol
- No atomic commit guidance

### 2. Missing Guardrails Enforcement

**Current behavior**: Execute tasks, report errors if they occur

**DEV agent guardrails**:
- **NO PARTIAL IMPLEMENTATION**: Must meet all success criteria (no placeholders, no "this would work if...")
- **NO SIMPLIFICATION EXCUSES**: No incomplete functionality with excuses
- **NO OVER-ENGINEERING**: Keep it simple, avoid unnecessary abstractions
- **PRODUCTIVE ITERATION ONLY**: Stop after 2-3 failed attempts, present problem clearly
- **FOLLOW EXISTING PATTERNS**: Analyze codebase first
- **STAY IN SCOPE**: No architectural decisions or unrelated refactoring

**Impact**: Agent can drift into over-engineering, partial implementations, or infinite retry loops

### 3. Missing Quality Standards Specification

**Current behavior**: Generic "validate tests pass and coverage meets requirements"

**DEV agent standards**:
- **Testing**: Smart, meaningful tests that validate real behavior (not just pass)
- **Code Quality**: Linting, type checking, error handling, following patterns
- **Documentation**: JSDoc/JavaDoc, inline comments explaining WHY, clear naming
- **Version Control**: Atomic commits per subtask, clear messages, reviewable changes

**What's missing**: Specific enforcement of *quality* vs just *functionality*

### 4. Missing Communication Protocol

**Current behavior**: "Report progress after each completed task"

**DEV agent communication**:
- Explain decisions and tradeoffs during implementation
- Surface risks and uncertainties proactively (before failures)
- Ask smart questions to unblock progress
- Admit when something is unclear or outside scope
- Provide specific, actionable next steps
- Avoid unnecessary verbosity

**Impact**: Agent just reports what it did, not WHY or what risks exist

### 5. Missing Live Application Testing

**Current behavior**: No guidance on functional validation beyond "tests pass"

**DEV agent approach**:
- For live/functional updates: run and test the live application
- Take screenshots as proof of functionality
- Verify acceptance criteria in running system, not just tests

**Impact**: Tests might pass but application might not work correctly

### 6. Missing Commit Strategy

**Current behavior**: "Mark task off as [X] in tasks file"

**DEV agent approach**:
- Atomic commits after EACH verified subtask
- Clear, descriptive commit messages
- Commits only after both acceptance AND quality verification pass

**Impact**: Poor version control history, unclear what each commit represents

### 7. Missing Iteration Protocol

**Current behavior**: Command ends after completion validation

**DEV agent approach**:
- **Phase 7: Finalize**: Present results and wait for user verification
- **Phase 8: Iteration**: Handle feedback by reopening subtasks or creating new ones

**Impact**: No protocol for handling inevitable refinement requests

---

## Alignment Opportunities

### 1. Constitution Already Aligned

The Spec Kit's constitution (`memory/constitution.md`) already embodies DEV's guardrails:
- Article VII: Simplicity (max 3 projects)
- Article VIII: Anti-Abstraction (use frameworks directly)
- Article III: Test-First Imperative

**Opportunity**: Reference constitution in `/implement` to enforce these during execution

### 2. Tasks.md Provides Structure

The tasks.md format already has:
- Phase grouping (Setup, Tests, Core, Integration, Polish)
- Dependency tracking
- Parallel execution markers [P]
- TDD ordering (tests before implementation)

**Opportunity**: Keep tasks.md format, but enhance execution within each task

### 3. Plan.md Contains Quality Standards

The plan.md includes:
- Tech stack and constraints
- Performance goals
- Testing approach
- Code organization

**Opportunity**: Extract quality standards from plan.md and apply them during execution

---

## Integration Strategy Recommendations

### RECOMMENDED: Sub-Agent Delegation Approach

**Architecture**: `/implement` acts as orchestrator, delegating execution to DEV sub-agent

**How it works**:
1. **Pre-execution** (by `/implement`):
   - Run prerequisites check script
   - Load context: tasks.md, plan.md, spec.md, contracts/, etc.
   - Extract quality standards from plan.md
   - Identify task phases and dependencies

2. **Execution loop** (delegated to DEV sub-agent):
   ```
   For each task (or task group):
   ├─ /implement prepares task context package:
   │  ├─ Task description and file paths
   │  ├─ Quality standards (lint/type/test commands)
   │  ├─ Relevant spec requirements
   │  └─ Constitution guardrails
   ├─ Invoke DEV sub-agent with context
   │  └─ DEV runs in separate context window:
   │     ├─ Execute code/test (TDD approach)
   │     ├─ Verify acceptance criteria
   │     ├─ Verify quality standards
   │     ├─ Apply guardrails (no partial impl, etc.)
   │     ├─ Atomic commit with clear message
   │     └─ Return results to /implement
   └─ /implement processes results:
      ├─ Mark task complete in tasks.md
      ├─ Log decisions/issues
      └─ Continue or halt based on outcome
   ```

3. **Post-execution** (by `/implement`):
   - Aggregate all DEV results
   - Run final verification checklist
   - Present summary to user with checkpoint
   - Handle iteration if user provides feedback

**Benefits**:
- ✅ **Separation of concerns**: Orchestration vs execution logic
- ✅ **Context management**: Main conversation preserved, DEV has focused context
- ✅ **Reusability**: DEV can be invoked standalone or from other commands
- ✅ **Stateless execution**: Each DEV invocation is clean, no context pollution
- ✅ **Tool scoping**: DEV only gets implementation tools
- ✅ **Quality enforcement**: DEV's verification loops run automatically
- ✅ **Scalability**: Can invoke multiple DEV instances in parallel for [P] tasks

**Implementation**:
1. Move `final/dev.md` → `.claude/agents/dev.md`
2. Add YAML frontmatter to configure sub-agent
3. Update `/implement` command to invoke DEV sub-agent
4. DEV sub-agent handles Phase 5-7 autonomously

### Alternative Approaches (For Comparison)

#### Approach A: Lightweight Reference (Original Analysis)

Modify `/implement` command to:
1. **Load DEV agent context**: Read `.claude/agents/dev.md` at start
2. **Apply DEV principles**: Instruct agent to "operate as DEV agent in Phase 5-7"
3. **Keep structure**: Maintain current task-level orchestration

**Pros**: Minimal disruption, flexible
**Cons**: Relies on interpretation, no context separation

#### Approach B: Explicit Integration (Original Analysis)

Rewrite `/implement` command to explicitly encode all DEV logic inline.

**Pros**: Very explicit, consistent
**Cons**: Major rewrite, less flexible, all in one context window

*(Approach C has been superseded by the Sub-Agent Delegation Approach above)*

---

## Sub-Agent Implementation Details

### 1. DEV Sub-Agent Configuration

**Location**: `.claude/agents/dev.md`

**Required YAML Frontmatter**:
```yaml
---
name: DEV
description: Senior Software Engineer focused on implementing features with quality-focused approach. Handles task execution with rigorous verification loops, guardrails, and TDD methodology.
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---
```

**Content Structure**:
- Core Principles (competencies, standards)
- Workflow (Phase 5: Implement, Phase 6: Verify, Phase 7: Finalize, Phase 8: Iteration)
- Quality Standards (testing, code quality, documentation, version control)
- Communication Protocol
- Guardrails (absolute rules)
- Project Context (populated from plan.md)

### 2. Updated `/implement` Command Structure

**Phase 0: Pre-execution** (Orchestrator responsibility)
```markdown
0. Pre-execution Setup:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`
   - Parse FEATURE_DIR and AVAILABLE_DOCS from output
   - Load context:
     * tasks.md (required)
     * plan.md (required)
     * spec.md (required)
     * data-model.md (if exists)
     * contracts/ (if exists)
     * research.md (if exists)
     * quickstart.md (if exists)
   - Extract from plan.md:
     * Quality standards (lint/typecheck/test commands)
     * Tech stack and constraints
     * Performance goals
   - Identify task phases and dependencies from tasks.md
```

**Phase 1-5: Task Execution** (Delegated to DEV sub-agent)
```markdown
1-5. For each task (or task phase):

   A. /implement prepares invocation package:
      Task: Use the Task tool to invoke DEV sub-agent
      Prompt: |
        Execute the following task from the implementation plan:

        **Task**: [Task ID and description from tasks.md]
        **Files**: [Exact file paths from task]
        **Phase**: [Setup/Tests/Core/Integration/Polish]

        **Context**:
        - Spec requirements: [Relevant FR-XXX from spec.md]
        - Quality standards:
          * Lint command: [from plan.md]
          * Type check: [from plan.md]
          * Test command: [from plan.md]
        - Tech stack: [from plan.md]
        - Constitution guardrails: [from constitution.md]

        **Instructions**:
        - Follow DEV agent Phase 5-7 workflow
        - Apply TDD if this is a test task
        - Verify acceptance criteria (functional)
        - Verify quality standards (lint/type/test)
        - Make atomic commit after verification passes
        - Return: status (complete/failed), files changed, commit hash, any issues

   B. DEV sub-agent executes (in separate context):
      - Gathers additional context if needed (reads files)
      - Implements code/tests following TDD
      - Runs acceptance verification
      - Runs quality verification (with 3-try limit for quality fixes)
      - Creates atomic commit
      - Returns results to /implement

   C. /implement processes results:
      - Mark task [X] in tasks.md
      - Log any decisions or issues raised by DEV
      - If failed: determine if should halt or continue
      - Update progress tracking
```

**Phase 6: Final Verification** (Orchestrator responsibility)
```markdown
6. Final Verification:
   - Aggregate all DEV results
   - Run comprehensive checklist:
     * All tasks marked complete
     * All tests pass (run full suite)
     * Coverage meets requirements
     * No linting errors
     * No type errors (if applicable)
     * Implementation matches spec.md
     * Follows plan.md architecture
     * No partial implementations
     * Commit history is clean
   - Collect screenshots/proof if live testing was done
```

**Phase 7: Finalization & User Checkpoint** (Orchestrator responsibility)
```markdown
7. Finalize:
   - Present comprehensive summary:
     * Tasks completed (list with commit hashes)
     * Key implementation decisions (from DEV reports)
     * Test results and coverage
     * Any deviations from plan (with justification)
     * Screenshots/proof of functionality
   - **EXPLICITLY WAIT for user verification**
   - Prompt user: "Implementation complete. Please review and verify. Provide feedback if changes needed."
```

**Phase 8: Iteration** (Orchestrator + DEV collaboration)
```markdown
8. Iteration (if user provides feedback):
   - Analyze feedback requirements
   - Determine scope:
     * Minor fixes → prepare specific tasks, invoke DEV
     * New functionality → may need to update tasks.md
     * Architectural changes → escalate, may need /plan revision
   - If minor: invoke DEV sub-agent with fix tasks
   - Return to Phase 6 verification after fixes
   - Repeat until user confirms satisfaction
```

### 3. Task Granularity Decision

**Recommended**: Invoke DEV at **task level** (not subtask, not full implementation)

**Rationale**:
- Tasks in tasks.md are already well-scoped (e.g., "T008 [P] User model in src/models/user.py")
- Each task maps to specific files and can be executed independently
- Parallel tasks [P] can invoke multiple DEV instances concurrently
- Allows /implement to track progress at task level
- DEV can internally break task into subtasks if needed

**Alternative for complex tasks**: /implement can detect "large" tasks and break them down before invoking DEV

### 4. State Management Strategy

**Approach**: /implement maintains state, DEV is stateless

**State tracked by /implement**:
- Tasks completed (updated tasks.md)
- Decisions made (logged per task)
- Issues encountered (logged with task ID)
- Quality metrics (test results, coverage)
- Commit history (task → commit mapping)

**Context passed to each DEV invocation**:
- Fresh context package for each task
- No assumption of memory from previous tasks
- All necessary context explicitly provided

**Benefits**:
- Clean separation: orchestration state vs execution logic
- DEV invocations are independent and parallelizable
- Easy to resume/retry individual tasks
- Clear audit trail of what was done

### 5. Parallel Execution Strategy

**For tasks marked [P]**:
```markdown
If tasks T004, T005, T006 are all [P]:
- /implement can invoke 3 DEV sub-agents concurrently
- Each gets its own context package
- Each operates independently in separate context window
- /implement aggregates results when all complete
- Mark all as [X] in tasks.md together
```

**Benefits**:
- Significant speed improvement for independent tasks
- Natural fit with sub-agent architecture
- Maintains quality (each DEV still does verification)

**Constraints**:
- Only truly independent tasks (different files, no dependencies)
- /implement must handle concurrent results correctly
     * STAY IN SCOPE
   - Extract quality standards from plan.md:
     * Linting command (if specified)
     * Type checking command (if specified)
     * Testing command and coverage requirements
     * Performance targets
```

### 2. Enhance Task Execution Loop

```markdown
4. Execute implementation following the task plan:
   - **Phase-by-phase execution**: Complete each phase before moving to the next
   - **Respect dependencies**: Run sequential tasks in order, parallel tasks [P] can run together
   - **Follow TDD approach**: Execute test tasks before their corresponding implementation tasks
   - **File-based coordination**: Tasks affecting the same files must run sequentially
   - **Validation checkpoints**: Verify each phase completion before proceeding

   For each task:
   a. Execute task code (test/implementation based on task type)

   b. Acceptance Criteria Verification:
      - Verify task meets its functional requirements
      - If live application updates: run app, test functionality, capture screenshots
      - If fails:
        * Write clear synopsis documenting what failed and why
        * Mark task incomplete
        * Return to step (a)

   c. Quality Standards Verification:
      - Run linting (zero errors/warnings required)
      - Run type checking (zero errors/warnings required)
      - Run tests (all must pass, coverage requirements met)
      - Verify tests are meaningful (validate real behavior, not just pass)
      - Check code follows existing patterns (analyze codebase if uncertain)
      - If fails:
        * Analyze failure type:
          - Functional issue → document, mark incomplete, return to step (a)
          - Quality-only issue → attempt to fix in place
            * Max 3 fix attempts
            * If still failing after 3 tries → STOP, present status with:
              - What was attempted
              - Why it failed
              - Specific blockers
              - Recommended next steps
            * Wait for user instruction before proceeding

   d. Atomic Commit:
      - Create commit with clear, descriptive message
      - Message should explain WHAT changed and WHY
      - Keep commit focused on this task only (reviewable size)

   e. Mark task complete [X] in tasks.md

   f. Report progress:
      - What was completed
      - Why key decisions were made
      - Any risks or uncertainties identified
      - Next steps
```

### 3. Add Verification Phase

```markdown
7. Phase 6 - Final Verification:
   - [ ] All required tasks completed (check tasks.md)
   - [ ] All tests pass (run full test suite)
   - [ ] Test coverage meets requirements (check coverage report)
   - [ ] Tests validate real behavior (not just pass for the sake of passing)
   - [ ] No linting errors or warnings (run linting)
   - [ ] No type errors or warnings (run type checking, if applicable)
   - [ ] Implementation matches specification (review spec.md requirements)
   - [ ] Implementation follows technical plan (review plan.md architecture)
   - [ ] Code follows existing patterns (no over-engineering)
   - [ ] Live application works correctly (if applicable - manual testing)
   - [ ] Documentation is complete and accurate (inline comments, JSDoc/JavaDoc)
   - [ ] Commit history is clean and meaningful (review git log)
   - [ ] NO partial implementations or placeholders
   - [ ] NO scope creep or unrelated changes
```

### 4. Add Finalization Phase

```markdown
8. Phase 7 - Finalize:
   - Present comprehensive results summary:
     * Tasks completed
     * Key implementation decisions and rationale
     * Test results and coverage metrics
     * Any deviations from plan and justification
     * Known limitations or future work
     * Screenshots/evidence of functionality (if applicable)
   - **WAIT for user verification and feedback**
   - Do NOT proceed to other work until user confirms completion
```

### 5. Add Iteration Protocol

```markdown
9. Phase 8 - Iteration (if needed):
   - If user provides feedback requiring changes:
     * Analyze feedback requirements
     * Determine scope:
       - Minor fixes → reopen relevant completed tasks
       - New functionality → create new tasks
       - Architectural changes → escalate, may require /plan revision
     * Update tasks.md with new/reopened tasks
     * Return to execution loop (step 4)
   - Continue iteration until user confirms satisfaction
```

### 6. Enhance Communication Throughout

```markdown
Throughout all phases, communicate using DEV agent protocol:
- ✅ Explain decisions and tradeoffs as you make them
- ✅ Surface risks and uncertainties proactively (before they cause failures)
- ✅ Ask clarifying questions when task requirements are ambiguous
- ✅ Admit when something is unclear or outside scope
- ✅ Provide specific, actionable next steps in all status reports
- ✅ Use clear, concise language (avoid unnecessary verbosity)
- ❌ Do not make assumptions without stating them explicitly
- ❌ Do not hide problems or partial implementations
```

---

## Integration Challenges

### Challenge 1: Subtask Granularity

**Problem**: Tasks in tasks.md are high-level (e.g., "T008 [P] User model in src/models/user.py"). The DEV agent operates on subtasks within each task.

**Solution Options**:
1. Keep tasks atomic and apply verification once per task
2. Have agent internally break complex tasks into subtasks
3. Enhance /tasks command to generate finer-grained tasks

**Recommendation**: Option 1 for simplicity, with guidance that complex tasks should be broken down during /tasks generation

### Challenge 2: Quality Standards Discovery

**Problem**: Where do quality standards (lint commands, test commands) come from?

**Solution Options**:
1. Extract from plan.md "Technical Context" section
2. Discover from project files (package.json, pyproject.toml, etc.)
3. Prompt user during /plan phase

**Recommendation**: Option 1 + 2 (extract from plan, fallback to project discovery)

### Challenge 3: Acceptance Criteria Traceability

**Problem**: Tasks in tasks.md don't always have explicit acceptance criteria.

**Solution Options**:
1. Enhance /tasks command to include acceptance criteria per task
2. Have agent infer acceptance criteria from task description + spec.md
3. Require manual acceptance criteria in tasks.md

**Recommendation**: Option 2 (inference) with suggestion to enhance /tasks template

### Challenge 4: Live Testing Automation

**Problem**: "Run live application and capture screenshots" requires environment-specific knowledge.

**Solution Options**:
1. Extract from quickstart.md or plan.md "how to run the app"
2. Prompt agent to discover run commands from project structure
3. Skip live testing if not feasible

**Recommendation**: Option 1 + 2, with graceful degradation if can't determine

### Challenge 5: Balancing Prescription vs Flexibility

**Problem**: Over-prescriptive commands limit agent intelligence; under-prescriptive commands lead to inconsistent behavior.

**Solution**: Use **principle-based instructions** rather than step-by-step scripts:
- State the WHAT and WHY (e.g., "ensure quality standards are met because...")
- Provide the GUARDRAILS (e.g., "max 3 fix attempts")
- Let agent figure out HOW based on context

---

## Recommended Implementation Path

### Phase 1: Minimal Viable Integration (Quick Win)
1. Add pre-execution step to load `final/dev.md`
2. Add instruction: "Operate as DEV agent during Phase 5-7, applying all principles and guardrails"
3. Add post-execution: "Phase 7 - wait for user verification"
4. Test with a small feature implementation

### Phase 2: Add Verification Gates (Quality Focus)
1. Add per-task quality verification checklist
2. Add failure handling protocol (functional vs quality, 3-try limit)
3. Add commit guidance (atomic, after verification)
4. Test with a medium complexity feature

### Phase 3: Enhance Communication (Transparency)
1. Add proactive risk surfacing
2. Add decision explanation requirements
3. Add uncertainty admission protocol
4. Test with a complex feature

### Phase 4: Add Iteration Support (Completeness)
1. Add Phase 8 iteration protocol
2. Add task reopening logic
3. Add feedback analysis guidance
4. Test with a feature requiring multiple iterations

---

## Success Metrics

How to measure if integration is successful:

1. **Quality Metrics**:
   - Zero linting errors in final implementation
   - Zero type errors in final implementation
   - 100% test pass rate
   - Test coverage meets plan.md requirements

2. **Process Metrics**:
   - Atomic commits per task (not one giant commit at end)
   - Clear commit messages explaining what and why
   - No partial implementations (all tasks fully complete)
   - Failures caught and resolved within 3 tries

3. **Communication Metrics**:
   - Decisions explained (not just "I did X")
   - Risks surfaced before failures occur
   - Questions asked when requirements unclear
   - Status reports include next steps

4. **User Experience**:
   - User feels informed throughout process
   - User has control (explicit verification checkpoints)
   - Iteration is smooth (not starting from scratch)
   - Final implementation meets all requirements

---

## Conclusion

The Spec Kit's `/implement` command provides excellent **orchestration** (context loading, task parsing, phase execution) but lacks the DEV agent's **quality enforcement** (verification loops, guardrails, iteration protocols).

**Recommended Integration Strategy**: **Approach C (Hybrid)**
- Preserve Spec Kit's orchestration structure
- Add DEV agent's verification gates and guardrails
- Enhance communication to be more transparent and proactive
- Add user checkpoint and iteration support

**Key Additions**:
1. Pre-execution: Load DEV agent principles and quality standards
2. Per-task: Add acceptance + quality verification loops with failure handling
3. Post-task: Atomic commits with clear messages
4. Post-execution: Phase 6 (verify), Phase 7 (user checkpoint), Phase 8 (iteration)
5. Throughout: DEV agent communication protocol

**Expected Outcome**: Higher quality implementations with clear process, proactive risk management, and smooth iteration based on user feedback.