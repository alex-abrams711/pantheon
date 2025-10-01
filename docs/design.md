# Simple DEV Agent Integration Proposal

**Status**: Draft Proposal
**Created**: 2025-10-01
**Purpose**: Drastically simplified approach to integrating DEV agent with Spec Kit

---

## Executive Summary

This proposal takes a minimalist approach to DEV agent integration: copy the agent file to `.claude/agents/`, then use a simple `/integrate-agents` command to add minimal directives to Spec Kit commands.

**Key Principle**: Don't rewrite commands. Just tell them to use the agent.

---

## Problem with Previous Approach

The original integration proposal was overly complex:
- Complex file merging logic
- Heuristic customization detection
- Interactive review of every change
- Manifest tracking
- Version management
- 21+ decision points

**Reality**: We don't need to rewrite `/implement`. We just need to tell it to use DEV.

---

## Simplified Architecture

### Library Distribution Model

**Package**: Python package installable via uvx (like Spec Kit)

**Installation**:
```bash
# One-time usage
uvx agents-library init

# Or install globally
uv tool install agents-library
agents-library init
```

**Workflow**:
```
┌─────────────────────────────────────────────────────────┐
│  Step 1: Install agents library                         │
│  uvx agents-library init                                │
│                                                          │
│  → Detects .claude/ directory (or creates it)          │
│  → Copies agents to .claude/agents/                     │
│  → Detects Spec Kit (if present)                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Step 2: Integrate with Spec Kit (if detected)         │
│  "Spec Kit detected. Integrate DEV with /implement?"    │
│  → If yes: runs integration automatically               │
│  → If no: agents installed, integration skipped         │
└─────────────────────────────────────────────────────────┘
```

### Library Structure

```
agents-library/
├── agents/              # Agent definitions
│   ├── dev.md
│   ├── qa.md
│   └── docs.md
├── integrations/        # Integration logic
│   └── spec-kit.py      # Spec Kit integration
├── cli.py               # Main CLI
└── pyproject.toml       # Package config
```

---

## Implementation Details

### CLI Commands

**`agents-library init`** - Initialize agents in project
- Detects or creates `.claude/agents/` directory
- Copies agent files from library to project
- Detects Spec Kit installation
- Offers integration if Spec Kit found

**`agents-library integrate`** - Add Spec Kit integration directives
- Backs up existing commands
- Inserts minimal directives into `/implement`, `/plan`, `/tasks`
- Validates changes
- Reports results

**`agents-library rollback`** - Revert integration
- Restores from most recent backup
- Removes integration directives
- Clean rollback to pre-integration state

**`agents-library list`** - Show available agents
- Lists agents in library
- Shows which are installed locally

### Step 1: Agent Installation (via uvx)

**Command**: `uvx agents-library init`

**What it does**:
1. Checks for `.claude/` directory (creates if missing)
2. Creates `.claude/agents/` directory
3. Copies `dev.md` from library to `.claude/agents/dev.md`

**Modifications needed**:
- Add YAML frontmatter:
  ```yaml
  ---
  name: DEV
  description: Senior Software Engineer focused on implementing features with quality-focused approach
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
- Remove Phase 1-4 (orchestrator responsibilities)
- Update Phase 5 to remove commit logic (orchestrator handles commits)
- Update Phase 7 to return results instead of waiting for user
- Add "Context Package" section explaining what DEV receives from orchestrator

**That's it. One file copy with minor modifications.**

---

### Step 2: Spec Kit Integration (via CLI)

**Command**: `agents-library integrate` (or auto-prompted after `init`)

**What it does**: Adds minimal integration directives to Spec Kit commands

**Detection**: Checks for `.specify/` directory and `.claude/commands/` to confirm Spec Kit presence

**For `/implement` command**, add this section at the beginning:

```markdown
## Agent Integration

**DEV Agent**: All task execution is delegated to the DEV sub-agent.

When executing tasks:
1. For each task in tasks.md, prepare a context package containing:
   - Task ID, description, and file paths
   - Relevant spec requirements (FR-XXX references)
   - Quality standards from plan.md (lint/type/test commands)
   - Subtasks as acceptance criteria
   - Tech stack constraints

2. Invoke DEV sub-agent using Task tool:
   ```
   Use Task tool:
     subagent_type: "dev"
     description: "Implement [Task ID]"
     prompt: [context package from above]
   ```

