---
name: visualize-vault
description: "Generate a visual map of the vault's link structure as an Obsidian JSON Canvas file, showing hub nodes, orphans, clusters, and the overall shape of the knowledge graph. Use when asked to visualize my vault, show vault topology, map [topic] connections, or generate a vault atlas."
---

# visualize-vault

Generates a visual map of your vault's link structure as a JSON Canvas file that opens natively in Obsidian's canvas viewer. The map shows every note as a node and every WikiLink as an edge, color-coded by PARA directory, with hub nodes, orphans, clusters, and bridge nodes highlighted for quick topology analysis.

## When to Use

- You want to see the overall shape of your knowledge graph
- You're looking for orphan notes that aren't connected to anything
- You want to identify hub notes that connect many areas of your vault
- You need to understand how a specific topic connects to the rest of your vault
- You're doing a vault health check and want a visual overview of link density

## Invocation

### Full Vault

```
Visualize my vault
Show vault topology
Generate a vault atlas
```

Scans all Markdown files across the vault and generates a complete link map.

### Scoped View

```
Map Project Atlas connections
Visualize the Project Cedar project
Show topology for science communication
```

Starts from the matching note and follows WikiLinks 2 levels deep, producing a focused neighborhood map.

## Layout: Grid-by-PARA

The canvas uses a quadrant layout based on the PARA directory structure:

```
┌─────────────────────┐  ┌─────────────────────┐
│   01_Projects/      │  │   02_Areas/          │
│   (green)           │  │   (cyan/blue)        │
│                     │  │                      │
│   Top-left          │  │   Top-right          │
└─────────────────────┘  └─────────────────────┘

┌─────────────────────┐  ┌─────────────────────┐
│   03_Resources/     │  │   04_Archives/       │
│   (orange)          │  │   (default)          │
│                     │  │                      │
│   Bottom-left       │  │   Bottom-right       │
└─────────────────────┘  └─────────────────────┘
```

Within each quadrant, nodes are arranged in a grid sorted by connection count (most-connected first). Hub nodes — the top 10% by connections — get a dedicated top row with larger dimensions for visibility.

### Color Coding

| Color | Meaning |
|:------|:--------|
| Green (preset 4) | Projects (`01_Projects/`) |
| Cyan/Blue (preset 5) | Areas (`02_Areas/`) |
| Orange (preset 2) | Resources (`03_Resources/`) |
| Default (no color) | Archives (`04_Archives/`) |
| Purple (preset 6) | Concept Hub notes |
| Red (preset 1) | Orphan nodes (0 connections) |

Orphan nodes stay in their PARA quadrant but are colored red so you can spot them immediately.

## Output

### Canvas File

- Full scope: `.agent/outputs/vault-atlas.canvas`
- Scoped: `.agent/outputs/vault-atlas-{topic}.canvas`

Open the `.canvas` file in Obsidian to explore the interactive map. You can zoom, pan, and click on any node to open the underlying note.

### Text Summary

Alongside the canvas, you get a text summary with:
- Total node and edge counts
- Top 5 hub nodes by connection count
- All orphan nodes
- Identified clusters and their sizes
- Bridge nodes connecting clusters
- Broken link count (WikiLinks to non-existent notes)

## Tips

### Organizing Canvases

If you regenerate the vault atlas frequently, consider creating a `Maps/` folder in your vault root and symlinking or moving canvases there for easy access:

```
Maps/
  vault-atlas.canvas          ← full vault map
  vault-atlas-atlas.canvas    ← Project Atlas neighborhood
  vault-atlas-cedar.canvas   ← Project Cedar neighborhood
```

This keeps your atlas files discoverable in Obsidian's file explorer without cluttering `.agent/outputs/`.

### Large Vaults

For vaults with 300+ Markdown files, the skill warns you before generating a full canvas. Large canvases can be slow to render in Obsidian. Scoped views are recommended for day-to-day exploration — save the full atlas for periodic vault health checks.

### Reading the Map

- **Large nodes at the top of each quadrant** are your hub notes — the most connected notes in that PARA category
- **Red nodes** are orphans — consider linking them to related notes or archiving them
- **Purple nodes** are concept hubs — these are your knowledge anchors
- **Bridge nodes** (listed in the summary) are structurally important — they connect otherwise separate clusters

## Error Handling

| Scenario | Behavior |
|:---------|:---------|
| No matching notes for scoped view | Reports the miss and exits |
| Empty vault / no Markdown files | Reports and exits |
| 300+ files in full scope | Warns and offers scoped alternative |
| Broken WikiLinks | Omitted from canvas, counted in summary |
| Circular WikiLinks | Handled via visited-node tracking |

## Prerequisites

| Dependency | Path | Purpose |
|:-----------|:-----|:--------|
| JSON Canvas skill | `.agent/skills/json-canvas/SKILL.md` | Canvas format reference |
| Vault content directories | `01_Projects/`, `02_Areas/`, `03_Resources/`, `04_Archives/` | Notes to visualize |
| Output directory | `.agent/outputs/` | Where canvas files are saved |
| Session log directory | `System/session-logs/YYYY-MM-DD/` | Activity logging |

## Related Skills

- `connect-domains` — Discovers connections between two specific topics (complementary for targeted bridging)
- `reconcile-vault` — Detects contradictions across vault notes (use after spotting suspicious clusters)
- `extract-concepts` — Discovers recurring concepts and generates concept hub pages (feeds into concept hub coloring)
- `optimize-workspace` — General vault health checks (complementary for maintenance workflows)
- `query-vault` — Q&A against vault content (use to investigate specific nodes or clusters)
