---
name: visualize-vault
description: "Generate a visual map of the vault's link structure as an Obsidian JSON Canvas file, showing hub nodes, orphans, clusters, and the overall shape of the knowledge graph. Use when asked to visualize my vault, show vault topology, map [topic] connections, or generate a vault atlas."
---

# visualize-vault

Generates a visual map of the vault's link structure as a JSON Canvas file compatible with Obsidian's native canvas viewer. Reads vault notes and WikiLinks to build a Link_Graph, then renders it as a grid-by-PARA layout with color-coded nodes, hub identification, orphan highlighting, and cluster detection. Outputs a `.canvas` file to `.agent/outputs/` and a text summary with topology statistics.

## Trigger Phrases

- "Visualize my vault"
- "Show vault topology"
- "Map [topic] connections"
- "Generate a vault atlas"
- "Show me the link structure"
- "Create a canvas map of my vault"

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| scope | No | `"full"` | `"full"` for entire vault, or a topic/project/entity name for a scoped view |

---

## Step 0 — Determine Scope

If no argument is provided, default to `"full"` scope.

If an argument is provided that is not `"full"`, treat it as a scoped view — the argument is the topic, project, or entity name to center the visualization on.

---

## Step 1 — Build Link Graph

### Step 1.1 — Full Scope: Read All Markdown Files

When scope is `"full"`:

```
**Tool:** file-search
Find all `.md` files across `01_Projects/`, `02_Areas/`, `03_Resources/`, `04_Archives/`, `Inbox/`.
```

```
**Tool:** file-read
Read each file and extract all `[[WikiLink]]` targets from the body and frontmatter.
```

Build the complete Link_Graph: each Markdown file is a node, each WikiLink from file A to file B is a directed edge.

**Large Vault Warning**: If the full scope contains **300 or more** Markdown files:

```
**Tool:** user-interact
"Your vault contains {N} Markdown files. A full canvas at this scale may be
large and slow to render in Obsidian.

Would you like to:
  1. Continue with the full vault visualization
  2. Generate a scoped view instead (provide a topic or project name)"
```

If the user chooses a scoped view, prompt for a topic and proceed to Step 1.2.

### Step 1.2 — Scoped: Follow WikiLinks 2 Levels Deep

When scope is a topic/project/entity name:

```
**Tool:** file-search
Find `.md` files matching the scope argument by filename.
```

```
**Tool:** content-search
Search for the scope argument across vault files by content and tags.
```

Select the best matching note as the **seed note**. If multiple matches exist, prefer exact title matches over content matches.

**If no matching note is found:**

Report: "No matching notes found for '{scope}'. Try a different topic or use 'full' scope."

Log to session log and exit gracefully.

**Hop 1**: Read the seed note. Extract all `[[WikiLink]]` targets. Read each linked note and add it to the graph.

```
**Tool:** file-read
Read each WikiLink target note.
```

**Hop 2**: For each hop-1 note, extract its WikiLinks and read those targets. Add them to the graph.

**Cycle Prevention**: Maintain a visited-node set. If a note has already been visited, skip it. This prevents infinite loops from circular WikiLinks.

### Step 1.3 — Resolve WikiLinks and Identify Broken Links

For each WikiLink target in the graph:
- If the target file exists in the vault → create an edge in the Link_Graph
- If the target file does NOT exist → **omit** from the canvas (no node, no edge), but increment the broken link counter

### Step 1.4 — Handle Empty Graph

If the Link_Graph contains **0 nodes** after processing:

Report: "No Markdown files found in scan scope. Cannot generate canvas."

Log to session log and exit gracefully.

---

## Step 2 — Classify Nodes

### Step 2.1 — Assign PARA Type

Classify each node by its file path:

| Path Prefix | PARA Type | Quadrant | Color Preset |
|:------------|:----------|:---------|:-------------|
| `01_Projects/` | Project | Top-left | `"4"` (green) |
| `02_Areas/` | Area | Top-right | `"5"` (cyan/blue) |
| `03_Resources/` | Resource | Bottom-left | `"2"` (orange) |
| `04_Archives/` | Archive | Bottom-right | _(no preset — default appearance)_ |
| Other (e.g., `Inbox/`, `System/`) | Resource | Bottom-left | `"2"` (orange) |

