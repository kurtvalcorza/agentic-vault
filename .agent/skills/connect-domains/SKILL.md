---
name: connect-domains
description: "Discover non-obvious connections between two unrelated topics in the vault by building domain clusters, tracing link graph paths, and generating categorized bridge ideas. Use when asked to connect [topic A] and [topic B], bridge [domain A] with [domain B], find connections between two subjects, or explore intersections across knowledge domains."
two_output: true
---

# connect-domains

Discovers non-obvious connections between two unrelated topics in the vault. Builds a Domain_Cluster for each topic by searching notes and following WikiLinks, then identifies shared elements, traces link graph paths, and generates up to 5 categorized connections (structural analogies, transfer opportunities, collision ideas). Approved connections are saved as idea notes in `Inbox/`. As a two-output skill, it also proposes WikiLink additions to source domain notes.

## Trigger Phrases

- "Connect [topic A] and [topic B]"
- "Bridge [domain A] with [domain B]"
- "Find connections between [topic A] and [topic B]"
- "What do [domain A] and [domain B] have in common?"
- "Explore intersections between [topic A] and [topic B]"

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| topic_a | Yes | — | First topic or domain name to build a cluster around |
| topic_b | Yes | — | Second topic or domain name to build a cluster around |

---

## Step 0 — Validate Input

### Step 0.1 — Check for Missing Topics

If **no topics** are provided:

```
**Tool:** user-interact
"To find connections, I need two topics. What are the two topics or domains
you'd like me to bridge?"
```

Wait for the user to provide both topics before proceeding.

If **only one topic** is provided:

```
**Tool:** user-interact
"I have '{topic_a}' as the first topic. What's the second topic or domain
you'd like me to connect it with?"
```

Wait for the user to provide the second topic before proceeding.

---

## Step 1 — Build Domain Clusters

For each topic (`topic_a` and `topic_b`), build a Domain_Cluster — a set of related vault notes.

### Step 1.1 — Search for Seed Notes

For each topic, find all directly matching notes:

```
**Tool:** file-search
Find all `.md` files across `01_Projects/`, `02_Areas/`, `03_Resources/`, `Inbox/`.
```

```
**Tool:** content-search
Search for the topic string across all found files.
```

A note is a **seed note** if it matches the topic by any of:
- **Title match**: note title or filename contains the topic (case-insensitive)
- **Tag match**: note frontmatter `tags` array contains a tag matching the topic
- **Content match**: note body contains the topic string as a keyword

### Step 1.2 — Follow WikiLinks (up to 2 hops)

For each seed note, extract all `[[WikiLink]]` targets from the note body and frontmatter.

**Hop 1**: Read each linked note and add it to the cluster.

```
**Tool:** file-read
Read each WikiLink target note.
```

**Hop 2**: For each hop-1 note, extract its WikiLinks and read those targets. Add them to the cluster.

Track visited notes to avoid cycles (circular WikiLinks). If a note has already been visited, skip it.

### Step 1.3 — Cluster Size Check

After building each cluster, count the total notes.

**If a cluster exceeds 100 notes:**

```
**Tool:** user-interact
"The cluster for '{topic}' contains {N} notes, which is quite large.
Would you like to:
  1. Continue with the full cluster
  2. Narrow the topic to get a more focused set of connections"
```

If the user chooses to narrow, prompt for a more specific topic and rebuild that cluster from Step 1.1.

### Step 1.4 — Empty Cluster Check

**If a cluster is empty** (no seed notes found and no linked notes):

Report: "No vault notes found related to '{topic}'."

If **both clusters** are empty, exit gracefully with a message explaining that neither topic has vault coverage. Log to session log.

If **one cluster** is empty, report which topic has no coverage and exit gracefully. The user may want to try a different topic.

---

## Step 2 — Find Bridges Between Clusters

With two populated Domain_Clusters, identify connections between them.

### Step 2.1 — Identify Shared Elements

Compare the two clusters to find:

- **Shared WikiLinks**: notes that appear in both clusters (linked from notes in both domains)
- **Shared tags**: tags that appear on notes in both clusters
- **Shared people references**: `[[Person Name]]` WikiLinks that appear in notes from both clusters

