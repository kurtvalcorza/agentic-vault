# Assimilate Skills

**Automated workspace parity checker for multi-agent environments**

---

## What is this?

Assimilate Skills is a technology scout that ensures your agent workspace stays synchronized with peer workspaces (Claude, Gemini, Codex, shared `.agent/` skills). When multiple AI agents evolve independently, each may develop unique skills or improvements. This skill prevents knowledge silos by:

- 🔍 **Discovering** skills developed in other workspaces
- 📊 **Comparing** version differences across workspaces
- 📋 **Generating** actionable plans for porting improvements
- 🎯 **Prioritizing** which skills to adopt based on strategic value

---

## When to use this skill

### Trigger Phrases
- "Check for new skills"
- "Run assimilation check"
- "What skills does Gemini have?"
- "Is my workspace up to date with Claude?"
- "Compare skills across workspaces"
- "Check for skill updates"

### Use Cases

**Scenario 1: Quarterly Workspace Audit**
```
"Run an assimilation check across all workspaces"

→ Generates comprehensive gap analysis
→ Identifies 7 missing skills and 3 upgrade opportunities
→ Creates prioritized implementation plan
```

**Scenario 2: Targeted Peer Check**
```
"Check if Gemini has any new skills I should port"

→ Scans Gemini workspace only
→ Highlights missing skills in relevant domains
→ Suggests which ones to port first
```

**Scenario 3: Before Starting New Project**
```
"Are there any presentation skills in other workspaces?"

→ Searches for domain-specific skills
→ Identifies "presentation-studio" in Gemini workspace
→ Recommends porting before project begins
```

---

## What it produces

### Output Files

**1. Gap Analysis Report**
- **File:** `outputs/assimilation-gap-analysis.md`
- **Contains:**
  - Summary statistics (missing, outdated, parity counts)
  - Missing skills table (port candidates)
  - Outdated skills table (upgrade candidates)
  - Unique domain skills (strategic evaluation)
  - Current advantages (reverse-port candidates)

**2. Assimilation Plan**
- **File:** `outputs/assimilation-plan.md`
- **Contains:**
  - Prioritized action items (high/medium/low)
  - Step-by-step porting instructions
  - Time estimates per skill
  - Post-assimilation checklist

---

## How it works

### Workflow Overview

```
Phase 1: Scan & Parse
├─ Discover all skills in peer workspaces
├─ Parse frontmatter (name, version, domain, status)
└─ Build skill inventory per workspace

Phase 2: Gap Analysis
├─ Compare inventories
├─ Classify gaps (Missing, Outdated, Unique Domain)
└─ Assign priorities

Phase 3: Generate Gap Analysis Report
├─ Create comparison tables
├─ Add summary statistics
└─ Save to outputs/assimilation-gap-analysis.md

Phase 4: Generate Assimilation Plan
├─ Create actionable task lists
├─ Add step-by-step instructions
└─ Save to outputs/assimilation-plan.md
```

### Gap Types Explained

| Gap Type | What It Means | Priority | Action |
|----------|--------------|----------|--------|
| **Missing** | Peer has skill you don't | **High** | Consider porting |
| **Outdated** | You have older version | **Medium** | Review and upgrade |
| **Unique Domain** | Peer has new capability area | **High** | Evaluate strategic fit |
| **Parity** | Versions match | **Low** | No action needed |
| **Your Advantage** | You're ahead | **Info** | Share with peers |

---

## Example Output

### Gap Analysis Report Sample

```markdown
# Assimilation Gap Analysis
**Generated:** 2026-02-14 14:30
**Scanned:** .gemini (45 skills), .claude (38 skills), .agent (75 skills)

## Summary
- Missing skills: 7 (High Priority)
- Outdated skills: 3 (Medium Priority)
- Current advantages: 2

## Missing Skills (Port Candidates)
| Skill | Domain | Source | Description |
|-------|--------|--------|-------------|
| presentation-studio | presentation | .gemini | Framework-based presentations |
| recursive-lit-review | research | .gemini | Automated literature synthesis |
| consolidate-weekly-report | reporting | .gemini | Weekly status automation |

## Outdated Skills (Upgrade Candidates)
| Skill | Current Ver | Peer Ver | Source |
|-------|-------------|----------|--------|
| skill-creator | 1.0 | 1.2 | .claude | 2 versions behind |
```

---

## Recommended Usage

### Frequency
- **Quarterly:** Run full workspace parity check
- **After major updates:** Targeted scan when peers announce new skills
- **Before projects:** Check for domain-relevant skills

### Workflow
1. Run assimilation check
2. Review generated gap analysis
3. Approve which skills to port
4. Use `skill-creator` to implement ports
5. Validate with `validate-skills-standard`
6. Update `SKILLS-REGISTRY.md`

---

## Integration with Other Skills

### Works Best With

**skill-creator**
- Use after identifying missing skills
- Creates proper skill structure for ports

**validate-skills-standard**
- Ensures ported skills comply with standards
- Catches frontmatter or structure issues

**workspace-optimizer**
- Run after bulk assimilation
- Updates registries and cleans up

---

## FAQ

**Q: Will this automatically port skills?**
A: No. It generates analysis and plans, but you must approve and execute ports.

**Q: What if a skill is agent-specific?**
A: The analysis flags agent-specific features and recommends adapting or skipping.

**Q: Can I share my advantages with peer workspaces?**
A: Yes! The report identifies where you're ahead and suggests reverse-porting to `.agent/skills/`.

**Q: How long does a full scan take?**
A: Typically 30-60 seconds to scan 150+ skills across 5 workspaces.

**Q: What if peer workspace has different frontmatter schema?**
A: The skill reads available fields and handles missing/different schemas gracefully.

---

## Technical Details

### Scanned Workspaces
- `.claude/skills/` - Claude workspace
- `.gemini/skills/` - Gemini workspace
- `.codex/skills/` - Codex workspace (if exists)
- `.agent/skills/` - Shared universal skills
- Current agent's workspace

### Required Tools
- `Glob` - File discovery
- `Read` - Frontmatter parsing
- `Write` - Report generation

### Skip Rules
- Skills with `status: deprecated`
- Skills with `status: experimental`
- Skills in `_archived/` directories

---

## Related Skills

- **skill-creator** - Port missing skills
- **validate-skills-standard** - Validate ported skills
- **workspace-optimizer** - Maintain registries after assimilation

---

## Need Help?

**For implementation details:** See [`SKILL.md`](SKILL.md)
**For gap methodology:** See [`references/gap-analysis-methodology.md`](references/gap-analysis-methodology.md)
**For report formats:** See [`references/report-templates.md`](references/report-templates.md)
**For integration steps:** See [`references/integration-workflow.md`](references/integration-workflow.md)
