# Integration Proposal: DEV Agent + Spec Kit `/implement` Command

**Status**: Draft - Decision Gathering
**Last Updated**: 2025-09-30
**Research**: See [implement-dev-integration-research.md](./implement-dev-integration-research.md)

---

## Overview

This proposal aims to integrate the DEV agent (defined in `final/dev.md`) with Spec Kit's `/implement` command using Claude Code's sub-agent architecture. The goal is to leverage DEV's quality-focused implementation methodology while preserving Spec Kit's orchestration framework.

**Key Insight from Research**: Claude Code sub-agents operate in separate context windows and are stateless, which significantly impacts our integration design.

---

## Core Architectural Decisions (Pre-Determined)

Based on research and analysis, these architectural decisions are established:

### ✅ Decision 1: Sub-Agent Location
**Location**: `.claude/agents/dev.md`
- Requires YAML frontmatter for sub-agent configuration
- Scoped tool access (Read, Write, Edit, Bash, Glob, Grep only)
- Reusable across commands and standalone invocation

### ✅ Decision 2: Invocation Method
**Method**: Explicit Task tool invocation from `/implement` command
- /implement prepares context package for each task
- Uses Task tool to invoke DEV sub-agent
- DEV executes in separate context window, returns results

### ✅ Decision 3: Task Granularity
**Level**: Per-task invocation
- Each task in tasks.md gets its own DEV invocation
- Parallel tasks [P] can invoke multiple DEV instances concurrently
- Allows fine-grained progress tracking and failure handling

### ✅ Decision 4: State Management
**Strategy**: /implement maintains state, DEV is stateless
- /implement tracks: completed tasks, decisions, issues, commits
- Each DEV invocation receives fresh context package
- No memory between DEV invocations (clean execution)

### ✅ Decision 5: Verification Ownership
**Approach**: DEV performs verification, /implement aggregates
- DEV runs acceptance + quality verification per task
- DEV applies 3-try limit and stop-and-present protocol
- /implement runs final comprehensive verification (Phase 6)

---

## Refinement Questions for Optimal Design

These questions will help us refine the implementation details and edge cases.

### Round 1: Context Package Design

**Q1.1: Context Extraction Strategy**

When /implement prepares the context package for each task, how detailed should it be?

- **Option A - Minimal**: Only task description + file paths
  - *Pros*: Small prompt, DEV figures out details
  - *Cons*: DEV may miss important constraints

- **Option B - Comprehensive**: Full context dump (all spec requirements, all quality standards)
  - *Pros*: DEV has everything it needs
  - *Cons*: Large prompts, token waste, context pollution

- **Option C - Smart Extraction**: Extract only relevant parts based on task
  - *Pros*: Optimized context, DEV gets what it needs
  - *Cons*: Requires intelligence in /implement to extract correctly

**Recommendation**: Option C - Smart Extraction

**Decision Rationale**: The orchestrator (/implement) maintains full project context and intelligently extracts only task-relevant information for each DEV invocation. This keeps DEV focused, token-efficient, and ensures it has exactly what it needs to complete its specific task.

---

**Q1.2: Quality Standards Discovery**

Where should quality standards (lint/type/test commands) be defined?

- **Option A - In plan.md**: Add to "Technical Context" section
  - *Pros*: Already part of planning phase, version controlled with feature
  - *Cons*: Might be forgotten during /plan

- **Option B - Separate config file**: Create `.specify/quality-standards.md`
  - *Pros*: Central definition, reusable across features
  - *Cons*: Another file to maintain

- **Option C - Auto-discovery**: /implement detects from project files (package.json, pyproject.toml)
  - *Pros*: No manual definition needed
  - *Cons*: May not catch custom scripts

- **Option D - Hybrid**: plan.md preferred, fallback to auto-discovery
  - *Pros*: Best of both worlds
  - *Cons*: More complex logic

**Recommendation**: Option A - In plan.md

**Decision Rationale**: Quality standards should be defined in plan.md as part of the planning phase. The /plan command should attempt to discover quality standards by analyzing the project (package.json, pyproject.toml, etc.). If quality standards cannot be determined, add a "CLARIFICATION REQUIRED" tag in plan.md to prompt user input before implementation begins.

---

**Q1.3: Acceptance Criteria Mapping**

How should acceptance criteria be linked to tasks?

- **Option A - Inferred**: DEV infers acceptance criteria from task description + spec.md
  - *Pros*: No extra work, flexible
  - *Cons*: May miss specific criteria

- **Option B - Explicit in tasks.md**: Enhance /tasks template to include acceptance criteria per task
  - *Pros*: Clear, testable criteria
  - *Cons*: More verbose tasks.md

- **Option C - Separate mapping file**: Create `acceptance-criteria.md` mapping tasks to criteria
  - *Pros*: Clean separation
  - *Cons*: Another artifact to maintain

**Recommendation**: Option B - Explicit in tasks.md

**Decision Rationale**: Tasks.md should be comprehensive. Each task can have subtasks that serve as acceptance criteria. This makes "done" explicit and measurable. The orchestrator can extract these subtask acceptance criteria when preparing DEV's context package, and DEV can verify each subtask is complete before marking the parent task as done.

---

### Round 2: Failure Handling & Recovery

**Q2.1: DEV Failure Response**

When DEV reports a task failure (after 3 tries), what should /implement do?

- **Option A - Halt completely**: Stop all execution, present status to user
  - *Pros*: Safe, user has control
  - *Cons*: Blocks parallel progress

- **Option B - Skip and continue**: Mark task as failed, continue with other tasks
  - *Pros*: Maximizes progress
  - *Cons*: May create dependencies issues

