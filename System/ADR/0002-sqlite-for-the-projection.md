# 0002 — SQLite/FTS for the derived projection

**Status:** Accepted

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
- Graph traversal is recursive SQL over an indexed `relations` table rather than
  a native graph engine. Measured index-backed rather than scanning; see
  `tests/test_performance.py`.
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
