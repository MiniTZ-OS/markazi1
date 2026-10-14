---
name: create-skill
description: Workflow skill to guide the creation of a new workspace SKILL.md for VS Code agent customization.
---

# Create Skill Workflow

Use this skill when you need to build a new `SKILL.md` file that documents a reusable workflow for codifying project-specific guidance.

## What this skill produces

- A workspace-level `SKILL.md` file with YAML frontmatter
- A clear description that surfaces trigger phrases and usage context
- A step-by-step workflow for turning conversation history into a reusable skill
- Guidance on scope, placement, and validation

## When to use

- You want to capture a multi-step workflow or team process as a skill
- The task is specific to the current repo or project setup
- The output should be a reusable customization file, not just a one-off answer

## Workflow

1. Review the conversation history for any ongoing methodology or multi-step process.
2. Identify the task outcome, decision points, and completion checks.
3. Decide whether the new customization should be workspace-scoped or user-scoped.
4. Choose the appropriate skill location and file name.
5. Draft the `SKILL.md` content with:
   - YAML frontmatter (`name`, `description`)
   - A concise role and purpose
   - A step-by-step workflow
   - Quality criteria and validation guidance
6. Validate the file:
   - Confirm valid YAML frontmatter
   - Ensure the description is meaningful and discoverable
   - Check the file path matches workspace conventions

## Clarification rules

- If the workflow is unclear, ask:
  - What outcome should the skill produce?
  - Should it be workspace-scoped or user-scoped?
  - Is it a quick checklist or a full multi-step workflow?
- If no clear workflow emerges, default to a general workspace skill template and request refinement.

## Validation checklist

- [ ] `name` and `description` are present in frontmatter
- [ ] Description includes trigger phrases for the target use case
- [ ] Skill body defines the expected output and the workflow
- [ ] Skill is saved in a workspace-friendly location

## Example prompts

- "Create a SKILL.md for adding a new page component in this repo."
- "Build a skill for reviewing Tailwind configuration and making styling changes."
- "Generate a workspace skill that documents how to add new API routes."
