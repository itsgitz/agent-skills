# Agents

Agent definitions for AI coding tools. Drop these into your tool's agent/config directory.

## Agents

| Agent | File | Platform | Model | Role |
|-------|------|----------|-------|------|
| architect-plan | `architect.claude-plan.md` | Claude Code | opus | Plan-only — never executes |
| architect-build | `architect.claude-build.md` | Claude Code | sonnet | Build-only — executes saved plans |
| architect | `architect.opencode.md` | OpenCode | configurable | Plan + build in one agent, gated |
| architect-plan | `architect.opencode-plan.md` | OpenCode | configurable | Plan-only — `bash` denied, never executes |
| architect-build | `architect.opencode-build.md` | OpenCode | configurable | Build-only — executes saved plans |

---

## Plan location

All agents persist plans as documentation under `docs/plans/`, one directory per plan:

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

### OpenCode — two-agent split (recommended)

Same plan/build separation as Claude Code, but in one OpenCode session via Tab-switch. The
gate is enforced by the **runtime**, not prose: `architect-plan` sets `bash: deny`, so it
*cannot* run, test, or build anything. There is no build path to slide into.

**Flow:**

```
architect-plan (primary)  →  brainstorm → design → write plan doc → STOP
                                                    ↓
                                  [user Tab-switches agent]
                                                    ↓
architect-build (primary) →  read plan → confirm scope → execute → verify
```

- `architect-plan`: read/search/research + writes the plan doc only. `bash` denied — no shell.
  Ends with "Plan saved. Tab-switch to architect-build to execute."
- `architect-build`: holds the execution tools (`edit`, `bash`) and build instructions.
  Reads the plan from `docs/plans/<feature|fix>-<name>/README.md`. Refuses to start with no plan.

**Why split?** The combined `architect` agent's gate is prose-only — it can leak into build
after planning. Splitting removes the build instructions from the planning agent entirely and
denies it shell, so the gate holds. The combined `architect` agent remains for users who
prefer a single conversation.

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
# combined agent (plan + build in one, gated)
curl -O https://raw.githubusercontent.com/itsgitz/agent-skills/master/agents/architect.opencode.md

# two-agent split (recommended)
curl -O https://raw.githubusercontent.com/itsgitz/agent-skills/master/agents/architect.opencode-plan.md
curl -O https://raw.githubusercontent.com/itsgitz/agent-skills/master/agents/architect.opencode-build.md
```

---

## Notes

- Caveman mode is always on for every agent — terse, no filler, full technical substance.
- All agents load superpowers skills automatically when context matches (`brainstorming`,
  `writing-plans`, `systematic-debugging`).
- `architect-build` (both platforms) will refuse to start if no plan exists — it won't improvise a design.
- The split OpenCode `architect-plan` enforces the no-execution gate via `bash: deny` (machine-level),
  not just prose — it physically cannot run shell.
- TDD is a hard gate for every agent: every code change follows test-first (Red→Green→Refactor) via the `test-driven-development` skill. Pure docs/config tasks are exempt.
