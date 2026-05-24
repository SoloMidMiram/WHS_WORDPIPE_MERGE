#!/usr/bin/env python3
"""
categorize.py – Tag events in a normalised/merged chronicle with theme labels.

Reads a markdown file with ## Event: YYYY-MM-DD – Title blocks and a JSON or YAML
config file mapping theme names to keyword lists. Tags each event with inline
HTML comments (<!-- themes: ... -->) and optionally writes a sidecar JSON file.

Supports negative keywords per theme to reduce false positives.

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
  python categorize.py --input merged.md --dry-run  # preview tags without writing

Exit codes:
  0 - Success
  1 - Input file not found
  2 - Config file not found or malformed
  3 - No events found in input
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

# ------------------------------------------------------------------------------
# Built-in default themes (used when no --config is provided)
# These are the tightened versions with negative keywords to reduce false positives.
# ------------------------------------------------------------------------------
DEFAULT_THEMES: Dict[str, Dict[str, List[str]]] = {
    "Web UI": {
        "keywords": [
            "chat.openai.com", "chatgpt.com", "web interface",
            "browser interface", "interface redesign", "website",
            "web app", "UI freeze", "button disappeared",
            "interface",
        ],
        "negative_keywords": [
            "API interface",
            "command line interface",
        ],
    },
    "API/Developer": {
        "keywords": [
            "API", "developer", "Linux terminal", "simulating",
            "pretend computer", "Linux shell", "function calling",
            "code interpreter", "playground", "endpoint",
            "rate limit", "token", "GPT-4 API",
        ],
        "negative_keywords": ["graphical", "GUI"],
    },
    "Outages": {
        "keywords": [
            "server crash", "system crash", "crash bug",
            "503 error", "server error", "error message",
            "downtime", "outage", "unavailable",
            "service disruption", "unreachable",
        ],
        "negative_keywords": [
            "meme crash", "crash course", "trial and error",
            "error in judgment", "crash diet",
        ],
    },
    "Jailbreaks/Exploits": {
        "keywords": [
            "jailbreak exploit", "prompt exploit", "security exploit",
            "prompt injection", "bypass", "DAN", "jailbreak",
            "ignore previous instructions", "prompt leak",
        ],
        "negative_keywords": [
            "creative exploit", "exploit the system creatively",
            "exploit a loophole creatively",
        ],
    },
    "Memory/Personalisation": {
        "keywords": [
            "memory", "chat history", "conversation history",
            "memory feature", "personalisation", "custom instructions",
            "bio", "remembers", "personalised",
        ],
        "negative_keywords": [
            "in memory of", "memory lane", "memory game",
        ],
    },
    "Culture/Virality": {
        "keywords": [
            "viral", "mega-viral", "viral sensation",
            "Twitter", "Reddit", "meme", "trending",
            "went viral", "social media", "community",
        ],
        "negative_keywords": ["anti-viral"],
    },
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


def load_themes(config_path: Optional[Path]) -> Dict[str, Dict[str, List[str]]]:
    """
    Load theme definitions from a JSON or YAML config file.

    Supports two formats:
      1. New format (dict with 'keywords' and 'negative_keywords' keys):
         {"Web UI": {"keywords": [...], "negative_keywords": [...]}}
      2. Legacy format (list of keyword strings):
         {"Web UI": ["kw1", "kw2"]}

    If config_path is None, returns built-in default themes.
    If config is missing or malformed, falls back to defaults with a warning.
    """
    if config_path is None:
        logging.info("No config file provided; using built-in default themes.")
        return dict(DEFAULT_THEMES)

    if not config_path.exists():
        logging.warning("Config file not found: %s; falling back to built-in defaults.", config_path)
        return dict(DEFAULT_THEMES)

    raw = config_path.read_text(encoding="utf-8")
    config: Dict[str, Any] = {}

    # Try JSON first, then YAML
    try:
        config = json.loads(raw)
    except json.JSONDecodeError:
        if yaml is not None:
            try:
                config = yaml.safe_load(raw)
                if config is None:
                    config = {}
            except yaml.YAMLError as e:
                logging.warning(
                    "Config file %s is not valid YAML: %s; falling back to defaults.",
                    config_path, e,
                )
                return dict(DEFAULT_THEMES)
        else:
            logging.warning(
                "Config file %s is not valid JSON and PyYAML is not installed; "
                "falling back to defaults.",
                config_path,
            )
            return dict(DEFAULT_THEMES)

    themes = config.get("themes")
    if not themes:
        logging.warning(
            "Config file %s has no 'themes' key; falling back to built-in defaults.",
            config_path,
        )
        return dict(DEFAULT_THEMES)

    if not isinstance(themes, dict):
        logging.warning(
            "'themes' must be a dictionary, got %s; falling back to defaults.",
            type(themes).__name__,
        )
        return dict(DEFAULT_THEMES)

    # Normalize: convert legacy format (list of strings) to new format (dict with keywords/negative_keywords)
    normalized: Dict[str, Dict[str, List[str]]] = {}
    for theme_name, theme_data in themes.items():
        if isinstance(theme_data, list):
            # Legacy format: just a list of keywords
            normalized[theme_name] = {
                "keywords": theme_data,
                "negative_keywords": [],
            }
        elif isinstance(theme_data, dict):
            # New format: dict with keywords and optional negative_keywords
            keywords = theme_data.get("keywords", [])
            if not isinstance(keywords, list):
                logging.warning(
                    "Theme '%s' keywords must be a list; skipping.",
                    theme_name,
                )
                continue
            negative = theme_data.get("negative_keywords", [])
            if not isinstance(negative, list):
                negative = []
            normalized[theme_name] = {
                "keywords": keywords,
                "negative_keywords": negative,
            }
        else:
            logging.warning(
                "Theme '%s' has unexpected type %s; skipping.",
                theme_name, type(theme_data).__name__,
            )

    if not normalized:
        logging.warning("No valid themes found in config; falling back to defaults.")
        return dict(DEFAULT_THEMES)

    return normalized


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
# Theme matching (with negative keyword support)
# ------------------------------------------------------------------------------


def match_themes(
    body: str,
    themes: Dict[str, Dict[str, List[str]]],
) -> List[str]:
    """
    Determine which themes match the given body text.

    Uses case-insensitive substring matching. A theme matches if:
      1. At least one positive keyword is found in the body, AND
      2. No negative keywords are found in the body

    Args:
        body: The event body text to scan
        themes: Dict of theme_name -> {"keywords": [...], "negative_keywords": [...]}

    Returns:
        Sorted list of matching theme names
    """
    if not body:
        return []

    body_lower = body.lower()
    matched: List[str] = []

    for theme_name, theme_data in themes.items():
        keywords = theme_data.get("keywords", [])
        negative_keywords = theme_data.get("negative_keywords", [])

        # Check negative keywords first (fast rejection)
        has_negative = any(neg.lower() in body_lower for neg in negative_keywords)
        if has_negative:
            continue

        # Check positive keywords
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
        description="Tag events in a normalised/merged chronicle with theme labels.",
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
        "--dry-run", action="store_true",
        help="Print tagged output to stdout without writing files",
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
    total_keywords = sum(
        len(td.get("keywords", [])) + len(td.get("negative_keywords", []))
        for td in themes.values()
    )
    logging.info(
        "Loaded %d themes with %d total keywords (%d positive, %d negative).",
        len(themes),
        total_keywords,
        sum(len(td.get("keywords", [])) for td in themes.values()),
        sum(len(td.get("negative_keywords", [])) for td in themes.values()),
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
        if not args.dry_run:
            out_path.write_text(original_text, encoding="utf-8")
            logging.info("Output written to %s (unchanged — no events to tag)", out_path)
        else:
            print(original_text)
        return

    # 5. Tag events
    for ev in events:
        ev["themes"] = match_themes(ev["body"], themes)

    # 6. Rebuild tagged markdown
    tagged_md = rebuild_tagged_md(original_text, events)

    # 7. Write output or dry-run
    if args.dry_run:
        print(tagged_md)
        return

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
