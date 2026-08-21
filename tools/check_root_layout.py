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

IGNORED_GENERATED_DIRECTORIES = {".pytest_cache"}


def find_violations(root: Path) -> list[str]:
    violations: list[str] = []
    for entry in root.iterdir():
        if entry.is_file() and entry.name not in ALLOWED_FILES:
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
