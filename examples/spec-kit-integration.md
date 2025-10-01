# Spec Kit Integration Example

This example demonstrates integrating Pantheon's DEV agent with an existing Spec Kit project.

## Prerequisites

- Python 3.9+
- Spec Kit installed in your project
- Claude Code

## Step-by-Step Guide

### 1. Install Pantheon

From your project directory:

```bash
uvx pantheon-agents init
```

Or install globally:

```bash
uv tool install pantheon-agents
pantheon init
```

### 2. Verify Spec Kit Detection

Pantheon will automatically detect Spec Kit if both exist:
- `.specify/` directory
- `.claude/commands/` directory

You should see:

```
✓ Found .claude/
✓ Found .claude/agents/
✓ Copied dev.md to .claude/agents/

Spec Kit detected!
Would you like to integrate DEV agent with Spec Kit? [Y/n]:
```

### 3. Integrate with Spec Kit

Choose "Y" to integrate, or run manually:

```bash
pantheon integrate
```

This will:
1. Create a timestamped backup of your command files
2. Add integration directives to:
   - `.claude/commands/implement.md`
   - `.claude/commands/plan.md`
   - `.claude/commands/tasks.md`
3. Validate the integration

### 4. Review Changes (Optional)

Before integrating, preview changes:

```bash
pantheon integrate --dry-run
```

Output:
```
🔍 Dry run mode - no changes will be made

Would create backup directory
Would modify:
  - .claude/commands/implement.md
  - .claude/commands/plan.md
  - .claude/commands/tasks.md
```

### 5. Use the Enhanced Workflow

#### A. Create Specification

```bash
/specify
```

Your spec will now include quality standards guidance.

#### B. Generate Implementation Plan

```bash
/plan
```

The plan will include:
- Lint command (e.g., `npm run lint`)
- Type check command (e.g., `tsc --noEmit`)
- Test command (e.g., `npm test`)
- Coverage requirement

#### C. Generate Tasks

```bash
/tasks
```

Tasks will follow the enhanced format:

```markdown
**T001** Implement user authentication (`src/auth/index.ts`)
- [ ] Create authentication service with login/logout methods
- [ ] Add JWT token generation and validation
- [ ] Implement password hashing with bcrypt
- Dependencies: None
- Implements: FR-001, FR-002
```

#### D. Execute Implementation

```bash
/implement
```

The `/implement` command will now:
1. Load task context (ID, description, file paths)
2. Prepare context package with:
   - Task requirements
   - Quality standards from plan.md
   - Subtasks as acceptance criteria
   - Tech stack constraints
3. Invoke DEV sub-agent using Task tool
4. Process results and mark tasks complete
5. Create commits at phase boundaries

## What DEV Does

For each task, DEV follows this workflow:

### Phase 5: Implement (Per Subtask)

1. **Code**: Write implementation
   ```typescript
   // DEV writes clean, well-structured code
   export class AuthService {
     async login(email: string, password: string): Promise<AuthToken> {
       // Implementation
     }
   }
   ```

2. **Test**: Write unit tests
   ```typescript
   describe('AuthService', () => {
     it('should authenticate valid credentials', async () => {
       // Test implementation
     });
   });
   ```

3. **Verify Acceptance Criteria**
   - ✅ Authentication service created with login/logout methods
   - If not met: refine and retry

4. **Verify Quality Standards**
   ```bash
   npm run lint    # Must pass
   tsc --noEmit    # Must pass
   npm test        # Must pass
   ```
   - If not met: fix issues and rerun

5. **Commit**: Create atomic commit
   ```bash
   git commit -m "feat: add authentication service

   - Implement login/logout methods
   - Add JWT token generation
   - Include password hashing with bcrypt

   Implements: FR-001, FR-002"
   ```

### Phase 6: Verify

Final verification that all success criteria are met and quality standards maintained.

### Phase 7: Finalize

Present results to user with summary of:
- Tasks completed
- Commits created
- Quality checks passed

## Rollback if Needed

If you need to undo the integration:

```bash
pantheon rollback
```

This will:
1. Find the most recent backup
2. Restore original command files
3. Report what was restored

With `--force` to skip confirmation:

```bash
pantheon rollback --force
```

## Project Structure After Integration

```
your-project/
├── .claude/
│   ├── agents/
│   │   └── dev.md                 # DEV agent (from Pantheon)
│   └── commands/
│       ├── implement.md           # Enhanced with DEV delegation
│       ├── plan.md                # Enhanced with quality standards
│       ├── tasks.md               # Enhanced with subtask format
│       ├── specify.md             # Unchanged
│       └── ...other commands
├── .specify/
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── .integration-backup-20251001-143000/  # Auto-created backup
│   ├── implement.md
│   ├── plan.md
│   └── tasks.md
└── ...your project files
```

## Tips

1. **Use Dry Run First**: Always preview changes with `--dry-run`
2. **Keep Backups**: Backups are automatic but timestamped, you can keep multiple
3. **Commit Often**: DEV creates atomic commits - leverage them
4. **Quality First**: Don't skip quality checks - they catch issues early
5. **Iterate**: Use Phase 8 for feedback and refinement

## Troubleshooting

### Integration Fails

```bash
❌ Integration failed!
  • Spec Kit not detected. Ensure .specify/ and .claude/commands/ exist.
```

**Solution**: Verify Spec Kit is installed:
```bash
ls -la .specify/
ls -la .claude/commands/
```

### DEV Agent Not Found

```bash
❌ Integration failed!
  • DEV agent not installed. Run 'pantheon init' first.
```

**Solution**: Initialize Pantheon first:
```bash
pantheon init
```

### Quality Checks Failing

If DEV reports quality issues:

1. Check the specific error (lint/type/test)
2. Review the reported file and line number
3. Fix the issue
4. DEV will retry automatically

### Rollback Not Working

```bash
❌ Rollback failed!
  • No backup found. Nothing to rollback.
```

**Solution**: Integration hasn't been run yet, or backup was manually deleted.

## Next Steps

- Read [DEV Agent Workflow](../README.md#dev-agent-workflow)
- Review [Architecture](../README.md#architecture)
- Check [Contributing Guide](../CONTRIBUTING.md)
- Report issues: https://github.com/alex-abrams711/pantheon/issues

## Additional Examples

For more examples, see:
- [Basic usage without Spec Kit](./standalone-usage.md) *(coming soon)*
- [Custom agent creation](./custom-agent.md) *(coming soon)*
- [CI/CD integration](./ci-cd.md) *(coming soon)*
