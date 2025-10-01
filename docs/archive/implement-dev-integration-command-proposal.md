# Agents Library Installation & Integration Proposal

**Status**: Draft Proposal
**Created**: 2025-10-01
**Updated**: 2025-10-01
**Purpose**: Create a distributable agents library that can be installed into any project, with optional Spec Kit integration

---

## Executive Summary

This proposal outlines an **agents library package** that can be installed into any project using `uvx` (similar to GitHub Spec Kit). The library provides reusable AI agents (starting with DEV) and detects existing tooling (like Spec Kit) to offer optional integrations.

**Key Insight**: A distributable library with intelligent detection is more flexible than a single-purpose integration tool. Users can install agents à la carte and get contextual integration options based on their project setup.

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│         Agents Library (uvx installable)            │
│  - Core agents (DEV, QA, DOCS, etc.)               │
│  - Detection logic (Spec Kit, custom setups)       │
│  - Integration commands (optional)                  │
└─────────────────────────────────────────────────────┘
                          │
                          ├─ uvx install command
                          ↓
┌─────────────────────────────────────────────────────┐
│              User's Project                         │
│  .claude/agents/        ← Selected agents installed │
│  .claude/commands/      ← Optional integrations     │
└─────────────────────────────────────────────────────┘
```

### Installation Flow

```
1. User runs: uvx agents-library init my-project

2. Library detects project environment:
   - Check for .claude/ directory
   - Check for Spec Kit (.specify/)
   - Check for other AI tooling

3. Interactive agent selection:
   "Which agents would you like to install?"
   [ ] DEV - Quality-focused implementation agent
   [ ] QA - Testing and validation agent
   [ ] DOCS - Documentation agent
   [x] All agents

4. Install selected agents to .claude/agents/

5. Conditional integration offers:
   IF Spec Kit detected:
     "Spec Kit detected! Would you like to integrate DEV agent
      with Spec Kit's /implement command?"
     → If yes: Install /integrate-dev command

6. Complete with summary and next steps
```

**Key Insight**: A prescriptive, intelligent installation process is more maintainable than a version-locked migration script, as it can adapt to different project setups and user preferences.

---

## Problem Statement

### Current Challenge
Teams want to use proven AI agents across multiple projects, but face:

1. **No reusable agent library**: Agents are project-specific, not portable
2. **Manual setup complexity**: Copy-paste agents, commands across projects
3. **Integration friction**: Hard to combine agents with existing tools (Spec Kit, etc.)
4. **Version management**: No easy way to update agents across projects
5. **Discovery challenge**: Teams don't know what agents are available

### Why Not Manual Installation?
- ❌ Error-prone copy-paste process
- ❌ No version tracking or updates
- ❌ Miss integration opportunities (e.g., Spec Kit + DEV)
- ❌ Inconsistent setup across projects
- ❌ No centralized agent library

### The Solution: Distributable Agents Library
✅ **uvx-based installation**: Similar to Spec Kit, familiar pattern
✅ **Agent marketplace**: Browse and select agents to install
✅ **Smart detection**: Discovers project setup, offers relevant integrations
✅ **Version management**: Update commands to refresh agents
✅ **Modular approach**: Install only what you need

---

## Library Specification

### Package Name
`agents-library` (or `@yourorg/agents-library` for scoped package)

### Installation Command
```bash
# One-time usage
uvx agents-library init my-project

# Persistent installation
uv tool install agents-library --from git+https://github.com/yourorg/agents-library.git

