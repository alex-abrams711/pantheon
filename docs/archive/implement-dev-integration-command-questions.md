# Agents Library Refinement Questions

**Purpose**: Identify critical decision points for finalizing the agents library and integration system
**Created**: 2025-10-01
**Updated**: 2025-10-01

**IMPORTANT CONTEXT**: This is now a **distributable agents library** (like Spec Kit) that:
1. Installs via `uvx agents-library init <project>`
2. Lets users select which agents to install
3. Detects Spec Kit and offers `/integrate-dev` command if relevant
4. Supports updates via `agents-library update`

---

## Round 0: Library Architecture (NEW)

### Q0.1: Library Package Structure

How should the library be structured and distributed?

**Options**:

- **Option A - Python package with uvx**: Following Spec Kit model
  - *Pros*: Familiar pattern, uvx handles dependencies
  - *Cons*: Python dependency, packaging complexity

- **Option B - Node.js package with npx**: JavaScript ecosystem
  - *Pros*: Wide adoption, npm ecosystem
  - *Cons*: Different from Spec Kit, Node dependency

- **Option C - Shell script with curl**: Minimal dependencies
  - *Pros*: No language runtime needed
  - *Cons*: Limited functionality, platform-specific

- **Option D - Go binary**: Single executable
  - *Pros*: No runtime, cross-platform
  - *Cons*: Build complexity, unfamiliar to some

**Recommendation**: ✅ **Option A - Python package with uvx**

**Decision Rationale**: Matches Spec Kit's distribution model (familiar to users), leverages existing Python toolchain, provides rich CLI capabilities, and makes integration with Spec Kit straightforward since both use the same ecosystem.

---

### Q0.2: Agent Storage in Library

Where should agents be stored within the library repository?

**Options**:

- **Option A - agents/ directory at root**: Simple, flat structure
  ```
  agents-library/
  ├── agents/
  │   ├── dev.md
  │   ├── qa.md
  │   └── docs.md
  ```

- **Option B - Categorized subdirectories**: Organized by type
  ```
  agents-library/
  ├── agents/
  │   ├── implementation/
  │   │   └── dev.md
  │   ├── quality/
  │   │   └── qa.md
  │   └── documentation/
  │       └── docs.md
  ```

- **Option C - Versioned agents**: Support multiple versions
  ```
  agents-library/
  ├── agents/
  │   ├── dev/
  │   │   ├── v1.md
  │   │   └── v2.md
  ```

**Recommendation**: ✅ **Option A - Flat agents/ directory**

**Decision Rationale**: Simple, clear, and sufficient for the initial agent library. Easy to refactor to categorized structure later if the library grows significantly. Version management can be handled at the package level rather than individual agent files.

---

### Q0.3: CLI Implementation Language

What language should the CLI be written in?

**Consideration**: Must match Q0.1 package structure choice

**Options**:

- **Option A - Python** (if uvx chosen)
  - *Pros*: Rich CLI libraries (click, typer), matches Spec Kit
  - *Cons*: Runtime dependency

- **Option B - JavaScript/TypeScript** (if npx chosen)
  - *Pros*: JSON handling, async, wide adoption
  - *Cons*: Runtime dependency

- **Option C - Shell** (if minimal chosen)
  - *Pros*: Universally available
  - *Cons*: Limited functionality

- **Option D - Go** (if binary chosen)
  - *Pros*: Single file, fast, cross-platform
  - *Cons*: Compile step, learning curve

**Recommendation**: ✅ **Option A - Python**

**Decision Rationale**: Must match Q0.1 decision (Python package with uvx). Python provides rich CLI libraries (click, typer), excellent file manipulation, YAML/Markdown parsing, and seamless integration with uvx distribution model. This is the only consistent choice given our package structure decision.

---

## Round 1: Installation Flow

### Q1.1: Agent Selection Interface

How should users select which agents to install?

**Options**:

- **Option A - Interactive menu**: Terminal UI with checkboxes
  ```
  Which agents would you like to install?
  [ ] DEV - Quality-focused implementation
  [ ] QA - Testing and validation
  [x] All agents
  ```
  - *Pros*: User-friendly, visual
  - *Cons*: Requires terminal UI library

