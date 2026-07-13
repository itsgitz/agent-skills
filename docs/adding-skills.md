# Adding Skills

## Directory Layout

Each skill lives in its own directory at the repo root:

```
agent-skills/
  <skill-name>/
    SKILL.md          # required — main skill reference
    supporting.*      # optional — heavy reference docs, scripts, templates
  docs/
  README.md
  LICENSE
```

One skill per directory. No nesting.

## SKILL.md Structure

Every `SKILL.md` must start with YAML frontmatter:

```yaml
---
name: skill-name-with-hyphens
description: >
  Use when [specific triggering conditions — symptoms, situations, keywords].
---
```

**Name rules:** letters, numbers, hyphens only. No parentheses or special characters.

**Description rules:**
- Start with `"Use when..."`
- List concrete triggers: user phrases, symptoms, contexts
- Third person (it's injected as a system prompt)
- Never summarize the skill's workflow — triggers only
- Max 1024 characters total for the entire frontmatter block

## Checklist Before Adding

- [ ] Skill name uses only letters, numbers, hyphens
- [ ] Frontmatter has `name` and `description`
- [ ] Description starts with "Use when..."
- [ ] Description contains no workflow summary
- [ ] `SKILL.md` has an Overview, When to Use, and at least one code example
- [ ] Skill directory added to the table in root `README.md`
- [ ] Skill `README.md` created with install command, update command, and trigger list

## Updating README.md

Add a row to the skills table in the root `README.md`:

```markdown
| [skill-name](./skill-name/) | One-line description | `npx skills add itsgitz/agent-skills/skill-name` |
```
