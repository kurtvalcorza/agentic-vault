# Gemini CLI: Vault Instructions

> **Source of Truth:** This file is a **derived digest** of [[AGENTS.md]]. Refer to [[AGENTS.md]] for the canonical version of all protocols. If anything here conflicts with AGENTS.md, AGENTS.md wins.
> **Synced with AGENTS.md version:** 1.4

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
- **Operating Method (Ultramode)**: Before substantive multi-step work (audits, builds, multi-file changes), follow `.agent/steering/ultramode.md` (or invoke `/ultramode`). Headline rule: re-verify any sub-agent / `COMPLETE` / second-hand claim against the source before acting. Also: verify before claiming; stay in scope and reversible; decision-gate genuine forks; lead with the outcome and close with state. Buys auditability, not baseline correctness; AGENTS.md and voice win on conflict.
- **Session Continuity**: Logs are stored in `System/session-logs/YYYY-MM-DD/` with `agent: gemini` provenance frontmatter. Check today's logs before starting work.
- **Steering Priority**: Do NOT preload all steering files. Read `.agent/steering/` files on the relevant action, per the Steering File Priority table in [[AGENTS.md]].
- **Audit Cadence**: On/after quarter boundaries (Mar/Jun/Sep/Dec 1), check `System/AUDIT-LOG.md`; if the current quarter has no entry, prompt to run `optimize-workspace`. Pruning is human-gated.
- **Path Safety**: Use relative paths from the vault root. Never hardcode drive letters.
- **Frontmatter**: Preserve all YAML metadata in existing notes.

### 4. Version Control (Local Git)
- The vault root is a **local git repo** (notes + config scope, no remote) — a background safety net. Never hand the owner git tasks.
- Session-end snapshots run `.agent/scripts/vault-git-commit.ps1` (other agents' hooks trigger this automatically; Gemini sessions may run it manually at end of work).
- **NEVER commit secrets** or nested git repos.

### 5. Knowledge Runtime & MCP (optional — read AGENTS.md § Knowledge Runtime & MCP before use)
- `.agent/knowledge/` is an **optional** typed knowledge layer: a disposable SQLite projection of the Markdown (entities, relations, claims, evidence, provenance, graph). Markdown stays canonical. **If it is not installed, fall back to ordinary vault search rather than blocking.**
- **`objects: 0` is expected** on an existing vault — a note joins the semantic graph only when it has **both** `id` and `type`. Everything else is still indexed for navigation.
- The build **fails closed**: one unparseable file blocks the whole index. Dot-directories are skipped automatically; drop a `.knowledge-ignore` file in any *non-dot* scaffolding tree.
- **Writes are off by default on every entry point.** `AGENTIC_VAULT_KNOWLEDGE_READ_ONLY` is honoured identically by MCP and the CLI: `knowledge_apply_patch` / `knowledge_apply_batch` raise, and `vault-knowledge apply-patch` / `apply-batch` refuse with exit code 2. Setting it to `0` lets an agent edit canonical Markdown — an outward state change; confirm with the owner first. `propose` and `validate-*` are unaffected.
- Never edit the generated database as knowledge; it is derived and rebuildable.
- **MCP wiring uses absolute paths in `.mcp.json`** — the narrow Path Safety exception for machine-local, gitignored client config launched by an external process. Keep absolute paths out of scripts and tracked files.
- **Connecting any MCP server to this vault:** check its write surface first — some expose ungated file delete/overwrite, and git only snapshots at session end. Keep credentials to **one copy**: a gitignored `mcp.json` is fine when a credential has no other home, but if it already lives in a plugin's own gitignored config, read it from there at runtime rather than duplicating it.

### 6. Security & Standards
- **PII/Secrets**: Never store API keys or unmasked PII in markdown notes.
- **Tone**: Professional for `01_Projects/`, `02_Areas/`, `03_Resources/`, `.agent/outputs/`; casual for `Inbox/` and personal notes. House voice → `.agent/steering/voice.md`; what to avoid → `.agent/steering/anti-style.md`.

## Key Directories
- **`.agent/`**: Shared write space for agent outputs, skills, scripts, steering, and registries. The ONLY shared write space — other agents' config dirs are read-only.
- **`System/`**: Templates, memory (glossary, people, projects), and session logs.

---
**Note to Gemini:** Always adhere to the "Agent Skills Standard" in `.agent/steering/skills-standard.md` when creating or modifying skills, and use generic capability names from `.agent/TOOL-TAXONOMY.md` in shared skills.
