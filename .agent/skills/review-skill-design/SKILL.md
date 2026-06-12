---
name: review-skill-design
description: Performs a deep cognitive audit (Level 2) of agent skills. Use when you need to evaluate the design quality, safety, prompt engineering, and functional logic of a skill beyond simple structural compliance.
---

# Review Skill Design (Level 2)

## Purpose

This skill provides a framework for performing a **Deep Code Review** (Level 2 Audit) of Agent Skills. While the `validate-skills-standard` skill checks for syntax and structure, this skill focuses on **semantics, safety, and design quality**.

Use this skill to audit high-value, complex, or risky skills before they are finalized.

## Safety & Confirmation
- **Self-Audit:** This skill is analytical and read-only. It does not perform destructive actions on its own.
- **Recommendations:** When recommending fixes (e.g., script modifications), always emphasize that the user must approve the changes.

## Path Resolution Standards
- **Dynamic Resolution:** When auditing paths, ensure the skill follows the `AGENTS.md` standard: **Dynamically resolve the vault root** at runtime.
- **Placeholders:** The placeholder `{{VaultRoot}}` should be used in documentation and examples, but implementation code must determine the absolute path programmatically (e.g., using `pathlib` in Python or `process.cwd()` in Node, combined with searching for a root marker like `.obsidian` or `.agent`).
- **Strict Prohibition:** Hardcoded drive letters (e.g., `[Drive]:\`) or user-specific paths (e.g., `\Users\[Name]\`) are failures.

## Validation Checklist (Level 2)

### 1. Functional Logic
- [ ] **Completeness:** Are all promised features actually implemented? (e.g., instructions say "Run script" but script is missing).
- [ ] **Dependencies:** Does it rely on missing folders or external tools not listed?
- [ ] **Edge Cases:** Does it handle empty inputs, missing files, or user rejections gracefully?
- [ ] **Error Handling:** Are potential failures (API errors, file locks) anticipated?
- [ ] **Path Resolution:** Does it strictly avoid hardcoded drive letters and use dynamic path resolution (e.g., `{{VaultRoot}}`) as per `GEMINI.md`?

### 2. Prompt Engineering
- [ ] **Ambiguity:** Are basic instructions clear? (e.g., "Use `brand.json`" is better than "Make it look good").
- [ ] **Context Awareness:** Does it respect the user's `GEMINI.md` rules (e.g., "Save to `01_Projects`", "Use specific tone")?
- [ ] **Trigger Clarity:** Is the `description` distinct enough to avoid confusing the routing agent?
- [ ] **Progressive Disclosure:** Does `SKILL.md` unnecessarily load tokens that should be in `references/`?

### 3. Architecture & Cohesion
- [ ] **Interoperability:** Can other skills consume its output? (e.g., standard JSON/Markdown formats).
- [ ] **DRY (Don't Repeat Yourself):** Does it duplicate logic found in `optimize-workspace` or `skill-creator`?
- [ ] **Separation of Concerns:** Does it separate configuration (user preferences) from logic (code)?
- [ ] **Idempotency:** Can the skill be run multiple times clearly without corrupting state?

### 4. Safety & Security
- [ ] **Destructive Actions:** Do file deletions, overwrites, or massive edits require explicit `confirm=True`?
- [ ] **Privacy:** Does it avoid sending sensitive data (PII, API keys) to external logs or tools?
- [ ] **Safe Defaults:** Does it prioritize non-destructive defaults (e.g., creating a backup before editing)?

## Workflow

1. **Select Skill to Review**
   - Identify a skill that has passed Level 1 (Structure) validation.

2. **Read Code & Instructions**
   - Read `SKILL.md` to understand the *intent*.
   - Read `scripts/*.py` or `*.sh` to understand the *implementation*.

3. **Perform Cognitive Audit**
   - mentally simulate the execution of the skill.
   - check against the checklist above.

4. **Generate Review Report**
   - Create a markdown report or comment block summarizing findings.
   - The `level2_audit.py` script generates a report at `.agent/outputs/YYYY-MM-DD_Level2-Audit-Report.md`.
   - Classify issues as **Critical** (Blocking), **Major** (Needs Fix), or **Minor** (Suggestion).

## Review Template

```markdown
# Design Review: [Skill Name]

## Summary
**Status:** [Approved / Needs Changes / Critical Issues]
**reviewer:** [Agent Name]

## Findings

### 1. Functional Logic
- ✅ clearly defined steps
- ⚠️ Script explicitly hardcodes absolute path (Fix needed: Use relative paths or {{VaultRoot}})

### 2. Prompt Engineering 
- ✅ Description contains good triggers
- ❌ Intro paragraph interprets "User Rules" too loosely

### 3. Architecture
- ✅ Good use of references/ folder

### 4. Safety
- ❌ **CRITICAL:** `cleanup.py` deletes files without confirmation.

## Recommendations
1. Modify `cleanup.py` to add `input("Delete? (y/n)")`.
2. Update `SKILL.md` line 45 to clarify scope.
```

## Remediation Guidelines

- **Critical:** Must fix before use. (Safety risks, broken code).
- **Major:** Fix before 'complete' status. (Logic bugs, confusing prompts).
- **Minor:** Fix if time permits. (Typos, style).
