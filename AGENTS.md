# AGENTS.md

## Scope
[[AGENTS.md]] is the **Universal Source of Truth** for all AI agents (Claude, Gemini, Copilot, Kiro, Codex, etc.) operating in this vault. Agent-specific config files (`.claude/`, `.gemini/`, etc.) may override **preferences** (output format, verbosity, tool aliases) but MUST NOT override **core protocols**: Security & Privacy, Path Safety, Frontmatter Preservation, Session Continuity, or Operational Protocols.

> **Canonical File:** `AGENTS.md` is the single source of truth for agent protocols. `CLAUDE.md` is a standalone file that references `AGENTS.md` via `@AGENTS.md` directive. `GEMINI.md` is a **derived digest** (not a symlink) regenerated whenever `AGENTS.md` bumps its version — it carries a `Synced with AGENTS.md version:` marker, and `.agent/scripts/sync-agents.ps1` checks that marker for drift.

## Vault Overview

This is a **Personal Knowledge Management (PKM)** system built as an **Obsidian Vault** using a **Hybrid PARA + Zettelkasten** structure:

*   **PARA** (Projects, Areas, Resources, Archives) provides the top-level folder hierarchy and workflow lifecycle — content flows from capture (`Inbox/`) through active work (`01_Projects/`) into long-term knowledge (`02_Areas/`, `03_Resources/`) and eventually retirement (`04_Archives/`).
*   **Zettelkasten** principles govern how individual notes are written and connected — atomic notes (one idea per note), dense bidirectional `[[WikiLinks]]` (3-5 per note minimum), and emergent structure through linking rather than rigid categorization.

The two systems complement each other: PARA answers *"where does this live?"* while Zettelkasten answers *"how does this connect?"*

### Technology Stack
*   **Platform**: Obsidian (markdown-based knowledge base)
*   **Plugins** (recommended): Templater (templates), Calendar (daily notes), Kanban (work board), Excalidraw (diagrams), Bases (database views)
*   **Linking**: WikiLinks `[[Note Name]]` for bidirectional connections
*   **Format**: Standard Markdown with YAML frontmatter

### User Context
> ✏️ **Customize this section.** Replace the placeholders with your own context so agents understand who they're working for.

*   **Owner**: **{{OWNER_NAME}}**, {{ROLE / WHAT YOU DO}}.
*   **Focus**: {{YOUR KEY PROJECTS AND TOPICS}}.
*   **Tone**: Professional for `01_Projects/`, `02_Areas/`, `03_Resources/`, and `.agent/outputs/`. Casual/Personal for `Inbox/` captures and personal notes. Session logs (`System/session-logs/`) are neutral/factual.

### Workflow Pattern
```
Capture (Inbox)
    ↓
Process (universal-triager: PARA route + Zettelkasten enrich)
    ├── Authored + deadline     → 01_Projects/
    ├── Authored + ongoing      → 02_Areas/
    ├── External / reference    → 03_Resources/ (+ Source Catalog entry)
    └── Inactive / stale        → 04_Archives/

    ↕ WikiLinks connect across all directories
    ↕ AI Tools (.agent/) operate across entire vault
```

## Directory Structure & Agent Actions

### Core Directories
| Directory | Purpose | Agent Action |
| :--- | :--- | :--- |
| **`Inbox/`** | Quick capture (ideas, snippets). | Triage via `universal-triager` (PARA route + Zettelkasten enrich). |
| **`System/`** | Templates (`templates/`) and session logs (`session-logs/YYYY-MM-DD/`). | Use templates for consistency. Check session logs when resuming. Auto-log on session end. |
| **`01_Projects/`** | Active work & deliverables with deadlines. | Main workspace for user requests. Live work queue is the Kanban board [[01_Projects/To Do]] — see Active Work Board below. |
| **`02_Areas/`** | Long-term authored knowledge. | Apply Zettelkasten enrichment (atomicity, linking) when filing. Use [[02_Areas/AREA-INDEX]] for discoverability. |
| **`03_Resources/`** | External reference materials, attachments, bookmarks. | Follow [[RESOURCE-INDEX]] for intake rules and Source Catalog. Sub-dirs: `Attachments/`, `Reference/`, `Bookmarks/`, `Reading-List/`, `Compiled/`. |
| **`04_Archives/`** | Inactive/Completed work. | Follows [[04_Archives/specs/archive-taxonomy]]. Search here for historical context. |

