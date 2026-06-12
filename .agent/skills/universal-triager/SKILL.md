---
name: universal-triager
description: "Consolidated triage agent for Inbox, Journal, and Notes. Scans the specified source and suggests moves. Use when organizing scattered notes, triaging Inbox items, sorting Journal entries, or cleaning up Notes."
---

# Universal Triage Agent

## Purpose

Scan a source directory (`Inbox/`) and suggest moves to the correct PARA destination. Operates in **Suggestion Mode** — propose moves, wait for approval, then execute.

> This is the single triage skill for all vault organization. It replaces the deprecated `triage-inbox`, `triage-journal`, and `triage-notes` skills.

## How to Invoke

**Agent:** triggers on:
- "Check my inbox"
- "Triage my inbox"
- "Triage the vault"
- "Organize my captures"
- "Clean up inbox"

## Required Capabilities

- `file-read` — Read file contents and frontmatter
- `file-search` — Find files in source directories
- `content-search` — Search file contents for project keywords
- `file-write` — Generate triage report
- `command-exec` — Move files on approval

## Pre-Execution

1. Read `AGENTS.md` to get current active projects and directory structure.
2. Read `02_Areas/area-intake-policy.md` for PARA boundary rules.
3. Note the current `02_Areas/` sub-areas and `03_Resources/` categories.

## PARA Decision Flowchart

For each file in the source directory, apply this logic:

```
Is this content authored by the vault owner?
├── NO → Is it a binary attachment (PDF, image, etc.)?
│   ├── YES → 03_Resources/Attachments/
│   └── NO → Is it a bookmark, link collection, or reading list?
│       ├── YES → 03_Resources/Bookmarks/ or 03_Resources/Reading-List/
│       └── NO → 03_Resources/Reference/
│
└── YES → Does it have a completion date or deadline?
    ├── YES → Is it tied to an active project?
    │   ├── YES → 01_Projects/{ProjectName}/
    │   └── NO → 01_Projects/ (new project or standalone deliverable)
    │
    └── NO → Is it ongoing knowledge or responsibility?
        ├── YES → 02_Areas/{matching sub-area}/
        │   Route by domain:
        │   ├── AI, ML, data science, governance → AI_and_Data_Science/
        │   ├── Photography, multimedia → Creative_Media/
        │   ├── Languages, frameworks, cloud, blockchain → Development/
        │   ├── Game notes → Gaming/
        │   ├── Writing, comms, lit review, panels → Professional_Skills/
        │   ├── Tool installs, configs, dev tools → Tools/
        │   └── Cover letters, job apps, personal → Personal_Documents/
        │
        └── NO → Is it inactive with no active references?
            ├── YES → 04_Archives/ (suggest archive-file skill)
            └── NO → Keep in Inbox/ and flag for clarification
```

## Confidence Scoring

| Level | Criteria |
|-------|----------|
| **High** | Clear project keyword match, obvious domain fit, or explicit metadata |
| **Medium** | Partial keyword match, ambiguous domain, or missing frontmatter |
| **Low** | No clear destination; needs human judgment |

## Workflow

### Step 1: Scan

1. List all files in `Inbox/`.
2. Read each text-based file (title, frontmatter, first ~50 lines).
3. Note binary files (PDFs, images) separately.

### Step 2: Analyze (PARA Routing)

For each file, determine:
- **Destination** using the PARA Decision Flowchart above
- **Confidence** (High / Medium / Low)
- **Reasoning** (one-line justification)
- **Frontmatter action**: preserve existing YAML; for files moving to `02_Areas/`, note if frontmatter needs to be added per `area-frontmatter-schema`

### Step 3: Zettelkasten Enrichment

After PARA routing but before reporting, apply Zettelkasten principles to each text-based file. Skip this step for binary files (PDFs, images).

#### 3a. Atomicity Check

Read the note content and assess whether it contains a single idea or multiple distinct ideas.

| Assessment | Action |
|-----------|--------|
| **Atomic** (one clear idea) | Proceed as-is |
| **Compound** (2-3 distinct ideas) | Flag for splitting. In the triage report, note: "⚠️ Compound note — suggest splitting into N atomic notes via `write-note` skill" |
| **Brain dump** (4+ ideas or unstructured) | Flag for processing. Note: "⚠️ Brain dump — suggest processing through `write-note` skill before filing" |

Do not auto-split. Flag and let the user decide.

#### 3b. Duplicate/Overlap Detection

Search for existing notes that cover the same concept:

```
**Tool:** content-search
Search for the note's core concept/title across 02_Areas/, Notes/, and 01_Projects/.
```

| Finding | Action |
|---------|--------|
| **No overlap** | Proceed normally |
| **Partial overlap** | Flag: "🔗 Related note exists: [[Existing Note]] — consider extending it rather than filing separately" |
| **Near-duplicate** | Flag: "⚠️ Possible duplicate of [[Existing Note]] — suggest merging" |

#### 3c. Connection Discovery & Link Insertion

For each note, identify 3-5 related existing notes using:
1. Keyword/concept matching against `02_Areas/AREA-INDEX` and `03_Resources/RESOURCE-INDEX.md`
2. Content search for key terms from the note

Record these as **Suggested WikiLinks** for the triage report. On execution (Step 5), these links will be inserted into the note body.