Collect all shared elements — these are the strongest bridge signals.

### Step 2.2 — Trace Link Graph Paths

Check whether a direct path exists in the vault's link graph between any note in Cluster A and any note in Cluster B.

**If a direct path exists** (within a reasonable depth, up to 5 hops):
- Trace the shortest path
- Document each intermediate hop: `[[Note A]] → [[Intermediate 1]] → [[Intermediate 2]] → [[Note B]]`
- Explain the relevance of each hop

**If no direct path exists**: proceed to Step 2.3.

### Step 2.3 — Semantic Overlap Analysis (no direct path)

When no direct link graph path connects the two clusters, identify the closest semantic overlap:

- **Shared concepts**: abstract ideas, frameworks, or methodologies that appear in both domains
- **Shared metaphors**: analogous language or framing used in both domains
- **Structural similarities**: similar organizational patterns, workflows, or hierarchies

This step relies on LLM judgment to identify meaningful parallels. Complementary or superficially similar terms are not sufficient — the overlap must represent a genuine conceptual bridge.

---

## Step 3 — Generate Connections

Based on the bridges found in Step 2, generate up to 5 specific, actionable connections.

### Step 3.1 — Categorize Each Connection

Each connection MUST be categorized as one of:

| Category | Description | Example |
|----------|-------------|---------|
| **structural-analogy** | A pattern in domain A maps to domain B | "The feedback loop in [A's process] mirrors the iteration cycle in [B's methodology]" |
| **transfer-opportunity** | What works in A could apply to B | "The evaluation framework used in [A] could be adapted for assessing [B]" |
| **collision-idea** | A new concept at the intersection | "Combining [A's approach] with [B's constraint] suggests a novel [hybrid concept]" |

### Step 3.2 — Apply Honesty Clause

**If the two clusters have no meaningful overlap** — no shared elements, no link graph path, and no genuine semantic parallels:

Report honestly:

```
"After analyzing {N_a} notes related to '{topic_a}' and {N_b} notes related to
'{topic_b}', I found no meaningful connections between these domains in your vault.
The topics appear to be genuinely unrelated based on your current notes.

You might consider:
- Adding notes that explicitly bridge these topics
- Trying more specific sub-topics within each domain
- Checking if related concepts exist under different terminology"
```

Do NOT fabricate connections to meet a count. Zero genuine connections is a valid and honest result.

### Step 3.3 — Format Connection List

Present connections as a numbered list:

```
## Connections Found: {topic_a} ↔ {topic_b}

**Clusters:** {N_a} notes in '{topic_a}', {N_b} notes in '{topic_b}'
**Shared elements:** {count} shared WikiLinks, {count} shared tags, {count} shared people

1. **[structural-analogy]** {Connection title}
   {Description of the connection and why it matters}
   Sources: [[Note from A]], [[Note from B]]

2. **[transfer-opportunity]** {Connection title}
   {Description of the connection and why it matters}
   Sources: [[Note from A]], [[Note from B]]

3. **[collision-idea]** {Connection title}
   {Description of the connection and why it matters}
   Sources: [[Note from A]], [[Note from B]]

...

Enter the numbers of connections you'd like to save (e.g., "1, 3"), or "none" to skip.
```

---

## Step 4 — User Selection and Saving

### Step 4.1 — Collect User Selection (Confirmation_Protocol)

Per the Confirmation_Protocol, present the numbered connection list and wait for explicit user approval before writing any files.

```
**Tool:** user-interact
Present the numbered connection list and ask the user which connections to save.
```

The user confirms by selecting numbers (e.g., "1, 3" or "all" or "none"). Partial approval is supported — only selected connections are saved. No vault writes occur before user confirmation.

If the user selects "none", skip to Step 5 (logging).

### Step 4.2 — Save Approved Connections

For each approved connection, create a note in `Inbox/` using the Connection Note data model:

```
**Tool:** file-write
Write to `Inbox/{Connection Title}.md`
```

**Connection Note format:**

