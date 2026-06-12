# Agent Skills Open Standard Compliance

This workspace follows the [Agent Skills open standard](https://agentskills.io) released by Anthropic in December 2025.

## What is the Agent Skills Standard?

Agent Skills is an open standard format for creating reusable AI capabilities that work across different AI platforms. It provides:

- **Portability**: Skills work across AI assistants and IDEs
- **Interoperability**: Standard format enables sharing and collaboration
- **Future-proofing**: Open standard ensures long-term compatibility
- **Community**: Fosters ecosystem growth and knowledge sharing

## Standard Compliance

### ✅ Directory Structure
```
skill-name/
├── SKILL.md           # Required: Technical implementation with YAML frontmatter
├── scripts/           # Optional: Executable code (Python/Bash/JavaScript/etc.)
├── references/        # Optional: Documentation loaded as needed
└── assets/            # Optional: Static resources (templates, images, etc.)
```

### ✅ Required YAML Frontmatter
```yaml
---
name: skill-name
description: "Max 1024 characters. Describes what the skill does and when to use it."
---
```

**Required Fields:**
- `name`: Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen.
- `description`: Max 1024 characters. Non-empty. Describes what the skill does and when to use it.

**Optional Fields:**
- `license`: License name or reference to a bundled license file
- `compatibility`: Max 500 characters. Environment requirements (intended product, system packages, network access, etc.)
- `metadata`: Arbitrary key-value mapping for additional metadata
- `allowed-tools`: Space-delimited list of pre-approved tools the skill may use (Experimental)

### ✅ Progressive Disclosure
- **Metadata (~100 tokens)**: The name and description fields are loaded at startup for all skills
- **Instructions (< 5000 tokens recommended)**: The full SKILL.md body is loaded when the skill is activated
- **Resources (as needed)**: Files in scripts/, references/, or assets/ are loaded only when required

### ✅ Content Organization
- Keep SKILL.md under 500 lines
- Move detailed reference material to separate files in `references/`
- Use `scripts/` for executable code that agents can run
- Use `assets/` for static resources (templates, images, fonts, etc.)
- Use relative paths from skill root when referencing files
- Keep file references one level deep from SKILL.md

### ✅ File Reference Format
When referencing other files in your skill, use relative paths from the skill root:
```markdown
See [detailed instructions](references/advanced-usage.md)
Run the setup script: `scripts/setup.py`
Use template: `assets/report-template.docx`
```

## Validation

Skills can be validated using the skills-ref reference library:
```bash
# Validate SKILL.md frontmatter and naming conventions
skills-ref validate skill-name/
```

## Relationship to MCP

Agent Skills complements Model Context Protocol (MCP):

- **Agent Skills**: Provide knowledge and workflows ("what" and "how")
- **MCP**: Provides tool integration and data access ("where" and "when")

Both are open standards that work together to create powerful AI agent capabilities.

## Benefits of Open Standards

1. **Cross-Platform Compatibility**: Skills work with multiple AI assistants
2. **Community Collaboration**: Share and improve skills across teams
3. **Future-Proofing**: Standards evolve with community input
4. **Ecosystem Growth**: More platforms adopting the standard increases value
5. **Transparency**: Open specification enables review and improvement

## Implementation Notes

This workspace implements the Agent Skills standard with these enhancements:

- **Multi-Agent Support**: Separate workspaces for different AI platforms
- **Vault Integration**: Skills integrate with Obsidian PKM system
- **Progressive Disclosure**: Three-level loading system for context efficiency
- **Quality Gates**: Validation and packaging tools for skill creation

## Resources

- [Official Agent Skills Specification](https://agentskills.io/specification)
- [Agent Skills GitHub Repository](https://github.com/agentskills/agentskills)
- [Example Skills](https://github.com/agentskills/agentskills#example-skills)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---
Last Updated: 2026-01-30
Standard Version: Official Specification (agentskills.io)