---
description: "Session continuity protocols — cross-device work tracking, session log format, workflow for resuming sessions, and naming conventions."
source-section: "Session Continuity"
---

## Session Continuity

### Cross-Device Work Tracking
*   **Session Logs**: `System/session-logs/YYYY-MM-DD/` folders contain individual session log files for each agent activity, enabling granular tracking and resuming work across devices.
*   **Auto-Logging**: Three harnesses auto-log at session end. Kiro hook `auto-log-session` (`.kiro/hooks/auto-log-session.kiro.hook`) creates an LLM-inferred summary on `agentStop`. Claude (`SessionEnd` hook) and Codex (`Stop` hook) run `.agent/scripts/vault-session-log.ps1 -Agent <name>`, which writes a deterministic log (git-derived file list, no LLM inference). All entries carry `agent:` provenance frontmatter.
*   **Manual Checkpoints**: Use `checkpoint-session` skill for major milestones (goal, status, skills/tools used, files, outputs, actions, decisions, next steps).
*   **Resuming Work**: Always check today's session log folder first to understand current context and previous actions.

### Session Log Format
Each entry includes:
- **Goal**: Primary objective
- **Status**: Current state (✅ completed, 🔄 in progress, ⏸️ paused, 🚫 blocked)
- **Skills/Tools Used**: What was invoked
- **Files Modified**: Changed files
- **Outputs**: Generated artifacts
- **Key Actions**: Major operations
- **Decisions**: Important choices made
- **Next Steps**: What to do when resuming

### Workflow for Resuming Sessions
1. Check `System/session-logs/YYYY-MM-DD/` folder for today's context
2. Review most recent log file for status and next steps
3. If work spans multiple days, check previous day's folder
4. Use checkpoint-session skill to mark major milestones
5. Auto-logging captures routine completions as separate files automatically

### Session Log Naming Convention
*   **Folder**: `System/session-logs/YYYY-MM-DD/`
*   **Log Files**: `HH-MM-SS_brief-description.md` or `HH-MM-SS_session-N.md`
*   **Example**: `System/session-logs/2026-02-08/14-30-45_update-agents-md.md`
*   **Timestamps**: Use the actual clock time, never an invented/round placeholder time.

### Session Log Archival
*   **Policy**: Session-log folders older than **30 days** are archived to `04_Archives/_agent-artifacts/session-logs/YYYY-MM/` (per [[04_Archives/specs/archive-taxonomy]]), and the batch is recorded in `04_Archives/ARCHIVE-INDEX.md`.
*   **Cadence**: Executed during quarterly `optimize-workspace` runs, or ad-hoc when the folder count grows noticeably. This is an agent task, never the owner's.