# Then use globally
agents-library init my-project
```

### Library Structure
```
agents-library/
├── agents/           # Agent definitions
│   ├── dev.md
│   ├── qa.md
│   └── docs.md
├── integrations/     # Integration commands
│   └── spec-kit/
│       └── integrate-dev.md
├── templates/        # Reusable templates
├── scripts/          # Setup and utility scripts
│   ├── detect.py     # Environment detection
│   └── install.py    # Installation logic
└── cli.py            # Main CLI entry point
```

### CLI Commands

**`agents-library init <project>`** - Initialize agents in a project
- Detects environment
- Interactive agent selection
- Installs to .claude/agents/
- Offers integrations based on detection

**`agents-library list`** - List available agents
- Shows all agents with descriptions
- Indicates which are installed

**`agents-library update`** - Update installed agents
- Checks for newer versions
- Updates agent definitions
- Preserves customizations (asks before overwriting)

**`agents-library integrate`** - Manually trigger integrations
- Shows available integrations
- User selects which to apply

### Scope
Multi-project tool (install once, use everywhere)

---

## Functional Requirements

### FR-001: Detect Project Environment
**Priority**: Critical
**Description**: Library must detect and understand the project setup

**Acceptance Criteria**:
- [ ] Detect `.claude/` directory (create if missing)
- [ ] Detect `.specify/` directory (Spec Kit)
- [ ] Detect other AI tooling (Copilot config, etc.)
- [ ] Identify Spec Kit version (if present)
- [ ] Report current project configuration
- [ ] Work with or without existing tooling

### FR-002: Interactive Agent Selection
**Priority**: Critical
**Description**: Allow users to choose which agents to install

**Acceptance Criteria**:
- [ ] Display available agents with descriptions
- [ ] Support multi-select (checkboxes)
- [ ] Support "all agents" option
- [ ] Show agent size/complexity
- [ ] Validate selections before proceeding

### FR-003: Install Selected Agents
**Priority**: Critical
**Description**: Copy selected agent definitions to project

**Acceptance Criteria**:
- [ ] Read agent definitions from library
- [ ] Copy to `.claude/agents/` directory
- [ ] Preserve YAML frontmatter and formatting
- [ ] Handle existing agents (ask to overwrite or skip)
- [ ] Set appropriate file permissions

### FR-004: Conditional Integration Offers
**Priority**: High
**Description**: Detect compatible tooling and offer relevant integrations

**Acceptance Criteria**:
- [ ] IF Spec Kit detected AND DEV agent selected:
  - Offer to install `/integrate-dev` command
  - Explain what the integration does
  - Wait for user confirmation
- [ ] Support future integrations (QA + testing frameworks, etc.)
- [ ] Install integration commands to `.claude/commands/`
- [ ] Provide integration documentation

### FR-005: Analyze Current State (for Spec Kit integration)
**Priority**: Medium
**Description**: Analyze existing Spec Kit files to understand customizations

**Acceptance Criteria**:
- [ ] Read existing `/implement` command (if exists)
- [ ] Read existing `/plan` command (if exists)
- [ ] Read existing `/tasks` command (if exists)
- [ ] Identify any customizations or deviations from standard Spec Kit
- [ ] Report findings to user

### FR-004: Interactive Confirmation
**Priority**: High
**Description**: Command must get user approval before making changes

**Acceptance Criteria**:
- [ ] Present summary of changes to be made
- [ ] List files to be created
- [ ] List files to be modified
- [ ] Show backup strategy
- [ ] Wait for explicit user confirmation

### FR-005: Create DEV Sub-Agent
**Priority**: Critical
**Description**: Create `.claude/agents/dev.md` from `final/dev.md`

**Acceptance Criteria**:
- [ ] Read `final/dev.md`
- [ ] Add required YAML frontmatter (model, tools)
- [ ] Remove Phase 1-4 (orchestrator responsibilities)
- [ ] Update Phase 5 (remove commit logic)
- [ ] Update Phase 7 (return results to orchestrator)
- [ ] Add "Context Package" section
- [ ] Write to `.claude/agents/dev.md`
- [ ] Validate YAML syntax

### FR-006: Update /implement Command
**Priority**: Critical
**Description**: Rewrite `/implement` command to use DEV sub-agent integration

**Acceptance Criteria**:
- [ ] Read existing `.claude/commands/implement.md`
- [ ] Preserve any project-specific customizations (if possible)
- [ ] Apply new structure from proposal (18-step workflow)
- [ ] Add Phase 0: Pre-execution validation
- [ ] Add Phase 1-5: DEV sub-agent invocation loop
- [ ] Add Phase 6: Final verification
- [ ] Add Phase 7: Comprehensive summary
- [ ] Add Phase 8: Iteration protocol
- [ ] Add error handling
- [ ] Write updated command
- [ ] Validate command syntax

### FR-007: Update /plan Command
**Priority**: High
**Description**: Enhance `/plan` command to include quality standards

**Acceptance Criteria**:
- [ ] Read existing `.claude/commands/plan.md`
- [ ] Add Quality Standards section to template
- [ ] Add auto-discovery logic for quality commands
- [ ] Add "CLARIFICATION REQUIRED" fallback
- [ ] Preserve existing plan template structure
- [ ] Write updated command

### FR-008: Update /tasks Command
**Priority**: High
**Description**: Enhance `/tasks` command to include subtasks as acceptance criteria

**Acceptance Criteria**:
- [ ] Read existing `.claude/commands/tasks.md`
- [ ] Update task template to include subtasks
- [ ] Add guidance for 2-5 subtasks per task
- [ ] Add FR-XXX reference requirements
- [ ] Preserve existing task generation logic
- [ ] Write updated command

### FR-009: Update Prerequisites Script
**Priority**: Medium
**Description**: Add git state validation to prerequisites check script

**Acceptance Criteria**:
- [ ] Read existing `.specify/scripts/bash/check-prerequisites.sh`
- [ ] Add `--check-git-state` flag
- [ ] Implement git clean state validation
- [ ] Maintain backward compatibility
- [ ] Write updated script
- [ ] Validate bash syntax

### FR-010: Create Backups
**Priority**: Critical
**Description**: Backup all files before modification for rollback capability

**Acceptance Criteria**:
- [ ] Create `.integration-backup/` directory
- [ ] Timestamp backup directory
- [ ] Copy all files to be modified
- [ ] Create backup manifest (list of files)
- [ ] Report backup location to user

### FR-011: Validate Integration
**Priority**: High
**Description**: Validate that integration was applied correctly

**Acceptance Criteria**:
- [ ] Verify `.claude/agents/dev.md` exists and has valid YAML
- [ ] Verify updated commands have required sections
- [ ] Check for syntax errors in modified files
- [ ] Report validation results
- [ ] Fail if critical issues found

### FR-012: Report Changes
**Priority**: High
**Description**: Provide comprehensive report of what was changed

**Acceptance Criteria**:
- [ ] List all files created
- [ ] List all files modified
- [ ] Summarize key changes per file
- [ ] Show backup location
- [ ] Provide next steps for user

### FR-013: Rollback Capability
**Priority**: Medium
**Description**: Provide ability to rollback integration if needed

**Acceptance Criteria**:
- [ ] Detect backup directory
- [ ] Restore all files from backup
- [ ] Remove newly created files
- [ ] Report rollback success
- [ ] Clean up backup directory (optional)

### FR-014: Handle Edge Cases
**Priority**: Medium
**Description**: Gracefully handle unexpected scenarios

**Acceptance Criteria**:
- [ ] Handle missing source files (final/dev.md, proposal.md)
- [ ] Handle existing `.claude/agents/dev.md` (ask to overwrite)
- [ ] Handle heavily customized Spec Kit files
- [ ] Handle partial previous integration attempts
- [ ] Provide clear error messages and recovery steps

---

## Non-Functional Requirements

### NFR-001: Idempotency
**Description**: Command can be run multiple times safely
- Running on already-integrated project should detect and report
- Should offer to re-apply or update integration
- Should not corrupt existing integration

### NFR-002: Adaptability
**Description**: Command adapts to Spec Kit variations
- Works with different Spec Kit versions
- Handles customized Spec Kit installations
- Intelligently merges changes with existing customizations

### NFR-003: Clarity
**Description**: Command provides clear communication
- Progress updates during execution
- Clear error messages with context
- Actionable next steps
- Comprehensive final report

### NFR-004: Safety
**Description**: Command protects against data loss
- Always creates backups before changes
- Validates changes before finalizing
- Provides rollback mechanism
- Requires explicit user confirmation

### NFR-005: Maintainability
**Description**: Command is easy to update and maintain
- Well-documented logic and decisions
- Clear separation of concerns
- Easy to update when proposal changes
- Resilient to minor Spec Kit updates

---

## Command Workflow

### Phase 1: Discovery & Analysis
```
1. Validate environment
   - Check for Spec Kit installation (.specify/, .claude/commands/)
   - Check for required source files (final/dev.md, proposal.md)
   - Identify Spec Kit version (if possible)

