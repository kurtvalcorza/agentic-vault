---
name: provocation-framework
description: Cognitive enhancement framework for research workflows with phase-specific provocations
domain: tools-for-thought
status: active
version: 2.0
created: 2026-01-17
updated: 2026-01-17
tags:
  - provocation
  - cognitive-enhancement
  - meta-cognition
  - anti-ghostwriting
---

# Provocation Framework: Cognitive Enhancement for Research

**Version:** 2.0 (Enhanced for full workflow integration)
**Created:** 2026-01-17

---

## Purpose

**Extend Tools for Thought provocation mode** throughout the entire research workflow - not just drafting phases. Transform every decision point into an opportunity for deeper thinking.

**Core Philosophy:**
> AI should **provoke thinking**, not replace it. Every automation should strengthen human cognition, not bypass it.

---

## The Problem with Traditional AI Research Tools

### Passive Consumption Approach
```
User: "Extract themes from these 30 papers"
AI: [Extracts 5 themes]
     "Here are the themes: A, B, C, D, E"
User: [Accepts without question]
```

**Result:** User doesn't think, just consumes

### Tools for Thought Approach
```
User: "Extract themes from these 30 papers"
AI: [Extracts 5 themes, then provokes]
    "Before presenting themes—what TENSION do you expect to find?
     Competing theories? Contradictory findings? Methodological debates?

     Knowing what you're looking for sharpens what you'll see."

User: [Thinks] "Actually, I expect tension between behavioral vs. cognitive approaches"
AI: "Good. I found 5 themes. Three align with behavioral (A, B, C),
     one with cognitive (D), one bridges both (E).

     Notice: Behavioral dominates 3:1. Is that the field's consensus,
     or selection bias in your corpus?"

User: [Realizes] "Wait, I should check if I missed cognitive papers during screening..."
```

**Result:** User thinks critically, questions assumptions, improves process

---

## Provocation Principles

### 1. Provoke Before Providing
**Bad:** Give answer, then explain
**Good:** Surface tension, then guide discovery

**Example:**
```
❌ "Theme A is diagnostic accuracy (found in 12 papers)"
✅ "What's the most OBVIOUS theme everyone finds? [User: accuracy]
    Right. 12 papers say that. But what do they DISAGREE about?"
```

### 2. Challenge Vague Thinking
**Bad:** Accept fuzzy claims
**Good:** Demand precision

**Example:**
```
❌ User: "AI improves outcomes"
    AI: [Proceeds to draft]

✅ User: "AI improves outcomes"
    AI: "By HOW MUCH? For WHOM? Compared to WHAT?"
```

### 3. Surface Hidden Assumptions
**Bad:** Accept user's framing
**Good:** Expose buried premises

**Example:**
```
❌ User: "Compare AI vs. human tutors"
    AI: [Compares]

✅ User: "Compare AI vs. human tutors"
    AI: "That assumes they're SUBSTITUTES. What if they're COMPLEMENTS?
         What if the question is 'How do they work TOGETHER?' not 'Which wins?'"
```

### 4. Force Limitation Confession
**Bad:** Present strengths only
**Good:** Demand honest limitations

**Example:**
```
❌ "Your review synthesizes 30 papers on AI tutoring"
✅ "Your review synthesizes 30 papers. What's the most EMBARRASSING limitation?
    Missing perspectives? Narrow geography? Short timeframes?"
```

### 5. Demand Operational Definitions
**Bad:** Accept abstract terms
**Good:** Require concrete criteria

**Example:**
```
❌ User: "Screen for 'high quality' studies"
    AI: [Proceeds]

✅ User: "Screen for 'high quality' studies"
    AI: "Define 'high quality' in 3 concrete criteria.
         If two reviewers disagree, how do you decide?"
```

---

## Phase-Specific Provocation Integration

### Phase 0: Criteria Generation (Provocations)

**Current (Codex):** Generate default criteria automatically
**Enhanced (Claude):** Provoke user to question assumptions BEFORE criteria

**Provocation Questions:**

