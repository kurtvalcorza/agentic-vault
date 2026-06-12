---
name: validate-workflow-state
description: "Diagnose and repair corrupted or interrupted orchestrator workflows. Use when a research workflow stalled mid-run, logs show errors, or you need to resume an interrupted orchestration pipeline."
---








# Validate Workflow State: Diagnosis & Repair

## Dependencies

### Required Skills
- None (Utility)

### Required Tools
- `file-read` - Read logs and state files.
- `file-write` - Generate diagnostic report.
- `file-search` - Check for output files.

### Phase Dependencies
- **Phase 1** -> **Phase 2** -> **Phase 3** -> **Phase 4**

### Input Files
- Workflow state files (e.g., `STAGING.md`, `execution.log`, `synthesis-matrix.md`)

### Output Directories
- `.agent/outputs/`

---

## Purpose
Diagnose and help users recover from corrupted or interrupted multi-phase orchestrator workflows (e.g., Review Literature, Generate Slides).

## What You Diagnose

**Execution Log Integrity:**
- JSON validation for state files (if applicable)
- Phase completion status verification
- Timestamp consistency checks

**Output File Existence:**
- Check if expected phase outputs exist (e.g., `STAGING.md` for Slides)
- Verify file integrity (not empty, valid format)
- Detect missing intermediate files

**Phase Dependency Validation:**
- Ensure Phase N-1 completed before Phase N
- Check dependency files exist
- Verify phase order compliance

## Diagnostic Report Format

```markdown
# Workflow State Diagnostic - [Workflow Name] - [Date]

## Status: ❌ Corrupted | ⚠️ Incomplete | ✅ Healthy

## Phase Completion Status
- ✅ Phase 0: Discovery (completed)
- ✅ Phase 1: Synthesis (completed)
- ❌ Phase 2: Interrogation (MISSING OUTPUT FILE)
- ⬜ Phase 3: Drafting (not started)

## Output Files Check
- ✅ STAGING.md exists (valid)
- ❌ presentation.md MISSING

## Recommended Recovery

**Option 1: Auto-Repair (Recommended)**
- Re-run Phase 2 using existing STAGING.md

**Option 2: Manual Fix**
- Create presentation.md manually

**Option 3: Restart Workflow**
- Clear working directory and restart
```

## Report Output

Save to: `.agent/outputs/YYYY-MM-DD_Workflow-Diagnostic.md`


## Internal Metadata
- **color**: grey
- **tags**: [utility, maintenance, diagnosis, recovery]
- **domain**: maintenance
- **status**: active
- **version**: 1.0
- **created**: 2026-01-16
- **updated**: 2026-01-16