#!/usr/bin/env python3
"""
Chronicle appendix-index generation.

Reads tagged chronicle markdown (output of categorize) and builds the pure
context/render logic for up to four appendix files:
  - event_index.md      - Events sorted by date with themes
  - theme_index.md      - Events grouped by theme
  - source_manifest.md  - Source contribution summary
  - link_registry.md    - All external URLs, deduplicated, sorted by domain

Uses Jinja2 templates if available; falls back to basic string formatting.

The CLI entrypoint lives in ``pipeline/index.py`` (thin wrapper).
"""


import html
import json
import logging
import re
import tempfile
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from wordpipe.chronicle.merge import (
    compute_body_hash,
    extract_events,
    parse_yaml_frontmatter,
    strip_keep_both_conflict_notes,
    validate_event_headings,
)

# ------------------------------------------------------------------------------
# Jinja2 availability check
# ------------------------------------------------------------------------------
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------
EVENT_HEADING_RE = re.compile(
    r"^(## Event:\s*\d{4}-\d{2}-\d{2}(?:\s*[–-]\s*.*?)?)\s*$",
    re.MULTILINE,
)
THEME_COMMENT_RE = re.compile(r"<!--\s*themes:\s*(.*?)\s*-->")
SURVIVOR_FRAGMENT_RE = re.compile(r"event-\d{4}-\d{2}-\d{2}-[0-9a-f]{64}")
EVENT_ANCHOR_RE = re.compile(rf'<a id="({SURVIVOR_FRAGMENT_RE.pattern})"></a>')
LEADING_THEME_RE = re.compile(r"\s*" + THEME_COMMENT_RE.pattern)
URL_RE = re.compile(r"https?://[^\s\)\]>\"'<>]+")
SOURCE_LINE_RE = re.compile(r"^#\s*Source:\s*(.+)$", re.MULTILINE)

# Default config values
DEFAULT_CONFIG: Dict[str, Any] = {
    "output_dir": "appendix",
    "templates_dir": "pipeline/templates",
    "dedup_method": "survivor",
    "theme_sort": "name",
    "no_link_registry": False,
    "event_snippet_max_chars": 200,
}


# ------------------------------------------------------------------------------
# Config loading
# ------------------------------------------------------------------------------
def load_config(config_path: Optional[Path], *, strict: bool = False) -> Dict[str, Any]:
    """
    Load index configuration from JSON file.

    Invalid files fall back to defaults unless strict mode is enabled.
    Omitting the file always uses defaults.
    """
    if config_path is None:
        return dict(DEFAULT_CONFIG)

    try:
        with open(config_path, encoding="utf-8") as f:
            user_config = json.load(f)
        if not isinstance(user_config, dict):
            raise ValueError("expected a JSON object")
        config = dict(DEFAULT_CONFIG)
        for key, value in user_config.items():
            if key == "_comment":
                if strict and not isinstance(value, str):
                    raise ValueError("_comment must be str")
                continue
            if key not in DEFAULT_CONFIG:
                if strict:
                    raise ValueError(f"unknown setting {key!r}")
                continue
            if type(value) is not type(DEFAULT_CONFIG[key]):
                raise ValueError(f"{key} must be {type(DEFAULT_CONFIG[key]).__name__}")
            if key in ("output_dir", "templates_dir") and (not value.strip() or "\x00" in value):
                raise ValueError(f"{key} must be a nonempty path")
            if key == "event_snippet_max_chars" and value < 0:
                raise ValueError(f"{key} must be nonnegative")
            if key == "dedup_method" and value not in ("survivor", "title", "date_title"):
                raise ValueError(f"{key} must be survivor, title or date_title")
            if key == "theme_sort" and value not in ("name", "count"):
                raise ValueError(f"{key} must be name or count")
            config[key] = value
    except (OSError, ValueError) as e:
        if strict:
            raise ValueError(f"Invalid index config {config_path}: {e}") from e
        logging.warning("Invalid index config %s: %s; using defaults.", config_path, e)
        return dict(DEFAULT_CONFIG)
    return config


