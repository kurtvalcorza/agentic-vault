---
name: assimilate-skills
description: "Scans peer AI workspaces (.claude, .gemini, .codex) to identify unique skills or superior versions and generates an assimilation plan. Triggers on 'check for new skills', 'run assimilation check', 'what skills does Gemini have', or workspace parity requests"
---

# Skill: Assimilate Skills

## Purpose

Technology scout that ensures the current agent workspace maintains feature parity with peer AI workspaces (Claude, Gemini, Codex, and shared `.agent/` skills).

When multiple AI agents evolve independently in the same vault, each may develop unique skills or improvements. This skill automates gap detection and generates actionable assimilation plans to:

- **Discover missing skills** developed in peer workspaces
- **Identify outdated versions** where peers have superior implementations
- **Detect unique domains** not yet covered in current workspace
- **Generate actionable plans** for porting and upgrading

This prevents knowledge silos and ensures all agents benefit from collective improvements.

---

## Dependencies

### Required Capabilities
- **`file-search`** - Discover skill directories across workspaces
- **`file-read`** - Parse frontmatter from SKILL.md files
- **`file-write`** - Generate analysis and plan outputs

### Scan Targets
Workspaces to compare:
- `.claude/skills/` - Claude workspace
- `.gemini/skills/` - Gemini workspace
- `.codex/skills/` - Codex workspace (if exists)
- `.agent/skills/` - Shared universal skills
- Current agent's workspace (e.g., `.kiro/skills/`)

### Output Location
```
[current-workspace]/skills/assimilate-skills/outputs/
  ├── assimilation-gap-analysis.md
  └── assimilation-plan.md
```

### Related Skills
- **skill-creator** - For porting missing skills from peer workspaces
- **validate-skills-standard** - For ensuring ported skills comply with standards
- **workspace-optimizer** - For maintaining skill registry after assimilation

**Detailed dependencies:** See [`references/dependencies.md`](references/dependencies.md)

---

## Workflow

### Phase 1: Scan & Parse

**Objective:** Build inventory of all skills across peer workspaces

#### 1.1 Discover Skill Directories
Use `file-search` to find all skills in target workspaces:

```
.claude/skills/*/SKILL.md
.gemini/skills/*/SKILL.md
.codex/skills/*/SKILL.md
.agent/skills/*/SKILL.md
[current-workspace]/skills/*/SKILL.md
```

#### 1.2 Parse Frontmatter
For each discovered SKILL.md, extract:
- **`name`** - Skill identifier for comparison
- **`version`** - For version comparison (if present)
- **`domain`** - For domain coverage analysis
- **`description`** - For understanding purpose
- **`status`** - Skip deprecated/experimental skills

#### 1.3 Build Skill Inventory
Create structured inventory per workspace:

```
Workspace: .gemini
  - skill-name (v1.2, domain: research, status: active)
  - another-skill (v2.0, domain: reporting, status: active)

Workspace: .claude
  - skill-name (v1.0, domain: research, status: active)
  - unique-skill (v1.5, domain: presentation, status: active)
```

---

### Phase 2: Gap Analysis

**Objective:** Compare peer workspaces against current workspace to identify gaps

#### 2.1 Gap Type Classification

Compare inventories and categorize each skill:

| Gap Type | Condition | Priority | Action |
|----------|-----------|----------|--------|
| **Missing** | Exists in peer, not in current | **High** | Port to current workspace |
| **Outdated** | Peer version > Current version | **Medium** | Review and upgrade |
| **Unique Domain** | Peer has domain not in current | **High** | Evaluate strategic fit |
| **Parity** | Versions match across workspaces | **Low** | No action needed |
| **Current Advantage** | Current version > Peer version | **Info** | Consider reverse-port |

#### 2.2 Skip Rules

**Exclude from analysis:**
- Skills with `status: deprecated`
- Skills with `status: experimental`
- Skills in `_archived/` directories
- Agent-specific skills (identified by description or content)

#### 2.3 Priority Assignment

**High Priority:**
- Missing skills in domains already covered by current workspace
- Unique domain skills with clear strategic value
- Outdated skills with major version differences (e.g., 1.0 vs 2.0)

**Medium Priority:**
- Outdated skills with minor version differences (e.g., 1.1 vs 1.2)
- Missing skills in tangential domains

**Low Priority:**
- Skills with full parity
- Experimental or unstable skills

**Detailed methodology:** See [`references/gap-analysis-methodology.md`](references/gap-analysis-methodology.md)

---

### Phase 3: Generate Gap Analysis Report

**Objective:** Create comprehensive comparison report

#### 3.1 Report Structure

Generate `outputs/assimilation-gap-analysis.md` with:

1. **Summary Statistics**
   - Total skills analyzed per workspace
   - Missing skills count
   - Outdated skills count
   - Unique domains discovered

2. **Missing Skills Table**
   - Skill name, domain, source workspace, description
   - Sorted by priority (domain relevance)

3. **Outdated Skills Table**
   - Skill name, current version, peer version, source, gap size
   - Sorted by version gap (largest first)

4. **Unique Domain Skills Table**
   - Skill name, new domain, source, description
   - Grouped by domain

5. **Current Advantages Table**
   - Skills where current workspace is ahead
   - Potential reverse-port candidates

6. **Full Parity List**
   - Skills synchronized across workspaces
   - No action needed

#### 3.2 Example Report Format

