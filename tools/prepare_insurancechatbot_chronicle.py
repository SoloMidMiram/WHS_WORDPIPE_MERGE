#!/usr/bin/env python3
"""Prepare InsuranceChatbot markdown for the Chronicle pipeline.

The Chronicle ingest stage expects dated bullet events. The
InsuranceChatbot inputs are project docs: a commit log, a roadmap, and a
project digest. This tool converts those source shapes into staged
Chronicle-compatible markdown and records preparation metrics.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence


COMMIT_FILE = "Commit history.md"
DIGEST_FILE = "combined_git_history_digest (2).md"
ROADMAP_FILE = "ROADMAP.md"
DEFAULT_FALLBACK_DATE = "2026-07-16"
EVENT_LINEAGE_FILENAME = "event_lineage.json"

COMMIT_HEADING_RE = re.compile(
    r"^##\s+(?P<sha>[0-9a-f]{7,40})\s+(?:--|---|-|—|ΓÇö)\s+"
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T[^\s]+)\s*$",
    re.MULTILINE,
)
SECTION_HEADING_RE = re.compile(r"^(?P<marks>#{2,4})\s+(?P<title>.+?)\s*$", re.MULTILINE)
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")


@dataclass(frozen=True)
class ChronicleEvent:
    date: str
    title: str
    body: str


def normalize_mojibake(text: str) -> str:
    """Normalize known mojibake found in the supplied InsuranceChatbot docs."""
    replacements = {
        "ΓÇö": "—",
        "ΓÇô": "–",
        "ΓÇ£": '"',
        "ΓÇ¥": '"',
        "ΓÇÿ": "'",
        "ΓÇÖ": "'",
        "ΓÇª": "...",
        "â€”": "—",
        "â€“": "–",
        "â€™": "'",
        "â€œ": '"',
        "â€\x9d": '"',
        "\xa0": " ",
    }
    for raw, clean in replacements.items():
        text = text.replace(raw, clean)
    return text


def sanitize_title(title: str) -> str:
    """Keep event titles compact and safe for a markdown heading."""
    title = normalize_mojibake(title)
    title = re.sub(r"\s+", " ", title).strip()
    title = title.strip("#`*_[]() ")
    return title[:180] if len(title) > 180 else title


def first_date(text: str, fallback: str = DEFAULT_FALLBACK_DATE) -> str:
    match = DATE_RE.search(text)
    if match:
        return match.group(1)
    return fallback


def split_sections(text: str, heading_levels: Iterable[int]) -> list[tuple[str, str]]:
    """Split markdown into non-empty sections for selected heading levels."""
    levels = {int(level) for level in heading_levels}
    matches = [
        match for match in SECTION_HEADING_RE.finditer(text)
        if len(match.group("marks")) in levels
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


def parse_commit_history(
    text: str,
    *,
    source_file: str = COMMIT_FILE,
) -> tuple[list[ChronicleEvent], list[dict[str, object]], int]:
    text = normalize_mojibake(text)
    matches = list(COMMIT_HEADING_RE.finditer(text))
    events: list[ChronicleEvent] = []
    lineage: list[dict[str, object]] = []
    seen_shas: set[str] = set()
    for index, match in enumerate(matches):
        candidate_ordinal = index + 1
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        non_empty = [line.strip() for line in block.splitlines() if line.strip()]
        subject = non_empty[0] if non_empty else "Commit update"
        raw_sha = match.group("sha").lower()
        if len(raw_sha) < 7:
            raise ValueError(f"commit SHA too short in {source_file}: {raw_sha!r}")
        if raw_sha in seen_shas:
            raise ValueError(f"duplicate commit SHA locator in {source_file}: {raw_sha}")
        seen_shas.add(raw_sha)
        timestamp = match.group("timestamp")
        date = timestamp[:10]
        title = sanitize_title(f"{raw_sha[:7]} - {subject}")
        body = f"Timestamp: {timestamp}\n\n{block}".strip()
        events.append(ChronicleEvent(date=date, title=title, body=body))
        lineage.append({
            "locator_kind": "commit_heading",
            "source_file": source_file,
            "candidate_ordinal": candidate_ordinal,
            "commit_sha": raw_sha,
            "original_heading_text": subject,
            "staged_event_ordinal": candidate_ordinal,
            "date": date,
            "title": title,
            "start_line": _start_line(text, match.start()),
            "commit_timestamp": timestamp,
        })
    return events, lineage, len(matches)


def _parse_markdown_sections(
    text: str,
    *,
    source_file: str,
    heading_levels: tuple[int, ...],
    fallback_date: str | None = None,
) -> tuple[list[ChronicleEvent], list[dict[str, object]], int]:
    text = normalize_mojibake(text)
    fallback = fallback_date or first_date(text)
    levels = {int(level) for level in heading_levels}
    matches = [
        match for match in SECTION_HEADING_RE.finditer(text)
        if len(match.group("marks")) in levels
    ]
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
        event_date = first_date(f"{title}\n{body}", fallback)
        event_title = sanitize_title(title)
        events.append(ChronicleEvent(date=event_date, title=event_title, body=body))
        lineage.append({
            "locator_kind": "markdown_section",
            "source_file": source_file,
            "candidate_ordinal": candidate_ordinal,
            "heading_level": len(match.group("marks")),
            "original_heading_text": title.strip(),
            "staged_event_ordinal": staged_ordinal,
            "date": event_date,
            "title": event_title,
            "start_line": _start_line(text, match.start()),
        })
    return events, lineage, len(matches)


def parse_roadmap(
    text: str,
    fallback_date: str | None = None,
    *,
    source_file: str = ROADMAP_FILE,
) -> tuple[list[ChronicleEvent], list[dict[str, object]], int]:
    return _parse_markdown_sections(
        text,
        source_file=source_file,
        heading_levels=(2,),
        fallback_date=fallback_date,
    )


def parse_digest(
    text: str,
    fallback_date: str | None = None,
    *,
    source_file: str = DIGEST_FILE,
) -> tuple[list[ChronicleEvent], list[dict[str, object]], int]:
    return _parse_markdown_sections(
        text,
        source_file=source_file,
        heading_levels=(3, 4),
        fallback_date=fallback_date,
    )


def render_staged_markdown(source_title: str, events: list[ChronicleEvent]) -> str:
    lines = [
        f"# {source_title}",
        "",
        "## July 2026",
        "",
    ]
    for event in events:
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


def prepare(input_dir: Path, output_dir: Path, metrics_path: Path) -> dict[str, object]:
    input_dir = input_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    consumed_sources = [
        input_dir / COMMIT_FILE,
        input_dir / DIGEST_FILE,
        input_dir / ROADMAP_FILE,
    ]
    commit_path, digest_path, roadmap_path = consumed_sources

    commit_text = commit_path.read_text(encoding="utf-8")
    digest_text = digest_path.read_text(encoding="utf-8")
    roadmap_text = roadmap_path.read_text(encoding="utf-8")

    commit_events, commit_lineage, commit_candidates = parse_commit_history(commit_text)
    roadmap_events, roadmap_lineage, roadmap_candidates = parse_roadmap(roadmap_text)
    digest_events, digest_lineage, digest_candidates = parse_digest(digest_text)

    # Staged-file order is lexicographic on filenames (01, 02, 03).
    outputs = {
        "01_commit_history.md": ("InsuranceChatbot Commit History", commit_events, commit_lineage),
        "02_project_digest.md": ("InsuranceChatbot Project Digest", digest_events, digest_lineage),
        "03_roadmap.md": ("InsuranceChatbot Roadmap", roadmap_events, roadmap_lineage),
    }
    event_lineage: list[dict[str, object]] = []
    for filename, (title, events, file_lineage) in outputs.items():
        (output_dir / filename).write_text(
            render_staged_markdown(title, events),
            encoding="utf-8",
        )
        for record in file_lineage:
            entry = dict(record)
            entry["staged_file"] = filename
            event_lineage.append(entry)

    staged_files = sorted(outputs.keys())
    source_lineage = [
        {
            "source_file": COMMIT_FILE,
            "staged_file": "01_commit_history.md",
            "candidate_count": commit_candidates,
            "staged_event_count": len(commit_events),
        },
        {
            "source_file": DIGEST_FILE,
            "staged_file": "02_project_digest.md",
            "candidate_count": digest_candidates,
            "staged_event_count": len(digest_events),
        },
        {
            "source_file": ROADMAP_FILE,
            "staged_file": "03_roadmap.md",
            "candidate_count": roadmap_candidates,
            "staged_event_count": len(roadmap_events),
        },
    ]

    staged_event_count = len(commit_events) + len(roadmap_events) + len(digest_events)
    candidate_count = commit_candidates + roadmap_candidates + digest_candidates

    lineage_path = metrics_path.parent / EVENT_LINEAGE_FILENAME
    lineage_path.write_text(
        json.dumps({"events": event_lineage}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    metrics: dict[str, object] = {
        **source_metrics(consumed_sources),
        "input_dir": str(input_dir),
        "output_dir": str(output_dir.resolve()),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "candidate_commit_headings": commit_candidates,
        "candidate_roadmap_sections": roadmap_candidates,
        "candidate_digest_sections": digest_candidates,
        "candidate_total_sections": candidate_count,
        "staged_event_count": staged_event_count,
        "extraction_coverage_percent": round(
            (staged_event_count / candidate_count * 100), 2
        ) if candidate_count else 0.0,
        "staged_files": staged_files,
        "source_lineage": source_lineage,
        "event_lineage_file": EVENT_LINEAGE_FILENAME,
    }
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return metrics


def load_event_count(markdown_path: Path) -> int:
    if not markdown_path.exists():
        return 0
    text = markdown_path.read_text(encoding="utf-8")
    match = re.search(r"^event_count:\s*(\d+)\s*$", text, re.MULTILINE)
    return int(match.group(1)) if match else len(re.findall(r"^## Event:", text, re.MULTILINE))


def count_tagged_events(tagged_path: Path) -> int:
    if not tagged_path.exists():
        return 0
    text = tagged_path.read_text(encoding="utf-8")
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

    output_files = {
        str(path.relative_to(run_dir)): path.stat().st_size
        for path in sorted(pipeline_dir.rglob("*"))
        if path.is_file()
    }
    metrics: dict[str, object] = {
        **prepare_metrics,
        "pipeline_wall_clock": perf_text.strip(),
        "merged_event_count": load_event_count(pipeline_dir / "merged.md"),
        "tagged_event_count": load_event_count(pipeline_dir / "chronicle_tagged.md"),
        "events_with_theme_tags": count_tagged_events(pipeline_dir / "chronicle_tagged.md"),
        "duplicate_conflict_count": count_duplicates(pipeline_dir / "merged.duplicates.json"),
        "warning_count": len(re.findall(r"\bWARN(?:ING)?\b", log_text, re.IGNORECASE)),
        "error_count": len(re.findall(r"\bERROR\b|\[FAIL\]", log_text, re.IGNORECASE)),
        "output_files": output_files,
    }
    status = "PASS" if metrics["error_count"] == 0 and metrics["merged_event_count"] else "REVIEW"
    summary = [
        "# InsuranceChatbot Report Run Summary",
        "",
        f"Status: {status}",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Metrics",
        "",
        f"- Input files: {metrics['input_file_count']}",
        f"- Input bytes: {metrics['input_total_bytes']}",
        f"- Input lines: {metrics['input_total_lines']}",
        f"- Candidate commit headings: {metrics['candidate_commit_headings']}",
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

    summary = subparsers.add_parser("summarize", help="Summarize a completed pipeline run")
    summary.add_argument("--run-dir", required=True, type=Path)
    summary.add_argument("--prepare-metrics", required=True, type=Path)
    summary.add_argument("--performance", required=True, type=Path)
    summary.add_argument("--run-log", required=True, type=Path)

    parser.add_argument("--input-dir", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--output-dir", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--metrics", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.command == "summarize":
        summarize_run(args.run_dir, args.prepare_metrics, args.performance, args.run_log)
        return

    if args.command == "prepare":
        prepare(args.input_dir, args.output_dir, args.metrics)
        return

    if args.input_dir and args.output_dir and args.metrics:
        prepare(args.input_dir, args.output_dir, args.metrics)
        return

    parser.print_help()
    raise SystemExit(2)


if __name__ == "__main__":
    main()
