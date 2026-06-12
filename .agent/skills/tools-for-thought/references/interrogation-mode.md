# Interrogation Mode: Tools for Thought Protocol

## Why This Mode Exists

The other three modes (Exploration, Development, Refinement) are creation modes — dialogic, interactive, and cognitively engaging in real time. They assume you're building something, and the AI challenges your thinking as you go.

Interrogation Mode is different in kind, not just in timing. It assumes you've already built something — and now you need structured critique before it reaches a real audience.

**Core difference:**
- Refinement asks: *Is this well-expressed?*
- Interrogation asks: *Is this actually right?*

**Relationship to Tools for Thought:** The other three modes earn the "Tool for Thought" label through real-time dialogue — the user thinks alongside the AI. Interrogation Mode complements that approach with a different mechanism: it externalizes the full decision space as a structured report, letting the user engage with critique asynchronously and non-linearly. The cognitive work happens *after* delivery, when the user works through the Decision Menu — not during the interaction itself.

---

## When to Use This Mode

Activate when the user:
- Has an existing artifact (document, report, speech, paper, proposal)
- Wants it challenged, not improved
- Needs to find load-bearing weaknesses before others do
- Is preparing to defend work to a skeptical audience
- Wants to know what they're *not* seeing

**Trigger phrases:**
- "Challenge this."
- "What's wrong with this?"
- "Where would a skeptic attack?"
- "Is this defensible?"
- "What am I missing?"
- "Interrogate this."
- "Let's do an adversarial review."
- "Adversarial review."

---

## What This Mode Does NOT Do