#### 3d. Connection-Informed Routing

If the PARA flowchart produced a Medium or Low confidence destination, use the discovered connections to refine:
- If 3+ related notes cluster in a specific `02_Areas/` sub-area, prefer that destination
- If the note's strongest connections are to a specific project, route there instead
- Note any routing changes in the Reasoning column: "Routed by connection affinity to [[X]], [[Y]]"

### Step 4: Report

Present a triage table grouped by destination confidence:

```markdown
# Triage Report — YYYY-MM-DD

## Zettelkasten Flags
| File | Flag | Detail |
|:-----|:-----|:-------|
| `big-idea.md` | ⚠️ Compound | 3 distinct ideas — suggest splitting via `write-note` |
| `react-hooks.md` | 🔗 Overlap | Related: [[React Patterns]] — consider extending |

## High Confidence
| File | Destination | Reasoning | Links |
|:-----|:------------|:----------|:------|
| `beacon-api-notes.md` | `01_Projects/Project Beacon/` | Mentions Project Beacon API endpoints | `[[Project Beacon]]` |
| `react-patterns.md` | `02_Areas/Development/` | Framework guide, ongoing reference | `[[Development]]` |
| `paper.pdf` | `03_Resources/Reference/` | External paper, not authored | — |

## Medium Confidence
| File | Destination | Reasoning | Links |
|:-----|:------------|:----------|:------|
| `meeting-notes-mar.md` | `01_Projects/Project Atlas/` | Mentions Project Atlas but unclear scope | `[[Project Atlas]]` |

## Low Confidence (Needs Input)
| File | Question |
|:-----|:---------|
| `random-idea.md` | Atomic note or project seed? |

## Frontmatter Gaps
| File | Destination | Missing Fields |
|:-----|:------------|:---------------|
| `react-patterns.md` | `02_Areas/Development/` | `area`, `type`, `tags` |
```

### Step 5: Execute (On Approval)

**Agent:** asks: "Want me to execute these moves? I can handle High-confidence items automatically, or go item-by-item."

- **YES (all)**: Move High + Medium confidence items. Add missing frontmatter for `02_Areas/` files.
- **YES (selective)**: Go item-by-item for approval.
- **NO**: Ask for feedback and re-analyze.

On move:
- Preserve existing YAML frontmatter.
- For `02_Areas/` destinations: add frontmatter per `area-frontmatter-schema` if missing.
- **Bi-temporal tracking**: if triage updates an entity-like factual field (`role`, `status`, `company`, `affiliation`) on an existing note in `01_Projects/` or `02_Areas/`, append a `timeline` entry (`event_time`, `transaction_time`, `claim`, `source`) per `.agent/steering/bi-temporal-tracking.md`. Append-only — never edit or delete prior entries.
- For `03_Resources/` destinations: append a new row to the **Source Catalog** table in `03_Resources/RESOURCE-INDEX.md` with: `Date Encountered` (today), `Title`, `Author(s)`, `Type` (book/paper/article/talk/video/podcast/course/reference/tool-doc), `Status` (unread/reading/completed), `Notes` (WikiLink to the moved file), `Tags`. Insert at the top of the table (newest first). Also update the `Catalog Entries (total)` count in Summary Statistics.
- **Insert WikiLinks**: Add the Suggested WikiLinks from Step 3c into the note body (in a `## Related` section or inline where contextually appropriate). If the note already has a Related/Links section, append there.
- **Add backlinks**: In the top 1-2 most relevant connected notes, add a WikiLink back to the newly filed note (in their Related section or as an inline reference).
- Verify relative links (images, PDFs) still resolve after move.
- For items flagged as compound/brain dump in Step 3a: move to destination first, then suggest running `write-note` skill to split.
- For items routed to `04_Archives/`: suggest using the `archive-file` skill instead of direct move.

## Edge Cases

| Situation | Action |
|-----------|--------|
| Empty file | Flag as trash candidate; suggest delete (with approval only) |
| File links to assets (images/PDFs) | Verify asset paths before moving; move assets together |
| Duplicate filename at destination | Append `-1` suffix and flag for manual review |
| Git repo folder content | Never move files inside `02_Areas/Skills/` or `02_Areas/Tools for Thought/` — these are protected |
| File already has correct location metadata | Skip; note as "already triaged" |
| Compound note (user declines split) | File as-is but add a `#needs-splitting` tag for future processing |
| Near-duplicate detected (user declines merge) | File normally but add WikiLink to the existing note to acknowledge the overlap |

## Guidelines

- Never delete files without explicit approval.
- Never modify files inside `.obsidian/`, `.agent/`, or other agent workspaces.
- Preserve all existing YAML frontmatter.
- Use `[[WikiLinks]]` in reasoning to connect to existing vault notes.
- For unclear items, suggest `Inbox/` (keep) and ask for clarification.
- Batch moves are preferred over one-at-a-time for efficiency.
- **Zettelkasten principle**: Filing is also connecting. Every note moved should gain at least 1-2 WikiLinks to existing notes, and those notes should link back. The goal is knowledge graph density, not just folder placement.
- **Atomicity over speed**: It's better to flag a compound note for splitting than to file it quickly. One idea per note is the standard.
