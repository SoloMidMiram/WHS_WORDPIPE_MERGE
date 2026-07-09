"""Merge module for the chronicle pipeline.

Pure functions for combining multiple normalised chronicle files into one
deduplicated file with conflict resolution and source coverage.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------
EVENT_HEADING_RE = re.compile(
    r"^## Event:\s*(\d{4}-\d{2}-\d{2})(?:\s*[–-]\s*(.*?))?\s*$",
    re.MULTILINE,
)


# ------------------------------------------------------------------------------
# Parsing helpers
# ------------------------------------------------------------------------------


def parse_yaml_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """
    If the file starts with a YAML front-matter block (between '---' lines),
    return (metadata_dict, rest_of_text). Otherwise return ({}, text).
    """
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) >= 3:
        try:
            metadata = yaml.safe_load(parts[1])
            return (metadata or {}), parts[2].lstrip("\n")
        except yaml.YAMLError as e:
            logging.warning("Malformed YAML front-matter: %s", e)
            return {}, text
    return {}, text


def extract_events(md_body: str) -> List[Dict[str, str]]:
    """
    Split the normalised body into a list of event dicts.

    Each event block starts with a line matching::
      ## Event: YYYY-MM-DD - Optional Title

    Returns list of dicts with keys:
      'date'   - YYYY-MM-DD string
      'title'  - title string (may be empty)
      'block'  - full raw block including heading
      'body'   - body text after heading (may be empty)
    """
    events: List[Dict[str, str]] = []
    matches = list(EVENT_HEADING_RE.finditer(md_body))

    if not matches:
        return events

    for i, match in enumerate(matches):
        date = match.group(1)
        title = (match.group(2) or "").strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_body)
        raw_block = md_body[start:end].strip()

        # Separate heading line from body
        newline_pos = raw_block.find("\n")
        if newline_pos >= 0:
            body = raw_block[newline_pos:].strip()
        else:
            body = ""

        events.append({
            "date": date,
            "title": title,
            "block": raw_block,
            "body": body,
        })

    return events


def compute_body_hash(body: str) -> str:
    """Return SHA-256 hex digest of the normalised body text."""
    normalised = " ".join(body.split())  # collapse all whitespace
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()


def parse_date_tuple(date_str: str) -> Tuple[int, int, int]:
    """Convert 'YYYY-MM-DD' to (year, month, day) tuple for sorting."""
    parts = date_str.split("-")
    return int(parts[0]), int(parts[1]), int(parts[2])


# ------------------------------------------------------------------------------
# Source coverage
# ------------------------------------------------------------------------------


def generate_source_coverage(
    source_names: List[str],
    event_contributions: Dict[str, int],
    duplicates: List[Dict],
) -> str:
    """
    Generate a markdown table showing source contributions.

    Args:
        source_names: Ordered list of all source files processed
        event_contributions: Dict of source_name -> unique events contributed
        duplicates: List of duplicate/conflict entries from merge

    Returns:
        Markdown table string
    """
    lines = [
        "# Source Coverage\n",
        "| Source | Unique Events | Duplicates | Status |",
        "|--------|--------------|------------|--------|",
    ]

    # Count duplicates per source
    dup_counts: Dict[str, int] = {}
    for d in duplicates:
        for src in d.get("sources", []):
            dup_counts[src] = dup_counts.get(src, 0) + 1

    for src in source_names:
        unique = event_contributions.get(src, 0)
        dups = dup_counts.get(src, 0)
        status = "ok" if unique > 0 else "no events"
        lines.append(f"| {src} | {unique} | {dups} | {status} |")

    lines.append("")
    lines.append(f"_Total unique events: {sum(event_contributions.values())}_")
    return "\n".join(lines)


# ------------------------------------------------------------------------------
# Core merge logic
# ------------------------------------------------------------------------------


def merge_files(
    file_paths: List[Path],
    conflict_mode: str = "keep-both",
) -> Tuple[str, List[Dict], Dict[str, int], List[str]]:
    """
    Read all normalised files, collect events, deduplicate, and produce merged
    markdown, a duplicates report, and source contribution counts.

    Args:
        file_paths: List of paths to normalised .md files
        conflict_mode: 'keep-both' | 'manual' | 'skip'

    Returns:
        (merged_markdown, duplicates_list, source_contributions, source_names)
    """
    all_events: List[Tuple[Dict[str, str], str]] = []  # (event_dict, source_name)
    source_names: List[str] = []

    for file_path in file_paths:
        logging.info("Reading %s", file_path)
        text = file_path.read_text(encoding="utf-8")
        metadata, body = parse_yaml_frontmatter(text)

        src = metadata.get("source", file_path.stem)
        source_names.append(src)

        events_list = extract_events(body)
        if not events_list:
            logging.warning("No events found in %s (source: %s)", file_path.name, src)

        for ev in events_list:
            all_events.append((ev, src))

    # --- Step 1: Group by (date, hash) to find true duplicates ---
    # seen: (date, hash) -> { 'event': event, 'sources': [src1, src2, ...] }
    seen: Dict[Tuple[str, str], Dict[str, Any]] = {}
    duplicates: List[Dict] = []

    for ev, src in all_events:
        date = ev["date"]
        body_hash = compute_body_hash(ev["body"])
        key = (date, body_hash)

        if key not in seen:
            seen[key] = {"event": ev, "sources": [src]}
        else:
            existing = seen[key]
            if src not in existing["sources"]:
                existing["sources"].append(src)
                duplicates.append({
                    "date": date,
                    "hash": body_hash,
                    "sources": list(existing["sources"]),
                    "title": ev["title"],
                    "note": "Duplicate content (same date + same body)",
                })

    # --- Step 2: Group by date to find conflicts (same date, different hash) ---
    date_groups: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
    for (date, hash_val), entry in seen.items():
        date_groups.setdefault(date, []).append((hash_val, entry))

    # --- Step 3: Resolve conflicts per date ---
    final_events: List[Dict[str, Any]] = []
    source_contributions: Dict[str, int] = {}

    for date in sorted(date_groups.keys(), key=parse_date_tuple):
        hashed_entries = date_groups[date]

        if len(hashed_entries) == 1:
            # Unique date+hash -- keep as-is
            entry = hashed_entries[0][1]
            final_events.append({
                "date": date,
                "block": entry["event"]["block"],
                "title": entry["event"]["title"],
                "sources": entry["sources"],
                "conflict_note": None,
            })
            for src in entry["sources"]:
                source_contributions[src] = source_contributions.get(src, 0) + 1
        else:
            # Same date, different content -> conflict
            logging.warning(
                "Conflict on date %s: %d different event bodies.",
                date,
                len(hashed_entries),
            )

            if conflict_mode == "skip":
                # Keep first occurrence, drop rest
                first_hash, first_entry = hashed_entries[0]
                final_events.append({
                    "date": date,
                    "block": first_entry["event"]["block"],
                    "title": first_entry["event"]["title"],
                    "sources": first_entry["sources"],
                    "conflict_note": None,
                })
                for src in first_entry["sources"]:
                    source_contributions[src] = source_contributions.get(src, 0) + 1

                for _, other_entry in hashed_entries[1:]:
                    duplicates.append({
                        "date": date,
                        "hash": compute_body_hash(other_entry["event"]["body"]),
                        "sources": other_entry["sources"],
                        "title": other_entry["event"]["title"],
                        "note": "Skipped due to date conflict (keep-first mode).",
                    })

            elif conflict_mode == "manual":
                # Omit all from merged output; write all to duplicates
                for _, entry in hashed_entries:
                    duplicates.append({
                        "date": date,
                        "hash": compute_body_hash(entry["event"]["body"]),
                        "sources": entry["sources"],
                        "title": entry["event"]["title"],
                        "note": "Conflict -- manual review needed.",
                    })
                # Do not add to final_events

            else:  # "keep-both" (default)
                for i, (_, entry) in enumerate(hashed_entries):
                    note = None
                    if i > 0:
                        note = "<!-- Duplicate date, different content -->"
                    final_events.append({
                        "date": date,
                        "block": entry["event"]["block"],
                        "title": entry["event"]["title"],
                        "sources": entry["sources"],
                        "conflict_note": note,
                    })
                    for src in entry["sources"]:
                        source_contributions[src] = source_contributions.get(src, 0) + 1

    # --- Step 4: Sort final events by date ---
    final_events.sort(key=lambda e: parse_date_tuple(e["date"]))

    # --- Step 5: Build merged markdown ---
    min_date = final_events[0]["date"] if final_events else "unknown"
    max_date = final_events[-1]["date"] if final_events else "unknown"
    event_count = len(final_events)

    frontmatter: Dict[str, Any] = {
        "sources": source_names,
        "date_range": f"{min_date} to {max_date}",
        "event_count": event_count,
        "merged_from": len(file_paths),
    }
    yaml_str = yaml.dump(
        frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
    ).strip()

    md = f"---\n{yaml_str}\n---\n\n# Source: Merged Chronicles\n\n"

    for ev in final_events:
        if ev["conflict_note"]:
            md += ev["conflict_note"] + "\n"
        md += ev["block"].strip() + "\n\n"

    return md, duplicates, source_contributions, source_names


# ------------------------------------------------------------------------------
# Output writers
# ------------------------------------------------------------------------------


def write_duplicates_report(duplicates: List[Dict], output_path: Path) -> None:
    """Write duplicates JSON report."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(duplicates, f, indent=2, ensure_ascii=False)
    logging.info("Duplicates report written to %s", output_path)