# ------------------------------------------------------------------------------
# Event extraction from tagged markdown
# ------------------------------------------------------------------------------
def _survivor_anchor(date: str, body: str) -> str:
    return f"event-{date}-{compute_body_hash(body)}"


def merged_survivor_anchors(merged_md: str) -> list[str]:
    """Return topic-neutral anchors using the Phase 17 merged-survivor key."""
    _, body = parse_yaml_frontmatter(merged_md)
    validate_event_headings(body)
    return [
        _survivor_anchor(event["date"], event["body"])
        for event in extract_events(strip_keep_both_conflict_notes(body))
    ]


def extract_events_from_tagged(tagged_md: str) -> List[Dict[str, Any]]:
    """
    Parse tagged markdown into event dicts.

    Each event dict contains:
      - date: YYYY-MM-DD string
      - title: event title
      - anchor: stable navigation target derived from the merged-survivor key
      - body: full body text
      - themes: list of theme strings
      - sources: list of source names (from inline annotations)
      - snippet: first N chars of body for index display
    """
    events: List[Dict[str, Any]] = []

    tagged_md = strip_keep_both_conflict_notes(tagged_md)
    matches = list(EVENT_HEADING_RE.finditer(tagged_md))
    if not matches:
        return events

    for i, match in enumerate(matches):
        heading_line = match.group(1).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(tagged_md)
        raw_block = tagged_md[start:end].strip()

        # Extract date and title
        date_title_match = re.match(
            r"^## Event:\s*(\d{4}-\d{2}-\d{2})(?:\s*[–-]\s*(.*))?$",
            heading_line,
        )
        date = date_title_match.group(1) if date_title_match else "unknown"
        title = (date_title_match.group(2) or "").strip() if date_title_match else ""

        # Separate heading from body
        newline_pos = raw_block.find("\n")
        if newline_pos >= 0:
            body = raw_block[newline_pos:].strip()
        else:
            body = ""

        themes: List[str] = []
        theme_match = THEME_COMMENT_RE.match(body)
        if theme_match:
            themes = list(dict.fromkeys(t.strip() for t in theme_match.group(1).split(",") if t.strip()))
            body = body[theme_match.end():].strip()
        marker = EVENT_ANCHOR_RE.match(body)
        body_clean = body[marker.end():].strip() if marker else body
        anchor = _survivor_anchor(date, body_clean)
        if marker and marker.group(1) != anchor:
            raise ValueError(f"Event anchor does not match its body: {marker.group(1)}")

        # Extract sources from body (inline annotations like "Source: Reddit")
        sources: List[str] = []
        for src_match in SOURCE_LINE_RE.finditer(body_clean):
            sources.append(src_match.group(1).strip())

        events.append({
            "date": date,
            "title": title,
            "anchor": anchor,
            "has_anchor": marker is not None,
            "body": body_clean,
            "themes": themes,
            "sources": sources,
            "snippet": body_clean[:DEFAULT_CONFIG["event_snippet_max_chars"]],
        })

    return events


def prepare_index_targets(tagged_md: str, events: List[Dict[str, Any]]) -> str:
    """Validate embedded targets or add them to an in-memory legacy copy."""
    anchors = [event["anchor"] for event in events]
    if len(anchors) != len(set(anchors)):
        raise ValueError("Tagged Chronicle contains duplicate survivor keys")
    markers = [match.group(1) for match in EVENT_ANCHOR_RE.finditer(tagged_md)]
    if markers:
        if markers != anchors or any(not event["has_anchor"] for event in events):
            raise ValueError("Tagged Chronicle contains missing, misplaced or duplicate event anchors")
        return tagged_md

    # Insert after a leading legacy theme comment when present.
    parts = []
    cursor = 0
    for heading, anchor in zip(EVENT_HEADING_RE.finditer(tagged_md), anchors, strict=True):
        newline = tagged_md.find("\n", heading.end(1))
        end = len(tagged_md) if newline == -1 else newline + 1
        theme = LEADING_THEME_RE.match(tagged_md, end)
        if theme:
            end = theme.end()
        parts.append(tagged_md[cursor:end])
        parts.append(f'\n\n<a id="{anchor}"></a>\n\n')
        cursor = end
    return "".join(parts) + tagged_md[cursor:]


