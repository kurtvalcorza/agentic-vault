# Validate Workspace

Automated frontmatter validation across all agent workspace files, ensuring compliance with organizational standards.

## What This Does

Runs a 4-phase validation process:

1. **Discovery**: Scans `.agent/` and agent workspace directories for all markdown files
2. **Validation**: Checks frontmatter against schema requirements
3. **Reporting**: Generates detailed validation report with specific violations
4. **Auto-Repair** (optional): Fixes common issues with user approval

## What Gets Validated

- **Required Fields**: `name`, `description` (for skills)
- **Field Formats**: `name` must be kebab-case
- **YAML Syntax**: Valid YAML structure
- **Directory Structure**: Skills in `*/skills/`, proper organization
- **Schema Compliance**: Matches strict validation rules

## When to Use

- **Before committing new skills**: Ensure compliance with standards
- **After bulk changes**: Verify nothing broke during refactoring
- **Onboarding**: Understand frontmatter requirements
- **Quality assurance**: Regular checks to maintain consistency

## How to Trigger

Say: **"Validate my workspace"** or **"Check frontmatter compliance"**

## What You Get

A validation report showing:

- Files scanned and validation status
- Specific violations with file paths and issues
- Suggestions for fixing common problems
- Option to auto-repair (requires your approval)

## Auto-Repair Capabilities

Can automatically fix:

- Missing `name` field (infers from directory name)
- Missing `description` field (generates placeholder)
- Invalid YAML syntax (basic formatting issues)
- Incorrect `name` casing (converts to kebab-case)

**Note**: Always review auto-repair changes before accepting. Complex issues may require manual intervention.
