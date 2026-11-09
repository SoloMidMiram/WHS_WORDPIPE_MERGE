"""Batch verification helpers for Chronicle ingest output."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

import yaml

DEFAULT_RAW_DIR = Path("inputs/chatgpt-chronicle/markdown")
DEFAULT_INGEST = Path("pipeline/ingest.py")


def parse_ingest_stderr(stderr: str) -> tuple[int, list[str]]:
    """Parse legacy or current ingest logs for callers of this compatibility helper."""
    event_count = 0
    warnings: list[str] = []
    for line in stderr.splitlines():
        match = re.search(r"\bExtracted (\d+) events(?:, \d+ rejected)?\.", line)
        if match:
            event_count = int(match[1])
        if "WARNING" in line or "warning" in line.lower():
            warnings.append(line.strip())
        if "ERROR" in line or "error" in line.lower():
            warnings.append(line.strip())
    return event_count, warnings


def _read_event_count(path: Path) -> int:
    """Read the accepted event count from normalized output front matter."""
    opening, _, rest = path.read_text(encoding="utf-8").partition("\n")
    header, closing, _ = rest.partition("\n---\n")
    if opening != "---" or not closing:
        raise ValueError("missing normalized front matter")
    metadata = yaml.safe_load(header)
    count = metadata.get("event_count") if isinstance(metadata, dict) else None
    if type(count) is not int or count < 0:
        raise ValueError("invalid normalized event_count")
    return count


def classify_file_result(
    returncode: int,
    event_count: int,
    warnings: list[str],
) -> tuple[str, str | None]:
    """Classify a single file's ingest result."""
    if returncode != 0:
        return "[ERROR]", "exit code != 0"
    if event_count == 0:
        if not any("No dates" in warning for warning in warnings):
            return "[ZERO]", "0 events (narrative file?)"
        return "[ZERO]", None
    return "[OK]", None


def verify_directory(raw_dir: Path, ingest_script: Path, *, verbose: bool = False) -> int:
    """Run an ingest script against every markdown file in ``raw_dir``.

    Returns a process-style exit code: ``0`` when all files process without
    hard errors or unexpected zero-event files, ``1`` otherwise.
    """
    if not raw_dir.is_dir():
        print(f"ERROR: Raw directory not found: {raw_dir}")
        return 1
    if not ingest_script.is_file():
        print(f"ERROR: ingest.py not found: {ingest_script}")
        return 1

    md_files = sorted(raw_dir.glob("*.md"))
    if not md_files:
        print(f"WARNING: No .md files found in {raw_dir}")
        return 0

    print(f"{'File':<75} {'Events':<8} {'Warnings':<30} {'Status':<10}")
    print("-" * 125)

    exit_code = 0
    total_events = 0
    files_with_issues: list[tuple[str, str]] = []
    tmp_dir = Path(tempfile.mkdtemp(prefix="verify_ingest_"))

    try:
        for md_file in md_files:
            out_path = tmp_dir / md_file.name
            result = subprocess.run(
                [sys.executable, "-X", "utf8", str(ingest_script), "--input", str(md_file), "--output", str(out_path)],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            warnings = [
                line.strip()
                for stream in (result.stdout, result.stderr)
                for line in stream.splitlines()
                if line.lstrip().startswith(("WARNING:", "ERROR:"))
            ]
            event_count = 0
            try:
                if result.returncode == 0:
                    event_count = _read_event_count(out_path)
            except (OSError, ValueError, yaml.YAMLError) as exc:
                status, issue_reason = "[ERROR]", f"invalid normalized output: {exc}"
            else:
                status, issue_reason = classify_file_result(result.returncode, event_count, warnings)
            total_events += event_count
            if issue_reason is not None:
                exit_code = 1
                files_with_issues.append((md_file.name, issue_reason))

            warn_str = "; ".join(warnings[:2]) if warnings else ""
            if verbose or status != "[OK]":
                print(f"{md_file.name:<75} {event_count:<8} {warn_str:<30} {status:<10}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("-" * 125)
    print(f"\nTotal files: {len(md_files)}")
    print(f"Total events extracted: {total_events}")
    print(f"Files with issues: {len(files_with_issues)}")

    if files_with_issues:
        print("\nFiles requiring attention:")
        for name, reason in files_with_issues:
            print(f"  - {name}: {reason}")

    if exit_code != 0:
        print("\n[FAIL] Verification FAILED -- some files produced errors.")
    else:
        print("\n[PASS] Verification PASSED -- all files processed without errors.")
    return exit_code


verify_ingest = verify_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify ingest.py against all raw .md files.")
    parser.add_argument(
        "--dir",
        default=str(DEFAULT_RAW_DIR),
        help=f"Directory containing raw .md files (default: {DEFAULT_RAW_DIR})",
    )
    parser.add_argument(
        "--ingest",
        default=str(DEFAULT_INGEST),
        help=f"Path to ingest.py (default: {DEFAULT_INGEST})",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Show per-file details")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return verify_directory(Path(args.dir), Path(args.ingest), verbose=args.verbose)
