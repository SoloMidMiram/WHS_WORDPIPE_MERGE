"""CLI wrapper for the chronicle merge stage.

Delegates to wordpipe.chronicle.merge for pure logic and handles
CLI argument parsing, I/O, and logging.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import yaml

from wordpipe.chronicle.merge import (
    collect_input_files,
    merge_files,
    write_duplicates_report,
    write_source_coverage,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge normalised chronicle .md files into a single deduplicated chronicle."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--inputs", "-i", nargs="+", metavar="FILE",
        help="List of normalised .md files",
    )
    group.add_argument(
        "--input-dir", "-d", metavar="DIR",
        help="Directory containing normalised .md files (all .md files will be used)",
    )
    parser.add_argument(
        "--output", "-o", default="merged.md",
        help="Output merged markdown (default: merged.md)",
    )
    parser.add_argument(
        "--conflict-mode",
        choices=["keep-both", "manual", "skip"],
        default="keep-both",
        help="How to handle events with same date but different content (default: keep-both)",
    )
    parser.add_argument(
        "--source-coverage", action="store_true",
        help="Also generate a source_coverage.md table",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # 1. Collect and validate input files
    files = collect_input_files(args.inputs, args.input_dir)
    logging.info("Processing %d file(s).", len(files))

    # 2. Perform merge
    merged_md, duplicates, source_contributions, source_names = merge_files(
        files, args.conflict_mode
    )

    # 3. Write merged output
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(merged_md, encoding="utf-8")
    # Count events from the front-matter (more reliable than counting ## Event: in body)
    _fm_start = merged_md.find("---") + 3
    _fm_end = merged_md.find("---", _fm_start)
    _fm_data = yaml.safe_load(merged_md[_fm_start:_fm_end].strip())
    _event_count = _fm_data.get("event_count", 0) if _fm_data else 0
    logging.info("Merged chronicle written to %s (%d events)", out_path, _event_count)

    # 4. Write duplicates report
    dup_path = out_path.with_suffix(".duplicates.json")
    write_duplicates_report(duplicates, dup_path)
    if duplicates:
        logging.info("%d duplicate/conflict entries recorded.", len(duplicates))
    else:
        logging.info("No duplicates or conflicts found.")

    # 5. Optionally write source coverage
    if args.source_coverage:
        coverage_path = out_path.with_suffix(".source_coverage.md")
        write_source_coverage(source_names, source_contributions, duplicates, coverage_path)


if __name__ == "__main__":
    main()
