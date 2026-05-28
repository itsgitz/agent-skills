# agent-skills

[![skills.sh](https://skills.sh/b/itsgitz/agent-skills)](https://skills.sh/itsgitz/agent-skills)

Personal Claude Code skill collection by [Anggit M Ginanjar](https://github.com/itsgitz).

Skills are reusable reference guides that help AI agents apply proven techniques and patterns consistently across projects.

## Quick Install

Install all skills from this repository at once:

```bash
npx skills add itsgitz/agent-skills
```

## Skills

| Skill | Description | Install |
|-------|-------------|---------|
| [docker-vps-deploy](./docker-vps-deploy/) | Deploy Dockerized app to VPS via SSH — no container registry, image travels as `.tar.gz` | `npx skills add itsgitz/agent-skills/docker-vps-deploy` |

## Usage

Install a specific skill into your project:

```bash
npx skills add itsgitz/agent-skills/<skill-name>
```

Once installed, your AI agent will automatically invoke the skill when relevant triggers are detected (e.g., "deploy to VPS", "rsync docker image").

Skills from this repository are discoverable on [skills.sh](https://skills.sh/itsgitz/agent-skills).

## Adding Skills

See [docs/adding-skills.md](./docs/adding-skills.md) for conventions and checklist.

## License

MIT — see [LICENSE](./LICENSE).