```yaml
---
date: {YYYY-MM-DD}
tags: [idea]
connection_type: {structural-analogy | transfer-opportunity | collision-idea}
domains:
  - "[[{topic_a representative note or topic name}]]"
  - "[[{topic_b representative note or topic name}]]"
---

# {Connection Title}

{Description of the connection and why it matters}

## Source Domains
- [[{Domain A note}]] — {context from domain A}
- [[{Domain B note}]] — {context from domain B}
```

Each saved note MUST:
- Have `tags: [idea]` in frontmatter (the `#idea` tag)
- Have WikiLinks to both source domains in the `domains` frontmatter array
- Have WikiLinks to both source domains in the `## Source Domains` body section
- Have a `connection_type` matching one of the three categories

---

## Step 5 — Two-Output: Propose WikiLink Additions

As a `two_output: true` skill, after the primary output (connection discovery and saving), propose secondary updates to source domain notes.

### Step 5.1 — Identify Proposed WikiLink Additions

For each of the two source domain topics, identify the most representative seed note (the note most central to the cluster).

Propose adding WikiLinks to these representative notes:
- **Cross-reference**: Add a WikiLink from the topic_a representative note to the topic_b representative note (and vice versa)
- **Connection note links**: If any connection notes were saved, add WikiLinks to those connection notes from both representative domain notes

Proposed additions are limited to:
- Appending WikiLinks to the note body
- Adding entries to the `related` or `concepts` frontmatter arrays

Per the Two-Output Rule, secondary outputs MUST NOT:
- Create new notes
- Delete existing content
- Modify frontmatter fields other than `related` and `concepts`

### Step 5.2 — Present Secondary Proposals

Present the proposed WikiLink additions separately from the primary output:

```
**Tool:** user-interact
"## Secondary Updates (Two-Output Rule)

Based on the connections found, I'd like to propose these WikiLink additions
to strengthen cross-domain references:

### [[{Topic A representative note}]]
- Add `[[{Topic B representative note}]]` to related notes
- Add `[[{Saved Connection Note}]]` to body

### [[{Topic B representative note}]]
- Add `[[{Topic A representative note}]]` to related notes
- Add `[[{Saved Connection Note}]]` to body

Approve all / Select by number / Reject all?"
```

Support partial approval — the user may approve some additions and reject others.

### Step 5.3 — Apply Approved Secondary Updates

For each approved WikiLink addition:

```
**Tool:** file-read
Read the target note.
```

Apply the approved changes:
- If adding to `related` frontmatter array: append the WikiLink to the existing array (preserve all other frontmatter fields)
- If adding to note body: append a line with the WikiLink at an appropriate location

```
**Tool:** file-write
Write the updated note.
```

---

## Step 6 — Session Log

Log the bridging exercise to `System/session-logs/{YYYY-MM-DD}/`:

- Skill invoked: `connect-domains`
- Topics: `{topic_a}`, `{topic_b}`
- Cluster sizes: `{N_a}` notes, `{N_b}` notes
- Shared elements found: `{count}` WikiLinks, `{count}` tags, `{count}` people
- Connections generated: `{count}`
- Connections saved: `{count}` (list titles)
- Two-output proposals: `{count}` proposed, `{count}` approved
- Outcome: saved / partially saved / no connections found / no overlap

If the session log directory does not exist, create `System/session-logs/{YYYY-MM-DD}/` first.

---

## Required Capabilities

| Capability | Usage |
|:-----------|:------|
| `file-read` | Read vault notes, follow WikiLinks, gather cluster content |
| `file-search` | Find `.md` files across vault directories for cluster building |
| `content-search` | Search for topic keywords, tags, people references across notes |
| `user-interact` | Missing topic prompts, cluster size warnings, connection selection, two-output approval |
| `file-write` | Save approved connection notes to `Inbox/`, apply secondary WikiLink updates |

### Referenced Policies

| Policy | Path | Purpose |
|:-------|:-----|:--------|
| Two-output rule | `.agent/steering/two-output-rule.md` | Governs secondary output behavior (WikiLink proposals) |
| Skills standard | `.agent/steering/skills-standard.md` | Directory structure and frontmatter requirements |

---

## Error Handling

