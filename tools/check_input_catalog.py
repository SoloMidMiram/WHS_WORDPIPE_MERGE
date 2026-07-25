#!/usr/bin/env python3
"""Validate canonical corpus inputs against their provenance catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any


FORMAT_EXTENSIONS = {"markdown": ".md", "docx": ".docx"}
CLASSIFICATIONS = {"source", "exact_duplicate", "derived_input"}
LEGACY_INPUT_DIRS = (
    Path("WordHorrorStories/chatgpt-chronicle/sources/raw/chatgpt_mds"),
    Path("WordHorrorStories/insurancechatbot/input"),
)


def _normalized_content(path: Path) -> bytes:
    """Read file and normalize CRLF to LF for consistent hashing."""
    raw = path.read_bytes()
    return raw.replace(b"\r\n", b"\n")


def _catalog_entries(catalog: Any) -> list[dict[str, Any]]:
    sv = catalog.get("schema_version")
    if sv == 1:
        # v1: hash_mode is implicitly "lf_normalized_utf8" (CRLF was normalized
        # before hashing). Accept without requiring an explicit field.
        pass
    elif sv == 2:
        hm = catalog.get("hash_mode")
        if hm is None:
            raise ValueError("catalog v2 requires 'hash_mode' field")
        expected = "lf_normalized_utf8"
        if hm != expected:
            raise ValueError(
                f"catalog v2 hash_mode must be {expected!r}, got {hm!r}"
            )
    else:
        raise ValueError(
            f"catalog schema_version must be 1 or 2, got {sv!r}"
        )
    entries = catalog.get("entries")
    if not isinstance(entries, list):
        raise ValueError("catalog.entries must be a list")
    return entries


def find_violations(root: Path, catalog_path: Path | None = None) -> list[str]:
    root = root.resolve()
    catalog_path = catalog_path or root / "inputs" / "catalog.json"
    violations: list[str] = []
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        entries = _catalog_entries(catalog)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"catalog: {exc}"]

    by_path: dict[str, dict[str, Any]] = {}
    hashes: dict[str, list[dict[str, Any]]] = {}
    for index, entry in enumerate(entries):
        prefix = f"entries[{index}]"
        if not isinstance(entry, dict):
            violations.append(f"{prefix}: must be an object")
            continue
        rel = entry.get("path")
        if not isinstance(rel, str) or "\\" in rel:
            violations.append(f"{prefix}.path: must use portable forward slashes")
            continue
        pure = PurePosixPath(rel)
        parts = pure.parts
        if pure.is_absolute() or ".." in parts or len(parts) != 4 or parts[0] != "inputs":
            violations.append(
                f"{prefix}.path: expected inputs/<corpus>/<format>/<top-level-file>"
            )
            continue
        corpus, file_format, filename = parts[1], parts[2], parts[3]
        expected_ext = FORMAT_EXTENSIONS.get(file_format)
        if expected_ext is None or PurePosixPath(filename).suffix.lower() != expected_ext:
            violations.append(f"{prefix}.path: extension does not match format {file_format!r}")
        if entry.get("corpus") != corpus or entry.get("format") != file_format:
            violations.append(f"{prefix}: corpus/format must match path")
        if rel in by_path:
            violations.append(f"{prefix}.path: duplicate catalog path {rel}")
            continue
        by_path[rel] = entry

        classification = entry.get("classification")
        if classification not in CLASSIFICATIONS:
            violations.append(f"{prefix}.classification: unsupported value {classification!r}")
        expected_hash = entry.get("sha256")
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            violations.append(f"{prefix}.sha256: expected a 64-character digest")
            continue
        hashes.setdefault(expected_hash, []).append(entry)

        path = root / PurePosixPath(rel)
        if not path.is_file():
            violations.append(f"{rel}: missing input")
            continue
        norm = _normalized_content(path)
        if len(norm) != entry.get("size_bytes"):
            violations.append(f"{rel}: size differs from catalog")
        if hashlib.sha256(norm).hexdigest() != expected_hash:
            violations.append(f"{rel}: SHA-256 differs from catalog")

    for digest, same_hash in hashes.items():
        if len(same_hash) < 2:
            continue
        primary_paths = {item["path"] for item in same_hash if item.get("classification") != "exact_duplicate"}
        for item in same_hash:
            if item.get("classification") == "exact_duplicate":
                target = item.get("duplicate_of")
                if target not in primary_paths:
                    violations.append(
                        f"{item['path']}: duplicate_of must name a same-hash primary input"
                    )
            elif len(primary_paths) > 1:
                violations.append(f"{item['path']}: duplicate content is not classified")

    discovered = {
        path.relative_to(root).as_posix()
        for path in (root / "inputs").rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".docx"}
        and path.name != "README.md"
    }
    for rel in sorted(discovered - set(by_path), key=str.casefold):
        violations.append(f"{rel}: unlisted input")
    for rel in sorted(set(by_path) - discovered, key=str.casefold):
        if not (root / PurePosixPath(rel)).is_file():
            continue
        violations.append(f"{rel}: cataloged file is outside discoverable input layout")

    for legacy in LEGACY_INPUT_DIRS:
        legacy_path = root / legacy
        if legacy_path.exists():
            violations.append(f"{legacy.as_posix()}: legacy input location must not recur")

    return sorted(set(violations), key=str.casefold)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--catalog", type=Path, default=None)
    args = parser.parse_args()
    violations = find_violations(args.root, args.catalog)
    if violations:
        print("input_catalog: FAIL")
        for violation in violations:
            print(f"- {violation}")
        return 1
    print("input_catalog: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
