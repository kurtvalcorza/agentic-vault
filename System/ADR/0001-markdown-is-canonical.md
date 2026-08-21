# 0001 — Markdown/YAML is canonical; projections are disposable

**Status:** Accepted
**Related:** [[0002-sqlite-for-the-projection]] · [[0003-content-based-fingerprint]] · [[0006-writes-off-by-default-everywhere]] · [[AGENTS.md]]

## Context

The runtime needs indexes, a graph, and full-text search to answer questions
quickly. The obvious way to get those is to make the database the system of
record and treat files as an import format. Most knowledge tools do exactly that.

This vault is an Obsidian vault. Its notes are edited by a human in an editor
that knows nothing about the runtime, synced by tools that know nothing about it,
and versioned by git line-by-line.

## Decision

Markdown/YAML files are the **only** source of truth. Every derived store is
disposable and reconstructible from them by a full rebuild.

## Consequences

- Deleting `.agent/knowledge/generated/` is always safe. That is the recovery
  procedure for any index corruption, and it makes the DB gitignorable.
- The runtime can be uninstalled without data loss — it is genuinely optional,
  which is what lets `knowledge-runtime` say "fall back to ordinary search".
- Writes are harder: a mutation must edit Markdown and re-index, rather than
  updating a row. Hence the proposal-first flow with hash-bound conflict checks.
- Some queries are slower than a database-native design would allow. Accepted.
- **Never edit the generated database as knowledge.** Anything written only
  there is destroyed by the next rebuild, silently.

## Alternatives considered

**Database as system of record, files as export.** Faster and simpler
internally. Rejected: it breaks editing the vault in Obsidian, breaks git as a
meaningful history, and makes the runtime mandatory rather than optional. The
runtime is a lens on the vault; it must not become the vault.

**Bidirectional sync.** Rejected: requires conflict resolution between two
writable stores, which is a substantially harder problem than the one being
solved, and fails in exactly the situation it exists for — concurrent edits.