### Active Work Board (Kanban)

The vault's live work queue is the Obsidian Kanban board at [[01_Projects/To Do]] (`01_Projects/To Do.md`, rendered by the Kanban plugin). It is the **authoritative tracker for active work**, so check it when resuming, prioritizing, or asking "what's next?".

- **Columns**: `Pending` (committed, not started) → `Ongoing` (in progress) → `Parked` (deferred/blocked) → `Complete` (done).
- **Card format**: `<TYPE> > <context> > <deliverable> 📅 YYYY-MM-DD`, where the 📅 date is the deadline. Define your own TYPE codes (e.g., `TALK`, `REPORT`, `DEV`).
- **Agent actions**: When a task maps to a card, reference the card. When work completes, move the card to `Complete` and mark it `[x]`. Do **not** restructure the board, rename columns, or strip the `kanban-plugin` frontmatter or the `%% kanban:settings %%` block — these are plugin-managed.

### Agent Workspaces
*   **`.agent/`**: Shared workspace (skills, scripts, outputs, steering, SKILLS-REGISTRY.md, TOOL-TAXONOMY.md). The only shared write space.
*   **`.claude/`**, **`.gemini/`**, **`.kiro/`**, **`.codex/`**: Agent-specific configs (READ-ONLY for other agents).

> **Symlink Architecture:** All agent `skills/` directories are symlinks/junctions to `.agent/skills/` — single canonical skill directory, single registry. Run `setup.ps1` after cloning to create the junctions (git cannot store them).

## Organizational Standards (The "Agent Skills Standard")

> **Extracted:** Full detail in `.agent/steering/skills-standard.md`

- **Dual-Documentation Pattern**: All skills require both `SKILL.md` (agent instructions) and `README.md` (human docs)
- **Standardized Frontmatter**: Strict YAML schema with `name` (kebab-case) and `description` (what + when)
- **Skills as Directories**: `skill-name/` → `{SKILL.md, README.md, references/, templates/}`
- **Universality Standards**: Shared skills must be agent-agnostic (generic tool names from `TOOL-TAXONOMY.md`, `**Agent:**` labels, `.agent/` paths)
- **Content Safety**: Skill modifications must be reviewed by the user before use by other agents. When creating or editing a shared skill, notify the user in the chat response and log the change in the session log. `validate-skills-standard` checks structure; content safety is the author's responsibility.

## File Naming & Linking

> **Extracted:** Full detail in `.agent/steering/file-naming-conventions.md`

- Daily notes: `YYYY-MM-DD.md` | Skills: `skill-name/{SKILL.md, README.md}` | Outputs: `YYYY-MM-DD_Output-Description.md`
- WikiLinks `[[Note Name]]` for all internal connections; 3-5 links per note minimum (fewer is acceptable for genuinely isolated topics, but actively search for connections before settling for less)

## Tag Taxonomy

> **Extracted:** Full detail in `.agent/steering/tag-taxonomy.md`

- Hierarchical, lowercase: `#project/example`, `#skill/research`, `#status/active`

## Conversational Interface

> **Extracted:** Full detail in `.agent/steering/conversational-interface.md`

- **Skills-First Protocol**: Always check `.agent/skills/` and `.agent/SKILLS-REGISTRY.md` before implementing manually. If no matching skill exists, proceed with the task directly — do not block on skill absence.
- Common triggers: "write a note", "synthesize research", "compile my sources into a wiki", "what do my notes say about X?", "clip this article", "find recurring concepts"

## Script Execution & Quality Assurance

