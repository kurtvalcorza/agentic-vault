---
name: write-note
description: "Interactive atomic note creation through Socratic interrogation. Use when writing a new note, capturing a concept as an atomic note, or creating a Zettelkasten entry."
---








# Write Note Skill

## Purpose
Helps the user create atomic, reusable notes through guided interrogation. Focuses on **one idea per note** with heavy linking to build a knowledge web.

## Dependencies

### Required Tools
- `file-search` - Search for related notes.
- `file-write` - Save the note.
- `file-edit` - Update related files with backlinks.

### Input
- User intent to create a note (e.g., "Let's write a note about [concept]").

### Output Directories
- `Notes/`

---

## Phase 1: Concept Clarification
**Goal:** Ensure the note is atomic (one clear idea).

1.  **Ask:**
    - "What's the core idea?"
    - "Why does this matter?"
    - "Where did this come from?" (Source/Context)
2.  **Refine:** If the idea is too broad, ask to break it down.

## Phase 2: Socratic Interrogation
**Goal:** Deepen the note through questions.

1.  **Ask (Select 2-3):**
    - "How is this different from [related concept]?"
    - "When would you NOT use this?"
    - "What assumptions does this rely on?"
    - "What's a concrete example from your work?"

## Phase 3: Connection Discovery
**Goal:** Identify links to existing knowledge.

1.  **Search:**
    - `01_Projects/` for mentions.
    - `02_Areas/` for related concepts.
    - `Notes/` for connections.
2.  **Ask:** "What other concepts is this related to?"

## Phase 4: Note Draft
**Goal:** Specific, atomic note structure.

1.  **Draft:** Use the `System/Templates/Notes Entry.md` structure (aligned with standard).
2.  **Naming:** Enforce `[Concept]-[Specificity].md`.

## Phase 5: Finalization & Linking
**Goal:** Save and interconnect.

1.  **Save:** to `Notes/[Note-Name].md`.
2.  **Backlink:** Immediately update related files (Projects/Areas) to link to the new note.
3.  **Enhance Areas:** If the note relates to an Area, suggest adding it to the Area file ('Related Concepts' or similar).


## Internal Metadata
- **color**: blue
- **tags**: [agent, zettelkasten, second-brain, atomic-notes, progressive-enhancement]
- **domain**: knowledge-management
- **status**: active
- **version**: 1.0
- **created**: {{date}}
- **updated**: {{date}}