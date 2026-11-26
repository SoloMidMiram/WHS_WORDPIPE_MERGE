#!/usr/bin/env python3
"""Generic Markdown section adapter for the Chronicle pipeline.

Converts any folder of long-form Markdown files into staged
Chronicle-compatible input by splitting each file into sections
at ``##`` / ``###`` headings and extracting dates.

Usage:
    python tools/prepare_generic_markdown_chronicle.py <command> [options]

Commands:
    prepare   --input-dir DIR --output-dir DIR --metrics FILE
    summarize --run-dir DIR --prepare-metrics FILE --performance FILE --run-log FILE
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

# The standalone CLI recognizes these names without importing WordPipe.
LEGACY_MODE = "legacy-v1"
STRUCTURAL_MODE = "structural-v1"
MARKDOWN_MODES = (LEGACY_MODE, STRUCTURAL_MODE)
DEFAULT_FALLBACK_DATE = "2026-07-16"
EVENT_LINEAGE_FILENAME = "event_lineage.json"
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
SECTION_HEADING_RE = re.compile(r"^(?P<marks>#{2,4})\s+(?P<title>.+?)\s*$", re.MULTILINE)
# Matches the bold-bullet format that the InsuranceChatbot adapter uses
# so existing Chronicle ingest can parse it identically.
BULLET_TITLE_RE = re.compile(r"^-\s+\*\*(?P<title>.+?):\*\*\s*(?P<body>.*)$", re.MULTILINE)


@dataclass(frozen=True)
class ChronicleEvent:
    date: str
    title: str
    body: str


def sanitize_title(title: str) -> str:
    """Keep event titles compact and safe for a markdown heading."""
    title = re.sub(r"\s+", " ", title).strip()
    title = title.strip("#`*_[]() ")
    return title[:180] if len(title) > 180 else title


def first_date(text: str, fallback: str = DEFAULT_FALLBACK_DATE) -> str:
    match = DATE_RE.search(text)
    return match.group(1) if match else fallback


def split_sections(text: str, heading_levels: Iterable[int]) -> list[tuple[str, str]]:
    """Split markdown into non-empty sections for selected heading levels."""
    levels = {int(level) for level in heading_levels}
    matches = [
        m for m in SECTION_HEADING_RE.finditer(text)
        if len(m.group("marks")) in levels
    ]
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        title = match.group("title")
        body = text[start:end].strip()
        if body:
            sections.append((title, body))
    return sections


def _start_line(text: str, offset: int) -> int:
    return text[:offset].count("\n") + 1


def source_label(filename: str) -> str:
    """Derive a short readable label from a filename for title prefixing."""
    stem = Path(filename).stem
    # Remove leading date prefixes like "2025-08-06-" or "2025-08-06 "
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}[-.\s]+", "", stem)
    # Convert underscores/hyphens to spaces, title-case
    stem = stem.replace("_", " ").replace("-", " ").strip()
    # Keep it short
    if len(stem) > 40:
        stem = stem[:40].rstrip()
    return stem


def parse_file(
    path: Path,
    heading_levels: tuple[int, ...] = (2,),
) -> tuple[list[ChronicleEvent], list[dict[str, object]], int]:
    """Parse a single markdown file into Chronicle events + raw lineage.

    Each matching heading is a candidate (including empty bodies). Empty
    sections advance ``candidate_ordinal`` but are omitted from emit/lineage.
    """
    text = path.read_text(encoding="utf-8")
    fallback_date = first_date(text)
    levels = {int(level) for level in heading_levels}
    matches = [
        m for m in SECTION_HEADING_RE.finditer(text)
        if len(m.group("marks")) in levels
    ]
    prefix = source_label(path.name)

    events: list[ChronicleEvent] = []
    lineage: list[dict[str, object]] = []
    staged_ordinal = 0
    for index, match in enumerate(matches):
        candidate_ordinal = index + 1
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        title = match.group("title")
        body = text[start:end].strip()
        if not body:
            continue
        staged_ordinal += 1
        event_date = first_date(f"{title}\n{body}", fallback_date)
        event_title = f"{prefix} - {sanitize_title(title)}" if prefix else sanitize_title(title)
        trimmed = event_title[:180]
        events.append(ChronicleEvent(date=event_date, title=trimmed, body=body))
        lineage.append({
            "locator_kind": "markdown_section",
            "source_file": path.name,
            "candidate_ordinal": candidate_ordinal,
            "heading_level": len(match.group("marks")),
            "original_heading_text": title.strip(),
            "staged_event_ordinal": staged_ordinal,
            "date": event_date,
            "title": trimmed,
            "start_line": _start_line(text, match.start()),
        })

    return events, lineage, len(matches)


def parse_structural_file(path: Path, heading_levels: tuple[int, ...] = (2,)):
    from wordpipe.chronicle.markdown_sections import SourceLines, section_boundaries

    source = SourceLines.from_bytes(path.read_bytes())
    frontmatter_end, diagnostic, headings, fences = section_boundaries(source, heading_levels)
    spans = []
    candidates = []
    events = []
    lineage = []
    prefix = source_label(path.name)

    def record_span(kind, start, end):
        if end > start:
            spans.append({"kind": kind, **source.span(start, end)})

    record_span("frontmatter", 0, frontmatter_end)
    first_heading = headings[0][0] if headings else len(source.lines)
    record_span("preamble", frontmatter_end, first_heading)
    file_date = DATE_RE.search(source.text)
    for ordinal, (start, heading_end, level, title) in enumerate(headings, 1):
        end = headings[ordinal][0] if ordinal < len(headings) else len(source.lines)
        body = "".join(source.lines[heading_end:end]).strip()
        record_span("heading", start, heading_end)
        record_span("body" if body else "empty_body", heading_end, end)
        candidate = {
            "candidate_ordinal": ordinal,
            "heading_level": level,
            "original_heading_text": title,
            "heading_span": source.span(start, heading_end),
            "section_span": source.span(start, end),
            "staged_event_ordinal": None,
        }
        candidates.append(candidate)
        if not body:
            continue
        section_date = DATE_RE.search(f"{title}\n{body}")
        date = (section_date or file_date)
        date_role = "section" if section_date else "file_fallback" if file_date else "default"
        ordering_date = date.group(1) if date else DEFAULT_FALLBACK_DATE
        event_title = (f"{prefix} - {sanitize_title(title)}" if prefix else sanitize_title(title))[:180]
        events.append(ChronicleEvent(ordering_date, event_title, body))
        candidate.update(staged_event_ordinal=len(events), date=ordering_date, date_role=date_role)
        lineage.append({
            **candidate,
            "locator_kind": "markdown_section",
            "source_file": path.name,
            "title": event_title,
            "start_line": start + 1,
            "source_sha256": source.sha256,
        })
    return events, lineage, {
        "source_file": path.name,
        "source_sha256": source.sha256,
        "byte_count": source.offsets[-1],
        "line_count": len(source.lines),
        "spans": spans,
        "candidates": candidates,
        "fences": [source.span(start, end) for start, end in fences],
        "diagnostics": [{"code": diagnostic, **source.span(0, 1)}] if diagnostic else [],
    }


def render_staged_markdown(source_title: str, events: list[ChronicleEvent]) -> str:
    """Render events in the Chronicle-compatible staged format."""
    lines = [f"# {source_title}", ""]
    current_month: tuple[int, int] | None = None
    for event in events:
        parsed_date = datetime.strptime(event.date, "%Y-%m-%d")
        event_month = (parsed_date.year, parsed_date.month)
        if event_month != current_month:
            lines.extend([f"## {parsed_date.strftime('%B %Y')}", ""])
            current_month = event_month
        body = escape_nested_event_bullets(event.body.strip()) or "_No body supplied._"
        lines.append(f"- **{event.date} - {event.title}:** {body}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def escape_nested_event_bullets(body: str) -> str:
    """Prevent original bold bullets from being mistaken for new top-level events."""
    escaped: list[str] = []
    for line in body.splitlines():
        if line.lstrip().startswith("- **") and ":**" in line:
            indent_len = len(line) - len(line.lstrip())
            line = f"{line[:indent_len]}* {line.lstrip()[2:]}"
        escaped.append(line)
    return "\n".join(escaped)


def source_metrics(files: Sequence[Path]) -> dict[str, int]:
    """Compute input metrics for sources actually consumed by the adapter."""
    total_bytes = 0
    total_lines = 0
    for path in files:
        raw = path.read_bytes()
        total_bytes += len(raw)
        total_lines += path.read_text(encoding="utf-8").count("\n") + 1
    return {
        "input_file_count": len(files),
        "input_total_bytes": total_bytes,
        "input_total_lines": total_lines,
    }


def prepare(
    input_dir: Path, output_dir: Path, metrics_path: Path, *, markdown_mode: str = LEGACY_MODE,
    heading_levels: tuple[int, ...] = (2,),
) -> dict[str, object]:
    input_dir = input_dir.resolve()
    if markdown_mode not in MARKDOWN_MODES:
        raise ValueError(f"unsupported Markdown mode: {markdown_mode!r}")
    structural = markdown_mode == STRUCTURAL_MODE
    if not heading_levels or any(level not in range(2, 7) for level in heading_levels):
        raise ValueError("heading levels must be in 2–6")
    if not structural and heading_levels != (2,):
        raise ValueError("the legacy prepare CLI uses level 2")
    lineage_path = metrics_path.parent / EVENT_LINEAGE_FILENAME
    if structural:
        from wordpipe.chronicle.markdown_sections import STRUCTURAL_RAW_SCHEMA, parser_provenance

        provenance = parser_provenance(heading_levels)
        output_dir = output_dir.resolve()
        run_dir = output_dir.parent
        if (
            metrics_path.resolve() != run_dir / "prepare_metrics.json"
            or input_dir.is_relative_to(run_dir)
            or run_dir.is_relative_to(input_dir)
            or not run_dir.is_dir()
            or any(path.name != "run.log" for path in run_dir.iterdir())
        ):
            raise ValueError("structural prepare requires a fresh run directory separate from input")
    output_dir.mkdir(parents=True, exist_ok=not structural)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    staged_files: list[str] = []
    source_lineage: list[dict[str, object]] = []
    event_lineage: list[dict[str, object]] = []
    source_accounting = []
    total_staged = 0
    total_candidates = 0
    file_metrics: dict[str, dict[str, object]] = {}

    md_files = sorted(input_dir.glob("*.md"))
    for idx, md_file in enumerate(md_files):
        if structural:
            events, file_lineage, accounting = parse_structural_file(md_file, heading_levels)
            candidates = len(accounting["candidates"])
            source_accounting.append(accounting)
        else:
            events, file_lineage, candidates = parse_file(md_file, heading_levels=(2,))
        total_candidates += candidates
        total_staged += len(events)

        stem = md_file.stem
        filename = f"{idx + 1:02d}_{stem}.md"
        source_title = source_label(md_file.name) or stem

        rendered = render_staged_markdown(source_title, events)
        if structural:
            from wordpipe.chronicle.ingest import split_into_events
            from wordpipe.chronicle.merge import EVENT_HEADING_LINE_RE

            parsed, rejected = split_into_events(rendered)
            expected = [
                {"date": event.date, "title": event.title, "body": escape_nested_event_bullets(event.body)}
                for event in events
            ]
            if rejected or parsed != expected or EVENT_HEADING_LINE_RE.search(rendered):
                raise ValueError(f"{md_file.name}: structural section conflicts with reserved Chronicle framing")
        (output_dir / filename).write_text(rendered, encoding="utf-8")
        staged_files.append(filename)
        file_metrics[str(md_file.name)] = {
            "candidates": candidates,
            "staged": len(events),
            "staged_filename": filename,
        }
        source_lineage.append({
            "source_file": md_file.name,
            "staged_file": filename,
            "candidate_count": candidates,
            "staged_event_count": len(events),
        })
        for record in file_lineage:
            entry = dict(record)
            entry["staged_file"] = filename
            event_lineage.append(entry)

    lineage_doc = {"events": event_lineage}
    if structural:
        lineage_doc.update({
            "$schema": STRUCTURAL_RAW_SCHEMA,
            "markdown_mode": markdown_mode,
            "source_accounting": source_accounting,
            "parser_provenance": provenance,
        })
    lineage_path.write_text(
        json.dumps(lineage_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    metrics: dict[str, object] = {
        **source_metrics(md_files),
        "input_dir": str(input_dir),
        "output_dir": str(output_dir.resolve()),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "adapter": "prepare_generic_markdown_chronicle",
        "candidate_total_sections": total_candidates,
        "staged_event_count": total_staged,
        "extraction_coverage_percent": round(
            (total_staged / total_candidates * 100), 2
        ) if total_candidates else 0.0,
        "staged_files": staged_files,
        "file_metrics": file_metrics,
        "source_lineage": source_lineage,
        "event_lineage_file": EVENT_LINEAGE_FILENAME,
    }
    if structural:
        metrics["markdown_mode"] = markdown_mode
        metrics["heading_levels"] = list(heading_levels)
        metrics["parser_provenance"] = provenance
    metrics_path.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return metrics


def load_event_count(markdown_path: Path) -> int:
    if not markdown_path.exists():
        return 0
    text = markdown_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^event_count:\s*(\d+)\s*$", text, re.MULTILINE)
    return int(match.group(1)) if match else len(re.findall(r"^## Event:", text, re.MULTILINE))


def count_tagged_events(tagged_path: Path) -> int:
    if not tagged_path.exists():
        return 0
    text = tagged_path.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r"^<!-- themes:", text, re.MULTILINE))


def count_duplicates(duplicates_path: Path) -> int:
    if not duplicates_path.exists():
        return 0
    data = json.loads(duplicates_path.read_text(encoding="utf-8"))
    return len(data) if isinstance(data, list) else 0


def summarize_run(
    run_dir: Path,
    prepare_metrics_path: Path,
    performance_path: Path,
    run_log_path: Path,
) -> dict[str, object]:
    run_dir = run_dir.resolve()
    pipeline_dir = run_dir / "pipeline"
    prepare_metrics = json.loads(prepare_metrics_path.read_text(encoding="utf-8"))
    log_text = run_log_path.read_text(encoding="utf-8") if run_log_path.exists() else ""
    perf_text = performance_path.read_text(encoding="utf-8") if performance_path.exists() else ""
    topic = str(prepare_metrics.get("topic") or "Topic")

    output_files = {
        str(path.relative_to(run_dir)): path.stat().st_size
        for path in sorted(pipeline_dir.rglob("*"))
        if path.is_file()
    }

    metrics: dict[str, object] = {
        **prepare_metrics,
        "topic": topic,
        "pipeline_wall_clock": perf_text.strip(),
        "merged_event_count": load_event_count(pipeline_dir / "merged.md"),
        "tagged_event_count": load_event_count(pipeline_dir / "chronicle_tagged.md"),
        "events_with_theme_tags": count_tagged_events(pipeline_dir / "chronicle_tagged.md"),
        "duplicate_conflict_count": count_duplicates(pipeline_dir / "merged.duplicates.json"),
        "warning_count": len(re.findall(r"\bWARN(?:ING)?\b", log_text, re.IGNORECASE)),
        "error_count": len(re.findall(r"\bERROR\b|\[FAIL\]", log_text, re.IGNORECASE)),
        "output_files": output_files,
    }
    status = "PASS" if metrics["error_count"] == 0 and (metrics["merged_event_count"] or 0) > 0 else "REVIEW"
    summary = [
        f"# {topic} Report Run Summary",
        "",
        f"Status: {status}",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Metrics",
        "",
        f"- Input files: {metrics['input_file_count']}",
        f"- Input bytes: {metrics['input_total_bytes']}",
        f"- Input lines: {metrics['input_total_lines']}",
        f"- Candidate sections: {metrics['candidate_total_sections']}",
        f"- Staged events: {metrics['staged_event_count']}",
        f"- Extraction coverage: {metrics['extraction_coverage_percent']}%",
        f"- Merged events: {metrics['merged_event_count']}",
        f"- Tagged events: {metrics['tagged_event_count']}",
        f"- Events with theme tags: {metrics['events_with_theme_tags']}",
        f"- Duplicate/conflict entries: {metrics['duplicate_conflict_count']}",
        f"- Warnings: {metrics['warning_count']}",
        f"- Errors: {metrics['error_count']}",
        "",
        "## Main Outputs",
        "",
        "- `pipeline/merged.md`",
        "- `pipeline/chronicle_tagged.md`",
        "- `pipeline/appendix/event_index.md`",
        "- `pipeline/appendix/theme_index.md`",
        "- `pipeline/appendix/source_manifest.md`",
        "- `pipeline/appendix/link_registry.md`",
        "- `prepare_metrics.json`",
        "- `performance.txt`",
        "- `run.log`",
        "",
        "## Performance",
        "",
        "```text",
        perf_text.strip(),
        "```",
        "",
    ]
    (run_dir / "RUN_SUMMARY.md").write_text("\n".join(summary), encoding="utf-8")
    (run_dir / "run_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")

    prep = subparsers.add_parser("prepare", help="Create staged Chronicle input")
    prep.add_argument("--input-dir", required=True, type=Path)
    prep.add_argument("--output-dir", required=True, type=Path)
    prep.add_argument("--metrics", required=True, type=Path)
    prep.add_argument("--markdown-mode", choices=MARKDOWN_MODES, default=LEGACY_MODE)
    prep.add_argument("--heading-levels", nargs="+", type=int, choices=range(2, 7), default=(2,))

    summary = subparsers.add_parser("summarize", help="Summarize a completed pipeline run")
    summary.add_argument("--run-dir", required=True, type=Path)
    summary.add_argument("--prepare-metrics", required=True, type=Path)
    summary.add_argument("--performance", required=True, type=Path)
    summary.add_argument("--run-log", required=True, type=Path)

    args = parser.parse_args()

    if args.command == "prepare":
        if args.markdown_mode == STRUCTURAL_MODE and __package__ in (None, ""):
            sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        prepare(
            args.input_dir, args.output_dir, args.metrics,
            markdown_mode=args.markdown_mode, heading_levels=tuple(args.heading_levels),
        )
        return

    if args.command == "summarize":
        summarize_run(args.run_dir, args.prepare_metrics, args.performance, args.run_log)
        return

    parser.print_help()
    raise SystemExit(2)


if __name__ == "__main__":
    main()
