# Validate Frontmatter

Validate YAML frontmatter compliance for agent skills.

## When to Use
- After creating or modifying skills
- Before committing changes
- During workspace optimization

## What It Does
1. Scans `.agent/skills/` directory
2. Checks YAML schema compliance
3. Validates required fields (name, description)
4. Generates governance report

## Quick Start
Just say: **"validate frontmatter"**

## Output Location
Terminal report with pass/fail status

## Common Issues Detected
- Missing `name` or `description` fields
- Invalid YAML syntax
- Unsupported top-level fields

## Works With
- validate-workspace (comprehensive checks)
- optimize-workspace (cleanup workflows)
