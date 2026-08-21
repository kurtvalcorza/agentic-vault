# 0003 — Rebuild fingerprint includes a content digest

**Status:** Accepted
**Related:** [[0001-markdown-is-canonical]] · [[0002-sqlite-for-the-projection]] · [[0005-builds-fail-closed]] · [[AGENTS.md]]

## Context

`RuntimeIndex.refresh()` should not redo work when nothing changed. The cheap way
to detect "nothing changed" is file metadata — mtime and size — which is what
most build tools use.

Metadata alone is not sufficient here. Sync clients and editors can preserve
mtime and byte length across a real edit, and mtime granularity can miss a
same-second change. A metadata-only fingerprint would then skip the rebuild and
serve a stale graph.

## Decision

The fingerprint is a tuple **per file** of `(relative path, st_mtime_ns,
st_size, sha256 of contents)` — for every scanned note, every schema YAML, and
`VERSION`. The content digest is **added to** the metadata, not substituted for
it. The short-circuit lives in `refresh()`; `build()` always does the full work
and is the right call for an unconditional rebuild.

## Consequences

- A real edit can never be missed, because the digest cannot stay equal when the
  canonical bytes change. That is the property being bought.
- **The converse is not true: identical content can still invalidate the
  fingerprint.** Because `st_mtime_ns` is part of the tuple, a sync client, a
  `git checkout`, or anything that rewrites timestamps forces a full rebuild even
  though nothing was edited. Verified directly: bumping `st_mtime_ns` on a
  byte-identical file changes the fingerprint and `refresh()` rebuilds.
- The error therefore leans toward **unnecessary work, never stale answers**,
  which is the correct direction for a derived store — but on a vault living in a
  sync folder, expect the short-circuit to miss more often than "content-based"
  would suggest.
- When the short-circuit does hit, the saving is substantial: measured on 400
  synthetic notes, **2196 ms cold vs 264 ms warm, about 88% saved**
  (`test_refresh_short_circuits_on_unchanged_vault`). The warm path still reads
  and hashes every file; it skips parse, validate and write.
- Calling `build()` twice does **not** exercise this and shows no short-circuit —
  a mistake made once already while writing these benchmarks.

## Alternatives considered

**Metadata-only fingerprint (mtime + size).** Proposed in issue #9. Rejected: it
converts a performance question into a correctness one. Serving a stale graph is
a worse failure than a slower refresh, and it fails silently.

**Digest only, dropping mtime and size.** Would remove the spurious-rebuild
behaviour above, since byte-identical files would compare equal regardless of
timestamps. Not adopted, but it is the obvious refinement if sync-driven mtime
churn becomes a practical problem: the digest already subsumes metadata for
correctness, so the metadata fields are buying nothing except cheap
short-circuit *invalidation*. Worth revisiting with a measurement of how often
churn actually fires.
