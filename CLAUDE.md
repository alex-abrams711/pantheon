# Claude Instructions

## Initial Context

ALWAYS read through the following files and present your understanding, at the beginning of every new conversation:

- README.md
- docs/research.md
- docs/design.md
- tasks.md

NEVER access the docs/archive directory.

## Working Agreements

### DOs

- ALWAYS work to understand the task at hand. Ask questions when instructions are ambiguous or vague. Be skeptical.
- ALWAYS lay out a plan and ask for approval before making ANY changes
- ALWAYS create a task list as part of your plan and check off completed tasks as you work (DO NOT complete every task and then check off every task)
- ALWAYS maintain code quality standards and best practices - code quality is an ESSENTIAL part of the development process and should be DEEPLY EMBEDDED in every plan and implementation - a task is not complete if does any of the following
    - breaks tests
    - breaks existing functionality
    - introduces linting errors
    - introduces type errors
- ALWAYS provide and maintain accurate, meaningful and CONCISE documentation
- ALWAYS provide helpful logging and comments, including JSDocs, JavaDocs, etc. AS NECESSARY when writing complex code

### DONTs

- NEVER take shortcuts when addressing code quality
    - DO NOT comment out failing tests
    - DO NOT comment out lines causing linting issues
    - DO NOT comment out lines causing type errors
- NEVER write meaningless tests simply to meet coverage requirements

### Methodologies

- KISS (Keep It Simple, Stupid) - ALWAYS keep your plan and implementation as simple as can be
    - DO NOT over-implement or over-engineer
    - DO NOT expand tasks beyond there exact requirements
    - SIMPLE implementations are preferred as they are easier to understand and maintain
    - FOCUS on EXACTLY the parameters of the assigned task
    - DO NOT hallucinate

## MCP Servers

- Github - Useful for working with GitHub. Available tools include those related to repos, issues, and pull_requests
- Browser - Useful for accessing the browser - great for manually testing front ends
- Context7 - Comprehensive documentation for hundreds of different services, libraries, frameworks - use this when you need to research service, libraries, or frameworks
- SequentialThinking - Enhanced thinking capabilities - use when we need to think through complex problems
- Brave-Search - Enhanced web search - use this when you need to research topics that you don't natively understand - especially helpful for understanding best practices for working with specific tech stacks