2. Analyze current state
   - Read existing /implement, /plan, /tasks commands
   - Identify customizations
   - Check if DEV integration already exists

3. Read integration requirements
   - Parse implement-dev-integration-proposal.md
   - Extract file modification specs
   - Understand architectural decisions
```

### Phase 2: Planning & Confirmation
```
4. Generate integration plan
   - List files to create: [.claude/agents/dev.md]
   - List files to modify: [implement.md, plan.md, tasks.md, check-prerequisites.sh]
   - Identify any conflicts or issues
   - Determine backup strategy

5. Present plan to user
   - Show summary of changes
   - Show backup location
   - Highlight any risks or conflicts
   - Request explicit confirmation

6. Wait for user approval
   - If approved: proceed to Phase 3
   - If declined: exit gracefully
```

### Phase 3: Backup & Preparation
```
7. Create backup
   - Create .integration-backup-[timestamp]/
   - Copy all files to be modified
   - Create manifest.txt listing all backed up files
   - Report backup location

8. Prepare for integration
   - Validate write permissions
   - Ensure directories exist
   - Set up logging
```

### Phase 4: Integration Execution
```
9. Create DEV sub-agent
   - Read final/dev.md
   - Add YAML frontmatter (name: DEV, model: claude-sonnet-4-5, tools: [Read, Write, Edit, Bash, Glob, Grep, mcp__browser__*])
   - Remove Phase 1-4 sections
   - Update Phase 5 (remove commit steps)
   - Update Phase 7 (return results instead of user wait)
   - Add Context Package section
   - Write to .claude/agents/dev.md

