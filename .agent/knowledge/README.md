# Agentic Vault Knowledge Runtime

Optional, generic, agent-agnostic knowledge runtime for `agentic-vault`.

The runtime keeps **Markdown/YAML as the canonical source of truth** and builds disposable local projections for validation, full-text search, graph traversal, provenance, and MCP access. It is domain-neutral and ships only synthetic examples.

## Components

- `schema/core.yaml` — LinkML base schema for knowledge objects, claims, evidence, relations, and bi-temporal records.
- `schema/relations.yaml` — controlled, extensible core relation registry.
- `runtime/` — deterministic parser, validator, entity resolver, SQLite/FTS index, query layer, safe mutation workflow, health checks, and optional enrichment adapter boundary.
- `mcp/server.py` — MCP adapter exposing semantic read/write operations without arbitrary SQL.
- `migrations/` — schema migration registry and runner.
- `tests/` — synthetic fixtures and acceptance-oriented tests.

## Install

From the vault root:

```bash
python -m venv .venv
# activate .venv, then
pip install -e ./.agent/knowledge
```

The runtime works without an LLM. Optional semantic enrichment is deliberately adapter-based and disabled by default.

## CLI

```bash
vault-knowledge validate
vault-knowledge build
vault-knowledge health
vault-knowledge search "sample"
vault-knowledge get project:sample-project
vault-knowledge neighbors project:sample-project
vault-knowledge trace project:sample-project concept:sample-concept
```

The default generated database is `.agent/knowledge/generated/knowledge.db`. It is disposable and should not be treated as authoritative.

## Semantic note marker

A Markdown file becomes a semantic knowledge object when its frontmatter contains both `id` and `type`:

```yaml
---
id: project:sample-project
type: Project
title: Sample Project
aliases: [Project Sample]
relations:
  - predicate: related_to
    target: concept:sample-concept
    derivation: asserted
    status: accepted
---
```

Normal operational Markdown remains searchable/navigation-capable but is not required to satisfy semantic schemas.

## Design invariants

1. Markdown is authoritative.
2. Derived stores are disposable and rebuildable.
3. Stable IDs are independent of file paths/titles.
4. WikiLink adjacency and typed semantic relations are distinct.
5. Assertions, extraction, inference, and ambiguity remain distinguishable.
6. Claims/relations may carry evidence and temporal metadata.
7. Agent-generated candidates do not silently become accepted facts.
8. Deterministic extraction wins over LLM extraction.
9. Schema evolution is versioned and migratable.
10. Agent/vendor/graph-engine integrations remain replaceable adapters.

See `DESIGN.md` and GitHub issue #2 for the complete contract.
