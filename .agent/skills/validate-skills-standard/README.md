# Validate Agent Skills Standard

Compliance validator for the Agent Skills open standard.

## What It Does

Validates skills against structural and content requirements:
- Directory structure (SKILL.md + README.md)
- YAML frontmatter schema (strict mode)
- Content organization (sections, progressive disclosure)
- Naming conventions (kebab-case)

Generates detailed compliance reports with pass/fail status and specific violations.

## When to Use

- Before committing new skills
- During skill reviews or audits
- Maintaining standard compliance across vault
- Troubleshooting skill loading issues

## Quick Start

**Trigger**: "Validate agent skills standard"

The skill will:
1. Scan `.agent/skills/` and agent workspace skill directories
2. Check each skill against standard requirements
3. Report violations with specific file paths and line numbers
4. Optionally apply fixes for common issues (with your approval)

## Components

- **Validation Checklist**: `SKILL.md` — structure, frontmatter, and content checks
- **Standard Reference**: `references/agent-skills-standard.md` — the full Agent Skills standard
- **Compliance Report**: Markdown summary written to `.agent/outputs/`

## Related Skills

- `review-skill-design` - Deep cognitive audit beyond structural compliance
- `assimilate-skills` - Import external skills with validation
