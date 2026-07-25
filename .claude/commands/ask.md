---
description: Stop and put the open decisions to the user as multiple choice (AskUserQuestion)
argument-hint: [topic or decision - optional]
---

Use the **AskUserQuestion** tool now. $ARGUMENTS

**With `$ARGUMENTS`** — turn what the user wrote into structured questions. It may
be a decision they want to make ("pandoc or quarto for the render"), a topic they
want scoped ("the auth layer"), or a bare instruction to check something first.

**Without `$ARGUMENTS`** — surface the decisions already sitting open in the
current work: the assumptions you were about to proceed on, the forks where two
readings lead to materially different output, the ship/publish/delete calls that
belong to the user. If nothing genuine is open, say so in one line and carry on —
do not manufacture a question to satisfy the command.

Composing the questions:

1. **Ask about forks, not preferences you can infer.** A question earns its slot
   only if the answer changes what you do next. Conventional defaults, facts
   verifiable in the repo, and choices the user already made earlier in the
   session are not questions.
2. **Four questions maximum, two to four options each.** Order the options best
   first and mark your pick `(Recommended)` — you have read the material, so take
   a position rather than presenting a neutral survey.
3. **Each option states its consequence**, not just its name. "Quarto — one
   source, DOCX + PDF from the same build" beats "Quarto".
4. **`multiSelect: true`** when the options genuinely combine (which sections to
   include, which checks to run). Leave it off for mutually exclusive forks.
5. **Headers ≤ 12 characters.** `Scope`, `Render path`, `Migration`.
6. **Never add an "Other" option** — the tool supplies one. Use it for the free
   text the user might want to type.
7. **Do not ask procedural questions** — "ready to proceed?", "does this plan
   look right?" Ask about the substance.

After the answers come back: restate the decisions in one line each, then do the
work. Treat an answer as durable for the rest of the session — do not re-ask the
same fork later in different words.

If a decision is irreversible or outward-facing (publishing, sending, deleting,
overwriting a deliverable), name that plainly in the option text so the user knows
which choice cannot be taken back.
