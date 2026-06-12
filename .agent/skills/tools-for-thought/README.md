# Tools for Thought: Content Writing Skill

## Overview

This skill transforms AI-assisted content creation from simple task completion into genuine cognitive enhancement. Based on the "AI as Tool for Thought" paradigm, it helps you think more deeply about your writing rather than just producing it faster.

## The Philosophy

Traditional AI writing assistants optimize for speed and convenience. This skill optimizes for **understanding** and **thinking quality**.

| Traditional AI Assistant | Tool for Thought |
|--------------------------|------------------|
| Writes content for you | Challenges your thinking |
| Optimizes for speed | Optimizes for understanding |
| Gives you answers | Helps you ask better questions |
| Reduces cognitive effort | Enhances cognitive engagement |

## When It Activates

The skill activates when you're working on:
- News releases and press communications
- Academic writing (papers, proposals, literature reviews)
- Technical reports and documentation
- Blog posts and thought leadership
- Panel talking points and presentation scripts

## How It Works: Four Modes

### Mode 1: Exploration
When you're starting fresh or unclear about direction. The skill surfaces tensions and framings instead of giving you answers.

### Mode 2: Development
When you have direction but need to build the argument. The skill challenges claims as they emerge and surfaces counterarguments.

### Mode 3: Refinement
When you have a draft and need to strengthen it. The skill identifies hedging, tests framings, and flags inconsistencies.

### Mode 4: Interrogation
When you have a finished artifact and want it challenged before it reaches a real audience. The skill produces a structured Interrogation Report with adversarial reads and a decision menu.

## Council Mode (opt-in extension of Interrogation)

For genuinely high-stakes, going-public artifacts (keynotes, press releases, panel talking points, decision memos), Interrogation Mode can run as a **council** — the adversarial read is produced by *multiple AI models* (Claude, Gemini, Codex/GPT) instead of one model playing every persona.

**Why:** when two different models independently flag the same weakness, that convergence is real signal, not one model agreeing with itself.

**How it differs:** only the adversarial-read section fans out to other models. Everything else — claim distillation, assumption surfacing, convergence synthesis, decision menu — stays with the orchestrating model.

**Default lens → model mapping:**
- Institutional / political → Claude (in-session)
- External public / accountability → Gemini
- Technical / production reality → Codex or Cursor (`gpt-5.1-codex`)

You can remap conversationally (e.g., "Gemini as a COA auditor"). If a model is unavailable (rate-limited, not logged in), that lens is marked a known gap and the report proceeds with the rest.

**Trigger:** explicit only — say "council adversarial review." Plain "adversarial review" stays single-model, because the council is slower and costs more model calls.

## Usage Examples

### Starting a News Release
```
User: I need to write a press release about our new AI center.
Tool for Thought: Before drafting, let me surface some tensions...
```

### Challenging a Finished Draft
```
User: Here's my speech. Challenge this.
Tool for Thought: [Interrogation Mode] Let me identify the adversary persona...
```

### Running a Council Review
```
User: Council adversarial review on this keynote.
Tool for Thought: Council mapping: A = public/journalist (Gemini),
B = technical (Cursor/gpt-5.1-codex), C = institutional (Claude, me).
Firing A and B now — confirm or correct.
```

## Reference Documentation

- `references/workflow-modes.md` — Detailed mode descriptions and selection guidance
- `references/interrogation-mode.md` — Complete Interrogation Mode protocol and report template
- `references/council-mode.md` — Council Mode: multi-model adversarial read
- `references/content-type-protocols.md` — Provocations by content type
- `references/interaction-patterns.md` — Core engagement patterns
- `references/metacognitive-checkpoints.md` — Strategic reflection prompts
- `references/provocation-bank.md` — Comprehensive question catalog
- `scripts/council-adversary-read.ps1` — Orchestrator fan-out script for Council Mode

## Requirements (Council Mode)

Council Mode shells out to external CLIs. Ensure these are installed and authenticated as needed:
- **Gemini CLI** (`gemini`) — for the public/external lens
- **Codex CLI** (`codex`) — for the technical lens (has a usage cap)
- **Cursor CLI** (`cursor-agent`) — alternative technical lens; requires `cursor-agent login`

Standard Interrogation Mode (single-model) needs none of these.
