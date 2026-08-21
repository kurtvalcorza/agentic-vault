# Schema migrations

Knowledge schemas are versioned. Migrations are explicit, ordered, testable transforms of canonical Markdown; they are never implicit database migrations masquerading as source-of-truth changes.

Naming convention:

```text
NNN-short-description.py
```

Each migration should expose:

```python
FROM_VERSION = "0.x"
TO_VERSION = "0.y"
def plan(vault_root): ...   # return proposed file patches, no writes
def apply(vault_root, proposals): ...  # use validated/hash-bound write path
```

Rules:

- migrations are proposal-first;
- preserve stable IDs;
- never silently merge entities;
- preserve/supersede historical claims rather than deleting them where possible;
- support dry-run output;
- include fixtures covering forward migration;
- destructive or ambiguous migrations require explicit user approval.
