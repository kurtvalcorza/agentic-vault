# Level 2 Design Review Criteria

## Overview
Level 2 design review focuses on cognitive aspects that automated tools cannot assess: design quality, safety considerations, prompt engineering effectiveness, and architectural soundness.

## Scoring Framework

### 1. Functional Logic (3 points)

#### Completeness (1 point)
- **✅ Full Credit**: All promised features implemented, instructions match scripts
- **⚠️ Partial Credit**: Minor gaps between promises and implementation  
- **❌ No Credit**: Major features missing or instructions don't match reality

**Red Flags**:
- Instructions reference scripts that don't exist
- Workflow steps that lead nowhere
- Promises in description not fulfilled in implementation

#### Dependencies & Requirements (1 point)
- **✅ Full Credit**: All dependencies clearly listed, no missing tools/folders
- **⚠️ Partial Credit**: Most dependencies clear, minor gaps
- **❌ No Credit**: Hidden dependencies, assumes tools not mentioned

**Red Flags**:
- References to external APIs without mentioning API keys
- Assumes specific directory structure not documented
- Requires tools not listed in compatibility section

#### Edge Case Handling (1 point)
- **✅ Full Credit**: Graceful handling of empty inputs, missing files, user rejections
- **⚠️ Partial Credit**: Some edge cases handled
- **❌ No Credit**: No consideration of failure scenarios

**Red Flags**:
- No validation of user inputs
- Assumes files always exist
- No fallback for network failures

### 2. Prompt Engineering (3 points)

#### Clarity & Specificity (1 point)
- **✅ Full Credit**: Instructions unambiguous, specific actions defined
- **⚠️ Partial Credit**: Mostly clear with some vague areas
- **❌ No Credit**: Vague instructions, unclear expectations

**Examples**:
- ✅ "Create `config.json` with brand colors in hex format"
- ⚠️ "Update the configuration file appropriately"  
- ❌ "Make it look good"

#### Context Awareness (1 point)
- **✅ Full Credit**: Respects workspace rules, follows established patterns
- **⚠️ Partial Credit**: Some awareness of context
- **❌ No Credit**: Ignores workspace conventions

**Check Against**:
- File naming conventions (YYYY-MM-DD format)
- Save locations (01_Projects vs 02_Areas)
- Tone and style guidelines
- Existing skill patterns

#### Trigger Specificity (1 point)
- **✅ Full Credit**: Description clearly indicates when to use skill
- **⚠️ Partial Credit**: Some usage context provided
- **❌ No Credit**: Unclear when skill should be activated

**Good Triggers**:
- "Use when creating AI policy presentations"
- "For validating YAML frontmatter compliance"
- "When consolidating weekly reports into monthly summaries"

### 3. Architecture & Cohesion (2 points)

#### Interoperability (1 point)
- **✅ Full Credit**: Output consumable by other skills, standard formats
- **⚠️ Partial Credit**: Some standardization
- **❌ No Credit**: Proprietary formats, hard to integrate

**Standards**:
- Markdown for documentation
- JSON for structured data
- Standard file naming conventions
- Consistent output locations

#### Separation of Concerns (1 point)
- **✅ Full Credit**: Configuration separate from logic, proper progressive disclosure
- **⚠️ Partial Credit**: Some separation
- **❌ No Credit**: Everything mixed together

**Indicators**:
- Large SKILL.md (>300 lines) without references/
- Configuration hardcoded in scripts
- No clear distinction between user settings and implementation

### 4. Safety & Security (2 points)

#### Destructive Action Protection (1 point)
- **✅ Full Credit**: Destructive operations require confirmation, have safeguards
- **⚠️ Partial Credit**: Some protection measures
- **❌ No Credit**: Destructive operations without safeguards

**Destructive Operations**:
- File deletion or overwriting
- Bulk modifications
- External API calls that modify data
- Directory restructuring

**Required Safeguards**:
- Explicit user confirmation
- Backup creation before changes
- Clear warnings about consequences
- Ability to undo/rollback

#### Input Validation & Privacy (1 point)
- **✅ Full Credit**: Input sanitization, no sensitive data exposure
- **⚠️ Partial Credit**: Some validation measures
- **❌ No Credit**: No input validation, potential privacy issues

**Security Concerns**:
- Path traversal attacks (../../../etc/passwd)
- Code injection through user inputs
- Logging sensitive information
- Exposing API keys or personal data

## Risk-Based Prioritization

### High Priority (Always Require Level 2)
- **Destructive Operations**: Delete, overwrite, bulk modify
- **External Integrations**: API calls, network requests
- **Complex Workflows**: Multi-step processes with dependencies
- **Sensitive Data**: Handles PII, credentials, or confidential information

### Medium Priority (Recommended Level 2)
- **Script Components**: Executable code beyond simple templates
- **Cross-Skill Dependencies**: Relies on or feeds other skills
- **User-Facing Interfaces**: Direct user interaction or input collection
- **Data Processing**: Transforms or analyzes user content

### Low Priority (Optional Level 2)
- **Simple Validation**: Basic checks and confirmations
- **Documentation Generation**: Template-based output creation
- **Basic File Operations**: Simple read/write without modification
- **Static Templates**: No dynamic logic or user input

## Common Anti-Patterns

### Functional Logic Issues
- **The Phantom Feature**: Promises functionality not implemented
- **The Hidden Dependency**: Requires tools/setup not documented
- **The Happy Path Only**: No consideration of failure scenarios

### Prompt Engineering Issues
- **The Vague Directive**: "Improve this" without specific criteria
- **The Context Blind**: Ignores established workspace patterns
- **The Trigger Collision**: Description too similar to existing skills

### Architecture Issues
- **The Monolith**: Everything crammed into SKILL.md
- **The Island**: Cannot integrate with other skills
- **The Reinvention**: Duplicates existing functionality

### Safety Issues
- **The Silent Destroyer**: Destructive operations without warning
- **The Data Leaker**: Exposes sensitive information
- **The Injection Point**: No input validation or sanitization

## Review Calibration Examples

### Excellent Design (9-10 points)
- Clear, specific instructions with examples
- Comprehensive error handling and edge cases
- Proper progressive disclosure and file organization
- Strong safety measures for any destructive operations
- Good integration with existing skill ecosystem

### Good Design (7-8 points)
- Clear instructions with minor ambiguities
- Basic error handling present
- Reasonable file organization
- Some safety measures
- Integrates well with most skills

### Needs Improvement (5-6 points)
- Some unclear instructions or missing details
- Limited error handling
- Poor file organization or separation of concerns
- Minimal safety measures
- Limited integration capability

### Poor Design (0-4 points)
- Vague or confusing instructions
- No error handling
- Poor organization, everything in SKILL.md
- No safety measures for destructive operations
- Cannot integrate with other skills