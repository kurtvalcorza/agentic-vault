---
description: "Kiro integration protocols — spec-driven development, agent hooks, and output organization."
source-section: "Kiro Integration"
---

## Kiro Integration

### Spec-Driven Development
Kiro uses a formal spec-driven development methodology for building features with correctness guarantees:

**Workflow**: Requirements → Design → Tasks → Implementation

**Structure**: `.kiro/specs/{feature-name}/`
- `requirements.md` - User stories and acceptance criteria
- `design.md` - Architecture and correctness properties
- `tasks.md` - Implementation task list with property-based testing

**Property-Based Testing (PBT)**: All specs include executable correctness properties validated through PBT frameworks. This ensures software conforms to formal specifications.

**When to Use**:
- Building new features with formal correctness requirements
- Implementing complex functionality requiring systematic validation
- Creating testable specifications before implementation

### Agent Hooks
Kiro supports automated agent actions triggered by IDE events:

**Hook Types**:
- `fileEdited` - Triggered when files are saved
- `fileCreated` - Triggered when new files are created
- `fileDeleted` - Triggered when files are deleted
- `promptSubmit` - Triggered when user submits a prompt
- `agentStop` - Triggered when agent execution completes
- `userTriggered` - Manually triggered by user
- `preToolUse` - Triggered before a tool is executed (supports tool category/regex filtering)
- `postToolUse` - Triggered after a tool is executed (supports tool category/regex filtering)
- `preTaskExecution` - Triggered before a spec task starts
- `postTaskExecution` - Triggered after a spec task completes

**Hook Actions**:
- `askAgent` - Send prompt to agent (valid with all event types)
- `runCommand` - Execute shell command (valid with all event types)

**Hook Location**: `.kiro/hooks/` (`.kiro.hook` configuration files)

**Examples**:
- Auto-lint on file save: `fileEdited` → `askAgent` → "Run linter and fix errors"
- Session logging: `agentStop` → `askAgent` → "Log session activity"
- Build on prompt: `promptSubmit` → `runCommand` → "npm run build"

### Output Organization
All agent outputs go to `.agent/outputs/` — the shared write space. Do not create agent-specific output directories (`.gemini/outputs/`, `.kiro/outputs/`).