class _NavigationHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._label: list[str] = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value and (name == "id" or (tag == "a" and name == "name")):
                self.anchors.append(value)
            if value and tag == "a" and name == "href":
                self._href = value

    def handle_data(self, data):
        if self._href is not None:
            self._label.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, "".join(self._label)))
            self._href = None
            self._label.clear()


def _markdown_renderer():
    try:
        from markdown_it import MarkdownIt
    except ImportError as exc:
        raise ValueError("Index navigation requires the wordpipe[chronicle] extra") from exc
    return MarkdownIt("commonmark").enable("table")


def rendered_navigation(markdown: str) -> tuple[list[str], list[tuple[str, str]]]:
    """Inspect actual Markdown navigation, excluding links and IDs in code blocks."""
    result = _NavigationHTML()
    result.feed(_markdown_renderer().render(markdown))
    result.close()
    return result.anchors, result.links


def verify_index_targets(markdown: str, events: List[Dict[str, Any]]) -> str:
    """Verify rendered targets, splitting spanning fences in a navigation copy."""
    expected = [event["anchor"] for event in events]
    counts = Counter(rendered_navigation(markdown)[0])
    if any(counts[anchor] == 0 for anchor in expected):
        markdown = _split_fences_at_events(markdown)
        counts = Counter(rendered_navigation(markdown)[0])
    if any(counts[anchor] != 1 for anchor in expected):
        raise ValueError("Tagged Chronicle must render exactly one target per survivor")
    return markdown


def _split_fences_at_events(markdown: str) -> str:
    """Expose event headings hidden inside a fence without changing the input."""
    lines = re.split(r"(?<=\n)", markdown)
    headings = (i for i, line in enumerate(lines) if EVENT_HEADING_RE.match(line))
    anchors = (i for i, line in enumerate(lines) if EVENT_ANCHOR_RE.fullmatch(line.strip()))
    anchor_lines = dict(zip(headings, anchors, strict=True))
    insertions: dict[int, list[str]] = defaultdict(list)
    for token in _markdown_renderer().parse(markdown):
        if token.type != "fence" or token.map is None:
            continue
        start, end = token.map
        for row in range(start + 1, end):
            anchor = anchor_lines.get(row)
            if anchor is not None and row < anchor < end:
                insertions[row].append(f"\n{token.markup}\n\n")
                insertions[anchor + 1].append(f"\n{token.markup}{token.info}\n")
    if not insertions:
        return markdown
    parts = []
    for i, line in enumerate([*lines, ""]):
        parts.extend(insertions.get(i, ()))
        parts.append(line)
    return "".join(parts)


# ------------------------------------------------------------------------------
# Deduplication
# ------------------------------------------------------------------------------
def deduplicate_events(
    events: List[Dict[str, Any]],
    method: str = "date_title",
) -> List[Dict[str, Any]]:
    """
    Deduplicate events by title (normalized) or by date+title.

    When duplicates are found:
      - Themes are merged (union of all theme lists)
      - The longest body text is kept
      - Sources are merged (deduplicated)

    Args:
        events: List of event dicts
        method: "title" (default) or "date_title"

    Returns:
        Deduplicated list of event dicts
    """
    if method not in ("title", "date_title"):
        logging.warning("Unknown dedup method '%s'; using 'date_title'.", method)
        method = "date_title"

    seen: Dict[str, Dict[str, Any]] = {}

    for ev in events:
        norm_title = re.sub(r"\s+", " ", ev["title"].lower()).strip()
        if method == "title":
            key = norm_title
        else:
            key = f"{ev['date']}|{norm_title}"

        if key in seen:
            existing = seen[key]
            # Merge themes
            existing["themes"] = list(dict.fromkeys(existing["themes"] + ev["themes"]))
            # Keep the longest body while the first survivor represents the group.
            if len(ev["body"]) > len(existing["body"]):
                for field in ("body", "snippet"):
                    existing[field] = ev[field]
            # Merge sources
            existing["sources"] = list(dict.fromkeys(existing["sources"] + ev["sources"]))
        else:
            seen[key] = dict(ev)

    result = list(seen.values())
    if len(result) < len(events):
        logging.info(
            "Deduplication: %d events → %d unique (method: %s)",
            len(events),
            len(result),
            method,
        )
    return result