- **Option C - Smart halt**: Continue only with tasks that don't depend on failed task
  - *Pros*: Balanced approach
  - *Cons*: Requires dependency graph analysis

- **Option D - User choice**: Prompt user immediately when failure occurs
  - *Pros*: User decides strategy
  - *Cons*: Interrupts flow

**Recommendation**: Option A - Halt completely

**Decision Rationale**: When DEV reports a task failure after 3 tries, /implement should stop all execution and present a comprehensive status report to the user. This ensures user control, prevents cascading failures, and allows the user to assess the situation before deciding how to proceed. Safety and clarity over speed.

---

**Q2.2: Partial Phase Completion**

If only some tasks in a phase complete (e.g., 3 out of 5 Core tasks), should /implement:

- **Option A - Require full phase**: Don't proceed to next phase until all tasks complete
  - *Pros*: Clean phase boundaries
  - *Cons*: May be overly strict

- **Option B - Allow progression**: Move to next phase, track incomplete tasks
  - *Pros*: Flexible, maintains momentum
  - *Cons*: May create integration issues

- **Option C - Critical path only**: Allow progression if critical tasks complete
  - *Pros*: Smart about what matters
  - *Cons*: Requires critical path identification

**Recommendation**: Option A - Require full phase

**Decision Rationale**: All tasks in a phase must complete before proceeding to the next phase. This maintains clean phase boundaries, ensures quality gates are met, and aligns with the halt-on-failure approach. Phases represent logical milestones and should be fully complete.

---

### Round 3: Parallel Execution Optimization

**Q3.1: Parallel Invocation Limit**

When multiple tasks are marked [P], how many DEV instances should run concurrently?

- **Option A - Unlimited**: Invoke all [P] tasks at once
  - *Pros*: Maximum speed
  - *Cons*: Resource intensive, rate limits

- **Option B - Fixed limit (e.g., 3)**: Run max 3 concurrent DEV instances
  - *Pros*: Controlled resource use
  - *Cons*: Arbitrary limit

- **Option C - Dynamic**: Based on task complexity or system resources
  - *Pros*: Optimal use of resources
  - *Cons*: Complex to implement

- **Option D - User configurable**: Let user set via environment variable
  - *Pros*: User control
  - *Cons*: Adds configuration burden

**Recommendation**: Option B - Fixed limit of 3

**Decision Rationale**: Run a maximum of 3 concurrent DEV instances for parallel tasks. This provides controlled resource usage, prevents rate limiting issues, and maintains predictable behavior while still offering meaningful parallelization benefits.

---

**Q3.2: Parallel Result Aggregation**

When concurrent DEV instances complete, how should /implement handle results?

- **Option A - Wait for all**: Only process results when all parallel tasks complete
  - *Pros*: Clean batch processing
  - *Cons*: Slow tasks block reporting

- **Option B - Process immediately**: Update tasks.md as each DEV returns
  - *Pros*: Real-time progress
  - *Cons*: Potential race conditions

- **Option C - Streaming updates**: Report progress as it happens, aggregate at end
  - *Pros*: Best user experience
  - *Cons*: More complex

**Recommendation**: Option C - Streaming updates (native behavior)

**Decision Rationale**: This is the natural behavior of Claude Code's sub-agent architecture. When multiple DEV instances run in parallel, they return results as they complete. The orchestrator processes each result immediately (update tasks.md, report progress, launch next queued task), then aggregates for final verification. No special implementation needed - this is how the system works.

---

### Round 4: User Experience & Feedback

**Q4.1: Progress Reporting Frequency**

How often should /implement report progress to the user?

- **Option A - Per task**: Report after each task completes
  - *Pros*: User always knows current status
  - *Cons*: Can be verbose for many tasks

- **Option B - Per phase**: Report only at phase boundaries
  - *Pros*: Clean, less noise
  - *Cons*: User waits longer for updates

- **Option C - Adaptive**: Frequent for slow tasks, less frequent for fast tasks
  - *Pros*: Optimized for perceived progress
  - *Cons*: Unpredictable

- **Option D - Configurable**: User sets via command argument
  - *Pros*: User preference
  - *Cons*: More to configure

**Recommendation**: Option B - Per phase

**Decision Rationale**: Report progress at phase boundaries only. This provides clean, focused updates without overwhelming the user with per-task noise. Each phase summary includes completed tasks, quality metrics, and any decisions made during that phase. The orchestrator still processes results as they arrive (per Q3.2) but batches reporting to phase milestones.

---

**Q4.2: Final Summary Format**

What should the Phase 7 completion summary include?

- **Option A - Concise**: Task count, test results, commit hash
  - *Pros*: Quick to read
  - *Cons*: May miss important details

- **Option B - Comprehensive**: All tasks, all decisions, all metrics, screenshots
  - *Pros*: Complete information
  - *Cons*: Information overload

- **Option C - Tiered**: Brief summary + expandable details
  - *Pros*: Balanced
  - *Cons*: Requires structured format

- **Option D - User customizable**: Template-based summary
  - *Pros*: Flexible
  - *Cons*: More setup

**Recommendation**: Option B - Comprehensive

**Decision Rationale**: The Phase 7 completion summary should be comprehensive, including all completed tasks with commit hashes, all implementation decisions made by DEV instances, complete quality metrics (test results, coverage, lint/type status), screenshots/proof from live testing, and any deviations from the plan with justifications. This aligns with DEV's transparency requirements and provides a complete record for verification.

---

**Q4.3: Iteration Protocol Trigger**

How should Phase 8 (Iteration) be triggered?

- **Option A - Automatic**: Any user feedback triggers iteration
  - *Pros*: Seamless flow
  - *Cons*: May misinterpret comments as requests

- **Option B - Explicit command**: User must type "/iterate" or similar
  - *Pros*: Clear intent
  - *Cons*: Extra step

