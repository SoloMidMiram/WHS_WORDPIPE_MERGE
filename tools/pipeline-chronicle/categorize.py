#!/usr/bin/env python3
"""
categorize.py – Tag events in a normalised/merged chronicle with theme labels.

Reads a markdown file with ## Event: YYYY-MM-DD – Title blocks and a JSON or YAML
config file mapping theme names to keyword lists. Tags each event with inline
HTML comments (<!-- themes: ... -->) and optionally writes a sidecar JSON file.

Input:
  - A markdown file with optional YAML front-matter and ## Event: blocks
  - A JSON or YAML configuration file with a 'themes' key

Output:
  - Tagged markdown with inline <!-- themes: ... --> comments after each event heading
  - Optional sidecar JSON with structured tag data

Usage:
  python categorize.py --input merged.md --config config.json --output tagged.md
  python categorize.py --input merged.md --config themes.yaml --sidecar
  python categorize.py --input normalised.md  # uses built-in default themes
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# ------------------------------------------------------------------------------
# Built-in default themes (used when no --config is provided)
# ------------------------------------------------------------------------------
DEFAULT_THEMES = {
    "Web UI": [
        "chat.openai.com", "chatgpt.com", "web interface", "browser",
        "UI freeze", "button disappeared", "interface", "web app",
    ],
    "API/Developer": [
        "api.openai.com", "ChatGPT API", "playground", "code interpreter",
        "function calling", "API", "developer", "endpoint", "rate limit",
        "token", "GPT-4 API",
    ],
    "Outages": [
        "down", "outage", "downtime", "unreachable", "503 error",
        "service disruption", "error", "unavailable", "crash",
    ],
    "Jailbreaks/Exploits": [
        "jailbreak", "DAN", "prompt injection", "bypass",
        "ignore previous instructions", "exploit", "prompt leak",
    ],
    "Memory/Personalisation": [
        "memory", "custom instructions", "bio", "personalised",
        "remembers", "personalisation",
    ],
    "Culture/Virality": [
        "viral", "Twitter", "Reddit", "meme", "social media",
        "went viral", "community",
    ],
}

# ------------------------------------------------------------------------------
# Constants — shared event heading regex (same as merge.py)
# ------------------------------------------------------------------------------
EVENT_HEADING_RE = re.compile(
    r"^(## Event:\s*\d{4}-\d{2}-\d{2}(?:\s*[–-]\s*.*?)?)\s*$",
    re.MULTILINE,
)

# ------------------------------------------------------------------------------
# Config loading
# ------------------------------------------------------------------------------


def load_themes(config_path: Optional[Path]) -> Dict[str, List[str]]:
    """
    Load theme definitions from a JSON or YAML config file.

    If config_path is None, returns built-in default themes.
    Expects a 'themes' key in the config file.
    """
    if config_path is None:
        logging.info("No config file provided; using built-in default themes.")
        return dict(DEFAULT_THEMES)

    if not config_path.exists():
        logging.error("Config file not found: %s", config_path)
        sys.exit(1)

    raw = config_path.read_text(encoding="utf-8")
    config: Dict[str, Any] = {}

    # Try JSON first, then YAML
    try:
        config = json.loads(raw)
    except json.JSONDecodeError:
        try:
            config = yaml.safe_load(raw)
            if config is None:
                config = {}
        except yaml.YAMLError as e:
            logging.error("Config file %s is neither valid JSON nor valid YAML: %s", config_path, e)
            sys.exit(1)

    themes = config.get("themes")
    if not themes:
        logging.warning("Config file %s has no 'themes' key; using built-in defaults.", config_path)
        return dict(DEFAULT_THEMES)

    if not isinstance(themes, dict):
        logging.error("'themes' must be a dictionary, got %s.", type(themes).__name__)
        sys.exit(1)

    # Validate each theme has a list of keyword strings
    for theme_name, keywords in themes.items():
        if not isinstance(keywords, list):
            logging.error("Theme '%s' must map to a list of keyword strings, got %s.", theme_name, type(keywords).__name__)
            sys.exit(1)
        if not all(isinstance(kw, str) for kw in keywords):
            logging.error("Theme '%s' contains non-string keyword entries.", theme_name)
            sys.exit(1)

    return themes


# ------------------------------------------------------------------------------
# Event extraction (same pattern as merge.py)
# ------------------------------------------------------------------------------


def extract_events(md_body: str) -> List[Dict[str, str]]:
    """
    Split the markdown body into event blocks.

    Each event block starts with a line matching:
      ## Event: YYYY-MM-DD – Optional Title

    Returns list of dicts with keys:
      'date'         - YYYY-MM-DD string
      'title'        - title string (may be empty)
      'heading_line' - the full ## Event: heading line
      'block'        - full raw block including heading
      'body'         - body text after heading (may be empty)
    """
    events: List[Dict[str, str]] = []
    matches = list(EVENT_HEADING_RE.finditer(md_body))

    if not matches:
        return events

    for i, match in enumerate(matches):
        heading_line = match.group(1).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_body)
        raw_block = md_body[start:end].strip()

        # Extract date and title from heading
        date_title_match = re.match(
            r"^## Event:\s*(\d{4}-\d{2}-\d{2})(?:\s*[–-]\s*(.*))?$",
            heading_line,
        )
        date = date_title_match.group(1) if date_title_match else "unknown"
        title = (date_title_match.group(2) or "").strip() if date_title_match else ""

        # Separate heading line from body
        newline_pos = raw_block.find("\n")
        if newline_pos >= 0:
            body = raw_block[newline_pos:].strip()
        else:
            body = ""

        events.append({
            "date": date,
            "title": title,
            "heading_line": heading_line,
            "block": raw_block,
            "body": body,
        })

    return events


# ------------------------------------------------------------------------------
# Theme matching
# ------------------------------------------------------------------------------


def match_themes(body: str, themes: Dict[str, List[str]]) -> List[str]:
    """
    Determine which themes match the given body text.

    Uses simple case-insensitive substring matching (not word-boundary regex)
    to avoid issues with special characters like dots, dashes, and numbers
    in keywords (e.g., "chat.openai.com", "503 error", "DALL·E").

    Args:
        body: The event body text to scan
        themes: Dict of theme_name -> list of keyword strings

    Returns:
        Sorted list of matching theme names
    """
    if not body:
        return []

    body_lower = body.lower()
    matched: List[str] = []

    for theme_name, keywords in themes.items():
        for kw in keywords:
            if kw.lower() in body_lower:
                matched.append(theme_name)
                break  # one keyword match suffices for this theme

    return sorted(matched)


# ------------------------------------------------------------------------------
# Output assembly
# ------------------------------------------------------------------------------


def rebuild_tagged_md(
    original_text: str,
    events: List[Dict[str, Any]],
) -> str:
    """
    Reconstruct the full markdown with tag comments inserted.

    Preserves YAML front-matter and any content before the first event heading.
    Inserts <!-- themes: ... --> comment on the line after each event heading
    that has matching themes.
    """
    # Find where the body starts (after YAML front-matter and # Source: line)
    body_start = 0
    if original_text.startswith("---"):
        parts = original_text.split("---", 2)
        if len(parts) >= 3:
            # parts[2] is everything after the closing ---
            body_start = original_text.index(parts[2])

    preamble = original_text[:body_start]
    body = original_text[body_start:]

    # Build tagged blocks
    tagged_blocks: List[str] = []
    for ev in events:
        raw = ev["block"]
        if ev["themes"]:
            heading = ev["heading_line"]
            comment = f"<!-- themes: {', '.join(ev['themes'])} -->"
            # Find the body part (everything after the heading line)
            newline_pos = raw.find("\n")
            if newline_pos >= 0:
                rest = raw[newline_pos:]
            else:
                rest = ""
            tagged_blocks.append(f"{heading}\n{comment}{rest}")
        else:
            tagged_blocks.append(raw)

    return preamble + "\n\n".join(tagged_blocks) + "\n"


def build_sidecar_json(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build a sidecar JSON structure with per-event tag data.

    Returns a list of dicts with keys: date, title, themes.
    """
    sidecar: List[Dict[str, Any]] = []
    for ev in events:
        sidecar.append({
            "date": ev["date"],
            "title": ev["title"],
            "themes": ev["themes"],
        })
    return sidecar


