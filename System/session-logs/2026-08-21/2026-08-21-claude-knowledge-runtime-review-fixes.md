---
agent: claude
date: 2026-08-21
status: completed
scope: knowledge-runtime
---

# 2026-08-21 - Claude Session Log

## Goal
Address the second review pass on PR #3 (Codex, against head `99b2e3e`) for the agent-agnostic knowledge runtime, without regressing earlier fixes or the architecture invariants.

## Key Actions (correctness / safety fixes)
- Rejected silent semantic demotion and stable-ID changes on ordinary patches; require explicit migrate/merge operations.
- Re-checked the source content hash *after* full-vault candidate validation to close a TOCTOU write race.
- Validated the combined final state of multi-file batches (cross-proposal domain/range), not just each proposal in isolation.
- Enabled `create` proposals (`propose_entity`) to be applied atomically through `apply_patch`/`apply_batch`.
- Validated claim domains against each claim's declared `subject`, not the containing note's type.
- Preserved canonical relation validity fields (`valid_from`/`valid_to`/`recorded_at`) in the SQLite projection, with a disposable-DB migration.
- Hardened the OKF exporter: refuse protected destinations (`.agent`, `.git`, config/workspace dirs, vault root/ancestors) and require an exporter-owned ownership manifest before replacing any directory.
- Made the cached SQLite connection safe under the MCP worker-thread model (`check_same_thread=False`, access serialized by the existing lock).
- Deduplicated claim-derived contradiction candidates.
- Accepted the schema-declared `imported` relation derivation.
- Rejected unknown object lifecycle statuses.
- Required explicit stable claim IDs (list-position IDs are unstable across edits).
- Excluded accepted-but-inferred edges from default graph traversal (`trace`, `impact`, `communities`, `central`), with an `include_derived` opt-in.
- Recognized a closing frontmatter delimiter at end of file.
- Added regression tests for every distinct finding above.

## Safety / Provenance
Changes are generic, synthetic, and agent-agnostic. Markdown/YAML remains authoritative; derived SQLite/FTS projections and OKF bundles remain disposable. No private vault content, credentials, or domain-specific ontology introduced. No coupling to any specific agent (Claude/Codex/Gemini/Kiro).

## Status
Review fixes implemented on `feat/knowledge-runtime-rfc-2`; PR #3 remains the review surface. Full local pytest (excluding the LinkML-dependency test, which CI runs) is green; `validate` / `build --full` / `health` on the public vault report zero issues.
