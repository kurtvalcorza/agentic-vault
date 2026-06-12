---
name: graduate-idea
description: "Promote an idea fragment into a full project specification with goals, tasks, phases, and linked context. Use when asked to graduate this idea, promote [idea] to project, turn [idea] into a project, or make [idea] a real project."
two_output: true
---

# graduate-idea

Promotes an idea fragment (from `Inbox/`, `#idea` tagged notes, or daily notes) into a structured Project_Spec in `01_Projects/`. Gathers context from linked notes and vault-wide research, generates a complete project specification with goals, phased tasks, open questions, and related note links. Updates the original Idea_Note with graduation status. As a two-output skill, it also proposes WikiLink additions to discovered related notes.

## Trigger Phrases

- "Graduate this idea"
- "Promote [idea] to project"
- "Turn [idea] into a project"
- "Make [idea] a real project"
- "Convert this idea to a project spec"

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| idea | No | — | Title or keyword to search for a specific idea. If omitted, lists recent ideas for selection. |
| days | No | 30 | Lookback window in days for listing recent ideas |

---

## Step 0 — Idea Discovery

### Step 0.1 — Search for Matching Ideas

**If an idea title/keyword argument is provided:**

Search for matching Idea_Notes using case-insensitive substring matching across:

```
**Tool:** file-search
Find all `.md` files in `Inbox/`.
```

```
**Tool:** content-search
Search for notes tagged `#idea` across `01_Projects/`, `02_Areas/`, `03_Resources/`, `Inbox/`.
```

```
**Tool:** content-search
Search recent daily notes in `System/` or the daily notes directory for idea references.
```

A note matches if its title or filename contains the search string (case-insensitive substring match).

### Step 0.2 — Handle Search Results

**If exactly one match is found:** proceed to Step 1 with that note.

**If multiple matches are found:** present a disambiguation prompt:

```
**Tool:** user-interact
"I found multiple ideas matching '{keyword}':

1. [[Idea A]] — {first line or description}
2. [[Idea B]] — {first line or description}
3. [[Idea C]] — {first line or description}

Which idea would you like to graduate? (Enter a number)"
```

Wait for the user to select one before proceeding.

**If no matches are found:**

```
**Tool:** user-interact
"No ideas found matching '{keyword}'. Try a different keyword, or run without
an argument to see recent ideas."
```

Exit gracefully. Log to session log.

### Step 0.3 — List Mode (No Argument)

**If no idea argument is provided:**

Search for all Idea_Notes from the last N days (default 30, configurable via `days` argument):

```
**Tool:** file-search
Find all `.md` files in `Inbox/`.
```

```
**Tool:** content-search
Search for notes tagged `#idea` across the vault.
```

Filter to notes with dates within the last N days (using frontmatter `date` field or file modification time).

**If no recent ideas are found:**

```
**Tool:** user-interact
"No ideas found in the last {N} days. Try increasing the lookback window
(e.g., 'graduate idea days:90') or check if your ideas are tagged with #idea."
```

Exit gracefully. Log to session log.

**If recent ideas are found:** present a selection list:

```
**Tool:** user-interact
"Recent ideas (last {N} days):

1. [[Idea A]] — {date} — {first line}
2. [[Idea B]] — {date} — {first line}
3. [[Idea C]] — {date} — {first line}

Which idea would you like to graduate? (Enter a number)"
```

### Step 0.4 — Already Graduated Check

After selecting an idea, check if it already has `status: graduated` in its frontmatter.

**If already graduated:**

```
**Tool:** user-interact
"[[{Idea Name}]] has already been graduated to a project.
The existing project spec is at [[{Project_Spec link}]].

Would you like to:
  1. Graduate it again (create a new project spec)
  2. Cancel and choose a different idea"
