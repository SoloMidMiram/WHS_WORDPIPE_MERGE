#!/usr/bin/env python3
"""Reconcile completed legacy and structural MD-01 runs against a frozen input."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    root = Path(__file__).resolve().parents[1]
    if "WORDPIPE_ORIGIN_QUALIFICATION" in os.environ:
        from runpy import run_path

        run_path(str(root / "pipeline" / "_import_origin.py"))["require_driver"](
            __file__, "wordpipe.chronicle.markdown_sections",
        )
    sys.path.insert(0, str(root))

from tools import prepare_generic_markdown_chronicle as adapter
from tools.run_topic_report import (
    ProvenanceError,
    attach_verified_navigation,
    compute_individual_report_event_id,
    compute_source_event_id,
)
from wordpipe.chronicle.markdown_sections import (
    LEGACY_MODE,
    STRUCTURAL_CORRELATION_SCHEMA,
    STRUCTURAL_LINEAGE_SCHEMA,
    STRUCTURAL_MODE,
    SourceLines,
    validate_parser_provenance,
)


def load_completed_run(run: Path, mode: str):
    def load(name: str):
        return json.loads((run / name).read_text(encoding="utf-8"))

    manifest = load("topic_run_manifest.json")
    if (
        manifest["adapter"]["id"] != "prepare_generic_markdown_chronicle"
        or manifest["adapter"].get("markdown_mode", LEGACY_MODE) != mode
    ):
        raise ValueError(f"{run}: expected a {mode} run")
    exit_codes = manifest["exit_codes"]
    if not {"prepare", "pipeline", "provenance", "summarize"} <= exit_codes.keys() or any(exit_codes.values()):
        raise ValueError(f"{run}: incomplete or failed run")
    lineage = load("event_lineage.json")
    correlation = load("event_correlation.json")
    schemas = (
        (STRUCTURAL_LINEAGE_SCHEMA, STRUCTURAL_CORRELATION_SCHEMA)
        if mode == STRUCTURAL_MODE else ("event-lineage-v1", "event-correlation-v1")
    )
    for document, schema in zip((lineage, correlation), schemas, strict=True):
        if document["$schema"] != schema or document.get("markdown_mode", LEGACY_MODE) != mode:
            raise ValueError(f"{run}: incompatible sidecar schema or mode")
        if document["run_id"] != manifest["run_id"] or document["topic"] != manifest["topic"]:
            raise ValueError(f"{run}: sidecar belongs to a different run")
    if mode == STRUCTURAL_MODE:
        levels = tuple(manifest["adapter"].get("heading_levels", (2,)))
        producer = validate_parser_provenance(lineage.get("parser_provenance"), levels)
        if validate_parser_provenance(correlation.get("parser_provenance"), levels) != producer:
            raise ValueError(f"{run}: structural sidecars disagree on parser provenance")
    if correlation["ambiguous_matches"] or correlation["unmerged_source_event_count"]:
        raise ValueError(f"{run}: unresolved correlation")
    events = lineage["events"]
    reports = {row["report_event_id"]: row for row in correlation["report_events"]}
    memberships = {report_id: set() for report_id in reports}
    for event in events:
        source_id = compute_source_event_id(manifest["topic"], event, markdown_mode=mode)[0]
        report_id = compute_individual_report_event_id(
            manifest["topic"], event["date"], event["body_sha256"], markdown_mode=mode,
        )[0]
        if event["source_event_id"] != source_id or event["report_event_id"] != report_id:
            raise ValueError(f"{run}: event identity disagrees with its sidecar payload")
        report = reports[report_id]
        if (report["date"], report["body_sha256"]) != (event["date"], event["body_sha256"]):
            raise ValueError(f"{run}: report payload disagrees with lineage")
        memberships[report_id].add(source_id)
    if any(
        not members or members != set(reports[report_id]["source_event_ids"])
        for report_id, members in memberships.items()
    ):
        raise ValueError(f"{run}: report membership disagrees with lineage")
    attach_verified_navigation(run, events, reports, markdown_mode=mode)
    return manifest, lineage


def legacy_candidates(source: SourceLines):
    selected = (match for match in adapter.SECTION_HEADING_RE.finditer(source.text)
                if len(match.group("marks")) == 2)
    for ordinal, match in enumerate(selected, 1):
        start = source.text.count("\n", 0, match.start())
        end = source.text.count("\n", 0, match.end("title")) + 1
        yield {
            "candidate_ordinal": ordinal,
            "heading_span": source.span(start, end),
            "heading_level": 2,
            "original_heading_text": match.group("title").strip(),
            "staged_event_ordinal": None,
        }


def candidates_by_heading(candidates, events):
    by_ordinal = {event["candidate_ordinal"]: event for event in events}
    rows = {}
    for candidate in candidates:
        coordinates = candidate["heading_span"]
        key = (coordinates["start_byte"], coordinates["end_byte"])
        if key in rows:
            raise ValueError(f"ambiguous candidate correspondence at bytes {key}")
        rows[key] = {**candidate, **by_ordinal.pop(candidate["candidate_ordinal"], {})}
    if by_ordinal:
        raise ValueError("event lineage has no matching candidate")
    return rows


def compare(legacy_run: Path, structural_run: Path, input_dir: Path) -> dict:
    legacy_run, structural_run = legacy_run.resolve(), structural_run.resolve()
    if legacy_run.is_relative_to(structural_run) or structural_run.is_relative_to(legacy_run):
        raise ValueError("comparison needs separate run directories")
    legacy_manifest, legacy = load_completed_run(legacy_run, LEGACY_MODE)
    structural_manifest, structural = load_completed_run(structural_run, STRUCTURAL_MODE)
    if legacy_manifest["topic"] != structural_manifest["topic"]:
        raise ValueError("comparison requires matching topics")
    files = sorted(input_dir.glob("*.md"))
    accounting = {item["source_file"]: item for item in structural["source_accounting"]}
    legacy_metrics = json.loads((legacy_run / "prepare_metrics.json").read_text(encoding="utf-8"))
    legacy_files = {row["source_file"]: row["staged_file"] for row in legacy_metrics["source_lineage"]}
    if {path.name for path in files} != accounting.keys() or accounting.keys() != legacy_files.keys():
        raise ValueError("input snapshot membership differs from run evidence")

    comparisons = []
    for path in files:
        source = SourceLines.from_bytes(path.read_bytes())
        ledger = accounting[path.name]
        if source.sha256 != ledger["source_sha256"]:
            raise ValueError(f"{path.name}: input bytes differ from structural snapshot")
        projected, projected_lineage, _ = adapter.parse_file(path)
        legacy_events = [event for event in legacy["events"] if event["source_file"] == path.name]
        structural_events = [event for event in structural["events"] if event["source_file"] == path.name]
        staged = legacy_run / "staged_input" / Path(legacy_files[path.name]).name
        expected = adapter.render_staged_markdown(adapter.source_label(path.name) or path.stem, projected)
        if staged.read_text(encoding="utf-8") != expected or len(projected_lineage) != len(legacy_events):
            raise ValueError(f"{path.name}: legacy staged output does not replay from the snapshot")
        for expected_record, actual in zip(projected_lineage, legacy_events, strict=True):
            if any(actual.get(key) != value for key, value in expected_record.items()):
                raise ValueError(f"{path.name}: legacy lineage does not replay from the snapshot")
        old = candidates_by_heading(legacy_candidates(source), legacy_events)
        new = candidates_by_heading(ledger["candidates"], structural_events)
        for heading in sorted(old.keys() | new.keys()):
            before, after = old.get(heading), new.get(heading)
            if before is None:
                disposition = "new_candidate"
            elif after is None:
                fenced = any(s["start_byte"] <= heading[0] < s["end_byte"] for s in ledger["fences"])
                disposition = "removed_fenced_heading" if fenced else "removed_boundary"
            elif before.get("body_sha256") != after.get("body_sha256") or before.get("date") != after.get("date"):
                disposition = "changed_payload"
            else:
                disposition = "matched_heading"
            comparisons.append({
                "source_file": path.name,
                "source_sha256": source.sha256,
                "disposition": disposition,
                "legacy": before,
                "structural": after,
            })
    return {
        "$schema": "markdown-mode-comparison-v2",
        "structural_parser_provenance": structural["parser_provenance"],
        "topic": legacy_manifest["topic"],
        "legacy_run_id": legacy_manifest["run_id"],
        "structural_run_id": structural_manifest["run_id"],
        "legacy_snapshot_verification": "staged_and_lineage_replay",
        "candidates": comparisons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("legacy-run", "structural-run", "input-dir", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    try:
        if any(args.output.resolve().is_relative_to(path.resolve()) for path in (
            args.legacy_run, args.structural_run, args.input_dir,
        )):
            raise ValueError("comparison output must be outside both runs and the input snapshot")
        result = compare(args.legacy_run, args.structural_run, args.input_dir)
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except (OSError, ValueError, KeyError, TypeError, ProvenanceError) as exc:
        parser.exit(1, f"Comparison failed: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