- Does **not** improve expression, tone, or structure (that's Refinement)
- Does **not** summarize the artifact back to the user
- Does **not** validate what's already strong (unless asked)
- Does **not** deliver findings as a sequential chat loop — the report is delivered whole (though the setup phase requires brief user input to identify adversaries and confirm the core claim)

**Key departure from other modes:** Interrogation Mode produces a **single structured artifact** — an Interrogation Report — delivered after a brief setup phase (adversary identification + core claim confirmation). The setup is conversational; the delivery is not. Once the report lands, the user decides which threads to pull.

---

## The Output: Interrogation Report

The Interrogation Report is a markdown document the user can act on asynchronously, share with collaborators, or use as a decision menu for revision.

### Report Structure

```markdown
## Interrogation Report: [Document Title]
**Artifact type:** [Speech / Report / Paper / Proposal / etc.]
**Interrogated by:** Tools for Thought — Interrogation Mode
**Date:** [Date]

---

### 1. Core Claim
What this artifact is actually asserting — stripped of framing, hedging, and structure.
Often differs from what the artifact *says* it's asserting.

> [One to three sentences. Distilled, not quoted.]

**Flag:** Does the artifact know what it's claiming? [Yes / Unclear / No]

---

### 2. Load-Bearing Assumptions
What must be true for the core claim to hold.
These are often unstated. Surface them without judgment, then flag each one.

| Assumption | Status | Notes |
|------------|--------|-------|
| [Assumption 1] | [Stated / Unstated] | [Brief note on how central this is] |
| [Assumption 2] | [Stated / Unstated] | [...] |
| [Assumption 3] | [Stated / Unstated] | [...] |

**Decision Point:** Which assumptions need to be made explicit before this artifact is defensible?

---

### 3. Silences
What the artifact conspicuously does not say.
Not every silence is a problem — but every silence is a choice. Name them.

- **[Topic/Question]** — [Why a skeptic would notice this absence]
- **[Topic/Question]** — [...]
- **[Topic/Question]** — [...]

**Decision Point:** Which silences are strategic (intentional de-emphasis) and which are gaps?

---

### 4. Evidence vs. Claim Gap
Where the evidence supports a weaker version of what's asserted.
Flags overreach, missing premises, and confidence miscalibration.

| Claim in Artifact | What Evidence Actually Supports | Gap Severity |
|-------------------|--------------------------------|--------------|
| [Claim as written] | [Weaker version the evidence supports] | [High / Medium / Low] |
| [...] | [...] | [...] |

**Decision Point:** Which claims need to be walked back, and which need stronger evidence?

---

### 5. Adversarial Read
The strongest attack each identified adversary would make — and where they'd aim first.

**If single adversary persona was identified:**

**Adversary:** [Named persona — e.g., "TP panel reviewer," "COA auditor," "peer reviewer"]
**Primary attack vector:** [The most vulnerable point from this adversary's perspective]

**Secondary vulnerabilities:**
- [Vulnerability 2]
- [Vulnerability 3]

**What the adversary would say:** [Two to four sentences in the voice of the skeptic]

**Decision Point:** Do you address this proactively, or does addressing it change your argument fundamentally?

**If multiple adversary personas were identified:**

Produce a separate adversarial read per persona. Each follows the same structure:

#### Adversary A: [Named persona]
**What they care about:** [One sentence — e.g., "Methodological rigor and reproducibility"]
**Primary attack vector:** [Most vulnerable point from their perspective]
**What they would say:** [Two to four sentences in their voice]

#### Adversary B: [Named persona]
**What they care about:** [One sentence]
**Primary attack vector:** [Most vulnerable point from their perspective]
**What they would say:** [Two to four sentences in their voice]

*(Repeat for each identified adversary. Cap at 3-4 personas to keep the report actionable.)*

**Cross-cutting Decision Point:** Where do the adversaries' attacks converge? Convergence points are the highest-priority fixes — they're vulnerable from multiple angles.

> **Council Mode (opt-in):** When the user explicitly requests a "council adversarial review," the per-persona reads in this section are produced by *different AI models* (Claude, Gemini, Codex/GPT) rather than the orchestrator alone — so convergence reflects independent model cognition, not one model agreeing with itself. Council Mode changes only this section; everything else in the protocol is unchanged. See [[council-mode.md]] for mapping, runner invocation, and failure handling. Each council read is attributed (`**Voice from:** [model]`).

---

### 6. Decision Menu
Specific choices the author needs to make before this artifact is defensible.
Ordered by urgency.

| # | Decision | Options | Stakes |
|---|----------|---------|--------|
| 1 | [What needs to be decided] | [Option A / Option B] | [What's at risk if left unresolved] |
| 2 | [...] | [...] | [...] |
| 3 | [...] | [...] | [...] |

---

### Interrogation Summary
**Strongest element:** [What holds up under pressure]
**Most urgent fix:** [The one thing that must be resolved]
**Overall defensibility:** [High / Medium / Low — with one sentence explanation]
```

---

## How to Conduct the Interrogation

### Step 0: Preliminary Scan
Before committing to a full report, read the artifact once and assess whether it warrants full interrogation. Not every finished artifact needs seven sections of critique.

**Triage outcomes:**
- **Full report:** The artifact has a debatable core claim, multiple assumptions, identifiable adversaries. Proceed with all steps.
- **Abbreviated report:** The artifact is generally well-constructed but has 1-2 specific vulnerabilities. Produce a focused report: Core Claim + the relevant sections (often Silences and/or Evidence vs. Claim Gap) + Decision Menu. Skip sections that would only produce "low severity" rows.
- **Redirect:** The artifact isn't finished enough for interrogation — it needs Development or Refinement first. Say so and offer to switch modes.

**Tell the user which triage outcome you've chosen and why** before proceeding. If abbreviated, name which sections you're skipping and why they're not load-bearing for this artifact.

### Step 1: Read Without Charity
Read the artifact as a skeptic, not as a collaborator. Assume the author is wrong until proven otherwise. Do not validate what's working — focus entirely on what's vulnerable.

### Step 2: Identify the Adversary Persona(s)
Before proceeding, establish *who* will challenge this artifact. Different audiences attack differently — a peer reviewer hunts methodological flaws, an auditor hunts procurement justification gaps, a legislative committee hunts overclaimed outcomes, an external partner hunts unclear commitments.

**Why named adversaries matter:** A generic "skeptic" produces generic findings ("the argument could be stronger"). A named adversary has specific concerns, institutional incentives, and a particular angle of attack. A COA auditor hunts procurement justification gaps — they don't care about prose quality. A peer reviewer hunts methodological flaws — they don't care about budget alignment. Naming the adversary constrains the adversarial read to the attack vectors that actually matter for this artifact's real audience.

**Ask the user:** *"Who is the toughest audience for this? Who are you most worried about?"*

If the user names a specific audience (e.g., "TP panel," "COA auditor," "the Undersecretary"), adopt that persona for the adversarial read. If the user names multiple audiences, the report will produce multiple adversarial reads (see Section 5).

If the user doesn't specify, infer from the artifact type and context:
- Academic paper → peer reviewer who wants to reject
- Budget/procurement document → auditor looking for red flags
- Policy proposal → skeptical official or legislative staffer
- Technical report → stakeholder who already disagrees with the conclusion
- Speech/remarks → journalist pulling one quote; skeptical official in the front row

**Do not skip this step.** A generic "skeptic" produces a generic adversarial read. Named adversaries produce actionable findings.

### Step 3: Distill the Core Claim
Before anything else, answer: *What is this artifact actually claiming?* Strip away structure, context, and hedging. If the core claim is unclear, that is itself the primary finding.

**Confirmation step:** Before proceeding, surface the distilled claim to the user in one to three sentences and ask: *"Is this what you're claiming?"* The entire report rests on this distillation. A misread core claim produces a report that is thorough but wrong. Wait for confirmation or correction before building the rest of the report.

### Step 4: Surface Assumptions Systematically
Work through the artifact's logic chain. At each step, ask: *What has to be true for this to follow?* Distinguish between:
- **Stated assumptions** (acknowledged by the author)
- **Unstated assumptions** (taken for granted)
- **Contested assumptions** (areas where reasonable people disagree)

### Step 5: Hunt the Silences
Ask: *What would a hostile reader notice is missing?* Common silences include:
- Counterarguments the author chose not to engage
- Data that would complicate the narrative
- Stakeholders whose perspectives are absent
- Implications the author avoids drawing

### Step 6: Calibrate Evidence to Claims
For each major claim, ask: *Does the evidence actually support this, or a weaker version?* Flag overreach. Note where confidence language ("clearly demonstrates," "proves," "shows") exceeds what the evidence can bear.

### Step 7: Write the Adversarial Read
Adopt the voice of each adversary persona identified in Step 2. For each persona, identify their primary attack vector — the single point most likely to be challenged from their specific perspective — and secondary vulnerabilities. Make the attack concrete, not abstract.

**Single persona:** Write one adversarial read with primary attack, secondary vulnerabilities, and the adversary's voice.

**Multiple personas:** Write a separate adversarial read per persona (capped at 3-4). After all individual reads, identify convergence points — vulnerabilities that multiple adversaries would independently target. These are the highest-priority findings.

**Council Mode (opt-in, explicit trigger only):** If the user requested a "council adversarial review," delegate the non-Claude persona reads to other AI models via their CLIs instead of writing every persona yourself. The orchestrator still writes the institutional/Claude persona in-session and still performs all other steps. Default mapping: institutional → Claude, external/public → Gemini, technical → Codex or Cursor (`gpt-5.1-codex`); override conversationally and echo the mapping back before dispatch. Use the fan-out script for 2+ external runners. Failed runners are marked UNAVAILABLE and the report proceeds (proceed-note rule). Full protocol: [[council-mode.md]].

### Step 8: Build the Decision Menu
Translate findings into decisions the author must make. Each item in the decision menu should be:
- **Specific** (not "strengthen your argument" but "choose: walk back Claim 3, or provide evidence X")
- **Actionable** (a choice the user can actually make)
- **Consequential** (leaving it unresolved has identifiable stakes)

---

## After the Report: What Comes Next

The Interrogation Report is a starting point, not an endpoint. Once delivered, one of three paths follows:

**Path 1: Revise and re-interrogate.** User addresses the Decision Menu items, produces a revised artifact, and runs Interrogation Mode again. Use when the findings are fundamental — core claim is wrong, key assumptions are unstated, adversarial read exposes a structural problem.

**Path 2: Move to Refinement Mode.** User accepts the findings, makes decisions, and wants to strengthen expression. Use when the interrogation confirms the argument is sound but surface-level issues remain.

**Path 3: Dialogue on a specific finding.** User wants to go deeper on one section of the report — interrogate an assumption, stress-test the adversarial read, or think through a specific decision. Use the Decision Menu item as the entry point for a focused conversation.

If the user is unsure which path to take, the Interrogation Summary's "Most urgent fix" is the deciding signal: if it points to argument structure, Path 1. If it points to expression, Path 2. If it points to a specific unresolved question, Path 3.

---

## Adaptation by Content Type

### Speeches and Remarks
- Core claim: What is the ONE message that survives if nothing else lands?
- Key silence to hunt: What commitment is implied but not stated explicitly?
- Adversarial read: The journalist who will pull one quote. The skeptical official in the front row.

### Academic Papers
- Core claim: What is the actual contribution — not the stated contribution?
- Key silence to hunt: What counterevidence or alternative explanation is not engaged?
- Adversarial read: The peer reviewer who wants to reject this.

### Technical Reports
- Core claim: What decision does this report support, and does it earn that recommendation?
- Key silence to hunt: What does the data show that the interpretation doesn't address?
- Adversarial read: The stakeholder in the room who already disagrees with the conclusion.

### Proposals and Pitches
- Core claim: What is being promised, and to whom?
- Key silence to hunt: What risk is not named?
- Adversarial read: The evaluator looking for reasons to reject.

---

## Relationship to Other Modes

| Mode | Entry Point | Output | Primary Question |
|------|-------------|--------|-----------------|
| Exploration | No artifact | Framings and tensions | What am I actually trying to say? |
| Development | Outline or direction | Challenged arguments | Does this hold together? |
| Refinement | Draft | Polished expression | Is this well-expressed? |
| **Interrogation** | **Finished artifact** | **Interrogation Report** | **Is this actually right?** |

Interrogation Mode can precede Refinement — but it should never be skipped in favor of Refinement. Polishing a flawed argument makes it worse, not better.

---

## Design Principles

**Multi-turn setup, single-artifact delivery.** The interaction has two phases: a brief conversational setup (adversary identification, core claim confirmation, triage) and a single-artifact delivery (the report). The setup phase typically requires 2-3 exchanges before the report is built. The working hypothesis is that externalizing the full decision space at once serves users better than sequential dialogue when the artifact is already finished: it allows async review, sharing with collaborators, and non-linear engagement. This is a design choice with a real tradeoff — dialogue-based challenge may surface things a single-pass report misses. If the report feels incomplete, transition to a dialogue using the Decision Menu as the starting point.

**Sequential within, non-linear for the user.** The interrogation follows a fixed sequence internally (claim → assumptions → silences → evidence → adversarial read → decisions). But the user can enter the report at any section and act on it in any order.

**Decisions, not verdicts.** The report surfaces choices — it does not tell the user what to do. Every finding translates into a decision point. The user retains authorship.

**Productive, not punishing — as tone, not structure.** The interrogation does not open with validation, and it does not soften findings. But the voice throughout is that of a trusted colleague asking hard questions before the real audience does — not an adversary. Concretely: findings are stated plainly, not dramatically. Vulnerabilities are named without editorializing. The Decision Menu offers choices, not verdicts. The goal is that the user finishes the report feeling equipped, not defeated.

---

## Anti-Patterns to Avoid

### ❌ Validating before interrogating
Do not open with what works. That signals the interrogation will be gentle. It won't be useful.

### ❌ Vague findings
"The argument could be stronger" is not a finding. "Claim 3 depends on an assumption that Recommendation 2 contradicts" is a finding.

### ❌ Delivering provocations sequentially
Do not ask one question, wait for a response, then ask another. That is Refinement mode behavior. Interrogation Mode delivers the full report at once.

### ❌ Fixing instead of flagging
The report identifies vulnerabilities. It does not fix them. Fixing is the user's work.

### ❌ Ignoring the decision menu
Every finding must translate into a decision. A finding without a decision point is just criticism.

---

## When This Mode Fails

Interrogation Mode is not universally applicable. Recognize these failure conditions:

### Artifacts that resist interrogation
- **Purely informational documents** (meeting minutes, event summaries, inventories). These have no core claim to interrogate. If the user asks for interrogation, redirect: "This is a record, not an argument. What claim do you think is implicit in it?"
- **Highly personal or creative writing** (essays, reflections, narratives). The protocol's assumption-hunting and evidence-calibration steps don't map to work that isn't making truth-claims.
- **Composite documents with no unifying claim** (annual reports, portfolio compilations). The protocol assumes one core claim; composite documents have many. Either interrogate each section as a separate artifact or acknowledge the protocol doesn't scale to this format.

### When the protocol produces unhelpful output
- **Artifact is well-constructed:** The report generates low-severity findings across most sections because the protocol structurally generates findings. This is the purpose of the Preliminary Scan (Step 0) — triage to an abbreviated report when a full report would be padding.
- **Core claim is genuinely unclear:** Step 3 asks the user to confirm the distilled claim, but some artifacts are confused about what they're claiming. If the user can't confirm after two attempts, that *is* the primary finding — deliver an abbreviated report focused on Section 1 (Core Claim) and Section 6 (Decision Menu), and recommend the user return to Development Mode.
- **Adversary persona is too generic:** If the user says "just anyone" or "a general audience," the adversarial read will be generic. Push back once: "The more specific the adversary, the more actionable the findings. Can you name one person or role?" If they can't, proceed but note the limitation in the report.

### When the format is wrong
- **User wants dialogue, not a report:** Some users arrive with "challenge this" but actually want a back-and-forth conversation. If the user starts responding to individual findings before the report is complete, or says "wait, let me explain," they want Refinement Mode with harder questions — not Interrogation Mode. Offer to switch.
- **Artifact is too early-stage:** The user thinks it's finished but the triage reveals it's still in Development. Redirect explicitly rather than producing a report that's really a Development Mode critique dressed in Interrogation Mode clothing.

---

## Scaling the Report

The full seven-section report is calibrated for medium-length artifacts (5-20 pages) with a debatable core claim and identifiable adversaries. Adapt for other scales:

### Short artifacts (1-4 pages: memos, talking points, abstracts)
- Use abbreviated format: Core Claim + the 1-2 most relevant middle sections + Decision Menu
- The Interrogation Summary alone may be sufficient
- Typical report length: 300-600 words

### Medium artifacts (5-20 pages: reports, papers, proposals)
- Full report is appropriate
- All seven sections
- Typical report length: 800-1500 words

### Long artifacts (20+ pages: research papers, policy documents, multi-chapter reports)
- Consider interrogating the executive summary / abstract separately from the full document
- For composite documents, identify the 2-3 highest-stakes sections and interrogate those
- The full report should still be one document, but note which sections of the artifact each finding refers to
- Typical report length: 1200-2000 words (longer reports don't help — they just move the cognitive load from the artifact to the critique)

---

## Version History
- 2026-05-30: Added Council Mode hooks — Step 7 council-delegation note and Section 5 attribution note; cross-links to new `council-mode.md`. Council Mode is an opt-in, explicit-trigger extension that fans the adversarial read out to multiple AI models; all other steps unchanged.
- 2026-04-04b: Meta-interrogation fixes — reframed TfT relationship (Interrogation as structured critique complement); resolved single-artifact vs. conversation tension (multi-turn setup acknowledged); added Step 0 (Preliminary Scan) with triage; added "When This Mode Fails" section; added "Scaling the Report" section; justified named adversary personas; synced with workflow-modes.md, SKILL.md, and README.md
- 2026-04-04: Added Step 2 (Identify Adversary Personas); revised Section 5 and Step 7 for multi-vector adversarial reads; added "adversarial review" trigger phrases; renumbered steps 2-7 → 3-8
- 2026-02-18: Initial creation — Interrogation Mode added as Mode 4
- 2026-02-18: Revised post-interrogation — applied five decisions: single-artifact reframed as hypothesis (D1A), core claim confirmation step added (D2A), post-report workflow added (D3B), productive-not-punishing reframed as tone guidance (D4B), Promptions integration deferred (D5B)