- **Option B - Command flags**: `--agents dev,qa,docs` or `--all`
  - *Pros*: Scriptable, automation-friendly
  - *Cons*: Less discoverable, must know agent names

- **Option C - Interactive prompts**: Yes/no for each agent
  ```
  Install DEV agent? (y/n): y
  Install QA agent? (y/n): n
  ```
  - *Pros*: Simple, no UI library needed
  - *Cons*: Tedious for many agents

- **Option D - Hybrid**: Interactive by default, flags for automation
  - *Pros*: Best of both worlds
  - *Cons*: More implementation complexity

**Recommendation**: ✅ **Option D - Hybrid**

**Decision Rationale**: Interactive mode by default (good UX for discovery), with `--agents` flag for automation and power users. Provides flexibility without forcing one pattern. Python's typer library makes this straightforward to implement.

---

### Q1.2: Integration Offer Timing

When should Spec Kit integration be offered?

**Options**:

- **Option A - During init**: Immediately after agent selection
  ```
  Agents installed!
  Spec Kit detected. Integrate DEV with /implement? (y/n):
  ```
  - *Pros*: One-time setup, everything configured
  - *Cons*: May feel rushed

- **Option B - Separate command**: `agents-library integrate`
  ```
  # User runs later when ready
  agents-library integrate
  ```
  - *Pros*: User controls timing
  - *Cons*: Extra step, may be forgotten

- **Option C - Auto-detect and apply**: No prompting, just do it
  - *Pros*: Fastest, least friction
  - *Cons*: Assumes user wants integration

- **Option D - Post-install message**: Show instructions after init
  ```
  Agents installed!
  Tip: Run 'agents-library integrate' to connect DEV with Spec Kit
  ```
  - *Pros*: Informative, non-intrusive
  - *Cons*: Requires user action

**Recommendation**: ✅ **Option A - During init (with option to defer)**

**Decision Rationale**: Offer integration immediately after agent selection with a clear prompt: "Spec Kit detected. Integrate DEV with /implement? (y/n/later)". This completes the setup flow while respecting user control. The separate `agents-library integrate` command remains available for users who choose "later" or want to re-run integration.

---

### Q1.3: Update Mechanism

How should `agents-library update` work?

**Options**:

- **Option A - Update all**: Refresh all installed agents to latest
  - *Pros*: Simple, comprehensive
  - *Cons*: May overwrite customizations

- **Option B - Selective update**: Choose which agents to update
  - *Pros*: Granular control
  - *Cons*: More complex interface

- **Option C - Smart update**: Compare versions, only update if newer
  - *Pros*: Safe, automatic
  - *Cons*: Requires version tracking

- **Option D - Update + integrate**: Also update integration commands
  - *Pros*: Keeps everything in sync
  - *Cons*: Complex, may break customizations

**Recommendation**: ✅ **Option C - Smart update**

**Decision Rationale**: Compare versions, only update agents that have newer versions available. Show a summary of what will be updated before applying. Preserve customizations by detecting changes from baseline. Integration commands should be updated separately via `agents-library integrate --update` to give users explicit control over that more complex operation.

---

## Round 2: Customization Preservation

### Q2.1: Detecting Customizations

How should the command identify project-specific customizations in Spec Kit files?

**Options**:

- **Option A - Baseline comparison**: Compare against known Spec Kit baseline
  - *Pros*: Precise detection
  - *Cons*: Requires maintaining baseline, breaks with Spec Kit updates

- **Option B - Heuristic analysis**: Look for custom sections, non-standard patterns
  - *Pros*: Adaptive, doesn't require baseline
  - *Cons*: May miss subtle customizations

- **Option C - User declaration**: Ask user "have you customized /implement?"
  - *Pros*: Explicit, user knows best
  - *Cons*: Relies on user memory/knowledge

- **Option D - No detection**: Assume no customizations, warn user beforehand
  - *Pros*: Simple, clear expectations
  - *Cons*: May overwrite important customizations