```

If the user chooses to cancel, return to Step 0.3 or exit.

---

## Step 1 — Context Gathering

### Step 1.1 — Read the Idea Note

```
**Tool:** file-read
Read the full content of the selected Idea_Note.
```

Extract:
- Title and description
- All `[[WikiLinks]]` in the note body and frontmatter
- Tags
- Any mentioned people, projects, or concepts

### Step 1.2 — Read Linked Notes

For each WikiLink found in the Idea_Note:

```
**Tool:** file-read
Read each linked note to gather context.
```

Collect relevant context from linked notes: descriptions, statuses, related concepts.

### Step 1.3 — Vault-Wide Research

Search the vault for related content:

```
**Tool:** content-search
Search for overlapping projects in `01_Projects/` — projects with similar scope, goals, or keywords.
```

```
**Tool:** content-search
Search for mentioned people — `[[Person Name]]` references related to the idea's domain.
```

```
**Tool:** content-search
Search for related decisions — notes tagged `#decision` or containing decision-related keywords.
```

```
**Tool:** content-search
Search for similar past ideas — other `#idea` tagged notes with overlapping keywords.
```

Collect all discovered related notes for inclusion in the Project_Spec.

---

## Step 2 — Generate Project_Spec

Using the gathered context, generate a Project_Spec following this data model:

```yaml
---
date: {YYYY-MM-DD}
tags: [project]
status: planning
idea_source: "[[{Original Idea Note}]]"
---

# {Project Name}

## Description
{What this project is and why it matters — synthesized from the idea note and gathered context}

## Goals
1. {Goal 1 — concrete, actionable}
2. {Goal 2}
3. {Goal 3}
...
(up to 5 goals maximum)

## Phases & Tasks
### Phase 1: {Name}
- [ ] Task 1 (priority: high/medium/low)
- [ ] Task 2 (priority: high/medium/low)
...

### Phase 2: {Name}
- [ ] Task 3 (priority: high/medium/low)
- [ ] Task 4 (priority: high/medium/low)
...

## Open Questions
- {Question requiring user input}
- {Unresolved dependency or decision}

## Related Notes
- [[{Related Project}]]
- [[{Related Person}]]
- [[{Related Decision}]]
- [[{Similar Past Idea}]]
```

### Generation Rules

- **Date**: Use today's date in `YYYY-MM-DD` format
- **Tags**: Always include `project` in the tags array
- **Status**: Always set to `planning`
- **Idea source**: WikiLink to the original Idea_Note
- **Goals**: Generate up to 5 concrete, actionable goals based on the idea and context. Fewer is acceptable if the idea is narrow.
- **Phases & Tasks**: Break work into logical phases. Each task should have a priority (high/medium/low). Phases should be sequential and actionable.
- **Open Questions**: Include genuine unknowns — things the user needs to decide or investigate before proceeding.
- **Related Notes**: Include WikiLinks to all related notes discovered during vault research (overlapping projects, mentioned people, related decisions, similar past ideas).

---

## Step 3 — Confirmation Protocol

Present the full Project_Spec to the user for review before writing any files:

```
**Tool:** user-interact
"Here's the generated Project_Spec for **{Project Name}**:

{Full Project_Spec content}

---

This will be saved to `01_Projects/{Project Name}.md`.
The original idea note [[{Idea Name}]] will be updated with `status: graduated`.

Approve / Edit / Cancel?"
```

**If approved:** proceed to Step 4.
**If the user requests edits:** incorporate feedback and re-present.
**If cancelled:** log the cancellation in the session log and exit.

---

## Step 4 — Save Project_Spec

### Step 4.1 — Ensure Target Directory Exists

Check if `01_Projects/` exists. If not, create it:

```
**Tool:** file-write
Create `01_Projects/` directory if missing.
```

### Step 4.2 — Write Project_Spec

```
**Tool:** file-write
Write the approved Project_Spec to `01_Projects/{Project Name}.md`
```

The file is saved at the root level of `01_Projects/`. The user can move it to a sub-folder after review.

---

## Step 5 — Update Idea_Note

After the Project_Spec is saved, update the original Idea_Note.

### Step 5.1 — Read Current Idea_Note

```
**Tool:** file-read
Read the current content of the Idea_Note.
```

### Step 5.2 — Add Graduation Status

**If the Idea_Note has existing frontmatter:**

Add `status: graduated` to the existing frontmatter block. Preserve ALL existing frontmatter fields — do not remove or modify any existing fields.

Add a WikiLink to the new Project_Spec in the note body (e.g., append `\n\n> Graduated to [[{Project Name}]]` at the end).

```
**Tool:** file-edit
Update the Idea_Note frontmatter to add `status: graduated` and append the WikiLink.
```

**If the Idea_Note has NO frontmatter block:**

Create a new frontmatter block at the top of the file:

```
---
status: graduated
---
```

Then append the WikiLink to the Project_Spec in the body.

```
**Tool:** file-edit
Add frontmatter block and append WikiLink.
```

### Frontmatter Preservation Rules

- NEVER remove existing frontmatter fields
- NEVER modify existing frontmatter values
- ONLY add `status: graduated` to the frontmatter
- If `status` already exists with a different value, replace it with `graduated`
- All other fields (`date`, `tags`, `related`, custom fields, etc.) must remain unchanged

---

## Step 6 — Two-Output: Propose WikiLink Additions

As a `two_output: true` skill, after the primary output, propose secondary updates to discovered related notes.

### Step 6.1 — Identify Proposed Updates

For each related note discovered during vault research (Step 1.3), propose adding a WikiLink to the new Project_Spec:

- **Overlapping projects**: Add `[[{New Project Name}]]` to their `related` frontmatter array
- **Mentioned people**: Add `[[{New Project Name}]]` to their `related` frontmatter array
- **Related decisions**: Add `[[{New Project Name}]]` to their body text
- **Similar past ideas**: Add `[[{New Project Name}]]` to their `related` frontmatter array

Proposed additions are limited to:
- Adding entries to the `related` or `concepts` frontmatter arrays
- Appending WikiLinks to note body text

Per the Two-Output Rule, secondary outputs MUST NOT:
- Create new notes
- Delete existing content
- Modify frontmatter fields other than `related` and `concepts`

### Step 6.2 — Present Secondary Proposals

```
**Tool:** user-interact
"## Secondary Updates (Two-Output Rule)