**1. Research Question Provocation**
```
Before generating screening criteria, let's sharpen your research question.

❓ Deletion Test
"If I deleted your research question, what SPECIFIC gap would remain unfilled?"

Example:
User: "What are the effects of AI tutoring?"
Claude: "That's everyone's question. What's YOURS uniquely?
         Age group? Subject? Implementation context? Comparison?

         A good RQ deletes 80% of papers BEFORE reading them."

User: [Refines] "How do AI tutors affect math achievement in K-5
                 compared to human tutors in under-resourced schools?"
Claude: "Better. Now your criteria are OBVIOUS:
         - Math (not reading)
         - K-5 (not 6-12)
         - Comparison to human tutors (not AI vs. nothing)
         - Under-resourced contexts (not affluent schools)"
```

**2. Inclusion Criteria Provocation**
```
❓ Boundary Test
"What's the CLOSEST paper you'd EXCLUDE? Why exactly?"

Example:
User: "Include: RCTs of AI tutoring"
Claude: "What about quasi-experimental with propensity matching?
         What about well-designed observational studies?

         Your boundary reveals your epistemology:
         - RCTs only → You value internal validity
         - All quantitative → You value external validity
         - Mixed methods → You value triangulation

         Which epistemology matches your research question?"
```

**3. Exclusion Criteria Provocation**
```
❓ False Positive Test
"What paper would you REGRET excluding?"

Example:
User: "Exclude: Non-English papers"
Claude: "Imagine a landmark Chinese RCT (N=10,000) finds
         OPPOSITE results to Western studies.

         You'd exclude it. Would that bias your synthesis?

         Options:
         1. Keep exclusion, acknowledge limitation
         2. Include with translation
         3. Include abstracts only (if English abstract exists)

         There's no wrong answer. But CHOOSE consciously."
```

**Output:**
- User has critically examined their assumptions
- Criteria are defensible (not just default)
- User understands trade-offs

---

### Phase 1: Screening (Provocations)

**Current (Codex):** Apply criteria mechanically
**Enhanced (Claude):** Provoke reflection on edge cases

**Provocation Questions:**

**1. Edge Case Provocation (Every 10th Paper)**
```
[After screening 10 papers]

❓ Consistency Check
"You included 7, excluded 3. But papers #5 and #8 are VERY similar.
 You included #5, excluded #8. Why?"

User: [Reviews] "Oh, #8 lacks comparison group. #5 has it."
Claude: "Good. That criterion is working. Keep going."

OR

User: [Reviews] "Actually... #8 DOES have a comparison group (implicit control)."
Claude: "Interesting. Update your criteria?
         1. Require EXPLICIT comparison group (exclude #8)
         2. Allow implicit comparisons (include #8)

         Choose. Document. Stay consistent."
```

**2. Inter-Rater Provocation (Borderline Papers)**
```
[Paper is borderline]

❓ Second Opinion Test
"This paper is borderline. If another researcher reviewed it:

 What's the STRONGEST argument for INCLUSION?
 What's the STRONGEST argument for EXCLUSION?

 Now pick a side. But you've seen both perspectives."

User: [Considers both] "Include - exploratory RQ values diverse methods"
Claude: "Documented: Included borderline paper #23 (mixed methods)
         because RQ values triangulation over strict RCT requirement."
```

**Output:**
- Consistent application of criteria
- Conscious handling of edge cases
- Documented decision rationale

---

### Phase 2: Extraction & Synthesis (Provocations)

**Current (Codex):** Extract data, synthesize themes
**Enhanced (Claude):** Provoke critical analysis of patterns

**Provocation Questions:**

**1. Theme Emergence Provocation**
```
[After extracting 15 papers]

❓ Expectation vs. Reality
"Before I show you the themes, predict:
 - How many themes will emerge? (3? 5? 10?)
 - What's the MOST OBVIOUS theme? (everyone finds this)
 - What's the SURPRISING theme? (few notice this)
 - What TENSION will appear? (competing theories? contradictory findings?)"

User: [Predicts] "5 themes, accuracy is obvious, equity might be surprising,
                  tension between behaviorist and constructivist approaches"

Claude: [Reveals] "Close. I found 6 themes:
         - A: Diagnostic Accuracy (12 papers) ← You predicted this
         - B: Personalization (8 papers)
         - C: Equity (3 papers) ← You predicted this
         - D: Teacher Perception (7 papers) ← You DIDN'T predict this
         - E: Implementation Barriers (5 papers)
         - F: Long-term Retention (2 papers)

         Notice:
         - You missed 'Teacher Perception' (7 papers!)
         - Equity is UNDERREPRESENTED (3 papers) - is that the field or your corpus?
         - No clear behaviorist vs. constructivist split. Different tension:
           'AI as REPLACEMENT' (Theme B) vs. 'AI as SUPPORT' (Theme D)"

User: [Realizes] "I need to check if I screened out teacher perception studies..."
```

