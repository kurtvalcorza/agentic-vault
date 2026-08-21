# 0005 — Builds fail closed on parse errors

**Status:** Accepted

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