3. Process DEV results:
   - If success: mark task complete, log decisions, continue
   - If failure: halt, report status, wait for user

4. At phase boundaries: create sequential commits for completed tasks

See `.claude/agents/dev.md` for DEV's methodology and workflow.
```

**For `/plan` command**, add:

```markdown
## Quality Standards (Required for DEV Integration)

Include in plan.md output:
- Lint command (e.g., `npm run lint`)
- Type check command (e.g., `tsc --noEmit`)
- Test command (e.g., `npm test`)
- Coverage requirement (e.g., 80%)

If commands cannot be auto-discovered, mark as "CLARIFICATION REQUIRED".
```

**For `/tasks` command**, add:

```markdown
## Task Format (Required for DEV Integration)

Each task should include subtasks as acceptance criteria:

**T001** [Task Description] (`path/to/file.ext`)
- [ ] Subtask 1: [Specific acceptance criterion]
- [ ] Subtask 2: [Specific acceptance criterion]
- Dependencies: [Task IDs or "None"]
- Implements: [FR-XXX references]
```

---

## The Integration Process (Python CLI)

**Implementation**: `integrations/spec-kit.py`

### Integration Flow

```python
def integrate_spec_kit():
    """Add minimal directives to Spec Kit commands"""

    # 1. Prerequisites
    verify_agents_installed()  # Check .claude/agents/dev.md exists
    verify_spec_kit()          # Check .specify/ and .claude/commands/ exist

    # 2. Backup
    backup_dir = create_backup()  # .integration-backup-[timestamp]/

    # 3. Insert directives
    integrate_implement_command()  # Add DEV delegation directive
    integrate_plan_command()       # Add quality standards guidance
    integrate_tasks_command()      # Add subtask format guidance

    # 4. Validate
    validate_integration()         # Check files parseable, sections present

    # 5. Report
    print_integration_summary()    # Show what changed, backup location
```

### Key Functions

**`integrate_implement_command()`**:
- Reads `.claude/commands/implement.md`
- Inserts "Agent Integration" section after title
- Preserves all existing content
- Writes updated file

**`integrate_plan_command()`**:
- Reads `.claude/commands/plan.md`
- Inserts "Quality Standards" guidance section
- Writes updated file

**`integrate_tasks_command()`**:
- Reads `.claude/commands/tasks.md`
- Inserts "Task Format" guidance section
- Writes updated file

### Rollback Implementation

**Command**: `agents-library rollback`

```python
def rollback_integration():
    """Restore from most recent backup"""
    backup_dir = find_latest_backup()
    restore_files(backup_dir)
    print(f"Rolled back from {backup_dir}")
```

### Design Principles

- **Minimal changes**: Add directives, don't rewrite commands
- **Preserve existing logic**: All Spec Kit functionality remains
- **Clear boundaries**: Integration sections are clearly marked
- **Reversible**: Full rollback capability via backup

---

## What This Simplification Achieves

### ✅ Keeps
- Clear separation: agents define methodology, commands orchestrate
- Sub-agent invocation pattern (Task tool)
- Backup and rollback safety
- Quality-focused workflow from DEV agent

### ❌ Removes
- Complex file merging and customization detection
- Interactive review of every change
- Manifest tracking and version management
- Heuristic analysis
- 90% of the decision complexity

### 🎯 Result
- **2 files modified** (dev.md + integrate-agents.md) instead of 6+
- **Simple text insertion** instead of complex merging
- **One command** (`/integrate-agents`) instead of elaborate installation flow
- **5 minutes** to implement instead of days

---

## Agent File Structure

### Required: `.claude/agents/dev.md`

Structure:
```markdown
---
name: DEV
description: Senior Software Engineer focused on implementing features
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