```markdown
# Assimilation Gap Analysis
**Generated:** 2026-02-14 14:00
**Scanned:** .gemini (45 skills), .claude (38 skills), .agent (75 skills)

## Summary
- Missing skills: 7
- Outdated skills: 3
- Current advantages: 2

## 1. Missing Skills (Port Candidates)
| Skill | Domain | Source | Description |
|-------|--------|--------|-------------|
| presentation-studio | presentation | .gemini | Framework-based slide generation |
```

**Full template:** See [`references/report-templates.md`](references/report-templates.md)

---

### Phase 4: Generate Assimilation Plan

**Objective:** Create actionable implementation plan

#### 4.1 Plan Structure

Generate `outputs/assimilation-plan.md` with:

1. **Priority Actions**
   - High priority items (missing, unique domains)
   - Medium priority items (upgrades)
   - Strategic evaluation items

2. **Action Steps per Skill**
   - Specific porting/upgrade steps
   - Source file paths
   - Integration requirements
   - Testing checklist

3. **Recommended Workflow**
   - Phase-based implementation order
   - Time estimates
   - Dependencies

4. **Post-Assimilation Tasks**
   - Registry updates
   - Validation steps
   - Documentation requirements

#### 4.2 Example Plan Format

```markdown
# Assimilation Plan

## High Priority (Missing Skills)

### 1. Port `presentation-studio` from .gemini
- **Domain:** presentation
- **Action Steps:**
  1. Read `.gemini/skills/presentation-studio/SKILL.md`
  2. Use `skill-creator` to create structure
  3. Adapt content to current workspace
  4. Verify no agent-specific dependencies
  5. Update SKILLS-REGISTRY.md

**Estimated Time:** 20 minutes
```

**Full template:** See [`references/report-templates.md`](references/report-templates.md)

---

## Workflow Examples

### Example 1: Quick Parity Check
**Scenario:** User wants to know if peer workspaces have new skills

```
User: "Check if Gemini has any new skills"

Agent Actions:
1. Scan .gemini/skills/ and current workspace
2. Identify missing skills
3. Generate gap analysis report
4. Present summary with high-priority items

Output:
"Found 3 new skills in Gemini workspace:
- presentation-studio (presentation)
- recursive-lit-review (research)
- consolidate-weekly-report (reporting)

Full analysis saved to: outputs/assimilation-gap-analysis.md"
```

---

### Example 2: Full Workspace Parity
**Scenario:** User wants comprehensive analysis across all workspaces

```
User: "Run an assimilation check across all workspaces"

Agent Actions:
1. Scan .claude/, .gemini/, .codex/, .agent/, current workspace
2. Perform comprehensive gap analysis
3. Generate detailed reports
4. Create actionable assimilation plan

Output:
"Workspace parity analysis complete:
- Scanned 5 workspaces (178 total skills)
- Identified 7 missing skills (high priority)
- Found 3 upgrade opportunities (medium priority)
- Discovered 2 unique domains

Reports generated:
- outputs/assimilation-gap-analysis.md
- outputs/assimilation-plan.md"
```

---

### Example 3: Targeted Scan
**Scenario:** User wants to compare with specific workspace

```
User: "What skills does Codex have that I'm missing?"

Agent Actions:
1. Scan .codex/skills/ only
2. Compare against current workspace
3. Filter for missing skills
4. Generate focused report

Output:
"Codex comparison:
- 12 skills in Codex workspace
- 4 missing from current workspace:
  - code-review-automation (coding)
  - test-generator (testing)
  - refactor-assistant (coding)
  - dependency-analyzer (maintenance)

See outputs/assimilation-gap-analysis.md for details"
```

---

## Output Artifacts

| File | Purpose | When Generated |
|------|---------|----------------|
| `outputs/assimilation-gap-analysis.md` | Raw comparison data with all gaps categorized | Always (Phase 3) |
| `outputs/assimilation-plan.md` | Actionable task list for porting/upgrading | Always (Phase 4) |

Both files are timestamped and can be regenerated on-demand for updated analysis.

---

## Integration Notes

### Post-Analysis Workflow

After generating assimilation reports:

1. **Review with User**
   - Present summary findings
   - Get approval on which skills to port
   - Prioritize based on current needs

2. **Port High-Priority Skills**
   - Use `skill-creator` for structure
   - Adapt peer content to current workspace
   - Verify no agent-specific dependencies

3. **Update Skill Registry**
   - Add newly ported skills to `SKILLS-REGISTRY.md`
   - Update skill counts
   - Add trigger phrases

4. **Validate Changes**
   - Run `validate-skills-standard`
   - Test ported skills
   - Check for broken WikiLinks

5. **Consider Bidirectional Parity**
   - If current workspace has advantages, share with peers
   - Port current improvements to `.agent/skills/` if universal

### Recommended Cadence

- **Quarterly:** Run full assimilation check across all workspaces
- **After major updates:** Scan specific workspace if significant changes announced
- **Before new projects:** Check if relevant domain skills exist in peer workspaces

**Detailed integration workflow:** See [`references/integration-workflow.md`](references/integration-workflow.md)

---

## Related Documentation

- **Dependencies:** [`references/dependencies.md`](references/dependencies.md) - Tools, scan targets, related skills
- **Gap Analysis Methodology:** [`references/gap-analysis-methodology.md`](references/gap-analysis-methodology.md) - Gap types, priorities, skip rules
- **Report Templates:** [`references/report-templates.md`](references/report-templates.md) - Output formats and examples
- **Integration Workflow:** [`references/integration-workflow.md`](references/integration-workflow.md) - Post-analysis implementation steps
