---
name: query-vault
description: Answer complex questions by searching and synthesizing content from the vault's own notes, compiled wikis, and project docs. Use when asking questions about vault content, querying personal knowledge base, searching across notes for answers, or interrogating accumulated knowledge with citations.
---

# query-vault

Answers natural language questions by searching across vault content (notes, compiled wikis, project docs) and synthesizing an answer with inline `[[WikiLink]]` citations. Explicitly flags confidence level and identifies gaps when the vault lacks sufficient information.

## Trigger Phrases

- "What do my notes say about X?"
- "Search my vault for information on X"
- "Query my knowledge base about X"
- "What have I written about X?"
- "Summarize what I know about X"
- "Find everything in my vault related to X"

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| Question | Yes | — | Natural language question to answer from vault content |
| `--scope` | No | Entire vault | Limit search to a specific directory (e.g., `--scope 01_Projects/Project Atlas/`) |
| `--output` | No | `inline` | Output format: `inline` (conversation), `note` (Obsidian note via `write-note`), `report` (structured Markdown report) |

---

## Step 1 — Index Scan (Broad Discovery)

Identify candidate files that may contain relevant information. This is a breadth-first pass — read indexes and metadata, not full file content.

### Step 1.1 — Apply Scope Filter

If the user provided `--scope {directory}`:
- **All subsequent file reads and searches are limited to that directory and its subdirectories.**
- Skip Steps 1.2–1.4 (vault-wide indexes) and go directly to Step 1.5, scoped to the specified directory.
- In Step 1.5, pass the scope directory as the `--path` filter to vault-search.

If no scope is provided, proceed with full vault discovery (Steps 1.2–1.5).

### Step 1.2 — Read Area Index

```
**Tool:** file-read
Read `02_Areas/AREA-INDEX.md`
```

Scan the index for entries related to the question's topic. Note any relevant area directories and note names for Step 2.

### Step 1.3 — Read Resource Index

```
**Tool:** file-read
Read `03_Resources/RESOURCE-INDEX.md` (if it exists)
```

Scan the **Source Catalog** table for relevant entries (by title, author, type, or tags). Also check reference documents and compiled wiki pointers. The Source Catalog tracks all sources encountered — including those without vault notes — so it may surface sources not discoverable through file search alone.

### Step 1.4 — Discover Compiled Wikis

