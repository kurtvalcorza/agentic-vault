# Tool Capability Taxonomy

**Purpose:** Provide a universal vocabulary for referencing agent capabilities in shared skills (`.agent/skills/`). Each agent maps these generic names to its own tool implementations at runtime.

---

## Convention

> In `.agent/skills/` SKILL.md files, always use the **Generic Capability** name (e.g., `file-read`, `content-search`) instead of agent-specific tool names. Each agent maps these to its own tools at runtime.

**Why:** Skills in `.agent/skills/` must be executable by any AI agent (Claude, Gemini, Kiro, Copilot, etc.). Using agent-specific tool names creates lock-in and breaks portability.

---

## Capability Mapping

| Generic Capability | Claude | Gemini / Kiro | Description |
|:---|:---|:---|:---|
| `file-read` | Read | readFile | Read file contents |
| `file-write` | Write | writeFile | Create or overwrite files |
| `file-edit` | Edit | editFile / replace_file_content | Modify existing file content in place |
| `file-search` | Glob | fileSearch / find_files | Find files by name or glob pattern |
| `content-search` | Grep | grepSearch | Search inside file contents by pattern |
| `command-exec` | Bash | runCommand / runInTerminal | Execute shell commands |
| `user-interact` | AskUserQuestion | (conversational) | Ask the user a question interactively |
| `web-fetch` | WebFetch | searchWeb | Retrieve or search web content |
| `sub-agent` | Task | (native delegation) | Spawn a sub-agent for parallel work |
| `obsidian-query` | run_command | run_command | Execute read-only Obsidian CLI commands (e.g., `tags`, `aliases`) |
| `obsidian-action` | run_command | run_command | Execute state-modifying Obsidian CLI commands (e.g., `plugin:reload`) |


### Notes
- **New agents:** Add a column to this table when onboarding a new AI agent to the vault.
- **New capabilities:** Add a row when a shared skill requires a capability not listed here.
- **Agent-specific skills** (in `.claude/skills/`, `.gemini/skills/`, `.kiro/skills/`) may use their native tool names directly.

---

## How to Use This

### In SKILL.md Tool Dependencies

**Before (agent-specific):**
```markdown
### Required Tools
- `Read` - Read input files
- `Write` - Generate output report
- `Bash` - Execute shell scripts
- `Glob` - Find corpus files
```

**After (universal):**
```markdown
### Required Capabilities
- `file-read` - Read input files
- `file-write` - Generate output report
- `command-exec` - Execute shell scripts
- `file-search` - Find corpus files
```

### In Workflow Descriptions

**Before (agent-specific):**
```markdown
Use `AskUserQuestion` to gather requirements, then use `Grep` to search the corpus.
```

**After (universal):**
```markdown
Use `user-interact` to gather requirements, then use `content-search` to search the corpus.
```

### In Example Dialogues

**Before (agent-specific):**
```markdown
**Claude:** What topic would you like to explore?
```

**After (universal):**
```markdown
**Agent:** What topic would you like to explore?
```

---

## Validation

Run this check to find violations in shared skills:
```
grep -rn "`Read`\|`Write`\|`Edit`\|`Bash`\|`Glob`\|`Grep`\|`Task`\|`AskUserQuestion`\|`WebFetch`" .agent/skills/*/SKILL.md
```

Expected result: zero matches (all shared skills use generic capability names).

---

**Last Updated:** 2026-02-14
**Referenced by:** [[AGENTS.md]] (Organizational Standards section)