- **Option C - Confirmation prompt**: Ask "Would you like me to apply these changes?"
  - *Pros*: Clear, safe
  - *Cons*: Extra interaction

**Recommendation**: Option C - Confirmation prompt

**Decision Rationale**: After presenting the comprehensive Phase 7 summary and receiving user feedback, /implement should explicitly ask "Would you like me to iterate on the implementation?" This prevents misinterpretation of casual comments as change requests while keeping the iteration process clear and intentional.

---

### Round 5: DEV Sub-Agent Configuration

**Q5.1: Tool Restrictions**

Should DEV sub-agent have access to additional tools beyond Read/Write/Edit/Bash?

Current scope: Read, Write, Edit, Bash, Glob, Grep

- **Option A - Keep restricted**: Only implementation tools
  - *Pros*: Focused, secure
  - *Cons*: May need web research for libraries

- **Option B - Add WebFetch**: Allow DEV to research during implementation
  - *Pros*: Self-sufficient
  - *Cons*: May waste time on unnecessary research

- **Option C - Add MCP tools**: Allow access to specific MCPs (GitHub, Context7)
  - *Pros*: Enhanced capabilities
  - *Cons*: More complex

- **Option D - Dynamic based on task**: Grant tools based on task type
  - *Pros*: Optimal per task
  - *Cons*: Complex configuration

**Recommendation**: Option A - Keep restricted (with verification tools)

**Decision Rationale**: DEV sub-agent should have access to implementation tools (Read, Write, Edit, Bash, Glob, Grep) plus any tools necessary for verification. This includes:
- Bash for running scripts, lint/typecheck/test commands
- Browser MCP for testing live applications and capturing screenshots
- Any other verification-specific MCPs needed to validate acceptance criteria and quality standards

DEV remains focused on execution and verification, not research. All research context is provided by the orchestrator.

---

**Q5.2: DEV Agent Model Selection**

Which Claude model should DEV sub-agent use?

- **Option A - Same as main**: Use whatever model /implement is using
  - *Pros*: Consistent capabilities
  - *Cons*: May be overkill or underpowered

- **Option B - Fixed (Sonnet 4.5)**: Always use specific model for DEV
  - *Pros*: Predictable performance
  - *Cons*: No flexibility

- **Option C - Task-based**: Complex tasks get stronger model
  - *Pros*: Optimized cost/performance
  - *Cons*: Requires task complexity assessment

- **Option D - User configurable**: Let user specify in frontmatter
  - *Pros*: User control
  - *Cons*: More to configure

**Recommendation**: Option B - Fixed (Sonnet 4.5)

**Decision Rationale**: DEV sub-agent should always use Sonnet 4.5 for consistent, high-quality performance across all implementation tasks. This ensures predictable behavior for coding, reasoning, and verification regardless of what model the orchestrator uses.

---

### Round 6: Edge Cases & Robustness

**Q6.1: Missing Context Handling**

What if required context (plan.md, spec.md) is incomplete or missing?

- **Option A - Strict**: Fail fast, require complete context
  - *Pros*: Ensures quality
  - *Cons*: Less flexible

- **Option B - Graceful degradation**: Work with what's available, flag gaps
  - *Pros*: Still makes progress
  - *Cons*: May produce lower quality

- **Option C - Interactive**: Prompt user for missing information
  - *Pros*: Gets what's needed
  - *Cons*: Interrupts flow

**Recommendation**: Option A - Strict

**Decision Rationale**: Fail fast and require complete context. The prerequisites check should validate that all required files (plan.md, spec.md, tasks.md) exist and contain necessary information. Better to fail early with a clear error message than attempt implementation with incomplete context and produce poor quality results. Aligns with the "CLARIFICATION REQUIRED" approach.

---

**Q6.2: Git State Management**

How should /implement handle git state issues (conflicts, dirty working tree, etc.)?

- **Option A - Pre-flight check**: Verify clean state before starting
  - *Pros*: Prevents issues
  - *Cons*: Strict requirements

- **Option B - Auto-stash**: Stash changes, implement, restore
  - *Pros*: Transparent to user
  - *Cons*: May hide problems

- **Option C - User decision**: Detect issues, ask user how to proceed
  - *Pros*: User control
  - *Cons*: Interrupts flow

**Recommendation**: Option A - Pre-flight check

**Decision Rationale**: Verify clean git state before starting implementation. The prerequisites check should ensure working tree is clean, preventing merge conflicts and lost work. Implementation should start from a known, clean state. User can address git issues before running /implement.

**Additional Decision - Commit Strategy**:
To handle parallel execution safely while maintaining atomic commits:
- During phase execution: DEV instances complete tasks and verify quality but do NOT commit
- At phase completion: /implement creates one commit per completed task sequentially using files reported by each DEV
- This prevents parallel commit conflicts while maintaining granular, atomic commit history per task

---

**Q6.3: Task Breakdown Threshold**

At what point should a task be considered "too large" and broken down?

- **Option A - Line count**: If task description > X lines in tasks.md
  - *Pros*: Simple heuristic
  - *Cons*: May not reflect complexity

- **Option B - File count**: If task affects > Y files
  - *Pros*: Reflects scope
  - *Cons*: May miss single-file complexity

- **Option C - Never auto-break**: Trust /tasks to create appropriate granularity
  - *Pros*: Simpler implementation
  - *Cons*: May get unwieldy tasks

- **Option D - DEV decides**: Let DEV break down if it determines task is complex
  - *Pros*: Intelligent decision
  - *Cons*: Less predictable

**Recommendation**: Option C - Never auto-break