Notes outside the four PARA directories are placed in the Resources quadrant (bottom-left) as a sensible default.

### Step 2.2 — Compute Connection Counts

For each node, compute:
- **Inbound connections**: count of edges where this node is the target
- **Outbound connections**: count of edges where this node is the source
- **Total connections**: inbound + outbound

### Step 2.3 — Identify Hub Nodes

Hub_Nodes are the **top 10%** of nodes by total connection count.

Calculate: `hub_threshold = ceil(total_node_count * 0.10)`

Sort all nodes by total connection count descending. The top `hub_threshold` nodes are Hub_Nodes.

If all nodes have 0 connections, there are no Hub_Nodes.

### Step 2.4 — Identify Orphan Nodes

Orphan_Nodes are nodes with **0 total connections** (no inbound and no outbound edges).

### Step 2.5 — Identify Concept Hubs

A node is a Concept_Hub if its file path is within a concept hub directory or if its frontmatter contains `tags` including `concept` or `concept-hub`. Concept_Hubs receive the purple color preset `"6"`.

**Color priority**: Concept_Hub purple (`"6"`) overrides the PARA color. Orphan red (`"1"`) overrides both Concept_Hub and PARA colors. This ensures orphans are always visually distinct.

### Step 2.6 — Identify Clusters and Bridge Nodes

**Clusters**: Groups of nodes that are densely interconnected. Use connected component analysis on the undirected version of the Link_Graph. Each connected component with 2+ nodes is a Cluster.

**Bridge_Nodes**: Nodes that, if removed, would split a Cluster into two or more disconnected components (articulation points). These are structurally important connectors in the knowledge graph.

---

## Step 3 — Generate JSON Canvas

### Step 3.1 — Generate Node IDs

For each node, generate a deterministic 16-character lowercase hex ID:

1. Take the relative file path of the note (e.g., `01_Projects/Project Atlas/overview.md`)
2. Compute the MD5 hash of the path string
3. Take the first 16 characters of the hex digest

This ensures stable IDs across runs, making canvas diffs meaningful.

### Step 3.2 — Compute Grid-by-PARA Layout

For each PARA quadrant, compute the layout independently:

**Quadrant origins** (in canvas coordinates):

| Quadrant | Origin X | Origin Y |
|:---------|:---------|:---------|
| Top-left (Projects) | 0 | 0 |
| Top-right (Areas) | quadrant_width + 600 | 0 |
| Bottom-left (Resources) | 0 | quadrant_height + 600 |
| Bottom-right (Archives) | quadrant_width + 600 | quadrant_height + 600 |

The 600px gap between quadrants provides visual separation.

**Within each quadrant:**

1. Separate nodes into Hub_Nodes and non-hub nodes
2. Sort both groups by total connection count descending

**Hub_Node row** (top of quadrant):
- Hub_Nodes are placed in a dedicated top row
- Dimensions: **400×100** per hub node
- Horizontal spacing: 300px between hub nodes
- Y position: quadrant origin Y

**Non-hub node grid** (below hub row):
- Columns = `ceil(sqrt(non_hub_node_count))`
- Column spacing: 300px
- Row spacing: 300px
- Dimensions: **250×60** per non-hub node
- Y offset: quadrant origin Y + (hub_row_height + 200 if hubs exist, else 0)
- Nodes fill left-to-right, top-to-bottom

### Step 3.3 — Apply Colors

For each node, determine the `color` field:

1. If the node is an **Orphan_Node** → `"1"` (red)
2. Else if the node is a **Concept_Hub** → `"6"` (purple)
3. Else apply PARA color:
   - Projects → `"4"` (green)
   - Areas → `"5"` (cyan/blue)
   - Resources → `"2"` (orange)
   - Archives → _(omit color field — default appearance)_

### Step 3.4 — Build Canvas JSON

