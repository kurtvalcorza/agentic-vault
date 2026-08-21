# 0006 — Canonical writes off by default, on every entry point

**Status:** Accepted

## Context

`apply-patch` / `apply-batch` and their MCP equivalents edit canonical Markdown —
the vault's actual notes, per ADR-0001. The vault's git snapshot runs at session
end, so a destroy-and-recreate inside a single session leaves no intermediate
restore point.

The MCP server was gated behind `AGENTIC_VAULT_KNOWLEDGE_READ_ONLY` from the
start. The CLI was not, on the reasoning that a human typing `apply-patch` has
expressed intent in a way an agent calling a tool has not.

## Decision

Every entry point honours the same flag, with the same default (read-only on)
and the same truthiness rules. MCP tools raise; the CLI refuses with exit code 2
and leaves the file untouched.

Only `apply` is gated. `propose` and `validate-*` remain available read-only, so
the whole `propose → validate → apply` flow can be rehearsed against a protected
vault — which is the point of a proposal-first API.

## Consequences

- "Writes are off by default" is true without qualification, which is the only
  form of that sentence anyone will remember correctly.
- Enabling writes is a deliberate act that shows up in a config file or a shell
  session, rather than being the ambient state.
- A human doing legitimate CLI work must set the variable. Accepted: minor
  friction, once, against silent edits to canonical notes.

## Alternatives considered

**Gate MCP only, document the CLI as ungated.** This was the shipped state for
one commit. Rejected on review: a guarantee that holds on one entry point and
not another is worse than no guarantee, because it invites setting the MCP
default and assuming the vault is protected. Nobody reliably carries the
exception in their head.

**A `--force` flag instead of an environment variable.** Rejected: two
mechanisms for one guarantee, and it would diverge from the MCP path. One
variable, honoured identically everywhere, is the property worth having.
