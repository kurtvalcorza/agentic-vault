---
name: extract-concepts
description: Run a periodic LLM pass over vault areas to discover recurring concepts and generate concept hub pages with backlinks. Use when finding emergent themes, surfacing undocumented concepts, generating concept hubs, running vault concept health checks, or detecting terminology inconsistencies.
two_output: true
---

# extract-concepts

Scans Markdown files in a target directory (default: `02_Areas/`) to discover recurring concepts, entities, frameworks, and themes. Proposes new concept hub pages for themes appearing across multiple notes, suggests backlink repairs for existing hubs, and optionally runs a health check for terminology inconsistencies and stale hubs.

## Trigger Phrases

- "Find recurring concepts in my Areas"
- "Extract concepts from 02_Areas/"
- "What themes appear across my notes?"
- "Generate concept hubs"
- "Run concept health check"
- "Check for terminology inconsistencies"
- "Surface undocumented concepts"

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| Target directory | No | `02_Areas/` | Directory to scan for recurring concepts |
| `--threshold` | No | `3` | Minimum number of distinct notes a concept must appear in to be proposed. User can override by saying e.g., "use threshold of 5" |
| `--health` | No | Off | Enable health mode: detect terminology inconsistencies, stale hubs, missing cross-links |

---

## Phase 1 — Scan

Read all Markdown files in the target directory and extract structured metadata.

### Step 1.1 — Enumerate Files

```
**Tool:** file-search
Recursively find all `.md` files in the target directory.
```

Exclude:
- Files inside `.obsidian/`, `.agent/`, `.claude/`, `.gemini/`, `.kiro/`, `.git/`, `node_modules/`
- Files matching patterns in `.agent/search-index/exclude.txt`

### Step 1.2 — Extract Metadata Per File

For each `.md` file:

```
**Tool:** file-read
Read the file content.
```

Extract:
- **Title**: from YAML frontmatter `title` field, or first `# heading`, or filename
- **Frontmatter**: all YAML fields (especially `type`, `tags`, `aliases`)
- **Key terms**: entities, frameworks, named concepts, technical terms, acronyms that appear in the body text. Focus on domain-specific terminology, not generic words.
- **Outgoing WikiLinks**: all `[[Link Target]]` references
- **Tags**: from frontmatter `tags` field

### Step 1.3 — Build Term Frequency Map

Aggregate across all files:
- For each extracted key term, record which files mention it and how many times
- Track WikiLinks: which terms are already linked vs. mentioned only in prose
- Output: a term frequency map — `{ term: [list of source file paths] }`

---

## Phase 2 — Cluster

Group related terms, identify canonical names, and filter by occurrence threshold.

### Step 2.1 — Group Related Terms

Cluster terms that refer to the same concept:
- **Abbreviations**: "FL" ↔ "Federated Learning"
- **Synonyms**: "deep learning" ↔ "deep neural networks"
- **Case/plural variants**: "LLM" ↔ "LLMs" ↔ "large language model" ↔ "Large Language Models"
- **Partial matches**: "differential privacy" ↔ "DP" (when context confirms)

For each cluster, select a **canonical name** — prefer the most descriptive, full-form version (e.g., "Federated Learning" over "FL").

### Step 2.2 — Filter by Threshold

Remove concept candidates that appear in fewer than N distinct notes (default N=3, user-configurable via `--threshold` or natural language like "use threshold of 5").

Merge source lists for clustered terms: if "FL" appears in 2 notes and "Federated Learning" appears in 2 other notes, the cluster has 4 source notes total.

### Step 2.3 — Exclude Ignored Concepts

```
**Tool:** file-read
Read `.agent/concept-ignore.txt`
```

Remove any concept candidate whose canonical name (case-insensitive) matches a line in the ignore list.

### Step 2.4 — Output Concept Candidates

For each surviving candidate:
- Canonical name
- All variant terms in the cluster
- List of source notes (file paths)
- Source count

---

## Phase 3 — Gap Analysis

Determine which candidates are genuinely new vs. already documented.

### Step 3.1 — Check for Existing Hub Pages

For each concept candidate, search for an existing hub page:

```
**Tool:** content-search
Search for files with frontmatter `title` matching the canonical name (case-insensitive).
Also search for `aliases` fields that match any variant in the cluster.
```

Classify each candidate:
- **No existing hub**: Mark as "proposed new hub"
- **Hub exists**: Mark as "existing hub — check for unlinked sources"

