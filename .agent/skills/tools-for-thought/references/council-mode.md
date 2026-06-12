# Council Mode: Multi-Model Adversarial Read

## What This Is

Council Mode is an **opt-in extension of Interrogation Mode (Mode 4)**. It changes one thing and nothing else: the adversarial read (Step 7 / Report Section 5) is produced by **multiple AI models** instead of the orchestrating model alone.

Standard Interrogation Mode already supports multiple adversary *personas* — but a single model plays all of them. That produces stylistic variation over one underlying cognition. Council Mode assigns personas to **different model lineages** (Claude, Gemini, Codex/GPT) so the attacks come from genuinely different training, instincts, and blind spots.

**Why this matters:** when two *different* models independently flag the same vulnerability, that convergence is real signal — not the same model agreeing with itself. Convergence becomes the highest-priority finding precisely because it survived three different adversaries.

> **Everything except the adversarial read stays with the orchestrator.** Preliminary scan, core-claim distillation, assumption surfacing, silence hunting, evidence calibration, convergence synthesis, and the decision menu are all single-voice, single-structure. Only Section 5 fans out.

---

## When to Activate

**Explicit trigger only.** Council Mode is expensive (3+ model calls) and slow (minutes per call). It never fires on the default Interrogation path.

Activate when the user says:
- "council adversarial review"
- "stress-test this with the council"
- "run the council on this"

If the user says only "adversarial review" / "challenge this" / "interrogate this" → that is **standard** Interrogation Mode (single model). Do not escalate to the council without the explicit word.

---

## Persona ↔ Model Mapping

### Fixed defaults

| Adversary lens | Default runner | Why this model |
|----------------|----------------|----------------|
| **Institutional / political** (skeptical executive, peer agency, oversight body) | **Claude** (orchestrator, in-session) | Strongest at tone-savvy stakeholder and mandate reads |
| **External public / accountability** (journalist, public critic) | **Gemini** (`gemini -p`) | Large context for cross-referencing public record; different public-discourse instincts |
| **Technical / production reality** (domain expert, methodologist, ops reviewer) | **Codex** (`codex exec`) or **Cursor** (`cursor-agent --model gpt-5.1-codex`) | Code/systems-tuned; hunts operational and evidence-chain gaps |

The Claude/institutional read is always written by the orchestrator in-session (no subprocess). Only the non-Claude lenses fan out to CLIs.

### Per-invocation override

The user may remap conversationally:
> *"council adversarial review with Gemini as a COA auditor and Codex as a methodological peer reviewer"*

**Always echo the parsed mapping back before fanning out**, so a misparse can be corrected:
> "Council mapping: A = COA auditor (Gemini), B = methodological peer reviewer (Codex), C = institutional/mandate (Claude, me). Firing A and B now — confirm or correct."

---

## Runner Invocation Reference

These quirks were learned by prototyping. Do not "simplify" them away.

| Runner | Invocation | Quirks |
|--------|-----------|--------|
| **Gemini** | `gemini -p "<prompt>"` | Emits noisy stderr (local Gemma router 500s, ripgrep/MCP warnings) that is **harmless** — capture stdout only (`2>$null`). Response follows the warnings. |
| **Codex** | `$prompt \| codex exec --skip-git-repo-check` | Prompt **must** be piped via stdin. Passing it as an argument makes `codex exec` block waiting on stdin EOF (hangs forever in background). Has a usage cap surfacing as `"hit your usage limit"`. |
| **Cursor** | `cursor-agent --print --output-format text --force --trust --model gpt-5.1-codex "<prompt>"` | **Long-form flags only** on the PowerShell shim (`--print`, not `-p`). Model name is `gpt-5.1-codex` (check `cursor-agent --list-models`), not `gpt-5`. **Requires `cursor-agent login`** — fails with "Authentication required" / "No models available" otherwise. |

