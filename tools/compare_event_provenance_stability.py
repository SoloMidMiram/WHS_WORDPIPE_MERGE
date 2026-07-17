#!/usr/bin/env python3
"""Compare Phase 16/17 event provenance sidecars for stable SourceEvent/ReportEvent IDs.

Non-mutating of topic-run evidence directories. Writes only into a separately
reserved comparison-evidence output directory.

Exit codes:
  0 — stable (exact match)
  1 — verified drift (valid inputs; full report written)
  2 — invalid or incomplete evidence (no partial report)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


LOCATOR_FIELDS = (
    "locator_kind",
    "source_file",
    "candidate_ordinal",
    "heading_level",
    "commit_sha",
    "original_heading_text",
)


class StabilityEvidenceError(ValueError):
    """Invalid or incomplete provenance evidence for comparison."""


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise StabilityEvidenceError(f"missing file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StabilityEvidenceError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise StabilityEvidenceError(f"root must be object: {path}")
    return data


def _require_unique_ids(values: list[str], label: str) -> None:
    seen: set[str] = set()
    dupes: list[str] = []
    for value in values:
        if value in seen:
            dupes.append(value)
        seen.add(value)
    if dupes:
        raise StabilityEvidenceError(f"duplicate {label}: {sorted(set(dupes))}")


def _lineage_by_source(lineage: dict[str, Any]) -> dict[str, dict[str, Any]]:
    events = lineage.get("events")
    if not isinstance(events, list):
        raise StabilityEvidenceError("event_lineage.events must be a list")
    ids = [str(item.get("source_event_id", "")) for item in events if isinstance(item, dict)]
    if any(not sid for sid in ids):
        raise StabilityEvidenceError("event_lineage event missing source_event_id")
    _require_unique_ids(ids, "source_event_id in lineage")
    return {str(item["source_event_id"]): item for item in events if isinstance(item, dict)}


def _correlation_maps(
    correlation: dict[str, Any],
) -> tuple[dict[str, str], dict[str, set[str]], dict[str, dict[str, Any]]]:
    report_events = correlation.get("report_events")
    if not isinstance(report_events, list):
        raise StabilityEvidenceError("event_correlation.report_events must be a list")
    report_ids = [
        str(item.get("report_event_id", ""))
        for item in report_events
        if isinstance(item, dict)
    ]
    if any(not rid for rid in report_ids):
        raise StabilityEvidenceError("report_events entry missing report_event_id")
    _require_unique_ids(report_ids, "report_event_id in correlation")

    source_to_report: dict[str, str] = {}
    report_to_sources: dict[str, set[str]] = {}
    report_by_id: dict[str, dict[str, Any]] = {}
    source_ids_seen: list[str] = []

    for item in report_events:
        if not isinstance(item, dict):
            raise StabilityEvidenceError("report_events entries must be objects")
        rid = str(item["report_event_id"])
        report_by_id[rid] = item
        sources = item.get("source_event_ids")
        if not isinstance(sources, list):
            raise StabilityEvidenceError(f"{rid} source_event_ids must be a list")
        bucket = report_to_sources.setdefault(rid, set())
        for sid in sources:
            sid_s = str(sid)
            source_ids_seen.append(sid_s)
            if sid_s in source_to_report:
                raise StabilityEvidenceError(
                    f"source_event_id {sid_s} maps to multiple report_event_ids"
                )
            source_to_report[sid_s] = rid
            bucket.add(sid_s)

    _require_unique_ids(source_ids_seen, "source_event_id in correlation mappings")
    return source_to_report, report_to_sources, report_by_id


def _validate_run_pair_side(
    *,
    label: str,
    lineage: dict[str, Any],
    correlation: dict[str, Any],
) -> dict[str, Any]:
    if lineage.get("$schema") != "event-lineage-v1":
        raise StabilityEvidenceError(f"{label} lineage schema must be event-lineage-v1")
    if correlation.get("$schema") != "event-correlation-v1":
        raise StabilityEvidenceError(
            f"{label} correlation schema must be event-correlation-v1"
        )
    topic = lineage.get("topic")
    run_id = lineage.get("run_id")
    if not isinstance(topic, str) or not topic:
        raise StabilityEvidenceError(f"{label} lineage topic missing")
    if not isinstance(run_id, str) or not run_id:
        raise StabilityEvidenceError(f"{label} lineage run_id missing")
    if correlation.get("topic") != topic:
        raise StabilityEvidenceError(f"{label} correlation topic mismatch")
    if correlation.get("run_id") != run_id:
        raise StabilityEvidenceError(f"{label} correlation run_id mismatch")

    by_source = _lineage_by_source(lineage)
    source_to_report, report_to_sources, report_by_id = _correlation_maps(correlation)

    for sid, report_id in source_to_report.items():
        if sid not in by_source:
            raise StabilityEvidenceError(
                f"{label} correlation source_event_id missing from lineage: {sid}"
            )
        lineage_report = by_source[sid].get("report_event_id")
        if lineage_report is not None and str(lineage_report) != report_id:
            raise StabilityEvidenceError(
                f"{label} lineage/correlation report_event_id disagree for {sid}"
            )

    for sid, record in by_source.items():
        if sid not in source_to_report:
            raise StabilityEvidenceError(
                f"{label} lineage source_event_id missing from correlation: {sid}"
            )

    return {
        "topic": topic,
        "run_id": run_id,
        "by_source": by_source,
        "source_to_report": source_to_report,
        "report_to_sources": report_to_sources,
        "report_by_id": report_by_id,
        "source_event_count": correlation.get("source_event_count"),
        "report_event_count": correlation.get("report_event_count"),
    }


def compare_event_provenance_stability(
    *,
    baseline_lineage: dict[str, Any],
    baseline_correlation: dict[str, Any],
    candidate_lineage: dict[str, Any],
    candidate_correlation: dict[str, Any],
    required_baseline_run_id: str | None = None,
) -> dict[str, Any]:
    """Pure comparison. Returns a report dict; does not write files."""
    baseline = _validate_run_pair_side(
        label="baseline",
        lineage=baseline_lineage,
        correlation=baseline_correlation,
    )
    candidate = _validate_run_pair_side(
        label="candidate",
        lineage=candidate_lineage,
        correlation=candidate_correlation,
    )

    if baseline["topic"] != candidate["topic"]:
        raise StabilityEvidenceError(
            f"topic mismatch: {baseline['topic']!r} vs {candidate['topic']!r}"
        )
    if baseline["run_id"] == candidate["run_id"]:
        raise StabilityEvidenceError("baseline and candidate run_id must be distinct")
    if required_baseline_run_id is not None and baseline["run_id"] != required_baseline_run_id:
        raise StabilityEvidenceError(
            f"baseline run_id must be {required_baseline_run_id!r}, "
            f"got {baseline['run_id']!r}"
        )

    b_sources = set(baseline["by_source"])
    c_sources = set(candidate["by_source"])
    b_reports = set(baseline["report_by_id"])
    c_reports = set(candidate["report_by_id"])

    missing_source_ids = sorted(b_sources - c_sources)
    added_source_ids = sorted(c_sources - b_sources)
    missing_report_ids = sorted(b_reports - c_reports)
    added_report_ids = sorted(c_reports - b_reports)

    changed_records: list[dict[str, Any]] = []
    for sid in sorted(b_sources & c_sources):
        b_rec = baseline["by_source"][sid]
        c_rec = candidate["by_source"][sid]
        deltas: dict[str, Any] = {}
        for field in LOCATOR_FIELDS:
            if b_rec.get(field) != c_rec.get(field):
                deltas[field] = {"baseline": b_rec.get(field), "candidate": c_rec.get(field)}
        for field in ("date", "body_sha256", "title"):
            if field == "title":
                continue  # diagnostic only; not identity
            if b_rec.get(field) != c_rec.get(field):
                deltas[field] = {"baseline": b_rec.get(field), "candidate": c_rec.get(field)}
        b_map = baseline["source_to_report"][sid]
        c_map = candidate["source_to_report"][sid]
        if b_map != c_map:
            deltas["report_event_id"] = {"baseline": b_map, "candidate": c_map}
        if deltas:
            title_diag = None
            if b_rec.get("title") != c_rec.get("title"):
                title_diag = {
                    "baseline": b_rec.get("title"),
                    "candidate": c_rec.get("title"),
                }
            entry: dict[str, Any] = {"source_event_id": sid, "changes": deltas}
            if title_diag is not None:
                entry["title_diagnostic"] = title_diag
            changed_records.append(entry)

    mapping_drift: list[dict[str, Any]] = []
    for rid in sorted(b_reports & c_reports):
        b_set = baseline["report_to_sources"][rid]
        c_set = candidate["report_to_sources"][rid]
        if b_set != c_set:
            mapping_drift.append({
                "report_event_id": rid,
                "baseline_source_event_ids": sorted(b_set),
                "candidate_source_event_ids": sorted(c_set),
            })

    count_drift: dict[str, Any] = {}
    for key in ("source_event_count", "report_event_count"):
        if baseline[key] != candidate[key]:
            count_drift[key] = {
                "baseline": baseline[key],
                "candidate": candidate[key],
            }

    stable = not any([
        missing_source_ids,
        added_source_ids,
        missing_report_ids,
        added_report_ids,
        changed_records,
        mapping_drift,
        count_drift,
    ])

    return {
        "$schema": "provenance-stability-v1",
        "status": "STABLE" if stable else "DRIFT",
        "topic": baseline["topic"],
        "baseline_run_id": baseline["run_id"],
        "candidate_run_id": candidate["run_id"],
        "missing_source_event_ids": missing_source_ids,
        "added_source_event_ids": added_source_ids,
        "missing_report_event_ids": missing_report_ids,
        "added_report_event_ids": added_report_ids,
        "changed_records": changed_records,
        "report_to_sources_drift": mapping_drift,
        "count_drift": count_drift,
        "source_to_report_equal": baseline["source_to_report"] == candidate["source_to_report"],
        "report_to_sources_equal": baseline["report_to_sources"] == candidate["report_to_sources"],
    }


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        tmp_path.replace(path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Provenance Stability Report",
        "",
        f"- Status: **{report['status']}**",
        f"- Topic: `{report['topic']}`",
        f"- Baseline: `{report['baseline_run_id']}`",
        f"- Candidate: `{report['candidate_run_id']}`",
        f"- source→report maps equal: {report['source_to_report_equal']}",
        f"- report→sources maps equal: {report['report_to_sources_equal']}",
        "",
    ]
    return "\n".join(lines)


def reserve_output_dir(output_dir: Path) -> Path:
    """Create a fresh comparison-evidence directory; refuse collisions."""
    try:
        output_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise StabilityEvidenceError(
            f"comparison evidence directory already exists: {output_dir}"
        ) from exc
    report_path = output_dir / "provenance_stability.json"
    if report_path.exists():
        raise StabilityEvidenceError(f"stability report already exists: {report_path}")
    return output_dir


def compare_run_dirs(
    *,
    baseline_run_dir: Path,
    candidate_run_dir: Path,
    output_dir: Path,
    required_baseline_run_id: str | None = "phase16_event_lineage_validation",
) -> tuple[int, dict[str, Any] | None]:
    """CLI orchestration: validate, compare, atomically write on 0/1."""
    try:
        reserve_output_dir(output_dir)
        baseline_lineage = _load_json(baseline_run_dir / "event_lineage.json")
        baseline_correlation = _load_json(baseline_run_dir / "event_correlation.json")
        candidate_lineage = _load_json(candidate_run_dir / "event_lineage.json")
        candidate_correlation = _load_json(candidate_run_dir / "event_correlation.json")
        report = compare_event_provenance_stability(
            baseline_lineage=baseline_lineage,
            baseline_correlation=baseline_correlation,
            candidate_lineage=candidate_lineage,
            candidate_correlation=candidate_correlation,
            required_baseline_run_id=required_baseline_run_id,
        )
    except StabilityEvidenceError as exc:
        print(f"[INVALID] {exc}", file=sys.stderr)
        return 2, None

    _atomic_write_json(output_dir / "provenance_stability.json", report)
    (output_dir / "provenance_stability.md").write_text(
        _render_markdown(report),
        encoding="utf-8",
    )
    if report["status"] == "STABLE":
        return 0, report
    return 1, report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-run-dir", type=Path, required=True)
    parser.add_argument("--candidate-run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--required-baseline-run-id",
        default="phase16_event_lineage_validation",
        help="Expected baseline run_id (default: phase16_event_lineage_validation)",
    )
    parser.add_argument(
        "--allow-any-baseline-run-id",
        action="store_true",
        help="Disable required baseline run_id check (tests only)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    required = None if args.allow_any_baseline_run_id else args.required_baseline_run_id
    code, report = compare_run_dirs(
        baseline_run_dir=args.baseline_run_dir,
        candidate_run_dir=args.candidate_run_dir,
        output_dir=args.output_dir,
        required_baseline_run_id=required,
    )
    if report is not None:
        print(f"Status: {report['status']} (exit {code})")
        print(f"Wrote: {args.output_dir / 'provenance_stability.json'}")
    return code


if __name__ == "__main__":
    sys.exit(main())
