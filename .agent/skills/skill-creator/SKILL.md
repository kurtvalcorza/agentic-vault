---
name: skill-creator
description: "Interactive guide for creating skills that extend the agent's capabilities. Use when user asks to 'create a skill', 'build a new skill', 'make a skill for', or wants to package specialized workflows, domain knowledge, or tool integrations. Covers use case definition, frontmatter generation, instruction writing, and validation."
---








# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend the agent's capabilities by providing specialized knowledge, workflows, and tools. They work identically across agent platforms—create once, use everywhere.

### Common Skill Use Cases

**Category 1: Document & Asset Creation**
- Creating consistent, high-quality output (presentations, documents, code, designs)
- Embedded style guides and brand standards
- Template structures for consistent output
- Example: frontend-design skill, docx-generator skill

**Category 2: Workflow Automation**
- Multi-step processes with consistent methodology
- Step-by-step workflows with validation gates
- Iterative refinement loops
- Example: skill-creator skill, sprint-planning skill

**Category 3: MCP Enhancement**
- Workflow guidance for MCP server tool access
- Coordinates multiple MCP calls in sequence
- Embeds domain expertise and error handling
- Example: sentry-code-review skill, notion-project-setup skill

## Safety & Security

### Confirmation Protocol
- **Destructive Actions:** Always ask for explicit user confirmation before deleting, removing, or overwriting ANY file.
- **Permissions:** Ensure the user has authorized the initialization or packaging of a skill before execution.

### Security Restrictions

**Forbidden in frontmatter:**
- XML angle brackets (< >) - Can inject malicious instructions
- Skills with vendor-specific names (e.g., "claude", "anthropic", "gemini") - Reserved names
- Rationale: Frontmatter appears in the agent's system prompt

**Naming requirements:**
- Use kebab-case only: `notion-project-setup` ✅
- No spaces: `Notion Project Setup` ❌
- No underscores: `notion_project_setup` ❌
- No capitals: `NotionProjectSetup` ❌

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else the agent needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: The agent is already very capable.** Only add context the agent doesn't already have. Challenge each piece of information: "Does the agent really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of the agent as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)    - Agent-facing technical instructions
├── README.md (required)   - Human-facing documentation (vault standard)
│   ├── YAML frontmatter metadata (required in SKILL.md)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields that the agent reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

**Writing effective descriptions:**

Use the formula: `[What it does] + [When to use it] + [Key capabilities]`

Include specific trigger phrases users might say:

```yaml
# Good - specific and actionable
description: Analyzes Figma design files and generates developer handoff 
documentation. Use when user uploads .fig files, asks for "design specs", 
"component documentation", or "design-to-code handoff".

# Good - includes trigger phrases
description: Manages Linear project workflows including sprint planning, 
task creation, and status tracking. Use when user mentions "sprint", 
"Linear tasks", "project planning", or asks to "create tickets".
```

**Character limit:** Under 1024 characters

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by the agent for patching or environment-specific adjustments

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform the agent's process and thinking.

- **When to include**: For documentation that the agent should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API docs, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when the agent determines it's needed
- **Best practice**: If files are large (>10k words), include search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to reference files.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output the agent produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables the agent to use files without loading them into context

#### What to Not Include in a Skill

A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files such as INSTALLATION_GUIDE.md, QUICK_REFERENCE.md, CHANGELOG.md, etc.

**README.md exception:** This vault requires a `README.md` in every skill directory (Dual-Documentation Pattern). `SKILL.md` contains agent-facing technical instructions; `README.md` provides human-readable documentation (what it does, when to use, quick start). This deviates from Anthropic's single-agent guide but is intentional for multi-agent compatibility. See `AGENTS.md` for rationale.

The skill should not contain auxiliary context about the process that went into creating it, setup and testing procedures beyond what the agent needs, etc.

### Vault-Specific Standards

Skills created in `.agent/skills/` are shared across all AI agents and MUST follow these universality rules (see `AGENTS.md` for full details):

- **Tool references**: Use generic capability names from `.agent/TOOL-TAXONOMY.md` (e.g., `file-read`, `content-search`) instead of agent-specific names (e.g., Read, Glob, readFile, grepSearch)
- **Example dialogues**: Use `**Agent:**` as speaker label, not `**Claude:**` or `**Gemini:**`
- **Model metadata**: Do NOT include `model:` lines with specific model names
- **Paths**: Reference `.agent/` paths, not agent-specific directories
- **Dual-Documentation**: Every skill MUST have both `SKILL.md` (agent instructions) and `README.md` (human documentation)
- **Description triggers**: The `description` field MUST include both WHAT the skill does AND WHEN to use it (trigger phrases)

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed (Unlimited because scripts can be executed without reading into context window)

#### Progressive Disclosure Patterns

Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from SKILL.md and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.

**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.

**Pattern 1: High-level guide with references**

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

The agent loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.

**Pattern 2: Domain-specific organization**

For Skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

When a user asks about sales metrics, the agent only reads sales.md.

Similarly, for skills supporting multiple frameworks or variants, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

When the user chooses AWS, the agent only reads aws.md.

**Pattern 3: Conditional details**

Show basic content, link to advanced content:

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

The agent reads REDLINING.md or OOXML.md only when the user needs those features.

**Important guidelines:**

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so the agent can see the full scope when previewing.

## Skill Creation Workflow

1. **Phase 1: Discovery** - Understand intent with concrete examples and identify use case category
2. **Phase 2: Planning** - Identify reusable scripts, references, and assets
3. **Phase 3: Initialization** - Create skill folder structure
4. **Phase 4: Implementation** - Implement resources and write `SKILL.md`
5. **Phase 5: Testing** - Validate trigger conditions and success criteria
6. **Phase 6: Iteration** - Refine based on real-world usage

### Success Criteria

**Quantitative metrics:**
- Skill triggers on 90% of relevant queries
- Completes workflow in expected number of tool calls
- 0 failed API calls per workflow

**Qualitative metrics:**
- Users don't need to prompt the agent about next steps
- Workflows complete without user correction
- Consistent results across sessions

For detailed instructions, usage patterns, and design guides for each step, see:
- **[references/creation-steps.md](references/creation-steps.md)** - Skill Creation Deep Dive
- **[references/workflows.md](references/workflows.md)** - Multi-step Process Guide
- **[references/output-patterns.md](references/output-patterns.md)** - Quality Standards & Templates

## Utility Scripts

Helper scripts in `scripts/` for common skill operations. All use Python 3.9+ with standard library (+ PyYAML for validation).

### `scripts/init_skill.py` — Scaffold a new skill

Creates a skill directory with templated SKILL.md, example resource directories (scripts/, references/, assets/), and placeholder files.

```bash
python scripts/init_skill.py <skill-name> --path <target-directory>
# Example: python scripts/init_skill.py my-new-skill --path .agent/skills
```

### `scripts/quick_validate.py` — Validate skill frontmatter

Checks SKILL.md existence, YAML frontmatter structure, required fields (name, description), naming conventions (kebab-case), character limits, and forbidden characters.

```bash
python scripts/quick_validate.py <path/to/skill-directory>
```

### `scripts/package_skill.py` — Package skill for distribution

Runs validation then zips the skill directory into a `.skill` file. Requires `quick_validate.py` in the same directory.

```bash
python scripts/package_skill.py <path/to/skill-directory> [output-directory]
```