**Recommendation**: ✅ **Option B - Heuristic analysis**

**Decision Rationale**: Look for custom sections, non-standard patterns, and deviations from typical Spec Kit structure. Python's text processing makes pattern detection feasible. This provides automatic protection without requiring baseline maintenance or user knowledge. Can flag potential customizations and ask for confirmation before proceeding.

---

### Q2.2: Handling Conflicts

When customizations conflict with integration requirements, what should the command do?

**Options**:

- **Option A - Fail safe**: Halt integration, report conflicts, ask for manual resolution
  - *Pros*: Safe, user control
  - *Cons*: Blocks automation, requires manual work

- **Option B - Intelligent merge**: Attempt to merge customizations with new structure
  - *Pros*: Automated, preserves work
  - *Cons*: Complex, may get wrong

- **Option C - Preserve + append**: Keep customizations, append new requirements
  - *Pros*: Nothing lost
  - *Cons*: May create redundancy or confusion

- **Option D - User choice per conflict**: Present each conflict, ask how to handle
  - *Pros*: User decides
  - *Cons*: Interactive, time-consuming

**Recommendation**: ✅ **Option A - Fail safe**

**Decision Rationale**: When customizations conflict with integration requirements, halt with a clear report showing what was detected and where conflicts exist. Provide guidance on resolution options (manual merge, rollback customizations, or skip integration). This ensures users never lose customizations and maintains working state.

---

### Q2.3: Customization Documentation

How should the command document what customizations were preserved/modified?

**Options**:

- **Option A - Detailed diff report**: Show before/after for each file
  - *Pros*: Complete transparency
  - *Cons*: Verbose, may overwhelm

- **Option B - Summary report**: List files changed and high-level changes
  - *Pros*: Concise, readable
  - *Cons*: May miss important details

- **Option C - Interactive review**: Let user review each change before applying
  - *Pros*: Full control
  - *Cons*: Slow, tedious for many changes

- **Option D - Git commit with detailed message**: Let git diff show changes
  - *Pros*: Uses standard tools
  - *Cons*: Requires git, may not be enough context

**Recommendation**: ✅ **Option C - Interactive review**

**Decision Rationale**: Let user review each change before applying. Show what will be modified in each file with clear before/after context. User confirms or rejects each change. This provides maximum control and transparency, ensuring users understand and approve all modifications. Particularly important given we're modifying working Spec Kit commands.

---

## Round 3: Rollback Strategy

### Q3.1: Rollback Mechanism

How should rollback be implemented?

**Options**:

- **Option A - Copy from backup**: Restore files from .integration-backup/
  - *Pros*: Simple, reliable
  - *Cons*: Manual process, no automation

- **Option B - Dedicated rollback command**: `/integrate-dev --rollback`
  - *Pros*: Automated, easy to use
  - *Cons*: More code to maintain

- **Option C - Git reset**: Use git to revert changes
  - *Pros*: Standard tooling, built-in
  - *Cons*: Requires git, may affect other changes

- **Option D - Undo script**: Generate custom undo script during integration
  - *Pros*: Precise, targeted
  - *Cons*: Complex to generate, may fail

**Recommendation**: ✅ **Option B - Dedicated rollback command (with automatic backup)**

**Decision Rationale**: `agents-library integrate --rollback` provides clear, automated rollback. Before integration, automatically create timestamped backup in `.integration-backup-[timestamp]/` containing all files that will be modified. Rollback command restores from this backup, removes integration artifacts (DEV agent, modified commands). Can detect the most recent integration backup automatically. Simple to use and doesn't require git knowledge.

---

### Q3.2: Backup Retention

How long should backups be kept?

**Options**:

- **Option A - Forever**: Keep until user manually deletes
  - *Pros*: Always available
  - *Cons*: Clutters workspace

- **Option B - Until next integration**: Delete old backup when new integration starts
  - *Pros*: Only keeps latest
  - *Cons*: Can't rollback older integrations

- **Option C - User prompted**: Ask user after successful integration
  - *Pros*: User control
  - *Cons*: Extra interaction

