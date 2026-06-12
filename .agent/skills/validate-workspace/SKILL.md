---
name: validate-workspace
description: "Automated frontmatter validation utility that checks YAML metadata compliance across the agent workspace. Use when you need to validate workspace structure and frontmatter compliance."
---








# Validate Workspace: Frontmatter & Structure

## Safety & Confirmation
- **Destructive Actions:** Actions that **remove**, overwrite, or **delete** files MUST be explicitly **confirmed** by the user.
- **Auto-Cleanup:** Any script that performs **cleanup** or **purge** operations must ask for **approval** first.

## Dependencies

### Required Skills
- None (Utility)

### Required Tools
- `file-read` - Read markdown files.
- `file-search` - Find all skill files.
- `file-write` - Save compliance report.

### Phase Dependencies
- **Phase 1** -> **Phase 2** -> **Phase 3** -> **Phase 4**

### Input Files
- `.agent/skills/**/*.md`

### Output Directories
- `.agent/outputs/`

---

## Safety & Confirmation
- **Auto-Repair:** The "Auto-Repair" feature (Phase 4) modifies files. **Explicit user confirmation (confirm=True) is MANDATORY before any repair action is taken.**
- **Non-Destructive Scanning:** Phase 1-3 are read-only and do not require confirmation.

## Purpose
Ensure all workflow specifications and skills in the agent workspace comply with organizational standards defined in `AGENTS.md`.

## Required Frontmatter Fields

Per the Agent Skills Standard (`.agent/steering/skills-standard.md`), all skill files MUST include:

```yaml
---
name: [kebab-case-name]
description: "[What it does]. Use when [trigger phrases]."
---
```

Optional fields: `license`, `compatibility`, `metadata`, `two_output`. Shared skills MUST NOT include a `model:` field (see Universality Standards in `.agent/SKILLS-REGISTRY.md`).

## Validation Rules

**Format Checks:**
- `name` must be kebab-case and match the skill's directory name
- `description` must cover both *what* the skill does and *when* to use it
- No `model:` field in shared skills
- No agent-specific tool names in skill bodies (use generic capabilities from `.agent/TOOL-TAXONOMY.md`)

**Directory Structure:**
- Skills must be in `.agent/skills/{skill-name}/`
- Must contain `SKILL.md` and `README.md`

## 4-Phase Workflow

**Phase 1: Discovery**
- Scan `.agent/skills/` recursively
- List all `SKILL.md` files
- Count total files to validate

**Phase 2: Validation**
For each file:
- Check frontmatter exists (between `---` markers)
- Validate required fields present
- Check format compliance
- Verify directory structure matches skill name
- Flag errors/warnings

**Phase 3: Reporting**
Generate compliance report:

```markdown
# Workspace Validation Report - [Date]

## Summary
- Total skills scanned: X
- Pass: Y
- Fail: Z
- Warnings: W

## Failed Files

### .agent/skills/example/SKILL.md
- ❌ Missing field: `description`
- ⚠️  `name` does not match the skill's directory name

## Passed Files
- ✅ .agent/skills/write-note/SKILL.md
```

**Phase 4: Auto-Repair (Optional)**
If user approves, fix common issues:
- Add missing `name` (inferred from the directory name)
- Add missing `description` (placeholder for the author to refine)
- Convert `name` to kebab-case
- Remove `model:` fields from shared skills

## Report Output

Save to: `.agent/outputs/YYYY-MM-DD_Workspace-Validation-Report.md`


## Internal Metadata
- **capabilities**: file-read, file-search, file-write
- **color**: grey
- **tags**: [utility, maintenance, validation, frontmatter]
- **domain**: maintenance
- **status**: active
- **version**: 1.0
- **created**: 2026-01-16
- **updated**: 2026-01-16