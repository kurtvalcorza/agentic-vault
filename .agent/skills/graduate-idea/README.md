---
name: graduate-idea
description: "Promote an idea fragment into a full project specification with goals, tasks, phases, and linked context. Use when asked to graduate this idea, promote [idea] to project, turn [idea] into a project, or make [idea] a real project."
---

# graduate-idea

Promotes idea fragments into structured project specifications. Searches your vault for matching ideas, gathers context from linked notes and related content, and generates a complete Project_Spec with goals, phased tasks, open questions, and cross-references. The original idea note is updated with graduation status, and related notes are offered WikiLink additions via the Two-Output Rule.

## When to Use

- You have an idea in `Inbox/` or tagged `#idea` that you want to develop into a real project
- You want to turn a rough concept into an actionable project specification with goals and tasks
- You want the vault's existing knowledge to inform and enrich a new project plan
- You want to automatically link a new project to related notes, people, and decisions

## Invocation

### With a Specific Idea

```
Graduate the Project Beacon marketplace idea
Promote "AI Ethics Framework" to project
Turn the training pipeline idea into a project
```

Provide a keyword or title fragment. The skill searches `Inbox/`, `#idea` tagged notes, and recent daily notes using case-insensitive substring matching.

### Without an Argument (Browse Mode)

```
Graduate idea
```

Lists all ideas from the last 30 days and prompts you to select one.

### With Custom Lookback Window

```
Graduate idea days:90
```

Lists ideas from the last 90 days instead of the default 30.

## What Happens

1. The skill searches your vault for matching idea notes
2. If multiple matches are found, you choose which one to graduate
3. It reads the idea note and all linked notes for context
4. It searches the vault for overlapping projects, mentioned people, related decisions, and similar past ideas
5. It generates a Project_Spec with description, goals, phased tasks, open questions, and related note links
6. You review and approve the spec (Confirmation Protocol)
7. The spec is saved to `01_Projects/` and the original idea is marked as graduated
8. The skill proposes WikiLink additions to related notes (Two-Output Rule)

## Project_Spec Structure

The generated project specification follows this structure:

```yaml
---
date: YYYY-MM-DD
tags: [project]
status: planning
idea_source: "[[Original Idea Note]]"
---

# {Project Name}

## Description
{What this project is and why it matters}

## Goals
1. {Goal 1}
2. {Goal 2}
...
(up to 5 goals)

## Phases & Tasks
### Phase 1: {Name}
- [ ] Task 1 (priority: high/medium/low)
- [ ] Task 2 (priority: high/medium/low)

### Phase 2: {Name}
- [ ] Task 3 (priority: high/medium/low)
...

## Open Questions
- {Question requiring user input}

## Related Notes
- [[Related Project]]
- [[Related Person]]
- [[Related Decision]]
```

### Key Fields

- **date**: Today's date
- **tags**: Always includes `project`
- **status**: Always `planning` (you can change it later)
- **idea_source**: WikiLink back to the original idea note for traceability
- **Goals**: Up to 5 concrete, actionable goals
- **Phases & Tasks**: Work broken into sequential phases with prioritized tasks
- **Open Questions**: Genuine unknowns that need your input
- **Related Notes**: All related content discovered during vault research

## Output Locations

| Output | Location |
|:-------|:---------|
| Project_Spec | `01_Projects/{Project Name}.md` (root level) |
| Idea_Note update | Original idea note (frontmatter + body) |
| Secondary WikiLink updates | Various related notes (with approval) |
| Session log | `System/session-logs/YYYY-MM-DD/` |

## Idea_Note Update

After graduation, the original idea note is updated:

- **Frontmatter**: `status: graduated` is added (all existing fields preserved)
- **Body**: A WikiLink to the new Project_Spec is appended
- **No frontmatter**: If the idea note has no frontmatter block, one is created with `status: graduated`

## Secondary Updates (Two-Output Rule)

After saving the Project_Spec, the skill proposes WikiLink additions to related notes discovered during vault research:

- Overlapping projects get `[[New Project]]` in their `related` array
- Mentioned people get `[[New Project]]` in their `related` array
- Related decisions get `[[New Project]]` appended to body text

All secondary updates require your explicit approval. You can approve all, select specific updates, or reject all.

## Error Handling

| Scenario | Behavior |
|:---------|:---------|
| No recent ideas found | Reports the gap and suggests increasing the lookback window |
| No matches for keyword | Reports no matches and suggests alternatives |
| Multiple matches | Presents a disambiguation list for you to choose from |
| Already graduated idea | Warns you and shows the existing project link; offers to re-graduate or cancel |
| Idea has no frontmatter | Creates a new frontmatter block with `status: graduated` |
| Missing `01_Projects/` | Creates the directory automatically |
| User cancels | Logs the cancellation and exits without changes |

## Prerequisites

| Dependency | Path | Purpose |
|:-----------|:-----|:--------|
| Two-output rule steering | `.agent/steering/two-output-rule.md` | Governs secondary WikiLink proposals |
| Vault content directories | `Inbox/`, `01_Projects/`, `02_Areas/`, `03_Resources/` | Notes to search and link |
| Output directory | `01_Projects/` | Where Project_Specs are saved |
| Session log directory | `System/session-logs/YYYY-MM-DD/` | Activity logging |

## Related Skills

- `connect-domains` — Discovers connections between two topics (use to find bridges before graduating)
- `reconcile-vault` — Detects contradictions across vault notes (use to check consistency of related content)
- `visualize-vault` — Generates a visual map of vault link structure (use to see how the new project connects)
- `extract-concepts` — Discovers recurring concepts (complementary for identifying themes in the idea's domain)
- `query-vault` — Q&A against vault content (use to investigate specific aspects of the idea before graduating)
