#!/usr/bin/env python3
"""Validate the repository-root allowlist documented in ROOT_ORGANIZATION.md."""

from __future__ import annotations

import argparse
from pathlib import Path


ALLOWED_FILES = {
    ".env.example",
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "ARCHITECTURE_AND_MODULES.md",
    "INDEX.md",
    "JOURNAL.md",
    "ONTOLOGY_MODEL.md",
    "PLAN.md",
    "README.md",
    "REPO_ORGANIZATION_PLAN.md",
    "ROADMAP.md",
    "ROOT_ORGANIZATION.md",
    "VERIFICATION.md",
    "WORKSPACE_OVERVIEW.md",
    "ontology.json",
    "pyproject.toml",
}

ALLOWED_DIRECTORIES = {
    ".agents",
    ".codex",
    ".continue",
    ".cursor",
    ".git",
    ".github",
    "_ARCHIVE",
    "_INBOX",
    "_META",
    "_SECURITY",
    "_WORK",
    "docs",
    "inputs",
    "pipeline",
    "scripts",
    "tests",
    "tools",
    "WordHorrorStories",
    "wordpipe",
}

IGNORED_GENERATED_DIRECTORIES = {".pytest_cache", ".ruff_cache"}


def is_linked_worktree_pointer(entry: Path) -> bool:
    """Accept only a reciprocally linked Git worktree administrative record.

    Do not execute Git or accept an arbitrary gitdir directive (e.g. submodules).
    Both directions and the shared repository structure must exist.
    """
    if entry.name != ".git" or entry.is_symlink():
        return False
    try:
        lines = entry.read_text(encoding="utf-8").splitlines()
        if len(lines) != 1 or not lines[0].startswith("gitdir: "):
            return False
        target = lines[0][8:]
        if not target:
            return False
        admin = (entry.parent / target).resolve(strict=True)
        common_text = (admin / "commondir").read_text(encoding="utf-8").splitlines()
        back_text = (admin / "gitdir").read_text(encoding="utf-8").splitlines()
        if len(common_text) != 1 or not common_text[0] or len(back_text) != 1 or not back_text[0]:
            return False
        common = (admin / common_text[0]).resolve(strict=True)
        back = (admin / back_text[0]).resolve(strict=True)
        return (
            back == entry.resolve(strict=True)
            and admin.parent == common / "worktrees"
            and (admin / "HEAD").is_file()
            and (common / "HEAD").is_file()
            and (common / "objects").is_dir()
            and (common / "refs").is_dir()
        )
    except (OSError, UnicodeError, ValueError, RuntimeError):
        return False


def find_violations(root: Path) -> list[str]:
    violations: list[str] = []
    for entry in root.iterdir():
        if entry.is_file() and entry.name not in ALLOWED_FILES:
            if is_linked_worktree_pointer(entry):
                continue
            violations.append(entry.name)
        elif entry.is_dir():
            if entry.name in ALLOWED_DIRECTORIES or entry.name in IGNORED_GENERATED_DIRECTORIES:
                continue
            if entry.name.endswith(".egg-info"):
                continue
            violations.append(f"{entry.name}/")
    return sorted(violations, key=str.casefold)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    violations = find_violations(args.root.resolve())
    if violations:
        print("root_layout: FAIL")
        for violation in violations:
            print(f"- {violation}")
        return 1
    print("root_layout: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
