# Checkpoint Session

Manually log session milestones for cross-device work continuity.

## When to Use
- Completing a major task
- Making important decisions
- Before switching devices
- End of work session
- After significant progress

## What It Does
1. Captures your current goal and status
2. Detects recent file changes and outputs
3. Logs skills/tools used
4. Records key actions and decisions
5. Notes next steps for resuming

## Quick Start
Just say: **"checkpoint session"**

The agent will guide you through capturing the essential details.

## Output Location
`System/session-logs/YYYY-MM-DD/HH-MM-SS_description.md`

Each session creates a separate log file in the daily folder for granular tracking.

## Works With
- Auto-logging hook (for automatic tracking)
- All other skills (references their outputs)
- Project files and daily notes

## Example
```
You: "checkpoint session"

Agent: "What was your main goal this session?"
You: "Fix skill validation issues"

Agent: "Current status?"
You: "Completed - 98% production ready"

[Agent logs everything and confirms]
```

Your session is now documented for easy resumption from any device.
