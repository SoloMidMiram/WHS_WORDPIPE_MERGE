"""Categorize module for the chronicle pipeline (v2).

Pure functions for tagging chronicle events with theme labels,
supporting negative keyword filtering and legacy format compatibility.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# ------------------------------------------------------------------------------
# Built-in default themes (used when no --config is provided)
# ------------------------------------------------------------------------------
DEFAULT_THEMES: dict[str, list[str] | dict[str, list[str]]] = {
    "Web UI": ["chat.openai.com", "chatgpt.com", "web interface", "browser",
               "UI freeze", "button disappeared", "interface", "web app"],
    "API/Developer": ["api.openai.com", "ChatGPT API", "playground", "code interpreter",
                      "function calling", "API", "developer", "endpoint", "rate limit",
                      "token", "GPT-4 API"],
    "Outages": ["down", "outage", "downtime", "unreachable", "503 error",
                "service disruption", "error", "unavailable", "crash"],
    "Jailbreaks/Exploits": ["jailbreak", "DAN", "prompt injection", "bypass",
                            "ignore previous instructions", "exploit", "prompt leak"],
    "Memory/Personalisation": ["memory", "custom instructions", "bio", "personalised",
                                "remembers", "personalisation"],
    "Culture/Virality": ["viral", "Twitter", "Reddit", "meme", "social media",
                         "went viral", "community"],
}

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------
EVENT_HEADING_RE = re.compile(
    r"^(## Event:\s*\d{4}-\d{2}-\d{2}(?:\s*[–-]\s*.*?)?)\s*$",
    re.MULTILINE,
)


# ------------------------------------------------------------------------------
# Config loading (v2: supports negative_keywords)
# ------------------------------------------------------------------------------


def load_themes(config_path: Path | None) -> dict[str, list[str]]:
    """Load theme definitions from JSON/YAML config file or return built-in defaults.

    v2 enhancement: supports ``negative_keywords`` per theme.
    Legacy format (``{"Theme": ["kw1", "kw2"]}``) is still accepted.
    """
    if config_path is None:
        logging.info("No config file provided; using built-in default themes.")
        return _normalise_themes(DEFAULT_THEMES)

    if not config_path.exists():
        logging.error("Config file not found: %s", config_path)
        sys.exit(1)

    raw = config_path.read_text(encoding="utf-8")
    config: dict[str, Any] = {}

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
        return _normalise_themes(DEFAULT_THEMES)

    if not isinstance(themes, dict):
        logging.error("'themes' must be a dictionary, got %s.", type(themes).__name__)
        sys.exit(1)

    return _normalise_themes(themes)


def _normalise_themes(themes: dict[str, Any]) -> dict[str, list[str]]:
    """Normalise theme definitions: accept both legacy list-of-strings and v2 dict format."""
    normalised: dict[str, list[str]] = {}
    for name, value in themes.items():
        if isinstance(value, list):
            # Legacy format: just keywords
            if not all(isinstance(kw, str) for kw in value):
                logging.error("Theme '%s' contains non-string entries.", name)
                sys.exit(1)
            normalised[name] = list(value)
        elif isinstance(value, dict):
            # v2 format: {"keywords": [...], "negative_keywords": [...]}
            kw = value.get("keywords", [])
            if not isinstance(kw, list) or not all(isinstance(k, str) for k in kw):
                logging.error("Theme '%s' has invalid 'keywords' list.", name)
                sys.exit(1)
            normalised[name] = list(kw)
        else:
            logging.error("Theme '%s' must map to a list or dict, got %s.", name, type(value).__name__)
            sys.exit(1)
    return normalised


def _load_negative_keywords(config_path: Path | None) -> dict[str, list[str]]:
    """Load negative keywords from config (used to reduce false positives)."""
    if config_path is None:
        return {}

    if not config_path.exists():
        return {}

    raw = config_path.read_text(encoding="utf-8")
    config: dict[str, Any] = {}

    try:
        config = json.loads(raw)
    except json.JSONDecodeError:
        try:
            config = yaml.safe_load(raw)
            if config is None:
                config = {}
        except yaml.YAMLError:
            return {}

    themes = config.get("themes")
    if not isinstance(themes, dict):
        return {}

    neg: dict[str, list[str]] = {}
    for name, value in themes.items():
        if isinstance(value, dict):
            nk = value.get("negative_keywords", [])
            if isinstance(nk, list) and all(isinstance(k, str) for k in nk):
                neg[name] = list(nk)
    return neg


# ------------------------------------------------------------------------------
# Event extraction
# ------------------------------------------------------------------------------


def extract_events(md_body: str) -> list[dict[str, str]]:
    """Split the markdown body into event blocks.

    Returns list of dicts with keys: date, title, heading_line, block, body.
    """
    events: list[dict[str, str]] = []
    matches = list(EVENT_HEADING_RE.finditer(md_body))

    if not matches:
        return events

    for i, match in enumerate(matches):
        heading_line = match.group(1).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_body)
        raw_block = md_body[start:end].strip()

        date_title_match = re.match(
            r"^## Event:\s*(\d{4}-\d{2}-\d{2})(?:\s*[–-]\s*(.*))?$",
            heading_line,
        )
        date = date_title_match.group(1) if date_title_match else "unknown"
        title = (date_title_match.group(2) or "").strip() if date_title_match else ""

        newline_pos = raw_block.find("\n")
        body = raw_block[newline_pos:].strip() if newline_pos >= 0 else ""

        events.append({
            "date": date,
            "title": title,
            "heading_line": heading_line,
            "block": raw_block,
            "body": body,
        })

    return events


# ------------------------------------------------------------------------------
# Theme matching (v2: with negative keyword filtering)
# ------------------------------------------------------------------------------


def match_themes(
    body: str,
    themes: dict[str, list[str]],
    negative_keywords: dict[str, list[str]] | None = None,
) -> list[str]:
    """Determine which themes match the given body text.

    Uses case-insensitive substring matching. If ``negative_keywords`` are
    provided for a theme, the body must NOT contain any of those keywords
    for the theme to match.
    """
    if not body:
        return []

    neg = negative_keywords or {}
    body_lower = body.lower()
    matched: list[str] = []

    for theme_name, keywords in themes.items():
        for kw in keywords:
            if kw.lower() in body_lower:
                # Check negative keywords
                neg_kws = neg.get(theme_name, [])
                if any(nk.lower() in body_lower for nk in neg_kws):
                    continue  # negative match -- skip this theme
                matched.append(theme_name)
                break

    return sorted(matched)


# ------------------------------------------------------------------------------
# Output assembly
# ------------------------------------------------------------------------------


def rebuild_tagged_md(original_text: str, events: list[dict[str, Any]]) -> str:
    """Reconstruct full markdown with ``<!-- themes: ... -->`` comments inserted."""
    body_start = 0
    if original_text.startswith("---"):
        parts = original_text.split("---", 2)
        if len(parts) >= 3:
            body_start = original_text.index(parts[2])

    preamble = original_text[:body_start]
    body = original_text[body_start:]

    tagged_blocks: list[str] = []
    for ev in events:
        raw = ev["block"]
        if ev.get("themes"):
            heading = ev["heading_line"]
            comment = f"<!-- themes: {', '.join(ev['themes'])} -->"
            newline_pos = raw.find("\n")
            rest = raw[newline_pos:] if newline_pos >= 0 else ""
            tagged_blocks.append(f"{heading}\n{comment}{rest}")
        else:
            tagged_blocks.append(raw)

    return preamble + "\n\n".join(tagged_blocks) + "\n"


def build_sidecar_json(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build sidecar JSON with per-event tag data."""
    return [
        {"date": ev["date"], "title": ev["title"], "themes": ev.get("themes", [])}
        for ev in events
    ]
