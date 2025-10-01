# Research: Claude Code Sub-Agents for DEV Integration

**Date**: 2025-09-30

---

## Research Findings: Claude Code Sub-Agents

### What Are Sub-Agents?

Sub-agents are **specialized AI assistants within Claude Code** designed for specific tasks:

**Key Characteristics**:
- Operate in **separate context windows** (preserves main conversation context)
- Handle **specific types of tasks** with focused expertise
- Provide **reusable, configurable** AI assistants

**Configuration**:
- Defined in **Markdown files** with **YAML frontmatter**
- Can specify:
  - Name and description
  - Specific tools available
  - Model selection
  - System prompts/instructions

**Invocation Methods**:
1. **Automatic delegation**: Claude automatically routes tasks based on description
2. **Explicit invocation**: User/agent mentions the sub-agent by name

**Example Sub-agents**:
- **Code Reviewer**: Checks code quality and security
- **Debugger**: Analyzes and resolves technical issues
- **Data Scientist**: Performs SQL and data analysis tasks

### Agent Architecture (Core Loop)

From Anthropic's engineering article, effective agents follow a feedback loop:

```
gather context → take action → verify work → repeat
```

**Context Management**:
- Agentic search through file systems
- Sub-agents for parallel information retrieval
- Compaction to manage long-term context limits

**Action Capabilities**:
- Custom tools for primary actions
- Bash/scripting for flexible interactions
- Code generation for complex tasks
- MCP for external service integration

**Verification Strategies**:
- Define clear rules
- Visual feedback (screenshots, outputs)
- Use additional LLMs as "judges"

### Sub-Agent Best Practices

1. **Create focused sub-agents** with clear, single responsibilities
2. **Write detailed system prompts** that define behavior
3. **Limit tool access** to only what's needed
4. **Version control** project-level sub-agents
5. **Chain multiple sub-agents** for complex workflows
6. **Dynamic selection** based on context

### Limitations

- May add latency (separate context window)
- Require careful configuration for optimal performance
- Each sub-agent invocation is stateless (no memory between calls)

---

## Implications for DEV Agent Integration

### Current Understanding

1. **DEV Agent as Sub-Agent**: We can define `final/dev.md` as a Claude Code sub-agent configuration
2. **Invocation from /implement**: The `/implement` command can explicitly invoke the DEV sub-agent for task execution
3. **Separate Context**: DEV operates in its own context window, preserving main conversation state
4. **Tool Access**: We can limit DEV's tools to only what's needed for implementation (Read, Write, Edit, Bash, etc.)

### Key Architectural Considerations

**Stateless Nature**:
- Each DEV invocation has no memory of previous calls
- State must be managed externally (by /implement or written to files)
- Context must be re-provided for each invocation

**Context Window Separation**:
- Main conversation preserved while DEV works
- DEV has its own token budget
- Results returned to main conversation

**Tool Scoping**:
- Can restrict DEV to only implementation tools (no web search, etc.)
- Ensures DEV stays focused on coding tasks

**Verification Loop**:
- DEV's "gather context → take action → verify work → repeat" aligns with Phase 5 workflow
- Can leverage DEV's internal verification before returning results

---

## Sources

- Claude Code Documentation: https://docs.claude.com/en/docs/claude-code/sub-agents
- Anthropic Engineering Blog: https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk
