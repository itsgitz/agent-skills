# generate-execute-prompt

Turn an approved plan (`docs/plans/<feature|fix>-<name>/README.md`) into one
portable, model-agnostic execution prompt — copy-paste it into any model
(DeepSeek, GLM, Gemini, GPT, a fresh Claude session) or any agentic tool to
build the plan there.

## Install

```bash
# Path syntax
npx skills add itsgitz/agent-skills/generate-execute-prompt

# Flag syntax
npx skills add itsgitz/agent-skills --skill generate-execute-prompt
npx skills add itsgitz/agent-skills -s generate-execute-prompt
```

## Triggers

Claude invokes this skill when you ask about:

- "generate execute prompt"
- "portable prompt for the plan"
- "prompt to build this plan in another model"
- "hand this plan to DeepSeek/GLM"
- "run the plan in a different model/tool"
- "give me a copy-paste prompt for this plan"

## What It Generates

A single fenced code block containing:

1. An implementation-agent role header — execute exactly, don't redesign
2. The plan's canonical path plus its full text embedded inline
3. Model-agnostic execution rules: TDD ordering (Red → Green → Refactor),
   task-by-task batching, a `Done/Next/Blocker/Tests` progress format,
   stop-on-deviation, and out-of-scope flagging
4. A note to drop any `rtk`-style command proxy prefix if the target
   environment doesn't have it

No Claude-specific tool names, `@agent` mentions, or vendor/model names
appear in the output — it's readable and executable by any model with
file-edit and shell access, with or without access to this repository.

## Full Reference

See [SKILL.md](./SKILL.md) for the full template and plan-lookup rules.