### Step 3.2 — Identify Unlinked Source Notes

For candidates with existing hubs:

1. Read the existing hub page to find its `## Key Appearances` section (or equivalent backlink list).
2. Compare against the source notes found in Phase 1.
3. Any source note that discusses the concept but is NOT listed in the hub's appearances = **unlinked source**.

### Step 3.3 — Build Gap Report

Output:
- **New concepts**: candidates with no existing hub (proposed for creation)
- **Existing hubs needing updates**: hubs with unlinked source notes
- **Orphaned hubs**: existing concept hubs (files with `type: concept-article` and `origin: extracted`) whose source notes have ALL been archived (moved to `04_Archives/`) or deleted

---

## Phase 4 — Proposal

Present findings to the user for approval.

### Step 4.1 — Present New Hub Proposals

For each proposed new hub, present:

```
### {Canonical Name}
- **Sources:** {N} notes
- **Preview:** {2-sentence summary of what this concept covers across the source notes}
- **Proposed location:** 02_Areas/{sub-area}/
- **Approve / Reject?**
```

Use `user-interact` to let the user approve or reject each proposal.

### Step 4.2 — Present Link-Repair Suggestions

For existing hubs with unlinked sources:

```
### {Hub Name} — {M} unlinked sources
- [[Source Note A]] — mentions "{concept}" but not backlinked
- [[Source Note B]] — mentions "{concept}" but not backlinked
- **Add backlinks?**
```

### Step 4.3 — Present Orphaned Hubs

For orphaned concept hubs:

```
### Orphaned: {Hub Name}
- All {N} source notes have been archived or deleted
- **Archive this hub? / Keep?**
```

### Step 4.4 — Health Mode Additions (if `--health` flag)

If health mode is active, also present:

**Terminology inconsistencies:**
```
### Inconsistency: "{Term A}" vs "{Term B}"
- {N} notes use "{Term A}", {M} notes use "{Term B}"
- **Suggested canonical name:** {preferred form}
- **Rename all occurrences?**
```

**Missing cross-links between related hubs:**
```
### Missing cross-link: [[Hub A]] ↔ [[Hub B]]
- Both hubs share {N} source notes but don't link to each other
- **Add mutual WikiLinks?**
```

**Stale hubs:**
```
### Stale: {Hub Name}
- All source notes archived to 04_Archives/
- Hub has not been updated since {date}
- **Archive / Keep / Update?**
```

---

## Phase 5 — Generation

Create approved hub pages, insert backlinks, and update indexes.

### Step 5.1 — Generate Hub Pages

For each approved new concept hub:

1. **Determine placement** — follow `02_Areas/area-intake-policy`:
   - Identify the most relevant sub-area based on the concept's domain
   - Place the hub at `02_Areas/{sub-area}/{slugified-concept-name}.md`

2. **Generate content** using the template at `templates/concept-hub-template.md`:
   - `title`: Canonical concept name
   - `type`: `concept-article`
   - `origin`: `extracted`
   - `area`: Parent area path (e.g., `02_Areas/AI_and_Data_Science`)
   - `sources_count`: Number of source notes
   - `created` / `updated`: Today's date
   - `tags`: `[concept-article, {domain-tag}]` — derive domain-tag from the sub-area

   Write the article body:
   - **Summary** — 2-3 paragraph synthesis from all source notes
   - **Key Appearances** — WikiLinked list of source notes with one-line context
   - **Related Concepts** — WikiLinks to other concept hubs (existing or newly created)
   - **Notes** — Cross-cutting observations, tensions, or open questions

```
**Tool:** file-write
Write the hub page to `02_Areas/{sub-area}/{slugified-concept-name}.md`
```

### Step 5.2 — Propose Backlink Insertions (Batch)

Collect ALL backlink insertions across all approved hubs into a single batch:

```
### Proposed Backlink Insertions

| Source Note | Link to Add |
|:------------|:------------|
| [[Source Note A]] | [[New Concept Hub 1]] |
| [[Source Note B]] | [[New Concept Hub 1]], [[New Concept Hub 2]] |
| [[Source Note C]] | [[New Concept Hub 2]] |

**Approve all backlink insertions?** (single confirmation for the entire batch)
```

Present this batch to the user via `user-interact` for a **single confirmation** (authorized exception to per-file confirmation rule per CX2).

### Step 5.3 — Apply Approved Backlinks

If the user approves the batch:

For each source note in the batch:

