# compile-wiki

Compile a folder of raw source materials (PDF, DOCX, Markdown, TXT, HTML) into a structured, interlinked wiki of concept articles with a navigable index and source manifest. Supports incremental compilation — re-runs only process new or modified sources.

## Purpose

Transforms a collection of raw documents into a structured knowledge base:
- **Concept articles** — one article per identified concept, synthesized from all contributing sources
- **Interlinked** — mutual WikiLinks between related concepts
- **Indexed** — `INDEX.md` with categorized article listing, `SOURCES.md` with processing manifest
- **Incremental** — only new/modified sources are processed on re-runs
- **User-edit safe** — detects manual edits and preserves them

## Usage

### First Run (Basic)

```
Compile the folder 01_Projects/Project Atlas/research-papers/ into a wiki
```

Output: `03_Resources/Compiled/atlas-research-papers/` with concept articles, INDEX.md, and SOURCES.md.

### With Custom Wiki Name

```
Compile research/ml-privacy/ into a wiki called "privacy-survey"
```

### With Custom Output Directory

```
Compile research/ml-privacy/ into a wiki at 01_Projects/Privacy/wiki/
```

### Incremental Update

```
I added new papers to the research folder. Update the wiki.
```

Only new/modified sources are processed. Existing articles are updated with new information.

## Output Examples

### Article Frontmatter

```yaml
---
title: "Federated Learning"
type: concept-article
wiki: ml-research
origin: compiled
sources:
  - "federated-learning-overview.md"
  - "distributed-training-notes.txt"
related:
  - "[[Differential Privacy]]"
  - "[[Model Aggregation]]"
created: 2026-04-03
updated: 2026-04-03
tags:
  - concept-article
  - compiled
  - ai
---
```

### INDEX.md

```markdown
---
title: "ML Research — Index"
type: wiki-index
wiki: ml-research
origin: compiled
---

# ML Research

Compiled wiki generated from `research/ml-papers/`.

## AI / Machine Learning

- [[Federated Learning]] — Distributed training across decentralized data sources
- [[Model Aggregation]] — Strategies for combining model updates in federated settings
- [[Machine Learning]] — Core ML concepts and paradigms

## Privacy & Security

- [[Differential Privacy]] — Mathematical framework for privacy-preserving data analysis
- [[Data Governance]] — Policies and practices for managing data assets

**Sources:** 4 documents processed — see [[SOURCES]] for full manifest.
**Articles:** 5 concept articles generated.
```

### SOURCES.md

```markdown
---
title: "ML Research — Sources"
type: wiki-sources
wiki: ml-research
origin: compiled
---

# Sources — ML Research

## Processed Sources

| # | File | Format | Status | Concepts Extracted |
|---|------|--------|--------|--------------------|
| 1 | `federated-learning-overview.md` | Markdown | processed | Federated Learning, Machine Learning, Model Aggregation |
| 2 | `privacy-in-ml.md` | Markdown | processed | Differential Privacy, Machine Learning, Data Governance |
| 3 | `distributed-training-notes.txt` | Plain text | processed | Federated Learning, Model Aggregation, Differential Privacy |
| 4 | `data-governance-primer.html` | HTML | processed | Data Governance, Machine Learning, Differential Privacy |

## Changelog

- **2026-04-03** — Initial compilation: 4 sources processed, 5 concepts extracted.
```

### Directory Structure (Generated Wiki)

```
03_Resources/Compiled/ml-research/
├── INDEX.md
├── SOURCES.md
├── federated-learning.md
├── differential-privacy.md
├── machine-learning.md
├── data-governance.md
└── model-aggregation.md
```

## Processing Pipeline

The skill operates in 5 phases:

1. **Inventory** — Scan source folder, diff against compile state, build processing manifest
2. **Conversion** — Convert non-Markdown sources (PDF → `convert-pdf-to-md`, DOCX → `convert-docx-to-md`, HTML → inline conversion)
3. **Concept Extraction** — Process sources in batches of 5-10, extract concepts, merge across batches
4. **Article Generation** — Generate/update concept articles with WikiLinks and source citations
5. **Index Generation** — Produce INDEX.md and SOURCES.md, update compile state

## Incremental Compilation

