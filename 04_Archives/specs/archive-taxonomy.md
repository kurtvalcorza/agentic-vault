---
title: 04_Archives — Taxonomy
status: active
version: 1.0
---

# Archive Taxonomy

How `04_Archives/` is organized. Mirrors the active PARA structure so locating archived content feels intuitive.

## Design Principles

1. **Mirror active PARA structure** — archive categories parallel `01_Projects`, `02_Areas`, `03_Resources`.
2. **Content-type separation** — agent artifacts are clearly separated from human-authored content.
3. **Date-first inside categories** — within a category, sort by year (`YYYY/` or `YYYY-MM/`).
4. **No dated dump directories at the root** — every cleanup event files into the correct category.
5. **Flat at the top, structured inside** — keep top-level categories to ~6.

## Structure

```
04_Archives/
├── ARCHIVE-INDEX.md          ← master index (update on every archival)
├── _projects/                ← completed/abandoned projects (mirrors 01_Projects)
│   └── <ProjectName>/
├── _areas/                   ← retired area content (mirrors 02_Areas)
│   └── <AreaName>/
├── _reports/                 ← periodic reports, by year
├── _skills/                  ← deprecated/superseded skills (with reason)
├── _agent-artifacts/         ← agent-generated content (NOT human-authored)
│   └── session-logs/YYYY-MM/ ← session-log folders older than 30 days
└── specs/                    ← this folder — archive system design docs
```

## Rules

- **Archival is decided by lifecycle + the owner's call** — is it off the work board, genuinely inactive? Never archive by folder location or import markers alone, and confirm scope with the user before bulk moves.
- Moves go **through the `archive-file` skill** (handles taxonomy placement + index row).
- Archived notes keep their frontmatter; add `status: archived` + `archived: YYYY-MM-DD`.
- **Reactivation is normal**: move back to the PARA tier, update frontmatter, re-index.
- Session-log folders older than **30 days** archive to `_agent-artifacts/session-logs/YYYY-MM/` (quarterly cadence).
