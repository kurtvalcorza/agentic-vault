# archive-file

Archive files or folders to `04_Archives/` following the vault's taxonomy and policy.

## When to Use

- A project is completed or abandoned and should move to cold storage
- A skill has been deprecated and replaced
- Agent artifacts (outputs, session logs, configs) are from a completed cycle
- Reports belong to a past period and are no longer current
- Any content meets an archiving trigger from the [[archive-policy]]

## How It Works

1. You tell the agent what to archive (file, folder, or pattern)
2. The agent classifies it against the [[archive-taxonomy]]
3. It checks for inbound WikiLinks, unresolved TODOs, and retention rules
4. It presents a move plan for your approval
5. On confirmation: adds archive frontmatter, moves to the correct taxonomy folder, updates `ARCHIVE-INDEX.md`

## Quick Start

```
"Archive the Project Sigma project"
"Move deprecated skills to the archive"
"Archive session logs older than 30 days"
"Archive the October 2025 accomplishment report"
```

## What It Won't Do

- **Delete anything** — archiving is preservation, not deletion
- **Archive active items** — refuses if `status: active` or recent activity detected
- **Create dump folders** — always routes to taxonomy categories, never `Archived-YYYY-MM-DD/`
- **Touch git repos** — `02_Areas/Skills/` and `02_Areas/Tools for Thought/` are off-limits
- **Act without confirmation** — always presents a plan first

## Related

- [[archive-policy]] — Governing policy (triggers, procedures, retention)
- [[archive-taxonomy]] — Folder structure and naming conventions
- [[optimize-workspace]] — Quarterly maintenance (flags stale items for archiving)
- [[universal-triager]] — Triage companion (routes Inbox items; archive-file handles end-of-life)
