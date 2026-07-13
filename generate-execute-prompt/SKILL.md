---
name: generate-execute-prompt
description: >
  Use when a plan already exists under docs/plans/ and the user wants to execute
  it somewhere other than the current session — a different model (DeepSeek,
  GLM, Gemini, GPT), a different tool, or a fresh session with no shared
  context. Triggers: "generate execute prompt", "portable prompt for the
  plan", "prompt to build this plan in another model", "hand this plan to
  DeepSeek/GLM", "run the plan in a different model/tool", "give me a
  copy-paste prompt for this plan".
license: MIT
---

# Generate Execute Prompt

## Overview

Turns an approved plan document into a single self-contained execution
prompt — one fenced code block, safe to copy-paste into any model in any
agentic coding tool. The prompt embeds the full plan text plus a
model-agnostic set of execution rules (TDD ordering, batching, progress
reporting, stop-on-deviation). No tool names, no `@agent` mentions, no
vendor/model names — it works whether the target is Claude, DeepSeek, GLM,
or anything else with file-edit and shell tools.

## When to Use

- A plan is saved at `docs/plans/<feature|fix>-<name>/README.md` and approved
- User wants to execute that plan in a **different model or tool** than the
  one that wrote it (e.g. planned with Opus, wants to build with DeepSeek V4
  Pro or GLM 5.2)
- User wants a portable backup of the plan as a single prompt, independent of
  this repo's agent files or any specific harness

## When NOT to Use

- No plan exists yet — brainstorm and write the plan first
  (see `writing-plans` / the `architect-plan` agent)
- Executing in the **same** long-context session that wrote the plan — no
  hand-off needed, just continue (e.g. Claude Code with Sonnet 5's ~1M
  context can go straight from plan to build in one session)
- User wants the plan *changed* — that's a planning task, not prompt
  generation

## How It Works

1. **Locate the plan.**
   - If an argument is given, treat it as a plan slug and match
     `docs/plans/*<slug>*/README.md`.
   - Otherwise, use the most recently modified `docs/plans/*/README.md`.
   - If none found, or more than one matches ambiguously, ask the user which
     plan — never guess.
2. **Read the full plan file.**
3. **Emit exactly one fenced code block** containing the portable prompt
   (template below) with the plan's full text embedded at the end. Say
   nothing else except a one-line instruction to copy the block into the
   target model.

## Portable Prompt Template

Fill in `<PLAN_PATH>` and `<PLAN_TEXT>` from the located plan file. Every
other line stays as-is — it is intentionally vendor- and tool-agnostic.

````markdown
You are an implementation agent. Execute the plan below exactly as written.
Do not redesign the approach — if something in the plan seems wrong or
incomplete, stop and report it instead of improvising a fix.

Plan source: <PLAN_PATH> (read it directly if you have file access to this
repository; otherwise the full text is embedded below).

Execution rules:
- Test-first: for every code-changing task, write a failing test before any
  implementation (Red), write the minimum code to pass it (Green), then
  refactor. Skip this only for pure docs/config tasks.
- Work task by task, in the order given. Batch closely related tasks
  together rather than going file by file or doing everything at once.
  Respect any dependencies the plan states between tasks.
- After each batch, report in this format:
  Done: <what was completed>
  Next: <what's coming>
  Blocker: <anything, or "none">
  Tests: <pass/fail counts, or "skipped" with reason>
- If you hit something not covered by the plan, stop and report it — do not
  silently expand scope or redesign architecture.
- If you notice something broken outside the plan's scope, flag it; do not
  fix it unless asked.
- Run the verification commands listed in the plan using whatever shell
  access your environment provides. If a command is prefixed with a proxy
  tool (e.g. `rtk`) that isn't available in your environment, drop the
  prefix and run the bare command instead.

## Plan

<PLAN_TEXT>
````

## Example

```
User: I approved the plan at docs/plans/feature-rate-limiter/README.md.
      Generate an execute prompt — I want to build it with GLM 5.2 instead.

Skill: [reads docs/plans/feature-rate-limiter/README.md, fills the template]

Output: one fenced markdown block containing the filled template — copy
        this into the GLM 5.2 session to execute.
```