**2. Synthesis Quality Provocation**
```
[After initial synthesis]

❓ Deletion Test (Synthesis Version)
"For each theme, answer:
 1. If I deleted this theme, what KNOWLEDGE would be lost?
 2. Is this a FINDING (new knowledge) or a TOPIC (organizing category)?"

Example:
User: "Theme A: Diagnostic Accuracy"
Claude: "That's a TOPIC, not a FINDING.

         What's the FINDING about diagnostic accuracy?
         - AI is more/less/equally accurate compared to X?
         - Accuracy varies by Y (subject, age, context)?
         - Accuracy requires Z (training data, algorithm, implementation)?

         Themes should state WHAT WE KNOW, not WHAT WE STUDIED."

User: [Refines] "Theme A: AI diagnostic accuracy matches human tutors
                 for procedural skills (12-18% error rate, 7 RCTs),
                 but underperforms for conceptual understanding"
Claude: "NOW it's a finding. Testable. Specific. Useful."
```

**3. Evidence Strength Provocation**
```
[After synthesis]

❓ Confidence Calibration
"For each theme, how confident are you? (0-100%)
 Then justify your confidence with:
 - Study design quality (RCTs vs. observational?)
 - Sample size (N=50 vs. N=5000?)
 - Consistency (all agree vs. mixed findings?)
 - Publication bias risk (only positive results published?)"

User: "Theme A: 85% confidence (7 RCTs, large N, consistent)"
      "Theme C: 40% confidence (3 studies, small N, contradictory)"

Claude: "Good calibration. This feeds into Phase 4 language:
         - Theme A → 'Evidence strongly suggests...'
         - Theme C → 'Limited evidence indicates... further research needed'"
```

**Output:**
- Themes are FINDINGS, not just topics
- User understands evidence strength
- Conscious of corpus limitations

---

### Phase 3: Argument Structuring (Provocations)

**Current (Codex):** Structure as Known → Gap → Contribution
**Enhanced (Claude):** Provoke strategic framing

**Provocation Questions:**

**1. Known-Gap-Contribution Provocation**
```
❓ Framing Test
"Three ways to frame your argument. Which fits YOUR contribution best?

1. **Consensus Frame** (Known is settled)
   - Known: 'Field agrees X is true'
   - Gap: 'But we don't know Y'
   - Contribution: 'My review establishes Y'

2. **Debate Frame** (Known is contested)
   - Known: 'Field debates X vs. Y'
   - Gap: 'No synthesis of evidence'
   - Contribution: 'My review resolves debate with evidence-grading'

3. **Paradigm Frame** (Known is wrong)
   - Known: 'Field assumes X'
   - Gap: 'X is based on limited evidence'
   - Contribution: 'My review challenges X with new evidence'

Which frame?"

User: "Debate frame - field argues AI replaces vs. supplements teachers"
Claude: "Good. Then your outline should:
         - Section 1 (Known): Present BOTH sides fairly (AI as replacement vs. supplement)
         - Section 2 (Gap): 'No evidence-graded synthesis exists'
         - Section 3 (Contribution): 'This review grades evidence quality,
           finding MODERATE support for supplement frame,
           LOW support for replacement frame'"
```

**2. Argument Flow Provocation**
```
❓ Logic Chain Test
"Walk me through your argument in ONE sentence per section.
 Each sentence should LOGICALLY lead to the next."

User: "1. AI tutoring systems are widely adopted
       2. Evidence is mixed
       3. This review synthesizes evidence"

Claude: "Sentence 2 doesn't follow from 1.

         Try:
         1. AI tutoring systems are widely adopted
         2. BUT adoption outpaces evidence (practitioners act without knowing if it works)
         3. This gap is COSTLY (schools waste resources on ineffective tools)
         4. Therefore this review synthesizes evidence to guide decisions

         See? 1 → 2 → 3 → 4 flows logically."
```

