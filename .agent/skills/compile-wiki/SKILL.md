---
name: compile-wiki
description: Compile a folder of raw source materials into a structured, interlinked wiki of concept articles with index and source manifest. Use when compiling sources into a wiki, building a knowledge base from documents, creating a structured reference from raw materials, or incrementally updating an existing compiled wiki.
---

# compile-wiki

Reads a source folder of raw documents (PDF, DOCX, Markdown, TXT, HTML), identifies key concepts across all sources, and generates a structured wiki of interlinked concept articles with an index and source manifest. Supports incremental compilation — re-runs only process new or modified sources.

## Trigger Phrases

- "Compile this folder into a wiki"
- "Build a wiki from my research folder"
- "Compile my sources into a knowledge base"
- "Update the compiled wiki with new sources"
- "Recompile the wiki"
- "Create a structured reference from these documents"

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| Source folder | Yes | — | Path to folder containing raw source materials |
| Wiki name | No | Derived from source folder name (slugified to kebab-case) | Identifier for the compiled wiki |
| Output directory | No | `03_Resources/Compiled/{wiki-name}/` | Where to write generated articles |

---

## Phase 1 — Inventory

Scan the source folder and determine what needs processing.

### Step 1.1 — Derive Wiki Name

If the user provided a wiki name, use it (slugified to kebab-case).
Otherwise, derive from the source folder's directory name:
- Lowercase
- Replace spaces and special characters with hyphens
- Collapse multiple hyphens
- Strip leading/trailing hyphens
- Example: `My Research Notes` → `my-research-notes`

### Step 1.2 — Load or Initialize Compile State

Check for existing compile state:

```
**Tool:** file-read
Read `.agent/search-index/compile-states/{wiki-name}.json`
```

- **If found:** Load the state. This contains previously processed source hashes, concept mappings, and article content hashes.
- **If not found (first run):** Initialize an empty state structure:
  ```json
  {
    "wiki_name": "{wiki-name}",
    "source_dir": "{source-folder-path}",
    "output_dir": "03_Resources/Compiled/{wiki-name}",
    "last_compiled": null,
    "sources": {},
    "concepts": {}
  }
  ```

### Step 1.3 — Scan Source Folder

```
**Tool:** file-search
Recursively scan the source folder for all files.
```

Supported file types:
- `.md` — Markdown (read directly)
- `.txt` — Plain text (read directly)
- `.html` — HTML (read and convert inline)
- `.pdf` — PDF (delegate to converter)
- `.docx` — Word document (delegate to converter)
- `.png`, `.jpg`, `.jpeg`, `.svg`, `.webp` — Images (catalogue as visual assets)

Unsupported types (`.pptx`, `.xlsx`, etc.): log as unsupported in the compilation report and skip.

### Step 1.4 — Diff Against Compile State

For each supported source file:

1. **Compute SHA-256 hash** of the file content:
   ```
   **Tool:** command-exec
   certutil -hashfile "{file-path}" SHA256
   ```
   (On Unix: `sha256sum "{file-path}"`)

2. **Compare against stored hash** in compile state `sources[filename].hash`:
   - **Hash matches:** Mark as `unchanged` — skip in Phase 2.
   - **Hash differs:** Mark as `modified` — reprocess in Phase 2.
   - **Not in state:** Mark as `new` — process in Phase 2.

3. **Detect removed sources:** Any filename in compile state but not on disk — mark as `removed`. Flag in report but do NOT delete articles (requires user confirmation).

### Step 1.5 — Build Processing Manifest

Output a manifest listing:
- New sources to process
- Modified sources to reprocess
- Unchanged sources to skip
- Removed sources to flag

If all sources are unchanged, report "No changes detected" and exit (unless user explicitly requests full recompilation).

If the source folder contains no supported files, report an empty source warning and exit gracefully.

---

## Phase 2 — Conversion

Convert each new/modified source to normalized Markdown. Update compile state after EACH source is converted (crash recovery).

### Step 2.1 — Process Each Source

For each source in the processing manifest (new + modified):

#### PDF files (`.pdf`)
```
Delegate to the `convert-pdf-to-md` skill.
If conversion fails or produces poor output, fall back to the `convert-with-docling` skill.
```

#### Word documents (`.docx`)
```
Delegate to the `convert-docx-to-md` skill.
```

#### HTML files (`.html`)
```
**Tool:** file-read
Read the raw HTML file.
```
Then convert inline: strip HTML tags, preserve content structure (headings, lists, paragraphs, tables, code blocks). No external parser needed — the agent reads the HTML and produces clean Markdown.

