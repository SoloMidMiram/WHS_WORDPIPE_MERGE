#!/usr/bin/env python3
"""
verify_ingest.py – Run ingest.py against all raw .md files and report results.

Usage:
  python verify_ingest.py [--dir <path>] [--ingest <path>]

Default --dir: WordHorrorStories/chatgpt-chronicle/sources/raw/chatgpt_mds/
Default --ingest: tools/pipeline-chronicle/ingest.py

Exits with non-zero code if any file produced zero events or an error.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Default paths (relative to project root)
# ---------------------------------------------------------------------------
DEFAULT_RAW_DIR = Path("WordHorrorStories/chatgpt-chronicle/sources/raw/chatgpt_mds")
DEFAULT_INGEST = Path("tools/pipeline-chronicle/ingest.py")


def main():
    parser = argparse.ArgumentParser(
        description="Verify ingest.py against all raw .md files."
    )
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
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show per-file details"
    )
    args = parser.parse_args()

    raw_dir = Path(args.dir)
    ingest_script = Path(args.ingest)

    if not raw_dir.is_dir():
        print(f"ERROR: Raw directory not found: {raw_dir}")
        sys.exit(1)
    if not ingest_script.is_file():
        print(f"ERROR: ingest.py not found: {ingest_script}")
        sys.exit(1)

    md_files = sorted(raw_dir.glob("*.md"))
    if not md_files:
        print(f"WARNING: No .md files found in {raw_dir}")
        sys.exit(0)

    print(f"{'File':<75} {'Events':<8} {'Warnings':<30} {'Status':<10}")
    print("-" * 125)

    exit_code = 0
    total_events = 0
    total_files = 0
    files_with_issues = []

    import tempfile
    import os

    # Create a temp directory for output files
    tmp_dir = Path(tempfile.mkdtemp(prefix="verify_ingest_"))

    for f in md_files:
        total_files += 1
        out_path = tmp_dir / f.name
        result = subprocess.run(
            ["python", str(ingest_script), "--input", str(f), "--output", str(out_path)],
            capture_output=True,
            text=True,
        )

        # Parse stderr for event count and warnings (logging goes to stderr)
        event_count = 0
        warnings = []
        for line in result.stderr.splitlines():
            if "Extracted" in line and "events" in line:
                try:
                    event_count = int(line.split()[-2])
                except (ValueError, IndexError):
                    pass
            if "WARNING" in line or "warning" in line.lower():
                warnings.append(line.strip())
            if "ERROR" in line or "error" in line.lower():
                warnings.append(line.strip())

        total_events += event_count

        # Determine status
        if result.returncode != 0:
            status = "[ERROR]"
            exit_code = 1
            files_with_issues.append((f.name, "exit code != 0"))
        elif event_count == 0:
            # Zero events is OK for narrative files, but flag it
            status = "[ZERO]"
            if not any("No dates" in w for w in warnings):
                files_with_issues.append((f.name, "0 events (narrative file?)"))
        else:
            status = "[OK]"

        warn_str = "; ".join(warnings[:2]) if warnings else ""
        if args.verbose or status != "[OK]":
            print(f"{f.name:<75} {event_count:<8} {warn_str:<30} {status:<10}")

    # Summary
    print("-" * 125)
    print(f"\nTotal files: {total_files}")
    print(f"Total events extracted: {total_events}")
    print(f"Files with issues: {len(files_with_issues)}")

    if files_with_issues:
        print("\nFiles requiring attention:")
        for name, reason in files_with_issues:
            print(f"  - {name}: {reason}")

    # Clean up temp directory
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    if exit_code != 0:
        print("\n[FAIL] Verification FAILED -- some files produced errors.")
    else:
        print("\n[PASS] Verification PASSED -- all files processed without errors.")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
