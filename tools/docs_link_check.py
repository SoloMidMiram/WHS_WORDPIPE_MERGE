"""Validate internal documentation references.

Scans markdown files for `docs/<...>.md` references and verifies that each
referenced path exists on disk. This is intended as a lightweight pre-commit
check for the docs pack.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DOC_REF_RE = re.compile(r"docs/[A-Za-z0-9_./-]+\.md")


def iter_scan_files(repo_root: Path) -> list[Path]:
    docs_root = repo_root / "docs"
    files: list[Path] = []
    if docs_root.is_dir():
        files.extend(sorted(docs_root.rglob("*.md")))
    for p in [repo_root / "WORKSPACE_OVERVIEW.md", repo_root / "tools" / "README_tools.md"]:
        if p.is_file():
            files.append(p)
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root (defaults to parent of tools/).",
    )
    args = parser.parse_args()

    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        repo_root = Path(__file__).resolve().parents[1]

    scan_files = iter_scan_files(repo_root)
    refs: set[str] = set()
    for p in scan_files:
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Some evidence docs may not be UTF-8; skip to avoid false failures.
            continue
        refs.update(DOC_REF_RE.findall(text))

    missing: list[str] = []
    for ref in sorted(refs):
        if not (repo_root / ref).is_file():
            missing.append(ref)

    print(f"scanned_files: {len(scan_files)}")
    print(f"doc_refs_found: {len(refs)}")
    if missing:
        print("missing_docs:")
        for m in missing:
            print(f"- {m}")
        return 2
    print("ok: all referenced docs/*.md paths exist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