#### Markdown files (`.md`)
```
**Tool:** file-read
Read the file directly. It is already in the target format.
```

#### Plain text files (`.txt`)
```
**Tool:** file-read
Read the file directly as plain text. Treat as unstructured content.
```

#### Image files (`.png`, `.jpg`, `.jpeg`, `.svg`, `.webp`)
Catalogue as a visual asset. Generate a brief description of the image content. Do not convert — reference in articles where relevant.

### Step 2.2 — Update Compile State (per source)

After each source is successfully converted, immediately update the compile state:

```
**Tool:** file-write
Update `.agent/search-index/compile-states/{wiki-name}.json`:
- Set `sources[filename].hash` to the computed SHA-256 hash
- Set `sources[filename].last_processed` to current ISO timestamp
- Set `sources[filename].status` to "processed"
- Leave `sources[filename].concepts_extracted` empty (filled in Phase 3)
```

This ensures crash recovery: if compilation is interrupted during Phase 2, re-invocation skips already-hashed sources.

---

## Phase 3 — Concept Extraction (Batched)

Extract key concepts from all sources (new + modified + previously processed unchanged sources that contribute context).

### Step 3.1 — Batch Sources

Group all source content into batches of 5–10 files (sized to fit context window). If there are fewer than 5 sources, process as a single batch.

### Step 3.2 — Extract Concepts Per Batch

For each batch, read the normalized Markdown content and identify:
- **Key concepts** — major topics, frameworks, methodologies, entities
- **Relationships** — which concepts co-occur in the same source
- **Source mappings** — which source files discuss each concept

Output per batch: a partial concept list with source mappings.

### Step 3.3 — Merge Concept Lists

After all batches are processed:

1. **Merge** partial concept lists into a unified concept map.
2. **Deduplicate** — cluster related terms (abbreviations, synonyms, minor variations) under a canonical name.
3. **Map** each concept to its full list of contributing source files.
4. **Identify relationships** — concepts that co-occur in the same source are related.

### Step 3.4 — Update Compile State (concepts)

After the merge completes, write the full concept map to compile state:

```
**Tool:** file-write
Update `.agent/search-index/compile-states/{wiki-name}.json`:
- For each source: set `sources[filename].concepts_extracted` to the list of concepts found in that source
- For each concept: set `concepts[concept_name]` with `article_path`, `source_count`, `last_updated`
```

---

## Phase 4 — Article Generation

Generate or update a concept article for each identified concept.

### Step 4.1 — Check Existing Articles

For each concept, check if an article already exists in the output directory:

```
**Tool:** file-search
Search for files in `{output-dir}/` whose frontmatter `title` matches the concept name (case-insensitive).
```

### Step 4.2 — User-Edit Detection

For existing articles, detect whether the user has manually edited the article:

1. **Read the current article content:**
   ```
   **Tool:** file-read
   Read the existing article file.
   ```

2. **Compute content hash** (SHA-256 of the file content).

3. **Compare** against `concepts[concept_name].article_content_hash` in compile state:
   - **Hash matches:** Article is unmodified by user → safe to regenerate.
   - **Hash differs:** User has edited the article → preserve user content.

### Step 4.3 — Generate or Update Articles

For each concept:

#### New article (no existing file)
Generate a full article using the template at `templates/article-template.md`:
- `title`: Concept name
- `type`: `concept-article`
- `wiki`: `{wiki-name}`
- `origin`: `compiled`
- `sources`: List of contributing source filenames (plain filenames, NOT WikiLinks — source files are raw inputs, not vault notes)
- `related`: WikiLinks to other concept articles in this wiki (`[[Other Concept]]`)
- `created` / `updated`: Today's date
- `tags`: `[concept-article, compiled, {domain-tag}]` — derive domain-tag from the wiki's subject matter

Write the article body:
- **Summary** — 2-3 paragraph synthesis from all contributing sources
- **Key Points** — bullet list of main takeaways
- **Related Concepts** — WikiLinked list with one-line relationship explanations
- **Source Bibliography** — each contributing source filename with a one-line summary of its contribution

```
**Tool:** file-write
Write the article to `{output-dir}/{slugified-concept-name}.md`
```

#### Existing article, unmodified by user (hash matches)
Regenerate the full article with all sources (old + new). This replaces the previous version.

```
**Tool:** file-write
Overwrite the article at its existing path.
```

