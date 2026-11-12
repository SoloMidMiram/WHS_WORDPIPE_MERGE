#!/usr/bin/env python3
"""index.py - thin CLI wrapper; index logic lives in wordpipe.chronicle.index.

Kept for backward compatibility: ``python pipeline/index.py`` and
``from pipeline.index import <name>`` continue to work. New code should import
from wordpipe.chronicle.index.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import quote

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
    merged_survivor_anchors,
    prepare_index_targets,
    rendered_navigation,
    render_template,
    safe_write,
)

from wordpipe.chronicle.merge import validate_event_headings

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
    parser.add_argument("--merged", type=Path, help="Verify the tagged survivors against this merged Chronicle")
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
        "--dedup-method", choices=["survivor", "title", "date_title"],
        help="Index projection: survivor (default), title or date_title",
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

    try:
        generate_indices(Path(args.input), config, args.merged, args.source_coverage)
    except (OSError, ValueError) as exc:
        logging.error("Index generation failed: %s", exc)
        sys.exit(1)


def generate_indices(input_path: Path, config: dict, merged_path: Path | None,
                     source_coverage: str | None) -> None:
    tagged_md = input_path.read_text(encoding="utf-8")
    validate_event_headings(tagged_md)
    events = extract_events_from_tagged(tagged_md)
    if not events:
        raise ValueError("Tagged Chronicle contains no valid event headings")
    if merged_path is not None:
        expected = merged_survivor_anchors(merged_path.read_text(encoding="utf-8"))
        if [event["anchor"] for event in events] != expected:
            raise ValueError("Tagged events do not match the ordered merged survivor keys")
    target_md = prepare_index_targets(tagged_md, events)
    anchor_counts = Counter(rendered_navigation(target_md)[0])
    if any(anchor_counts[event["anchor"]] != 1 for event in events):
        raise ValueError("Tagged Chronicle must render exactly one target per survivor")

    output_dir = Path(config["output_dir"])
    target = input_path if target_md == tagged_md else output_dir / "chronicle_tagged_anchored.md"
    target_path = target.resolve() if target == input_path else output_dir.resolve() / target.name
    relative_path = os.path.relpath(target_path, output_dir.resolve())
    target_url = quote(Path(relative_path).as_posix(), safe="/")
    for event in events:
        event["target"] = target_url

    method = config["dedup_method"]
    if method != "survivor":
        before = len(events)
        events = deduplicate_events(events, method=method)
        logging.info("Explicit %s projection omitted %d survivor entries", method, before - len(events))

    event_context = build_event_index(events)
    theme_context = build_theme_index(events)
    contexts = {
        "event_index.md": event_context,
        "theme_index.md": theme_context,
        "source_manifest.md": build_source_manifest(
            events, Path(source_coverage) if source_coverage else None
        ),
    }
    if not config["no_link_registry"]:
        contexts["link_registry.md"] = build_link_registry(events)

    rendered = {
        name: render_template(name + ".j2", context, templates_dir=config["templates_dir"])
        for name, context in contexts.items()
    }
    for name, rows in (
        ("event_index.md", event_context["events"]),
        ("theme_index.md", [event for group in theme_context["themes"].values() for event in group]),
    ):
        expected_links = Counter(
            (f"{target_url}#{event['anchor']}", event["title"] or "Untitled event")
            for event in rows
        )
        actual_links = Counter(rendered_navigation(rendered[name])[1])
        if actual_links != expected_links:
            raise ValueError(f"{name} does not link to exactly the expected Chronicle events")

    outputs = {output_dir / name: content for name, content in rendered.items()}
    if target != input_path:
        outputs = {target: target_md, **outputs}
    protected = {input_path.resolve()}
    if merged_path is not None:
        protected.add(merged_path.resolve())
    if any(path.resolve() in protected for path in outputs):
        raise ValueError("An index output would overwrite a Chronicle input")

    for path, content in outputs.items():
        if not content.strip():
            raise ValueError(f"Empty index output: {path.name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        safe_write(path, content)
    for path, content in outputs.items():
        if path.read_text(encoding="utf-8") != content:
            raise ValueError(f"Index output was not written as validated: {path.name}")
    if target.read_text(encoding="utf-8") != target_md:
        raise ValueError("Chronicle navigation target changed during indexing")
    logging.info("Generated %d index artifacts for %d entries in %s", len(outputs), len(events), output_dir)


if __name__ == "__main__":
    main()
