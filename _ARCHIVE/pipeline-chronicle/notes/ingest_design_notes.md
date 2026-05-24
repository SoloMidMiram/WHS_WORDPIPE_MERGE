### 1. **`ingest.py`** — **Highest priority**  
*Milestone A1 → A2*  
Converts a single raw deep‑search file into a standard Markdown file with:
- extracted title, date, source attribution
- consistent headers (e.g., `# Source: xxx`, `## Event: yyy`)
- a metadata YAML front‑matter block

**Switches**:
--input deepsearch.txt
--output date-event-slug.md
--config config.json # to read ontology for header hints
--source-name "ChatGPT Reddit" # override auto-detection
--date-format "%Y-%m-%d"
--metadata-only # only extract metadata, no full conversion

text

It's part of the pipeline-chronicle. I need to write a Python script that implements that. The deep-search file is likely a markdown with multiple incidents, each with a date and description. Or maybe it's just a collection of reports? The summary says "Raw deep-search .md files" as input, so maybe it's already markdown but needs normalization. The ingest.py will parse each section, extract date (from filename or content), add YAML front-matter, standardize headers, clean mojibake.

I should write a robust Python script with argparse, using libraries like yaml, re, hashlib, pathlib, dateutil maybe for date parsing.

The script will:
- Accept --input (required) path to the raw .md file.
- --output (optional) path to normalized .md file; if not given, generate from input name with normalized prefix.
- --config (optional) JSON config file; if provided, load ontology (maybe for validation but primary use is later).
- --source-name (optional) to override source detection (maybe from filename).
- --date-format (optional) default "%Y-%m-%d" to interpret dates in file.
- --metadata-only flag: if set, only output metadata (JSON?) not full conversion. I'll output a JSON with extracted info.

Processing steps:
1. Read raw .md file.
2. Apply mojibake fixes: replace known patterns (â€“ → –, â€™ → ’, etc.) using a mapping from config or hardcoded defaults.
3. Extract metadata:
   - Title: maybe from first top-level heading (e.g., "# ChatGPT Deep Search" or filename).
   - Date: find a date pattern within the content (like "June 2025", "2025-06-15") or from filename (if it contains date). Use dateutil.parser to parse. If multiple, pick earliest or most prominent? Spec says "date" (singular) for the whole file. If multiple incidents, maybe later pipeline will split by event; but ingest.py deals with one file that might contain many events. Perhaps the file is a collection of incidents from one source for a period. Then the metadata should reflect the source and overall date range. But the output is a normalized MD that will be split? The pipeline expects merge.py to combine multiple normalized MDs, each representing a source's contribution. So ingest.py normalizes an entire source file, extracting a high-level title and date (maybe the date range of content) and source. Then the file itself may contain multiple sections with individual incident dates. The YAML front-matter could include `date: "2025-06"` or a date range. The header pattern `# Source: source-name` and `## Event: ...` suggests that the normalized MD will have a top-level heading for source and second-level headings for each incident. That implies that the raw deep-search file might be structured with multiple events; ingest.py will parse them, clean them, and restructure them into a consistent format.

Based on that, I'll implement ingest.py to:
- Parse the raw MD, detect sections (maybe by dates or separators).
- For each section, extract event date, title/description, and content.
- Output a single MD with:
   - YAML front-matter containing `source`, `date` (overall range or single date), `title`, `input_file`.
   - Top-level heading `# Source: {source}`
   - For each event: `## Event: {date} - {title}` or similar, with event content.
- Also handle mojibake globally.

The script should be flexible and configurable.

Implementation details:

- Use `re` to find sections. Could be lines starting with "**Date:**" or "### 2025-..." etc. I can assume the raw deep-search format from earlier mention: The "ChatGPT_Incidents_Merged.md" (manual merge) likely has a structure we can mimic. The ingest.py should normalize to something similar. The merged manual file has sections like:
June 2025
[Specific incident title] (Date)
...

text
But that manual file may have been structured differently. The pipeline's goal is to automate what was done manually. So we can standardize: each incident gets `## Event: [date] – [title]` with content.

But I don't have the exact format of the raw deep-search files. I'll make ingest.py robust enough to extract any date-like patterns and group content accordingly. I'll use a heuristic: split by lines that start with a date pattern (e.g., `## 2025-06-15` or `**2025-06-15**`). The script can attempt to detect the structure and reorganize.

Alternatively, the raw deep-search file might just be a collection of paragraphs with dates embedded. I'll need a flexible extraction: look for date patterns and use them as event boundaries. If none, treat the whole file as one event.

I'll write the script with these steps:

