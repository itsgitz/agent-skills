# AGENTS.md

This file provides guidance to Claude Code (<https://claude.ai/code>) and OpenCode (<https://opencode.ai/>) when working with code in this repository.

## What This Repo Is

Two companion collections for AI coding tools:

- **Skills** — Markdown reference guides that agents invoke when specific triggers are detected. Installed via `npx skills add itsgitz/agent-skills/<skill-name>`.
- **Agents** — agent role definitions (the `architect` family) for Claude Code and OpenCode, with an enforced plan/build split. Installed by copying files or running `scripts/install_agents.py`.

## Repo Layout

```
agent-skills/
  <skill-name>/
    SKILL.md        # required — YAML frontmatter + skill body
    README.md       # required — install command + trigger list
    supporting.*    # optional — extra reference docs, templates
  agents/
    claude/
      architect.claude-plan.md  # Claude Code plan-only (opus)
      architect.claude-build.md # Claude Code build-only (sonnet)
    opencode/
      architect.md               # OpenCode combined (plan+build, gated)
      architect-plan.md          # OpenCode plan-only (bash denied)
      architect-build.md         # OpenCode build-only
    README.md       # agent setup + workflow docs
  scripts/
    install_agents.py           # fetch + install agent files from GitHub raw
  docs/
    adding-skills.md            # skill authoring checklist
  README.md
  LICENSE
```

---

## Skills

### SKILL.md Frontmatter Rules

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

### Required Sections in SKILL.md

Every skill needs: **Overview**, **When to Use**, **When NOT to Use**, at least one code example.

### Adding a New Skill

1. Create `<skill-name>/SKILL.md` with valid frontmatter
2. Create `<skill-name>/README.md` with install command and trigger list
3. Add row to skills table in root `README.md`

See `docs/adding-skills.md` for the full checklist.

### Checklist Before Committing a Skill

- [ ] Name: letters, numbers, hyphens only
- [ ] Frontmatter has `name`, `description`, `license`
- [ ] Description starts with `"Use when..."`, no workflow summary
- [ ] `SKILL.md` has Overview, When to Use, When NOT to Use, code example
- [ ] `README.md` has install command and trigger list
- [ ] Row added to root `README.md` skills table

---

## Agents

Agent files live under `agents/claude/` and `agents/opencode/`, split by platform. Claude Code
files are named `architect.claude-<role>.md` — Claude Code reads the agent's display name from
frontmatter `name:`, decoupled from the filename, so the platform tag in the filename costs
nothing. OpenCode has no such field: the display name *is* the filename minus `.md`, so its files
drop the redundant `opencode` segment entirely (`architect.md`, `architect-plan.md`,
`architect-build.md`) — otherwise Tab-switching would show `Architect.Opencode-Build` inside
OpenCode itself.

| File | Platform | Role |
|------|----------|------|
| `claude/architect.claude-plan.md` | Claude Code | Plan-only (opus) — read-only, never executes |
| `claude/architect.claude-build.md` | Claude Code | Build-only (sonnet) — executes saved plans |
| `opencode/architect.md` | OpenCode | Combined plan+build in one agent, prose-gated |
| `opencode/architect-plan.md` | OpenCode | Plan-only — `bash: deny`, gate enforced by runtime |
| `opencode/architect-build.md` | OpenCode | Build-only — executes saved plans |

### Plan / Build Split

The core design: planning and execution are separated so a planning agent can't slide into building.

- **Claude Code** — role split, not mandatory two sessions: `@architect-plan` (opus) writes the plan, then hands off with a build menu. Default is same-session — the main thread spawns `@architect-build` as a sonnet subagent (subagents honor their own `model:`; hand-off works via the plan saved to disk). Alternatives: a fresh `@architect-build` session (clean context), or another model via `/generate-execute-prompt`. `architect-plan` never spawns the builder itself (no `Agent`/`Bash` tool).
- **OpenCode combined** — one agent, prose gate. Halts after writing the plan; resumes build only on `execute` / `continue` / `go` / `build it` / `run it`.
- **OpenCode split (recommended)** — Tab-switch between two agents. `architect-plan` sets `bash: deny`, so the no-execution gate is machine-enforced, not prose.
- **Any model/tool** — use the `generate-execute-prompt` skill to produce a portable prompt that can execute the plan in a different model, tool, or fresh session.

### Plan location convention

All agents persist plans as documentation under `docs/plans/`, one directory per plan:

```
feature  →  docs/plans/feature-<name>/{README.md, PROGRESS.md, PRD.md?}
bug fix   →  docs/plans/fix-<name>/{README.md, PROGRESS.md, PRD.md?}
<name>    =  short kebab-case slug (e.g. user-auth, login-crash)
```

`README.md` is the canonical plan doc; `PROGRESS.md` is the build tracker (checklist mirroring the plan). The plan half writes both — `README.md` with the plan, `PROGRESS.md` scaffolded with one unchecked `- [ ]` per task. The build half reads `README.md` (refuses to start if it's missing) and ticks off / logs into `PROGRESS.md` as it executes.

`PRD.md` is **optional and opt-in** — three triggers: (1) user asks at any point ("with a PRD", "PRD too") → written directly; (2) agent offers `PRD too? (y/n)` (default `n`) after brainstorm, only for user-facing or fuzzy-requirement work, never re-asked; (3) no offer at all for bugfixes/refactors/small specified work. PRD = what/why (problem, goals/non-goals, users, numbered testable `R1…` requirements Must/Should/Could, UX notes, success metrics, risks); plan README = how (tasks, files, tests) and links back with `Spec: ./PRD.md`. Written before the plan. Build agents read it as context; `README.md` stays the executable spec and the `code-review` spec arg.

### Cross-cutting agent rules

- **TDD gate** — every code change follows test-first (Red→Green→Refactor) via the `tdd` skill (mattpocock). Install globally (once, all projects) or per-project: `npx skills add https://github.com/mattpocock/skills --skill tdd -g`. Pure docs/config tasks are exempt.
- **Code-review gate** — build agents (`architect-build` both platforms, combined `architect`) run the `code-review` skill (mattpocock — Standards + Spec axes) before declaring work complete, passing the plan `docs/plans/<feature|fix>-<name>/README.md` as the spec (skill's step-2 path arg) so the Spec axis reviews against the plan, not a branch-name guess: `npx skills add https://github.com/mattpocock/skills --skill code-review -g`. Plan agents don't review (no code exists yet).
- **Superpowers** — build agents auto-load `systematic-debugging` and `using-git-worktrees` (the only two skills the agents take from [obra/superpowers](https://github.com/obra/superpowers)) when context matches. Brainstorming and plan-writing are **inline** in the plan agents (`# BRAINSTORM STRUCTURE` / `# PLAN STRUCTURE`), not external skills — keeps them self-contained when installed without superpowers.
- **Grilling gate** — plan agents (and combined `architect` in PLAN mode) load the `grilling` skill (mattpocock) at BRAINSTORM for features, user-facing work, or fuzzy requirements: a design-tree interview in rounds — numbered questions, each with a recommended answer — until the frontier is empty. Skipped for bugfixes and small well-specified asks (same bar as the PRD offer); "grill me" forces it on. It drives the questioning only; the inline `# BRAINSTORM STRUCTURE` write-up is unchanged and is the fallback when the skill is absent. Build agents don't load it. Install: `npx skills add https://github.com/mattpocock/skills --skill grilling -g`. Note `grilling` is the model-invocable engine — `grill-me` / `grill-with-docs` in that repo are `disable-model-invocation` slash-command wrappers, for humans not agents.
- **Skill preflight** — no skill is required and none is ever force-installed. On its **first response**, every agent compares the auto-load table against the skills actually available to it; all present → silent, any missing → one block listing each missing skill, what it buys, and one `npx skills add … -g` command **per source repo** (batching that repo's skills). Printed once per session, never re-nagged per skill. Plan agents (no bash) can't install — they also write the commands into the plan doc's "Suggested skills" note. Build + combined agents (have bash) ask `(y/n)`; on decline they continue and state what degrades (a declined `code-review` means the work is reported unreviewed, not silently skipped). Never block — every gate has an inline fallback. `scripts/install_agents.py` prints the same commands after installing the agent files; keep its `SKILL_SOURCES` in sync with the agent tables and the `agents/README.md` dependency table.
- **OpenCode subagents** — `scout` (external docs / dependency research) and `explore` (codebase search) are OpenCode **built-ins** invoked via the `task` tool, not skills and not from superpowers. No install. Claude Code has no equivalent for `architect-plan` — it has no `Agent`/`Task` tool and researches with `WebSearch`/`WebFetch`.
- **Ponytail** — agents auto-load [`ponytail`](https://github.com/DietrichGebert/ponytail) (external skill, install separately): plan agents design lazily (YAGNI, fewest files), build agents build lazily (the ladder: reuse/stdlib/native/dep before new code). TDD gate wins on *whether* to test; ponytail governs *how much* code to write.
- **Find-skills** — agents auto-load `find-skills` at project start to match installable skills to the stack. Build agents + combined `architect` have bash → run `npx skills find` and offer to install. Plan agents have no bash → recommend skills and write `npx skills add …` install commands into the plan doc.
- **Caveman mode** — always on: terse, no filler, full technical substance.

### Editing agent files

When changing an agent's behavior, keep these in sync:
- The agent `.md` file(s) themselves
- `agents/README.md` (workflow + notes)
- Root `README.md` Agents table
- `scripts/install_agents.py` if a file is added/renamed (see `AGENT_FILES` map)

---

## Install Script

`scripts/install_agents.py` fetches agent files from GitHub raw (no clone needed) and writes them into the tool's agent dir. Interactive by default; flags for scripting:

- `--platform {claude,opencode}`
- `--variant {combined,split}` (OpenCode only — Claude Code is always split)
- `--scope {global,project}` (`~/.claude` or `~/.opencode` vs. cwd)
- `--yes` (skip confirm; skip existing files), `--force` (overwrite), `--dry-run` (preview only)

The `AGENT_FILES` map keys `(platform, variant)` → filename list. Update it when agent files change.