- **Option D - Time-based**: Auto-delete after 30 days
  - *Pros*: Automatic cleanup
  - *Cons*: Arbitrary timeframe, may delete too soon

**Recommendation**: ✅ **Option C - User prompted**

**Decision Rationale**: After successful integration and validation, prompt: "Integration complete. Keep backup at `.integration-backup-[timestamp]/`? (y/n)". If 'n', clean up. If 'y', preserve indefinitely. This gives users control while preventing clutter. Also provide `agents-library clean-backups` command to manually remove old backups later.

---

### Q3.3: Partial Rollback

Should the command support rolling back only specific files?

**Options**:

- **Option A - All or nothing**: Rollback entire integration or nothing
  - *Pros*: Simple, clean state
  - *Cons*: Can't fix individual file issues

- **Option B - Selective rollback**: Choose which files to restore
  - *Pros*: Flexible, surgical fixes
  - *Cons*: Complex, may create inconsistent state

- **Option C - No rollback**: User manages via git or manual restore
  - *Pros*: Simplest for command
  - *Cons*: Least user-friendly

**Recommendation**: ✅ **Option A - All or nothing**

**Decision Rationale**: Rollback restores complete pre-integration state - all modified files, removes DEV agent. This ensures consistent state and prevents broken configurations. If users need surgical fixes, they can rollback completely, then manually reapply parts they want to keep. Integration is atomic: fully applied or fully reverted.

---

## Round 4: Validation Strategy

### Q4.1: Validation Depth

How thorough should validation be?

**Options**:

- **Option A - Syntax only**: Check YAML valid, files parseable
  - *Pros*: Fast, reliable
  - *Cons*: Doesn't verify functionality

- **Option B - Structural validation**: Check required sections exist
  - *Pros*: Verifies completeness
  - *Cons*: Doesn't test if it works

- **Option C - Functional test**: Try to invoke DEV sub-agent on dummy task
  - *Pros*: Proves it works
  - *Cons*: Slow, requires test setup

- **Option D - Tiered validation**: Syntax → Structure → Functional (optional)
  - *Pros*: Balanced, user can choose depth
  - *Cons*: More complex

**Recommendation**: ✅ **Option B - Structural validation**

**Decision Rationale**: Validate YAML syntax in DEV agent frontmatter AND verify required sections exist in modified commands (Phase 0-8 in /implement, Quality Standards in /plan, etc.). This catches integration errors without requiring test infrastructure. Functional testing happens naturally when users run `/implement` on their first feature.

---

### Q4.2: Validation Failures

What should happen when validation fails?

**Options**:

- **Option A - Auto-rollback**: Immediately revert all changes
  - *Pros*: Safe, clean state
  - *Cons*: User loses progress, can't debug

- **Option B - Report + recommend rollback**: Show issues, suggest rollback
  - *Pros*: User decides, can investigate
  - *Cons*: May leave broken state

- **Option C - Attempt auto-fix**: Try to repair validation issues
  - *Pros*: May succeed, saves manual work
  - *Cons*: May make things worse

- **Option D - Leave as-is + document**: Log issues, let user fix manually
  - *Pros*: Maximum flexibility
  - *Cons*: Requires user expertise

**Recommendation**: ✅ **Option B - Report + recommend rollback**

**Decision Rationale**: When structural validation fails, show clear error report detailing what's missing/broken and which files are affected. Recommend using `agents-library integrate --rollback` to restore previous state. This preserves the integration attempt for debugging while giving users clear next steps. Avoids auto-rollback so users can inspect what went wrong.

---

## Round 5: Idempotency & Re-runs

### Q5.1: Detecting Existing Integration

How should the command detect if DEV integration already exists?

**Options**:

- **Option A - Check for .claude/agents/dev.md**: File presence indicates integration
  - *Pros*: Simple, clear signal
  - *Cons*: Doesn't verify it's OUR integration

- **Option B - Check for marker in files**: Add "DEV_INTEGRATION_APPLIED" comments
  - *Pros*: Explicit tracking
  - *Cons*: Pollutes files with markers