On re-runs, the skill compares source file SHA-256 hashes against the compile state:
- **Unchanged sources** — skipped entirely
- **New sources** — processed and concepts merged into existing wiki
- **Modified sources** — reprocessed, articles updated
- **Removed sources** — flagged in report (articles NOT auto-deleted; requires user confirmation)

## User-Edit Detection

If a user manually edits a generated article, the skill detects this by comparing the article's content hash against the stored hash in compile state. When user edits are detected:
- The existing content is **preserved**
- New source material is **appended** to a `## Updates` section with a date separator
- Frontmatter `sources` and `related` fields are updated to include new entries

## Compile State

Stored at `.agent/search-index/compile-states/{wiki-name}.json`. Tracks:
- Source file hashes (for incremental skip)
- Concept-to-source mappings
- Article content hashes (for user-edit detection)
- Processing timestamps

Updated incrementally for crash recovery:
- `sources` section updated after each source is converted (Phase 2)
- `concepts` section written after Phase 3 merge completes
- Article hashes written after Phase 4

## Prerequisites

| Dependency | Path | Required |
|:-----------|:-----|:---------|
| `convert-pdf-to-md` skill | `.agent/skills/convert-pdf-to-md/` | For PDF sources |
| `convert-with-docling` skill | `.agent/skills/convert-with-docling/` | Fallback for complex PDFs |
| `convert-docx-to-md` skill | `.agent/skills/convert-docx-to-md/` | For DOCX sources |
| `compile-states/` directory | `.agent/search-index/compile-states/` | Required (created by infrastructure setup) |
| `03_Resources/Compiled/` directory | `03_Resources/Compiled/` | Default output location |

## Supported File Types

| Extension | Handler | Notes |
|-----------|---------|-------|
| `.md` | Read directly | Already in target format |
| `.txt` | Read directly | Treated as unstructured content |
| `.html` | Inline conversion | Agent strips HTML, produces clean Markdown |
| `.pdf` | `convert-pdf-to-md` / `convert-with-docling` | Delegated to conversion skills |
| `.docx` | `convert-docx-to-md` | Delegated to conversion skill |
| `.png`, `.jpg`, `.svg`, `.webp` | Catalogue | Visual assets with generated descriptions |
| `.pptx`, `.xlsx`, etc. | Skipped | Logged as unsupported |

## Error Handling

- **Empty source folder**: Reports warning and exits gracefully
- **Conversion failures**: Logged in SOURCES.md; `convert-with-docling` used as PDF fallback
- **Corrupted compile state**: Backed up, reinitialized, full reprocess triggered
- **Orphan WikiLinks**: Flagged in compilation report
- **Cross-vault title collisions**: Fully qualified `[[path/to/Note]]` form used

## Test Scenarios

### Test 1: Initial Compilation (4 test fixtures)
- **Input:** 4 test files (2 `.md`, 1 `.txt`, 1 `.html`) covering overlapping concepts
- **Expected:** 5 concept articles generated, INDEX.md lists all 5, SOURCES.md lists all 4 sources as processed, all WikiLinks between articles resolve

### Test 2: Incremental Update
- **Input:** Re-run with 2 new sources added to the fixture folder
- **Expected:** Only new sources processed (unchanged sources skipped by hash match), index updated with new concepts/articles

### Test 3: WikiLink Resolution
- **Validate:** All generated `[[WikiLinks]]` resolve to existing files in the wiki output directory
- **Validate:** No orphan links

### Test 4: Cross-Vault WikiLink Qualification
- **Validate:** When a concept title matches a note outside the wiki, the WikiLink uses fully qualified path `[[path/to/Note]]`

### Test 5: Agent Skills Standard Compliance
- **Validate:** `SKILL.md` has proper YAML frontmatter with `name` and `description`
- **Validate:** Uses agent-agnostic tool names from `.agent/TOOL-TAXONOMY.md`
- **Validate:** Dual documentation pattern (SKILL.md + README.md)
- **Validate:** Directory structure follows `skill-name/{SKILL.md, README.md, references/, templates/}`

## Related Skills

- `clip-and-localize` — Web content capture (upstream data source)
- `query-vault` — Q&A against compiled wikis (downstream consumer)
- `extract-concepts` — Concept hub generation from existing vault content
- `convert-pdf-to-md` — PDF extraction (used during Phase 2)
- `convert-docx-to-md` — Word document conversion (used during Phase 2)
- `convert-with-docling` — Complex document parsing with OCR (Phase 2 fallback)