```
**Tool:** file-read
Read the source note.
```

Insert the backlink:
- **If the note has a `## Related Concepts` section**: append the hub WikiLink(s) to that section.
- **Otherwise**: add a `concepts` list field to the YAML frontmatter:
  ```yaml
  concepts:
    - "[[New Concept Hub]]"
  ```

```
**Tool:** file-edit
Insert the backlink into the source note.
```

### Step 5.4 — Update AREA-INDEX

```
**Tool:** file-read
Read `02_Areas/AREA-INDEX.md`
```

Add entries for newly created concept hubs under the appropriate sub-area section.

```
**Tool:** file-edit
Append new hub entries to AREA-INDEX.md
```

### Step 5.5 — Handle Rejected Concepts

For each concept the user rejected:

```
**Tool:** file-read
Read `.agent/concept-ignore.txt`
```

Append the rejected concept's canonical name:

```
**Tool:** file-edit
Append "{Canonical Name}" to `.agent/concept-ignore.txt`
```

This ensures the concept is not re-proposed on future runs.

---

## Health Mode (`--health`)

When invoked with the `--health` flag, the skill performs additional checks after the standard 5-phase pipeline.

### Health Check 1 — Terminology Inconsistencies

Detect cases where the same concept is named differently across notes:
- Compare term clusters from Phase 2 against existing hub page titles
- Flag clusters where multiple distinct names are used in prose but no canonical hub exists
- Suggest renames: propose the most common or most descriptive form as canonical

### Health Check 2 — Stale Hubs

Identify concept hubs whose backing sources are all gone:
- For each file with `type: concept-article` and `origin: extracted`:
  - Check if ALL source notes listed in `## Key Appearances` have been moved to `04_Archives/` or deleted
  - If so, flag as stale

### Health Check 3 — Missing Cross-Links

Identify related concept hubs that should link to each other but don't:
- Two hubs are "related" if they share 2+ source notes
- Check if each pair has mutual WikiLinks in their `## Related Concepts` sections
- Flag missing links

### Health Check 4 — Contradiction Detection

Identify factual contradictions between Concept_Hub pages that share source notes.

#### Step 4.1 — Identify Shared Source Notes

For each pair of Concept_Hub pages (files with `type: concept-article` and `origin: extracted`):

1. Parse the `## Key Appearances` section of each hub
2. Extract all WikiLinks (`[[Note Name]]`) from that section — these are the hub's source notes
3. Two hubs **share source notes** when both contain a WikiLink to the same note in their `## Key Appearances` sections
4. Build a list of all hub pairs that share at least one source note

#### Step 4.2 — Detect Contradictions Between Hub Pairs

For each pair of hubs sharing source notes:

1. Read the summary/definition sections of both hubs (the opening paragraphs, `## Summary`, or the first substantive section after frontmatter)
2. Compare factual claims using LLM judgment:
   - **Contradiction**: claims are mutually exclusive (e.g., "X uses approach A" vs "X uses approach B")
   - **NOT a contradiction**: claims are complementary, differently-scoped, or additive
3. Flag pairs where claims are mutually exclusive

> **Note:** This step relies on LLM judgment. False positives are expected — the health report is a triage tool, not a verdict. The `reconcile-vault` handoff provides detailed resolution with Source_Authority and Recency_Date heuristics.

#### Step 4.3 — Report and Suggest Resolution

For each contradictory pair:

```
### Contradiction: [[Hub A]] ↔ [[Hub B]]
- **Shared sources:** [[Source Note 1]], [[Source Note 2]]
- **Hub A claims:** {summary of claim from Hub A}
- **Hub B claims:** {summary of conflicting claim from Hub B}
- **Suggested action:** Run `reconcile-vault` with topic "{relevant topic}" for detailed resolution
```

### Health Report Output

Generate a remediation report:

