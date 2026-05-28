# agent-skills

[![skills.sh](https://skills.sh/b/itsgitz/agent-skills)](https://skills.sh/itsgitz/agent-skills)

Personal skill collection by [Anggit M Ginanjar](https://github.com/itsgitz).

Skills are reusable reference guides that help AI agents apply proven techniques and patterns consistently across projects. Compatible with any AI agent that supports `~/.agents` skills (Claude Code, Cursor, OpenCode, and more).

## Quick Install

Install all skills from this repository at once:

```bash
npx skills add itsgitz/agent-skills
```

Or use the `--skill` flag for more control:

```bash
npx skills add itsgitz/agent-skills --skill '*'   # all skills
npx skills add itsgitz/agent-skills --skill docker-vps-deploy  # specific skill
```

## Skills

| Skill | Description | Install |
|-------|-------------|---------|
| [docker-vps-deploy](./docker-vps-deploy/) | Deploy Dockerized app to VPS via SSH — no container registry, image travels as `.tar.gz` | `npx skills add itsgitz/agent-skills/docker-vps-deploy` |

## Usage

Install a specific skill into your project — two equivalent syntaxes:

```bash
# Path syntax
npx skills add itsgitz/agent-skills/<skill-name>

# Flag syntax (handy for multiple skills)
npx skills add itsgitz/agent-skills --skill <skill-name>
npx skills add itsgitz/agent-skills --skill skill-a skill-b  # multiple at once
```

Once installed, your AI agent will automatically invoke the skill when relevant triggers are detected (e.g., "deploy to VPS", "rsync docker image").

Skills from this repository are discoverable on [skills.sh](https://skills.sh/itsgitz/agent-skills).

## Adding Skills

See [docs/adding-skills.md](./docs/adding-skills.md) for conventions and checklist.

## License

MIT — see [LICENSE](./LICENSE).
