# Technical Reports: Tools for Thought Protocol

## The Problem with AI-Assisted Technical Reports

When AI analyzes your data and writes your findings:
- You don't understand what the data actually shows
- You can't defend your interpretations in meetings
- You miss anomalies that AI doesn't flag
- Your expertise doesn't shape the narrative

This protocol ensures you *interpret* your data rather than validating AI's interpretation.

## Core Principle: Anomalies Before Conclusions

**Don't ask**: "Analyze this data and write findings"

**Do ask**: "What's surprising in this data? What doesn't fit the expected pattern?"

Anomalies reveal insights. Expected patterns confirm what you already knew.

---

## Phase 1: Understanding the Decision Context

### Before Touching Data

Answer these questions:

1. **Who reads this report?** (Name specific people if possible)
2. **What decision will they make based on it?** (Be concrete)
3. **What would change their decision?** (The actual stakes)
4. **What do they already believe?** (Your starting point)

**Provocation**: "If I knew the answer before analysis, would I still run the analysis? If not, what am I actually trying to learn?"

### Defining Success

| Good Report Goal | Bad Report Goal |
|------------------|-----------------|
| "Determine if Q4 marketing spend drove conversion" | "Analyze Q4 performance" |
| "Identify which regions underperformed vs. forecast" | "Report on regional sales" |
| "Recommend whether to continue pilot program" | "Summarize pilot program results" |

**Provocation**: "Can I state my report's purpose as a question with a yes/no answer?"

---

## Phase 2: Data Interrogation

### The Anomaly Hunt

Before calculating anything, scan for:
- **Gaps**: Missing data, blank periods, null values
- **Spikes**: Sudden changes that break patterns
- **Divergences**: Metrics that usually correlate but don't here
- **Boundaries**: Values at limits (0%, 100%, round numbers)

For each anomaly, ask: "Is this data quality issue or genuine signal?"

**Provocation**: "What's the weirdest thing in this data? Why is it weird?"

### Questioning Your Metrics

| For every metric, ask: |
|-----------------------|
| What does this actually measure? |
| What doesn't it capture? |
| Could it go up while the thing I care about goes down? |
| What would make this metric misleading? |

**Example**: "Conversion rate" could mean different things:
- Visits to sign-ups?
- Sign-ups to purchases?
- Purchases to repeat purchases?

**Provocation**: "If my metric looks good but reality is bad, how would I know?"

### The Comparison Problem

Numbers mean nothing without context. Always ask:
- Compared to what period?
- Compared to what benchmark?
- Compared to what expectation?

| Finding | Uninformative | Informative |
|---------|---------------|-------------|
| Sales number | "Sales were $1.2M" | "Sales were $1.2M, up 15% YoY but 8% below forecast" |
| Conversion rate | "Conversion was 3.2%" | "Conversion was 3.2%, the highest since Q2 2023" |
| Cost metric | "CAC was $45" | "CAC was $45, in line with budget but 2x competitor benchmark" |

---

## Phase 3: Interpretation

### The Confidence Calibration

For every claim, explicitly state your confidence:

| Language | Confidence Level | When to Use |
|----------|------------------|-------------|
| "The data shows X" | High | Clear, direct measurement |
| "The data suggests X" | Medium | Reasonable inference with caveats |
| "X may be a factor" | Low | Possible explanation, not proven |
| "X is worth investigating" | Hypothesis | Pattern noticed, needs more analysis |

**Provocation**: "What's my actual confidence in this claim? Does my language match it?"

### Alternative Explanations

For every interpretation, identify at least one alternative:

**Finding**: Conversion rate dropped in March
**Your interpretation**: New checkout flow confused users
**Alternative 1**: Seasonal effect (March always dips)
**Alternative 2**: Marketing mix shifted to lower-intent channels
**Alternative 3**: Data tracking issue after site update

**Provocation**: "If I'm wrong about why this happened, what's the next most likely explanation?"

### The "So What" Test

Every finding needs an implication:

