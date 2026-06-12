# Integration Workflow

## Post-Analysis Workflow

After generating gap analysis and assimilation plan, follow this workflow to actually implement the changes.

---

## Phase 1: Review & Approval

### User Review
1. **Present Gap Analysis Report**
   - Show summary statistics
   - Highlight high-priority items
   - Explain recommendations

2. **Get User Approval**
   - Which skills to port?
   - Which upgrades to apply?
   - Which domains to evaluate?
   - Priority order for implementation

3. **Set Expectations**
   - Estimated time per skill
   - Dependencies or blockers
   - Testing requirements

---

## Phase 2: Skill Porting

### For Missing Skills (New Ports)

**Step 1: Read Source**
```
Read peer-workspace/skills/skill-name/SKILL.md
Read peer-workspace/skills/skill-name/README.md
Check for reference files in peer-workspace/skills/skill-name/references/
```

**Step 2: Adapt Content**
- Remove agent-specific features (if any)
- Generalize conversational examples to workflow descriptions
- Update file paths to current workspace
- Verify frontmatter uses strict schema (name + description)

**Step 3: Create Structure**
```
current-workspace/skills/skill-name/
  ├── SKILL.md (main implementation)
  ├── README.md (user-facing docs)
  ├── references/ (if needed)
  └── outputs/ (if skill generates artifacts)
```

**Step 4: Integration**
- Use `skill-creator` for standardized structure (optional)
- Ensure dual-documentation pattern (SKILL.md + README.md)
- Create reference files for complex logic

**Step 5: Validation**
- Run `validate-skills-standard` on new skill
- Verify no hardcoded paths or agent names
- Test basic functionality
- Check WikiLinks resolve

**Step 6: Registry Update**
- Add skill to `SKILLS-REGISTRY.md`
- Include trigger phrases
- Add to appropriate category
- Update skill count

---

### For Outdated Skills (Upgrades)

**Step 1: Compare Versions**
```bash
# Side-by-side comparison
Read current-workspace/skills/skill-name/SKILL.md
Read peer-workspace/skills/skill-name/SKILL.md
```

**Step 2: Identify Changes**
- What features were added?
- What bugs were fixed?
- What documentation improved?
- Are there breaking changes?

**Step 3: Apply Relevant Changes**
- Merge new features (if universal)
- Skip agent-specific additions
- Update documentation
- Increment version number

**Step 4: Test Upgrades**
- Verify existing functionality still works
- Test new features
- Check for regressions
- Validate with standards

**Step 5: Document Changes**
- Update frontmatter version
- Add changelog entry (if skill maintains one)
- Note source of upgrade

---

## Phase 3: Tool Integration

### Skills to Use During Assimilation

#### `skill-creator`
**Use when:** Porting a new skill from scratch

**Invocation:**
```
"Create a new skill called [skill-name] for [purpose]"
```

**Benefits:**
- Standardized structure
- Compliant frontmatter
- Dual-documentation setup

---

#### `validate-skills-standard`
**Use when:** Verifying ported/upgraded skills

**Invocation:** Run the `validate-skills-standard` skill — checklist-driven validation that writes a compliance report to `.agent/outputs/`.

**Benefits:**
- Catches frontmatter violations
- Ensures README.md exists
- Validates structure

---

#### `workspace-optimizer`
**Use when:** After bulk assimilation

**Invocation:**
```
"Run workspace optimization"
```

**Benefits:**
- Updates skill counts
- Fixes broken WikiLinks
- Cleans up orphaned files

---

## Phase 4: Registry Maintenance

### Update SKILLS-REGISTRY.md

**For New Skills:**
```markdown
#### skill-name
**Description:** Brief description
**Triggers:** "trigger phrase", "another phrase"
**Use when:** Specific use cases
**Location:** `./skills/skill-name/`
```

**For Updated Skills:**
- Update version number (if shown)
- Add new trigger phrases (if any)
- Update description (if changed)

---

### Update Category Indices

If workspace maintains category-specific registries:
- Add skills to appropriate domain categories
- Update skill counts per category
- Verify cross-references

---

## Phase 5: Bidirectional Parity

### Share Current Advantages

If current workspace has superior versions:

**Step 1: Identify Reverse-Port Candidates**
- Skills where current version > peer version
- New skills developed in current workspace
- Domain expertise unique to current workspace

**Step 2: Evaluate Portability**
- Is skill universal or current-agent-specific?
- Does peer workspace need this capability?
- Are there dependencies peer lacks?

**Step 3: Coordinate with Peer Workspace**
- Document in peer's assimilation backlog
- Share via `.agent/skills/` if universal
- Consider creating agent-agnostic version

---

## Phase 6: Scheduling & Maintenance

### Recommended Cadence

**Quarterly Assimilation Check:**
```
Run "assimilation check" every 3 months
```

**After Major Peer Updates:**
```
If peer workspace announces major skill releases, run targeted scan
```

**Before Starting New Projects:**
```
Check if peer workspaces have relevant domain skills
```

---

### Maintenance Tasks

**Monthly:**
- [ ] Review assimilation backlog (deferred items)
- [ ] Check for deprecated skills in current workspace

**Quarterly:**
- [ ] Run full assimilation analysis
- [ ] Port high-priority items
- [ ] Share current advantages with peers

**Annually:**
- [ ] Comprehensive skill audit across all workspaces
- [ ] Archive obsolete skills
- [ ] Evaluate strategic domain coverage

---

## Troubleshooting

### Common Issues

**Issue:** Skill has agent-specific dependencies
**Solution:** Create universal adapter or skip porting

**Issue:** Version comparison fails (non-semantic versioning)
**Solution:** Use manual review, document discrepancy

**Issue:** Skill exists in multiple peer workspaces with different versions
**Solution:** Port the highest version, note in analysis report

**Issue:** Ported skill fails validation
**Solution:** Review frontmatter, file structure, fix compliance issues

---

## Best Practices

### Before Porting
- [ ] Read source skill completely
- [ ] Understand purpose and workflow
- [ ] Check for agent-specific features
- [ ] Verify dependencies are available

### During Porting
- [ ] Maintain dual-documentation pattern
- [ ] Use strict frontmatter schema
- [ ] Generalize agent-specific content
- [ ] Test incrementally

### After Porting
- [ ] Validate with standards
- [ ] Update registry immediately
- [ ] Document porting decisions
- [ ] Test end-to-end functionality

### Quality Gates
- [ ] No hardcoded agent names or paths
- [ ] README.md exists and is comprehensive
- [ ] Frontmatter uses strict schema
- [ ] All WikiLinks resolve
- [ ] Skill passes validation script
