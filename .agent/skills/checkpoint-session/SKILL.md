---
name: checkpoint-session
description: Manually log a session checkpoint with goals, actions, decisions, and next steps for cross-device continuity. Use when saving progress at a milestone, switching devices, or creating a manual session checkpoint.
---

# Checkpoint Session

## Purpose
Capture important session milestones with context for resuming work across devices. Use when completing major tasks, making key decisions, or before switching devices.

## Trigger Phrases
- "checkpoint session"
- "log this session"
- "save session state"
- "create checkpoint"

## Input Requirements
- **Goal** (required): What you're trying to accomplish
- **Status** (required): Current state (completed, in-progress, blocked, paused)
- **Key Actions** (optional): Major operations performed
- **Decisions** (optional): Important choices made
- **Next Steps** (optional): What to do when resuming

## Process

### 1. Gather Session Context
Ask user for:
- Primary goal/objective
- Current status
- Skills/tools used
- Key actions taken
- Important decisions made
- Next steps

### 2. Detect Session Artifacts
Scan for recent changes:
- Files modified in last 2 hours
- Outputs in `.agent/outputs/`
- Skills invoked (if trackable)

### 3. Update Session Log
- Create or access folder `System/session-logs/YYYY-MM-DD/`
- Create new log file with timestamp: `HH-MM-SS_brief-description.md`
- Include all gathered information concisely
- Format as structured markdown with clear sections
- Link to relevant outputs

### 4. Confirm Checkpoint
- Show summary of logged information
- Confirm file location
- Suggest next steps if provided

## Output Format

```markdown
## Session N (HH:MM - HH:MM)
**Goal**: [Primary objective]
**Status**: [emoji] [Status text]
**Skills Used**: [skill-1, skill-2]
**Tools Used**: [tool-1, tool-2]
**Files Modified**: 
- [file paths]
**Outputs**: 
- [output paths]
**Key Actions**:
- [action items]
**Decisions**: 
- [key decisions]
**Next Steps**: 
- [next actions]
```

## Error Handling
- If session log doesn't exist, create it with proper header
- If user provides minimal info, infer from recent file activity
- If no changes detected, log as planning/discussion session
- Handle missing timestamps gracefully

## Safety Considerations
- Never overwrite existing session entries
- Always append to daily log file
- Preserve all previous session data
- Use UTC or local time consistently

## Example Usage

**User**: "checkpoint session"

**Agent**: 
1. Asks for goal, status, and key details
2. Scans for recent file changes
3. Creates new log file in `System/session-logs/2026-02-08/14-30-45_session-checkpoint.md`
4. Confirms: "Session checkpoint saved. You can resume from any device by checking today's session log folder."

## Integration Points
- Works with auto-logging hook for complete session history
- References outputs from other skills
- Links to project files in `01_Projects/`
- Connects to daily notes in `Journal/`