1. Load config (optional) for mojibake mapping, theme keywords (not needed now), and date formats.
2. Read input.
3. Apply text normalization (mojibake, unicode).
4. Extract source name: from --source-name, or guess from filename (remove path and extension, maybe clean up).
5. Determine overall date or date range: parse all found dates, take min and max; if only one, use that.
6. Split file into events based on date patterns: Scan for lines that are dates, treat them as start of new event. For each event, capture header (date line) and body until next event start.
7. For each event, clean up the date line to extract a clean title (remove asterisks, hashes, etc.). Create a normalized heading: `## Event: YYYY-MM-DD – Cleaned Title` (if title present else just date). The title could be the rest of the line after the date.
8. Assemble YAML front-matter with source, date (range), title (maybe filename derived), and number of events.
9. Write output.

If --metadata-only, skip assembling full MD and just output JSON with extracted info.

Now I'll produce the code, with comments. The mojibake mapping: from the earlier context, patterns like â€™ → ', â€œ → “, â€\x9d → ”, â€“ → –, â€” → —. I'll include a default mapping.

Edge cases: Dates like "June 2025" might be month-only. dateutil can parse "June 2025" giving 2025-06-01. I'll use `dateutil.parser.parse` with `fuzzy=True` to extract dates from strings, but for splitting I might need a regex that matches common date patterns (YYYY-MM-DD, "Month DD, YYYY", etc.) to identify lines that are dates. I'll craft a regex that captures ISO and named month formats.

The script should be in `tools/pipeline-chronicle/ingest.py`. I'll write it as a standalone script with argparse.

I'll also include a main guard and logging.

Now I'll write the response.
I'll write ingest.py as a self‑contained tool, following the spec and handling mojibake, date extraction, and event splitting.