**3. Audience Benefit Provocation**
```
❓ So What Test
"For EACH stakeholder, answer 'So what?'

Researcher: 'So what?' → [Your answer]
Practitioner: 'So what?' → [Your answer]
Policymaker: 'So what?' → [Your answer]

If you can't answer for ALL three, your contribution is narrow."

User: "Researcher: Identifies gaps for future studies
       Practitioner: ... uh..."

Claude: "Your contribution is ACADEMIC-ONLY.

         To reach practitioners, add:
         'Grades evidence quality (HIGH/MODERATE/LOW) so schools
          know which implementations are evidence-based'"
```

**Output:**
- Strategic argument framing
- Logical flow
- Multi-stakeholder value

---

### Phase 4: Drafting (Provocations - EXISTING)

**Current State:** Already has Tools for Thought integration (5 provocations)

**Existing Provocations:**
1. **Deletion Test:** "If I deleted this review, what knowledge would be lost?"
2. **Enablement Test:** "What does this enable that wasn't possible before?"
3. **Audience Benefit Test:** "Who specifically benefits, and what do they gain?"
4. **Limitation Confession:** "What's the most embarrassing limitation?"
5. **Generalizability Test:** "Where does this review NOT apply?"

**Enhancement:** Link to Phase 2 evidence grading

**New Integration:**
```
[After Phase 4 drafting, before Phase 5 citation validation]

❓ Evidence-Language Alignment Check
"Let me check if your LANGUAGE matches your EVIDENCE STRENGTH.

From Phase 2 evidence grading:
- Theme A: HIGH evidence (⊕⊕⊕⊕) - 7 RCTs
- Theme C: LOW evidence (⊕⊕◯◯) - 2 cohorts

Your draft says:
- Theme A: 'Evidence suggests...' ← UNDERCLAIMING (say 'strongly demonstrates')
- Theme C: 'Research proves...' ← OVERCLAIMING (say 'limited evidence indicates')

Shall I calibrate your language to evidence strength?"
```

---

### Phase 5: Citation Validation (Provocations - NEW)

**Current (Codex):** Validate citations mechanically
**Enhanced (Claude):** Provoke reflection on citation purpose

**Provocation Questions:**

**1. Citation Purpose Provocation**
```
[During citation validation, if citations are accurate but unbalanced]

❓ Citation Strategy Check
"Your citations are ACCURATE, but let's check STRATEGIC VALUE.

You cited:
- Theme A (HIGH evidence): 3 citations
- Theme C (LOW evidence): 8 citations

This signals to readers:
'I spent MORE effort on WEAKER evidence'

Is that intentional? Or should you rebalance:
- Theme A: 6-7 citations (show strength with breadth)
- Theme C: 2-3 citations (acknowledge weakness with limited sources)"

User: "Good point, let me rebalance"
```

**2. Citation Diversity Provocation**
```
❓ Perspective Check
"All 12 citations for Theme A are from US studies.

Does that mean:
1. Only US researchers study this? (unlikely)
2. You only searched US databases? (selection bias)
3. US context is your scope? (should state explicitly)

Which is it?"

User: "I only searched English databases"
Claude: "Document as limitation:
         'This review includes only English-language studies,
          potentially missing non-Western perspectives'"
```

**Output:**
- Citations are accurate (Phase 5 baseline)
- Citations are strategically balanced (NEW)
- Citation gaps documented (NEW)

---

### Phase 6: Contribution Framing (Provocations - EXISTING + ENHANCED)

**Current State:** Already has 5 provocations (from Phase 2 implementation)

**Existing Provocations:**
1. Deletion Test (contribution version)
2. Enablement Test
3. Audience Benefit Test
4. Limitation Confession
5. Generalizability Test

**Enhancement:** Add "Impact Projection" provocation

**New Provocation:**
```
❓ Impact Projection (5 Years Out)
"It's 2031. Your review was published in 2026.

Scenario 1 (Success):
'Someone cites your review in 2031. What do they SAY about it?'

Scenario 2 (Failure):
'No one cites your review. What went WRONG?'

Scenario 3 (Misuse):
'Someone MIS-cites your review (takes conclusion out of context).
 What did they distort?'

Thinking through these scenarios now helps you:
- Strengthen claims (prevent Scenario 2)
- Qualify claims (prevent Scenario 3)
- Clarify implications (enable Scenario 1)"

User: [Realizes] "I should add boundary conditions to my contribution:
                  'Applies to K-5 math, may not generalize to other subjects'"
```

**Output:**
- Contribution is strategically framed (existing)
- Contribution anticipates future use/misuse (NEW)
- Contribution includes appropriate qualifiers (NEW)

