---
description: "Running log of vault stack audits — the cadence reference point. Append one row per audit. Checked on/after quarter boundaries per AGENTS.md (Audit Cadence)."
tags: [reference/audit-log]
---

# Audit Log

The source-of-truth history for vault stack audits. **Cadence: quarterly.** On or
after each quarter boundary (Mar 1 / Jun 1 / Sep 1 / Dec 1), an agent checks this
file; if the current quarter has no entry, it prompts to run `optimize-workspace`.
After each audit, append a row to the table and a short detail block below.

> **Pruning is human-gated.** The audit *surfaces* dead weight and *proposes*
> cuts; you approve before anything is removed. The local git history is the undo.

| Date | Quarter | Scope reviewed | What changed | Next due |
|------|---------|----------------|--------------|----------|
| _YYYY-MM-DD_ | _Qn YYYY_ | _e.g. skills, steering, connectors_ | _what was pruned/updated, or "no changes"_ | _next quarter boundary_ |

## Audit detail

> Append one block per audit, newest first — for example:
>
> ### YYYY-MM-DD — Qn YYYY
> Full `optimize-workspace` audit. Reports in `.agent/outputs/YYYY-MM-DD_Workspace-Optimization/`.
> - Health score + one-line state
> - Key findings (redundancies, orphans, stale context)
> - Prune decision (human-gated)