# ------------------------------------------------------------------------------
# Index builders
# ------------------------------------------------------------------------------
def build_event_index(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build event index context for template rendering.

    Returns dict with:
      - events: sorted by date (ascending)
      - date_range_start, date_range_end
    """
    sorted_events = sorted(events, key=lambda e: e["date"])
    dates = [e["date"] for e in sorted_events if e["date"] != "unknown"]

    return {
        "events": sorted_events,
        "date_range_start": min(dates) if dates else "unknown",
        "date_range_end": max(dates) if dates else "unknown",
    }


def build_theme_index(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build theme index context.

    Groups events by theme. Returns dict with:
      - themes: dict of theme_name -> list of events
    """
    theme_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for ev in events:
        for theme in ev["themes"]:
            theme_groups[theme].append(ev)

    return {"themes": dict(theme_groups)}


def build_source_manifest(
    events: List[Dict[str, Any]],
    source_coverage_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Build source manifest context.

    If source_coverage_path is provided, parses it for source names and counts.
    Supports two markdown table formats:

    - Numbered: ``| Number | Source | Count |``
    - Un-numbered: ``| Source | Unique Events | Duplicates | Status |``

    Otherwise, extracts source names from inline annotations in events.

    Returns dict with:
      - sources: list of {name, event_count, status}
      - total_events, sources_with_events, sources_without_events

    Raises:
        ValueError: If the coverage file has no recognizable format or zero valid rows.
    """
    sources: Dict[str, int] = defaultdict(int)
    source_statuses: Dict[str, str] = {}

    if source_coverage_path and source_coverage_path.exists():
        # Parse source coverage markdown
        text = source_coverage_path.read_text(encoding="utf-8")

        # Detect format from the first non-empty table header row
        header_match = re.search(
            r"^\|(.+?)\|\s*$", text, re.MULTILINE
        )
        if not header_match:
            raise ValueError(
                f"Cannot find table header in source coverage file: {source_coverage_path}"
            )
        header = header_match.group(1).strip().lower()

        numbered_header = re.match(
            r"\s*number\s*\|\s*source\s*\|", header
        )
        unnamed_header = re.match(
            r"\s*source\s*\|\s*unique\s+events\s*\|", header
        )

        if numbered_header:
            # Format: | Number | Source | Count |
            table_row_re = re.compile(
                r"^\|\s*\d+\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|", re.MULTILINE
            )
            for match in table_row_re.finditer(text):
                name = match.group(1).strip()
                count = int(match.group(2))
                sources[name] = count
                source_statuses[name] = "active" if count > 0 else "no events"
        elif unnamed_header:
            # Format: | Source | Unique Events | Duplicates | Status |
            table_row_re = re.compile(
                r"^\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|",
                re.MULTILINE,
            )
            for match in table_row_re.finditer(text):
                name = match.group(1).strip()
                count = int(match.group(2))
                status = match.group(4).strip()
                # Skip header/separator rows
                if name.lower() in ("source", "--------"):
                    continue
                sources[name] = count
                source_statuses[name] = status
        else:
            raise ValueError(
                f"Unrecognized source coverage table format in {source_coverage_path}. "
                f"Expected '| Number | Source | Count |' or '| Source | Unique Events | "
                f"Duplicates | Status |'. Got header: {header_match.group(1).strip()!r}"
            )

        if not sources:
            raise ValueError(
                f"Source coverage file {source_coverage_path} contains zero valid rows."
            )
    else:
        # Extract from event inline annotations
        for ev in events:
            for src in ev["sources"]:
                sources[src] += 1
        if not sources:
            # Fallback: count unique source annotations across all events
            all_sources = set()
            for ev in events:
                for src in ev["sources"]:
                    all_sources.add(src)
            if not all_sources:
                # Last resort: single merged source
                sources["Merged Chronicle"] = len(events)

    source_list = [
        {
            "name": name,
            "event_count": count,
            "status": source_statuses.get(name, "active"),
        }
        for name, count in sorted(sources.items(), key=lambda x: -x[1])
    ]

    return {
        "sources": source_list,
        "total_events": len(events),
        "sources_with_events": sum(1 for s in source_list if s["event_count"] > 0),
        "sources_without_events": sum(1 for s in source_list if s["event_count"] == 0),
    }


def build_link_registry(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build link registry context.

    Extracts all external URLs from event bodies, deduplicates, groups by domain.

    Returns dict with:
      - links: dict of domain -> list of {url, first_seen}
    """
    domain_links: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    seen_urls: set = set()

    for ev in events:
        urls = URL_RE.findall(ev["body"])
        for url in urls:
            # Normalize: strip trailing punctuation
            url = url.rstrip(".,;:!?\"'")
            if url in seen_urls:
                continue
            seen_urls.add(url)

            try:
                parsed = urlparse(url)
                domain = parsed.netloc or "unknown"
            except Exception:
                domain = "unknown"

            domain_links[domain].append({
                "url": url,
                "first_seen": ev["date"],
            })

    return {"links": dict(domain_links)}


# ------------------------------------------------------------------------------
# Rendering
# ------------------------------------------------------------------------------
def render_template(
    template_name: str,
    context: Dict[str, Any],
    templates_dir: str = "pipeline/templates",
) -> str:
    """
    Render a template with the given context.

    Uses Jinja2 if available; falls back to basic string formatting.
    """
    templates_path = Path(templates_dir)

    if HAS_JINJA2:
        if not templates_path.exists():
            logging.warning(
                "Template directory '%s' not found; using fallback formatting.",
                templates_dir,
            )
            return _fallback_render(template_name, context)

        try:
            env = Environment(
                loader=FileSystemLoader(str(templates_path)),
                autoescape=select_autoescape(["md"]),
            )
            env.globals["event_link"] = event_link
            template = env.get_template(template_name)
            return template.render(context)
        except Exception as e:
            logging.warning("Jinja2 rendering failed (%s); using fallback.", e)
            return _fallback_render(template_name, context)
    else:
        logging.warning("Jinja2 not installed; using basic string formatting.")
        return _fallback_render(template_name, context)


def _fallback_render(template_name: str, context: Dict[str, Any]) -> str:
    """
    Fallback rendering when Jinja2 is unavailable.

    Produces a simple markdown table for each index type.
    """
    if "event_index" in template_name:
        return _render_event_index_fallback(context)
    elif "theme_index" in template_name:
        return _render_theme_index_fallback(context)
    elif "source_manifest" in template_name:
        return _render_source_manifest_fallback(context)
    elif "link_registry" in template_name:
        return _render_link_registry_fallback(context)
    else:
        return f"# {template_name}\n\n(No Jinja2 template available)\n"


def event_link(event: Dict[str, Any]) -> str:
    """Escape a Markdown table link label while preserving its Unicode text."""
    label = html.escape(event["title"] or "Untitled event")
    for char in "\\[]|`*_~":
        label = label.replace(char, f"&#{ord(char)};")
    return f"[{label}]({event.get('target', '')}#{event['anchor']})"


def _render_event_index_fallback(context: Dict[str, Any]) -> str:
    lines = [
        "# Event Index",
        "",
        f"> Generated from chronicle tagged output.",
        f"> **Total events:** {len(context.get('events', []))}",
        f"> **Date range:** {context.get('date_range_start', 'unknown')} to {context.get('date_range_end', 'unknown')}",
        "",
        "| # | Date | Title | Themes |",
        "|---|------|-------|--------|",
    ]
    for i, ev in enumerate(context.get("events", []), 1):
        themes = ", ".join(ev.get("themes", []))
        lines.append(f"| {i} | {ev.get('date', '')} | {event_link(ev)} | {themes} |")
    lines.append("")
    return "\n".join(lines)


def _render_theme_index_fallback(context: Dict[str, Any]) -> str:
    lines = [
        "# Theme Index",
        "",
        "> Events grouped by theme.",
        "",
    ]
    themes = context.get("themes", {})
    for theme_name in sorted(themes.keys()):
        theme_events = themes[theme_name]
        lines.append(f"## {theme_name}")
        lines.append("")
        lines.append(f"**{len(theme_events)} events**")
        lines.append("")
        lines.append("| Date | Title |")
        lines.append("|------|-------|")
        for ev in theme_events:
            lines.append(f"| {ev.get('date', '')} | {event_link(ev)} |")
        lines.append("")
    return "\n".join(lines)


def _render_source_manifest_fallback(context: Dict[str, Any]) -> str:
    lines = [
        "# Source Manifest",
        "",
        "> Sources contributing to the chronicle.",
        "",
    ]
    sources = context.get("sources", [])
    lines.append(f"**Total sources:** {len(sources)}")
    lines.append("")
    lines.append("| # | Source Name | Events Contributed | Status |")
    lines.append("|---|-------------|-------------------|--------|")
    for i, src in enumerate(sources, 1):
        lines.append(f"| {i} | {src.get('name', '')} | {src.get('event_count', 0)} | {src.get('status', '')} |")
    lines.append("")
    lines.append("## Source Coverage Summary")
    lines.append("")
    lines.append(f"- **Total events in merged chronicle:** {context.get('total_events', 0)}")
    lines.append(f"- **Sources with events:** {context.get('sources_with_events', 0)}")
    lines.append(f"- **Sources without events:** {context.get('sources_without_events', 0)}")
    lines.append("")
    return "\n".join(lines)


def _render_link_registry_fallback(context: Dict[str, Any]) -> str:
    lines = [
        "# Link Registry",
        "",
        "> All external URLs extracted from the chronicle, deduplicated and sorted by domain.",
        "",
    ]
    links = context.get("links", {})
    total = sum(len(v) for v in links.values())
    lines.append(f"**Total unique links:** {total}")
    lines.append("")
    for domain in sorted(links.keys()):
        domain_links = links[domain]
        lines.append(f"## {domain}")
        lines.append("")
        lines.append("| # | URL | First Seen In |")
        lines.append("|---|-----|---------------|")
        for i, link in enumerate(domain_links, 1):
            lines.append(f"| {i} | {link.get('url', '')} | {link.get('first_seen', '')} |")
        lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------------------------
# Safe file writing (atomic via temp file + rename)
# ------------------------------------------------------------------------------
def safe_write(path: Path, content: str) -> None:
    """
    Write content to a file atomically.

    Writes to a temporary file first, then renames to the final path.
    This prevents half-written files if the process crashes mid-write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path_str = tempfile.mkstemp(
        suffix=".tmp",
        prefix=path.stem + "_",
        dir=str(path.parent),
    )
    try:
        with open(fd, "w", encoding="utf-8") as f:
            f.write(content)
        # Atomic rename (Windows: replace=True)
        import os
        os.replace(tmp_path_str, str(path))
    except Exception:
        # Clean up temp file on failure
        import os
        try:
            os.unlink(tmp_path_str)
        except OSError:
            pass
        raise
