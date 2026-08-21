# 0004 — Minimal runtime dependencies

**Status:** Accepted

## Context

The runtime installs into a vault owned by someone who is not necessarily a
Python developer, on whatever interpreter is to hand, on Windows as often as
Linux. Every dependency is something that can fail to build, conflict, or need
rotating.

The README states the baseline plainly: *"needs no LLM, API key, embeddings,
graph server, or remote service."*

## Decision

Baseline dependencies are `PyYAML` and `mcp` only. Everything else is an
optional extra (`[test]`, `[linkml]`) or lives behind an adapter protocol.
Anything requiring compilation needs a measured justification.

## Consequences

- `pip install -e .` works on a bare interpreter without a toolchain. This is
  what makes the runtime genuinely optional rather than a project to set up.
- Some things are slower than a compiled alternative would be — accepted until
  measured otherwise.
- Optional capabilities (semantic enrichment, vector retrieval) are adapters
  returning candidates. They never become canonical storage, so a missing
  optional dependency degrades a feature rather than breaking the vault.

## Alternatives considered

**`orjson` in place of stdlib `json`** (proposed in issue #9, "3-10x faster
serialization"). Rejected: no benchmark showed serialization was hot, and it is a
compiled wheel — a new failure mode on every platform, for a speedup on a path
nobody had measured. `tests/test_performance.py` now records where time actually
goes; revisit with numbers, not with a benchmark from the library's README.

**Vendoring dependencies.** Rejected: trades install friction for update and
security friction, and hides what is actually being run.