> **Extracted:** Full detail in `.agent/steering/scripts-and-qa.md`

- Scripts live in `.agent/scripts/` (PowerShell via `pwsh`, Python 3.9+)
- Run `validate-skills-standard` before committing new skills
- Pre-commit: skills need `SKILL.md` + `README.md`, kebab-case `name`, no hardcoded paths

## Security & Privacy Protocols

> **Extracted:** Full detail in `.agent/steering/security-best-practices.md`

- **PII Redaction**: Sanitize personally identifiable information in shared or exported content
- **Agent Boundaries**: `.agent/` is the shared write space; respect cross-agent isolation for `.gemini/`, `.claude/`, `.kiro/`
- **Secret Management**: Never store API keys or tokens in Markdown notes; use `.env` files (gitignored) and `mcp.json`
- **Script Safety**: No hardcoded paths or drive letters; validate script existence before invoking
- **External Integrations**: Vault contents are private by default; confirm scope **with the user** before syncing, publishing, or uploading any vault content to external services

## Session Continuity

> **Extracted:** Full detail in `.agent/steering/session-continuity.md`

- Session logs: `System/session-logs/YYYY-MM-DD/` (one file per agent activity)
- **Provenance**: Every session log entry MUST include the agent name in YAML frontmatter (`agent: claude`, `agent: kiro`, etc.) so entries are attributable.
- Resume rule: always check today's session log folder first
- Use `checkpoint-session` skill for major milestones; auto-logging at session end

## Steering File Priority

Not all steering files need to be read on every session. Priority levels:

| Priority | When to read | Files |
| :--- | :--- | :--- |
| **Always** | Every session, before any work | `AGENTS.md` (this file), today's session log, `memory-hot-cache.md` |
| **On relevant action** | Before performing the matching action | `skills-standard.md` (creating/editing skills), `file-naming-conventions.md` (creating files), `tag-taxonomy.md` (applying tags), `security-best-practices.md` (external integrations), `session-continuity.md` (logging), `bi-temporal-tracking.md` (updating entity frontmatter: `role`, `status`, `company`, `affiliation`), `two-output-rule.md` (invoking a skill with `two_output: true`) |
| **On first encounter** | First time in a session the topic arises | `conversational-interface.md`, `scripts-and-qa.md`, `kiro-integration.md` |

Agents SHOULD NOT preload all steering files at session start. Read them when the action demands it.

## Operational Protocols

1.  **Protocol Inheritance**: This file (`AGENTS.md`) is the root protocol.
2.  **Skills First**: Always check `.agent/skills/` and `.agent/SKILLS-REGISTRY.md` before implementing manually. If no matching skill exists, proceed directly — do not block.
3.  **Path Safety**: Vault root = the directory containing this `AGENTS.md` file. Resolve dynamically from the agent's working directory. Never hardcode drive letters or absolute paths.
4.  **Zettelkasten Enrichment**: Filing is connecting. Check atomicity (one idea per note), detect duplicates, discover connections (3-5 minimum; actively search before settling for fewer), insert `[[WikiLinks]]`, and add backlinks. Folder placement alone is insufficient. See `universal-triager` Step 3.
5.  **Source Catalog**: Every source encountered gets an entry in `03_Resources/RESOURCE-INDEX.md` Source Catalog table, even without a vault note. The `universal-triager` handles this for `03_Resources/` items.
6.  **Preserve Frontmatter**: Never strip YAML metadata from existing files.
7.  **Professional Standards**: Outputs intended for work or publication must be professional-grade.
8.  **Session Continuity**: Check `System/session-logs/YYYY-MM-DD/` when starting; auto-log on completion.
9.  **Protected Directories**: If you nest separate git repositories inside the vault (e.g., cloned tools under `02_Areas/`), never rename or move them, and add them to `.gitignore`.
10. **Area & Resource Intake**: Use [[02_Areas/AREA-INDEX]] for `02_Areas/` and [[RESOURCE-INDEX]] for `03_Resources/`. Update indexes when adding content.
11. **Obsidian CLI**: For vault-level operations (batch search, orphan detection, plugin management), use the `obsidian-cli` skill — not raw file-system tools.
12. **Local Git Snapshots**: The vault root is a local git repo (notes + config scope). Commits run **automatically at session end** via `.agent/scripts/vault-git-commit.ps1`. Never commit secrets or nested repos. See **Version Control** below.

