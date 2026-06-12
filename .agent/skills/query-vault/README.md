# query-vault

Answer complex questions by searching and synthesizing content from the vault's own notes, compiled wikis, and project docs. Returns answers with inline `[[WikiLink]]` citations, confidence levels, and gap analysis.

## Purpose

Interrogates the vault as a knowledge corpus — finds relevant notes, synthesizes a coherent answer, and cites sources as WikiLinks. Explicitly flags what the vault does NOT cover and suggests next steps for filling gaps.

Key capabilities:
- **Cross-domain synthesis** — searches across Projects, Areas, Resources, and compiled wikis
- **Cited answers** — every claim backed by `[[WikiLink]]` to source note
- **Confidence scoring** — high / medium / low based on evidence quality
- **Gap detection** — identifies missing information and suggests search terms
- **Scoped queries** — limit search to a specific directory
- **Multiple output formats** — inline, Obsidian note, or structured report

## Usage

### Basic Query (Inline)

```
What do my notes say about federated learning?
```

Returns the answer directly in conversation with WikiLink citations.

### Scoped Query

```
What does my Project Atlas project say about model deployment? --scope 01_Projects/Project Atlas/
```

Limits all searches to the specified directory and its subdirectories.

### Output as Note

```
What do my notes say about science communication frameworks? --output note
```

Delegates to `write-note` skill — creates an Obsidian note in `Inbox/` with proper frontmatter.

### Output as Report

```
Summarize what I know about AI governance --output report
```

Generates a structured Markdown report with Question, Findings, Evidence, Gaps, and References sections.

## Output Examples

### Inline Answer

```
Your vault covers federated learning extensively. According to [[Federated Learning]],
it is a distributed ML approach that trains models across decentralized data sources.
The [[Project Atlas]] project explores FL applications, as noted in [[Project Atlas Research Notes]].

**Confidence:** high — multiple corroborating sources.

**Gaps:** No coverage of FL deployment challenges. Suggested search terms:
"federated learning communication efficiency", "non-IID data federated".
```

### Answer Note Frontmatter

```yaml
---
title: "Vault Q&A — Federated Learning Overview"
type: vault-qa
question: "What do my notes say about federated learning?"
sources:
  - "[[Federated Learning]]"
  - "[[Project Atlas Research Notes]]"
  - "[[Differential Privacy]]"
confidence: high
created: 2026-04-03
tags:
  - vault-qa
  - synthesis
---
```

### Report Structure

```markdown
# Vault Report — AI Governance

## Question
What do my notes say about AI governance?

## Findings
[Synthesized answer with [[WikiLink]] citations]

## Evidence
[Key passages from each source, quoted with attribution]

## Gaps & Limitations
[What the vault doesn't cover, suggested search terms]

## References
- [[AI Governance Notes]]
- [[NAIS Ph Strategy]]
- [[Project Cedar Program Overview]]
```

## Query Resolution Strategy

The skill uses a 4-step resolution strategy:

1. **Index Scan (broad)** — Read AREA-INDEX, RESOURCE-INDEX, compiled wiki INDEX.md files, and vault-search top-20 candidates to build a ranked candidate list
2. **Targeted Read (deep)** — Read top 5-10 candidates in full, follow WikiLinks 1 hop for additional context
3. **Synthesis** — Generate answer with `[[WikiLink]]` citations, assess confidence, detect gaps
4. **Filing (optional)** — `--output note` delegates to `write-note`, `--output report` writes structured Markdown

## Confidence Levels

| Level | Criteria |
|:------|:---------|
| **high** | Multiple corroborating sources from different vault areas |
| **medium** | Single authoritative source, or partial coverage from multiple sources |
| **low** | Inferred from tangential references; vault has significant gaps |

## Insufficient Information

When the vault lacks sufficient information, the skill:
1. States clearly that the vault cannot answer the question
2. Lists any partial or tangential findings
3. Suggests search terms for external research
4. Recommends skills for ingesting new material (`clip-and-localize`, `compile-wiki`)

## Prerequisites

| Dependency | Path | Required |
|:-----------|:-----|:---------|
| Vault search index | `.agent/search-index/index.json` | Recommended (falls back to content-search) |
| `vault-search.py` CLI | `.agent/scripts/vault-search.py` | Recommended (for fast candidate discovery) |
| AREA-INDEX | `02_Areas/AREA-INDEX.md` | Recommended (skipped if missing) |
| RESOURCE-INDEX | `03_Resources/RESOURCE-INDEX.md` | Recommended (skipped if missing) |
| Compiled wikis | `03_Resources/Compiled/*/INDEX.md` | Optional (enhances results) |
| `write-note` skill | `.agent/skills/write-note/` | Required for `--output note` mode |

## Test Scenarios

### Test 1: Well-Documented Topic
- **Input:** Ask about a topic with multiple vault notes (e.g., a known project or concept)
- **Expected:** Cited answer with 2+ WikiLinks, confidence high or medium

### Test 2: Topic Not in Vault
- **Input:** Ask about a topic with no vault coverage
- **Expected:** "Insufficient information" response with suggestions for external research

### Test 3: Output as Note
- **Input:** Query with `--output note`
- **Expected:** Valid Obsidian note in `Inbox/` with frontmatter (title, type: vault-qa, question, sources, confidence, tags)

### Test 4: Scoped Query
- **Input:** Query with `--scope 01_Projects/Project Atlas/`
- **Expected:** All cited sources are within the scoped directory

### Test 5: Agent Skills Standard Compliance
- **Validate:** `SKILL.md` has proper YAML frontmatter with `name` and `description`
- **Validate:** Uses agent-agnostic tool names from `.agent/TOOL-TAXONOMY.md`
- **Validate:** Dual documentation pattern (SKILL.md + README.md)
- **Validate:** Directory structure follows `skill-name/{SKILL.md, README.md, templates/}`

## Related Skills

- `compile-wiki` — Compiles source folders into structured wikis (upstream content producer)
- `clip-and-localize` — Clips web articles into the vault (data ingest)
- `extract-concepts` — Discovers recurring concepts across vault content
- `write-note` — Creates Obsidian notes with proper frontmatter (used by `--output note`)
