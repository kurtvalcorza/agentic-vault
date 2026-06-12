# Report Templates

## Gap Analysis Report Template

**Filename:** `outputs/assimilation-gap-analysis.md`

```markdown
# Assimilation Gap Analysis
**Generated:** YYYY-MM-DD HH:MM
**Scanned Workspaces:**
- .claude (N skills)
- .gemini (N skills)
- .codex (N skills)
- .agent (N skills)
- [current-workspace] (N skills)

---

## Summary

| Metric | Count |
|--------|-------|
| Missing skills (High Priority) | N |
| Outdated skills (Medium Priority) | N |
| Unique domain skills (High Priority) | N |
| Current advantages | N |
| Full parity | N |
| **Total analyzed** | **N** |

---

## 1. Missing Skills (Port Candidates)

**Priority:** High
**Action:** Consider porting to current workspace

| Skill | Domain | Source | Description |
|-------|--------|--------|-------------|
| skill-name | domain | .gemini | Brief description of functionality |
| another-skill | coding | .codex | Brief description |

---

## 2. Outdated Skills (Upgrade Candidates)

**Priority:** Medium
**Action:** Review peer changes and upgrade if significant

| Skill | Current Ver | Peer Ver | Source | Status |
|-------|-------------|----------|--------|--------|
| skill-name | 1.0 | 1.2 | .claude | 2 versions behind |
| another-skill | 2.1 | 2.3 | .gemini | Minor update available |

---

## 3. Unique Domain Skills (Strategic Candidates)

**Priority:** High
**Action:** Evaluate strategic fit before porting

| Skill | Domain | Source | Description |
|-------|--------|--------|-------------|
| new-domain-skill | video-editing | .gemini | First skill in new domain |

---

## 4. Current Advantages (Reverse-Port Candidates)

**Priority:** Info
**Action:** Consider sharing with peer workspaces

| Skill | Current Ver | Peer Ver | Advantage |
|-------|-------------|----------|-----------|
| skill-name | 2.0 | 1.5 | 5 versions ahead |

---

## 5. Full Parity (No Action Needed)

| Skill | Version | Status |
|-------|---------|--------|
| skill-name | 1.0 | In sync across all workspaces |
| another-skill | 2.5 | In sync |

---

## Recommendations

### Immediate Actions (High Priority)
1. Port missing skills: [list skill names]
2. Evaluate unique domain skills: [list skill names]

### Planned Actions (Medium Priority)
1. Upgrade outdated skills: [list skill names]

### Optional Actions
1. Share advantages with peer workspaces: [list skill names]
```

---

## Assimilation Plan Template

**Filename:** `outputs/assimilation-plan.md`

```markdown
# Assimilation Plan
**Generated:** YYYY-MM-DD HH:MM
**Based on:** assimilation-gap-analysis.md (YYYY-MM-DD)

---

## Priority Actions

### High Priority (Missing Skills)

#### 1. Port `skill-name` from .gemini
- **Domain:** domain-name
- **Description:** Brief description of skill
- **Action Steps:**
  1. Read `.gemini/skills/skill-name/SKILL.md`
  2. Invoke `skill-creator` to create structure in current workspace
  3. Adapt content to current workspace conventions
  4. Verify no agent-specific dependencies
  5. Test functionality
  6. Update SKILLS-REGISTRY.md

**Source:** `.gemini/skills/skill-name/`

---

#### 2. Port `another-skill` from .codex
- **Domain:** coding
- **Description:** Brief description
- **Action Steps:** [same pattern as above]

**Source:** `.codex/skills/another-skill/`

---

### Medium Priority (Upgrades)

#### 1. Upgrade `skill-name` from v1.0 to v1.2
- **Source:** .claude
- **Changes:** [Review peer version for changelog]
- **Action Steps:**
  1. Read `.claude/skills/skill-name/SKILL.md`
  2. Identify new features in v1.2
  3. Apply relevant changes to current workspace version
  4. Update version number in frontmatter
  5. Test functionality
  6. Document changes

**Source:** `.claude/skills/skill-name/`

---

### Strategic Evaluation (Unique Domains)

#### 1. Evaluate `new-domain-skill` (video-editing)
- **Source:** .gemini
- **Domain:** New domain not currently covered
- **Questions to Answer:**
  - [ ] Does this domain align with current workspace focus?
  - [ ] Are there dependencies or tools we don't have?
  - [ ] Is this a strategic capability we want?
  - [ ] Can we maintain this skill long-term?

**Decision:** [ ] Port / [ ] Defer / [ ] Reject

---

## Recommended Workflow

### Phase 1: High Priority Ports
1. Review this plan with user for approval
2. Port missing skills one at a time
3. Test each ported skill thoroughly
4. Update SKILLS-REGISTRY.md after each port

**Estimated Time:** X hours (assuming Y minutes per skill)

---

### Phase 2: Medium Priority Upgrades
1. Review peer changes for each outdated skill
2. Determine if upgrade is worthwhile
3. Apply changes incrementally
4. Test after each upgrade

**Estimated Time:** X hours

---

### Phase 3: Strategic Evaluation
1. Discuss unique domain skills with user
2. Make strategic decisions on domain expansion
3. Port approved skills
4. Document decisions for future reference

**Estimated Time:** X hours (includes evaluation time)

---

## Post-Assimilation Tasks

- [ ] Update SKILLS-REGISTRY.md with new/upgraded skills
- [ ] Run `validate-skills-standard` on all modified skills
- [ ] Document porting decisions (what was ported, what was deferred, why)
- [ ] Consider bidirectional parity (share current advantages with peers)
- [ ] Schedule next assimilation check (recommended: quarterly)

---

## Notes

- Some skills may require adaptation for current workspace
- Test thoroughly before marking as complete
- Document any issues encountered during porting
- Update this plan as work progresses
```

---

## Output Format Guidelines

### Table Formatting
- Use markdown tables with proper alignment
- Keep descriptions concise (1-2 sentences)
- Include source workspace for traceability

### Priority Indicators
- **High Priority:** 🔴 or **[HIGH]**
- **Medium Priority:** 🟡 or **[MEDIUM]**
- **Low Priority:** 🟢 or **[LOW]**
- **Info Only:** ℹ️ or **[INFO]**

### Version Notation
- Use semantic versioning: `major.minor.patch`
- Show clear comparison: "1.0 → 1.2" or "2 versions behind"

### Actionable Language
- Use imperative mood: "Port skill", "Upgrade version", "Review changes"
- Include specific next steps
- Provide file paths for traceability