10. Update /implement command
    - Read existing .claude/commands/implement.md
    - Apply new 18-step workflow from proposal
    - Preserve project-specific customizations if possible
    - Add all phases (0-8) as specified
    - Write updated command

11. Update /plan command
    - Read existing .claude/commands/plan.md
    - Add Quality Standards section with auto-discovery
    - Preserve existing template structure
    - Write updated command

12. Update /tasks command
    - Read existing .claude/commands/tasks.md
    - Add subtask template (2-5 subtasks per task)
    - Add FR-XXX reference guidance
    - Preserve existing logic
    - Write updated command

13. Update prerequisites script
    - Read existing .specify/scripts/bash/check-prerequisites.sh
    - Add --check-git-state flag implementation
    - Maintain backward compatibility
    - Write updated script
```

### Phase 5: Validation & Reporting
```
14. Validate integration
    - Check .claude/agents/dev.md has valid YAML
    - Check all commands have required sections
    - Run basic syntax validation
    - Identify any issues

15. Generate integration report
    - Files created: [list with line counts]
    - Files modified: [list with summary of changes]
    - Customizations preserved: [list if any]
    - Issues encountered: [list if any]
    - Backup location: [path]

16. Present report to user
    - Show comprehensive summary
    - Highlight any warnings
    - Provide next steps:
      * Test integration with a simple feature
      * Review modified files
      * Run /implement on test feature
      * Rollback if needed: [command]
```

### Phase 6: Post-Integration (Optional)
```
17. Offer rollback if issues detected
    - If validation failed: recommend rollback
    - Provide rollback command

18. Clean up (optional)
    - Offer to remove backup after user confirms success
    - Log integration completion
```

---

## Command Implementation Structure

### File: `.claude/commands/integrate-dev.md`

```markdown
# /integrate-dev - Integrate DEV Agent into Spec Kit

Intelligently integrate DEV agent quality-focused methodology into your Spec Kit installation.

## What This Does

This command applies the DEV agent integration proposal to your Spec Kit project:
- Creates DEV sub-agent (.claude/agents/dev.md)
- Updates /implement command with quality-focused workflow
- Enhances /plan command with quality standards
- Updates /tasks command with subtask acceptance criteria
- Adds git state validation to prerequisites

## Prerequisites

Required files:
- `final/dev.md` (DEV agent definition)
- `docs/implement-dev-integration-proposal.md` (integration specification)
- Existing Spec Kit installation (.specify/, .claude/commands/)

## Safety Features

- ✅ Creates timestamped backups before changes
- ✅ Validates integration after application
- ✅ Provides rollback capability
- ✅ Requires explicit user confirmation
- ✅ Adapts to customizations

## Execution

### Phase 1: Discovery & Analysis

[Detailed steps as outlined in workflow above]

### Phase 2: Planning & Confirmation

[Detailed steps as outlined in workflow above]

### Phase 3: Backup & Preparation

[Detailed steps as outlined in workflow above]

### Phase 4: Integration Execution

[Detailed steps as outlined in workflow above]

### Phase 5: Validation & Reporting

[Detailed steps as outlined in workflow above]

### Phase 6: Post-Integration

[Detailed steps as outlined in workflow above]

## Rollback

If integration fails or you need to revert:

```bash
# Manual rollback from backup
cp -r .integration-backup-[timestamp]/* .
```

Or re-run: `/integrate-dev --rollback [timestamp]`

## Troubleshooting

**Issue**: Spec Kit not detected
- **Solution**: Ensure .specify/ and .claude/commands/ directories exist

**Issue**: Source files missing
- **Solution**: Ensure final/dev.md and docs/implement-dev-integration-proposal.md exist

