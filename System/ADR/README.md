# Architecture Decision Records

Short records of decisions that are **load-bearing and non-obvious** — the ones
where the reasoning lives in someone's head or a code comment, and where a later
reader could reasonably propose the opposite.

## Why these exist

Issue #9 proposed replacing stdlib `json` with `orjson` against this project's
stated no-compiled-dependencies baseline, and swapping the content-based
fingerprint for a metadata-only one that `runtime_index.py` documents as unsafe.
Neither proposal was unreasonable on its face. Both were easy to make precisely
because the reasoning was invisible.

An ADR is cheaper than re-litigating a decision, and much cheaper than
implementing its reversal.

## What earns one

A decision earns an ADR when **all three** hold:

1. A competent reader could propose the opposite in good faith.
2. Reversing it would be expensive, or would quietly break something.
3. The reason is not obvious from the code.

Formatting conventions, library choices with no tradeoff, and anything already
explained by its own docstring do not need one.

## Format

Numbered `NNNN-kebab-title.md`, newest number wins. Each states **Context**,
**Decision**, **Consequences** (including the costs accepted), and
**Alternatives considered** — the last is the section that does the work, since
it is what a future proposal will be re-deriving.

Status is `Accepted`, `Superseded by NNNN`, or `Deprecated`. Records are
append-only: supersede, never rewrite. The record of a decision that was later
reversed is more useful than no record.

## Index

| ADR | Title | Status |
|:---|:---|:---|
| [0001](0001-markdown-is-canonical.md) | Markdown/YAML is canonical; projections are disposable | Accepted |
| [0002](0002-sqlite-for-the-projection.md) | SQLite/FTS for the derived projection | Accepted |
| [0003](0003-content-based-fingerprint.md) | Content-based rebuild fingerprint | Accepted |
| [0004](0004-stdlib-only-runtime-dependencies.md) | Minimal runtime dependencies | Accepted |
| [0005](0005-builds-fail-closed.md) | Builds fail closed on parse errors | Accepted |
| [0006](0006-writes-off-by-default-everywhere.md) | Canonical writes off by default on every entry point | Accepted |
