# Skill Creation: Detailed Steps

## Step 0: Identify Use Case Category

Before diving into examples, identify which category your skill falls into. This helps guide design decisions and set appropriate expectations.

**Category 1: Document & Asset Creation**
- Purpose: Creating consistent, high-quality output (documents, presentations, apps, designs, code)
- Key techniques: Embedded style guides, template structures, quality checklists
- Examples: frontend-design, docx-generator, pptx-creator
- Success criteria: Consistent output quality, no external tools needed

**Category 2: Workflow Automation**
- Purpose: Multi-step processes with consistent methodology
- Key techniques: Step-by-step workflows, validation gates, iterative refinement loops
- Examples: skill-creator, sprint-planning, code-review
- Success criteria: Users don't need to prompt about next steps, workflows complete without correction

**Category 3: MCP Enhancement**
- Purpose: Workflow guidance for MCP server tool access
- Key techniques: Coordinates multiple MCP calls, embeds domain expertise, error handling
- Examples: sentry-code-review, notion-project-setup, linear-workflow
- Success criteria: 0 failed API calls, consistent tool usage, lower learning curve

## Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.

Conclude this step when there is a clear sense of the functionality the skill should support.

## Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:

1. Rotating a PDF requires re-writing the same code each time
2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill

Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:

1. Writing a frontend webapp requires the same boilerplate HTML/React each time
2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill

Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:

1. Querying BigQuery requires re-discovering the table schemas and relationships each time
2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill

To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.

## Step 3: Initializing the Skill

At this point, it is time to actually create the skill.

Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.

When creating a new skill from scratch, always run the `init_skill.py` script. The script conveniently generates a new template skill directory that automatically includes everything a skill requires, making the skill creation process much more efficient and reliable.

Usage:

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

The script:

- Creates the skill directory at the specified path
- Generates a SKILL.md template with proper frontmatter and TODO placeholders
- Creates example resource directories: `scripts/`, `references/`, and `assets/`
- Adds example files in each directory that can be customized or deleted

After initialization, customize or remove the generated SKILL.md and example files as needed.

## Step 4: Edit the Skill

When editing the (newly-generated or existing) skill, remember that the skill is being created for other agents to use. Include information that would be beneficial and non-obvious to the agent. Consider what procedural knowledge, domain-specific details, or reusable assets would help another agent execute these tasks more effectively.

### Learn Proven Design Patterns

Consult these helpful guides based on your skill's needs:

- **Multi-step processes**: See references/workflows.md for sequential workflows and conditional logic
- **Specific output formats or quality standards**: See references/output-patterns.md for template and example patterns

These files contain established best practices for effective skill design.

### Start with Reusable Skill Contents

To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.

Added scripts must be tested by actually running them to ensure there are no bugs and that the output matches what is expected. If there are many similar scripts, only a representative sample needs to be tested to ensure confidence that they all work while balancing time to completion.

Any example files and directories not needed for the skill should be deleted. The initialization script creates example files in `scripts/`, `references/`, and `assets/` to demonstrate structure, but most skills won't need all of them.

### Update SKILL.md

**Writing Guidelines:** Always use imperative/infinitive form.

#### Frontmatter

Write the YAML frontmatter with `name` and `description`:

- `name`: The skill name (kebab-case, no spaces, no capitals, no underscores)
- `description`: This is the primary triggering mechanism for your skill. Use the formula: **[What it does] + [When to use it] + [Key capabilities]**
  - Include specific trigger phrases users might say
  - Under 1024 characters
  - Include both what the Skill does and specific triggers/contexts for when to use it
  - Include all "when to use" information here - Not in the body. The body is only loaded after triggering, so "When to Use This Skill" sections in the body are not helpful to the agent
  - Example (good): "Analyzes Figma design files and generates developer handoff documentation. Use when user uploads .fig files, asks for 'design specs', 'component documentation', or 'design-to-code handoff'."
  - Example (good): "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when the agent needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"