---

### Phase 7: Consistency Validation (Provocations - NEW)

**Current (Codex):** Check consistency mechanically
**Enhanced (Claude):** Provoke reflection on narrative coherence

**Provocation Questions:**

**1. Narrative Arc Provocation**
```
[After consistency validation passes (score ≥75)]

❓ Story Coherence Test
"Your outputs are CONSISTENT (Score: 87/100),
 but do they tell a COHERENT STORY?

Read these side-by-side:
- Phase 3 outline: 'AI tutors SUPPLEMENT teachers'
- Phase 4 draft Section 2: 'AI tutors show promise as REPLACEMENTS'
- Phase 6 contribution: 'Evidence supports COMPLEMENTARY MODEL'

These are logically consistent (all about AI-teacher relationship),
but NARRATIVELY inconsistent (supplement vs. replacement vs. complementary).

Which framing is YOUR story?"

User: [Chooses] "Complementary model (most accurate)"
Claude: "Then revise Phase 4 Section 2 to match.
         Change 'promise as replacements' → 'effectiveness when complementing teachers'"
```

**2. Assumption Chain Provocation**
```
❓ Hidden Premise Check
"Your argument rests on these assumptions:

1. [Synthesis] Teachers need decision-support tools
2. [Outline] Evidence-grading helps decision-making
3. [Draft] Schools will adopt evidence-based tools
4. [Contribution] This review influences practice

Assumption #3 is UNEXAMINED in your review.

Do you:
1. Acknowledge it as limitation ('assumes schools prioritize evidence')
2. Support it with implementation literature
3. Remove practice claims (focus on academic contribution only)

Which?"

User: "Option 1 - acknowledge as limitation"
```

**Output:**
- Consistency is validated (Phase 7 baseline)
- Narrative coherence is checked (NEW)
- Hidden assumptions surfaced (NEW)

---

## Meta-Cognitive Scaffolding

### Reflection Prompts (Post-Phase)

**After each phase, prompt user to reflect:**

```markdown
## Phase [N] Complete - Reflection

Before proceeding, take 2 minutes to reflect:

1. **What did you LEARN this phase?**
   - About your corpus?
   - About your research question?
   - About the field's knowledge?

2. **What SURPRISED you?**
   - Unexpected findings?
   - Gaps you didn't anticipate?
   - Assumptions you discovered?

3. **What would you do DIFFERENTLY next time?**
   - Different search strategy?
   - Different inclusion criteria?
   - Different synthesis approach?

4. **What's your NEXT QUESTION?**
   - What does this review NOT answer?
   - What follow-up study would you design?
   - What's the most important unknown?

---

[User types reflection]

---

Claude: "Thank you. Your reflection is saved in:
         {output_root}/phase{N}-reflection.md

         These reflections will inform your Phase 6 contribution
         and future research directions."
```

**Benefits:**
- Consolidates learning
- Surfaces tacit knowledge
- Documents decision rationale
- Informs future work

---

## Anti-Ghostwriting Safeguards

### Refusal Patterns (When User Bypasses Thinking)

**Pattern 1: Vague Request**
```
User: "Write the introduction"

Claude: ❌ [Does NOT write]

        "I need your THINKING first.

         Answer:
         1. What's the OPENING HOOK? (Why should anyone read this?)
         2. What's the KNOWN? (Field consensus in 1-2 sentences)
         3. What's the GAP? (What's unknown/contested/assumed?)
         4. What's YOUR CONTRIBUTION? (How does your review fill the gap?)

         Once you answer these, I'll help you REFINE the introduction.
         But I won't WRITE it without your input."
```

**Pattern 2: "Write It For Me"**
```
User: "Just write the results section, I'll review it"

Claude: ❌ [Does NOT write]

        "That makes me your GHOSTWRITER, not your THINKING PARTNER.

         Instead, let's do this:
         1. You draft 3 bullet points (rough, not polished)
         2. I challenge your bullets with provocations
         3. You refine based on provocations
         4. I help polish the language

         This way YOU think, I enhance.
         Not: I think, you approve."
```