Based on the vault research for this graduation, I'd like to propose these
WikiLink additions to strengthen cross-references:

### [[{Related Project}]]
- Add `[[{New Project Name}]]` to `related` frontmatter array

### [[{Mentioned Person}]]
- Add `[[{New Project Name}]]` to `related` frontmatter array

### [[{Related Decision}]]
- Add `[[{New Project Name}]]` to body text

Approve all / Select by number / Reject all?"
```

Support partial approval.

### Step 6.3 — Apply Approved Secondary Updates

For each approved update:

```
**Tool:** file-read
Read the target note.
```

```
**Tool:** file-edit
Apply the approved WikiLink addition (to `related` array or body text).
```

Preserve all existing frontmatter fields when modifying the `related` array.

---

## Step 7 — Session Log

Log the graduation activity to `System/session-logs/{YYYY-MM-DD}/`:

- Skill invoked: `graduate-idea`
- Idea: `[[{Idea Name}]]`
- Project_Spec created: `[[{Project Name}]]` at `01_Projects/{Project Name}.md`
- Context gathered: `{count}` linked notes read, `{count}` related notes found
- Related notes discovered: overlapping projects, mentioned people, related decisions, similar ideas
- Two-output proposals: `{count}` proposed, `{count}` approved
- Outcome: graduated / cancelled / already graduated

If the session log directory does not exist, create `System/session-logs/{YYYY-MM-DD}/` first.

---

## Required Capabilities

| Capability | Usage |
|:-----------|:------|
| `file-read` | Read Idea_Note, linked notes, related notes, current frontmatter |
| `file-search` | Find `.md` files in `Inbox/`, `01_Projects/`, daily notes directories |
| `content-search` | Search for `#idea` tags, overlapping projects, people, decisions, similar ideas |
| `file-write` | Save Project_Spec to `01_Projects/`, create directories if missing |
| `file-edit` | Update Idea_Note frontmatter with graduation status, apply secondary WikiLink updates |
| `user-interact` | Disambiguation prompts, idea selection, confirmation protocol, two-output approval, already-graduated warning |

### Referenced Policies

| Policy | Path | Purpose |
|:-------|:-----|:--------|
| Two-output rule | `.agent/steering/two-output-rule.md` | Governs secondary output behavior (WikiLink proposals) |
| Skills standard | `.agent/steering/skills-standard.md` | Directory structure and frontmatter requirements |

---

## Error Handling