```markdown
# Concept Health Report — {target directory}
**Date:** {YYYY-MM-DD}
**Files scanned:** {N}
**Existing concept hubs:** {M}

## Terminology Inconsistencies

| Variant A | Variant B | Notes Using A | Notes Using B | Suggested Canonical |
|-----------|-----------|---------------|---------------|---------------------|
| {term}    | {term}    | {N}           | {M}           | {preferred}         |

## Stale Hubs

| Hub | Source Notes | Status |
|-----|-------------|--------|
| [[Hub Name]] | {N} sources, all archived | Recommend archive |

## Missing Cross-Links

| Hub A | Hub B | Shared Sources | Action |
|-------|-------|----------------|--------|
| [[Hub A]] | [[Hub B]] | {N} | Add mutual WikiLinks |

## Contradictions

| Hub A | Hub B | Shared Sources | Hub A Claim | Hub B Claim | Suggested Action |
|-------|-------|----------------|-------------|-------------|------------------|
| [[Hub A]] | [[Hub B]] | {N} | {claim summary} | {conflicting claim} | Run `reconcile-vault` with topic "{topic}" |

## Summary
- {X} terminology inconsistencies found
- {Y} stale hubs detected
- {Z} missing cross-links identified
- {W} contradictions detected between concept hubs
```

Log the health report to `System/session-logs/YYYY-MM-DD/`.

---

## Required Capabilities

| Capability | Usage |
|:-----------|:------|
| `file-read` | Read source notes, existing hubs, ignore list, AREA-INDEX |
| `file-write` | Write new hub pages, health reports |
| `file-edit` | Insert backlinks into source notes, update AREA-INDEX, append to ignore list |
| `file-search` | Enumerate .md files in target directory |
| `content-search` | Search for existing hubs by title/alias, find term occurrences |
| `user-interact` | Present proposals for user approval/rejection |

### Referenced Policies

| Policy | Path | Purpose |
|:-------|:-----|:--------|
| Area intake policy | `02_Areas/area-intake-policy` | Determines hub placement in `02_Areas/` sub-directories |
| Concept ignore list | `.agent/concept-ignore.txt` | Concepts to skip (user-rejected) |
| AREA-INDEX | `02_Areas/AREA-INDEX.md` | Updated when new hubs are created |

---

## Error Handling

| Scenario | Action |
|:---------|:-------|
| Target directory is empty or has no `.md` files | Report "no Markdown files found" and exit gracefully |
| Ignore list file missing | Create `.agent/concept-ignore.txt` with header comment, continue |
| AREA-INDEX not found | Warn user, skip index update, continue with hub generation |
| Source note cannot be read (permissions, encoding) | Log warning, skip that file, continue scanning |
| No concepts meet threshold | Report "no concepts found above threshold of {N}" and exit |
| All candidates are in ignore list | Report "all candidates are on the ignore list" and exit |
| Backlink insertion would corrupt file | Skip that file, log warning, continue with remaining files |
| Health mode finds no issues | Report "no issues found — vault concepts are healthy" |

---

## Examples

### Basic Run

**User:** Find recurring concepts in my Areas.

**Agent:**
1. Scanning `02_Areas/` — found 142 Markdown files.
2. Extracted 87 distinct terms across all files.
3. Clustered into 34 concept groups.
4. After threshold filter (≥3 notes): 12 candidates remain.
5. After ignore list filter: 11 candidates.
6. Gap analysis: 8 new concepts, 3 existing hubs with unlinked sources.

**Proposals:**

### Federated Learning
- **Sources:** 7 notes
- **Preview:** Distributed machine learning approach discussed across Project Atlas project notes and AI governance documents. Covers both technical implementation and policy implications.
- **Proposed location:** `02_Areas/AI_and_Data_Science/federated-learning.md`
- **Approve / Reject?**

*(... more proposals ...)*

### With Custom Threshold

**User:** Extract concepts from 02_Areas/AI_and_Data_Science/ with threshold of 5.

**Agent:**
1. Scanning `02_Areas/AI_and_Data_Science/` — found 38 Markdown files.
2. After threshold filter (≥5 notes): 6 candidates remain.
*(... proposals ...)*

### Health Mode

**User:** Run concept health check on my Areas.

**Agent:**
1. Running standard extraction pipeline...
2. Running health checks...

**Health Report:**
- 2 terminology inconsistencies: "FL" vs "Federated Learning" (suggest merge), "LLM" vs "Large Language Model" (suggest canonical: "Large Language Model")
- 1 stale hub: [[Blockchain Basics]] — all 3 source notes archived
- 3 missing cross-links: [[Federated Learning]] ↔ [[Differential Privacy]], ...

### Re-run After Approval

**User:** Run extract-concepts again.

**Agent:**
1. Scanning `02_Areas/` — found 145 Markdown files (3 new hubs from last run).
2. 12 candidates after threshold filter.
3. 3 candidates match newly created hubs — skipping (already exist).
4. 2 candidates on ignore list — skipping.
5. 7 new proposals.
*(No duplicates from previous run.)*