**Security restrictions:**
- No XML angle brackets (< >) in frontmatter - can inject malicious instructions
- No "claude" or "anthropic" in skill names - reserved names
- Rationale: Frontmatter appears in the agent's system prompt

Do not include any other fields in YAML frontmatter.

#### Body

Write instructions for using the skill and its bundled resources.

## Step 5: Packaging a Skill

Once development of the skill is complete, it must be packaged into a distributable .skill file that gets shared with the user. The packaging process automatically validates the skill first to ensure it meets all requirements:

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory specification:

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

The packaging script will:

1. **Validate** the skill automatically, checking:

   - YAML frontmatter format and required fields
   - Skill naming conventions and directory structure
   - Description completeness and quality
   - File organization and resource references

2. **Package** the skill if validation passes, creating a .skill file named after the skill (e.g., `my-skill.skill`) that includes all files and maintains the proper directory structure for distribution. The .skill file is a zip file with a .skill extension.

If validation fails, the script will report the errors and exit without creating a package. Fix any validation errors and run the packaging command again.

## Step 6: Iterate

After testing the skill, users may request improvements. Often this happens right after using the skill, with fresh context of how the skill performed.

**Iteration workflow:**

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again


## Step 5: Testing and Validation

After implementing the skill, validate it meets success criteria before considering it complete.

### Trigger Testing

**Goal:** Skill triggers on 90% of relevant queries

**How to test:**
1. Create 10-20 test queries that should trigger your skill
2. Run each query in a fresh conversation
3. Track how many times the skill loads automatically vs. requires explicit invocation
4. Refine the description field if trigger rate is below 90%

**Example test queries for a `pdf-editor` skill:**
- "Rotate this PDF 90 degrees"
- "Help me edit this PDF file"
- "Can you modify this document?" (with PDF attached)
- "I need to change something in this PDF"

### Workflow Efficiency Testing

**Goal:** Completes workflow in expected number of tool calls

**How to test:**
1. Run the same task with and without the skill enabled
2. Count tool calls and total tokens consumed
3. Compare efficiency - skill should reduce both

**Example:** A `sprint-planning` skill should complete sprint setup in 5-7 tool calls vs. 15-20 without the skill.

### Error Rate Testing

**Goal:** 0 failed API calls per workflow (especially for MCP skills)

**How to test:**
1. Monitor MCP server logs during test runs
2. Track retry rates and error codes
3. Add error handling for common failure modes
4. Test edge cases (empty responses, rate limits, network errors)

### Consistency Testing

**Goal:** Consistent results across sessions

**How to test:**
1. Run the same request 3-5 times in separate conversations
2. Compare outputs for structural consistency and quality
3. Check if a new user can accomplish the task on first try with minimal guidance

### Quality Checklist

Before finalizing the skill, verify:

- [ ] Description includes trigger phrases and is under 1024 characters
- [ ] No XML brackets or reserved names in frontmatter
- [ ] SKILL.md is under 500 lines (split to references if longer)
- [ ] All scripts have been tested and work correctly
- [ ] No README.md or auxiliary documentation files in skill folder
- [ ] References are one level deep (not nested)
- [ ] Skill triggers automatically on relevant queries
- [ ] Workflows complete without user correction
- [ ] Results are consistent across multiple runs

## Step 6: Iteration and Refinement

Skills improve through real-world usage. After deployment:

1. **Monitor usage patterns** - Which queries trigger the skill? Which don't but should?
2. **Collect feedback** - Do users need to redirect or clarify frequently?
3. **Refine descriptions** - Add trigger phrases for missed queries
4. **Optimize workflows** - Reduce tool calls, improve efficiency
5. **Update references** - Add new patterns, examples, or edge cases discovered

**Iteration cycle:**
- Deploy skill → Monitor usage → Identify gaps → Update skill → Test changes → Deploy update

**Common refinements:**
- Adding more trigger phrases to description
- Splitting large SKILL.md into references
- Adding error handling for edge cases
- Optimizing script performance
- Updating examples based on real usage