```
**Tool:** file-search
Glob for `03_Resources/Compiled/*/INDEX.md`
```

For each discovered `INDEX.md`:

```
**Tool:** file-read
Read the compiled wiki INDEX.md
```

Scan each wiki index for articles related to the question. Compiled wikis are high-value sources — they contain synthesized, interlinked concept articles.

### Step 1.5 — Vault Search (Top-20 Candidates)

If the vault search index exists (`.agent/search-index/index.json`):

```
**Tool:** command-exec → python .agent/scripts/vault-search.py --json --limit 20 "{search terms}"
```

Extract effective search terms from the user's question:
- Use key nouns, technical terms, and named entities
- Drop filler words ("what", "how", "does", "my", "notes", "say", "about")
- If the question mentions a specific project or concept, include it as a search term

If `--scope` is active, add the path filter:
```
**Tool:** command-exec → python .agent/scripts/vault-search.py --json --limit 20 --path "{scope_directory}" "{search terms}"
```

If the vault search index does not exist, fall back to content-search:
```
**Tool:** content-search
Search for key terms from the question across `.md` files in the vault (or scoped directory).
```

### Step 1.6 — Build Candidate List

Merge results from Steps 1.2–1.5 into a ranked candidate list:
1. Files mentioned in multiple sources (index + search) rank highest
2. Files from compiled wiki indexes rank above raw notes
3. Files with higher vault-search scores rank above lower scores
4. Deduplicate by file path

Output: a ranked list of 10–20 candidate file paths.

---

## Step 2 — Targeted Read (Deep Evidence Gathering)

Read the most promising candidates in full and follow their links one hop.

### Step 2.1 — Read Top Candidates

Select the top 5–10 candidates from the ranked list (prioritize diversity — don't read 5 files from the same directory if candidates span multiple areas).

```
**Tool:** file-read
Read each candidate file in full.
```

For each file, extract:
- Key passages relevant to the question
- Outgoing WikiLinks (`[[Note Name]]`) that may contain additional evidence
- Frontmatter metadata (title, type, tags, sources)

### Step 2.2 — Follow WikiLinks (1 Hop)

From the files read in Step 2.1, collect all outgoing WikiLinks. Filter to links that appear topically relevant to the question (by name/context).

For the most relevant linked files (up to 5 additional files):

```
**Tool:** file-read
Read the linked file.
```

This 1-hop follow captures context that the top candidates reference but don't fully explain.

### Step 2.3 — Build Evidence Corpus

Compile all relevant passages into an evidence corpus:
- Tag each passage with its source file path (for citation)
- Note which passages corroborate each other
- Note which passages contradict or add nuance
- Identify any gaps — aspects of the question not covered by any source

---

## Step 3 — Synthesis

Generate the answer from the evidence corpus.

### Step 3.1 — Synthesize Answer

Compose an answer that:
1. **Directly addresses the question** — lead with the answer, not background
2. **Cites sources as WikiLinks** — use `[[Note Name]]` inline (e.g., "According to [[Federated Learning]], the approach uses...")
3. **Synthesizes across sources** — don't just list what each note says; weave findings into a coherent narrative
4. **Acknowledges nuance** — if sources disagree or present different perspectives, note this
5. **Uses the vault's own terminology** — mirror the language used in the source notes

### Step 3.2 — Assess Confidence

Assign a confidence level based on evidence quality:

| Level | Criteria |
|:------|:---------|
| **high** | Multiple corroborating sources from different vault areas; topic is well-documented |
| **medium** | Single authoritative source, or partial coverage from multiple sources |
| **low** | Inferred from tangential references; vault has significant gaps on this topic |

State the confidence level explicitly in the answer.

### Step 3.3 — Gap Detection

Explicitly identify what the vault does NOT cover:
- Aspects of the question that no source addresses
- Topics mentioned in sources but not elaborated on in the vault
- Areas where the vault's information may be outdated

For each gap, suggest:
- **Search terms** for external research (web search, literature databases)
- **Vault areas** where the missing information might logically be added
- **Related skills** that could help fill the gap (e.g., `clip-and-localize` for web sources, `compile-wiki` for structuring new material)

### Step 3.4 — Insufficient Information Handling

If the vault does not contain sufficient information to answer the question:

1. **Do NOT hallucinate an answer.** State clearly: "The vault does not contain sufficient information to answer this question."
2. List what WAS found (if anything) — partial matches, tangentially related notes.
3. Suggest specific actions:
   - Search terms for external research
   - Vault areas to check manually
   - Skills to use for ingesting new material (`clip-and-localize`, `compile-wiki`)

---

## Step 4 — Output Filing

Deliver the answer in the requested format.

### `--output inline` (Default)

Return the answer directly in the conversation. Include:
- The synthesized answer with `[[WikiLink]]` citations
- Confidence level
- Gap analysis (if any gaps detected)
- List of sources consulted

### `--output note`

Delegate to the `write-note` skill to create a vault note:

```
Delegate to: .agent/skills/write-note/
```

Provide the `write-note` skill with:
- **Title:** "Vault Q&A — {brief summary of question}"
- **Content:** The synthesized answer (same as inline output)
- **Frontmatter** (from `templates/answer-note-template.md`):
  ```yaml
  title: "Vault Q&A — {summary}"
  type: vault-qa
  question: "{original question}"
  sources:
    - "[[Source Note 1]]"
    - "[[Source Note 2]]"
  confidence: {high|medium|low}
  created: {YYYY-MM-DD}
  tags:
    - vault-qa
    - synthesis
  ```
- **Destination:** `Inbox/` (default for `write-note`)

The `write-note` skill handles file creation, frontmatter formatting, and placement.

### `--output report`

Generate a structured Markdown report using `templates/report-template.md`:

```
**Tool:** file-write
Write the report to a user-specified path, or default to `Inbox/{YYYY-MM-DD}_vault-report_{slugified-question}.md`
```

Report structure:
1. **Question** — the original question
2. **Findings** — synthesized answer with citations
3. **Evidence** — key passages from each source (quoted with attribution)
4. **Gaps & Limitations** — what the vault doesn't cover
5. **References** — full list of consulted notes as WikiLinks

Report frontmatter:
```yaml
title: "Vault Report — {summary}"
type: vault-report
question: "{original question}"
sources:
  - "[[Source Note 1]]"
  - "[[Source Note 2]]"
confidence: {high|medium|low}
created: {YYYY-MM-DD}
tags:
  - vault-report
  - synthesis
```

---

## Required Capabilities

| Capability | Usage |
|:-----------|:------|
| `file-read` | Read index files, candidate notes, linked notes |
| `file-write` | Write report output (--output report) |
| `file-search` | Discover compiled wiki INDEX.md files |
| `content-search` | Fallback search when vault-search index unavailable |
| `command-exec` | Invoke `vault-search.py` CLI for candidate discovery |

### Delegated Skills

| Skill | Path | Purpose |
|:------|:-----|:--------|
| `write-note` | `.agent/skills/write-note/` | File answer as Obsidian note (`--output note`) |

### Infrastructure

| Resource | Path | Purpose |
|:---------|:-----|:--------|
| Vault search index | `.agent/search-index/index.json` | Fast candidate discovery (optional but recommended) |
| vault-search CLI | `.agent/scripts/vault-search.py` | Query the search index |
| AREA-INDEX | `02_Areas/AREA-INDEX.md` | Area-level topic discovery |
| RESOURCE-INDEX | `03_Resources/RESOURCE-INDEX.md` | Source Catalog and resource-level topic discovery |
| Compiled wiki indexes | `03_Resources/Compiled/*/INDEX.md` | Compiled knowledge discovery |

---

## Error Handling

| Scenario | Action |
|:---------|:-------|
| Vault search index not found | Fall back to `content-search` across `.md` files; warn user that results may be slower/less comprehensive |
| AREA-INDEX or RESOURCE-INDEX missing | Skip that index; proceed with other discovery methods |
| No compiled wikis found | Skip Step 1.4; rely on search index and content-search |
| `--scope` directory does not exist | Report error: "Directory not found: {path}". Suggest checking the path. |
| No relevant results found | Follow Step 3.4 — insufficient information handling |
| `write-note` skill unavailable | For `--output note`: fall back to writing the note directly using `file-write` with the answer-note-template frontmatter |
| WikiLink target ambiguous (multiple matches) | Use fully qualified `[[path/to/Note Name]]` form |

---

## Examples

### Basic Query (Inline)

**User:** What do my notes say about federated learning?

**Agent:**
1. Reading AREA-INDEX... found entries under AI_and_Data_Science.
2. Reading RESOURCE-INDEX... found compiled wiki reference.
3. Discovered compiled wiki: `03_Resources/Compiled/ml-research/INDEX.md` — contains [[Federated Learning]] article.
4. Vault search: top candidates include `02_Areas/AI_and_Data_Science/federated-learning.md`, `01_Projects/Project Atlas/research-notes.md`.
5. Reading top 5 candidates...
6. Following WikiLinks to [[Differential Privacy]], [[Model Aggregation]]...

**Answer:**
Your vault covers federated learning extensively. According to [[Federated Learning]], it is a distributed ML approach that trains models across decentralized data sources without exchanging raw data. The [[Project Atlas]] project explores FL applications for government AI services, as noted in [[Project Atlas Research Notes]].

Key aspects documented:
- **Architecture:** [[Model Aggregation]] describes FedAvg and FedProx strategies
- **Privacy:** [[Differential Privacy]] covers the mathematical guarantees applied in FL settings
- **Applications:** [[Project Atlas Research Notes]] discusses FL for health data and government services

**Confidence:** high — multiple corroborating sources across Areas and compiled wikis.

**Gaps:** Your vault does not cover FL deployment challenges (communication overhead, non-IID data). Suggested search terms: "federated learning communication efficiency", "non-IID data federated".

### Scoped Query

**User:** What does my Project Atlas project say about model deployment? --scope 01_Projects/Project Atlas/

**Agent:**
1. Scope active: limiting all searches to `01_Projects/Project Atlas/`.
2. Vault search (scoped): `vault-search.py --json --limit 20 --path "01_Projects/Project Atlas/" "model deployment"`
3. Reading top candidates within Project Atlas project...

### Output as Note

**User:** What do my notes say about science communication frameworks? --output note

**Agent:**
1. [Performs Steps 1-3 as normal]
2. Delegating to `write-note` skill with:
   - Title: "Vault Q&A — Science Communication Frameworks"
   - Content: synthesized answer with citations
   - Frontmatter: type vault-qa, sources list, confidence level
3. Note written to `Inbox/`.

### Insufficient Information

**User:** What do my notes say about quantum computing?

**Agent:**
The vault does not contain sufficient information to answer this question comprehensively.

**Partial findings:**
- [[AI Governance Notes]] mentions quantum computing briefly in the context of future threats to encryption, but does not elaborate.

**Suggestions:**
- Search terms for external research: "quantum computing overview", "quantum machine learning applications"
- Consider using `clip-and-localize` to clip introductory articles into the vault
- After clipping, use `compile-wiki` to build a structured quantum computing reference

**Confidence:** low — only tangential references found.
