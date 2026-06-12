---
description: "Defines the Two-Output Rule convention where skills tagged with `two_output: true` in their SKILL.md frontmatter propose vault page updates as a secondary output alongside their primary response. Governs opt-in mechanism, substantive insight criteria, secondary output constraints, and logging requirements."
---

# Two-Output Rule Convention

## Purpose

This steering file establishes a convention for **passive vault enrichment**. When a skill produces a substantive insight during its primary task, it should also propose updates to relevant existing vault notes as a secondary output — so the vault accumulates knowledge without requiring explicit update commands.

The Two-Output Rule is **opt-in per skill**. Only skills that explicitly declare participation will produce secondary outputs.

## Opt-In Mechanism

Skills opt in by adding `two_output: true` to their SKILL.md YAML frontmatter:

```yaml
---
name: skill-name
description: "What the skill does and when to use it"
two_output: true
---
```

When an agent loads a skill with `two_output: true`, it activates the Two-Output Rule for that skill's execution. Skills without this field (or with `two_output: false`) produce only their primary output.

### Default Opt-In Skills

The following skills opt in by default and MUST have `two_output: true` in their SKILL.md frontmatter:

| Skill | Rationale |
|:------|:----------|
| `connect-domains` | Bridge-finding between topics naturally surfaces cross-references worth adding to source notes |
| `graduate-idea` | Idea research discovers related projects and people that benefit from backlinks |
| `extract-concepts` | Concept extraction identifies connections and relationships that enrich existing notes |

### Excluded Skills

| Skill | Reason for Exclusion |
|:------|:---------------------|
| `reconcile-vault` | Its primary function already proposes vault modifications (contradiction resolution, history entries, conflict notes). Adding a secondary output layer would be redundant and confusing. |

### Adding New Skills

Any skill may opt in to the Two-Output Rule by adding `two_output: true` to its SKILL.md frontmatter. No changes to this steering file are required — the frontmatter field is the sole mechanism.

## Substantive Insight Criteria

A secondary output is triggered only when the skill's primary execution produces a **substantive insight**. Not every skill invocation warrants vault updates — the insight must meet at least one of these criteria:

1. **New factual claim** — a previously unrecorded fact about an entity, project, or concept (e.g., discovering that a person changed roles, or that a project adopted a new technology)
2. **Connection between unlinked concepts** — identifying a relationship between two notes or concepts that are not currently connected by WikiLinks (e.g., realizing that two projects share a common dependency)
3. **Correction or update** — information that supersedes, corrects, or refines what an existing note currently states (e.g., an outdated status, a revised date, a clarified definition)
4. **Synthesis adding context** — a summary, interpretation, or contextual framing that enriches an existing note beyond what it currently contains (e.g., adding a paragraph that explains how a concept relates to a broader theme)

If the skill's primary output does not produce any insight meeting these criteria, no secondary output is generated. The agent should not force secondary outputs when none are warranted.

## Secondary Output Constraints

Secondary outputs are **conservative by design**. They enrich existing notes without disrupting vault structure.

### Permitted Actions

| Action | Scope |
|:-------|:------|
| **Append body content** | Add paragraphs, bullet points, or sections to the end of an existing note's body |
| **Add WikiLinks** | Insert `[[WikiLinks]]` into existing note body text or into permitted frontmatter arrays |
| **Modify `related` frontmatter array** | Add entries to the `related` array field in YAML frontmatter |
| **Modify `concepts` frontmatter array** | Add entries to the `concepts` array field in YAML frontmatter |

### Prohibited Actions

| Action | Reason |
|:-------|:-------|
| **Create new notes** | Secondary outputs enrich existing notes only; new note creation is a primary output concern |
| **Delete content** | No removal of existing body text, sections, WikiLinks, or frontmatter fields |
| **Modify other frontmatter fields** | Only `related` and `concepts` arrays may be touched; all other fields (including `tags`, `status`, `date`, etc.) are off-limits |
| **Rename or move notes** | Structural changes are outside the scope of secondary outputs |

## Confirmation Protocol Requirement

**All proposed secondary updates require user confirmation via the Confirmation_Protocol before being applied.**

The agent MUST:

1. Present the proposed secondary updates clearly, separate from the primary output
2. Show which notes would be modified and what changes would be made (diff-style for edits, full preview for additions)
3. Wait for explicit user approval before writing any changes
4. Support partial approval — the user may approve some proposed updates and reject others

No secondary output may be written to the vault without the user's explicit confirmation.

## Session Log Requirement

**All proposed secondary updates MUST be logged to the current Session_Log regardless of whether the user approves them.**

The session log entry for a Two-Output Rule proposal should include:

- The skill that generated the proposal
- Which notes were proposed for update
- What changes were proposed
- Whether the user approved, partially approved, or rejected the proposals

This ensures a complete audit trail of vault enrichment proposals, even when the user declines them. Rejected proposals may still be valuable for understanding what the agent considered noteworthy.