#### Existing article, modified by user (hash differs)
Preserve the user's content. Append new source material:

1. Read the existing article.
2. Append a `## Updates` section (if not already present) or append below existing Updates entries.
3. Add a date separator: `### {YYYY-MM-DD}`
4. Below the separator, add new information from the new sources.
5. Update the `sources` and `related` frontmatter fields to include new entries.
6. Update the `updated` frontmatter field.

```
**Tool:** file-edit
Append the Updates section to the existing article.
```

### Step 4.4 — WikiLink Resolution

After all articles are generated, verify that all WikiLinks resolve:

1. **Within the wiki:** Each `[[Concept Name]]` should match an article file in the output directory.
2. **Cross-vault check:** If a concept title matches a note outside the wiki (in `01_Projects/`, `02_Areas/`, etc.), use the fully qualified form `[[path/to/Note Name]]` to avoid ambiguity.

To check for cross-vault matches:
```
**Tool:** content-search
Search for files with matching titles outside the wiki output directory.
```

If a match is found outside the wiki, rewrite the WikiLink to use the fully qualified path.

### Step 4.5 — Deduplication

**Within wiki output directory:** Before generating a new article, check if an article with the same title already exists (case-insensitive frontmatter `title` match). If so, merge into the existing article rather than creating a duplicate.

**Cross-vault overlaps:** Do NOT automatically deduplicate against notes in `01_Projects/`, `02_Areas/`, etc. Instead, flag potential overlaps in the compilation report for user review:
```
⚠ Potential overlap: "Federated Learning" also exists at 02_Areas/AI_and_Data_Science/federated-learning.md
```

### Step 4.6 — Update Compile State (article hashes)

After all articles are written, update the compile state with content hashes:

```
**Tool:** file-write
Update `.agent/search-index/compile-states/{wiki-name}.json`:
- For each concept: set `concepts[concept_name].article_content_hash` to SHA-256 of the generated article
- Set `concepts[concept_name].last_updated` to current ISO timestamp
- Set `concepts[concept_name].source_count` to number of contributing sources
```

---

## Phase 5 — Index Generation

Produce navigable index files for the compiled wiki.

### Step 5.1 — Generate INDEX.md

Using the template at `templates/index-template.md`:

1. **Group articles by category** — derive categories from the wiki's subject matter (e.g., "AI / Machine Learning", "Privacy & Security", "Data Management").
2. **List each article** as a WikiLink with a one-line description.
3. **Include metadata:** source count, article count, last compiled date.

```
**Tool:** file-write
Write `{output-dir}/INDEX.md`
```

### Step 5.2 — Generate SOURCES.md

Using the template at `templates/sources-template.md`:

1. **List all source files** with:
   - Filename
   - Format (PDF, DOCX, MD, TXT, HTML)
   - Processing status (processed / skipped / error)
   - Concepts extracted from that source
2. **List skipped/errored files** with reasons.
3. **Append changelog entry:**
   - For initial compilation: `{date} — Initial compilation: {N} sources processed, {M} concepts extracted.`
   - For incremental runs: `{date} — Incremental update: {N} new sources, {M} modified, {K} unchanged. New concepts: {list}.`

```
**Tool:** file-write
Write `{output-dir}/SOURCES.md`
```

### Step 5.3 — Finalize Compile State

```
**Tool:** file-write
Update `.agent/search-index/compile-states/{wiki-name}.json`:
- Set `last_compiled` to current ISO timestamp
- Set `output_dir` to the actual output directory used
```

### Step 5.4 — Compilation Report

Present a summary to the user:

```
## Compilation Report: {wiki-name}

**Source folder:** {source-dir}
**Output:** {output-dir}
**Sources:** {total} ({new} new, {modified} modified, {unchanged} unchanged, {skipped} skipped)
**Concepts:** {concept-count} identified
**Articles:** {article-count} generated ({new-articles} new, {updated-articles} updated)

### Articles Generated
- [[Concept A]] — {source-count} sources
- [[Concept B]] — {source-count} sources

### Cross-Vault Overlaps (review recommended)
- "Concept X" also exists at {path}

### Skipped Sources
- {filename}: {reason}
```

---

## Crash Recovery

The compile state is designed for crash recovery at each phase boundary:

