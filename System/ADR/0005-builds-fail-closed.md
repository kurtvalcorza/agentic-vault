# 0005 — Builds fail closed on parse errors

**Status:** Accepted
**Related:** [[0001-markdown-is-canonical]] · [[0003-content-based-fingerprint]] · [[0006-writes-off-by-default-everywhere]] · [[AGENTS.md]]

## Context

Real vaults contain files that are not notes: skill templates with `{{title}}`
placeholders, slash-command definitions with `argument-hint: [a: b]`, archived
scaffolding. As YAML frontmatter these are errors — an unhashable dict, a
malformed flow sequence.

The build must decide what to do when it meets one: skip it, or stop.

## Decision

Stop. A parse error anywhere fails the whole build and the index is not updated.

## Consequences

- The index is never quietly partial. A query cannot return "no results" because
  a file failed to parse three days ago and nobody noticed.
- **Incremental builds are all-or-nothing, but only because of which class
  implements them.** `RuntimeIndex.build` resolves to
  `ExtendedKnowledgeIndex.build` (`advanced.py`), which scans and validates the
  entire vault first and returns *before any database write* if any issue has
  severity `error`. Verified by
  `test_failed_incremental_build_leaves_projection_untouched`: a simultaneous
  edit, deletion and unparseable file leave the projection byte-identical, still
  so after reopening the database.

  The base `KnowledgeIndex.build` in `core.py` behaves differently — it upserts
  as it iterates, removes stale rows, and calls `commit()` unconditionally, so a
  parse error there *would* leave a partially updated projection. It is not on
  the path any entry point takes (`cli.py` and `mcp_server.py` construct
  `RuntimeIndex` only), but reading `core.py` and assuming it is the shipped
  behaviour is an easy and repeated mistake. Check the MRO before concluding
  anything about build atomicity.
- **`build --full` is the genuine exception, and it is not currently safe.**
  `RuntimeIndex.rebuild()` closes the connection and `unlink()`s the database
  *before* validation runs, so a full rebuild that then hits a parse error leaves
  no index at all — the previous valid projection is already gone.
  This is availability loss, not data loss: Markdown remains canonical
  ([[0001-markdown-is-canonical]]) and the projection is reconstructible once the
  offending file is fixed. But "a failed build leaves the previous index intact"
  is **false for `--full`**, and the CI workflow uses `--full`.
  Fixing it means building into a temporary database and swapping on success;
  that is a behaviour change and belongs in its own change, not in the record
  that documents the current state.
- **Scan scope becomes a correctness concern**, not a performance one. This is
  why dot-directories are excluded by rule and why `.knowledge-ignore` exists
  for non-dot scaffolding trees.
- First contact with an existing vault is often a wall of errors. Porting into
  one real vault produced 22, of which 19 were agent-config and archived
  scaffolding — files that were never knowledge. That experience is what drove
  the dot-directory exclusion.
- The remedy is always to fix or exclude the file, never to loosen the build.

## Alternatives considered

**Skip unparseable files with a warning.** Friendlier first run. Rejected: it
makes the failure silent and permanent. Warnings scroll past; a missing note in
a query result does not announce itself. Fail-closed converts a silent wrong
answer into a loud, fixable error.

**Fail closed only for files with an `id`.** Rejected: a file's frontmatter must
parse before you can know whether it has an `id`, so the check is circular.
