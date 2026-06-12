# Universal Triager

Consolidated triage agent for vault organization. Scans `Inbox/` and suggests moves to the correct PARA destination.

## When to Use

- "Check my inbox" / "Triage my inbox"
- Inbox overflowing with captures
- Quarterly workspace cleanup
- After bulk imports or document conversions

## What It Does

1. Scans `Inbox/` for all files
2. Applies PARA decision flowchart (authored? deadline? ongoing? inactive?)
3. Runs Zettelkasten enrichment: atomicity check, duplicate/overlap detection, connection discovery, and connection-informed routing refinement
4. Routes to `01_Projects/`, `02_Areas/{sub-area}/`, `03_Resources/{category}/`, or `04_Archives/`
5. Presents a confidence-scored triage table with Zettelkasten flags (compound notes, overlaps, suggested links)
6. Executes moves on confirmation — preserves frontmatter, inserts WikiLinks, adds backlinks to related notes, updates Source Catalog for `03_Resources/` items

## PARA Routing Summary

| Content Type | Destination |
|-------------|-------------|
| Active project deliverable | `01_Projects/{project}/` |
| Ongoing domain knowledge (authored) | `02_Areas/{sub-area}/` |
| External reference, PDF, bookmark | `03_Resources/` |
| Inactive / completed / superseded | `04_Archives/` (via `archive-file`) |

## Operation Mode

**Suggestion Mode** (default) — proposes moves with reasoning, waits for confirmation. Supports batch or item-by-item approval.

## Replaces

- `triage-inbox` (deprecated)
- `triage-journal` (deprecated)
- `triage-notes` (deprecated)

## Works With

- `archive-file` — For items routed to Archives
- `optimize-workspace` — Full vault maintenance
- `write-note` — Atomic note creation and splitting compound notes
- `RESOURCE-INDEX.md` — Source Catalog updated when items move to `03_Resources/`
