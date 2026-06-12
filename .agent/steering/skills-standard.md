---
description: "Agent Skills Standard — Dual-Documentation Pattern, Standardized Frontmatter, Skills as Directories, and Universality Standards for shared skills."
source-section: "Organizational Standards (The \"Agent Skills Standard\")"
---

## Organizational Standards (The "Agent Skills Standard")

### 1. Dual-Documentation Pattern
All skills MUST have:
*   **`SKILL.md`**: Technical implementation (prompts, tool chains). This is the file agents load and execute.
*   **`README.md`**: User-facing documentation (what it does, when to use, quick start).

> **Deviation from Anthropic's official guide:** Anthropic's skill-authoring guidance says "Don't include README.md inside your skill folder." This vault intentionally keeps README.md because skills here serve multiple AI agents (Claude, Gemini, Kiro), not just Claude. README.md provides human-readable documentation separate from agent instructions — a separation of concerns the single-agent guide doesn't address.

### 2. Standardized Frontmatter
All skills must use the **Strict** YAML schema enforced by `validate-skills-standard`:
```yaml
---
name: [kebab-case-name]
description: [What it does]. Use when [trigger phrases].
# Optional: license, compatibility, metadata
---
```
*   **`description`** MUST include both WHAT the skill does AND WHEN to use it (trigger phrases). Under 1024 characters. No XML angle brackets.
*   Avoid adding top-level fields like `version` or `status` that cause validation failures.

### 3. Skills as Directories
Skills are directories in `*/skills/`, not single files.
Structure: `skill-name/` -> `{SKILL.md, README.md, references/, templates/}`.

### 4. Universality Standards for Shared Skills
Skills in `.agent/skills/` are shared across all agents and MUST be agent-agnostic:
*   **Tool references**: Use generic capability names from `.agent/TOOL-TAXONOMY.md` (e.g., `file-read`, `content-search`) instead of agent-specific tool names (e.g., `Read`, `Glob`, `readFile`).
*   **Example dialogues**: Use `**Agent:**` as the speaker label, not specific agent names.
*   **Model metadata**: Do NOT include `model:` lines with specific model names in shared skills.
*   **Paths**: Reference `.agent/` paths, not agent-specific directories like `.gemini/` or `.claude/`.
*   **Agent-specific extensions**: If a skill has agent-specific features, document them in a clearly labeled section of its `SKILL.md`.