| Crash Point | Recovery Behavior |
|:------------|:------------------|
| During Phase 2 (conversion) | `sources` section has per-source hashes. Re-invocation skips already-hashed sources, resumes from the next unprocessed source. |
| During Phase 3 (extraction) | Sources are converted (hashes saved). Re-invocation re-extracts concepts from already-converted sources (fast — no reconversion needed). |
| During Phase 4 (generation) | Concepts are mapped. Re-invocation regenerates articles. Existing articles with matching hashes are detected as user-unmodified. |
| During Phase 5 (indexing) | Articles exist on disk. Re-invocation regenerates INDEX.md and SOURCES.md from disk state. |

**Partially generated articles** (orphaned by a crash) are detected by comparing the compile state concept list against files on disk. Orphans are flagged for user review.

---

## Required Capabilities

| Capability | Usage |
|:-----------|:------|
| `file-read` | Read source files, compile state, existing articles |
| `file-write` | Write articles, INDEX.md, SOURCES.md, compile state |
| `file-edit` | Append Updates section to user-edited articles |
| `file-search` | Scan source folder, find existing articles |
| `content-search` | Cross-vault WikiLink resolution, dedup checking |
| `command-exec` | Compute SHA-256 hashes, invoke conversion scripts |

### Delegated Skills

| Skill | Path | Purpose |
|:------|:-----|:--------|
| `convert-pdf-to-md` | `.agent/skills/convert-pdf-to-md/` | Convert PDF sources to Markdown |
| `convert-with-docling` | `.agent/skills/convert-with-docling/` | Fallback PDF/document parsing with OCR |
| `convert-docx-to-md` | `.agent/skills/convert-docx-to-md/` | Convert Word documents to Markdown |

### Infrastructure

| Resource | Path | Purpose |
|:---------|:-----|:--------|
| Compile state | `.agent/search-index/compile-states/{wiki-name}.json` | Track source hashes, concepts, article hashes |
| Output directory | `03_Resources/Compiled/{wiki-name}/` | Default wiki output location |

---

## Error Handling

| Scenario | Action |
|:---------|:-------|
| Source folder is empty or has no supported files | Report empty source warning, exit gracefully |
| PDF conversion fails | Log error, try `convert-with-docling` as fallback. If both fail, mark source as `error` in SOURCES.md |
| DOCX conversion fails | Log error, mark source as `error` in SOURCES.md |
| HTML is malformed | Best-effort extraction, note quality warning |
| Unsupported file type | Log as unsupported in SOURCES.md, skip |
| Compile state is corrupted | Back up corrupted file, reinitialize empty state, reprocess all sources |
| WikiLink target not found | Flag as orphan link in compilation report |
| Cross-vault title collision | Use fully qualified `[[path/to/Note]]` form |
| User-edited article detected | Preserve content, append to `## Updates` section |

---

## Examples

### First Run

**User:** Compile the folder `01_Projects/Project Atlas/research-papers/` into a wiki.

**Agent:**
1. Wiki name: `atlas-research-papers` (derived from folder name)
2. No existing compile state — treating all sources as new.
3. Found 8 sources: 3 PDF, 2 DOCX, 2 MD, 1 TXT
4. Converting PDFs via `convert-pdf-to-md`... done.
5. Converting DOCX files via `convert-docx-to-md`... done.
6. Reading Markdown and text files directly.
7. Extracting concepts (1 batch of 8 sources)...
8. Identified 12 concepts across all sources.
9. Generating 12 concept articles...
10. Writing INDEX.md and SOURCES.md...

**Result:** Wiki at `03_Resources/Compiled/atlas-research-papers/` with 12 articles, INDEX.md, and SOURCES.md.

### Incremental Update

**User:** I added 2 new papers to the research folder. Update the wiki.

**Agent:**
1. Loading compile state for `atlas-research-papers`...
2. Scanning sources: 10 total (2 new, 0 modified, 8 unchanged).
3. Converting 2 new PDFs... done.
4. Re-extracting concepts (including context from existing sources)...
5. Found 3 new concepts, updated 4 existing concepts.
6. Generating 3 new articles, updating 4 existing articles...
7. Refreshing INDEX.md and SOURCES.md...

**Result:** 3 new articles added, 4 articles updated with new source material. INDEX.md refreshed.

### Custom Output Directory

**User:** Compile `research/ml-privacy/` into a wiki called "privacy-survey" and put it in `01_Projects/Privacy/wiki/`.

**Agent:**
1. Wiki name: `privacy-survey` (user-provided)
2. Output directory: `01_Projects/Privacy/wiki/` (user-specified)
3. Processing 6 sources...
