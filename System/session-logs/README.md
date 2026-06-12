# Session Logs

Per-session agent activity logs — the vault's cross-device, cross-agent continuity layer.

- **Layout:** `YYYY-MM-DD/HH-MM-SS_brief-description.md` (real clock time, never invented).
- **Provenance:** every entry carries `agent: <name>` in YAML frontmatter.
- **Who writes them:** Claude/Codex write deterministic logs automatically at session end (`.agent/scripts/vault-session-log.ps1`); Kiro writes LLM-summarized logs via its `agentStop` hook; rich milestones use the `checkpoint-session` skill.
- **Resume rule:** agents check today's folder first when starting work.
- **Archival:** folders older than 30 days move to `04_Archives/_agent-artifacts/session-logs/YYYY-MM/` (quarterly cadence).
