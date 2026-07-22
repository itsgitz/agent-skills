#!/usr/bin/env python3
"""Close tickets and move GitHub Projects v2 cards, via the `gh` CLI.

GitHub only. Resolves the "current active project" as the single open
project linked to the current repo; ambiguous or missing → pass --project.
"""

import argparse
import json
import re
import subprocess
import sys

GRAPHQL_LINKED_PROJECTS = (
    "query($owner:String!,$name:String!){ repository(owner:$owner, name:$name){ "
    "projectsV2(first:20){ nodes{ id title number closed url "
    "owner{ ... on Organization{login} ... on User{login} } } } } }"
)


class UsageError(Exception):
    """User-facing error: print message, exit 1, no traceback."""


def run_gh(args):
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise UsageError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def run_gh_json(args):
    return json.loads(run_gh(args))


def detect_repo():
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise UsageError("not in a git repo with an 'origin' remote — pass --repo owner/name")
    url = result.stdout.strip()
    match = re.search(r"github\.com[:/]([^/]+)/([^/.]+?)(?:\.git)?$", url)
    if not match:
        raise UsageError(f"origin remote isn't a github.com URL ({url}) — pass --repo owner/name")
    return match.group(1), match.group(2)


def repo_linked_projects(owner, repo):
    data = run_gh_json(
        [
            "api", "graphql",
            "-f", f"query={GRAPHQL_LINKED_PROJECTS}",
            "-f", f"owner={owner}",
            "-f", f"name={repo}",
        ]
    )
    return data["data"]["repository"]["projectsV2"]["nodes"]


def pick_active_project(projects, explicit_number=None):
    if explicit_number is not None:
        for project in projects:
            if project["number"] == explicit_number:
                return project
        raise UsageError(f"project #{explicit_number} isn't linked to this repo")

    open_projects = [p for p in projects if not p["closed"]]
    if not open_projects:
        raise UsageError("no open GitHub Project linked to this repo — pass --project N")
    if len(open_projects) > 1:
        names = ", ".join(f"#{p['number']} {p['title']!r}" for p in open_projects)
        raise UsageError(f"multiple open projects linked to this repo ({names}) — pass --project N")
    return open_projects[0]


def project_fields(owner, number):
    data = run_gh_json(["project", "field-list", str(number), "--owner", owner, "--format", "json"])
    return data["fields"]


def project_items(owner, number):
    data = run_gh_json(["project", "item-list", str(number), "--owner", owner, "--format", "json"])
    return data["items"]


def _status_field(fields):
    status_field = next((f for f in fields if f.get("name") == "Status"), None)
    if status_field is None or "options" not in status_field:
        raise UsageError("project has no 'Status' single-select field")
    return status_field


def find_status_option(fields, target_name):
    status_field = _status_field(fields)
    for option in status_field["options"]:
        if option["name"].lower() == target_name.lower():
            return status_field["id"], option["id"]
    names = ", ".join(o["name"] for o in status_field["options"])
    raise UsageError(f"unknown status {target_name!r} — valid: {names}")


def find_item_id(items, issue_number):
    for item in items:
        if item.get("content", {}).get("number") == issue_number:
            return item["id"]
    raise UsageError(f"issue/PR #{issue_number} isn't tracked in this project")


def edit_item_status(project_id, item_id, field_id, option_id):
    run_gh(
        [
            "project", "item-edit",
            "--id", item_id,
            "--field-id", field_id,
            "--project-id", project_id,
            "--single-select-option-id", option_id,
        ]
    )


def close_ticket(repo, number, kind):
    run_gh([kind, "close", str(number), "--repo", repo])


def resolve_project(args):
    owner, repo = args.repo.split("/", 1) if args.repo else detect_repo()
    projects = repo_linked_projects(owner, repo)
    project = pick_active_project(projects, args.project)
    return owner, repo, project


def cmd_resolve(args):
    _owner, _repo, project = resolve_project(args)
    print(f"#{project['number']} {project['title']!r} ({project['url']})")


def cmd_status_options(args):
    _owner, _repo, project = resolve_project(args)
    fields = project_fields(project["owner"]["login"], project["number"])
    for option in _status_field(fields)["options"]:
        print(option["name"])


def cmd_move(args):
    _owner, _repo, project = resolve_project(args)
    proj_owner = project["owner"]["login"]
    field_id, option_id = find_status_option(project_fields(proj_owner, project["number"]), args.to)
    item_id = find_item_id(project_items(proj_owner, project["number"]), args.issue)
    edit_item_status(project["id"], item_id, field_id, option_id)
    print(f"moved #{args.issue} to {args.to!r} in project #{project['number']} ({project['title']!r})")


def cmd_close(args):
    repo = args.repo or "/".join(detect_repo())
    close_ticket(repo, args.issue, args.type)
    print(f"closed {args.type} #{args.issue} in {repo}")
    if args.also_move_to:
        cmd_move(argparse.Namespace(
            repo=args.repo, project=args.project, issue=args.issue, to=args.also_move_to,
        ))


def build_parser():
    parser = argparse.ArgumentParser(
        prog="gh_project.py",
        description="Close tickets and move GitHub Projects v2 cards (GitHub only).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p):
        p.add_argument("--repo", help="owner/repo (default: detect from origin remote)")
        p.add_argument("--project", type=int, help="project number, if >1 project is linked")

    p_resolve = sub.add_parser("resolve", help="resolve the current active project linked to this repo")
    add_common(p_resolve)

    p_status = sub.add_parser("status-options", help="list valid Status column names")
    add_common(p_status)

    p_move = sub.add_parser("move", help="move a project item's Status field")
    add_common(p_move)
    p_move.add_argument("--issue", type=int, required=True)
    p_move.add_argument("--to", required=True, help="target Status column name")

    p_close = sub.add_parser("close", help="close an issue/PR")
    add_common(p_close)
    p_close.add_argument("--issue", type=int, required=True)
    p_close.add_argument("--type", choices=["issue", "pr"], default="issue")
    p_close.add_argument("--also-move-to", help="also move the project card to this Status column")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        {
            "resolve": cmd_resolve,
            "status-options": cmd_status_options,
            "move": cmd_move,
            "close": cmd_close,
        }[args.command](args)
    except UsageError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
