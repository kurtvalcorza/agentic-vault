---
description: Defines the bi-temporal `timeline` frontmatter array schema for tracking when facts changed in the real world (event_time) and when the vault recorded those changes (transaction_time). Governs append-only semantics, scope rules, pruning thresholds, and validation expectations for all agents operating on entity-like notes.
---

# Bi-Temporal Fact Tracking Convention

## Purpose

This steering file establishes a convention for tracking the **provenance of belief changes** in the vault. Every factual update to an entity-like note should record two timestamps:

1. **Event time** — when the fact was true in the real world
2. **Transaction time** — when the vault learned about it

This enables the vault owner to answer questions like *"What did I believe about X on date Y?"* and *"When did I first learn that X changed?"*

## Timeline Frontmatter Schema

Each entry in the `timeline` frontmatter array follows this structure:

```yaml
timeline:
  - event_time: "YYYY-MM-DD"       # ISO 8601 date — when the fact was true in the real world
    transaction_time: "YYYY-MM-DD"  # ISO 8601 date — when the vault recorded this change
    claim: "Factual assertion"      # Non-empty string describing what changed
    source: "[[Evidence Note]]"     # WikiLink or relative path to evidence
```

### Field Constraints

| Field | Type | Required | Constraint |
|:------|:-----|:---------|:-----------|
| `event_time` | string | Yes | Valid ISO 8601 date (`YYYY-MM-DD`) |
| `transaction_time` | string | Yes | Valid ISO 8601 date (`YYYY-MM-DD`) |
| `claim` | string | Yes | Non-empty string |
| `source` | string | Yes | WikiLink (`[[Note Name]]`) or relative file path |

## Append-Only Semantics

**Agents MUST append new `timeline` entries. Agents MUST NOT overwrite, edit, or delete existing entries.**

The timeline is an immutable log. When a fact changes, a new entry is appended — the old entry remains as historical record. This preserves the full provenance chain and allows reconstruction of the vault's belief state at any point in time.

## Scope Rules

### Applies To

- Notes in `01_Projects/` and `02_Areas/` that contain **entity-like frontmatter fields**: `role`, `status`, `company`, `affiliation`
- Notes where the agent is **explicitly updating a factual claim** (e.g., changing a person's role, updating a project status, correcting a decision)

### Does NOT Apply To

- `Inbox/` — transient capture notes; facts here are unprocessed and may be incomplete
- `System/templates/` — template files are structural, not factual

### Limitation Acknowledgment

> **Agents cannot reliably distinguish factual content from opinion content programmatically.** The presence of entity-like frontmatter fields (`role`, `status`, `company`, `affiliation`) serves as the primary signal that a note contains trackable facts. Agents should apply bi-temporal tracking when these fields are present or when they are explicitly updating a factual claim. When in doubt, agents should err on the side of tracking — a timeline entry for a non-factual change is harmless, while a missing entry for a factual change loses provenance.

## Examples

### Entity Role Change

A person changes teams:

```yaml
timeline:
  - event_time: "2026-03-15"
    transaction_time: "2026-04-01"
    claim: "the owner moved from Project Atlas team to Project Dawn team"
    source: "[[2026-03-15 Team Announcement]]"
  - event_time: "2025-06-01"
    transaction_time: "2025-06-03"
    claim: "the owner joined Project Atlas team as Project Information Officer"
    source: "[[2025-06-01 Onboarding Notes]]"
```

### Decision Reversal

A project decision is reversed:

```yaml
timeline:
  - event_time: "2026-05-10"
    transaction_time: "2026-05-12"
    claim: "Project Beacon deployment reverted to on-premise model after cloud pilot issues"
    source: "[[2026-05-10 Steering Committee Minutes]]"
  - event_time: "2026-02-01"
    transaction_time: "2026-02-03"
    claim: "Project Beacon approved for cloud-first deployment strategy"
    source: "[[2026-01-30 Architecture Decision Record]]"
```

### Status Update

A project status changes:

```yaml
timeline:
  - event_time: "2026-04-15"
    transaction_time: "2026-04-15"
    claim: "Project Cedar Year 2 funding approved by the funding agency"
    source: "[[2026-04-15 the funding agency Board Resolution]]"
  - event_time: "2026-01-20"
    transaction_time: "2026-01-22"
    claim: "Project Cedar Year 2 proposal submitted to the funding agency"
    source: "[[2026-01-20 Submission Confirmation]]"
```

## Pruning Threshold

**Maximum 20 timeline entries per note.** When a note reaches 20 entries, agents SHALL suggest archiving older entries to a linked note:

- Archive note name: `{Note Name} (Timeline Archive).md`
- Archive note location: same directory as the source note
- The source note retains the most recent 10 entries and adds a WikiLink to the archive: `See [[{Note Name} (Timeline Archive)]] for full history.`
- The archive note contains all entries in chronological order with a WikiLink back to the source note

Agents MUST NOT auto-prune. Pruning requires user confirmation via the Confirmation_Protocol.

## Validation by `reconcile-vault`

The `reconcile-vault` skill validates timeline entry format during its scans. An entry is **malformed** if any of the following are true:

- `event_time` is missing or not a valid ISO 8601 date (`YYYY-MM-DD`)
- `transaction_time` is missing or not a valid ISO 8601 date (`YYYY-MM-DD`)
- `claim` is missing or empty
- `source` is missing
- The entry is not a valid YAML mapping

Malformed entries are reported in the reconciliation summary under the **"Malformed Timeline Entries"** section. The `reconcile-vault` skill does not auto-fix malformed entries — it reports them for user review.