**Decision Rationale**: Trust /tasks command to generate appropriately-scoped tasks. Tasks already have subtasks as acceptance criteria (per Q1.3), providing granular verification points. If a task is too large, that's a planning issue to address during /tasks generation, not during implementation. DEV executes tasks as defined without attempting to break them down further.

---

## Decision Log

This section will be populated as decisions are made for each question above.

### Context Package Design
- Q1.1: ✅ **Option C - Smart Extraction** - Orchestrator extracts task-relevant context only
- Q1.2: ✅ **Option A - In plan.md** - Quality standards defined in plan.md with "CLARIFICATION REQUIRED" tag if undiscoverable
- Q1.3: ✅ **Option B - Explicit in tasks.md** - Tasks have subtasks as acceptance criteria

### Failure Handling & Recovery
- Q2.1: ✅ **Option A - Halt completely** - Stop execution and present status to user
- Q2.2: ✅ **Option A - Require full phase** - All tasks must complete before next phase

### Parallel Execution Optimization
- Q3.1: ✅ **Option B - Fixed limit of 3** - Maximum 3 concurrent DEV instances
- Q3.2: ✅ **Option C - Streaming updates** - Natural sub-agent behavior, process results as they arrive

### User Experience & Feedback
- Q4.1: ✅ **Option B - Per phase** - Report at phase boundaries only
- Q4.2: ✅ **Option B - Comprehensive** - Complete summary with tasks, decisions, metrics, proof
- Q4.3: ✅ **Option C - Confirmation prompt** - Ask "Would you like me to iterate on the implementation?"

### DEV Sub-Agent Configuration
- Q5.1: ✅ **Option A - Keep restricted (with verification tools)** - Implementation + verification tools only
- Q5.2: ✅ **Option B - Fixed (Sonnet 4.5)** - Always use Sonnet 4.5 for consistent performance

### Edge Cases & Robustness
- Q6.1: ✅ **Option A - Strict** - Fail fast, require complete context
- Q6.2: ✅ **Option A - Pre-flight check** - Verify clean git state; sequential commits at phase boundary
- Q6.3: ✅ **Option C - Never auto-break** - Trust /tasks to create appropriate granularity

---

## Proposal Details

### Architecture Overview

The integration leverages **Claude Code's sub-agent architecture** to combine Spec Kit's orchestration framework with DEV's quality-focused execution methodology.

```
┌─────────────────────────────────────────────────────────────┐
│                    /implement (Orchestrator)                 │
│  - Loads full project context (spec, plan, tasks, etc.)     │
│  - Manages phases and dependencies                           │
│  - Extracts task-relevant context packages                   │
│  - Invokes DEV sub-agents for execution                      │
│  - Aggregates results and manages commits                    │
│  - Reports at phase boundaries                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─ Invokes (max 3 concurrent)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    DEV Sub-Agent (Executor)                  │
│  - Receives task-specific context package                    │
│  - Implements code/tests (TDD if applicable)                 │
│  - Verifies acceptance criteria (functional)                 │
│  - Verifies quality standards (lint/type/test)               │
│  - Reports files modified and results                        │
│  - Returns to orchestrator (no commit)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓ Returns results
┌─────────────────────────────────────────────────────────────┐
│              Phase Boundary (Orchestrator)                   │
│  - Aggregates all task results                               │
│  - Creates sequential commits (one per task)                 │
│  - Runs final quality verification                           │
│  - Reports phase summary to user                             │
└─────────────────────────────────────────────────────────────┘
```

### Workflow Integration

#### Phase 0: Pre-execution (Orchestrator)
1. Run prerequisites check script with `--require-tasks`
2. Verify clean git state (fail if dirty)
3. Load complete context:
   - tasks.md (required)
   - plan.md (required)
   - spec.md (required)
   - quality standards from plan.md
   - constitution.md guardrails
   - Optional: data-model.md, contracts/, research.md, quickstart.md
4. Parse task phases and dependencies
5. Validate all required context present (fail if incomplete)

#### Phase 1-5: Task Execution (Orchestrator + DEV)

**For each phase (Setup, Tests, Core, Integration, Polish):**

1. **Orchestrator identifies tasks** in current phase
2. **Orchestrator prepares context packages** for each task:
   - Task ID, description, file paths
   - Relevant spec requirements (extracted via FR-XXX references)
   - Quality standards (lint/type/test commands from plan.md)
   - Subtasks as acceptance criteria
   - Constitution guardrails
   - Tech stack constraints

3. **Orchestrator invokes DEV sub-agents** (max 3 concurrent):
   - Uses Task tool with prepared context package
   - Parallel tasks [P] processed with limit of 3
   - Sequential tasks processed in order

4. **DEV executes autonomously** (in separate context):
   - Reads additional files if needed
   - Implements code/tests (follows TDD if test task)
   - Verifies acceptance criteria (runs app if needed, takes screenshots)
   - Verifies quality standards (lint/type/test)
   - Applies 3-try limit for quality fixes
   - If failure after 3 tries: returns failure status with details
   - If success: returns success with files modified, decisions made

5. **Orchestrator processes DEV results** (streaming):
   - Mark task complete in tasks.md
   - Log decisions and files modified
   - If failure: HALT completely, present status to user
   - If success: continue to next task

6. **Phase boundary reached** (all tasks in phase complete):
   - Create sequential commits (one per task):
     ```bash
     git add <files-from-T001> && git commit -m "T001: Description"
     git add <files-from-T002> && git commit -m "T002: Description"
     ```
   - Run phase-level quality verification
   - Present phase summary:
     * Tasks completed (count)
     * Key decisions made
     * Quality metrics
     * Any issues encountered

7. **Move to next phase** or proceed to final verification

#### Phase 6: Final Verification (Orchestrator)

