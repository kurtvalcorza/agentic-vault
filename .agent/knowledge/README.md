# Agentic Vault Knowledge Runtime

Optional, generic, agent-agnostic knowledge runtime for `agentic-vault`.

The runtime keeps **Markdown/YAML as the canonical source of truth** and builds disposable local projections for validation, full-text/graph retrieval, provenance, temporal queries, analytics, interoperability, and MCP access. It is domain-neutral and ships only synthetic examples.

## Components

- `schema/core.yaml` — LinkML base schema for knowledge objects, claims, evidence, relations, lifecycle, and bi-temporal fields.
- `schema/relations.yaml` — controlled, extensible core relation registry.
- `schema/extensions/` — deterministic downstream ontology/relation extension point.
- `agentic_vault_knowledge/` — parser, semantic validator, entity resolver, SQLite/FTS index, claims/graph runtime, retrieval/enrichment adapter contracts, safe transactions, interop, CLI, and MCP adapter.
- `migrations/` — explicit canonical-schema migration contract; generated DB schema upgrades are handled separately because the DB is disposable.
- `tests/` — synthetic acceptance and failure-mode tests.

## Install

From the vault root:

```bash
python -m venv .venv
# activate .venv, then
pip install -e './.agent/knowledge[test,linkml]'
```

Baseline operation needs no LLM, API key, embeddings, graph server, or remote service. Optional semantic enrichment and retrieval backends implement adapter protocols and return candidates/ranked results; they never become canonical storage.

## CLI

```bash
vault-knowledge --vault . validate
vault-knowledge --vault . build --full
vault-knowledge --vault . health
vault-knowledge --vault . search "sample"
vault-knowledge --vault . retrieve "sample"
vault-knowledge --vault . resolve project:sample-project
vault-knowledge --vault . get project:sample-project
vault-knowledge --vault . neighbors project:sample-project
vault-knowledge --vault . trace project:a project:b
vault-knowledge --vault . state-as-of project:sample-project 2026-08-20T00:00:00+00:00
vault-knowledge --vault . claims project:sample-project
vault-knowledge --vault . contradictions
vault-knowledge --vault . communities
vault-knowledge --vault . export-okf .agent/outputs/okf-export
vault-knowledge --vault . export-jsonld .agent/outputs/knowledge.jsonld
vault-knowledge --vault . export-rdf .agent/outputs/knowledge.nt
```

The default generated database is `.agent/knowledge/generated/knowledge.db`. It is gitignored, disposable, and fully rebuildable from canonical Markdown.

## Semantic note marker

A Markdown file is a semantic knowledge object when its frontmatter contains a stable `id` and a `type`:

```yaml
---
id: project:sample-project
knowledge_schema: 0.1.0
type: Project
title: Sample Project
aliases: [Project Sample]
status: active
relations:
  - predicate: related_to
    target: concept:sample-concept
    derivation: asserted
    status: accepted
---
```

Operational Markdown can remain ordinary Markdown. Existing templates, session logs, skills, steering docs, Kanban files, and other non-semantic files do not need to conform to the knowledge schema.

## Claims and promotion

Claims are first-class and carry their own lifecycle/provenance:

```yaml
claims:
  - id: claim:sample
    subject: project:sample-project
    predicate: depends_on
    object: artifact:sample-system
    status: proposed
    derivation: inferred
    valid_from: 2026-08-01
    recorded_at: 2026-08-02T09:00:00+08:00
    extraction_confidence: 0.91
    claim_confidence: 0.72
    evidence:
      - source: source:sample-design
        source_authority: primary
        locator:
          type: heading
          value: Dependencies
```

Only **accepted** entity-to-entity claims are projected into the assertion graph. Candidate/proposed claims stay inspectable without silently becoming canonical truth. Inferred accepted edges remain distinguishable and are excluded from ordinary neighbor queries unless explicitly requested.

## Navigation vs semantic graph

- **Navigation graph:** deterministic WikiLink adjacency; broad but semantically weak.
- **Semantic graph:** typed relations plus accepted claim projections; intentionally narrower and validated.

A WikiLink never automatically becomes a semantic `related_to` edge.

## Safe writes

The agent-facing mutation flow is proposal-first:

```text
propose -> validate -> hash/conflict check -> atomic apply -> re-index
```

Multi-file batches are staged before replacement and rolled back if replacement fails. MCP is **read-only by default**. Set `AGENTIC_VAULT_KNOWLEDGE_READ_ONLY=0` only when the host/user intends to allow canonical writes.

## MCP

Run locally over stdio (the MCP SDK default):

```bash
vault-knowledge-mcp
```

Set `AGENTIC_VAULT_ROOT` when the process is launched outside the vault root. The server exposes semantic operations for validation, resolution, search/retrieval, graph traversal, claims/evidence, temporal state, health/analytics, and proposal/validation/apply workflows. MCP contains no unique business logic; the CLI/tests use the same runtime library.

## Extensions

The public core stays domain-neutral. Downstream/private vaults may add classes and predicates under `schema/extensions/*.yaml`; extensions load deterministically and may not shadow core definitions. Provider/model-specific code belongs in adapters, not in the canonical schema.

## Interoperability

- **OKF v0.2:** Markdown/YAML bundle export + validation + candidate-only import.
- **JSON-LD:** disposable graph projection.
- **RDF:** N-Triples projection using reversible `urn:agentic-vault:*` identifiers.

These are interchange views, not replacement storage models.

## Design invariants

1. Markdown is authoritative.
2. Derived stores are disposable and rebuildable.
3. Stable IDs are independent of file paths/titles.
4. WikiLink adjacency and typed semantic relations are distinct.
5. Assertions, extraction, inference, and ambiguity remain distinguishable.
6. Claims/relations may carry fine-grained evidence and temporal metadata.
7. Candidate/proposed knowledge does not silently become accepted.
8. Deterministic extraction wins over LLM extraction.
9. Schema evolution is versioned and migratable.
10. Writes validate and conflict-check before canonical mutation.
11. Agent/vendor/graph/vector integrations remain replaceable adapters.
12. Public fixtures and ontology remain synthetic/domain-neutral.

See `DESIGN.md` and GitHub issue #2 for the complete contract.