| Finding | So What? |
|---------|----------|
| "Q4 sales increased 12%" | "We can invest more in Q1 marketing" |
| "Region X underperformed by 20%" | "We need to investigate or reallocate resources" |
| "Customer NPS dropped 5 points" | "Retention risk is elevated; support needs attention" |

**Provocation**: "If this finding is true, what should someone *do* differently?"

---

## Phase 4: Structure and Communication

### Structuring for Decision-Makers

**Executive summary structure**:
1. One sentence: What was the question?
2. One sentence: What's the answer?
3. One sentence: What's the key supporting evidence?
4. One sentence: What should we do?

**Common structural problems**:

| Problem | Example | Fix |
|---------|---------|-----|
| Buried recommendation | Recommendation in appendix | Lead with it |
| Data-first narrative | "First, let's look at..." | Question-first narrative |
| False precision | "Sales increased 12.847%" | Match precision to confidence |
| Missing uncertainty | No confidence intervals or caveats | Add them |

### Visualization Decisions

For every chart, ask:
- What comparison does this make obvious?
- What does it hide?
- Would a different chart type tell a different story?
- Is the scale manipulating perception?

**Provocation**: "If I showed the opposite trend on this chart, would the reader notice?"

---

## Phase 5: Recommendations

### The Recommendation Checklist

For every recommendation:

- [ ] Does it follow from my findings? (Can I trace the logic?)
- [ ] Is it specific enough to act on? (Who does what by when?)
- [ ] Have I considered the cost of being wrong?
- [ ] What would make me change this recommendation?

### Uncertainty Communication

Don't hide uncertainty—structure it:

> **Recommendation**: Expand pilot to Region B
> 
> **Confidence**: Medium-high. Pilot results were strong, but sample was small.
> 
> **Risk if wrong**: $50K investment, 2 months to learn
> 
> **What would change this**: If Region B demographics differ significantly from pilot region

**Provocation**: "If this recommendation fails, will I have been wrong or unlucky?"

---

## Phase 6: Self-Review

### The Skeptic Test

Before finalizing, adopt skeptic mode:

- [ ] "What claim am I most uncertain about?"
- [ ] "Where did I make an assumption I didn't test?"
- [ ] "What question will the smartest person in the room ask?"
- [ ] "If the data told the opposite story, would I report it the same way?"

### The Time-Travel Test

- [ ] "In six months, will these findings still be relevant?"
- [ ] "In six months, will I be embarrassed by anything I wrote?"
- [ ] "What additional data would I want if I had more time?"

### The Inheritance Test

- [ ] "If someone else read only this report, could they understand the situation?"
- [ ] "Is there tribal knowledge I'm assuming?"
- [ ] "Are my data sources documented enough to reproduce?"

---

## Anti-Patterns to Avoid

### Don't Let AI Interpret for You

**Problem**: You become a validator, not an analyst.

**Instead**: Have AI surface patterns and anomalies, then interpret them yourself.

### Don't Match Confidence to Stakes

**Problem**: "This is important, so I'll use confident language."

**Instead**: Match confidence to evidence, not importance.

### Don't Report Everything

**Problem**: 50-page report that no one reads.

**Instead**: What's the minimum to support the decision?

### Don't Avoid Bad News

**Problem**: Cherry-picking positive findings.

**Instead**: Report bad news in context of what to do about it.

---

## Workflow Summary

```
1. CONTEXT
   - Identify decision-maker and decision
   - Define concrete question
   - Document current beliefs

2. INTERROGATE
   - Hunt for anomalies
   - Question metrics
   - Establish comparisons

3. INTERPRET
   - Calibrate confidence
   - Generate alternatives
   - Apply "so what" test

4. STRUCTURE
   - Lead with answer
   - Match precision to confidence
   - Support decision-making

5. RECOMMEND
   - Trace logic from findings
   - Communicate uncertainty
   - Define success/failure conditions

6. REVIEW
   - Skeptic test
   - Time-travel test
   - Inheritance test
```
