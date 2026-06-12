---
name: reconcile-vault
description: Scan vault notes for contradictory claims, outdated entity descriptions, and reversed decisions, then propose resolutions with provenance tracking. Use when checking for contradictions, reconciling vault content, finding conflicting claims about a topic, or running truth maintenance.
---

# reconcile-vault

Detects and resolves contradictions across vault notes by comparing factual claims, entity descriptions, and decision records. Evaluates conflicts using recency and source authority heuristics, proposes updates with `## History` sections for clear winners, creates conflict notes for ambiguous cases, and appends bi-temporal timeline entries for evolutionary changes. All proposed modifications require user confirmation before being applied.

## Trigger Phrases

- "Check for contradictions"
- "Reconcile my vault"
- "Find conflicting claims about [topic]"
- "Run truth maintenance"
- "Are there any inconsistencies in my notes about [topic]?"

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| topic | No | *(full scan)* | Limits scan to notes matching the topic by title, tags, or content. When omitted, scans all notes in scope. |

---

## Step 1 — Determine Scan Scope

### Step 1.1 — Enumerate Target Files

```
**Tool:** file-search
Recursively find all `.md` files in:
  - `01_Projects/`
  - `02_Areas/`
  - `03_Resources/`

Explicitly EXCLUDE `04_Archives/` — archived notes are expected to contain outdated claims.
```

If a target directory does not exist, log a warning and skip it. Continue with remaining directories.

### Step 1.2 — Large Vault Warning

Count the total number of Markdown files found across all three directories.

**If the count exceeds 500 files:**

```
**Tool:** user-interact
"Your vault contains {N} Markdown files in the scan scope. A full reconciliation
scan may take a while. Would you like to:
  1. Continue with the full scan
  2. Run a scoped scan on a specific topic instead"
```

If the user chooses a scoped scan, prompt for a topic and proceed to Step 1.3.

### Step 1.3 — Apply Topic Filter (if topic argument provided)

When a topic argument is provided (either from invocation or from the large vault warning redirect):

Filter the file list to notes matching the topic by:
- **Title match**: note title or filename contains the topic (case-insensitive)
- **Tag match**: note frontmatter `tags` array contains a tag matching the topic
- **Content match**: note body contains the topic string

```
**Tool:** content-search
Search for the topic string across the enumerated files.
```

Retain only files matching at least one criterion.

### Step 1.4 — Empty Vault Check

If no Markdown files remain after enumeration and filtering:

Report "No Markdown files found in scan scope" and exit gracefully. Log the empty result to the session log.

---

## Step 2 — Read and Parse Notes

### Step 2.1 — Extract Note Metadata

For each file in the scan scope:

```
**Tool:** file-read
Read the file content.
```

Extract:
- **Frontmatter fields**: all YAML fields, especially `updated`, `date`, `status`, `role`, `company`, `affiliation`, `source_type`, `tags`
- **Title**: from frontmatter `title` field, or first `# heading`, or filename
- **Factual claims**: statements of fact about entities, statuses, decisions, dates, roles, affiliations
- **WikiLinks**: all `[[Link Target]]` references
- **Timeline entries**: existing `timeline` frontmatter array (if present)

**If a file cannot be read** (permissions, encoding, corruption): log a warning, skip the file, continue with remaining files.

**If YAML frontmatter is malformed**: log a warning, skip the file, continue with remaining files.

### Step 2.2 — Resolve Recency_Date for Each Note

For each note, determine its effective date using this priority order:

1. `updated` frontmatter field (if present and valid ISO 8601 date)
2. `date` frontmatter field (if present and valid ISO 8601 date)
3. File modification time (fallback)

Store the resolved Recency_Date alongside each note's metadata.

### Step 2.3 — Resolve Source_Authority for Each Note

For each note, determine its authority level using this inference chain:

1. **Explicit `source_type` frontmatter field** — if present, use directly
2. **Inferred from `tags`** — map tags to authority levels:
   - Tags containing `research`, `academic`, `peer-reviewed` → "peer-reviewed"
   - Tags containing `documentation`, `official` → "official documentation"
   - Tags containing `report` → "structured report"
   - Tags containing `blog` → "blog post"
   - Tags containing `transcript`, `meeting` → "transcript"
3. **Inferred from file location**:
   - `03_Resources/Research/` → "peer-reviewed" (academic context)
4. **Default** — when no signal is available → "opinion"

**Authority Ranking** (strict total order, highest to lowest):