## Version Control (Local Git)

The vault root is a **local git repository** (no remote) — a version history and undo safety net with a **notes + config** scope. Treat git as a background safety net; the owner should never need to run git by hand.

- **Tracked:** markdown notes + small text config. `.gitignore` excludes binary attachments, any nested git repos, caches, cloud-sync scratch files, and secrets.
- **Automatic commits:** a session-end snapshot runs `.agent/scripts/vault-git-commit.ps1`. Triggers: Claude `SessionEnd` hook (`.claude/settings.json`), Codex `Stop` hook (`.codex/hooks.json`), and Kiro `agentStop` hook (`.kiro/hooks/auto-commit-vault.kiro.hook`). The script purges cloud-sync-injected `desktop.ini` vault-wide, stages changes, runs a secret gate (AWS keys, private keys, GitHub/OpenAI-style/Google/Slack token patterns), and commits a timestamped snapshot **only when something changed**. Claude and Codex also write a deterministic session log first via `.agent/scripts/vault-session-log.ps1 -Agent <name>`.
- **History backup (off-root):** after each commit, `.agent/scripts/vault-git-bundle.ps1` writes a full `git bundle` to a configurable second location (default: `%USERPROFILE%\OneDrive\VaultBackups\`) — self-throttled to at most monthly, 3 rolling bundles, verified with `git bundle verify`. This protects history from a sync-account or disk failure. Restore: `git clone "<bundle>" restored-vault`.
- **NEVER commit secrets.** Add any secret-bearing file to `.gitignore` first; the commit script also auto-excludes files matching common key/token patterns.
- **Windows / cloud-sync gotchas:** if the vault lives in a synced folder (Google Drive, OneDrive), enable `core.longpaths true`, and expect `desktop.ini` injection — the commit script purges these each run.
- **Restore a note:** `git log -- "<file>"` then `git checkout <commit> -- "<file>"` (an agent task, never the owner's).

## Conflict Resolution & Error Handling

| Scenario | Resolution |
| :--- | :--- |
| **Concurrent triage**: Two agents process the same Inbox item | Check if the file has already been moved or has frontmatter with `status: processed` before triaging. If already processed, skip. |
| **Missing skill on disk**: SKILLS-REGISTRY.md references a skill that doesn't exist | Log a warning to the session log. Proceed without the skill. Do not create a stub. |
| **Broken WikiLink**: `[[Target]]` doesn't exist | Insert the link anyway (Obsidian shows broken links natively). Do NOT auto-create empty notes to satisfy links. |
| **Triage disagreement**: Agent's PARA routing conflicts with user's explicit placement | User placement wins. Do not move files the user has already placed. |
| **Stale archive**: User wants to reactivate archived content | Move from `04_Archives/` back to the appropriate PARA directory. Update frontmatter (`status`, dates). Re-index. This is a normal operation, not an exception. |
| **Duplicate detection**: A note substantially overlaps an existing note | Flag the overlap and ask the user whether to merge or keep separate. Do not auto-merge without confirmation. |

## Memory (Hot Cache)

> **Extracted:** Full detail in `.agent/steering/memory-hot-cache.md`

- **Owner**: {{OWNER_NAME}}, {{ROLE}}
- **Key projects**: {{PROJECT_1}}, {{PROJECT_2}}
- **Tone**: Professional for projects; Casual/Personal for inbox/notes
- Full glossary: `System/memory/glossary.md` | Profiles: `System/memory/people/` | Projects: `System/memory/projects/`

---
**Last Updated:** {{DATE}} | **Version:** 1.0 (Template release)
