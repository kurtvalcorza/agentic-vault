---
name: knowledge-runtime
description: Query, validate, reconcile, or safely propose updates through the optional agentic-vault knowledge runtime. Use when a task depends on typed entities, relations, claims, provenance, timelines, graph paths, or knowledge health.
---

# Knowledge Runtime

Use the knowledge runtime when it is installed and available. The runtime is agent-agnostic; tool aliases vary by harness.

## Rules

1. Prefer semantic runtime operations over manual graph reconstruction when the required knowledge is indexed.
2. Treat Markdown/YAML as canonical. Never edit the generated SQLite database as knowledge.
3. Distinguish WikiLink adjacency from typed semantic relations.
4. Distinguish asserted/extracted/inferred/ambiguous derivation.
5. Trace load-bearing semantic claims to evidence when available.
6. Never silently merge ambiguous entities.
7. Mutations are proposal-first: propose -> validate -> apply.
8. `apply` is outward state change and may be disabled/read-only. Follow the vault's confirmation/security protocols.
9. If the runtime is absent, fall back to normal vault search/read workflows rather than blocking.

## Common operations

- Resolve entity: `knowledge.resolve_entity`
- Search: `knowledge.search`
- Get object: `knowledge.get`
- Traverse typed relations: `knowledge.neighbors`, `knowledge.trace_path`
- Inspect history/evidence: `knowledge.timeline`, `knowledge.sources`
- Reconcile: `knowledge.contradictions`, `knowledge.health`
- Safe updates: `knowledge.propose_patch`, `knowledge.validate_patch`, `knowledge.apply_patch`

## Semantic enrichment

LLM-derived entities/relations/claims are candidates unless explicitly accepted by policy. Do not promote an inference to asserted canonical knowledge merely because the model is confident.
