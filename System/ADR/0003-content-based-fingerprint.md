# 0003 — Content-based rebuild fingerprint

**Status:** Accepted
**Related:** [[0001-markdown-is-canonical]] · [[0002-sqlite-for-the-projection]] · [[0005-builds-fail-closed]] · [[AGENTS.md]]

## Context

`RuntimeIndex.refresh()` should not redo work when nothing changed. The cheap way
to detect "nothing changed" is file metadata — mtime and size — which is what
most build tools use.

Metadata lies more often than is comfortable: sync clients rewrite mtimes,
editors preserve them, git checkouts set them to checkout time, and mtime
granularity can miss a same-second edit.

## Decision

The fingerprint hashes file **content**, not metadata. The short-circuit lives in
`refresh()`; `build()` always does the full work and is the right call when you
want an unconditional rebuild.

## Consequences

- A stale index cannot be served because a timestamp was wrong. That is the point.
- The warm path still reads and hashes every file, so the saving is bounded by
  I/O rather than being near-zero-cost. Measured on 400 synthetic notes
  (`test_refresh_short_circuits_on_unchanged_vault`): **2196 ms cold, 264 ms warm
  — about 88% saved.** The short-circuit skips parse, validate and write; it does
  not skip the read.
- That ratio will fall as notes get larger, since hashing cost grows with content
  while the skipped work grows with structure. Re-measure before assuming it holds
  at a different vault shape.
- Calling `build()` twice does **not** exercise this and will show no saving —
  a mistake made once already while writing these benchmarks.

## Alternatives considered

**Metadata-only fingerprint (mtime + size).** Would make the warm path nearly
free, and was proposed in issue #9. Rejected: it converts a performance question
into a correctness one. Serving a stale graph is a worse failure than a slower
refresh, and it fails silently — the caller gets confident wrong answers.
`runtime_index.py` carries an inline comment saying so.

**Hybrid — metadata first, content only on mismatch.** Rejected for now: it
inherits the metadata failure mode for the "unchanged" verdict, which is the
verdict that matters. With 88% already saved, the remaining headroom does not
justify the risk.
