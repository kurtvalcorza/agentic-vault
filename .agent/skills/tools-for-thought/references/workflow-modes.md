# Workflow Modes

Tools for Thought operates in four modes based on user intent and stage of content creation.

---

## Mode 1: Exploration (Understanding the Task)

**When to use:** User is starting a new piece or unclear about direction.

### Approach
1. Surface tensions and framings, not answers
2. Ask questions that reveal assumptions
3. Present multiple angles without recommending one

### Provocations to Offer
- "What's the one thing you want readers to remember?"
- "Who disagrees with your premise, and why?"
- "What would make this piece unnecessary?"

---

## Mode 2: Development (Building the Argument)

**When to use:** User has direction but needs to construct content.

### Approach
1. Challenge claims as they emerge
2. Identify gaps in reasoning
3. Surface counterarguments proactively
4. Never autocomplete ideas—offer alternatives instead

### Provocations to Offer
- "Your claim depends on [assumption]. How would you defend it?"
- "A skeptical reader might ask: [question]. How do you respond?"
- "You're implicitly de-emphasizing [X]. Is that intentional?"

---

## Mode 3: Refinement (Polishing Output)

**When to use:** User has a draft and needs to strengthen it.

### Approach
1. Identify where the user is hedging or vague
2. Test different framings without choosing for them
3. Flag logical inconsistencies
4. Ask about intended audience impact

### Provocations to Offer
- "Paragraph 3 takes a [tone]. Would [alternative tone] serve your goal better?"
- "You wrote '[phrase]'—what are you actually claiming here?"
- "This section assumes readers know [X]. Do they?"

---

## Mode 4: Interrogation (Stress-Testing a Finished Artifact)

**When to use:** User arrives with a finished or near-finished artifact and wants it challenged, not improved.

### Approach
0. Preliminary scan — triage to full report, abbreviated report, or redirect to another mode
1. Identify the adversary persona(s) — ask the user who the toughest audience is
2. Distill the core claim — confirm with user before proceeding
3. Surface load-bearing assumptions (stated and unstated)
4. Name the silences — what the artifact conspicuously does not say
5. Calibrate evidence against claims — flag overreach
6. Write the adversarial read — per persona if multiple audiences; identify convergence points
7. Translate all findings into a Decision Menu

### Key Departure from Other Modes
Interrogation Mode has two phases: a brief **conversational setup** (adversary identification, core claim confirmation, triage) and a **single-artifact delivery** (the Interrogation Report). The setup typically requires 2-3 exchanges. The report is then delivered whole — the user decides which threads to pull, acts on it asynchronously, and shares it with collaborators if needed.

### Output: Interrogation Report Sections
1. Core Claim
2. Load-Bearing Assumptions
3. Silences
4. Evidence vs. Claim Gap
5. Adversarial Read
6. Decision Menu
7. Interrogation Summary

### Trigger Phrases
- "Challenge this."
- "What's wrong with this?"
- "Where would a skeptic attack?"
- "Is this defensible?"
- "What am I missing?"
- "Interrogate this."
- "Let's do an adversarial review."
- "Adversarial review."

**Canonical reference:** See `references/interrogation-mode.md` for the complete protocol, report template, failure modes, scaling guidance, content type adaptations, and post-report workflow. When in doubt, `interrogation-mode.md` is authoritative.

---

## Mode Selection

The mode is determined by:
- **User's stated goal** ("I'm starting to think about..." → Exploration)
- **Artifacts present** (No draft → Exploration; Outline → Development; Full draft → Refinement or Interrogation)
- **User's questions** ("What should I write about?" → Exploration; "How do I say this?" → Development; "Is this good?" → Refinement; "Is this right?" → Interrogation)
- **User's intent** (Improve it → Refinement; Challenge it → Interrogation)

### Refinement vs. Interrogation
These two modes are the most commonly confused. Use this distinction:

| Signal | Mode |
|--------|------|
| "Help me strengthen this" | Refinement |
| "Is this well-expressed?" | Refinement |
| "Challenge this" / "What's wrong with this?" | Interrogation |
| "Is this defensible?" | Interrogation |
| User is preparing to defend work to a skeptical audience | Interrogation |

**Critical rule:** Do not default to Refinement when the user arrives with a finished artifact. Interrogation Mode exists precisely for this entry point. Polishing a flawed argument makes it worse, not better.

Modes can transition fluidly within a single session as the user's needs evolve.

---

## Mode Overview

| Mode | Entry Point | Output | Primary Question |
|------|-------------|--------|-----------------|
| Exploration | No artifact | Framings and tensions | What am I actually trying to say? |
| Development | Outline or direction | Challenged arguments | Does this hold together? |
| Refinement | Draft | Polished expression | Is this well-expressed? |
| Interrogation | Finished artifact | Interrogation Report | Is this actually right? |

---

## Version History
- 2026-04-04: Synced Mode 4 steps with canonical `interrogation-mode.md` (added Step 0 preliminary scan, adversary persona step, adversarial review triggers); reframed Key Departure to acknowledge multi-turn setup; added canonical reference note
- 2026-02-18: Added Mode 4 (Interrogation); updated Mode Selection with Refinement vs. Interrogation disambiguation; added Mode Overview table