All runners exit 0 even on refusal/cap, so **also scan output text** for failure signatures (see the orchestrator script's `Test-RunnerFailure`).

---

## Context Packed Per Persona (Standard depth)

Each fanned-out model receives:
1. The **artifact** (full text, or a faithful summary of key claims for long artifacts)
2. Its **persona brief** (who it is, what it hunts, the voice of its closing line)
3. The orchestrator's **distilled Core Claim**
4. The orchestrator's **Load-Bearing Assumptions**

It does **not** receive the orchestrator's Silences or Evidence-Gap reads. Withholding those keeps each persona's attack independent rather than anchored to the orchestrator's reading — independence is what makes convergence meaningful.

Each model is constrained to the same four-section output:
- What you care about (1 sentence)
- Primary attack vector (2-3 sentences)
- Secondary vulnerabilities (2-3 bullets)
- What you would say (2-4 sentences in persona voice)

---

## Failure Handling: "Proceed, Note"

If a runner errors, times out, hits a cap, or is unauthenticated:
- **Do not** block the report.
- **Do not** fall back to having the orchestrator play that persona — that defeats the council premise (you're back to one model multi-persona, with extra steps).
- **Do** record the persona as `UNAVAILABLE` with the reason, mark it a **known gap**, and proceed with the remaining reads.
- **Do** label convergence as provisional when fewer than all lenses reported.

A 2-of-3 council is still useful. A 1-of-3 council is just standard Interrogation — say so and offer to retry the others.

---

## How to Run It

### Option A — Orchestrator script (preferred for 2+ external runners)

1. Build a JSON job spec (see schema in `scripts/council-adversary-read.ps1`) with the artifact, core claim, assumptions, and persona/runner assignments for the **non-Claude** lenses.
2. Run:
   ```powershell
   .agent/skills/tools-for-thought/scripts/council-adversary-read.ps1 `
       -JobSpec  ".agent/outputs/<date>_council-job.json" `
       -OutFile  ".agent/outputs/<date>_council-reads.md"
   ```
3. The script writes the per-persona reads + a `.status.json` sidecar. Read both.
4. Write the **Claude/institutional** read yourself in-session.
5. Synthesize convergence and the decision menu (orchestrator work — see below).

### Option B — Manual fan-out (1 external runner, or debugging)

Invoke each runner directly per the Runner Invocation Reference, capture output, and assemble Section 5 by hand. Use this when only one lens needs an external model or a runner is misbehaving.

---

## Assembling Report Section 5 (Council variant)

```markdown
### 5. Adversarial Read (Council Mode)

#### Adversary A — [persona label]
**Lens:** [institutional / public / technical] · **Voice from:** [Claude / Gemini / Codex]
[four-section read]

#### Adversary B — [persona label]
**Lens:** [...] · **Voice from:** [...]
[four-section read]

#### Adversary C — [persona label]  ⚠️ UNAVAILABLE if applicable
[read, OR the unavailable note + named known gap]

#### Cross-cutting Convergence (synthesized by orchestrator)
| Vulnerability | A | B | C | Convergence |
|---|---|---|---|---|
| [vuln] | ✓ | ✓ | — | High — two lenses, independent |

**Highest-priority fix:** [the vulnerability multiple independent models attacked first]
```

After Section 5, continue the standard report: Section 6 Decision Menu and the Interrogation Summary, exactly as in `interrogation-mode.md`.

---

## Convergence Synthesis Rules

- **Convergence is the product.** A vulnerability flagged by 2+ independent models outranks any single-model finding, even a sharp one.
- **Preserve unique vectors.** A finding only one lens produced is not noise — it is what that lens was *for* (the institutional lens earning the mandate-overlap read; the public lens earning the broadband-reality read). Keep these; attribute them.
- **Do not merge into one voice.** The whole point of diverging is lost if you blend the three reads into a single paragraph. Stack them, then synthesize convergence *on top*.
- **Flag provisional convergence** when the council ran incomplete (e.g., 2 of 3).

---

## Cost Discipline

- Council Mode is for genuinely high-stakes, going-public artifacts (keynotes, press releases, panel talking points, decision memos) — not routine interrogations.
- Every fan-out triples model spend and adds minutes of latency. The explicit trigger is the cost gate; keep it.
- For short artifacts where one external opinion suffices, prefer standard Interrogation Mode with one optional external read (Option B) over a full council.

---

## Version History
- 2026-05-30: Initial creation. Council Mode added as an opt-in extension of Interrogation Mode (Mode 4). Fixed persona/model defaults with conversational override; standard context depth; proceed-note failure handling; orchestrator fan-out script with per-runner quirk handling.
