"""High-confidence secret scanner for local repository checks."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone

PATTERNS: dict[str, re.Pattern[str]] = {
    "openai_sk": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "openai_legacy_k": re.compile(r"\bk-[A-Za-z0-9]{20,}\b"),
    "github_pat": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "github_token": re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    "aws_access_key_id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
}

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
}


def parse_extensions(value: str) -> set[str]:
    exts = set()
    for raw in value.split(","):
        ext = raw.strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        exts.add(ext)
    return exts


def mask_secret(text: str) -> str:
    stripped = text.strip()
    if len(stripped) <= 12:
        return "<REDACTED>"
    return f"{stripped[:4]}...{stripped[-4:]}"


def is_probably_binary(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(2048)
        return b"\x00" in chunk
    except OSError:
        return True


def iter_text_files(root: str, extensions: set[str]):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = os.path.join(base, name)
            _, ext = os.path.splitext(name.lower())
            if ext not in extensions:
                continue
            if is_probably_binary(path):
                continue
            yield path


def scan_file(path: str) -> list[dict]:
    findings: list[dict] = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line_no, line in enumerate(f, 1):
                for rule_name, pattern in PATTERNS.items():
                    for match in pattern.finditer(line):
                        findings.append(
                            {
                                "path": os.path.relpath(path).replace("\\", "/"),
                                "line": line_no,
                                "rule": rule_name,
                                "match": mask_secret(match.group(0)),
                            }
                        )
    except OSError:
        return findings
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--json-out",
        default="_SECURITY/scan_reports/secret_scan_latest.json",
        help="Write findings to JSON report path.",
    )
    parser.add_argument(
        "--extensions",
        default=".py,.md,.json,.log,.txt,.yaml,.yml,.env,.ini,.cfg,.toml",
        help="Comma-separated file extensions to scan.",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit with non-zero status if any findings are present.",
    )
    args = parser.parse_args()

    root_abs = os.path.abspath(args.root)
    exts = parse_extensions(args.extensions)

    findings: list[dict] = []
    file_count = 0
    for path in iter_text_files(root_abs, exts):
        file_count += 1
        findings.extend(scan_file(path))

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": root_abs,
        "scanned_files": file_count,
        "findings_count": len(findings),
        "findings": findings,
    }

    out_abs = os.path.abspath(args.json_out)
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    with open(out_abs, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"scanned_files: {file_count}")
    print(f"findings_count: {len(findings)}")
    print(f"report: {out_abs}")
    for finding in findings[:20]:
        print(
            f"{finding['path']}:{finding['line']} "
            f"{finding['rule']} {finding['match']}"
        )

    if args.fail_on_findings and findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
