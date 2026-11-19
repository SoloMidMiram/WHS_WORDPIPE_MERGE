#!/usr/bin/env python3
"""Read-only, bounded Git context retrieval; no network or AI dependencies."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess


SCOPES = {
    "tools": ["tools/"],
    "tests": ["tests/"],
    "runtime": ["wordpipe/", ":(exclude)wordpipe/legacy/", ":(exclude)wordpipe/ai/"],
    "pipeline": ["pipeline/"],
    "docs": ["docs/"],
    "governance": ["AGENTS.md", "ROADMAP.md", "INDEX.md", "ROOT_ORGANIZATION.md",
                   "ARCHITECTURE_AND_MODULES.md", "pyproject.toml", ".github/workflows/"],
}


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], encoding="utf-8")


def snapshot(root: Path) -> dict:
    dirt = git(root, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
    branch = git(root, "branch", "--show-current").strip()
    return {
        "classification": "verified local snapshot; remote state unverified",
        "branch": branch or "DETACHED",
        "head": git(root, "rev-parse", "HEAD").strip(),
        "dirty_entries": len(dirt),
        "dirty_preview": dirt[:12],
        "dirty_preview_truncated": len(dirt) > 12,
        "next": "Read docs/engineering/REPO_MAP.md and newest relevant ROADMAP entry; then find keywords.",
    }


def find(root: Path, keywords: list[str], scopes: list[str], limit: int) -> dict:
    args = ["git", "-C", str(root), "--no-pager", "grep", "--no-color", "-n", "-I", "-i", "-F"]
    for keyword in keywords:
        args += ["-e", keyword]
    args += ["--", *[path for scope in scopes for path in SCOPES[scope]]]
    matches = []
    truncated = False
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          encoding="utf-8", errors="replace") as proc:
        assert proc.stdout is not None
        for line in proc.stdout:
            if len(matches) == limit:
                truncated = True
                proc.terminate()
                break
            line = line.rstrip("\r\n")
            matches.append(line[:240] + (" ... [line truncated]" if len(line) > 240 else ""))
        _, error = proc.communicate()
        if not truncated and proc.returncode not in (0, 1):
            raise RuntimeError(error.strip())
    return {"engine": "git grep literal, case-insensitive, tracked text only",
            "scopes": scopes, "matches": matches, "truncated": truncated,
            "interpretation": "Locators only; inspect enclosing contracts. No match is limited to these scopes."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("snapshot")
    search = commands.add_parser("find")
    search.add_argument("keywords", nargs="+")
    search.add_argument("--scope", choices=SCOPES, action="append")
    search.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == "find" and (not 1 <= args.limit <= 100 or any(not k.strip() for k in args.keywords)):
        parser.error("Use nonblank keywords and --limit between 1 and 100")
    try:
        actual = Path(git(root, "rev-parse", "--show-toplevel").strip()).resolve()
        if actual != root:
            parser.error("--root must be the Git checkout root")
        result = snapshot(root) if args.command == "snapshot" else find(
            root, args.keywords, args.scope or list(SCOPES), args.limit)
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        parser.exit(1, f"context retrieval failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
