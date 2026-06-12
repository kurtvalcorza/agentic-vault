---
description: "Security and privacy protocols — PII handling, agent boundaries, secret management, script safety, and external integrations."
source-section: "Security & Privacy Protocols"
---

## Security & Privacy Protocols

### Data Handling
- **PII Redaction**: Sanitize personally identifiable information in shared notes or exported content. Use `[name]`, `[email]`, `[phone]` placeholders in examples and templates.
- **Institutional Content**: Example Org materials must meet professional standards; verify accuracy before external sharing.
- **Sensitive Projects**: Mark confidential projects clearly; avoid exposing internal details in public-facing outputs.

### Secret Management
- Never store API keys, passwords, or tokens in Markdown notes or frontmatter
- Use `.env` files (gitignored) for credentials needed by scripts
- MCP server credentials belong in `mcp.json` — never in steering docs or notes
- Audit hook patterns to ensure sensitive files aren't sent to cloud AI

### Agent Boundaries
- **Cross-Agent Isolation**: Never modify agent-specific directories (`.gemini/`, `.kiro/`, `.claude/`) unless you are that agent's owner.
- **Read-Only Respect**: Treat other agents' workspaces as read-only for context gathering only.
- **Shared Workspace**: `.agent/` is the only shared write space for collaborative tasks.
- **Skill Ownership**: Skills in `.agent/skills/` are collectively owned; agent-specific skills stay in their respective directories.

### Script Safety
- Scripts in `.agent/scripts/` must not hardcode drive letters or absolute paths
- Validate script existence before invoking
- Handle errors gracefully — report failures, don't silently continue
- Log script outputs for debugging

### External Integrations
- Assume vault contents are private by default.
- When syncing or publishing, explicitly confirm scope with user.
- Sanitize metadata (timestamps, author info) if anonymity is required.
- Review git diffs for accidental exposure before pushing.