- **Option C - Separate manifest file**: .dev-integration-manifest.json
  - *Pros*: Clean tracking, version info
  - *Cons*: Another file to maintain

- **Option D - Analyze file structure**: Look for DEV-specific sections/patterns
  - *Pros*: No extra markers needed
  - *Cons*: Heuristic, may be wrong

**Recommendation**: ✅ **Option C - Separate manifest file**

**Decision Rationale**: Create `.agents-library-manifest.json` tracking installed agents and integrations with metadata (version, timestamp, files modified). Check this manifest to detect existing integration. Provides clean detection, version tracking for updates, and doesn't pollute code files with markers.

---

### Q5.2: Re-run Behavior

What should happen when command runs on already-integrated project?

**Options**:

- **Option A - Error and exit**: "Already integrated, use --force to override"
  - *Pros*: Safe, explicit
  - *Cons*: Blocks legitimate updates

- **Option B - Update integration**: Apply any changes from newer proposal
  - *Pros*: Keeps integration current
  - *Cons*: May overwrite intentional customizations

- **Option C - Ask user**: "Integration detected. Update, skip, or rollback?"
  - *Pros*: User control
  - *Cons*: Requires interaction

- **Option D - Compare versions**: If proposal newer, offer update; else skip
  - *Pros*: Intelligent, automated
  - *Cons*: Requires version tracking

**Recommendation**: ✅ **Option D - Compare versions (with user confirmation)**

**Decision Rationale**: Check manifest version against current library version. If newer version available, show what changed and ask: "Newer integration available (v1.0 → v1.1). Update? (y/n)". If same version, inform user: "Integration already at latest version (v1.1)". This combines intelligent detection with user control.

---

### Q5.3: Forced Re-integration

Should there be a `--force` flag to re-apply integration?

**Options**:

- **Option A - Yes, with confirmation**: `--force` requires explicit "yes" confirmation
  - *Pros*: Available but safe
  - *Cons*: Extra step

- **Option B - Yes, no confirmation**: `--force` immediately re-applies
  - *Pros*: Fast, scriptable
  - *Cons*: Dangerous, may lose work

- **Option C - No force flag**: Always interactive, always safe
  - *Pros*: Can't accidentally destroy
  - *Cons*: May be frustrating for power users

- **Option D - Different flag**: `--update` for safe re-apply vs `--force` for destructive
  - *Pros*: Semantic clarity
  - *Cons*: More flags to remember

**Recommendation**: ✅ **Option A - Yes, with confirmation**

**Decision Rationale**: Support `--force` flag to bypass version check and reapply integration, but still require confirmation prompt: "This will overwrite existing integration. Continue? (y/n)". Still goes through interactive review (Q2.3) so user sees what changes. Provides override capability while maintaining safety through confirmation.

---

## Round 6: User Experience

### Q6.1: Progress Reporting

How should the command report progress during execution?

**Options**:

- **Option A - Silent until done**: Only show final report
  - *Pros*: Clean, no clutter
  - *Cons*: User doesn't know what's happening

- **Option B - Per-phase updates**: Report after each phase completes
  - *Pros*: Balanced visibility
  - *Cons*: May still feel slow

- **Option C - Verbose logging**: Show each step as it happens
  - *Pros*: Complete transparency
  - *Cons*: Information overload

- **Option D - Progress bar/spinner**: Visual indicator with percentage
  - *Pros*: Modern UX, clear progress
  - *Cons*: Hard to implement in CLI

**Recommendation**: ?

---

### Q6.2: Confirmation Prompts

How many confirmation prompts should there be?

**Options**:

- **Option A - One upfront**: Confirm entire integration before starting
  - *Pros*: Simple, one decision
  - *Cons*: User commits without seeing details

- **Option B - Per-phase confirmations**: Confirm before each major phase
  - *Pros*: More control, can abort mid-process
  - *Cons*: Tedious, many interruptions

- **Option C - Two prompts**: One before backup, one before applying changes
  - *Pros*: Key decision points covered
  - *Cons*: Still multiple interruptions

- **Option D - None with `--yes` flag**: Default interactive, `--yes` skips all
  - *Pros*: Flexible for automation
  - *Cons*: Dangerous if misused