Construct the JSON Canvas object:

```json
{
  "nodes": [
    {
      "id": "{16-char-hex}",
      "type": "file",
      "file": "{relative-path-to-note}",
      "x": {computed_x},
      "y": {computed_y},
      "width": {250 or 400},
      "height": {60 or 100},
      "color": "{preset or omitted for archives}"
    }
  ],
  "edges": [
    {
      "id": "{16-char-hex}",
      "fromNode": "{source-node-id}",
      "toNode": "{target-node-id}"
    }
  ]
}
```

**Edge IDs**: Generate a deterministic 16-character lowercase hex ID for each edge by hashing the concatenation of `fromNode` path + `→` + `toNode` path, then taking the first 16 characters of the MD5 hex digest.

**Validation before writing**:
- All node IDs are unique
- All edge IDs are unique
- All edge `fromNode`/`toNode` values reference existing node IDs
- No edges reference broken links (already filtered in Step 1.3)

### Step 3.5 — Save Canvas File

Determine the output path:
- Full scope: `.agent/outputs/vault-atlas.canvas`
- Scoped: `.agent/outputs/vault-atlas-{scope}.canvas` (scope name lowercased, spaces replaced with hyphens)

```
**Tool:** file-write
Write the JSON Canvas to the output path.
```

---

## Step 4 — Generate Text Summary

Produce a text summary alongside the canvas:

```
## Vault Atlas — {scope}

**Generated:** {YYYY-MM-DD}
**Canvas:** `.agent/outputs/{filename}.canvas`

### Statistics
- **Total nodes:** {count}
- **Total edges:** {count}
- **Broken links (omitted):** {count}

### Top 5 Hub Nodes
| Rank | Note | Connections (In/Out) |
|------|------|---------------------|
| 1 | [[{note}]] | {in}/{out} ({total}) |
| 2 | [[{note}]] | {in}/{out} ({total}) |
| 3 | [[{note}]] | {in}/{out} ({total}) |
| 4 | [[{note}]] | {in}/{out} ({total}) |
| 5 | [[{note}]] | {in}/{out} ({total}) |

### Orphan Nodes ({count})
{List all orphan nodes, or "None detected" if empty}

### Clusters ({count})
{List each cluster with its node count and representative notes}

### Bridge Nodes ({count})
{List bridge nodes that connect clusters, or "None detected" if empty}
```

Present this summary in the chat response.

---

## Step 5 — Session Log

Log the visualization activity to `System/session-logs/{YYYY-MM-DD}/`:

- Skill invoked: `visualize-vault`
- Scope: `{full or topic name}`
- Total files scanned: `{count}`
- Nodes in canvas: `{count}`
- Edges in canvas: `{count}`
- Broken links omitted: `{count}`
- Hub nodes: `{count}` (list top 5)
- Orphan nodes: `{count}`
- Clusters: `{count}`
- Bridge nodes: `{count}`
- Canvas saved to: `{output path}`
- Outcome: generated / empty graph / user chose scoped view

If the session log directory does not exist, create `System/session-logs/{YYYY-MM-DD}/` first.

---

## Required Capabilities

| Capability | Usage |
|:-----------|:------|
| `file-read` | Read vault notes, extract WikiLinks, follow links for scoped views |
| `file-search` | Find `.md` files across vault directories |
| `content-search` | Search for topic keywords when building scoped views |
| `file-write` | Save the generated JSON Canvas file to `.agent/outputs/` |
| `user-interact` | Large vault warnings, scope selection, no-match prompts |

### Referenced Policies

| Policy | Path | Purpose |
|:-------|:-----|:--------|
| JSON Canvas Spec | `.agent/skills/json-canvas/SKILL.md` | Canvas format reference (node types, edge format, color presets) |
| Skills standard | `.agent/steering/skills-standard.md` | Directory structure and frontmatter requirements |

---

## Error Handling