def write_source_coverage(
    source_names: List[str],
    source_contributions: Dict[str, int],
    duplicates: List[Dict],
    output_path: Path,
) -> None:
    """Write source coverage markdown table."""
    md = generate_source_coverage(source_names, source_contributions, duplicates)
    output_path.write_text(md, encoding="utf-8")
    logging.info("Source coverage written to %s", output_path)


# ------------------------------------------------------------------------------
# Input validation
# ------------------------------------------------------------------------------


def collect_input_files(inputs: Optional[List[str]], input_dir: Optional[str]) -> List[Path]:
    """
    Collect and validate input file paths.

    Args:
        inputs: List of file paths from --inputs flag
        input_dir: Directory path from --input-dir flag

    Returns:
        List of resolved Path objects

    Raises:
        SystemExit on validation failure
    """
    files: List[Path] = []

    if inputs:
        for f in inputs:
            path = Path(f).resolve()
            if not path.exists():
                logging.error("File not found: %s", path)
                sys.exit(1)
            if not path.suffix.lower() == ".md":
                logging.warning("File does not have .md extension: %s", path)
            files.append(path)

    elif input_dir:
        dir_path = Path(input_dir).resolve()
        if not dir_path.is_dir():
            logging.error("Directory not found: %s", dir_path)
            sys.exit(1)
        files = sorted(dir_path.glob("*.md"))
        if not files:
            logging.error("No .md files found in directory: %s", dir_path)
            sys.exit(1)

    if not files:
        logging.error("No input files provided. Use --inputs or --input-dir.")
        sys.exit(1)

    # Check for duplicate files (same resolved path)
    seen_paths: set = set()
    unique_files: List[Path] = []
    for f in files:
        if f in seen_paths:
            logging.warning("Duplicate file skipped: %s", f)
        else:
            seen_paths.add(f)
            unique_files.append(f)

    return unique_files
