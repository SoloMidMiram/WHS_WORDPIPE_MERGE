"""CLI wrapper for the chronicle categorize stage.

Delegates to wordpipe.chronicle.categorize for pure logic and handles
CLI argument parsing, I/O, and logging.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from wordpipe.chronicle.categorize import (
    _load_negative_keywords,
    build_sidecar_json,
    extract_events,
    load_themes,
    match_themes,
    rebuild_tagged_md,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tag events in a normalised/merged chronicle with theme labels."
    )
    parser.add_argument("--input", "-i", required=True, help="Path to input .md file")
    parser.add_argument("--config", "-c", help="JSON or YAML config with themes (optional)")
    parser.add_argument("--output", "-o", help="Path for tagged output (default: <input>_tagged.md)")
    parser.add_argument("--sidecar", action="store_true", help="Write sidecar JSON")
    parser.add_argument("--dry-run", action="store_true", help="Preview tagging without writing")
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
    original_text = input_path.read_text(encoding="utf-8")

    config_path = Path(args.config) if args.config else None
    themes = load_themes(config_path)
    neg_keywords = _load_negative_keywords(config_path)
    logging.info("Loaded %d themes.", len(themes))

    body_start = 0
    if original_text.startswith("---"):
        parts = original_text.split("---", 2)
        if len(parts) >= 3:
            body_start = original_text.index(parts[2])
    body = original_text[body_start:]

    events = extract_events(body)
    if not events:
        logging.warning("No events found. Output will be unchanged.")
        if not args.dry_run:
            out_path = Path(args.output) if args.output else input_path.with_name(input_path.stem + "_tagged.md")
            out_path.write_text(original_text, encoding="utf-8")
        return

    for ev in events:
        ev["themes"] = match_themes(ev["body"], themes, neg_keywords)

    tagged_md = rebuild_tagged_md(original_text, events)

    tagged_count = sum(1 for ev in events if ev["themes"])
    logging.info("%d/%d events received theme tags.", tagged_count, len(events))

    if args.dry_run:
        logging.info("DRY RUN -- no files written.")
        if args.verbose:
            for ev in events:
                if ev["themes"]:
                    logging.debug("  %s -> %s", ev["date"], ", ".join(ev["themes"]))
        return

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = input_path.with_name(input_path.stem + "_tagged.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(tagged_md, encoding="utf-8")
    logging.info("Tagged output written to %s", out_path)

    if args.sidecar:
        sidecar_path = out_path.with_suffix(".tagged.json")
        sidecar_data = build_sidecar_json(events)
        with open(sidecar_path, "w", encoding="utf-8") as f:
            json.dump(sidecar_data, f, indent=2, ensure_ascii=False)
        logging.info("Sidecar JSON written to %s", sidecar_path)


if __name__ == "__main__":
    main()
