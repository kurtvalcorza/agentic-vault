# Validate Workflow State

Diagnose and repair interrupted multi-phase orchestrator workflows.

## When to Use
- Workflow crashed mid-execution
- Unsure which phase completed
- Output files missing or corrupted
- Need to resume long-running process

## What It Does
1. Checks execution logs for phase completion
2. Verifies output file existence and integrity
3. Validates phase dependencies
4. Suggests recovery options

## Supported Workflows
- Literature Review (search → screen → extract → synthesize)
- Slide Generation (brief → outline → draft → render)
- Meeting Synthesis (transcribe → summarize → report)
- Any multi-phase orchestrator pattern

## Recovery Options

**Auto-Repair**
- Resume from last successful phase
- Regenerate missing outputs
- Skip completed phases

**Manual Fix**
- Detailed diagnostic report
- Step-by-step recovery guide
- File-level issue identification

**Restart**
- Clean slate option
- Preserves logs for analysis

## Quick Start
Just say: **"Validate workflow state for [workflow-name]"**

## Output Location
Diagnostic reports saved to `.agent/outputs/workflow-diagnostics/`

## Works With
- `compile-wiki` - Multi-phase wiki compilation
- `optimize-workspace` - 5-phase workspace audit
- `assimilate-skills` - Multi-phase skill integration
- All multi-phase orchestrators
