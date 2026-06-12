---
description: "Conversational interface protocols — Skills-First Protocol, trigger phrases, skill categories, and workflow decision trees."
source-section: "Conversational Interface"
---

## Conversational Interface

This vault uses **natural language triggers** to activate specialized skills. Instead of manually creating files, use conversational phrases to invoke workflows.

### Skills-First Protocol

**CRITICAL: Always check for existing skills before implementing any workflow manually.**

When a user makes a request:

1. **Search for existing skills** using one of these methods:
   - Search `.agent/skills/` directory with `file-search` or `content-search`
   - Check `.agent/SKILLS-REGISTRY.md` for workflow decision trees and integration patterns

2. **Match trigger phrases** - Compare user request to documented trigger phrases in skill documentation

3. **Use existing skills** - If a skill exists that matches the request, use it rather than implementing from scratch

4. **Only deviate when**:
   - No existing skill matches the requirement
   - Existing skill doesn't fit the specific use case
   - User explicitly requests a different approach

5. **Document new patterns** - If you implement something manually that could be reused, suggest creating a skill for it

**Why this matters**: The vault ships 36 skills specifically designed to avoid reinventing workflows. Using existing skills ensures consistency, leverages tested patterns, and respects established conventions.

### Most Common Triggers

| Trigger Phrase | Skill | Purpose |
| :--- | :--- | :--- |
| "Let's write a note" | `write-note` | Atomic note creation (Socratic interrogation) |
| "Triage my inbox" | `universal-triager` | PARA routing + Zettelkasten enrichment |
| "Optimize workspace" | `optimize-workspace` | Quarterly vault maintenance & cleanup |
| "Archive this" | `archive-file` | Retire stale items per the archive taxonomy |
| "Convert this document" | `convert-docx-to-md` / `convert-pdf-to-md` | Word/PDF → Markdown |
| "Transcribe this recording" | `transcribe-audio` | Audio/video → text transcript |
| "Create a new skill" | `skill-creator` | Guided skill authoring |
| "Validate my skills" | `validate-skills-standard` | Structure & frontmatter compliance |

### Knowledge Base & Vault Intelligence

| Trigger Phrase | Skill | Purpose |
| :--- | :--- | :--- |
| "Compile my sources into a wiki" | `compile-wiki` | Raw documents → structured interlinked wiki |
| "What do my notes say about X?" | `query-vault` | Vault Q&A with cited answers and gap analysis |
| "Clip this article" | `clip-and-localize` | Web article → offline Markdown with localized images |
| "Find recurring concepts" | `extract-concepts` | Discover emergent themes and generate concept hubs |
| "Connect these topics" | `connect-domains` | Bridge notes between knowledge domains |
| "Check for contradictions" | `reconcile-vault` | Find conflicting claims across notes |

### Skill Categories

**36 template skills across eight categories** (full inventory: `.agent/SKILLS-REGISTRY.md`):
- **Capture & Triage**: Inbox triage, atomic notes, web clipping
- **Vault Intelligence**: Vault Q&A, wiki compilation, concept extraction, domain bridging
- **Maintenance**: Workspace optimization, archiving, session checkpoints, security audit
- **Validation**: Frontmatter, skills standard, workspace, workflow state
- **Skill Development**: Skill creation, design review, assimilation
- **Obsidian Toolkit**: CLI, markdown, bases, JSON Canvas
- **Conversion & Media**: Document conversion, media download, transcription, asset optimization
- **Writing**: Writing enhancement, tools for thought

**For workflow decision trees and integration patterns:** See `.agent/SKILLS-REGISTRY.md`