**Recommendation**: ?

---

### Q6.3: Error Communication

How should errors be presented to users?

**Options**:

- **Option A - Technical details**: Full stack trace, file paths, error codes
  - *Pros*: Complete information for debugging
  - *Cons*: Overwhelming for non-technical users

- **Option B - User-friendly messages**: Plain English, actionable next steps
  - *Pros*: Accessible, helpful
  - *Cons*: May hide important details

- **Option C - Tiered messaging**: Brief message + "details" section
  - *Pros*: Best of both worlds
  - *Cons*: More text to write/maintain

- **Option D - Link to documentation**: Error code + URL for details
  - *Pros*: Keeps command output clean
  - *Cons*: Requires external docs, network access

**Recommendation**: ?

---

## Round 7: Command Flags & Options

### Q7.1: Optional Enhancements

Which command flags should be supported?

**Current proposal mentions**: `--rollback`

**Options to consider**:

- **Flag: --dry-run**: Show what would happen without making changes
  - *Value*: Preview before commit
  - *Complexity*: Medium

- **Flag: --skip-backup**: Don't create backup (faster, riskier)
  - *Value*: Speed for trusted scenarios
  - *Complexity*: Low

- **Flag: --backup-dir <path>**: Specify custom backup location
  - *Value*: Control over backup placement
  - *Complexity*: Low

- **Flag: --skip-validation**: Apply without validation (debug mode)
  - *Value*: Bypass broken validation
  - *Complexity*: Low

- **Flag: --verbose**: Show detailed progress logging
  - *Value*: Debugging, transparency
  - *Complexity*: Medium

- **Flag: --quiet**: Minimal output, only errors
  - *Value*: Scriptability, automation
  - *Complexity*: Low

**Which flags should be implemented?**
- Essential: ?
- Nice-to-have: ?
- Skip: ?

---

### Q7.2: Configuration File

Should the command support a configuration file?

**Options**:

- **Option A - No config file**: All behavior via flags or interactive
  - *Pros*: Simple, no extra file
  - *Cons*: Must specify options each time

- **Option B - Optional .integrate-dev.config.json**: Defaults for flags, paths
  - *Pros*: Reusable settings
  - *Cons*: Another file, more complexity

- **Option C - Use existing config**: Piggyback on .claude/config or similar
  - *Pros*: Single config location
  - *Cons*: May pollute existing config

**Recommendation**: ?

---

## Round 8: Testing & Validation Requirements

### Q8.1: Pre-Integration Testing

What testing should happen BEFORE the command is released?

**Test Coverage Needed**:
1. Fresh Spec Kit (no customizations)
2. Customized Spec Kit (modified /implement)
3. Already integrated project
4. Missing source files
5. Invalid YAML in dev.md
6. Corrupted proposal.md
7. No write permissions
8. Different Spec Kit versions

**Question**: Should automated tests be created for the command itself?

**Options**:

- **Option A - Manual testing only**: Test cases run by humans
  - *Pros*: Simple, flexible
  - *Cons*: Not repeatable, error-prone

- **Option B - Automated test suite**: Scripts that verify command behavior
  - *Pros*: Repeatable, reliable
  - *Cons*: Significant effort to build

- **Option C - Example-based validation**: Provide example projects to test against
  - *Pros*: Real-world scenarios
  - *Cons*: Examples must be maintained

**Recommendation**: ?

---

### Q8.2: Post-Integration Validation

What should users do to verify the integration worked?

**Options**:

- **Option A - Built-in smoke test**: Command runs basic test automatically
  - *Pros*: Immediate validation
  - *Cons*: Requires test infrastructure

- **Option B - Manual checklist**: Provide steps for user to verify
  - *Pros*: Explicit, educational
  - *Cons*: Relies on user diligence

- **Option C - Separate validate command**: `/integrate-dev --validate`
  - *Pros*: On-demand validation
  - *Cons*: User must remember to run

- **Option D - Integration test feature**: Generate a test feature to implement
  - *Pros*: End-to-end proof
  - *Cons*: Complex, time-consuming