| Scenario | Action |
|:---------|:-------|
| No matching notes for scoped view | Report "no matching notes found for '{scope}'" and exit gracefully |
| 0 nodes after processing | Report "no Markdown files found in scan scope" and exit gracefully |
| Circular WikiLinks | Track visited nodes in a set; skip already-visited nodes to prevent infinite loops |
| WikiLink target does not exist | Omit from canvas (no node, no edge); increment broken link counter for summary |
| Full scope ≥ 300 files | Warn user via `user-interact`; offer scoped view alternative |
| File read failure (permissions, encoding) | Log warning, skip the file, continue processing |
| Malformed YAML frontmatter | Log warning, skip frontmatter parsing for that file, still include as node |
| Session log directory missing | Create `System/session-logs/{YYYY-MM-DD}/` directory, then log |
| Vault directory missing (e.g., `01_Projects/` doesn't exist) | Skip that directory, log warning, continue with available directories |

---

## Examples

### Full Vault Visualization

**User:** Visualize my vault.

**Agent:**
1. Scanning vault for Markdown files...
   - Found 187 files across 4 PARA directories + Inbox
2. Building link graph...
   - 187 nodes, 423 edges, 12 broken links omitted
3. Classifying nodes...
   - 19 Hub Nodes (top 10%), 8 Orphan Nodes, 6 Clusters
4. Generating canvas...

## Vault Atlas — full

**Generated:** 2026-04-05
**Canvas:** `.agent/outputs/vault-atlas.canvas`

### Statistics
- **Total nodes:** 187
- **Total edges:** 423
- **Broken links (omitted):** 12

### Top 5 Hub Nodes
| Rank | Note | Connections (In/Out) |
|------|------|---------------------|
| 1 | [[Project Atlas Overview]] | 18/12 (30) |
| 2 | [[Example Org]] | 22/5 (27) |
| 3 | [[Project Cedar]] | 15/9 (24) |
| 4 | [[Project Beacon]] | 11/8 (19) |
| 5 | [[the vault owner]] | 14/3 (17) |

### Orphan Nodes (8)
- [[Stale Draft Note]]
- [[Untitled Inbox Capture]]
- [[Old Meeting Notes 2024-01]]
- ... (5 more)

### Clusters (6)
- Project Atlas cluster: 45 notes (centered on [[Project Atlas Overview]])
- Project Cedar cluster: 32 notes (centered on [[Project Cedar]])
- ... (4 more)

### Bridge Nodes (3)
- [[Example Org]] — connects Project Atlas cluster ↔ Project Cedar cluster
- [[the funding agency]] — connects Project Cedar cluster ↔ Policy cluster
- [[the vault owner]] — connects Project Atlas cluster ↔ Professional cluster

Canvas saved to `.agent/outputs/vault-atlas.canvas`. Open it in Obsidian to explore the interactive map.

### Scoped Visualization

**User:** Map Project Atlas connections.

**Agent:**
1. Finding seed note for "Project Atlas"...
   - Seed: [[Project Atlas Overview]]
2. Following WikiLinks 2 levels deep...
   - Hop 1: 12 linked notes
   - Hop 2: 23 additional notes (35 total + seed = 36 nodes)
3. Building link graph...
   - 36 nodes, 67 edges, 2 broken links omitted
4. Generating canvas...

## Vault Atlas — Project Atlas

**Generated:** 2026-04-05
**Canvas:** `.agent/outputs/vault-atlas-atlas.canvas`

### Statistics
- **Total nodes:** 36
- **Total edges:** 67
- **Broken links (omitted):** 2

### Top 5 Hub Nodes
| Rank | Note | Connections (In/Out) |
|------|------|---------------------|
| 1 | [[Project Atlas Overview]] | 12/8 (20) |
| 2 | [[Project Beacon]] | 6/5 (11) |
| ... | ... | ... |

Canvas saved to `.agent/outputs/vault-atlas-atlas.canvas`.

### Large Vault Warning

**User:** Visualize my vault.

**Agent:**
Your vault contains 342 Markdown files. A full canvas at this scale may be large and slow to render in Obsidian.

Would you like to:
1. Continue with the full vault visualization
2. Generate a scoped view instead (provide a topic or project name)