**Issue**: Integration validation failed
- **Solution**: Review validation errors, check for syntax issues, consider rollback

**Issue**: Conflicts with customizations
- **Solution**: Review backup, manually merge customizations with new structure
```

---

## Alternative Implementations

### Option A: Single Monolithic Command
**What**: One large command with all logic inline
- **Pros**: Self-contained, no dependencies
- **Cons**: Hard to maintain, less flexible

### Option B: Multi-Step Interactive Wizard
**What**: Series of prompts guiding user through integration
- **Pros**: User-friendly, educational
- **Cons**: More complex, slower

### Option C: Hybrid with Sub-Commands
**What**: Main command with sub-commands for each phase
- **Pros**: Modular, can run phases independently
- **Cons**: More files, more complexity

**Recommendation**: **Option A (Single Monolithic Command)** with clear phase separation
- Easier to maintain (one file)
- Claude Code can handle complexity
- User gets simple single-command experience

---

## Testing Strategy

### Test Case 1: Fresh Spec Kit Installation
**Setup**: Clean Spec Kit project, no customizations
**Expected**: Integration applies cleanly, all files created/modified correctly

### Test Case 2: Customized Spec Kit
**Setup**: Spec Kit with custom /implement logic
**Expected**: Integration preserves customizations where possible, reports conflicts

### Test Case 3: Already Integrated Project
**Setup**: Project with DEV integration already applied
**Expected**: Detects existing integration, offers to update or skip

### Test Case 4: Missing Source Files
**Setup**: Missing final/dev.md or proposal.md
**Expected**: Clear error message, graceful exit

### Test Case 5: Rollback Scenario
**Setup**: Integration applied, then rollback requested
**Expected**: All files restored from backup, integration removed

### Test Case 6: Different Spec Kit Version
**Setup**: Older/newer Spec Kit version with different structure
**Expected**: Adapts to structure differences, applies integration intelligently

---

## Maintenance Plan

### When to Update Command

1. **Proposal Changes**: When implement-dev-integration-proposal.md is updated
   - Update command to reflect new specifications
   - Test with existing integrations

2. **Spec Kit Updates**: When Spec Kit releases new version
   - Test command with new version
   - Update file path assumptions if needed
   - Update detection logic if structure changed

3. **User Feedback**: When issues are reported
   - Add edge case handling
   - Improve error messages
   - Enhance validation logic

### Version Tracking

Add version to command frontmatter:
```yaml
---
name: integrate-dev
version: 1.0.0
compatible_with_proposal: 2025-10-01
last_updated: 2025-10-01
---
```

### Documentation Updates

Maintain:
- Changelog of command updates
- Compatibility matrix (Spec Kit versions)
- Known issues and workarounds
- Migration guide for manual fixes

---

## Success Metrics

Integration is successful when:
- ✅ All 6 files created/modified without errors
- ✅ YAML frontmatter in dev.md is valid
- ✅ Commands have all required sections
- ✅ Validation checks pass
- ✅ User can run /implement with DEV sub-agent
- ✅ Test feature implements successfully
- ✅ Quality gates enforce properly
- ✅ Rollback works if needed

---

## Timeline Estimate

**Command Development**: 4-6 hours
- Phase 1-2 (Discovery/Planning): 1 hour
- Phase 3-4 (Backup/Execution): 2-3 hours
- Phase 5-6 (Validation/Reporting): 1 hour
- Testing & Refinement: 1-2 hours

**Total**: 4-6 hours to production-ready command

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Spec Kit structure changes significantly | High | Medium | Adaptive logic, version detection |
| Customizations conflict with integration | Medium | High | Backup + rollback, conflict reporting |
| Source files missing/corrupted | High | Low | Pre-flight validation, clear errors |
| Integration partially applied | Medium | Low | Atomic operations where possible, validation |
| User regrets integration | Low | Medium | Easy rollback, clear documentation |

---

## Approval & Next Steps

**Proposal Status**: ✅ Complete - Ready for Review

**Recommended Next Action**:
1. Review this proposal
2. Approve/request modifications
3. Implement `/integrate-dev` command
4. Test with sample Spec Kit project
5. Document usage and rollback procedures

**Dependencies**:
- `final/dev.md` (source for DEV sub-agent)
- `docs/implement-dev-integration-proposal.md` (integration spec)
- Existing Spec Kit installation

**Deliverable**:
`.claude/commands/integrate-dev.md` - Production-ready integration command
