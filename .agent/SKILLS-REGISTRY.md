# SKILLS-REGISTRY.md

**Universal Skills Index** — master reference for AI agent capabilities across the vault.

---

## Purpose

This registry provides **cross-agent workflows, integration patterns, and decision trees** for the vault's skill ecosystem. For a live inventory of available skills, list `.agent/skills/` — each skill directory's `SKILL.md` frontmatter carries its `name` and `description`.

All agents share a single canonical skill directory (`.agent/skills/`) via symlinks/junctions (created by `setup.ps1`). This registry is the sole index for workflows and integration patterns.

---

## Skill Inventory (template set, 37)

| Category | Skills |
|:---|:---|
| **Capture & Triage** | `universal-triager`, `write-note`, `clip-and-localize` |
| **Vault Intelligence** | `query-vault`, `compile-wiki`, `extract-concepts`, `connect-domains`, `reconcile-vault`, `visualize-vault`, `graduate-idea`, `knowledge-runtime` |
| **Maintenance** | `optimize-workspace`, `archive-file`, `checkpoint-session`, `purge-desktop-ini`, `sync-agents`, `local-security-audit` |
| **Validation** | `validate-frontmatter`, `validate-skills-standard`, `validate-workspace`, `validate-workflow-state` |
| **Skill Development** | `skill-creator`, `review-skill-design`, `assimilate-skills` |
| **Obsidian Toolkit** | `obsidian-cli`, `obsidian-markdown`, `obsidian-bases`, `json-canvas` |
| **Conversion & Media** | `convert-docx-to-md`, `convert-pdf-to-md`, `convert-html-to-pdf`, `convert-with-docling`, `download-media`, `transcribe-audio`, `optimize-assets` |
| **Writing** | `enhance-writing`, `tools-for-thought` |

---

## Decision Trees

### Capture & Triage Workflow

```
Start: "Process my inbox" / a new item lands in Inbox/
│
├─ Is it a quick idea or concept?
│  └─ write-note (Socratic atomic-note creation)
│
├─ Is it a web article to keep?
│  └─ clip-and-localize (offline-readable clip with local images)
│
├─ Batch of mixed captures?
│  └─ universal-triager (PARA route + Zettelkasten enrichment)
│
└─ Where does it go?
   ├─ Authored + deadline   → 01_Projects/
   ├─ Authored + ongoing    → 02_Areas/  (+ AREA-INDEX entry)
   ├─ External / reference  → 03_Resources/ (+ Source Catalog row)
   └─ Inactive / stale      → 04_Archives/ (via archive-file)
```

### Vault Interrogation & Intelligence

```
Start: "What do my notes say about X?" / discovery work
│
├─ Is the optional typed knowledge runtime available?
│  ├─ Yes + typed entities/relations/claims needed → knowledge-runtime
│  └─ No / ordinary note question                  → query-vault
├─ Compile sources into a wiki                      → compile-wiki
├─ Find recurring concepts/themes                   → extract-concepts
├─ Bridge two topics                                → connect-domains
├─ Check for contradictions                         → reconcile-vault
├─ See vault topology                               → visualize-vault
└─ Promote an idea to a project                     → graduate-idea
```

### Typed Knowledge Runtime

```
Need typed/entity-aware knowledge work
│
├─ Resolve/search/get        → knowledge.resolve_entity / search / get
├─ Traverse graph            → knowledge.neighbors / trace_path / query
├─ Inspect evidence/history  → knowledge.sources / claims / timeline
├─ Reconcile/diagnose        → knowledge.contradictions / health / communities / impact
└─ Mutate semantic state     → propose_patch → validate_patch → apply_patch
                                (apply may be read-only / confirmation-gated)
```

### Maintenance Cycle

```
Quarterly OR after adding 3+ new skills
│
├─ optimize-workspace (5-phase audit: discovery → dependencies →
│    quality → performance → recommendations)
├─ archive-file (move stale items per 04_Archives/specs/archive-taxonomy;
│    session-log folders >30 days → 04_Archives/_agent-artifacts/)
├─ validate-workspace (frontmatter sweep)
├─ sync-agents (governance drift check: CLAUDE.md pointer, GEMINI.md version)
└─ local-security-audit (secrets/posture scan)
```

### Document Conversion

```
Start: "Convert this document"
│
├─ Word (.docx)                → convert-docx-to-md
├─ Simple text-heavy PDF       → convert-pdf-to-md (fastest)
├─ Complex/scanned PDF         → convert-with-docling (AI layout/OCR)
├─ HTML → PDF                  → convert-html-to-pdf
├─ Online video/audio          → download-media → transcribe-audio
└─ Images to compress          → optimize-assets
```

### Skill Development

```
Start: "Create or validate a skill"
│
├─ New skill                   → skill-creator (theory + structure)
├─ Structure compliance        → validate-skills-standard
├─ Design quality audit        → review-skill-design
└─ Import from a peer agent    → assimilate-skills
```

---

## Universality Standards

Skills in `.agent/skills/` must be executable by **any** AI agent:

| Rule | Do | Don't |
|:---|:---|:---|
| **Tool names** | Use generic capabilities from `TOOL-TAXONOMY.md` (e.g., `file-read`, `content-search`) | Hardcode agent tools (Read, Glob, readFile, grepSearch) |
| **Dialogues** | Use `**Agent:**` as speaker label | Use `**Claude:**` or `**Gemini:**` |
| **Model metadata** | Omit `model:` lines from shared skills | Include `model: sonnet` |
| **Paths** | Reference `.agent/` for shared outputs | Hardcode `.gemini/` or `.claude/` paths |

**Validation grep** (expect zero matches):
```
grep -rn "`Read`\|`Write`\|`Edit`\|`Bash`\|`Glob`\|`Grep`\|`AskUserQuestion`\|`WebFetch`" .agent/skills/*/SKILL.md
```

## Adding New Skills

1. Create the skill directory in `.agent/skills/` (it appears to all agents through the junctions).
2. Follow the Agent Skills Standard: `SKILL.md` (agent instructions) + `README.md` (human docs), YAML frontmatter with kebab-case `name` and a `description` covering *what + when*.
3. Run `validate-skills-standard`.
4. Update this file only if adding new decision trees or integration patterns.

---

**Owner**: {{OWNER_NAME}}
**Version**: 1.1 (Knowledge runtime integration)
