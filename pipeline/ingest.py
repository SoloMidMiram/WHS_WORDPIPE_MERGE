#!/usr/bin/env python3
"""
ingest.py – Normalise a raw deep‑search .md file into a standard chronicle format.

Produces:
  - YAML front‑matter (source, date range, title, input file)
  - Consistent headers: # Source: <source>   /   ## Event: YYYY-MM-DD – Title
  - Mojibake cleanup (â€“ → –, â€™ → ', …)
  - Hierarchical event segmentation matching actual raw file structure
  - Preamble preservation (content before first event)

The raw files follow this pattern:
  # Title
  ## Month Year
  - **Date range – Event Title:** Description...
  - **Date – Event Title:** Description...
  ## Next Month
  ...

Also handles items without a date prefix:
  - **Community Creativity & Cultural Buzz:** Description...

Usage:
  python ingest.py --input deep_chatgpt_incidents.md --output normalised.md
  python ingest.py --input raw.md --source-name "Reddit"
  python ingest.py --input raw.md --date-override 2025-06 --verbose
"""

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import dateutil.parser
import yaml

# ------------------------------------------------------------------------------
# Default mojibake mapping — only broken multi‑byte sequences → correct chars
# ------------------------------------------------------------------------------
# These are the actual byte‑level encoding artifacts found in deep‑search files.
# Do NOT add already‑correct Unicode characters here (they are harmless but
# confusing). Extend via the `extra_map` parameter if needed.
DEFAULT_MOJIBAKE_MAP = {
    "â€“": "–",        # en dash
    "â€”": "—",        # em dash
    "â€™": "’",        # right single quote
    "â€œ": "“",        # left double quote
    "â€\x9d": "”",     # right double quote (â€ followed by \x9d -> ”)
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
    """Replace known encoding artifacts using the built‑in mapping."""
    mapping = DEFAULT_MOJIBAKE_MAP
    # Apply replacements in order of longest key first to avoid partial matches
    for pattern, replacement in sorted(mapping.items(), key=lambda x: -len(x[0])):
        text = text.replace(pattern, replacement)
    return text


def extract_source_name(input_path: Path, cli_source: Optional[str]) -> str:
    """Determine source name from CLI argument or filename."""
    if cli_source:
        return cli_source
    # Fallback: use stem of file, replace underscores/hyphens, title-case
    stem = input_path.stem
    # Remove leading date pattern like "2025-08-06-" for cleaner name
    stem_clean = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
    name = stem_clean.replace("_", " ").replace("-", " ")
    # Collapse multiple spaces and strip
    name = re.sub(r"\s+", " ", name).strip().title()
    return name


def extract_title(raw_text: str, source: str) -> str:
    """Derive a title from the first H1, first H2, or source name."""
    # 1. Look for H1 heading
    match = re.search(r"^#\s+(.+)$", raw_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # 2. Look for first H2 heading
    match = re.search(r"^##\s+(.+)$", raw_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # 3. Fall back to source name
    return f"{source} Incidents"


def find_dates(text: str) -> List[datetime]:
    """
    Return a sorted list of all dates found in the text.
    Uses a regex to find likely date strings, then dateutil.parser with fuzzy.
    """
    patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",                          # 2025-06-15
        r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",  # 15 June 2025
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",  # June 15, 2025
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",  # June 2025
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",                    # 06/15/2025
    ]
    candidates = set()
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            candidates.add(m.group().strip())

    dates = []
    for cand in candidates:
        try:
            dt = dateutil.parser.parse(cand, fuzzy=True, default=datetime(2025, 1, 1))
            if 2022 <= dt.year <= 2027:
                dates.append(dt)
        except (ValueError, OverflowError):
            pass
    return sorted(dates)


def parse_date_range(text: str) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Return earliest and latest date found in text."""
    dates = find_dates(text)
    if not dates:
        return None, None
    return dates[0], dates[-1]


def _parse_single_date(date_str: str) -> Optional[str]:
    """
    Parse a single date string into YYYY-MM-DD format.
    Handles date ranges like "June 10–11" by taking the start date.
    Returns None if parsing fails.
    """
    # Strip date ranges: take the part before any dash that separates dates
    # e.g., "June 10–11" -> "June 10", "June 10-11" -> "June 10"
    range_pattern = re.compile(
        r"^(.+?)\s*[–—-]\s*(\d{1,2})(?:st|nd|rd|th)?\s*$"
    )
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


def extract_preamble(text: str, events: List[Dict[str, str]]) -> str:
    """
    Return the text before the first detected event.

    The preamble is everything from the start of the cleaned text up to the
    first line that triggered an event boundary. Structural headings (H1, H2)
    that are part of the file's standard layout are excluded — only
    descriptive/introductory paragraphs are kept.

    If no events were found, the entire text is returned as preamble
    (with headings stripped).
    """
    if not events:
        # No events — return entire text with headings stripped
        lines = text.splitlines()
        content_lines = [l for l in lines if not re.match(r"^#{1,6}\s", l.strip())]
        return "\n".join(content_lines).strip()

    # Find the first bullet‑bold line that produced an event
    bullet_start = re.search(r"^-\s+\*\*", text, re.MULTILINE)
    if not bullet_start:
        return ""

    # Get everything before the first bullet
    before = text[:bullet_start.start()].strip()

    # Remove structural headings (H1 title, H2 period headers) from preamble
    # since they are already represented in the YAML front-matter and output.
    lines = before.splitlines()
    content_lines = []
    for l in lines:
        stripped = l.strip()
        # Skip markdown headings of any level
        if re.match(r"^#{1,6}\s", stripped):
            continue
        # Skip blank lines that are only separators
        if stripped == "" and content_lines and content_lines[-1] == "":
            continue
        content_lines.append(l)
    cleaned = "\n".join(content_lines).strip()
    return cleaned


def split_into_events(text: str) -> List[Dict[str, str]]:
    """
    Split the raw markdown into event blocks based on the actual file structure.

    The raw files follow this pattern:
      # Title
      ## Month Year
      - **Date range – Event Title:** Description...
      - **Date – Event Title:** Description...
      ## Next Month
      ...

    Also handles items without a date prefix:
      - **Community Creativity & Cultural Buzz:** Description...

    Returns list of dicts with keys: 'date' (str YYYY-MM-DD), 'title' (str), 'body' (str)
    """
    # Pattern for H2 period headers: ## Month Year
    period_pattern = re.compile(
        r"^##\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}",
        re.IGNORECASE
    )

    # Pattern for any bullet-list item with bold text followed by colon:
    # - **Some Title:** Description...
    # Note: the actual format is **text:** (colon BEFORE closing **), not **text**:
    bullet_bold_pattern = re.compile(
        r"^-\s+\*\*(.+?):\*\*(.*)$",
        re.DOTALL
    )

    lines = text.splitlines(keepends=False)
    events = []
    current_period = ""  # e.g., "June 2025"
    current_date = None
    current_title = ""
    current_body = []

    def _save_current_event():
        """Save the current event being accumulated."""
        nonlocal current_date, current_title, current_body
        if current_date is not None and (current_body or current_title):
            events.append({
                "date": current_date,
                "title": current_title.strip(),
                "body": "\n".join(current_body).strip(),
            })
        current_date = None
        current_title = ""
        current_body = []

    def _extract_date_and_title(bold_content: str) -> Tuple[Optional[str], str]:
        """
        Extract date and title from bold content like:
        - "June 10–11 – Global ChatGPT Outage" -> ("2025-06-10", "Global ChatGPT Outage")
        - "Early June – Letter Spam Glitch" -> (period_date, "Letter Spam Glitch")
        - "Community Creativity & Cultural Buzz" -> (period_date, "Community Creativity & Cultural Buzz")
        """
        # Try to split by dash separator (en-dash, em-dash, or hyphen)
        # Use a greedy match for the date part so date ranges like "June 10-11" are captured fully
        dash_match = re.match(
            r"^\s*(.+)\s*[–—-]\s*(.+)\s*$",
            bold_content,
            re.DOTALL
        )
        if dash_match:
            date_candidate = dash_match.group(1).strip()
            title_candidate = dash_match.group(2).strip()
        else:
            date_candidate = None
            title_candidate = bold_content.strip()

        # Try to parse the date candidate
        if date_candidate:
            parsed = _parse_single_date(date_candidate)
            if parsed:
                return parsed, title_candidate

        # If date parsing failed or there was no dash, try period context
        period_date = _parse_single_date(current_period) if current_period else None
        if period_date:
            return period_date, bold_content.strip()

        return None, bold_content.strip()

    for line in lines:
        stripped = line.strip()

        # Check for H2 period header: ## Month Year
        period_match = period_pattern.match(stripped)
        if period_match:
            _save_current_event()
            current_period = period_match.group(0).strip().lstrip("##").strip()
            continue

        # Check for bullet-list item with bold text: - **text:**
        if stripped.startswith("- **") and ":**" in stripped:
            bullet_match = bullet_bold_pattern.match(stripped)
            if bullet_match:
                _save_current_event()
                bold_content = bullet_match.group(1).strip()
                body_text = bullet_match.group(2).strip()

                extracted_date, extracted_title = _extract_date_and_title(bold_content)
                current_date = extracted_date or "unknown"
                current_title = extracted_title
                current_body = [body_text] if body_text else []
                continue

        # If we're inside an event, accumulate body lines
        if current_date is not None:
            current_body.append(line)

    # Append last event
    _save_current_event()

    return events


def format_event(event: Dict[str, str]) -> str:
    """Render a single event as a normalised markdown block."""
    heading = f"## Event: {event['date']}"
    if event["title"]:
        heading += f" – {event['title']}"
    return f"{heading}\n\n{event['body']}\n"


def generate_normalised_md(
    source: str,
    title: str,
    date_range: Tuple[Optional[datetime], Optional[datetime]],
    events: List[Dict[str, str]],
    input_file: str,
    preamble: str = "",
) -> str:
    """Build the full normalised Markdown with YAML front-matter."""
    metadata = {
        "source": source,
        "title": title,
        "input_file": str(Path(input_file).name),
        "event_count": len(events),
    }
    if date_range[0] and date_range[1]:
        if date_range[0] == date_range[1]:
            metadata["date"] = str(date_range[0].strftime("%Y-%m-%d"))
        else:
            metadata["date"] = str(f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}")
    elif date_range[0]:
        metadata["date"] = str(date_range[0].strftime("%Y-%m-%d"))
    else:
        metadata["date"] = "unknown"

    frontmatter = yaml.dump(metadata, default_flow_style=False, allow_unicode=True, sort_keys=False).strip()

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


def main():
    parser = argparse.ArgumentParser(
        description="Normalise a raw deep-search MD file for the chronicle pipeline."
    )
    parser.add_argument("--input", "-i", required=True, help="Path to raw .md file")
    parser.add_argument("--output", "-o", help="Path for normalised output (default: <stem>_normalised.md)")
    parser.add_argument("--source-name", help="Override source name (otherwise derived from filename)")
    parser.add_argument("--date-override", help="Force a date (YYYY-MM-DD or YYYY-MM) when file has no parseable dates")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s: %(message)s")

    # 1. Read raw file
    input_path = Path(args.input)
    if not input_path.exists():
        logging.error("Input file not found: %s", input_path)
        sys.exit(1)
    raw_text = input_path.read_text(encoding="utf-8")

    # 2. Clean mojibake (always on)
    cleaned_text = clean_mojibake(raw_text)

    # 3. Extract source name
    source = extract_source_name(input_path, args.source_name)

    # 4. Extract overall title
    title = extract_title(cleaned_text, source)

    # 5. Determine date range (for metadata)
    date_start, date_end = parse_date_range(cleaned_text)
    if date_start is None:
        if args.date_override:
            try:
                forced_dt = dateutil.parser.parse(args.date_override, fuzzy=True, default=datetime(2025, 1, 1))
                if forced_dt.year < 2022 or forced_dt.year > 2027:
                    logging.warning("Override date year %d seems out of range; using anyway.", forced_dt.year)
                date_start = date_end = forced_dt
                logging.info("Date overridden to %s", forced_dt.strftime("%Y-%m-%d"))
            except (ValueError, OverflowError) as e:
                logging.error("Cannot parse --date-override value '%s': %s", args.date_override, e)
                sys.exit(1)
        else:
            logging.warning("No dates found in content; date will be 'unknown'.")

    # 6. Split into events
    events = split_into_events(cleaned_text)
    logging.info("Extracted %d events.", len(events))

    # 7. Extract preamble (content before first event)
    preamble = extract_preamble(cleaned_text, events)

    # 8. Generate normalised MD
    normalised_md = generate_normalised_md(
        source=source,
        title=title,
        date_range=(date_start, date_end),
        events=events,
        input_file=str(input_path),
        preamble=preamble,
    )

    # 9. Write output
    if args.output:
        out_path = Path(args.output)
    else:
        out_stem = input_path.stem + "_normalised"
        out_path = input_path.with_name(out_stem + ".md")
    out_path.write_text(normalised_md, encoding="utf-8")
    logging.info("Normalised file written to %s", out_path)


if __name__ == "__main__":
    main()
