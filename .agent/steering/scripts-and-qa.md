---
description: "Script execution guidelines and quality assurance workflows — available scripts, execution guidelines, validation workflows, and pre-commit checks."
source-section: "Script Execution, Quality Assurance"
---

## Script Execution

### Available Scripts
*   **Location**: `.agent/scripts/`
*   **PowerShell**: Use `pwsh` for cross-platform compatibility. Invoke with full path resolution.
*   **Python**: Assume Python 3.9+ with standard library unless dependencies are documented.
*   **Validation**: Run `validate-skills-standard` before committing new skills.

### Execution Guidelines
*   Always check script existence before invoking.
*   Log script outputs for debugging.
*   Handle errors gracefully; report failures to user.

## Quality Assurance

### Validation Workflows
*   **Frontmatter Validation**: All skills must pass YAML schema validation (strict mode).
*   **Link Integrity**: Verify `[[WikiLinks]]` resolve to existing notes before finalizing.
*   **Tone Consistency**: Projects/Areas = Professional/Institutional; Journals/Notes = Casual/Personal.
*   **Maintenance**: Run `optimize-workspace` quarterly to clean up orphaned files and broken links.

### Pre-Commit Checks
*   Skills must have both `SKILL.md` and `README.md`.
*   Frontmatter must use `name` and `description` fields (kebab-case for names).
*   No hardcoded paths or drive letters in scripts or notes.
