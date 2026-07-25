"""Ingest module for the chronicle pipeline.

Pure functions for normalising raw deep-search markdown files into a
standard chronicle format with YAML front-matter and consistent event headings.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import dateutil.parser
import yaml

# ------------------------------------------------------------------------------
# Default mojibake mapping -- only broken multi-byte sequences -> correct chars
# ------------------------------------------------------------------------------
DEFAULT_MOJIBAKE_MAP: dict[str, str] = {
    "â€\x9d": "”",     # right double quote
    "â€“": "–",        # en dash
    "â€”": "—",        # em dash
    "â€™": "’",        # right single quote
    "â€œ": "“",        # left double quote
    "â€˜": "‘",        # left single quote
    "â€¦": "…",        # ellipsis
    "â€¢": "•",        # bullet
    "Ã©": "é",
    "Ã¨": "è",
    "Ã§": "ç",
    "Â°": "°",
    "\xa0": " ",       # non-breaking space
}


def clean_mojibake(text: str) -> str:
    """Replace known encoding artifacts using the built-in mapping."""
    mapping = DEFAULT_MOJIBAKE_MAP
    for pattern, replacement in sorted(mapping.items(), key=lambda x: -len(x[0])):
        text = text.replace(pattern, replacement)
    return text


def extract_source_name(input_path: Path, cli_source: Optional[str]) -> str:
    """Determine source name from CLI argument or filename."""
    if cli_source:
        return cli_source
    stem = input_path.stem
    stem_clean = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
    name = stem_clean.replace("_", " ").replace("-", " ")
    name = re.sub(r"\s+", " ", name).strip().title()
    return name


def extract_title(raw_text: str, source: str) -> str:
    """Derive a title from the first H1, first H2, or source name."""
    match = re.search(r"^#\s+(.+)$", raw_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    match = re.search(r"^##\s+(.+)$", raw_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return f"{source} Incidents"


def find_dates(text: str) -> list[datetime]:
    """Return a sorted list of all dates found in the text."""
    patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ]
    candidates: set[str] = set()
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            candidates.add(m.group().strip())

    dates: list[datetime] = []
    for cand in candidates:
        try:
            dt = dateutil.parser.parse(cand, fuzzy=True, default=datetime(2025, 1, 1))
            if 2022 <= dt.year <= 2027:
                dates.append(dt)
        except (ValueError, OverflowError):
            pass
    return sorted(dates)


def parse_date_range(text: str) -> tuple[Optional[datetime], Optional[datetime]]:
    """Return earliest and latest date found in text."""
    dates = find_dates(text)
    if not dates:
        return None, None
    return dates[0], dates[-1]


def _parse_single_date(date_str: str) -> Optional[str]:
    """Parse a single date string into YYYY-MM-DD format."""
    range_pattern = re.compile(r"^(.+?)\s*[-\u2013-]\s*(\d{1,2})(?:st|nd|rd|th)?\s*$")
    range_match = range_pattern.match(date_str.strip())
    if range_match:
        date_str = range_match.group(1).strip()
    try:
        dt = dateutil.parser.parse(date_str, fuzzy=True, default=datetime(2025, 1, 1))
        if 2022 <= dt.year <= 2027:
            return dt.strftime("%Y-%m-%d")
    except (ValueError, OverflowError):
        pass
    return None


def extract_preamble(text: str, events: list[dict[str, Any]]) -> str:
    """Return the text before the first detected event."""
    if not events:
        lines = text.splitlines()
        content_lines = [l for l in lines if not re.match(r"^#{1,6}\s", l.strip())]
        return "\n".join(content_lines).strip()

    bullet_start = re.search(r"^-\s+\*\*", text, re.MULTILINE)
    if not bullet_start:
        return ""

    before = text[: bullet_start.start()].strip()
    lines = before.splitlines()
    content_lines: list[str] = []
    for l in lines:
        stripped = l.strip()
        if re.match(r"^#{1,6}\s", stripped):
            continue
        if stripped == "" and content_lines and content_lines[-1] == "":
            continue
        content_lines.append(l)
    cleaned = "\n".join(content_lines).strip()
    return cleaned


# Rejection reason codes
REASON_MISSING_EVENT_DATE = "missing_event_date"


def _make_rejection_record(
    input_filename: str,
    event_index: int,
    raw_heading: str,
    rejected_body: str,
    reason_code: str,
    line_number: int = 0,
) -> dict[str, Any]:
    """Build a structured rejection record for an undated event."""
    return {
        "input_file": input_filename,
        "line_number": line_number,
        "event_index": event_index,
        "raw_heading": raw_heading,
        "rejected_body": rejected_body,
        "reason_code": reason_code,
        "reason": "No ISO date or parseable date found in bold heading",
    }


def split_into_events(text: str) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    """Split raw markdown into event blocks based on the actual file structure.

    Returns:
        (events, rejection_records) where:
        - events: list of dicts with keys ``date`` (str YYYY-MM-DD),
          ``title`` (str), ``body`` (str)
        - rejection_records: list of structured rejection dicts for undated events
    """
    period_pattern = re.compile(
        r"^##\s+(January|February|March|April|May|June|July|"
        r"August|September|October|November|December)\s+\d{4}",
        re.IGNORECASE,
    )

    bullet_bold_pattern = re.compile(r"^-\s+\*\*(.+?):\*\*(.*)$", re.DOTALL)

    lines = text.splitlines(keepends=False)
    events: list[dict[str, str]] = []
    rejection_records: list[dict[str, Any]] = []
    current_period = ""
    current_date: Optional[str] = None
    current_title = ""
    current_body: list[str] = []
    event_index = 0

    def _save_current_event() -> None:
        nonlocal current_date, current_title, current_body
        if current_date is not None and (current_body or current_title):
            events.append(
                {
                    "date": current_date,
                    "title": current_title.strip(),
                    "body": "\n".join(current_body).strip(),
                }
            )
        current_date = None
        current_title = ""
        current_body = []

    def _extract_date_and_title(
        bold_content: str,
    ) -> tuple[Optional[str], str]:
        iso_date_match = re.match(
            r"^\s*(\d{4}-\d{2}-\d{2})\s*[-\u2013-]\s*(.+?)\s*$",
            bold_content,
            re.DOTALL,
        )
        if iso_date_match:
            return iso_date_match.group(1), iso_date_match.group(2).strip()

        dash_match = re.match(r"^\s*(.+)\s*[-\u2013-]\s*(.+)\s*$", bold_content, re.DOTALL)
        if dash_match:
            date_candidate = dash_match.group(1).strip()
            title_candidate = dash_match.group(2).strip()
        else:
            date_candidate = None
            title_candidate = bold_content.strip()

        if date_candidate:
            parsed = _parse_single_date(date_candidate)
            if parsed:
                return parsed, title_candidate

        period_date = _parse_single_date(current_period) if current_period else None
        if period_date:
            return period_date, bold_content.strip()

        return None, bold_content.strip()

    for line_idx, line in enumerate(lines):
        stripped = line.strip()
        line_number = line_idx + 1  # 1-indexed

        period_match = period_pattern.match(stripped)
        if period_match:
            _save_current_event()
            current_period = period_match.group(0).strip().lstrip("##").strip()
            continue

        if stripped.startswith("- **") and ":**" in stripped:
            bullet_match = bullet_bold_pattern.match(stripped)
            if bullet_match:
                _save_current_event()
                event_index += 1
                bold_content = bullet_match.group(1).strip()
                body_text = bullet_match.group(2).strip()

                extracted_date, extracted_title = _extract_date_and_title(bold_content)
                if extracted_date is None:
                    rec = _make_rejection_record(
                        input_filename="",
                        event_index=event_index,
                        raw_heading=stripped,
                        rejected_body=body_text,
                        reason_code=REASON_MISSING_EVENT_DATE,
                        line_number=line_number,
                    )
                    rejection_records.append(rec)
                    logging.warning(
                        "Rejected event at line %d: undated heading %r",
                        line_number,
                        bold_content,
                    )
                    continue
                current_date = extracted_date
                current_title = extracted_title
                current_body = [body_text] if body_text else []
                continue

        if current_date is not None:
            current_body.append(line)

    _save_current_event()
    return events, rejection_records


def format_event(event: dict[str, str]) -> str:
    """Render a single event as a normalised markdown block."""
    heading = f"## Event: {event['date']}"
    if event["title"]:
        heading += f" \u2013 {event['title']}"
    return f"{heading}\n\n{event['body']}\n"


def generate_normalised_md(
    source: str,
    title: str,
    date_range: tuple[Optional[datetime], Optional[datetime]],
    events: list[dict[str, str]],
    input_file: str,
    preamble: str = "",
) -> str:
    """Build the full normalised Markdown with YAML front-matter."""
    metadata: dict[str, Any] = {
        "source": source,
        "title": title,
        "input_file": str(Path(input_file).name),
        "event_count": len(events),
    }
    if date_range[0] and date_range[1]:
        if date_range[0] == date_range[1]:
            metadata["date"] = date_range[0].strftime("%Y-%m-%d")
        else:
            metadata["date"] = (
                f"{date_range[0].strftime('%Y-%m-%d')} to "
                f"{date_range[1].strftime('%Y-%m-%d')}"
            )
    elif date_range[0]:
        metadata["date"] = date_range[0].strftime("%Y-%m-%d")
    else:
        metadata["date"] = "unknown"

    frontmatter = yaml.dump(
        metadata, default_flow_style=False, allow_unicode=True, sort_keys=False
    ).strip()

    output = f"---\n{frontmatter}\n---\n\n"
    output += f"# Source: {source}\n\n"
    if preamble:
        output += f"> **Overview:** {preamble}\n\n"
    if not events:
        output += "_(No events extracted)_\n"
    else:
        for event in events:
            output += format_event(event)
    return output
