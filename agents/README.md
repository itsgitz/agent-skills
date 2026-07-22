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
feature  →  docs/plans/feature-<name>/{README.md, PROGRESS.md}
bug fix   →  docs/plans/fix-<name>/{README.md, PROGRESS.md}
<name>    =  short kebab-case slug (e.g. user-auth, login-crash)
```

- `README.md` is the **canonical** plan doc — GitHub renders it when the dir is opened.
- `PROGRESS.md` is the **build tracker** — a task checklist (`- [ ]` per plan task) plus a batch log.
- Supporting files (diagrams, scratch notes) may live beside it in the same dir.
- The planning half **writes** both (`README.md` = plan, `PROGRESS.md` = scaffolded checklist); the
  build half **reads** the README and ticks off / logs into `PROGRESS.md` as it executes.

---

## Workflows

### Claude Code — plan/build split

Planning needs deep reasoning (opus); execution needs speed (sonnet). These are two agents, not
two mandatory sessions: subagents honor their own `model:`, so an opus session can spawn
`@architect-build` as a sonnet subagent. The split is a role boundary — `architect-plan` never
executes — enforced by giving it no shell/edit tools, not by session separation.

**Session A — plan:**

```
@architect-plan  →  brainstorm → design → write plan doc → hand off
```

- Read-only. No file edits. No shell. Produces a saved plan document only.
- Writes the plan to `docs/plans/<feature|fix>-<name>/README.md` (see **Plan location**).
- Ends with a build menu and stops for the user to pick:
  1. **Same session (default)** — main thread spawns `@architect-build` as a sonnet subagent;
     it reads the plan from disk. No new session needed. `architect-plan` can't spawn it itself
     (no `Agent`/`Bash` tool) — the main thread does, after hand-off.
  2. **Separate session** — open a new Claude Code session and call `@architect-build` (clean context).
  3. **Another model/tool** (DeepSeek V4 Pro, GLM 5.2, Kimi, etc.) — invoke
     `/generate-execute-prompt` for a portable, model-agnostic execution prompt.

**Session B — build:**

```
@architect-build  →  read plan → confirm scope → execute → verify
```

- Reads the plan saved in session A from `docs/plans/<feature|fix>-<name>/README.md`.
- Executes task by task. Checkpoints after each phase.
- If plan is missing or ambiguous → stops and says so. Does not improvise.

**Why a split, not two sessions?** `@architect-plan` runs on `opus`, `@architect-build` on
`sonnet`. A subagent honors its own `model:` regardless of the main session's model, so opus can
spawn the sonnet builder in the same session — the hand-off works because the plan is saved to
disk, not because sessions are separate. A fresh session is optional (clean context), not required.

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

To build with a different model/tool instead (DeepSeek V4 Pro, GLM 5.2, etc.), invoke
`/generate-execute-prompt` for a portable, model-agnostic execution prompt.

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
- To build with a different model/tool instead (DeepSeek V4 Pro, GLM 5.2, etc.), invoke
  `/generate-execute-prompt` for a portable, model-agnostic execution prompt.

**Why split?** The combined `architect` agent's gate is prose-only — it can leak into build
after planning. Splitting removes the build instructions from the planning agent entirely and
denies it shell, so the gate holds. The combined `architect` agent remains for users who
prefer a single conversation.

---

## Command proxy

Executing agents (`architect-build` both platforms, and OpenCode's combined `architect`) proxy
all shell commands through [`rtk`](https://github.com/rtk-ai/rtk) — a token-optimized CLI proxy
— by default.

- Default: prefix commands with `rtk` (`rtk git status`, `rtk pnpm test`).
- Detect once per session via `command -v rtk`. Absent → fall back to the bare CLI, no prefix.
- Plan-only agents (`architect-plan` both platforms) hold no shell — they just note that
  verification commands *written into* the plan should use the `rtk` prefix (with fallback),
  since `architect-build` is the one that runs them.

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

### Script install (alternative)

Fetches the same files from GitHub raw over the network — no clone required. Interactive by
default, with flags for scripting.

```bash
# interactive picker
python3 scripts/install_agents.py

# or without cloning the repo:
curl -fsSL https://raw.githubusercontent.com/itsgitz/agent-skills/master/scripts/install_agents.py | python3 -

# non-interactive examples
python3 scripts/install_agents.py --platform claude --scope project --yes
python3 scripts/install_agents.py --platform opencode --variant split --scope global --yes