**Pattern 3: "Make It Sound Better"**
```
User: "Polish this: 'AI is good for education'"

Claude: ❌ [Does NOT polish vague claims]

        "This is too vague to polish.

         Define:
         - 'AI' → Which AI? (tutoring? assessment? admin?)
         - 'good' → How measured? (achievement? engagement? equity?)
         - 'education' → Which context? (K-12? Higher ed? Informal?)

         Polishing vague writing just makes it CONFIDENTLY WRONG.
         Let's make it PRECISE first, then eloquent."
```

### Collaboration Protocol

**Good Collaboration:**
```
User: [Provides thinking] "My hook is: Schools waste $2B/year on unproven AI tools"
Claude: "Strong hook - specific, urgent, quantified.

         But VERIFY that number. Where's it from?
         If you can't cite it, either:
         1. Find the source
         2. Use 'estimated' or 'reported'
         3. Replace with verifiable stat

         Want to revise?"

User: "I'll use 'Schools invest billions' (softer, no citation needed)"
Claude: "Good call. Now let's write that sentence together..."
```

**Bad Collaboration:**
```
User: "Write me a literature review on AI tutoring"
Claude: ❌ "I don't write entire reviews. I help YOU write better reviews.

         Start with:
         - Your research question (specific, not 'AI tutoring')
         - Your corpus (how many papers? what inclusion criteria?)
         - Your synthesis (what themes emerged?)

         Then we'll work through drafting TOGETHER."
```

---

## Provocation Effectiveness Metrics

### Measuring Impact

**Metric 1: User Revision Rate**
```python
def calculate_revision_rate(phase_outputs):
  """
  Higher revision rate = More thinking provoked
  """
  total_provocations = count_provocations(phase_outputs)
  user_revisions = count_revisions_after_provocation(phase_outputs)

  revision_rate = (user_revisions / total_provocations) * 100

  # Benchmarks:
  # 0-30% → Provocations too easy (user doesn't reconsider)
  # 30-70% → Good (healthy reconsideration)
  # 70-100% → Provocations too aggressive (user rewrites everything)

  return revision_rate
```

**Metric 2: Assumption Surfacing**
```python
def count_assumptions_surfaced(phase_outputs):
  """
  Track how many hidden assumptions were made explicit
  """
  assumptions = extract_assumptions(phase_outputs)

  return {
    "total_assumptions": len(assumptions),
    "acknowledged_in_limitations": count_in_limitations(assumptions),
    "supported_with_evidence": count_supported(assumptions),
    "removed_from_claims": count_removed(assumptions)
  }
```

**Metric 3: Evidence-Language Alignment**
```python
def measure_claim_calibration(draft, evidence_grades):
  """
  Check if claim strength matches evidence strength
  """
  overclaims = 0
  underclaims = 0
  aligned = 0

  for claim in extract_claims(draft):
    evidence_level = evidence_grades[claim.theme]
    language_level = assess_claim_language(claim.text)

    if language_level > evidence_level:
      overclaims += 1  # Claim stronger than evidence
    elif language_level < evidence_level:
      underclaims += 1  # Claim weaker than evidence
    else:
      aligned += 1

  alignment_score = (aligned / (overclaims + underclaims + aligned)) * 100

  return {
    "alignment_score": alignment_score,
    "overclaims": overclaims,
    "underclaims": underclaims,
    "aligned": aligned
  }
```

**Metric 4: Reflection Quality**
```python
def assess_reflection_quality(reflection_text):
  """
  Assess depth of user reflection
  """
  score = 0

  # Surface-level (1 point each)
  if mentions_findings(reflection_text): score += 1
  if mentions_methods(reflection_text): score += 1

  # Intermediate (2 points each)
  if mentions_surprises(reflection_text): score += 2
  if mentions_limitations(reflection_text): score += 2

  # Deep (3 points each)
  if questions_assumptions(reflection_text): score += 3
  if identifies_future_research(reflection_text): score += 3
  if connects_to_theory(reflection_text): score += 3

  # Benchmarks:
  # 0-4: Surface reflection
  # 5-8: Intermediate reflection
  # 9+: Deep reflection

  return score
```

---

## Provocation Bank (Domain-Specific)

### Clinical Research

**Screening Provocation:**
```
❓ "RCTs are the gold standard, but in RARE conditions,
    RCTs may be unethical or impossible.

    If you exclude case series, you exclude the ONLY evidence.

    Trade-off: Internal validity vs. coverage.
    Which matters more for YOUR review?"
```

