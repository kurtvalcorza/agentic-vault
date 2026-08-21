# 0003 — Content-based rebuild fingerprint

**Status:** Accepted

## Context

`RuntimeIndex.build()` should not redo work when nothing changed. The cheap way
to detect "nothing changed" is file metadata — mtime and size — which is what
most build tools use.

Metadata lies more often than is comfortable: sync clients rewrite mtimes,
editors preserve them, git checkouts set them to checkout time, and mtime
granularity can miss same-second edits.

## Decision

The fingerprint hashes file **content**, not metadata.

## Consequences

- A stale index cannot be served because a timestamp was wrong. This is the
  whole point.
- **Computing the fingerprint costs about as much as the scan it might skip.**
  A no-op rebuild is only marginally cheaper than a cold one — measured at
  roughly 2% on 400 notes (`test_noop_rebuild_short_circuits`). The
  short-circuit skips the *write* half of the build, not the *read* half.
- Anyone benchmarking "cached rebuild" will find a much smaller saving than the
  word "cached" implies. That is expected, and is why the test asserts "no
  worse" rather than a speedup.

## Alternatives considered

**Metadata-only fingerprint (mtime + size).** Would make no-op rebuilds
near-free, and was proposed in issue #9. Rejected: it converts a performance
question into a correctness one. Serving a stale graph is a worse failure than a
slow rebuild, and it fails silently — the caller gets confident wrong answers.
`runtime_index.py` carries an inline comment saying so.

**Hybrid — metadata first, content only on mismatch.** Rejected for now: it
inherits the metadata failure mode for the "unchanged" verdict, which is the
verdict that matters. Revisit only with a benchmark showing scan cost is a real
problem at realistic vault sizes.
