---
name: reconcile-vault
description: Scan vault notes for contradictory claims, outdated entity descriptions, and reversed decisions, then propose resolutions with provenance tracking. Use when checking for contradictions, reconciling vault content, finding conflicting claims about a topic, or running truth maintenance.
---

# reconcile-vault

Automatically detects and resolves contradictions across your vault by comparing factual claims, entity descriptions, and decision records. Uses recency and source authority heuristics to determine winners, creates conflict notes for ambiguous cases, and tracks changes with bi-temporal provenance.

## When to Use

- You suspect notes contain conflicting information about a person, project, or decision
- After a major organizational change (role changes, project pivots, policy reversals) to find stale references
- As periodic vault hygiene — run monthly or quarterly to catch drift
- When you want to validate that your `timeline` entries are well-formed

## Invocation

### Full Vault Scan

```
Reconcile my vault
Check for contradictions
Run truth maintenance
```

Scans all Markdown files in `01_Projects/`, `02_Areas/`, and `03_Resources/`. Excludes `04_Archives/` (archived notes are expected to contain outdated claims).

### Scoped Scan (by topic)

```
Find conflicting claims about Project Beacon
Reconcile my vault on the topic of Project Atlas
Check for contradictions about the owner's role
```

Limits the scan to notes matching the topic by title, tags, or content within the same directory scope.

## What It Detects

The skill identifies contradictions across three dimensions:

### 1. Conflicting Factual Claims

Two notes make mutually exclusive assertions about the same subject. For example, Note A says "Project Beacon uses cloud-first deployment" while Note B says "Project Beacon reverted to on-premise deployment." Complementary or differently-scoped claims are not flagged.

### 2. Outdated Entity Descriptions

A note describes a person, project, or organization with attributes that conflict with a newer note. For example, a team roster still lists someone's old role after they transferred teams.

### 3. Reversed or Superseded Decisions

A decision was made and later reversed, but notes referencing the original decision were never updated. For example, a project plan still references an approved cloud strategy after a steering committee reverted it.

## How Contradictions Are Resolved

Each detected contradiction is classified into one of three resolution paths:

### Clear Winner (Auto-Resolvable)

When one side wins on recency and/or authority (with the other being at least equal), the skill proposes updating the outdated note. A `## History` section is appended documenting what changed:

```markdown
## History

- **2026-04-05**: Changed "deployment strategy" from "cloud-first" to "on-premise". Source: [[2026-05-10 Steering Committee Minutes]]. Previous source: [[2026-01-30 Architecture Decision Record]]. Reason: newer source (2026-05-10 vs 2026-02-01), higher authority (official documentation vs structured report).
```

### Genuinely Ambiguous

When neither side clearly wins (e.g., equally recent, equally authoritative, or conflicting signals), the skill creates a conflict note in `Inbox/` for manual resolution:

```yaml
---
date: 2026-04-05
status: open
tags: [conflict, status/needs-review]
---

# Conflict — Project Beacon Deployment Strategy

## Claim A
Cloud-first deployment approved by architecture board — Source: [[Architecture Decision Record]]

## Claim B
On-premise deployment mandated by security review — Source: [[Security Review Findings]]

## Evidence
Architecture board approved cloud-first in January 2026 based on cost analysis.
Security review in March 2026 identified compliance issues requiring on-premise.
Both sources are official documentation from different governance bodies.
```

### Evolution (Entity Change Over Time)

When the discrepancy represents a legitimate change over time (not a contradiction), the skill proposes updating the note to reflect the current state. For notes with entity-like frontmatter fields (`role`, `status`, `company`, `affiliation`), a bi-temporal `timeline` entry is appended per the vault's tracking convention:

```yaml
timeline:
  - event_time: "2026-03-15"
    transaction_time: "2026-04-05"
    claim: "the owner moved from Project Atlas team to Project Dawn team"
    source: "[[2026-03-15 Team Announcement]]"
```

## Recency and Authority Heuristics

### Recency_Date Resolution

Each note's effective date is determined by this priority:

1. `updated` frontmatter field
2. `date` frontmatter field
3. File modification time (fallback)

### Source_Authority Ranking

Sources are ranked from most to least authoritative:

