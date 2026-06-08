# Agents

Agent definitions for AI coding tools. Drop these into your tool's agent/config directory.

## Agents

| Agent | File | Platform | Model | Role |
|-------|------|----------|-------|------|
| architect-plan | `architect.claude-plan.md` | Claude Code | opus | Plan-only — never executes |
| architect-build | `architect.claude-build.md` | Claude Code | sonnet | Build-only — executes saved plans |
| architect | `architect.opencode.md` | OpenCode | configurable | Plan + build, gated |

---

## Plan location

All three agents persist plans as documentation under `docs/plans/`, one directory per plan:

```
feature  →  docs/plans/feature-<name>/README.md
bug fix   →  docs/plans/fix-<name>/README.md
<name>    =  short kebab-case slug (e.g. user-auth, login-crash)
```

- `README.md` is the **canonical** plan doc — GitHub renders it when the dir is opened.
- Supporting files (diagrams, scratch notes) may live beside it in the same dir.
- The planning half **writes** this README; the build half **reads** from the same path.

---

## Workflows

### Claude Code — two-session model

Claude Code cannot switch models mid-session. Planning needs deep reasoning (opus); execution
needs speed (sonnet). Two separate sessions required.

**Session A — plan:**

```
@architect-plan  →  brainstorm → design → write plan doc → hand off
```

- Read-only. No file edits. No shell. Produces a saved plan document only.
- Writes the plan to `docs/plans/<feature|fix>-<name>/README.md` (see **Plan location**).
- Ends with: "Plan saved. Open a new Claude Code session and call `@architect-build`."

**Session B — build:**

```
@architect-build  →  read plan → confirm scope → execute → verify
```

- Reads the plan saved in session A from `docs/plans/<feature|fix>-<name>/README.md`.
- Executes task by task. Checkpoints after each phase.
- If plan is missing or ambiguous → stops and says so. Does not improvise.

**Why two sessions?** `@architect-plan` runs on `opus`. `@architect-build` runs on `sonnet`.
Claude Code can't hot-swap models, so you need a fresh session for the build half.

---

### OpenCode — single agent with execution gate

OpenCode's `architect` agent handles both phases in one conversation, but enforces a hard
stop between plan and build.

**Flow:**

```
architect  →  brainstorm → design → write plan → STOP
                                                    ↓
                              wait for "execute" or "continue"
                                                    ↓
                                               build → verify
```

**Gate rule:** After the plan is written, the agent halts completely. No edits. No shell.
It resumes build mode only when you type one of:

- `execute`
- `continue`
- `go`
- `build it` / `run it`

Any other reply (questions, feedback, "looks good") → agent treats it as plan feedback and
stays halted. If you say "looks good" without a trigger, the agent will prompt you:
`"Type execute to start building."`

---

## Install

Copy the relevant file into your tool's agent directory:

**Claude Code** — place in `~/.claude/agents/` or `.claude/agents/` in your project:

```bash
# plan agent
curl -O https://raw.githubusercontent.com/itsgitz/agent-skills/master/agents/architect.claude-plan.md

# build agent
curl -O https://raw.githubusercontent.com/itsgitz/agent-skills/master/agents/architect.claude-build.md
```

**OpenCode** — place in `~/.opencode/agents/` or `.opencode/agents/` in your project:

```bash
curl -O https://raw.githubusercontent.com/itsgitz/agent-skills/master/agents/architect.opencode.md
```

---

## Notes

- Caveman mode is always on for all three agents — terse, no filler, full technical substance.
- All agents load superpowers skills automatically when context matches (`brainstorming`,
  `writing-plans`, `systematic-debugging`).
- `architect-build` will refuse to start if no plan exists — it won't improvise a design.
