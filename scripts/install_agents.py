#!/usr/bin/env python3
"""Install architect agent files for Claude Code / OpenCode from GitHub raw."""

import argparse
import os
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

REPO_RAW_BASE = "https://raw.githubusercontent.com/itsgitz/agent-skills/master/agents/"

AGENT_FILES = {
    ("claude", "split"): ["architect.claude-plan.md", "architect.claude-build.md"],
    ("opencode", "combined"): ["architect.opencode.md"],
    ("opencode", "split"): ["architect.opencode-plan.md", "architect.opencode-build.md"],
}


def target_dir(platform, scope):
    home_dir = ".claude" if platform == "claude" else ".opencode"
    base = Path.home() if scope == "global" else Path.cwd()
    return base / home_dir / "agents"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="install_agents.py",
        description="Install architect agent files for Claude Code / OpenCode from GitHub raw.",
    )
    parser.add_argument("--platform", choices=["claude", "opencode"])
    parser.add_argument("--variant", choices=["combined", "split"])
    parser.add_argument("--scope", choices=["global", "project"])
    parser.add_argument(
        "-y", "--yes", action="store_true",
        help="skip the confirmation prompt; on file conflict, skip existing files instead of asking",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="overwrite existing files without prompting",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="print what would be installed; fetch and write nothing",
    )
    return parser.parse_args(argv)


def prompt_choice(question, options):
    print(question)
    for i, (_, label) in enumerate(options, 1):
        print(f"  {i}) {label}")
    while True:
        raw = input("> ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1][0]
        print(f"enter a number 1-{len(options)}")


def resolve_selection(args):
    platform = args.platform or prompt_choice(
        "Platform?", [("claude", "Claude Code"), ("opencode", "OpenCode")]
    )

    if platform == "claude":
        if args.variant == "combined":
            print(
                "error: Claude Code has no combined agent — only plan+build split is "
                "available. Omit --variant or use --variant split.",
                file=sys.stderr,
            )
            sys.exit(2)
        variant = "split"
    else:
        variant = args.variant or prompt_choice(
            "Variant?",
            [
                ("combined", "Combined (plan+build in one agent)"),
                ("split", "Split — plan-only + build-only (recommended)"),
            ],
        )

    scope = args.scope or prompt_choice(
        "Scope?",
        [
            ("global", f"Global ({target_dir(platform, 'global')})"),
            ("project", f"Project-local ({target_dir(platform, 'project')})"),
        ],
    )

    return platform, variant, scope


def confirm_plan(files, dest_dir):
    print(f"Will install into {dest_dir}:")
    for f in files:
        print(f"  {f}")
    reply = input("Proceed? [y/N] ").strip().lower()
    return reply in ("y", "yes")


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} fetching {url}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"network error fetching {url}: {e.reason}") from e


def write_atomic(dest, data):
    fd, tmp = tempfile.mkstemp(dir=dest.parent, prefix=dest.name + ".")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, dest)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def install_one(filename, dest_dir, args):
    dest = dest_dir / filename
    exists = dest.exists() and not args.force

    if args.dry_run:
        if exists:
            print(f"[dry-run] would skip (exists): {dest}")
        else:
            print(f"[dry-run] would fetch {REPO_RAW_BASE + filename} -> {dest}")
        return

    if exists:
        if args.yes:
            print(f"skip (exists): {dest}")
            return
        reply = input(f"{dest} exists — overwrite? [y/N] ").strip().lower()
        if reply not in ("y", "yes"):
            print("skip")
            return

    dest_dir.mkdir(parents=True, exist_ok=True)
    data = fetch(REPO_RAW_BASE + filename)
    write_atomic(dest, data)
    print(f"installed {dest}")


def main(argv=None):
    args = parse_args(argv)

    try:
        platform, variant, scope = resolve_selection(args)
    except (EOFError, KeyboardInterrupt):
        print()
        return 130

    files = AGENT_FILES[(platform, variant)]
    dest_dir = target_dir(platform, scope)

    if not args.yes and not args.dry_run:
        try:
            if not confirm_plan(files, dest_dir):
                print("aborted")
                return 0
        except (EOFError, KeyboardInterrupt):
            print()
            return 130

    try:
        for f in files:
            install_one(f, dest_dir, args)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print()
        return 130

    print(f"done — {len(files)} file(s) in {dest_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