# preview without writing anything
python3 scripts/install_agents.py --platform opencode --variant combined --scope global --dry-run
```

Flags: `--platform {claude,opencode}`, `--variant {combined,split}` (OpenCode only — Claude Code
always installs the plan/build split), `--scope {global,project}`, `--yes` (skip confirmation;
skip existing files instead of prompting), `--force` (overwrite existing files), `--dry-run`
(print planned actions; fetches and writes nothing). Omit any flag to be prompted for it.

### Dependency skills

The agents load two [mattpocock/skills](https://github.com/mattpocock/skills). `install_agents.py`
installs the **agent files only** — install these skills separately. Install **globally** (`-g`,
once for all projects — recommended for the agents) or per-project (drop `-g`):

```bash
# global — installs once, available in every project
npx skills add https://github.com/mattpocock/skills --skill tdd -g -y
npx skills add https://github.com/mattpocock/skills --skill code-review -g -y

# or per-project (run inside the repo, no -g)
# cd <your-project>
# npx skills add https://github.com/mattpocock/skills --skill tdd -y
# npx skills add https://github.com/mattpocock/skills --skill code-review -y
```

With `-g`, the CLI prints a harmless `PromptScript does not support global skill installation`
line — ignore it. The **universal** skill format still installs globally (to `~/.agents/skills/`,
symlinked into `~/.claude/skills/` and OpenCode), which is what the agents load. Only the unused
PromptScript variant skips the global step.

If `npx skills` errors with `Unknown command: skills` (a shell/proxy rewriting `npx`), run it via
the full npx path: `$(command -v npx) skills add …`.

Both verified installing cleanly (handles match the agent-doc references):

| Skill | Handle | Gen | Socket | Snyk |
|-------|--------|-----|--------|------|
| `tdd` | `tdd` | Safe | 0 alerts | Low |
| `code-review` | `code-review` | Safe | 0 alerts | Med |

> **Security note:** at install time skills.sh reports `code-review` as **Snyk: Med Risk** (`tdd`
> is Low). Expected — `code-review` reads your code and spawns parallel review sub-agents, so it
> runs with broad agent permissions. Not a blocker; review before use. Details:
> <https://skills.sh/mattpocock/skills>

---

## Notes

- Caveman mode is always on for every agent — terse, no filler, full technical substance.
- Build agents auto-load `systematic-debugging` (superpowers) when context matches. Brainstorming
  and plan-writing are **inline** in the plan agents (`# BRAINSTORM STRUCTURE` / `# PLAN STRUCTURE`),
  not external skills — self-contained when installed without superpowers.
- All agents also auto-load [`ponytail`](https://github.com/DietrichGebert/ponytail) (external
  skill, install separately) for lazy/minimal output — plan agents design lazily (YAGNI),
  build agents build lazily (reuse/stdlib/native/dep before new code). TDD gate still wins on
  *whether* to test; ponytail only governs *how much* code to write.
- All agents auto-load [`find-skills`](https://skills.sh/) to match installable skills to the project stack. Build agents + combined `architect` have bash → run `npx skills find` and offer to install. Plan agents (`architect-plan` both platforms) have no bash → they recommend skills and write the `npx skills add …` install commands into the plan doc for the build half or user to run.
- `architect-build` (both platforms) will refuse to start if no plan exists — it won't improvise a design.
- Build agents run the `code-review` skill ([mattpocock/skills](https://github.com/mattpocock/skills) — Standards + Spec axes) before declaring work complete, passing the plan `docs/plans/<feature|fix>-<name>/README.md` as the spec so the Spec axis reviews against the plan (not a branch-name guess): `npx skills add https://github.com/mattpocock/skills --skill code-review`. Plan agents don't review (nothing built yet).
- The split OpenCode `architect-plan` enforces the no-execution gate via `bash: deny` (machine-level),
  not just prose — it physically cannot run shell.
- TDD is a hard gate for every agent: every code change follows test-first (Red→Green→Refactor) via the `tdd` skill ([mattpocock/skills](https://github.com/mattpocock/skills)). Install **globally** (`-g`, once for all projects) or per-project: `npx skills add https://github.com/mattpocock/skills --skill tdd -g` (see **Dependency skills** for the harmless PromptScript note). Build agents can install it via their find-skills flow; plan agents write the install command into the plan doc. Pure docs/config tasks are exempt.
- Shell-executing agents proxy commands through `rtk` by default, falling back to the bare CLI when rtk is absent. See **Command proxy** above.