# ------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tag events in a normalised/merged chronicle with theme labels."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to input .md file (normalised or merged)",
    )
    parser.add_argument(
        "--config", "-c",
        help="JSON or YAML config file with theme keywords (optional; uses built-in defaults if omitted)",
    )
    parser.add_argument(
        "--output", "-o",
        help="Path for tagged output (default: <input>_tagged.md)",
    )
    parser.add_argument(
        "--sidecar", action="store_true",
        help="Also write a sidecar JSON file with structured tag data",
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

    # 1. Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        logging.error("Input file not found: %s", input_path)
        sys.exit(1)
    original_text = input_path.read_text(encoding="utf-8")

    # 2. Load themes (from config or built-in defaults)
    config_path = Path(args.config) if args.config else None
    themes = load_themes(config_path)
    logging.info(
        "Loaded %d themes with %d total keywords.",
        len(themes),
        sum(len(v) for v in themes.values()),
    )

    # 3. Find body start (skip YAML front-matter)
    body_start = 0
    if original_text.startswith("---"):
        parts = original_text.split("---", 2)
        if len(parts) >= 3:
            body_start = original_text.index(parts[2])
    body = original_text[body_start:]

    # 4. Extract events
    events = extract_events(body)
    if not events:
        logging.warning("No events found in input. Output will be unchanged.")
        out_path = Path(args.output) if args.output else input_path.with_name(input_path.stem + "_tagged.md")
        out_path.write_text(original_text, encoding="utf-8")
        logging.info("Output written to %s (unchanged — no events to tag)", out_path)
        return

    # 5. Tag events
    for ev in events:
        ev["themes"] = match_themes(ev["body"], themes)

    # 6. Rebuild tagged markdown
    tagged_md = rebuild_tagged_md(original_text, events)

    # 7. Write output
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = input_path.with_name(input_path.stem + "_tagged.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(tagged_md, encoding="utf-8")

    # 8. Summary
    tagged_count = sum(1 for ev in events if ev["themes"])
    logging.info("Tagged output written to %s", out_path)
    logging.info("%d/%d events received theme tags.", tagged_count, len(events))

    if args.verbose:
        for ev in events:
            if ev["themes"]:
                logging.debug("  %s → %s", ev["date"], ", ".join(ev["themes"]))

    # 9. Optional sidecar JSON
    if args.sidecar:
        sidecar_path = out_path.with_suffix(".tagged.json")
        sidecar_data = build_sidecar_json(events)
        with open(sidecar_path, "w", encoding="utf-8") as f:
            json.dump(sidecar_data, f, indent=2, ensure_ascii=False)
        logging.info("Sidecar JSON written to %s", sidecar_path)


if __name__ == "__main__":
    main()
