# agent-skills

Personal Claude Code skill collection by [Anggit M Ginanjar](https://github.com/itsgitz).

Skills are reusable reference guides that help Claude agents apply proven techniques and patterns consistently across projects.

## Skills

| Skill | Description | Install |
|-------|-------------|---------|
| [docker-vps-deploy](./docker-vps-deploy/) | Deploy Dockerized app to VPS via SSH — no container registry, image travels as `.tar.gz` | `npx skills add itsgitz/agent-skills/docker-vps-deploy` |

## Usage

Install a skill into your project:

```bash
npx skills add itsgitz/agent-skills/<skill-name>
```

Once installed, Claude will automatically invoke the skill when relevant triggers are detected (e.g., "deploy to VPS", "rsync docker image").

## Adding Skills

See [docs/adding-skills.md](./docs/adding-skills.md) for conventions and checklist.

## License

MIT — see [LICENSE](./LICENSE).
