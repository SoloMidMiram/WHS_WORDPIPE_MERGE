"""CLI wrapper for the chronicle ingest stage.

Delegates to wordpipe.chronicle.ingest for pure logic and handles
CLI argument parsing, I/O, and logging.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import dateutil.parser

from wordpipe.chronicle.ingest import (
    clean_mojibake,
    extract_preamble,
    extract_source_name,
    extract_title,
    generate_normalised_md,
    parse_date_range,
    split_into_events,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalise a raw deep-search MD file for the chronicle pipeline."
    )
    parser.add_argument("--input", "-i", required=True, help="Path to raw .md file")
    parser.add_argument(
        "--output", "-o", help="Path for normalised output (default: <stem>_normalised.md)"
    )
    parser.add_argument(
        "--source-name", help="Override source name (otherwise derived from filename)"
    )
    parser.add_argument(
        "--date-override",
        help="Force a date (YYYY-MM-DD or YYYY-MM) when file has no parseable dates",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    input_path = Path(args.input)
    if not input_path.exists():
        logging.error("Input file not found: %s", input_path)
        sys.exit(1)
    raw_text = input_path.read_text(encoding="utf-8")

    cleaned_text = clean_mojibake(raw_text)
    source = extract_source_name(input_path, args.source_name)
    title = extract_title(cleaned_text, source)

    date_start, date_end = parse_date_range(cleaned_text)
    if date_start is None:
        if args.date_override:
            try:
                forced_dt = dateutil.parser.parse(
                    args.date_override, fuzzy=True, default=datetime(2025, 1, 1)
                )
                if forced_dt.year < 2022 or forced_dt.year > 2027:
                    logging.warning(
                        "Override date year %d seems out of range; using anyway.",
                        forced_dt.year,
                    )
                date_start = date_end = forced_dt
                logging.info("Date overridden to %s", forced_dt.strftime("%Y-%m-%d"))
            except (ValueError, OverflowError) as e:
                logging.error(
                    "Cannot parse --date-override value '%s': %s", args.date_override, e
                )
                sys.exit(1)
        else:
            logging.warning("No dates found in content; date will be 'unknown'.")

    events = split_into_events(cleaned_text)
    logging.info("Extracted %d events.", len(events))

    preamble = extract_preamble(cleaned_text, events)

    normalised_md = generate_normalised_md(
        source=source,
        title=title,
        date_range=(date_start, date_end),
        events=events,
        input_file=str(input_path),
        preamble=preamble,
    )

    if args.output:
        out_path = Path(args.output)
    else:
        out_stem = input_path.stem + "_normalised"
        out_path = input_path.with_name(out_stem + ".md")
    out_path.write_text(normalised_md, encoding="utf-8")
    logging.info("Normalised file written to %s", out_path)


if __name__ == "__main__":
    main()
