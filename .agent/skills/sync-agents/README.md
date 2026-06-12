# Sync Agents

Keeps your agent configuration files in sync.

## What It Does
Copies the master `AGENTS.md` file to `CLAUDE.md` and `GEMINI.md` so all AI agents see the same instructions.

## When to Use
Run this whenever you update `AGENTS.md`:
- "Sync agent files"
- "Update CLAUDE.md and GEMINI.md"

## Why This Exists
Since the vault is on a filesystem that doesn't support symlinks or hardlinks, we maintain synchronized copies instead. This skill automates that process.
