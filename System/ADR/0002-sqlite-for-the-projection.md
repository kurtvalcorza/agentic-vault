# 0002 — SQLite/FTS for the derived projection

**Status:** Accepted
**Related:** [[0001-markdown-is-canonical]] · [[0003-content-based-fingerprint]] · [[0004-stdlib-only-runtime-dependencies]] · [[AGENTS.md]]

## Context

Given ADR-0001, the projection needs typed lookup, graph traversal, full-text
search, and temporal queries — over a vault that may hold tens of thousands of
notes, on a personal machine, with no server to administer.

## Decision

A single SQLite database with FTS5, written to `.agent/knowledge/generated/`.

## Consequences

- Zero setup: SQLite ships with Python. No daemon, no port, no credentials, and
  nothing to keep running between sessions — which is what allows the
  `vault-knowledge` MCP server to work with Obsidian closed.
- One file to delete for a clean rebuild (ADR-0001).
- Graph traversal is **a Python breadth-first search over indexed SQL lookups**,
  not recursive SQL and not a native graph engine. `core.trace()` keeps a
  `deque` frontier and issues one indexed query per visited node; `neighbors()`
  matches `source_id=? OR target_id=?`, which SQLite satisfies with a
  `MULTI-INDEX OR` across `relations_source` and `relations_target`.
- That shape has a consequence worth knowing: traversal cost is one round trip
  per node, so depth is paid in Python rather than inside the engine.
  `trace()` therefore takes a `max_depth`, defaulting to 6. A deep trace needs
  it raised explicitly — measured at 12 ms across a 399-hop chain
  (`test_query_surface_stays_responsive`).
- Concurrent writers are limited. Acceptable: the projection has one writer.

## Alternatives considered

**A graph database (Neo4j, KùzuDB).** Better traversal ergonomics. Rejected for
the baseline: a server or a heavier dependency contradicts ADR-0004, and it would
make the optional runtime a piece of infrastructure to operate. The adapter
boundary exists so a downstream vault can add one without changing the core.

**A vector store as the primary index.** Rejected: embeddings are approximate
and model-dependent, which is the wrong property for a canonical projection.
Retrieval adapters may add one; it returns ranked candidates, never storage.

**In-memory only.** Rejected: rebuild cost would be paid on every process start,
including every MCP server launch.