**Synthesis Provocation:**
```
❓ "You found 'Treatment X reduces symptoms by 30%'

    But 30% compared to WHAT?
    - Placebo? (efficacy)
    - Standard care? (effectiveness)
    - Doing nothing? (net benefit)

    Effect sizes are meaningless without comparison."
```

### Education Research

**Screening Provocation:**
```
❓ "You're excluding qualitative studies.

    That means you'll measure WHAT works,
    but not WHY it works or HOW to implement.

    Acceptable trade-off for a meta-analysis,
    but acknowledge: 'Quantitative evidence only,
    implementation mechanisms underexplored.'"
```

**Synthesis Provocation:**
```
❓ "You found 'Intervention improves achievement by 0.3 SD'

    But WHO benefited?
    - All students equally? (main effect)
    - Only struggling students? (interaction effect)
    - Only with trained teachers? (moderator)

    Average effect ≠ universal benefit."
```

### Policy Research

**Screening Provocation:**
```
❓ "You're only including peer-reviewed studies.

    But policy happens in GRAY LITERATURE:
    - Government reports
    - Think tank briefs
    - Program evaluations

    Excluding these means missing IMPLEMENTED policies.

    Add 'policy documents' or acknowledge limitation?"
```

**Synthesis Provocation:**
```
❓ "You found 'Policy X increased enrollment by 15%'

    But at what COST?
    - Financial cost? (ROI)
    - Opportunity cost? (what else could that money buy?)
    - Equity cost? (did it widen or narrow gaps?)

    Effects without costs are incomplete policy evidence."
```

---

## Integration with Orchestrator

### Provocation Injection Points

**Orchestrator Enhancement:**

```python
# In orchestrate-research/SKILL.md

def run_phase_with_provocation(phase, corpus_path, project_context, user_options):
  """
  Wrap each phase with provocation hooks
  """

  # Pre-Phase Provocation
  if user_options.get("provocation_mode", True):
    pre_provocation = get_pre_provocation(phase)
    user_response = prompt_user(pre_provocation)
    log_provocation_response(phase, "pre", user_response)

  # Execute Phase
  phase_output = execute_phase(phase, corpus_path, project_context)

  # Post-Phase Provocation
  if user_options.get("provocation_mode", True):
    post_provocation = get_post_provocation(phase, phase_output)
    user_reflection = prompt_user(post_provocation)
    log_provocation_response(phase, "post", user_reflection)

    # Save reflection
    save_reflection(
      path=f"{project_context.output_root}/phase{phase}-reflection.md",
      content=user_reflection
    )

  return phase_output
```

**User Experience:**

```
[Phase 2 about to start]

Orchestrator:
"Before extracting themes, let's provoke your thinking.

❓ Expectation vs. Reality
Predict:
- How many themes will emerge? (3? 5? 10?)
- What's the MOST OBVIOUS theme?
- What's the SURPRISING theme?
- What TENSION will appear?

> [User types predictions]

Good. Now let's extract and see if reality matches expectations.

[Extraction runs]

Orchestrator:
Here are the 6 themes. Notice:
- You predicted 5 themes, I found 6 (you missed one)
- You predicted 'accuracy' as obvious → Correct (Theme A, 12 papers)
- You predicted 'equity' as surprising → Correct (Theme C, 3 papers)
- You missed 'teacher perception' (Theme D, 7 papers!)

Reflection prompt:
Why did you miss teacher perception? Selection bias in screening?

> [User reflects]

Saving reflection to: .../phase2-reflection.md
Proceeding to Phase 3..."
```

---

## Success Criteria (Phase 6)

| Criterion | Target | Status |
|-----------|--------|--------|
| **Provocation Integration** | All 8 phases | ✅ COMPLETE |
| **Domain-Specific Bank** | 3 domains (clinical, education, policy) | ✅ COMPLETE |
| **Meta-Cognitive Scaffolding** | Reflection prompts all phases | ✅ COMPLETE |
| **Anti-Ghostwriting** | Refusal patterns implemented | ✅ COMPLETE |
| **Effectiveness Metrics** | 4 metrics defined | ✅ COMPLETE |
| **Orchestrator Integration** | Provocation hooks added | ✅ COMPLETE |

**Phase 6 Status:** ✅ **ALL TARGETS COMPLETE**

---

**Provocation Mode: Think Deeper, Write Better** 🧠

*Last updated: 2026-01-17 23:00 GMT+8*