| Rank | Source Type |
|------|------------|
| 1 | peer-reviewed |
| 2 | official documentation |
| 3 | structured report |
| 4 | blog post |
| 5 | transcript |
| 6 | opinion |

---

## Step 3 — Detect Contradictions

Compare notes pairwise (or in topic-scoped clusters) to identify contradictions across three dimensions.

### Dimension 1 — Conflicting Factual Claims

Two notes make mutually exclusive assertions about the same subject:
- Note A says "X uses approach A" while Note B says "X uses approach B"
- Note A states a date/figure that conflicts with Note B's date/figure
- Note A attributes a role/affiliation that conflicts with Note B

**Detection method**: This relies on LLM judgment. Compare factual claims extracted in Step 2.1 across note pairs. Flag pairs where claims are mutually exclusive. Complementary or differently-scoped claims are NOT contradictions.

### Dimension 2 — Outdated Entity Descriptions

A note describes an entity (person, project, organization) with attributes that conflict with a newer note:
- Person's role changed but old note still shows previous role
- Project status changed but related notes still reference old status
- Organization structure changed but notes reference old structure

**Detection method**: For notes with entity-like frontmatter fields (`role`, `status`, `company`, `affiliation`), compare values across notes referencing the same entity. Flag where older notes have stale values.

### Dimension 3 — Reversed or Superseded Decisions

A decision was made and later reversed, but notes referencing the original decision were never updated:
- Decision note says "approved cloud deployment" but a later note says "reverted to on-premise"
- Policy note references a superseded guideline

**Detection method**: Look for decision-related language ("decided", "approved", "adopted", "reverted", "cancelled", "superseded") and trace whether downstream notes reflect the latest decision state.

---

## Step 4 — Validate Timeline Entries

During the scan, validate any existing `timeline` frontmatter arrays per the bi-temporal tracking schema (`.agent/steering/bi-temporal-tracking.md`).

An entry is **malformed** if any of the following are true:
- `event_time` is missing or not a valid ISO 8601 date (`YYYY-MM-DD`)
- `transaction_time` is missing or not a valid ISO 8601 date (`YYYY-MM-DD`)
- `claim` is missing or empty
- `source` is missing
- The entry is not a valid YAML mapping

Collect all malformed entries for the reconciliation report.

**If a note has more than 20 timeline entries**: flag it with a suggestion to prune per the bi-temporal steering file's archival convention (`{Note Name} (Timeline Archive).md`).

---

## Step 5 — Classify and Resolve Contradictions

For each detected contradiction, classify it and determine the resolution strategy.

### Step 5.1 — Evaluate Winner

For each contradiction, compare the two sides:

1. **Recency**: Compare Recency_Date values (resolved in Step 2.2)
2. **Authority**: Compare Source_Authority levels (resolved in Step 2.3)

### Step 5.2 — Classification and Resolution

```
Contradiction Found
       │
       ▼
   ┌─────────────────────────────────────────────┐
   │ Does one side win on BOTH recency            │
   │ AND authority (or at least one, with the     │
   │ other being equal)?                          │
   └──────────┬──────────────────┬────────────────┘
              │ Yes              │ No
              ▼                  ▼
   ┌──────────────────┐  ┌─────────────────────────┐
   │ Is this an        │  │ Genuinely Ambiguous      │
   │ evolution (entity │  │ → Create conflict note   │
   │ change over time)?│  │   in Inbox/              │
   └───┬──────────┬────┘  └─────────────────────────┘
       │ Yes      │ No
       ▼          ▼
   ┌──────────┐ ┌──────────────────────┐
   │ Evolution │ │ Clear Winner          │
   │ → Update  │ │ → Update with         │
   │ with      │ │   ## History section   │
   │ timeline  │ └──────────────────────┘
   │ entry     │
   └──────────┘
```

#### Resolution A — Clear Winner (recency + authority)

Propose an update to the outdated note:
- Correct the outdated claim/field to match the winning note
- Append a `## History` entry at the end of the note (or to an existing `## History` section):

```markdown
## History

- **{YYYY-MM-DD}**: Changed "{field or claim}" from "{old value}" to "{new value}". Source: [[New Source Note]]. Previous source: [[Old Source Note]]. Reason: {recency/authority justification}.
```

- **Preserve all existing frontmatter fields** — only modify the specific field(s) that are outdated.

#### Resolution B — Genuinely Ambiguous

Create a conflict note in `Inbox/`:

```yaml
---
date: {YYYY-MM-DD}
status: open
tags: [conflict, status/needs-review]
---

# Conflict — {Subject}

## Claim A
{Description} — Source: [[Note A]]

## Claim B
{Description} — Source: [[Note B]]

## Evidence
{Summary of evidence for each side}
```