| Scenario | Action |
|:---------|:-------|
| No recent ideas found (list mode) | Report "no ideas found in the last {N} days", suggest increasing lookback window or checking `#idea` tags |
| No matches for keyword search | Report "no ideas found matching '{keyword}'", suggest alternatives |
| Multiple matches for keyword | Present disambiguation prompt via `user-interact`, wait for selection |
| Already graduated idea | Warn user, show existing Project_Spec link, offer to re-graduate or cancel |
| Idea_Note has no frontmatter block | Create a new frontmatter block with `status: graduated` at the top of the file |
| Missing `01_Projects/` directory | Create the directory before writing the Project_Spec |
| File read failure (permissions, encoding) | Log warning, skip the file, continue with available context |
| Malformed YAML frontmatter in Idea_Note | Log warning, attempt to add frontmatter block above existing content |
| WikiLink target does not exist | Include the WikiLink anyway (Obsidian shows broken links natively) |
| Session log directory missing | Create `System/session-logs/{YYYY-MM-DD}/` directory, then log |
| User cancels at confirmation | Log cancellation in Session_Log, exit without writing any files |

---

## Examples

### Successful Graduation

**User:** Graduate the Project Beacon marketplace idea.

**Agent:**
1. Searching for ideas matching "Project Beacon marketplace"...
   Found: [[Project Beacon Marketplace Concept]] in `Inbox/`

2. Gathering context...
   - Read [[Project Beacon Marketplace Concept]] + 4 linked notes
   - Found 3 overlapping projects, 2 mentioned people, 1 related decision

3. Generated Project_Spec:

```yaml
---
date: 2026-04-05
tags: [project]
status: planning
idea_source: "[[Project Beacon Marketplace Concept]]"
---

# Project Beacon AI Model Marketplace

## Description
A marketplace extension for the Project Beacon platform enabling researchers to publish,
discover, and deploy AI models with quality verification and usage tracking.

## Goals
1. Design marketplace API for model publishing and discovery
2. Implement model quality verification pipeline
3. Build researcher-facing submission portal
4. Integrate with existing Project Beacon model store
5. Establish usage tracking and impact metrics

## Phases & Tasks
### Phase 1: Research & Design
- [ ] Survey existing AI model marketplaces (priority: high)
- [ ] Define marketplace data model (priority: high)
- [ ] Design API specification (priority: medium)

### Phase 2: Core Implementation
- [ ] Build model submission pipeline (priority: high)
- [ ] Implement quality verification checks (priority: high)
- [ ] Create discovery and search interface (priority: medium)

### Phase 3: Integration & Launch
- [ ] Integrate with Project Beacon platform (priority: high)
- [ ] Deploy usage tracking (priority: medium)
- [ ] Conduct beta testing with select researchers (priority: medium)

## Open Questions
- What quality metrics should be required for model submission?
- Should the marketplace support paid models or be free-only?
- How does this interact with COARE access requirements?

## Related Notes
- [[Project Beacon]]
- [[Project Atlas Overview]]
- [[the vault owner]]
- [[AIaaS Strategy Decision]]
- [[AI Model Quality Framework Idea]]
```

This will be saved to `01_Projects/Project Beacon AI Model Marketplace.md`.
The original idea note [[Project Beacon Marketplace Concept]] will be updated with `status: graduated`.

Approve / Edit / Cancel?

**User:** Approve

**Agent:** ✓ Saved `01_Projects/Project Beacon AI Model Marketplace.md`
✓ Updated [[Project Beacon Marketplace Concept]] with `status: graduated`

## Secondary Updates (Two-Output Rule)

### [[Project Beacon]]
- Add `[[Project Beacon AI Model Marketplace]]` to `related` frontmatter array

### [[Project Atlas Overview]]
- Add `[[Project Beacon AI Model Marketplace]]` to `related` frontmatter array

### [[AIaaS Strategy Decision]]
- Add `[[Project Beacon AI Model Marketplace]]` to body text

Approve all / Select by number / Reject all?

### No Recent Ideas

**User:** Graduate idea

**Agent:** No ideas found in the last 30 days. Try increasing the lookback window (e.g., "graduate idea days:90") or check if your ideas are tagged with #idea.

### Multiple Matches

**User:** Graduate the AI idea.

**Agent:** I found multiple ideas matching "AI":

1. [[AI Ethics Framework Idea]] — 2026-03-28 — Framework for evaluating AI ethics in Example Org projects
2. [[AI Model Marketplace Concept]] — 2026-03-15 — Marketplace extension for Project Beacon
3. [[AI Training Pipeline Idea]] — 2026-04-01 — Automated training pipeline for iHubs

Which idea would you like to graduate? (Enter a number)
