# People Profiles

One markdown file per person agents should know about (collaborators, stakeholders). Use entity frontmatter so bi-temporal tracking applies:

```yaml
---
name: Jane Example
role: Collaborator
affiliation: Example Org
status: active
timeline:
  - event_time: "2026-06-12"
    transaction_time: "2026-06-12"
    claim: "Jane joined the project as collaborator"
    source: "[[Some Evidence Note]]"
---
```

When a person's `role`/`affiliation`/`status` changes, **append** a timeline entry — never rewrite history. See `.agent/steering/bi-temporal-tracking.md`.