**Recommendation**: ?

---

## Round 9: Documentation & Support

### Q9.1: Documentation Scope

What documentation should accompany the command?

**Options**:

- **Option A - Embedded in command**: All docs in .claude/commands/integrate-dev.md
  - *Pros*: Self-contained, always accessible
  - *Cons*: Makes command file very large

- **Option B - Separate docs file**: README-integrate-dev.md alongside command
  - *Pros*: Organized, detailed
  - *Cons*: User must find it

- **Option C - Inline help**: `--help` flag shows comprehensive guide
  - *Pros*: Standard CLI pattern
  - *Cons*: Limited formatting

- **Option D - Multi-format**: Inline help for quick ref + detailed external docs
  - *Pros*: Best of all worlds
  - *Cons*: Must maintain multiple versions

**Recommendation**: ?

---

### Q9.2: Troubleshooting Guide

How comprehensive should troubleshooting documentation be?

**Options**:

- **Option A - Basic FAQ**: 5-10 common issues with solutions
  - *Pros*: Covers most cases
  - *Cons*: May miss edge cases

- **Option B - Exhaustive guide**: Every possible error with remediation
  - *Pros*: Complete reference
  - *Cons*: Huge doc, hard to maintain

- **Option C - Community-driven**: Start basic, expand based on real issues
  - *Pros*: Organic, relevant
  - *Cons*: Incomplete initially

- **Option D - Error-code based**: Each error links to specific solution
  - *Pros*: Precise, organized
  - *Cons*: Requires error code system

**Recommendation**: ?

---

## Decision Log

This section will be populated as decisions are made for each question above.

### Round 0: Library Architecture
- Q0.1: ✅ **Option A - Python package with uvx**
- Q0.2: ✅ **Option A - Flat agents/ directory**
- Q0.3: ✅ **Option A - Python**

### Round 1: Installation Flow
- Q1.1: ✅ **Option D - Hybrid** (interactive + flags)
- Q1.2: ✅ **Option A - During init** (with defer option)
- Q1.3: ✅ **Option C - Smart update**

### Round 2: Customization Preservation
- Q2.1: ✅ **Option B - Heuristic analysis**
- Q2.2: ✅ **Option A - Fail safe**
- Q2.3: ✅ **Option C - Interactive review**

### Round 3: Rollback Strategy
- Q3.1: ✅ **Option B - Dedicated rollback command** (with automatic backup)
- Q3.2: ✅ **Option C - User prompted**
- Q3.3: ✅ **Option A - All or nothing**

### Round 4: Validation Strategy
- Q4.1: ✅ **Option B - Structural validation**
- Q4.2: ✅ **Option B - Report + recommend rollback**

### Round 5: Idempotency & Re-runs
- Q5.1: ✅ **Option C - Separate manifest file**
- Q5.2: ✅ **Option D - Compare versions** (with confirmation)
- Q5.3: ✅ **Option A - Yes, with confirmation**

### Round 6: User Experience
- Q6.1: [Pending]
- Q6.2: [Pending]
- Q6.3: [Pending]

### Round 7: Command Flags & Options
- Q7.1: [Pending]
- Q7.2: [Pending]

### Round 8: Testing & Validation
- Q8.1: [Pending]
- Q8.2: [Pending]

### Round 9: Documentation & Support
- Q9.1: [Pending]
- Q9.2: [Pending]

---

## Summary

**Total Questions**: 21 across 9 rounds

**Key Decision Areas**:
1. **File organization** - Where source files live, how proposals version
2. **Customization handling** - Detect, preserve, or merge user changes
3. **Safety mechanisms** - Backup strategy, rollback capability
4. **Validation rigor** - How thorough, what happens on failure
5. **Idempotency** - Detecting existing integration, re-run behavior
6. **User experience** - Progress reporting, confirmations, errors
7. **Flexibility** - Command flags and configuration options
8. **Quality assurance** - Testing requirements and validation
9. **Support** - Documentation scope and troubleshooting depth

**Next Steps**: Work through each question to finalize command specification
