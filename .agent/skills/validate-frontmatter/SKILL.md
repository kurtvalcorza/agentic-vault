---
name: validate-frontmatter
description: "Validate YAML frontmatter compliance for agent skills and workflows. Use when you need to check that skills follow proper frontmatter standards, ensure metadata consistency, or validate workspace compliance with organizational standards"
---

# Utility: Validate Frontmatter

### Related Workflows
- **[[../validate-workspace/SKILL|Validate Workspace]]** - Full frontmatter scan across agent workspace

---

## Purpose
Ensure agent skills and workflows comply with AGENTS frontmatter standards.

## Inputs
- `.agents` directory

## Outputs
- `.agents/outputs/validate-frontmatter/governance-report.md`

## Workflow

### 1. Scan
- Glob `**/*.md` in `.agents/skills` and `.agents/outputs` as needed.
- Exclude `README.md` unless explicitly requested.

### 2. Validation Loop
For each file:
1. **Check Frontmatter**: Must include `name` and `description`. `license` is optional.
2. **Check Values**: `description` should include both what the skill does and when to use it.
3. **Report Only**: This utility does not auto-fix; it reports issues for review.

### 3. Reporting
- Generate `governance-report.md`.
- List files passed/failed with missing fields.