#### Resolution C — Evolution (entity change over time)

Propose updating the note to reflect the current state. If the note has entity-like frontmatter fields (`role`, `status`, `company`, `affiliation`), append a `timeline` entry per the bi-temporal tracking schema:

```yaml
timeline:
  - event_time: "{YYYY-MM-DD}"
    transaction_time: "{today's date}"
    claim: "{description of what changed}"
    source: "[[Source Note]]"
```

- Preserve all existing timeline entries (append-only).
- Preserve all existing frontmatter fields.
- Update the specific field(s) to reflect the current state.

If the note does NOT have entity-like frontmatter fields, propose the update with a `## History` section instead (same as Resolution A).

---

## Step 6 — Generate Reconciliation Report

Build the reconciliation summary report with four sections.

```markdown
# Reconciliation Report — {scope}
**Date:** {YYYY-MM-DD}
**Files scanned:** {N}
**Scope:** {topic or "full vault"}

## Auto-Resolvable Contradictions
| Note A | Note B | Claim A | Claim B | Winner | Reason |
|--------|--------|---------|---------|--------|--------|
| [[Note]] | [[Note]] | {claim} | {claim} | {winner} | {reason} |

## Ambiguous Contradictions (User Decision Required)
| Note A | Note B | Claim A | Claim B | Evidence A | Evidence B |
|--------|--------|---------|---------|------------|------------|
| [[Note]] | [[Note]] | {claim} | {claim} | {evidence} | {evidence} |

## Evolution Updates
| Note | Old State | New State | Timeline Entry Added |
|------|-----------|-----------|---------------------|
| [[Note]] | {old} | {new} | Yes / N/A — no entity fields |

## Malformed Timeline Entries
| Note | Entry Index | Issue |
|------|-------------|-------|
| [[Note]] | {index} | {description of issue} |
```

*Note: "Timeline Entry Added" is "Yes" when the note has entity-like frontmatter fields (`role`, `status`, `company`, `affiliation`) per bi-temporal scope rules, "N/A — no entity fields" otherwise.*

**If no contradictions are found**: report "No contradictions detected — vault is internally consistent" (this is a healthy outcome, not an error).

---

## Step 7 — Present Proposed Changes (Confirmation_Protocol)

Present ALL proposed changes to the user before modifying any files.

### Step 7.1 — Present Auto-Resolvable Changes

For each clear-winner resolution:

```
### Proposed Update: [[Note Name]]
**Contradiction with:** [[Other Note]]
**Change:** Update "{field}" from "{old value}" to "{new value}"
**Reason:** {newer by date / higher authority / both}

**Diff:**
```diff
- old content line
+ new content line
```

**Approve / Reject?**
```

### Step 7.2 — Present Conflict Notes

For each ambiguous contradiction:

```
### New Conflict Note: Conflict — {Subject}
**Between:** [[Note A]] and [[Note B]]

{Full preview of the conflict note content}

**Create this conflict note in Inbox/? Approve / Reject?**
```

### Step 7.3 — Present Evolution Updates

For each evolution-type update:

```
### Proposed Evolution Update: [[Note Name]]
**Change:** Update "{field}" from "{old value}" to "{new value}"
**Timeline entry:** Will append bi-temporal entry

**Diff:**
```diff
- old content line
+ new content line
```

**Approve / Reject?**
```

```
**Tool:** user-interact
Present all proposed changes and collect approval/rejection for each.
```

Support partial approval — the user may approve some changes and reject others.

---

## Step 8 — Apply Approved Changes

### Step 8.1 — Apply Auto-Resolvable Updates

For each approved clear-winner resolution:

```
**Tool:** file-read
Read the target note.
```

- Update the outdated field/claim
- Append the `## History` entry (to existing `## History` section if present, otherwise create it at the end of the file)
- **Preserve all existing frontmatter fields**

```
**Tool:** file-edit
Apply the approved changes to the target note.
```

### Step 8.2 — Create Conflict Notes

For each approved conflict note:

```
**Tool:** file-write
Write the conflict note to `Inbox/Conflict — {Subject}.md`
```

### Step 8.3 — Apply Evolution Updates

For each approved evolution update:

```
**Tool:** file-read
Read the target note.
```

- Update the specific field(s) to reflect current state
- If note has entity-like frontmatter fields: append `timeline` entry to frontmatter
- If note does NOT have entity-like fields: append `## History` entry instead
- **Preserve all existing frontmatter fields and timeline entries**

