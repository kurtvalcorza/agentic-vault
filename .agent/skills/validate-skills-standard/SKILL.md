---
name: validate-skills-standard
description: "Validates existing skills against the Agent Skills open standard compliance. Use when you need to audit skills for standard compliance, check skill structure and formatting, ensure skills follow the open standard directory structure, validate YAML frontmatter, or prepare skills for cross-platform compatibility."
---

# Validate Agent Skills Standard

## Safety & Confirmation
- **Destructive Actions:** Actions that **remove**, overwrite, or **delete** files MUST be explicitly **confirmed** by the user.
- **Auto-Cleanup:** Any script that performs **cleanup** or **purge** operations must ask for **approval** first.

## Purpose

This skill validates existing Agent Skills against the open standard to ensure compliance, portability, and interoperability across AI platforms.

## Validation Checklist

### Directory Structure Compliance
- [ ] Skill is organized as a directory (not a single file)
- [ ] Contains required `SKILL.md` file
- [ ] Contains required `README.md` file (Dual-Documentation Pattern)
- [ ] Uses proper subdirectories: `scripts/`, `references/`, `assets/` (if needed)
- [ ] No extraneous files (CHANGELOG.md, INSTALLATION_GUIDE.md, etc.)

### YAML Frontmatter Standards
- [ ] Contains required fields: `name` and `description`
- [ ] Allows optional fields: `license`, `compatibility`, `metadata`, `allowed-tools`
- [ ] `name` matches directory name (kebab-case, alphanumeric + hyphens)
- [ ] `description` describes what the skill does and when to use it
- [ ] No unknown/extra fields in frontmatter (move to internal metadata)

### Content Organization
- [ ] SKILL.md body recommended under 5000 tokens (approx. 500 lines)
- [ ] Detailed content moved to `references/` when appropriate
- [ ] Executable code in `scripts/` directory
- [ ] Output templates/assets in `assets/` directory

### Progressive Disclosure Implementation
- [ ] Metadata (name + description) loaded first
- [ ] Core instructions in SKILL.md body
- [ ] Heavy resources lazy-loaded from subdirectories

### Documentation Quality (Structural)
- [ ] Purpose statement exists
- [ ] Trigger patterns present in description
- [ ] Step-by-step instructions present
- [ ] References link to existing files

## Validation Workflow

1. **Discover**
   - List every skill directory under `.agent/skills/` (`file-search`).

2. **Validate**
   - Check each skill against the Validation Checklist above (`file-read`).
   - Consult `references/agent-skills-standard.md` for the full standard.

3. **Report**
   - Write a compliance report to `.agent/outputs/` (`file-write`).
   - For any "Non-compliant" skills, address the specific structural issues listed (missing fields, wrong directory structure, etc.).

4. **Fix (Optional)**
   - With explicit user approval, apply fixes for common issues (missing fields, wrong directory structure).

## Output Format

The compliance report is written to `.agent/outputs/YYYY-MM-DD_Skills-Compliance-Report.md`:

```markdown
# Agent Skills Standard Compliance Report

## Summary
- Total skills: X
- Compliant: Y
...
```

## Remediation Actions

For each non-compliant skill, provide specific actions:

1. **Structure Issues**
   - Remove extraneous files
   - Create missing directories
   - Reorganize content properly

2. **Frontmatter Issues**
   - Add missing required fields
   - Remove extra fields
   - Improve description quality

3. **Content Issues**
   - Split oversized SKILL.md files
   - Move content to appropriate directories

## Integration Notes

This skill works with:
- `.agent/skills/` directory structure
- Agent Skills open standard specification
- Cross-platform compatibility requirements