Run comprehensive verification checklist:
- [ ] All tasks marked [X] in tasks.md
- [ ] All tests pass (full suite)
- [ ] Coverage meets requirements (from plan.md)
- [ ] No linting errors/warnings
- [ ] No type errors/warnings (if applicable)
- [ ] Implementation matches spec.md requirements
- [ ] Implementation follows plan.md architecture
- [ ] No partial implementations
- [ ] Commit history is clean and atomic

#### Phase 7: Finalization (Orchestrator)

Present comprehensive completion summary:
- **Tasks Completed**: List all with commit hashes
- **Implementation Decisions**: Key decisions from all DEV instances
- **Quality Metrics**:
  * Test results and coverage
  * Lint/type check status
  * Build status
- **Proof of Functionality**: Screenshots from live testing (if applicable)
- **Deviations from Plan**: Any changes with justifications
- **Known Issues**: Any limitations or future work

**WAIT for user verification**

If user provides feedback:
- Ask: "Would you like me to iterate on the implementation?"
- If yes: Analyze feedback, update/create tasks, return to Phase 1-5
- If no: Implementation complete

#### Phase 8: Iteration (Orchestrator + DEV)

If user requests iteration:
1. Analyze feedback to determine scope
2. Update tasks.md (reopen tasks or create new ones)
3. Return to Phase 1-5 execution loop
4. After changes: return to Phase 6 verification
5. Repeat until user confirms satisfaction

### Key Design Decisions Applied

**Context Management** (Q1.1):
- Orchestrator maintains full context
- Smart extraction: only task-relevant info sent to DEV
- Parse FR-XXX references to include specific spec sections

**Quality Standards** (Q1.2):
- Defined in plan.md during /plan phase
- Auto-discovered from project files with "CLARIFICATION REQUIRED" if missing
- Extracted and provided to each DEV invocation

**Acceptance Criteria** (Q1.3):
- Tasks in tasks.md have subtasks as acceptance criteria
- DEV verifies each subtask before marking parent task complete
- Orchestrator extracts subtasks when preparing context package

**Failure Handling** (Q2.1, Q2.2):
- DEV applies 3-try limit for quality fixes
- On failure: orchestrator halts completely, presents status
- Phases are strict gates: all tasks must complete before next phase

**Parallel Execution** (Q3.1, Q3.2):
- Maximum 3 concurrent DEV instances
- Streaming results: orchestrator processes as each DEV completes
- Queue management: launch next task when slot opens

**User Experience** (Q4.1, Q4.2, Q4.3):
- Progress reported at phase boundaries (not per task)
- Comprehensive final summary with all details
- Explicit confirmation prompt for iteration

**DEV Configuration** (Q5.1, Q5.2):
- Tools: Read, Write, Edit, Bash, Glob, Grep + Browser MCP for verification
- Model: Always Sonnet 4.5 for consistent performance
- Focus: Execution and verification (no research)

**Robustness** (Q6.1, Q6.2, Q6.3):
- Strict context validation: fail fast if incomplete
- Clean git state required: pre-flight check
- Sequential commits at phase boundary (prevents parallel conflicts)
- Trust /tasks granularity: no auto-breakdown

### State Management

**Orchestrator maintains:**
- Task completion status (tasks.md updates)
- Decision log (per task, aggregated)
- Files modified (per task, for commits)
- Quality metrics (test results, coverage, lint/type status)
- Phase progress tracking

**DEV is stateless:**
- Each invocation receives fresh context package
- No memory between invocations
- Returns results to orchestrator
- No assumptions about previous tasks

---

## Implementation Specification

### 1. DEV Sub-Agent Configuration

**File**: `.claude/agents/dev.md`

**Action**: Move and modify `final/dev.md` to `.claude/agents/dev.md` with required YAML frontmatter

**YAML Frontmatter**:
```yaml
---
name: DEV
description: Senior Software Engineer focused on implementing features with quality-focused approach. Handles task execution with rigorous verification loops, guardrails, and TDD methodology. Operates as execution agent within /implement command workflow.
model: claude-sonnet-4-5
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - mcp__browser__*
---
```

**Content Modifications**:
1. **Remove Phase 1-4** (Understand, Plan, Iterate on Plan, Document) - these are orchestrator responsibilities
2. **Keep Phase 5-8** (Implement, Verify, Finalize, Iteration) - these are DEV's core execution phases
3. **Update Phase 5 (Implement)** to clarify:
   - DEV receives context package from orchestrator
   - NO commits during execution (removed from workflow)
   - Returns results with files modified and decisions made
4. **Update Phase 7 (Finalize)** to clarify:
   - Return comprehensive results to orchestrator
   - Do not wait for user (orchestrator handles user interaction)
5. **Add new section: "Context Package"** explaining what DEV receives:
   ```markdown
   ## Context Package (Provided by Orchestrator)

   DEV receives a focused context package for each task containing:
   - Task ID, description, and file paths
   - Subtasks as acceptance criteria
   - Relevant spec requirements (FR-XXX references)
   - Quality standards (lint/type/test commands)
   - Constitution guardrails
   - Tech stack constraints

   DEV should trust this context is complete and accurate.
   ```

### 2. /implement Command Modifications

**File**: `.claude/commands/implement.md`

**Current Structure** (from analysis):
```markdown
0. Prerequisites check
1-5. Task execution loop
6. Report completion
```

