## Sub-Agent Integration

**Workflow**: DEV agents -> QA validation -> Repeat

### 1. Execute Tasks (DEV Agents)

For each task in tasks.md:
- Invoke DEV agent with context: Task ID, files, acceptance criteria,
  quality standards from plan.md
- For parallel tasks marked `[P]`: Invoke agents in parallel in a SINGLE message

### 2. Validate Quality (QA Agent)

**After EACH DEV agents completes**:

1. **DO NOT commit yet**
2. Invoke QA agent with completed task ID:
   ```
   Use Task tool:
     subagent_type: "qa"
     description: "Validate task: [ID]"
     prompt: [QA context - task, quality standards, Definition of Done]
   ```
3. Process QA report:
   - **PASS**: Present results to user
   - **FAIL**: Re-execute the failed task with another DEV agent, providing
    updated context based on the QA Report

See `.claude/agents/dev.md` and `.claude/agents/qa.md` for details.

---
