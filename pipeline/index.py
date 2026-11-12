#!/usr/bin/env python3
"""index.py - thin CLI wrapper; index logic lives in wordpipe.chronicle.index.

Kept for backward compatibility: ``python pipeline/index.py`` and
``from pipeline.index import <name>`` continue to work. New code should import
from wordpipe.chronicle.index.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from wordpipe.chronicle.index import (
    DEFAULT_CONFIG,
    EVENT_HEADING_RE,
    HAS_JINJA2,
    SOURCE_LINE_RE,
    THEME_COMMENT_RE,
    URL_RE,
    _fallback_render,
    _render_event_index_fallback,
    _render_link_registry_fallback,
    _render_source_manifest_fallback,
    _render_theme_index_fallback,
    build_event_index,
    build_link_registry,
    build_source_manifest,
    build_theme_index,
    deduplicate_events,
    extract_events_from_tagged,
    load_config,
    render_template,
    safe_write,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate appendix files from tagged chronicle markdown.",
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to tagged .md file (output of categorize.py)",
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Directory for generated appendix files (default: appendix/)",
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to index_config.json (optional; uses defaults if omitted)",
    )
    parser.add_argument(
        "--templates-dir", "-t",
        help="Directory containing Jinja2 templates (default: pipeline/templates)",
    )
    parser.add_argument("--strict-config", action="store_true",
                        help="Fail if the supplied index configuration is invalid")
    parser.add_argument(
        "--source-coverage", "-s",
        help="Path to source_coverage.md from merge.py (optional; extracts from inline annotations if omitted)",
    )
    parser.add_argument(
        "--no-link-registry", action="store_true",
        help="Skip link registry generation",
    )
    parser.add_argument(
        "--theme-sort", choices=["name", "count"],
        help="Sort themes by name (default) or by event count",
    )
    parser.add_argument(
        "--dedup-method", choices=["title", "date_title"],
        help="Deduplication method: 'title' or 'date_title' (default)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 1. Load config
    config_path = Path(args.config) if args.config else None
    try:
        config = load_config(config_path, strict=args.strict_config)
    except ValueError as exc:
        parser.error(str(exc))

    # Override config with CLI flags
    if args.output_dir:
        config["output_dir"] = args.output_dir
    if args.templates_dir:
        config["templates_dir"] = args.templates_dir
    if args.no_link_registry:
        config["no_link_registry"] = True
    if args.theme_sort:
        config["theme_sort"] = args.theme_sort
    if args.dedup_method:
        config["dedup_method"] = args.dedup_method

    # 2. Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        logging.error("Input file not found: %s", input_path)
        sys.exit(1)

    tagged_md = input_path.read_text(encoding="utf-8")

    # Validate that input looks like tagged markdown
    if "## Event:" not in tagged_md:
        logging.error(
            "Input file '%s' does not contain any ## Event: headings. "
            "Is this a tagged chronicle markdown file?",
            input_path,
        )
        sys.exit(1)

    # 3. Extract and deduplicate events
    events = extract_events_from_tagged(tagged_md)
    if not events:
        logging.warning("No events found in input. Output will be empty.")
        events = []

    events = deduplicate_events(events, method=config["dedup_method"])

    logging.info("Extracted %d unique events from %s.", len(events), input_path)

    # 4. Build output directory
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    # 5. Generate indices
    generated = []

    # 5a. Event index
    event_context = build_event_index(events)
    event_md = render_template(
        "event_index.md.j2",
        event_context,
        templates_dir=config["templates_dir"],
    )
    event_path = output_dir / "event_index.md"
    safe_write(event_path, event_md)
    generated.append(event_path)
    logging.info("Event index written to %s", event_path)

    # 5b. Theme index
    theme_context = build_theme_index(events)
    theme_md = render_template(
        "theme_index.md.j2",
        theme_context,
        templates_dir=config["templates_dir"],
    )
    theme_path = output_dir / "theme_index.md"
    safe_write(theme_path, theme_md)
    generated.append(theme_path)
    logging.info("Theme index written to %s", theme_path)

    # 5c. Source manifest
    source_coverage_path = Path(args.source_coverage) if args.source_coverage else None
    manifest_context = build_source_manifest(events, source_coverage_path)
    manifest_md = render_template(
        "source_manifest.md.j2",
        manifest_context,
        templates_dir=config["templates_dir"],
    )
    manifest_path = output_dir / "source_manifest.md"
    safe_write(manifest_path, manifest_md)
    generated.append(manifest_path)
    logging.info("Source manifest written to %s", manifest_path)

    # 5d. Link registry (optional)
    if not config["no_link_registry"]:
        link_context = build_link_registry(events)
        link_md = render_template(
            "link_registry.md.j2",
            link_context,
            templates_dir=config["templates_dir"],
        )
        link_path = output_dir / "link_registry.md"
        safe_write(link_path, link_md)
        generated.append(link_path)
        logging.info(
            "Link registry written to %s (%d unique links)",
            link_path,
            sum(len(v) for v in link_context["links"].values()),
        )
    else:
        logging.info("Link registry skipped (--no-link-registry).")

    # 6. Summary
    logging.info("Generated %d appendix files in %s:", len(generated), output_dir)
    for g in generated:
        size = g.stat().st_size
        logging.info("  %s (%d bytes)", g.name, size)


if __name__ == "__main__":
    main()