**New Structure**:
```markdown
# /implement - Execute Implementation Plan with DEV Agent Integration

Execute the implementation plan by processing tasks through DEV sub-agent with quality-focused methodology.

## Prerequisites

0. **Pre-execution Validation**:
   ```bash
   .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
   ```
   - Verify tasks.md exists and contains tasks
   - Verify plan.md exists
   - Verify spec.md exists
   - Parse FEATURE_DIR and AVAILABLE_DOCS from output

1. **Git State Check**:
   ```bash
   git status --porcelain
   ```
   - FAIL if working tree is not clean
   - Error message: "Working tree must be clean before implementation. Please commit or stash changes."

2. **Load Context**:
   - Read and parse tasks.md (required)
   - Read and parse plan.md (required)
   - Read and parse spec.md (required)
   - Read constitution.md for guardrails
   - Read optional: data-model.md, contracts/, research.md, quickstart.md

3. **Extract Quality Standards** from plan.md:
   - Look for "Quality Standards", "Testing", "Technical Context" sections
   - Extract: lint command, type check command, test command, coverage requirements
   - If not found: attempt auto-discovery from package.json, pyproject.toml, etc.
   - If still not found: FAIL with "CLARIFICATION REQUIRED: Quality standards not defined in plan.md"

4. **Parse Task Structure**:
   - Identify phases: Setup, Tests, Core, Integration, Polish
   - Identify parallel tasks (marked [P])
   - Identify dependencies
   - Build execution order

## Execution Loop

**For each phase:**

5. **Identify tasks in current phase**

6. **Prepare context packages**:
   For each task, extract:
   - Task ID and full description
   - File paths from task
   - Subtasks (acceptance criteria)
   - Parse task description for FR-XXX references, extract those spec sections
   - Quality standards (lint/type/test commands)
   - Relevant constitution guardrails
   - Tech stack from plan.md

7. **Invoke DEV sub-agents** (max 3 concurrent):

   For sequential tasks:
   ```
   For each task in order:
     Use Task tool to invoke DEV sub-agent:
       subagent_type: "dev"
       description: "Implement [Task ID]"
       prompt: |
         You are executing a task from the implementation plan.

         **Task**: [Task ID and description]
         **Files**: [File paths]
         **Phase**: [Setup/Tests/Core/Integration/Polish]

         **Context Package**:
         - Subtasks (Acceptance Criteria):
           [List of subtasks from tasks.md]

         - Spec Requirements:
           [Extracted FR-XXX sections from spec.md]

         - Quality Standards:
           * Lint: [command from plan.md]
           * Type Check: [command from plan.md]
           * Test: [command from plan.md]
           * Coverage: [requirement from plan.md]

         - Tech Stack: [from plan.md]

         - Constitution Guardrails:
           * NO PARTIAL IMPLEMENTATION
           * NO OVER-ENGINEERING
           * PRODUCTIVE ITERATION ONLY (3-try limit)
           * FOLLOW EXISTING PATTERNS
           * STAY IN SCOPE

         **Instructions**:
         1. Implement code/tests following Phase 5 workflow
         2. If this is a test task, use TDD approach
         3. Verify ALL subtasks meet acceptance criteria
         4. Verify quality standards (lint/type/test)
         5. If live application: run and test, capture screenshots
         6. Apply 3-try limit for quality fixes
         7. DO NOT commit (orchestrator handles commits)
         8. Return results with:
            - Status: "success" or "failed"
            - Files modified: [list of file paths]
            - Decisions made: [key implementation decisions]
            - Issues encountered: [if any]
            - Screenshots: [if applicable]
   ```

   For parallel tasks [P]:
   ```
   Queue all [P] tasks
   While queue not empty and active < 3:
     Launch next DEV instance with context package
     Track as active

   As each DEV completes:
     Process results (see step 8)
     Launch next queued task if available
   ```

8. **Process DEV results** (streaming):
   ```
   For each completed DEV instance:
     - If status = "failed":
       * HALT all execution immediately
       * Cancel any pending DEV instances
       * Present failure report:
         - Task that failed
         - What was attempted
         - Why it failed
         - Files modified before failure
         - Recommended next steps
       * EXIT command

     - If status = "success":
       * Mark task as [X] in tasks.md
       * Log to decisions.md:
         - Task ID and description
         - Files modified
         - Key decisions made
         - Any issues encountered
       * Store files modified for commit step
       * Continue to next task
   ```

9. **Phase boundary reached** (all tasks in phase complete):
   ```
   A. Create sequential commits:
      For each completed task in phase order:
        git add [files modified by this task]
        git commit -m "[Task ID]: [Task description]

        🤖 Generated with [Claude Code](https://claude.com/claude-code)

        Co-Authored-By: Claude <noreply@anthropic.com>"

   B. Run phase-level quality verification:
      - Run full test suite: [test command]
      - Check coverage: [coverage requirement]
      - Run linting: [lint command]
      - Run type check: [typecheck command]
      - If any fail: HALT, report issues

   C. Present phase summary:
      **Phase [Name] Complete**
      - Tasks completed: [count]/[total]
      - Commits created: [count]
      - Key decisions:
        [Aggregated decisions from all tasks]
      - Quality metrics:
        * Tests: [pass/fail count]
        * Coverage: [percentage]
        * Lint: [pass/fail]
        * Type check: [pass/fail]
      - Issues encountered:
        [Any non-blocking issues]
   ```

10. **Move to next phase** or proceed to final verification

## Final Verification (Phase 6)

11. **Run comprehensive verification**:
    ```
    Checklist:
    - [ ] All tasks marked [X] in tasks.md
    - [ ] All tests pass: [run test command]
    - [ ] Coverage meets requirements: [check coverage]
    - [ ] No linting errors: [run lint command]
    - [ ] No type errors: [run typecheck command]
    - [ ] Implementation matches spec.md (review FR-XXX requirements)
    - [ ] Implementation follows plan.md architecture
    - [ ] No partial implementations
    - [ ] Commit history is clean and atomic
    - [ ] Git log shows one commit per task
    ```

    If any fail: HALT, report specific failures

## Finalization (Phase 7)

12. **Present comprehensive completion summary**:
    ```markdown
    # Implementation Complete

    ## Tasks Completed
    [For each task:]
    - [Task ID]: [Description] (Commit: [hash])

    ## Implementation Decisions
    [Aggregated from all DEV instances:]
    - [Decision 1 with context]
    - [Decision 2 with context]
    ...

    ## Quality Metrics
    - Tests: [X passed, Y total]
    - Coverage: [percentage] (requirement: [requirement])
    - Linting: [pass/fail with details]
    - Type Check: [pass/fail with details]
    - Build: [pass/fail]

    ## Proof of Functionality
    [Screenshots from live testing, if applicable]

    ## Deviations from Plan
    [Any changes from plan.md with justifications]

    ## Known Issues / Future Work
    [Any limitations or recommended follow-ups]
    ```

13. **Wait for user verification**

14. **Handle user feedback**:
    ```
    If user provides feedback:
      Ask: "Would you like me to iterate on the implementation?"

      If user confirms yes:
        → Proceed to Phase 8 (Iteration)

      If user confirms no:
        → Implementation complete, exit command
    ```

## Iteration (Phase 8)

15. **Analyze feedback and determine scope**:
    ```
    - Parse user feedback
    - Categorize changes:
      * Minor fixes → update specific tasks in tasks.md
      * New functionality → create new tasks in tasks.md
      * Architectural changes → may require /plan revision, escalate to user
    ```

16. **Update tasks.md**:
    ```
    For minor fixes:
      - Reopen affected tasks (change [X] back to [ ])
      - Update task descriptions if needed

    For new functionality:
      - Add new tasks to appropriate phase
      - Mark dependencies
    ```

17. **Return to Phase 1-5 execution loop**:
    ```
    - Execute updated/new tasks using same DEV invocation pattern
    - Follow all quality verification steps
    - Create commits for changes
    ```

18. **After iteration changes complete**:
    ```
    - Return to Phase 6 (Final Verification)
    - Run full verification checklist
    - Present updated completion summary
    - Wait for user verification again
    - Repeat until user confirms satisfaction
    ```

## Error Handling

**Git State Errors**:
- Dirty working tree → fail with clear message
- Merge conflicts → fail, ask user to resolve

**Context Errors**:
- Missing required files → fail with specific file names
- Quality standards not found → fail with "CLARIFICATION REQUIRED"
- Malformed tasks.md → fail with parsing error details

**Execution Errors**:
- DEV failure after 3 tries → halt, present detailed status
- Quality verification failure → halt, show specific failures
- Test failures → halt, show test output

**Recovery**:
- All halts provide clear next steps
- User can fix issues and re-run /implement
- Command is idempotent: can resume from where it stopped
```

### 3. /plan Command Enhancement

**File**: `.claude/commands/plan.md`

**Addition**: Ensure quality standards are included in plan.md output

**New Section in Plan Template**:
```markdown
## Quality Standards

### Linting
- Command: [e.g., `npm run lint` or `ruff check .`]
- Standard: Zero errors, zero warnings

### Type Checking
- Command: [e.g., `tsc --noEmit` or `mypy .`]
- Standard: Zero errors, zero warnings

### Testing
- Test Command: [e.g., `npm test` or `pytest`]
- Coverage Command: [e.g., `npm run coverage` or `pytest --cov`]
- Coverage Requirement: [e.g., 80% or CLARIFICATION REQUIRED]

### Build
- Build Command: [e.g., `npm run build` or `python -m build`]
- Standard: Successful build with no errors
```

**Auto-Discovery Logic** (if standards not explicitly defined):
```markdown
During /plan execution:

1. Check for quality standard commands in:
   - package.json (scripts: test, lint, typecheck, build)
   - pyproject.toml (tool.pytest, tool.ruff, tool.mypy)
   - Makefile (test, lint, typecheck targets)
   - .github/workflows (CI configuration)

2. If found: populate Quality Standards section automatically

3. If not found: add "CLARIFICATION REQUIRED" markers:
   ```
   ## Quality Standards

   **CLARIFICATION REQUIRED**: Please specify quality standard commands

   ### Linting
   - Command: CLARIFICATION REQUIRED

   ### Type Checking
   - Command: CLARIFICATION REQUIRED (or N/A if not applicable)

   ### Testing
   - Test Command: CLARIFICATION REQUIRED
   - Coverage Requirement: CLARIFICATION REQUIRED
   ```
```

### 4. /tasks Command Enhancement

**File**: `.claude/commands/tasks.md`

**Addition**: Ensure tasks include subtasks as acceptance criteria

**Enhanced Task Template**:
```markdown
### Phase: [Phase Name]

**T001** [Task Description] (`path/to/file.ext`)
- [ ] Subtask 1: [Specific acceptance criterion]
- [ ] Subtask 2: [Specific acceptance criterion]
- [ ] Subtask 3: [Specific acceptance criterion]
- Dependencies: [Task IDs or "None"]
- Implements: [FR-XXX references from spec.md]

**T002** [P] [Task Description] (`path/to/file.ext`)
- [ ] Subtask 1: [Specific acceptance criterion]
- [ ] Subtask 2: [Specific acceptance criterion]
- Dependencies: None (parallel safe)
- Implements: [FR-XXX references from spec.md]
```

**Guidance for Task Generation**:
```markdown
When generating tasks:

1. Each task should be atomic (single file or tightly coupled files)
2. Include 2-5 subtasks as acceptance criteria
3. Subtasks should be:
   - Specific and measurable
   - Functional (what works, not how it's built)
   - Testable (can be verified)
4. Mark parallel-safe tasks with [P]
5. Always include FR-XXX references from spec.md
6. Group by phases: Setup, Tests, Core, Integration, Polish
```

### 5. Prerequisites Check Script Enhancement

**File**: `.specify/scripts/bash/check-prerequisites.sh`

**Addition**: Git state validation option

**New Flag**: `--check-git-state`

**Implementation**:
```bash
# Add to script
if [ "$CHECK_GIT_STATE" = true ]; then
  if [ -n "$(git status --porcelain)" ]; then
    if [ "$JSON_OUTPUT" = true ]; then
      echo '{"error": "Working tree is not clean", "status": "failed"}'
    else
      echo "ERROR: Working tree is not clean. Commit or stash changes before implementation."
      git status --short
    fi
    exit 1
  fi
fi
```

### 6. File Structure Changes

**New Files to Create**:
- `.claude/agents/dev.md` (moved from final/dev.md with modifications)

**Files to Modify**:
- `.claude/commands/implement.md` (complete rewrite per spec above)
- `.claude/commands/plan.md` (add quality standards section)
- `.claude/commands/tasks.md` (add subtask template and guidance)
- `.specify/scripts/bash/check-prerequisites.sh` (add git state check)

**Files to Keep**:
- `docs/implement-dev-integration-analysis.md` (reference documentation)
- `docs/implement-dev-integration-proposal.md` (this document)
- `docs/implement-dev-integration-research.md` (reference documentation)

---

## Next Steps

This proposal is now complete with all decisions finalized and technical specifications detailed. The recommended implementation path is:

### Phase 1: Foundation Setup
1. **Create DEV sub-agent** (`.claude/agents/dev.md`)
   - Move `final/dev.md` to `.claude/agents/dev.md`
   - Add YAML frontmatter with model and tool specifications
   - Remove Phase 1-4 (orchestrator responsibilities)
   - Update Phase 5 to remove commit logic
   - Update Phase 7 to return results instead of waiting for user
   - Add "Context Package" section

2. **Enhance prerequisites script**
   - Add `--check-git-state` flag to `.specify/scripts/bash/check-prerequisites.sh`
   - Implement git clean state validation

### Phase 2: Planning Command Updates
3. **Update /plan command**
   - Add Quality Standards section to plan.md template
   - Implement auto-discovery logic for quality commands
   - Add "CLARIFICATION REQUIRED" fallback

4. **Update /tasks command**
   - Enhance task template to include subtasks as acceptance criteria
   - Add guidance for task generation (2-5 subtasks, FR-XXX references)
   - Ensure parallel tasks marked [P]

### Phase 3: Implementation Command Rewrite
5. **Rewrite /implement command** (`.claude/commands/implement.md`)
   - Implement Phase 0: Pre-execution (prerequisites, git check, context loading)
   - Implement Phase 1-5: Task execution loop with DEV sub-agent invocation
   - Implement Phase 6: Final verification checklist
   - Implement Phase 7: Comprehensive completion summary
   - Implement Phase 8: Iteration protocol
   - Add error handling for all scenarios

### Phase 4: Testing & Validation
6. **Test with simple feature**
   - Create minimal spec/plan/tasks for testing
   - Run through full /implement workflow
   - Verify sub-agent invocation works correctly
   - Verify quality gates function properly
   - Verify commit strategy (sequential at phase boundaries)

7. **Test with complex feature**
   - Include parallel tasks [P]
   - Include TDD workflow (tests before implementation)
   - Include live application testing with screenshots
   - Test failure scenarios and halt behavior
   - Test iteration protocol

8. **Test edge cases**
   - Missing context files
   - Dirty git state
   - Quality standard failures
   - DEV sub-agent failures after 3 tries

### Phase 5: Documentation & Rollout
9. **Update project documentation**
   - Document new /implement workflow in README or docs
   - Document DEV sub-agent usage
   - Provide examples of tasks.md with subtasks
   - Provide examples of plan.md with quality standards

10. **Training & Adoption**
    - Share updated workflow with team
    - Demonstrate end-to-end usage
    - Gather feedback for refinements

### Success Criteria

Implementation is complete when:
- ✅ DEV sub-agent successfully invoked from /implement
- ✅ Context packages correctly prepared and extracted
- ✅ Parallel execution limited to 3 concurrent instances
- ✅ Phase boundary commits created atomically
- ✅ Quality verification gates enforced
- ✅ Comprehensive final summary presented
- ✅ Iteration protocol functional
- ✅ All error scenarios handled gracefully
- ✅ Test feature implemented end-to-end successfully

### Timeline Estimate

- **Phase 1-2** (Foundation & Planning): 2-4 hours
- **Phase 3** (Implementation Rewrite): 4-6 hours
- **Phase 4** (Testing): 3-4 hours
- **Phase 5** (Documentation): 1-2 hours

**Total Estimated Time**: 10-16 hours

### Dependencies

- Claude Code sub-agent architecture (already available)
- Spec Kit framework (already in place)
- Task tool for sub-agent invocation (already available)
- Browser MCP for verification (already available)

### Risks & Mitigations

**Risk**: Sub-agent context window limitations
- *Mitigation*: Smart context extraction (Q1.1) keeps packages focused

**Risk**: Parallel execution coordination complexity
- *Mitigation*: Fixed limit of 3, streaming results, sequential commits

**Risk**: Quality gate failures blocking progress
- *Mitigation*: Halt-and-present strategy with clear next steps

**Risk**: DEV sub-agent misinterpretation of tasks
- *Mitigation*: Comprehensive context packages with explicit guardrails

---

## Approval & Sign-off

**Proposal Status**: ✅ Complete - Ready for Implementation

**Decisions Finalized**: 18/18

**Next Action**: Proceed to Phase 1 implementation or request final review/approval
