---
description: "The default way to kick off a work session — state outcome, audience, success, and mode up front. The user-side half of a good opener; the 'read the stack' half is already automatic via AGENTS.md. Read by the /kickoff command across agents."
tags: [reference/playbook]
---

# Opening Move

> ✏️ **Customize the examples.** The structure is general-purpose; the worked
> examples below use a fictional placeholder — "Atlas," an in-house AI platform.
> Swap in real tasks from your own work.

The default way to start a real task. The goal isn't a perfect prompt — it's
triggering the right collaboration pattern in one line.

> **Why this is short:** half of a good opener — *read the stack, check the
> board, use a skill* — already happens automatically. `AGENTS.md` makes agents
> read themselves + today's session log + `memory-hot-cache` before any work,
> and skills-first routing handles the rest. So the opener only carries the part
> the agent can't infer: **what you're actually trying to do.**

## The four ingredients

State these and the agent has what it needs:

1. **Outcome** — what you want to exist when this is done
2. **Audience** — who it's for (sets register, depth, framing)
3. **Success** — what "good" looks like, concretely
4. **Mode** — think with me / draft / build / decide

## Default opener

> I want to **[outcome]** for **[audience]**. Success looks like **[criteria]**.
> Check the board ([[01_Projects/To Do]]) and use a matching skill. Ask only the
> questions that change the result, then recommend the move and execute.

## Worked examples

**Writing**
> I want a 2-page launch post for the **Atlas public beta**, for a developer
> audience. Success = an impact-first lead, one quotable sentence, zero
> unexplained jargon. Hold to [[voice]] + [[anti-style]]. Ask only what changes
> the result, then draft.

**Strategy / decide**
> I want to think through whether **Atlas v2** leads with the self-serve
> workbench or the shared pipeline. Success = a clear recommendation, the main
> tradeoff, and the next move.

**Build / system**
> I want to build a reusable **monthly metrics-report** workflow.
> Success = a working first version I can run on this month's data today.

## Mode variants

- **Strategy** — *"…Success = a recommendation, the main tradeoff, the next move."*
- **Writing** — *"…Success = something sharp, human, and ready to refine."* (voice + anti-style apply)
- **Build** — *"…Success = a working first version I can test today."*

> Keep it one or two lines. If the opener becomes a paragraph, it's doing work
> the stack already does.

## Interview (when run via /kickoff)

Frame the task as a quick **multiple-choice** interview, not prose Q&A. Skim the
session log + board first so the options are real, then present the four
ingredients with a recommended pick for each:

1. **Outcome** — likely in-flight items from the board, plus "Other"
2. **Audience** — media / leadership / academic / industry / public (see [[voice]])
3. **Success** — a few concrete markers to choose from
4. **Mode** — think with me / draft / build / decide

Skip anything already given. Then read the stack, pick the skill, recommend the
next move, and execute.

> **Tooling:** Claude renders these via the `AskUserQuestion` widget (clickable
> options + a recommended pick). Agents without it (Gemini, Codex) present the
> same options as a numbered list to reply to.