## Core Principles
[DEV's competencies and standards]

## Context Package (Provided by Orchestrator)
[What DEV receives from /implement]

## Workflow

### Phase 5: Implement
[Code/test implementation with TDD]

### Phase 6: Verify
[Acceptance + quality verification]

### Phase 7: Report
[Return results to orchestrator]

### Phase 8: Iteration
[Handle feedback and rework]

## Quality Standards
[Testing, code quality, documentation]

## Guardrails
[NO PARTIAL IMPLEMENTATION, etc.]
```

---

## Integration Example

### Before Integration

`.claude/commands/implement.md`:
```markdown
# /implement - Execute Implementation Plan

Execute the implementation plan by processing tasks.

1. Load context (tasks.md, plan.md, spec.md)
2. For each task: [implementation logic]
3. Verify completion
```

### After Integration

`.claude/commands/implement.md`:
```markdown
# /implement - Execute Implementation Plan

## Agent Integration

**DEV Agent**: All task execution is delegated to the DEV sub-agent.

[Integration directive from above]

---

## Original Implementation

Execute the implementation plan by processing tasks.

1. Load context (tasks.md, plan.md, spec.md)
2. For each task: [implementation logic - now delegates to DEV]
3. Verify completion
```

**Key insight**: Original logic still there, just enhanced with agent delegation.

---

## Rollback Strategy

**Backup Creation**: Before any changes
```
.integration-backup-2025-10-01-14-30/
├── implement.md
├── plan.md
└── tasks.md
```

**Rollback Command**: `agents-library integrate --rollback`
- Detects most recent backup directory
- Restores all files
- Optionally removes backup after confirmation

**Safety**: All operations are file-based and reversible.

---

## Validation Strategy

After integration, verify:
1. ✅ YAML frontmatter in `dev.md` is valid
2. ✅ Integration sections present in each command
3. ✅ All files still parseable as markdown
4. ✅ No syntax errors introduced

**If validation fails**: Recommend rollback, show specific errors

---

## Implementation Checklist

- [ ] Create `.claude/agents/dev.md` from `final/dev.md`
  - [ ] Add YAML frontmatter
  - [ ] Remove Phase 1-4
  - [ ] Update Phase 5 (no commits)
  - [ ] Update Phase 7 (return results)
  - [ ] Add Context Package section

- [ ] Create `.claude/commands/integrate-agents.md`
  - [ ] Implement backup logic
  - [ ] Implement text insertion for each command
  - [ ] Implement validation
  - [ ] Implement rollback capability
  - [ ] Add clear status reporting

- [ ] Test integration
  - [ ] Fresh Spec Kit installation
  - [ ] Run `/integrate-agents`
  - [ ] Verify directives added correctly
  - [ ] Run `/implement` on test feature
  - [ ] Verify DEV agent invoked
  - [ ] Test rollback

---

## Timeline Estimate

- **Agent file preparation**: 30 minutes
- **Integration command creation**: 2 hours
- **Testing**: 1 hour
- **Documentation**: 30 minutes

**Total**: ~4 hours (vs. multiple days for complex approach)

---

## Success Criteria

Integration is successful when:
- ✅ DEV agent file exists in `.claude/agents/dev.md` with valid YAML
- ✅ `/implement` command invokes DEV sub-agent for task execution
- ✅ `/plan` command includes quality standards guidance
- ✅ `/tasks` command includes subtask format guidance
- ✅ Original Spec Kit functionality preserved
- ✅ Rollback works correctly
- ✅ Test feature implements successfully with DEV workflow

---

## Next Steps

1. ✅ Approve this simplified approach
2. Create `.claude/agents/dev.md` from `final/dev.md`
3. Implement `/integrate-agents` command
4. Test with sample Spec Kit project
5. Document usage

---

## Comparison: Complex vs Simple

| Aspect | Complex Approach | Simple Approach |
|--------|------------------|-----------------|
| Files modified | 6+ (rewrites) | 3 (text insertions) |
| Lines of code | ~2000+ | ~300 |
| Decision points | 21+ | 5 |
| Implementation time | Multiple days | ~4 hours |
| Maintenance burden | High | Low |
| Customization handling | Heuristics + review | Not needed |
| Version tracking | Manifest system | Not needed |
| User interaction | Multiple prompts | 2-3 prompts |
| Rollback complexity | High | Simple file restore |

**Winner**: Simple approach - 90% less complexity, same core value.

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Integration text breaks existing logic | Medium | Backup + rollback, careful insertion points |
| Users have customized commands | Medium | Fail safe if unexpected structure detected |
| DEV agent not invoked correctly | High | Validation checks, test before release |
| Rollback fails | Low | Simple file operations, tested thoroughly |

---

## Conclusion

This simplified approach achieves the core goal (DEV agent integration with Spec Kit) with 10% of the complexity. By focusing on minimal directives rather than command rewrites, we get:

- Faster implementation
- Easier maintenance
- Less to go wrong
- Clearer separation of concerns
- Preserves Spec Kit's existing logic

**Recommendation**: Proceed with this simplified approach immediately.
