---
id: concept:zettelkasten
type: Concept
title: Example Topic
status: active
created: 2026-06-12
tags: [area/example, status/active]
relations:
  - predicate: supported_by
    target: source:how-to-take-smart-notes
    derivation: asserted
    status: accepted
    evidence:
      - source: source:how-to-take-smart-notes
        locator:
          type: heading
          value: How to Take Smart Notes
claims:
  - id: claim:linking-beats-collecting
    predicate: supported_by
    object: source:how-to-take-smart-notes
    derivation: inferred
    status: proposed
    claim_confidence: 0.6
    evidence:
      - source: source:how-to-take-smart-notes
        locator:
          type: heading
          value: How to Take Smart Notes
timeline:
  - event_time: "2026-06-12"
    transaction_time: "2026-06-12"
    claim: "Example Topic area created to demonstrate bi-temporal fact tracking"
    source: "[[AGENTS.md]]"
---

# Example Topic

> Seed example — an area note demonstrating **bi-temporal tracking**: the `timeline` array in frontmatter records *when a fact was true* (`event_time`) vs *when the vault learned it* (`transaction_time`). It is append-only — agents add entries when entity facts (`role`, `status`, `company`, `affiliation`) change, never edit old ones. See `.agent/steering/bi-temporal-tracking.md`.
>
> It is also the hub of the **semantic seed**. `id` + `type` promote a note from a filed document to a typed knowledge object; without both, the runtime indexes it for navigation only. Note the two different kinds of edge:
>
> - `relations:` — **asserted** and `accepted`. A human wrote it down. Canonical.
> - `claims:` — **inferred** and `proposed`. Something derived this; nothing has confirmed it. It stays a candidate until a person accepts it, which is why `knowledge.health` reports accepted and candidate claims separately.
>
> That distinction is the whole point of the runtime: a confident guess never silently becomes canonical knowledge.

An **Area** is a long-term commitment with no end date — a discipline you maintain rather than a deliverable you finish. Notes here follow Zettelkasten principles: one idea per note, densely linked.

## Related

- [[02_Areas/AREA-INDEX]]
- [[01_Projects/Sample Project/Sample Project]]
- [[03_Resources/Reading-List/How to Take Smart Notes]]
