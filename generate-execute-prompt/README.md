# generate-execute-prompt

Turn a plan — saved at `docs/plans/<feature|fix>-<name>/README.md`, or just
confirmed inline in conversation with no saved file — into one portable,
model-agnostic execution prompt. Copy-paste it into any model (DeepSeek, GLM,
Gemini, GPT, a fresh Claude session) or any agentic tool to build it there.

## Install

```bash
# Path syntax
npx skills add itsgitz/agent-skills/generate-execute-prompt

# Flag syntax
npx skills add itsgitz/agent-skills --skill generate-execute-prompt
npx skills add itsgitz/agent-skills -s generate-execute-prompt
```

## Update

```bash
npx skills update generate-execute-prompt
```

## Triggers

Claude invokes this skill when you ask about:

- "generate execute prompt"
- "portable prompt for the plan"
- "prompt to build this plan in another model"
- "hand this plan to DeepSeek/GLM"
- "run the plan in a different model/tool"
- "give me a copy-paste prompt for this plan"
- "save this prompt" / "save it to file"

## No Saved Plan? It Still Works

If no `docs/plans/` file matches, and the agent just proposed something
ad-hoc that you confirmed (e.g. "Want me to apply these? Small doc-only
edits, same branch." → "yes"), the skill synthesizes a minimal plan from
that exchange and builds the prompt from it — no plan doc required.

## What It Generates

A single fenced code block containing:

1. An implementation-agent role header — execute exactly, don't redesign
2. The plan's source — canonical path + full text (file-backed), or a note
   that it's synthesized from conversation (no saved file) + the embedded text
3. Model-agnostic execution rules: TDD ordering (Red → Green → Refactor),
   task-by-task batching, a `Done/Next/Blocker/Tests` progress format,
   stop-on-deviation, and out-of-scope flagging
4. A note to drop any `rtk`-style command proxy prefix if the target
   environment doesn't have it

No Claude-specific tool names, `@agent` mentions, or vendor/model names
appear in the output — it's readable and executable by any model with
file-edit and shell access, with or without access to this repository.

## Saving to a File

By default the prompt is only shown in chat. Ask to save it ("save it",
"save this prompt", "generate and save") and it's also written to
`.claude/generated-prompts/<slug>-execute-prompt.md` in the current project —
gitignored automatically, overwritten on regeneration.

## Full Reference

See [SKILL.md](./SKILL.md) for the full template, fallback rules, and save behavior.
