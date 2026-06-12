---
name: connect-domains
description: "Discover non-obvious connections between two unrelated topics in the vault by building domain clusters, tracing link graph paths, and generating categorized bridge ideas. Use when asked to connect [topic A] and [topic B], bridge [domain A] with [domain B], find connections between two subjects, or explore intersections across knowledge domains."
---

# connect-domains

Discovers non-obvious connections between two unrelated topics in your vault. Builds a cluster of related notes for each topic, identifies shared elements and link graph paths between them, and generates up to 5 categorized connections — structural analogies, transfer opportunities, and collision ideas. Approved connections are saved as idea notes in `Inbox/` for further development.

## When to Use

- You have two seemingly unrelated topics and want to find hidden connections between them
- You're looking for creative insights at the intersection of different knowledge domains
- You want to discover shared references, people, or concepts across two areas of your vault
- You're brainstorming and want the vault's link structure to suggest novel ideas

## Invocation

### Basic Usage

```
Connect Project Atlas and blockchain
Bridge AI ethics with science communication
Find connections between machine learning and project management
```

Provide two topic names. The skill searches your vault for notes related to each topic, builds clusters, and identifies bridges between them.

### What Happens

1. The skill searches your vault for notes matching each topic (by title, tags, and content)
2. It follows WikiLinks up to 2 hops from matching notes to build a Domain_Cluster for each topic
3. It compares the two clusters to find shared WikiLinks, tags, people references, and link graph paths
4. It generates up to 5 connections categorized by type
5. You select which connections to save (by number)
6. Approved connections are saved as idea notes in `Inbox/`
7. The skill proposes WikiLink additions to strengthen cross-domain references (Two-Output Rule)

## Connection Categories

Each generated connection is categorized as one of three types:

### Structural Analogies

A pattern or structure in domain A that maps to domain B. These highlight parallel architectures, processes, or organizational patterns across different fields.

Example: "Project Atlas's regional iHub network mirrors blockchain's distributed node architecture — both rely on decentralized nodes with a coordination layer."

### Transfer Opportunities

Something that works well in domain A and could be adapted for domain B. These are practical, actionable insights about applying proven approaches in new contexts.

Example: "The evaluation framework used in AI model assessment could be adapted for measuring science communication impact."

### Collision Ideas

New concepts that emerge at the intersection of the two domains. These are novel ideas that wouldn't exist without combining perspectives from both fields.

Example: "Combining Project Atlas's AIaaS delivery model with blockchain smart contracts could enable a trustless AI model marketplace."

## Output

### Connection Notes

Saved to `Inbox/` with the following structure:

```yaml
---
date: YYYY-MM-DD
tags: [idea]
connection_type: structural-analogy | transfer-opportunity | collision-idea
domains:
  - "[[Domain A]]"
  - "[[Domain B]]"
---

# {Connection Title}

{Description of the connection and why it matters}

## Source Domains
- [[Domain A]] — {context}
- [[Domain B]] — {context}
```

Each connection note includes:
- The `#idea` tag for easy discovery
- WikiLinks to both source domains
- The connection type for categorization
- Source context explaining the relevance from each domain

### Secondary Updates (Two-Output Rule)

After saving connections, the skill proposes WikiLink additions to the most representative notes from each domain cluster:
- Cross-references between the two domain notes
- Links to any saved connection notes

These proposals require your explicit approval before any existing notes are modified. You can approve all, select specific updates, or reject all.

### Session Log

Activity is logged to `System/session-logs/YYYY-MM-DD/` with topics, cluster sizes, connections found, and approval outcomes.

## Honesty Clause

If the two topics have no meaningful overlap in your vault — no shared elements, no link graph paths, and no genuine semantic parallels — the skill reports this honestly rather than fabricating connections. Zero genuine connections is a valid result. The skill may suggest ways to build bridges (adding bridging notes, trying sub-topics, checking alternate terminology).

## Cluster Size Warning

If a domain cluster exceeds 100 notes, the skill warns you and offers to narrow the topic for more focused results. Large clusters can produce noisy connections — a more specific sub-topic often yields better insights.

## Error Handling

| Scenario | Behavior |
|:---------|:---------|
| No topics provided | Prompts for both topics |
| Only one topic provided | Prompts for the second topic |
| No vault notes found for a topic | Reports which topic has no coverage and exits |
| Cluster exceeds 100 notes | Warns and offers to narrow the topic |
| No meaningful overlap | Reports honestly, suggests alternatives |
| User rejects all connections | Logs the session and exits without saving |

## Prerequisites

| Dependency | Path | Purpose |
|:-----------|:-----|:--------|
| Two-output rule steering | `.agent/steering/two-output-rule.md` | Governs secondary WikiLink proposals |
| Vault content directories | `01_Projects/`, `02_Areas/`, `03_Resources/`, `Inbox/` | Notes to search and cluster |
| Output directory | `Inbox/` | Where connection notes are saved |
| Session log directory | `System/session-logs/YYYY-MM-DD/` | Activity logging |

## Related Skills

- `reconcile-vault` — Detects contradictions across vault notes (complementary for checking consistency of connected domains)
- `visualize-vault` — Generates a visual map of vault link structure (complementary for seeing cluster topology)
- `graduate-idea` — Promotes idea notes to structured project specs (use after saving connection ideas you want to develop further)
- `extract-concepts` — Discovers recurring concepts across the vault (complementary for finding thematic bridges)
- `query-vault` — Q&A against vault content (use to investigate specific claims within a domain)
