# Gap Analysis Methodology

## Gap Type Definitions

### 1. Missing Skills
**Condition:** Skill exists in peer workspace but not in current workspace

**Priority:** **High**

**Criteria:**
- Peer workspace has skill with unique `name`
- No equivalent skill exists in current workspace
- Skill status is `active` (not deprecated/experimental)

**Action:** Consider porting skill to current workspace

---

### 2. Outdated Skills
**Condition:** Peer workspace has newer version of existing skill

**Priority:** **Medium**

**Criteria:**
- Skill exists in both workspaces
- Peer `version` > Current `version`
- Skill status is `active`

**Action:** Review peer changes and consider upgrading

---

### 3. Unique Domain Skills
**Condition:** Peer workspace has skill in domain not covered by current workspace

**Priority:** **High**

**Criteria:**
- Peer skill's `domain` doesn't exist in current workspace's skill inventory
- Represents new capability category
- Skill status is `active`

**Action:** Consider strategic domain expansion

---

## Priority Matrix

| Gap Type | Condition | Priority | Recommended Action |
|----------|-----------|----------|-------------------|
| **Missing** | Skill exists in peer, not in current | **High** | Port immediately if domain-relevant |
| **Outdated** | Peer version > Current version | **Medium** | Review changes, upgrade if significant improvements |
| **Unique Domain** | Peer has domain not in current | **High** | Evaluate strategic fit before porting |
| **Parity** | Versions match | **Low** | No action needed |
| **Current Advantage** | Current version > Peer version | **Info** | Consider reverse-porting to peer |

---

## Skip Rules

### Excluded from Analysis

**1. Deprecated Skills**
- Any skill with `status: deprecated`
- Rationale: Skill is being phased out

**2. Experimental Skills**
- Any skill with `status: experimental`
- Rationale: Not production-ready, likely unstable

**3. Agent-Specific Skills**
- Skills with agent-specific triggers or behaviors
- Example: Claude's "provocation mode" features
- Rationale: Not portable across agents

**4. Archived Skills**
- Skills in `_archived/` directories
- Rationale: No longer maintained

---

## Comparison Logic

### Version Comparison
```
Parse version as semantic version (major.minor.patch)
If peer_version > current_version:
  Flag as "Outdated"
If peer_version == current_version:
  Flag as "Parity"
If peer_version < current_version:
  Flag as "Current Advantage"
```

### Domain Coverage Analysis
```
Extract all unique domains from current workspace
For each peer skill:
  If skill.domain NOT IN current_domains:
    Flag as "Unique Domain"
```

### Missing Skill Detection
```
Extract all skill names from current workspace
For each peer skill:
  If skill.name NOT IN current_names:
    AND skill.status == "active":
      Flag as "Missing"
```

---

## Quality Filters

### Before Recommending Port

**Verify:**
- [ ] Skill has complete documentation (SKILL.md + README.md)
- [ ] Frontmatter uses standard schema
- [ ] No agent-specific dependencies
- [ ] Domain aligns with current workspace focus
- [ ] Skill is actively maintained (recent updates)

**Red Flags:**
- Missing README.md
- Hardcoded paths or agent names
- Unclear purpose or description
- Experimental status
- No recent updates (>6 months old)
