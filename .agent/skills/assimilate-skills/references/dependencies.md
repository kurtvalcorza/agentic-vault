# Dependencies

## Required Tools

### Core Tools
- **`Glob`** - Discover skill directories across workspaces
- **`Read`** - Parse frontmatter from SKILL.md files
- **`Write`** - Generate analysis and plan outputs

### Search Patterns
```
.claude/skills/*/SKILL.md
.gemini/skills/*/SKILL.md
.codex/skills/*/SKILL.md
[current-agent]/skills/*/SKILL.md
```

---

## Scan Targets

### Peer Workspaces
- `.claude/skills/` - Claude workspace
- `.gemini/skills/` - Gemini workspace
- `.codex/skills/` - Codex workspace (if exists)
- `.agent/skills/` - Shared universal skills
- Current agent's own workspace (e.g., `.kiro/skills/`)

### Frontmatter Fields to Extract
- `name` - Skill identifier
- `version` - For version comparison
- `domain` - For categorization
- `description` - For understanding purpose
- `status` - Skip deprecated/experimental skills

---

## Output Locations

### Standard Outputs
All outputs are generated in the skill's output directory:

- `outputs/assimilation-gap-analysis.md` - Raw comparison data
- `outputs/assimilation-plan.md` - Actionable task list

### Output Path Pattern
```
[current-agent]/skills/assimilate-skills/outputs/
```

---

## Related Skills

### Workflow Integration
- **skill-creator** - For porting missing skills from peer workspaces
- **workspace-optimizer** - For maintaining skill registry after assimilation
- **validate-skills-standard** - For ensuring ported skills comply with standards

### Registry Updates
After assimilation, update:
- `[current-agent]/SKILLS-REGISTRY.md` - Add newly ported skills
- Skill category indices (if maintained)
