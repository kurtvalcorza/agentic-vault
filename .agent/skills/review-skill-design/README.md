# Review Skill Design

Deep cognitive audit (Level 2) of agent skills beyond structural compliance.

## What It Does

Evaluates the **quality** of skill design across four dimensions:

1. **Functional Logic**: Does it solve the right problem correctly?
2. **Prompt Engineering**: Are instructions clear, specific, and effective?
3. **Architecture & Cohesion**: Is the skill well-organized and maintainable?
4. **Safety & Security**: Does it handle edge cases and protect user data?

This is analytical work—read-only, no modifications. Produces detailed review reports.

## When to Use

- Skill behaves unexpectedly or produces poor outputs
- Before publishing skills externally
- Improving existing skill quality
- Learning best practices through review feedback

## Quick Start

**Trigger**: "Review the design of [skill-name]"

The skill will:
1. Read SKILL.md and README.md
2. Analyze against design principles
3. Classify findings as Critical/Major/Minor
4. Provide specific recommendations with examples
5. Generate review report in `.agent/outputs/`

## What It Evaluates

- **Logic**: Correctness, completeness, edge cases
- **Prompts**: Clarity, specificity, guard rails
- **Architecture**: Modularity, reusability, documentation
- **Safety**: Input validation, error handling, data protection

## Severity Levels

- **Critical**: Breaks functionality or creates security risk
- **Major**: Significantly degrades quality or usability
- **Minor**: Improvement opportunities, polish

## Related Skills

- `validate-skills-standard` - Structural compliance checking
- `assimilate-skills` - Import skills with quality review