```
**Tool:** file-edit
Apply the approved changes to the target note.
```

---

## Step 9 — Save Report and Log

### Step 9.1 — Save Reconciliation Report

```
**Tool:** file-write
Write the reconciliation report to `.agent/outputs/{YYYY-MM-DD}_reconciliation-report.md`
```

Display the report summary in chat as well.

### Step 9.2 — Log to Session Log

Log the reconciliation activity to `System/session-logs/{YYYY-MM-DD}/`:

- Skill invoked: `reconcile-vault`
- Scope: full vault or topic
- Files scanned: count
- Contradictions found: count by type (auto-resolvable, ambiguous, evolution)
- Malformed timeline entries: count
- Changes proposed: count
- Changes approved: count
- Changes rejected: count

---

## Required Capabilities

| Capability | Usage |
|:-----------|:------|
| `file-read` | Read vault notes, existing frontmatter, timeline entries |
| `file-write` | Create conflict notes in `Inbox/`, save reconciliation report |
| `file-edit` | Update outdated notes with corrections and `## History` / timeline entries |
| `file-search` | Enumerate `.md` files across `01_Projects/`, `02_Areas/`, `03_Resources/` |
| `content-search` | Search for topic matches, entity references, decision language |
| `user-interact` | Large vault warning, Confirmation_Protocol for all proposed changes |

### Referenced Policies

| Policy | Path | Purpose |
|:-------|:-----|:--------|
| Bi-temporal tracking | `.agent/steering/bi-temporal-tracking.md` | Timeline entry schema for evolution resolutions |
| Two-output rule | `.agent/steering/two-output-rule.md` | This skill is explicitly EXCLUDED (primary function already proposes vault modifications) |

---

## Error Handling

| Scenario | Action |
|:---------|:-------|
| Target directory missing (`01_Projects/`, `02_Areas/`, or `03_Resources/` does not exist) | Log warning, skip that directory, continue with remaining directories |
| Empty vault (no Markdown files found in any scanned directory) | Report "No Markdown files found in scan scope" and exit gracefully |
| File read failure (permissions, encoding, corruption) | Log warning, skip the file, continue scanning |
| Malformed YAML frontmatter in a note | Log warning, skip the file, continue scanning |
| No contradictions found | Report "No contradictions detected — vault is internally consistent" (healthy outcome) |
| Scan scope exceeds 500 Markdown files | Warn user via `user-interact`, offer scoped scan on a specific topic |
| Note has >20 timeline entries | Flag in report with suggestion to prune per bi-temporal steering file archival convention |
| Topic argument matches no notes | Report "No matching notes found for topic '{topic}'" and exit gracefully |

---

## Examples

### Full Vault Scan

**User:** Reconcile my vault.

**Agent:**
1. Scanning `01_Projects/`, `02_Areas/`, `03_Resources/` — found 247 Markdown files.
2. Parsed metadata and resolved dates/authority for all notes.
3. Detected 3 contradictions:
   - 1 auto-resolvable (role change with clear recency winner)
   - 1 ambiguous (conflicting project timelines from equally authoritative sources)
   - 1 evolution (project status update)
4. Found 1 malformed timeline entry in `02_Areas/People/the vault owner.md` (missing `source` field at index 2).

**Proposed Changes:**

### Proposed Update: [[Project Atlas Team Roster]]
**Contradiction with:** [[2026-03-15 Team Announcement]]
**Change:** Update "role" from "Project Information Officer — Project Atlas" to "Project Information Officer — Project Dawn"
**Reason:** [[2026-03-15 Team Announcement]] is newer (2026-03-15 vs 2025-06-01) and is an official documentation source.

**Approve / Reject?**

*(... more proposals ...)*

### Scoped Scan

**User:** Find conflicting claims about Project Beacon.

**Agent:**
1. Scanning for notes matching "Project Beacon" — found 12 notes across `01_Projects/` and `02_Areas/`.
2. Detected 1 contradiction: deployment strategy conflict (cloud vs on-premise).
3. No malformed timeline entries.

*(... proposals ...)*

### No Contradictions Found

**User:** Check for contradictions.

**Agent:**
1. Scanning `01_Projects/`, `02_Areas/`, `03_Resources/` — found 183 Markdown files.
2. No contradictions detected — vault is internally consistent.
3. Validated 14 timeline entries across 5 notes — all well-formed.

Report saved to `.agent/outputs/2026-04-05_reconciliation-report.md`.
