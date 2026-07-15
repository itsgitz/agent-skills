---
name: generate-execute-prompt
description: >
  Use when a plan already exists under docs/plans/ and the user wants to
  execute it somewhere other than the current session — a different model
  (DeepSeek, GLM, Gemini, GPT), a different tool, or a fresh session with no
  shared context. Also use when no saved plan exists but the user just
  confirmed an ad-hoc action proposed earlier in this conversation (e.g. the
  agent asked "want me to apply these?" and the user said yes) and now wants
  a portable prompt for that action. Triggers: "generate execute prompt",
  "portable prompt for the plan", "prompt to build this plan in another
  model", "hand this plan to DeepSeek/GLM", "run the plan in a different
  model/tool", "give me a copy-paste prompt for this plan", "save this
  prompt", "save it to file".
license: MIT
---

# Generate Execute Prompt

## Overview

Turns a plan — saved on disk or just confirmed inline in conversation — into
a single self-contained execution prompt: one fenced code block, safe to
copy-paste into any model in any agentic coding tool. The prompt embeds the
full plan text plus a model-agnostic set of execution rules (TDD ordering,
batching, progress reporting, stop-on-deviation). No tool names, no
`@agent` mentions, no vendor/model names — it works whether the target is
Claude, DeepSeek, GLM, or anything else with file-edit and shell tools.

By default the prompt is only shown in chat for copy-paste. If the request
also signals intent to save it, it's additionally written to a gitignored
file under the project's `.claude/generated-prompts/`.

## When to Use

- A plan is saved at `docs/plans/<feature|fix>-<name>/README.md` and approved
- No saved plan exists, but the immediately preceding exchange was an
  ad-hoc action the agent proposed and the user just confirmed (e.g. "Want
  me to apply these? Small doc-only edits, same branch." → "yes")
- User wants to execute that plan/action in a **different model or tool**
  than the one that produced it (e.g. planned with Opus, wants to build
  with DeepSeek V4 Pro or GLM 5.2)
- User wants a portable backup of the plan/action as a single prompt,
  independent of this repo's agent files or any specific harness
- User asks to save the generated prompt to a file instead of (or in
  addition to) pasting it manually

## When NOT to Use

- Nothing has been proposed or confirmed yet, and no plan exists — brainstorm
  and design first (see `writing-plans` / the `architect-plan` agent). Don't
  fabricate a plan out of thin air.
- Executing in the **same** long-context session that wrote the plan — no
  hand-off needed, just continue (e.g. Claude Code with Sonnet 5's ~1M
  context can go straight from plan to build in one session)
- User wants the plan *changed* — that's a planning task, not prompt
  generation

## How It Works

1. **Locate the source.**
   - If an argument is given, treat it as a plan slug and match
     `docs/plans/*<slug>*/README.md`.
   - Otherwise, use the most recently modified `docs/plans/*/README.md`, if
     any exist.
   - **Fallback — no plan file matches:** check whether the immediately
     preceding exchange in this conversation is a proposed-and-confirmed
     ad-hoc action (agent proposed something, user replied affirmatively).
     If so, synthesize a minimal plan from it: what was proposed, files
     touched, why, and any verification step mentioned. Use that as the
     source instead of a file.
   - If neither a matching plan file nor a clear confirmed proposal exists,
     ask the user what to use as the source. Never guess.
2. **Read the full plan** (from the file) or **use the synthesized summary**
   (from conversation).
3. **Fill and emit the portable prompt** (template below) as one fenced code
   block.
   - File-backed: include the canonical path plus the full plan text.
   - Conversation-backed: state plainly that this came from the conversation,
     not a saved file — there's no path to reference, only the embedded text.
4. **Show the block in chat.** This is the default and always happens.
5. **Also save to a file, only if the request signals save intent** —
   phrases like "save it", "save this prompt", "save to file", "save it to
   .claude", or a combined ask like "generate and save". When saving:
   - Target: `.claude/generated-prompts/` in the current project (create the
     directory if missing).
   - Filename: `<slug>-execute-prompt.md` — `<slug>` is the plan's directory
     name (file-backed) or a short kebab-case slug derived from the
     synthesized topic (conversation-backed). Overwrite on regeneration, no
     timestamp.
   - Ensure `.claude/generated-prompts/` is gitignored — add a `.gitignore`
     entry (`.claude/generated-prompts/`) if the project doesn't already
     ignore it.
   - After writing, report the saved path. Saving is additive — the block
     is still shown in chat too.

## Portable Prompt Template

Fill in `<PLAN_SOURCE>` and `<PLAN_TEXT>` from the located source. Every
other line stays as-is — it is intentionally vendor- and tool-agnostic.

````markdown
You are an implementation agent. Execute the plan below exactly as written.
Do not redesign the approach — if something in the plan seems wrong or
incomplete, stop and report it instead of improvising a fix.

Plan source: <PLAN_SOURCE> (read it directly if you have file access to this
repository and a path is given above; otherwise the full text is embedded
below).

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
- For long-running commands (test suites, coverage, builds), run them in a
  single foreground call and give them enough time to finish. Do not
  background a process (`&`) and then poll it with repeated `sleep`/`ps` —
  many tools cap per-command time and give no completion callback, so
  polling loops forever. If your tool caps command duration, either raise
  that call's timeout, or write output to a log file in one call and read
  the log once afterward.

## Plan

<PLAN_TEXT>
````

`<PLAN_SOURCE>` for a file-backed plan is the path, e.g.
`docs/plans/feature-rate-limiter/README.md`. For a conversation-synthesized
plan, use: `synthesized from conversation — no saved file`.

## Examples

**File-backed:**

```
User: I approved the plan at docs/plans/feature-rate-limiter/README.md.
      Generate an execute prompt — I want to build it with GLM 5.2 instead.

Skill: [reads docs/plans/feature-rate-limiter/README.md, fills the template]

Output: one fenced markdown block containing the filled template — copy
        this into the GLM 5.2 session to execute.
```

**Ad-hoc fallback:**

```
Agent: Want me to apply these? Small doc-only edits, same branch.
User:  yes, and generate an execute prompt for that

Skill: [no docs/plans/ match → synthesizes a minimal plan from the just-
        confirmed edits, fills the template noting it's conversation-backed]

Output: one fenced markdown block — no file path, full synthesized plan
        embedded directly.
```

**With save:**

```
User: generate execute prompt and save it

Skill: [builds the prompt as above, writes it to
        .claude/generated-prompts/<slug>-execute-prompt.md, ensures that
        directory is gitignored]

Output: the fenced block in chat, plus: "Saved to
        .claude/generated-prompts/<slug>-execute-prompt.md"
```