python
#!/usr/bin/env python3
"""
ingest.py – Normalise a raw deep‑search .md file into a standard chronicle format.

Produces:
  - YAML front‑matter (source, date range, title, input file)
  - Consistent headers: # Source: <source>   /   ## Event: YYYY-MM-DD – Title
  - Mojibake cleanup (â€“ → –, â€™ → ', …)
  - Date‑based event segmentation

Usage:
  python ingest.py --input deep_chatgpt_incidents.md --output normalised.md
  python ingest.py --input raw.md --source-name "Reddit" --metadata-only
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import dateutil.parser
import yaml

# ------------------------------------------------------------------------------
# Default mojibake mapping (extendable via config)
# ------------------------------------------------------------------------------
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
    "\u2013": "–",     # sometimes already correct but keep for consistency
    "\u2014": "—",
    "\u2018": "‘",
    "\u2019": "’",
    "\u201c": "“",
    "\u201d": "”",
    "\u2026": "…",
    "\u2022": "•",
}


def load_config(path: Optional[str]) -> Dict:
    """Load a JSON configuration file, falling back to empty dict."""
    if path is None:
        return {}
    config_file = Path(path)
    if not config_file.exists():
        logging.warning("Config file %s not found; using defaults.", config_file)
        return {}
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config


def clean_mojibake(text: str, extra_map: Optional[Dict[str, str]] = None) -> str:
    """Replace known encoding artifacts."""
    mapping = DEFAULT_MOJIBAKE_MAP.copy()
    if extra_map:
        mapping.update(extra_map)
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
    name = stem.replace("_", " ").replace("-", " ")
    # If name looks like "ChatGPT_incidents_2025", keep meaningful part
    return name.strip().title()


def extract_title(raw_text: str, source: str) -> str:
    """Derive a title from the first H1 heading or source."""
    match = re.search(r"^#\s+(.+)$", raw_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # If no H1, use the source name as title
    return f"{source} Incidents"


def find_dates(text: str) -> List[datetime]:
    """
    Return a sorted list of all dates found in the text.
    Uses a regex to find likely date strings, then dateutil.parser with fuzzy.
    """
    # Regex patterns that capture dates (ISO, Month Day, Year, Month Year, etc.)
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
            # Ensure year is reasonable (2022-2027)
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


def split_into_events(text: str) -> List[Dict[str, str]]:
    """
    Split the raw markdown into event blocks based on date line heuristics.
    Returns list of dicts with keys: 'date' (str YYYY-MM-DD), 'title' (str), 'body' (str)
    """
    # Heuristic: a line that starts with a date pattern (or markdown header+date)
    # acts as event separator.
    # We'll search for lines that match: optional #s, optional **, then a date pattern,
    # possibly followed by a dash and title.
    # Regex for a date-like start (simplified):
    date_line_pattern = re.compile(
        r"^(?:#{1,3}\s+)?(?:\*{0,2})?"                         # optional markdown heading or bold
        r"("
        r"\d{4}-\d{2}-\d{2}"                                   # ISO
        r"|(?:\d{1,2}\s+)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}"
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}"
        r"|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}"
        r"|(?:\d{1,2}/\d{1,2}/\d{2,4})"
        r")"
        r"(?:\s*[-–—]\s*(.*))?$",                              # optional dash + title
        re.IGNORECASE
    )

    lines = text.splitlines(keepends=True)
    events = []
    current_date = None
    current_title = ""
    current_body = []

    for line in lines:
        match = date_line_pattern.match(line)
        if match:
            # Save previous event if exists
            if current_date and (current_body or current_title):
                events.append({
                    "date": current_date,
                    "title": current_title.strip(),
                    "body": "".join(current_body).strip(),
                })
            # Start new event
            date_str = match.group(1)
            title_str = match.group(2) or ""
            try:
                dt = dateutil.parser.parse(date_str, fuzzy=True, default=datetime(2025, 1, 1))
                current_date = dt.strftime("%Y-%m-%d")
            except (ValueError, OverflowError):
                # If parsing fails, skip this as a date line, treat as regular content
                current_body.append(line)
                continue
            current_title = title_str.strip()
            current_body = []
        else:
            # If we haven't started any event yet, consider everything before first date as preamble (skip)
            if current_date is None:
                # optionally we could collect a preamble, but for now discard
                pass
            else:
                current_body.append(line)

    # Append last event
    if current_date and (current_body or current_title):
        events.append({
            "date": current_date,
            "title": current_title.strip(),
            "body": "".join(current_body).strip(),
        })

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
) -> str:
    """Build the full normalised Markdown with YAML front-matter."""
    # Prepare YAML metadata
    metadata = {
        "source": source,
        "title": title,
        "input_file": str(Path(input_file).name),
        "event_count": len(events),
    }
    if date_range[0] and date_range[1]:
        if date_range[0] == date_range[1]:
            metadata["date"] = date_range[0].strftime("%Y-%m-%d")
        else:
            metadata["date"] = f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}"
    elif date_range[0]:
        metadata["date"] = date_range[0].strftime("%Y-%m-%d")
    else:
        metadata["date"] = "unknown"

    frontmatter = yaml.dump(metadata, default_flow_style=False, allow_unicode=True, sort_keys=False).strip()

    output = f"---\n{frontmatter}\n---\n\n"
    output += f"# Source: {source}\n\n"
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
    parser.add_argument("--config", "-c", help="JSON config file (e.g., pipeline/config.json)")
    parser.add_argument("--source-name", help="Override source name (otherwise derived from filename)")
    parser.add_argument("--date-format", default="%Y-%m-%d", help="Output date format (not currently used for splitting)")
    parser.add_argument("--metadata-only", action="store_true", help="Output only metadata as JSON, skip MD conversion")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s: %(message)s")

    # 1. Load config if provided
    config = load_config(args.config)
    mojibake_extra = config.get("mojibake_map", {})
    # Optionally we could get date_format from config, but CLI overrides.

    # 2. Read raw file
    input_path = Path(args.input)
    if not input_path.exists():
        logging.error("Input file not found: %s", input_path)
        sys.exit(1)
    raw_text = input_path.read_text(encoding="utf-8")

    # 3. Clean mojibake
    cleaned_text = clean_mojibake(raw_text, mojibake_extra)

    # 4. Extract source name
    source = extract_source_name(input_path, args.source_name)

    # 5. Extract overall title
    title = extract_title(cleaned_text, source)

    # 6. Determine date range (for metadata)
    date_start, date_end = parse_date_range(cleaned_text)
    if date_start is None:
        logging.warning("No dates found in content; date will be 'unknown'.")

    # 7. Split into events
    events = split_into_events(cleaned_text)
    logging.info("Extracted %d events.", len(events))

    if args.metadata_only:
        # Output JSON with extracted info
        meta_output = {
            "source": source,
            "title": title,
            "date_start": date_start.strftime("%Y-%m-%d") if date_start else None,
            "date_end": date_end.strftime("%Y-%m-%d") if date_end else None,
            "event_count": len(events),
            "input_file": str(input_path.name),
        }
        print(json.dumps(meta_output, indent=2, ensure_ascii=False))
        return

    # 8. Generate normalised MD
    normalised_md = generate_normalised_md(
        source=source,
        title=title,
        date_range=(date_start, date_end),
        events=events,
        input_file=str(input_path),
    )

    # 9. Determine output path
    if args.output:
        out_path = Path(args.output)
    else:
        out_stem = input_path.stem + "_normalised"
        out_path = input_path.with_name(out_stem + ".md")
    out_path.write_text(normalised_md, encoding="utf-8")
    logging.info("Normalised file written to %s", out_path)


if __name__ == "__main__":
    main()