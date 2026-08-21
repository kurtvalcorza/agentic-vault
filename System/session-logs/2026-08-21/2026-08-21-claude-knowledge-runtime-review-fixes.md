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

## Third pass (head f2c8a5e review)
- Batch writes: recheck every source hash and create-target absence after full-vault validation, immediately before the first replacement; abort the whole batch on any mismatch (closes the `apply_batch` TOCTOU the human review flagged as the remaining blocker).
- Semantic-demotion check now applies to `migrate`/`merge` operations too; only the stable-ID comparison is exempted for them.
- Restricted the write API to canonical Markdown outside protected workspaces (`.git`, `.claude`, `.gemini`, `.kiro`, `.codex`, `.obsidian`, generated/scan-excluded dirs).
- Relation contradiction candidates now require overlapping projected validity intervals instead of equal legacy `event_time`.
- `timeline` authored as a mapping/scalar (not a list) now raises `invalid-timeline` instead of being silently dropped.
- Refresh fingerprint now includes a content digest, so a same-length edit with a preserved mtime is no longer skipped.
- CI workflow triggers now include canonical knowledge dirs (`Inbox/`, `01_Projects/`–`04_Archives/`) so note-only PRs still run whole-vault validation.
- Added regression tests for each of the above.

## Fourth pass (head 1b14981 review)
- Populated canonical validity columns (`valid_from`/`valid_to`/`recorded_at`) on claim-derived graph edges (they previously carried only the legacy columns).
- Graph exports (`export-jsonld`/`export-rdf`) refuse to overwrite a Markdown path, preventing accidental note clobbering; RDF export now excludes inferred edges by default.
- OKF export uniquifies reserved-name collisions (`index.md` → `index-concept.md` vs an existing `index-concept.md`) instead of silently overwriting.
- `trace()` now enforces the requested `max_depth` exactly (no off-by-one extra edge).
- `iter_markdown` no longer excludes canonical folders by the generic names `generated`/`export`; only the runtime's own `.agent/knowledge/generated` tree and `.knowledge-ignore`-marked trees are skipped.
- Rejected `knowledge_schema` versions newer than `schema/VERSION` (`unsupported-schema-version`).
- Accepted the schema-declared `merged` relation status.
- Rejected self-links/cycles in the merged-object redirect graph (`redirect-cycle`).
- Validated `source_authority` on `Source` objects against the enum.
- MCP write tools now hold the shared index lock across apply, so no query observes a partial batch.
- Added regression tests for each.

## Status
Review fixes implemented on `feat/knowledge-runtime-rfc-2`; PR #3 remains the review surface. Full local pytest (excluding the LinkML-dependency test, which CI runs) is green; `validate` / `build --full` / `health` on the public vault report zero issues.
