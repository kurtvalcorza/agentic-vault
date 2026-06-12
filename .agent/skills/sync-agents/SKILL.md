---
name: sync-agents
description: Synchronizes CLAUDE.md and GEMINI.md with the master AGENTS.md file to ensure all agent configuration files are up-to-date. Use when AGENTS.md has been updated and symlinked copies need verification, or after editing agent configuration.
---

# Sync Agents Skill

## Purpose
Maintains consistency between the master `AGENTS.md` file and agent-specific copies (`CLAUDE.md`, `GEMINI.md`) by synchronizing their content.

## When to Use
- After editing `AGENTS.md`
- When setting up the vault for the first time
- As part of workspace maintenance routines
- Before committing changes to version control

## Trigger Phrases
- "Sync agent files"
- "Update CLAUDE.md and GEMINI.md"
- "Sync AGENTS.md"

## Implementation

### Script Location
`.agent/scripts/sync-agents.ps1`

### Execution
```powershell
powershell -ExecutionPolicy Bypass -File .agent/scripts/sync-agents.ps1
```

### What It Does
1. Locates the vault root dynamically
2. Copies `AGENTS.md` to `CLAUDE.md`
3. Copies `AGENTS.md` to `GEMINI.md`
4. Reports success or failure

## Notes
- This is necessary because the filesystem doesn't support hardlinks/symlinks
- Always run this after modifying `AGENTS.md`
- The script uses dynamic path resolution for portability