| Rank | Source Type | Example |
|------|------------|---------|
| 1 | Peer-reviewed | Research papers, journal articles |
| 2 | Official documentation | Board resolutions, policy documents |
| 3 | Structured report | Project reports, technical assessments |
| 4 | Blog post | Blog entries, informal write-ups |
| 5 | Transcript | Meeting transcripts, interview notes |
| 6 | Opinion | Personal notes, unattributed claims |

Authority is inferred using this resolution order:

1. Explicit `source_type` frontmatter field (highest priority)
2. Inferred from `tags` (e.g., `research` → peer-reviewed, `blog` → blog post)
3. Inferred from file location (e.g., `03_Resources/Research/` → peer-reviewed)
4. Default to "opinion" when no signal is available

## Confirmation Protocol

All proposed changes require explicit user approval before any files are modified:

1. The skill presents each proposed change with a diff-style preview (for edits) or full content preview (for new conflict notes)
2. The user can approve or reject each change individually (partial approval supported)
3. Only approved changes are written to the vault
4. Rejected changes are logged but not applied
5. The reconciliation report is saved regardless of approval decisions

No vault files are modified until the user explicitly approves each change.

## Timeline Entry Validation

During its scan, the skill validates any existing `timeline` frontmatter arrays against the bi-temporal tracking schema. Malformed entries are reported in the reconciliation summary under "Malformed Timeline Entries." The skill does not auto-fix malformed entries — it reports them for user review.

An entry is malformed if:
- `event_time` or `transaction_time` is missing or not a valid `YYYY-MM-DD` date
- `claim` is missing or empty
- `source` is missing
- The entry is not a valid YAML mapping

Notes with more than 20 timeline entries are flagged with a suggestion to prune older entries to a `{Note Name} (Timeline Archive).md` file.

## Output

### Reconciliation Report

Saved to `.agent/outputs/YYYY-MM-DD_reconciliation-report.md` and displayed in chat.

```markdown
# Reconciliation Report — {scope}
**Date:** YYYY-MM-DD
**Files scanned:** N
**Scope:** {topic or "full vault"}

## Auto-Resolvable Contradictions
| Note A | Note B | Claim A | Claim B | Winner | Reason |
|--------|--------|---------|---------|--------|--------|

## Ambiguous Contradictions (User Decision Required)
| Note A | Note B | Claim A | Claim B | Evidence A | Evidence B |
|--------|--------|---------|---------|------------|------------|

## Evolution Updates
| Note | Old State | New State | Timeline Entry Added |
|------|-----------|-----------|---------------------|

## Malformed Timeline Entries
| Note | Entry Index | Issue |
|------|-------------|-------|
```

### Conflict Notes

Created in `Inbox/` with `status: open` and tags `[conflict, status/needs-review]` for ambiguous contradictions requiring manual resolution.

### Session Log

Activity is logged to `System/session-logs/YYYY-MM-DD/` with scope, file count, contradiction counts, and approval outcomes.

## Error Handling

| Scenario | Behavior |
|:---------|:---------|
| Target directory missing | Skips that directory, logs warning, continues with others |
| Empty vault (no `.md` files) | Reports "no Markdown files found" and exits |
| File read failure | Logs warning, skips file, continues scanning |
| Malformed YAML frontmatter | Logs warning, skips file, continues scanning |
| No contradictions found | Reports "no contradictions detected" (healthy outcome) |
| Scan scope exceeds 500 files | Warns user, offers scoped scan on a specific topic |
| Topic matches no notes | Reports "no matching notes found" and exits |
| Note has >20 timeline entries | Suggests pruning per bi-temporal archival convention |

## Prerequisites

| Dependency | Path | Purpose |
|:-----------|:-----|:--------|
| Bi-temporal tracking steering | `.agent/steering/bi-temporal-tracking.md` | Timeline entry schema for evolution resolutions |
| Scan directories | `01_Projects/`, `02_Areas/`, `03_Resources/` | Content to scan (missing dirs are skipped) |
| Output directory | `.agent/outputs/` | Reconciliation report destination |
| Session log directory | `System/session-logs/YYYY-MM-DD/` | Activity logging |

## Related Skills

- `extract-concepts` — Health mode (Check 4) detects contradictions between concept hubs and suggests invoking `reconcile-vault` for detailed resolution
- `query-vault` — Q&A against vault content (complementary for investigating specific claims)
- `optimize-workspace` — General vault maintenance (complementary)
