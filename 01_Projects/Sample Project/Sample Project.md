---
id: project:sample-project
type: Project
title: Sample Project
status: active
started: 2026-06-12
deadline: 2026-07-01
tags: [project/sample, status/active]
relations:
  - predicate: depends_on
    target: concept:zettelkasten
    derivation: asserted
    status: accepted
timeline:
  - event_time: "2026-06-12"
    transaction_time: "2026-06-12"
    claim: "Sample Project started"
    source: "[[01_Projects/To Do]]"
---

# Sample Project

> Seed example — a minimal project note showing the conventions. Delete once you've made your own.
>
> Its `relations:` edge is what makes `knowledge.trace_path` return something on a fresh clone: this project → `concept:zettelkasten` → `source:how-to-take-smart-notes`. A `[[WikiLink]]` alone would not — links are navigation, `relations:` are typed semantics, and the runtime counts them separately.

**Goal:** Ship one deliverable that demonstrates the vault's project workflow end-to-end.

**Work board card:** see [[01_Projects/To Do]] → `DEV > Sample Project > Ship the first deliverable 📅 2026-07-01`

## Log

- 2026-06-12 — Project created from the template's seed content.

## Related

- [[01_Projects/To Do]]
- [[02_Areas/Example_Area/Example Topic]]
- [[03_Resources/Reading-List/How to Take Smart Notes]]
