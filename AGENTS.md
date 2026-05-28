# AGENTS.md

This file provides guidance to Claude Code (<https://claude.ai/code>) and OpenCode (<https://opencode.ai/>) when working with code in this repository.

## What This Repo Is

Collection of Claude Code skills — Markdown reference guides that Claude agents invoke when specific triggers are detected. Skills are installed into projects via `npx skills add itsgitz/agent-skills/<skill-name>`.

## Skill Structure

Each skill lives at `<skill-name>/SKILL.md` (flat, no nesting):

```
agent-skills/
  <skill-name>/
    SKILL.md        # required — YAML frontmatter + skill body
    README.md       # required — install command + trigger list
    supporting.*    # optional — extra reference docs, templates
  docs/
  README.md
  LICENSE
```

## SKILL.md Frontmatter Rules

```yaml
---
name: skill-name-with-hyphens # letters, numbers, hyphens only
description: >
  Use when [triggers — symptoms, situations, keywords].   # max 1024 chars total
license: MIT
---
```

- `description` must start with `"Use when..."`
- List concrete triggers (user phrases, symptoms), not workflow summaries
- Third person — it's injected as a system prompt

## Required Sections in SKILL.md

Every skill needs: **Overview**, **When to Use**, **When NOT to Use**, at least one code example.

## Adding a New Skill

1. Create `<skill-name>/SKILL.md` with valid frontmatter
2. Create `<skill-name>/README.md` with install command and trigger list
3. Add row to skills table in root `README.md`

See `docs/adding-skills.md` for the full checklist.

## Checklist Before Committing a Skill

- [ ] Name: letters, numbers, hyphens only
- [ ] Frontmatter has `name`, `description`, `license`
- [ ] Description starts with `"Use when..."`, no workflow summary
- [ ] `SKILL.md` has Overview, When to Use, When NOT to Use, code example
- [ ] `README.md` has install command and trigger list
- [ ] Row added to root `README.md` skills table
