---
name: git-ticket
description: >
  Use when the user wants to open a GitHub issue or pull request, a GitLab
  issue or merge request, or any forge ticket from their case/context —
  "create a github issue", "open a PR", "raise a MR", "file a bug",
  "open a merge request", "make a pull request for this branch". Also use
  when they mention a house title convention like `[API/{MODULE}] summary`,
  or when a forge CLI is missing/unauthed and they need a title + markdown
  body to paste in manually. Covers GitHub (gh) and GitLab (glab); unknown
  hosts (Bitbucket, self-hosted) fall back to markdown.
license: MIT
---

# Git Ticket

## Overview

Turns a user's case/context into a **forge ticket** — a GitHub issue/PR or
GitLab issue/MR — and creates it via the forge CLI when possible. When the
CLI is missing, unauthenticated, the host is unsupported, or the user
declines, it **falls back** to printing the title + a ready-to-paste
markdown body. It never hard-fails and never creates silently: the draft is
always shown and confirmed before anything is pushed to the remote.

"Ticket" is deliberately generic — one flow spans issues, PRs, and MRs, with
room to add new forges (Bitbucket, self-hosted) later.

## When to Use

- "Create/open a GitHub issue" or "open/raise a PR / pull request"
- "Open a GitLab MR / merge request" or "file a GitLab issue"
- "Make a PR for my current branch", "file a bug about X"
- User has a bug report, feature request, or a finished branch to propose
- Team uses a title convention (e.g. `[API/{MODULE}] summary`) and wants it
  applied consistently
- No forge CLI / not authed → user wants a title + markdown body to paste

## When NOT to Use

- Writing the **commit message** itself → that's a commit task, not a ticket
- Editing or commenting on an **existing** issue/PR/MR → use `gh`/`glab`
  directly; this skill is for creating new ones
- Pure local git work (branching, rebasing, staging) with no remote artifact

## Quick Reference

| Remote host | CLI | Create issue | Create PR/MR |
|---|---|---|---|
| `github.com` / GH Enterprise | `gh` | `gh issue create` | `gh pr create` |
| host contains `gitlab` | `glab` | `glab issue create` | `glab mr create` |
| anything else (Bitbucket, …) | — | markdown fallback | markdown fallback |

Shell proxy: if `command -v rtk` succeeds, prefix commands with `rtk`;
otherwise run the bare CLI.

## Flow

### 1. Detect forge

Parse the remote host: `git remote get-url origin`.

- `github.com` or a GitHub Enterprise host → **gh**
- host contains `gitlab` (gitlab.com or self-hosted) → **glab**
- anything else (e.g. `bitbucket.org`) → **unsupported CLI → markdown
  fallback** (step 6). New forges plug in here.

### 2. Detect item type

From user intent:

- "issue", bug report, feature request → **issue**
- "PR", "pull request", "MR", "merge request", or a feature branch with
  commits ahead of the base branch → **PR/MR**
- Ambiguous → ask once.

### 3. Tooling gate (create path only)

- `command -v gh` / `command -v glab` — binary present?
- `gh auth status` / `glab auth status` — authenticated?
- Missing or unauthed → **markdown fallback** (step 6). Do not attempt
  `curl` against the API unless the user explicitly supplies a token.

### 4. Resolve the title

Lookup order — stop at the first that yields a template:

1. **Repo config file** `.git-ticket-format` at repo root. One template line,
   shared across forges and item types, e.g.:

   ```
   [API/{MODULE}] {title}
   ```

2. **Infer from recent remote items** if no config file:
   `gh issue list -L 10` / `gh pr list -L 10` /
   `glab issue list` / `glab mr list`. If a clear prefix pattern emerges
   (e.g. most titles start `[API/...]`), reuse it.
3. **Default** — the commit subject: `git log -1 --pretty=%s`.

**Placeholders in the template:**

- `{title}` → the generated one-line summary of the case.
- Any other `{SLOT}` (e.g. `{MODULE}`, `{SERVICE_NAME}`) → fill from the
  user's context if the value is obvious (branch name, changed dir, the
  case text); otherwise **ask once** for the slot value. Never leave a raw
  `{SLOT}` in the final title.

### 5. Generate the body

Auto-pick the source:

- **Issue** → the user's prose/context.
  - Bug: `## Context`, `## Expected`, `## Actual`, optional `## Repro`.
  - Feature: `## Context`, `## Proposal`.
- **PR/MR** → the branch diff + commit messages, blended with any user prose:
  - `git log <base>..HEAD --pretty=%s` and `git diff --stat <base>..HEAD`
  - Sections: `## Summary`, `## Changes`, `## Testing`.
- Both signals present → blend prose into the relevant sections.

### 6. Draft-then-confirm — ALWAYS

Creating a ticket is outward-facing and hard to undo. The draft is shown and
confirmed every time, with no exceptions.

1. Show the resolved **title + full markdown body** in one fenced block.
2. Get explicit user confirmation.
3. **On confirm + tooling available** → create and return the URL:
   - `gh issue create --title "<title>" --body "<body>"`
   - `gh pr create --title "<title>" --body "<body>" --base <base> --head <branch>`
   - `glab issue create --title "<title>" --description "<body>"`
   - `glab mr create --title "<title>" --description "<body>" --source-branch <branch> --target-branch <base>`
4. **Tooling unavailable, unsupported host, or user declines create** →
   the fenced block IS the deliverable. Add one line:
   `Create manually — CLI unavailable/unauthed/declined.`
   For a PR/MR on a pushed branch, also give the remote's "new PR/MR" URL if
   known (e.g. `https://bitbucket.org/<ws>/<repo>/pull-requests/new?source=<branch>`).

## Fallback Rules

- Never hard-fail. Missing CLI, no auth, unknown host → markdown, not error.
- Never fabricate success. If you didn't create it, say so and hand back the
  markdown + link.
- Never create without showing the draft first, even if the user said
  "just do it" — show the draft, then create on their OK in the same turn.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Plain descriptive title, ignoring house style | Run the step-4 lookup: config file → infer from remote → commit subject |
| Leaving a raw `{MODULE}` in the title | Fill from context or ask once; never ship a literal placeholder |
| Creating immediately without a draft | Always show title + body and confirm first |
| Hard-failing when `gh`/`glab` missing | Fall back to markdown for manual creation |
| Using `gh` for a GitLab remote (or vice versa) | Detect the host from `git remote get-url origin` first |
| Guessing the PR base branch | Use the repo default (`git symbolic-ref refs/remotes/origin/HEAD`) or ask |

## Examples

### GitHub PR, with a config title format

```
User: open a PR for my current branch

Skill:
  - remote = github.com → gh; gh installed + authed
  - .git-ticket-format found: "[API/{MODULE}] {title}"
  - branch = feature/rate-limit; {MODULE} → RateLimit (from branch/changed dir)
  - body from: git log main..HEAD + git diff --stat

Draft shown:
  Title: [API/RateLimit] Add token-bucket rate limiter to gateway
  ## Summary
  ...
  ## Changes
  ...
  ## Testing
  ...

User: looks good

Skill runs:
  gh pr create --title "[API/RateLimit] Add token-bucket rate limiter to gateway" \
    --body "<body>" --base main --head feature/rate-limit
  → returns the PR URL
```

### Unsupported host → markdown fallback

```
User: open a PR for my current branch
  - remote = bitbucket.org → no wired CLI

Skill: shows the title + full markdown body in a fenced block, plus:
  "Create manually — Bitbucket CLI not supported. New PR:
   https://bitbucket.org/<ws>/<repo>/pull-requests/new?source=feature/x"
```
