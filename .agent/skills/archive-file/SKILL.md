---
name: archive-file
description: "Archive files or folders to 04_Archives following vault taxonomy and policy. Use when archiving completed projects, deprecated skills, stale agent artifacts, old reports, or any content that has reached end-of-life in the active workspace."
---

# Archive File

## Core Mission

You are the vault's archivist. Your job is to move inactive content from the active workspace into `04_Archives/` following the taxonomy and policy defined in `04_Archives/specs/`. You operate in **Suggestion Mode** by default — propose moves, get confirmation, then execute.

## Dependencies

### Required Reading (Load Before Executing)

1. `04_Archives/specs/archive-policy.md` — Triggers, procedures, metadata standards
2. `04_Archives/specs/archive-taxonomy.md` — Folder structure, naming conventions, mapping rules

### Required Tools
- `file-read` — Read file content and frontmatter
- `file-write` — Update frontmatter on archived items
- `command-exec` — Move files/folders
- `file-search` — Find WikiLinks pointing to the item being archived

## Workflow

### Phase 1: Identify & Classify

1. **Receive target** — User specifies a file, folder, or pattern to archive.
2. **Read the target** — Examine content and frontmatter to understand what it is.
3. **Classify content type** — Determine which taxonomy category applies:

| Content Type | Archive Destination | Reference |
|:---|:---|:---|
| Completed/abandoned project | `04_Archives/_projects/[ProjectName]/` | taxonomy §Proposed Structure |
| Periodic report (AR, weekly, meeting) | `04_Archives/_reports/[type]/[YYYY]/` | taxonomy §Proposed Structure |
| Archived area content | `04_Archives/_areas/[area-name]/` | taxonomy §Proposed Structure |
| Deprecated/superseded skill | `04_Archives/_skills/deprecated/` | taxonomy §Skills |
| Point-in-time skill snapshot | `04_Archives/_skills/[snapshot-name]/` | taxonomy §Skills |
| Agent output/audit/config | `04_Archives/_agent-artifacts/[sub]/` | taxonomy §Agent Artifacts |
| Session logs (>30 days old) | `04_Archives/_agent-artifacts/session-logs/YYYY-MM/` | policy §Session Log Archiving |

4. **Check archiving triggers** — Verify that the item meets at least one trigger from the policy:
   - Project completed/abandoned (no activity >3 months)
   - Content superseded by newer version
   - Content belongs to a past time period
   - Agent artifact from completed cycle
   - Skill deprecated and replaced

### Phase 2: Pre-Archive Checks

5. **Scan for inbound WikiLinks** — Search the vault for `[[Target Name]]` references. Report any active notes that link to the target.
6. **Check for unresolved work** — Look for `TODO`, `FIXME`, `WIP`, or `status: active` in frontmatter. If found, warn the user.
7. **Check retention minimums** — Cross-reference with policy retention table:

| Content Type | Minimum Retention |
|:---|:---|
| Completed Projects | 3 years |
| Accomplishment Reports | 5 years |
| Meeting Notes | 2 years |
| Agent Outputs / Audits | 1 year |
| Deprecated Skills (snapshots) | 6 months after supersession |
| Session Logs | 3 months |
| Personal Records | Indefinite |

### Phase 3: Propose & Confirm

8. **Present archive plan** — Show the user a table:

```markdown
| Item | Current Location | Proposed Destination | Reason | Inbound Links |
|------|-----------------|---------------------|--------|---------------|
| ... | ... | ... | ... | N links |
```

9. **Wait for explicit confirmation** — Do not proceed without user approval.

### Phase 4: Execute Archive

10. **Add archive frontmatter** — Update or add YAML metadata to each file:

```yaml
archived: true
archived_date: YYYY-MM-DD
archived_reason: "[completed | superseded | abandoned | migrated | deprecated]"
source_location: "[original path before archiving]"
```

For **skills**, also add:
```yaml
deprecated: true
deprecated_date: YYYY-MM-DD
replaced_by: "new-skill-name"   # If a replacement exists
```

11. **Move to taxonomy destination** — Move the file or folder to the correct location under `04_Archives/`.

12. **Handle naming conflicts** — If the destination already has a folder with the same name:
    - Compare contents
    - If identical → skip the move, report duplicate
    - If different → merge contents into existing folder
    - Never create `Folder 1` duplicates

13. **(Optional) Leave a stub** — For high-traffic items with many inbound links, create a one-line stub at the original location:

```markdown
---
archived: true
redirect: "[[04_Archives/_projects/ProjectName/original-file]]"
---
This file has been archived. See [[04_Archives/_projects/ProjectName/original-file]].
```

### Phase 5: Update Index

14. **Append to ARCHIVE-INDEX.md** — Add a row to `04_Archives/ARCHIVE-INDEX.md`:

```markdown
| Item | Category | Archived Date | Reason | Notes |
|------|----------|--------------|--------|-------|
| [Name] | [_category] | YYYY-MM-DD | [reason] | [brief description] |
```

If `ARCHIVE-INDEX.md` does not exist, create it with the header row.

15. **Report completion** — Summarize what was archived, where it went, and any warnings (broken links, unresolved TODOs).

## Bulk Archive Mode

When archiving multiple items (e.g., post-audit cleanup):

1. Scan the source directory for all items matching the criteria.
2. Classify each item using Phase 1 logic.
3. Present a single consolidated table for all items.
4. Execute all moves after one confirmation.
5. For agent artifacts: create a `MANIFEST.md` inside the container listing what was archived and why.

## Anti-Patterns (Never Do This)

- **Dated dump directories** — Never create `Archived-YYYY-MM-DD/` at the archive root. Always use taxonomy categories.
- **Silent archiving** — Never archive without frontmatter or a MANIFEST explaining why.
- **Archiving active items** — If something is referenced weekly or has `status: active`, it is not ready.
- **Nesting archives** — `04_Archives/Old Archives/` is never valid. Use the flat taxonomy.
- **Purging** — Never delete archived items. Purges require explicit human decision during annual review.

## Error Handling

| Situation | Action |
|:---|:---|
| Target has `status: active` in frontmatter | Warn user; do not archive without override |
| Target has unresolved TODOs | List them; ask user to confirm |
| Many inbound WikiLinks (>5) | Recommend leaving a stub; list the linking notes |
| Destination folder doesn't exist | Create it following taxonomy naming conventions |
| ARCHIVE-INDEX.md doesn't exist | Create it with standard header |
| Target is inside a git repo (`02_Areas/Skills/`, `02_Areas/Tools for Thought/`) | Refuse to archive; these are managed externally |

## Internal Metadata
- **color**: gray
- **tags**: [skill, organization, archiving, maintenance]
- **domain**: productivity
- **status**: active
- **version**: 1.0
- **created**: 2026-02-28
