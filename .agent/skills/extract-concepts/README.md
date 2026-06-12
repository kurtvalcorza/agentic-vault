# extract-concepts

Run a periodic LLM pass over vault areas to discover recurring concepts and generate concept hub pages with backlinks. Supports a health mode for detecting terminology inconsistencies, stale hubs, and missing cross-links.

## Purpose

Surfaces emergent themes across your vault by scanning Markdown files for recurring concepts:
- **Concept hubs** — one hub page per recurring theme, placed in `02_Areas/` per intake policy
- **Backlinks** — batch-inserts backlinks into source notes referencing each concept
- **Gap analysis** — identifies existing hubs with unlinked sources and orphaned hubs
- **Health mode** — detects terminology inconsistencies, stale hubs, missing cross-links between related hubs
- **Ignore list** — rejected concepts are remembered and not re-proposed

## Usage

### Basic Run (Default)

```
Find recurring concepts in my Areas
```

Scans `02_Areas/`, proposes concept hubs for themes appearing in 3+ notes.

### Custom Target Directory

```
Extract concepts from 02_Areas/AI_and_Data_Science/
```

### Custom Threshold

```
Extract concepts with threshold of 5
```

Only proposes concepts appearing in 5+ distinct notes.

### Health Mode

```
Run concept health check on my Areas
```

Runs the standard extraction pipeline plus health checks for terminology inconsistencies, stale hubs, and missing cross-links.

## Output Examples

### Concept Hub (Generated)

```yaml
---
title: "Federated Learning"
type: concept-article
origin: extracted
area: "02_Areas/AI_and_Data_Science"
sources_count: 7
created: 2026-04-03
updated: 2026-04-03
tags:
  - concept-article
  - ai
---

## Summary

Federated Learning is a distributed machine learning approach that enables
model training across decentralized data sources without exchanging raw data.
It appears across Project Atlas project documentation, AI governance notes, and
technical research summaries in this vault.

The concept connects privacy-preserving computation with practical deployment
challenges in government AI systems, particularly in the public-sector context
where data sovereignty is a key concern.

## Key Appearances

- [[Project Atlas Technical Architecture]] — describes FL as core training paradigm
- [[AI Governance Framework]] — discusses FL in context of data privacy regulations
- [[Distributed Systems Notes]] — covers FL aggregation strategies
- [[Project Cedar Research Priorities]] — lists FL as priority research area

## Related Concepts

- [[Differential Privacy]]
- [[Model Aggregation]]
- [[Data Governance]]

## Notes

There is a tension between the theoretical privacy guarantees of FL and the
practical challenges of deploying it in resource-constrained environments
like regional iHubs.
```

### Remediation Report (Health Mode)

```markdown
# Concept Health Report — 02_Areas/
**Date:** 2026-04-03
**Files scanned:** 142
**Existing concept hubs:** 15

## Terminology Inconsistencies

| Variant A | Variant B | Notes Using A | Notes Using B | Suggested Canonical |
|-----------|-----------|---------------|---------------|---------------------|
| FL        | Federated Learning | 3          | 5             | Federated Learning  |
| LLM       | Large Language Model | 8         | 2             | Large Language Model |

## Stale Hubs

| Hub | Source Notes | Status |
|-----|-------------|--------|
| [[Blockchain Basics]] | 3 sources, all archived | Recommend archive |

## Missing Cross-Links

| Hub A | Hub B | Shared Sources | Action |
|-------|-------|----------------|--------|
| [[Federated Learning]] | [[Differential Privacy]] | 4 | Add mutual WikiLinks |

## Summary
- 2 terminology inconsistencies found
- 1 stale hub detected
- 1 missing cross-link identified
```

## Processing Pipeline

The skill operates in 5 phases:

1. **Scan** — Read all `.md` files in target directory, extract titles, frontmatter, key terms, WikiLinks, tags
2. **Cluster** — Group related terms (abbreviations, synonyms), filter by occurrence threshold, exclude ignored concepts
3. **Gap Analysis** — Check for existing hub pages, identify unlinked source notes, find orphaned hubs
4. **Proposal** — Present candidates to user with title, source count, 2-sentence preview; user approves/rejects each
5. **Generation** — Create hub pages via template, batch-insert backlinks (single user confirmation), update AREA-INDEX

## Ignore List

Rejected concepts are appended to `.agent/concept-ignore.txt` (one concept per line). These concepts will not be re-proposed on future runs. To re-enable a concept, remove or comment out its line in the file.

## Prerequisites

| Dependency | Path | Required |
|:-----------|:-----|:---------|
| Concept ignore list | `.agent/concept-ignore.txt` | Auto-created if missing |
| Area intake policy | `02_Areas/area-intake-policy.md` | For hub placement decisions |
| AREA-INDEX | `02_Areas/AREA-INDEX.md` | Updated when new hubs are created |
| Concept hub template | `.agent/skills/extract-concepts/templates/concept-hub-template.md` | Template for generated hubs |

## Test Scenarios

### Test 1: Basic Extraction
- **Input:** Run on `02_Areas/AI_and_Data_Science/`
- **Expected:** Proposes concept hubs for themes appearing in 3+ notes. Each proposal includes title, source count, and 2-sentence preview.

### Test 2: No Duplicate Proposals
- **Input:** Re-run after approving hubs from Test 1
- **Expected:** Previously created hubs are detected as existing — no duplicate proposals. Rejected concepts are on the ignore list — not re-proposed.

### Test 3: Health Mode
- **Input:** Run with `--health` flag
- **Expected:** Detects a concept with two naming variants (e.g., "FL" vs "Federated Learning"). Outputs remediation report with suggested renames/merges.

### Test 4: Agent Skills Standard Compliance
- **Validate:** `SKILL.md` has proper YAML frontmatter with `name` and `description`
- **Validate:** Uses agent-agnostic tool names from `.agent/TOOL-TAXONOMY.md`
- **Validate:** Dual documentation pattern (SKILL.md + README.md)
- **Validate:** Directory structure follows `skill-name/{SKILL.md, README.md, references/, templates/}`

## Related Skills

- `compile-wiki` — Compiles source folders into structured wikis (upstream content producer)
- `query-vault` — Q&A against vault content (uses concept hubs for discovery)
- `validate-workspace` — Workspace health checks (complementary maintenance)
- `optimize-workspace` — Vault optimization (complementary maintenance)
