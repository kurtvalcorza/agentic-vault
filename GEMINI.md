# Gemini CLI: Vault Instructions

> **Source of Truth:** This file is a **derived digest** of [[AGENTS.md]]. Refer to [[AGENTS.md]] for the canonical version of all protocols. If anything here conflicts with AGENTS.md, AGENTS.md wins.
> **Synced with AGENTS.md version:** 1.0

## Project Overview
This is the personal knowledge management (PKM) vault of **{{OWNER_NAME}}**. It uses a **Hybrid PARA + Zettelkasten** structure to organize projects, long-term knowledge, and references.

## Core Protocols (Mandatory)

### 1. Organizational Structure (PARA)
- **`Inbox/`**: Initial capture. All items must be triaged.
- **`01_Projects/`**: Active work with deadlines. Live work queue is the Kanban board [[01_Projects/To Do]] — do not restructure the board or strip its `kanban-plugin` frontmatter / `%% kanban:settings %%` block.
- **`02_Areas/`**: Long-term authored knowledge. See [[02_Areas/AREA-INDEX]].
- **`03_Resources/`**: External references. Update [[RESOURCE-INDEX]] Source Catalog when adding.
- **`04_Archives/`**: Completed/inactive work, per [[04_Archives/specs/archive-taxonomy]].

### 2. Zettelkasten Enrichment
- **Atomicity**: One idea per note.
- **Connectivity**: Maintain **3-5 [[WikiLinks]]** per note. Actively search for connections; do not settle for isolation.
- **Filing is Connecting**: Folder placement is secondary to dense bidirectional linking.

### 3. Session & Tooling
- **Skills First**: Check `.agent/skills/` and `.agent/SKILLS-REGISTRY.md` before manual implementation. If no matching skill exists, proceed directly — do not block.
- **Session Continuity**: Logs are stored in `System/session-logs/YYYY-MM-DD/` with `agent: gemini` provenance frontmatter. Check today's logs before starting work.
- **Steering Priority**: Do NOT preload all steering files. Read `.agent/steering/` files on the relevant action, per the Steering File Priority table in [[AGENTS.md]].
- **Path Safety**: Use relative paths from the vault root. Never hardcode drive letters.
- **Frontmatter**: Preserve all YAML metadata in existing notes.

### 4. Version Control (Local Git)
- The vault root is a **local git repo** (notes + config scope, no remote) — a background safety net. Never hand the owner git tasks.
- Session-end snapshots run `.agent/scripts/vault-git-commit.ps1` (other agents' hooks trigger this automatically; Gemini sessions may run it manually at end of work).
- **NEVER commit secrets** or nested git repos.

### 5. Security & Standards
- **PII/Secrets**: Never store API keys or unmasked PII in markdown notes.
- **Tone**: Professional for `01_Projects/`, `02_Areas/`, `03_Resources/`, `.agent/outputs/`; casual for `Inbox/` and personal notes.

## Key Directories
- **`.agent/`**: Shared write space for agent outputs, skills, scripts, steering, and registries. The ONLY shared write space — other agents' config dirs are read-only.
- **`System/`**: Templates, memory (glossary, people, projects), and session logs.

---
**Note to Gemini:** Always adhere to the "Agent Skills Standard" in `.agent/steering/skills-standard.md` when creating or modifying skills, and use generic capability names from `.agent/TOOL-TAXONOMY.md` in shared skills.
