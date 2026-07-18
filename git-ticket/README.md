# git-ticket

Turn your case/context into a **forge ticket** — a GitHub issue/PR or GitLab
issue/MR — and create it via the forge CLI (`gh` / `glab`). When the CLI is
missing, unauthenticated, or the host is unsupported (Bitbucket, self-hosted),
it falls back to a ready-to-paste title + markdown body. Bodies are kept
simple — a few sentences, headings only when needed. Always drafts and
confirms before creating; never creates silently, never hard-fails.

## Install

```bash
# Path syntax
npx skills add itsgitz/agent-skills/git-ticket

# Flag syntax
npx skills add itsgitz/agent-skills --skill git-ticket
npx skills add itsgitz/agent-skills -s git-ticket
```

## Update

```bash
npx skills update git-ticket
```

## Triggers

Claude invokes this skill when you ask about:

- "create a github issue" / "file a bug"
- "open a PR" / "make a pull request for this branch"
- "open a GitLab MR" / "raise a merge request" / "file a gitlab issue"
- a house title convention like `[API/{MODULE}] summary`
- getting a title + markdown body to paste in manually

## Title Format

By default the title is the commit subject. To enforce a house convention,
put a single template line in `.git-ticket-format` at the repo root:

```
[API/{MODULE}] {title}
```

- `{title}` → the generated one-line summary.
- Any other `{SLOT}` (e.g. `{MODULE}`, `{SERVICE_NAME}`) → filled from your
  context (branch, changed dir, the case text) or asked once. No raw
  placeholder ever ships in the final title.

No config file? The skill **asks** you for the format, pre-filling a pattern
inferred from your recent issues/PRs/MRs on the remote as the suggested
default. Give one and it offers to save it to `.git-ticket-format` so it
stops asking; skip it and the title defaults to the commit subject.

## Fallback

If `gh`/`glab` isn't installed or authenticated, or the remote host isn't
supported, the skill prints the title + full markdown body in a fenced block
(plus the remote's "new PR/MR" URL when known) so you can create it by hand.
It tells you plainly that it did not create the ticket.

## Full Reference

See [SKILL.md](./SKILL.md) for forge detection, the title lookup order, body
generation, and the draft-then-confirm flow.