| Scenario | Action |
|:---------|:-------|
| No topics provided | Prompt user for both topics via `user-interact` |
| Only one topic provided | Prompt user for the second topic via `user-interact` |
| Empty cluster (no vault notes found for a topic) | Report "no vault notes found related to '{topic}'" for the empty cluster(s); exit gracefully |
| Cluster exceeds 100 notes | Warn user via `user-interact`, offer to narrow the topic before proceeding |
| No meaningful overlap between clusters | Report honestly per honesty clause — do not fabricate connections |
| Circular WikiLinks during cluster building | Track visited notes; skip already-visited notes to prevent infinite loops |
| WikiLink target does not exist | Note as broken link; do not include non-existent notes in cluster |
| File read failure (permissions, encoding) | Log warning, skip the file, continue building cluster |
| Malformed YAML frontmatter | Log warning, skip the file, continue processing |
| Session log directory missing | Create `System/session-logs/{YYYY-MM-DD}/` directory, then log |
| User rejects all connections | Log rejection in Session_Log, exit without saving any files |

---

## Examples

### Successful Bridge Finding

**User:** Connect Project Atlas and blockchain.

**Agent:**
1. Building domain clusters...
   - "Project Atlas" cluster: 23 notes (seed: 8, hop-1: 11, hop-2: 4)
   - "blockchain" cluster: 9 notes (seed: 3, hop-1: 4, hop-2: 2)
2. Analyzing bridges...
   - Shared WikiLinks: 2 ([[Example Org]], [[Project Beacon]])
   - Shared tags: 1 (#project/cedar)
   - Direct path found: [[Project Atlas Overview]] → [[Project Beacon]] → [[Project Ledger]] → [[Blockchain Research Notes]]

## Connections Found: Project Atlas ↔ blockchain

**Clusters:** 23 notes in 'Project Atlas', 9 notes in 'blockchain'
**Shared elements:** 2 shared WikiLinks, 1 shared tag, 0 shared people

1. **[transfer-opportunity]** Project Beacon Model Provenance via Blockchain
   The Project Beacon AI model store could use blockchain-based provenance tracking to verify model lineage and training data integrity, similar to how Project Ledger tracks digital assets.
   Sources: [[Project Beacon]], [[Project Ledger]]

2. **[structural-analogy]** Decentralized Hub Architecture
   Project Atlas's iHub network (regional AI centers) mirrors blockchain's distributed node architecture — both rely on decentralized nodes with a coordination layer.
   Sources: [[Project Atlas iHubs]], [[Blockchain Architecture Notes]]

3. **[collision-idea]** AI Model Marketplace on Chain
   Combining Project Atlas's AIaaS delivery model with blockchain smart contracts could enable a trustless AI model marketplace where researchers publish and consumers verify model quality on-chain.
   Sources: [[Project Atlas AIaaS Strategy]], [[Smart Contract Patterns]]

Enter the numbers of connections you'd like to save (e.g., "1, 3"), or "none" to skip.

**User:** 1, 3

**Agent:** Saved 2 connection notes to Inbox/:
- `Inbox/Project Beacon Model Provenance via Blockchain.md`
- `Inbox/AI Model Marketplace on Chain.md`

## Secondary Updates (Two-Output Rule)

Based on the connections found, I'd like to propose these WikiLink additions:

### [[Project Atlas Overview]]
- Add `[[Project Ledger]]` to related frontmatter array
- Add `[[Project Beacon Model Provenance via Blockchain]]` to body

### [[Blockchain Research Notes]]
- Add `[[Project Atlas Overview]]` to related frontmatter array
- Add `[[AI Model Marketplace on Chain]]` to body

Approve all / Select by number / Reject all?

### No Overlap Found

**User:** Connect Project Atlas and gardening.

**Agent:**
1. Building domain clusters...
   - "Project Atlas" cluster: 23 notes
   - "gardening" cluster: 0 notes

No vault notes found related to 'gardening'. Unable to find connections without vault coverage for both topics.

### Large Cluster Warning

**User:** Bridge AI and research.

**Agent:**
The cluster for 'research' contains 142 notes, which is quite large. Would you like to:
1. Continue with the full cluster
2. Narrow the topic to get a more focused set of connections
