"""Phase 17 provenance stability comparator tests."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "compare_event_provenance_stability.py"
SPEC = importlib.util.spec_from_file_location("compare_event_provenance_stability", MODULE_PATH)
cmp_mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = cmp_mod
SPEC.loader.exec_module(cmp_mod)


def _lineage(topic: str, run_id: str, events: list[dict]) -> dict:
    return {
        "$schema": "event-lineage-v1",
        "topic": topic,
        "run_id": run_id,
        "events": events,
    }


def _corr(topic: str, run_id: str, report_events: list[dict], *, source_count: int) -> dict:
    return {
        "$schema": "event-correlation-v1",
        "topic": topic,
        "run_id": run_id,
        "source_event_count": source_count,
        "report_event_count": len(report_events),
        "unmerged_source_event_count": 0,
        "ambiguous_matches": [],
        "report_events": report_events,
    }


def _event(
    sid: str,
    rid: str,
    *,
    date: str = "2026-01-01",
    body: str = "abc",
    title: str = "T",
    source_file: str = "a.md",
) -> dict:
    return {
        "locator_kind": "markdown_section",
        "source_file": source_file,
        "candidate_ordinal": 1,
        "heading_level": 2,
        "original_heading_text": title,
        "staged_file": "01_a.md",
        "staged_event_ordinal": 1,
        "date": date,
        "title": title,
        "source_event_id": sid,
        "body_sha256": body,
        "report_event_id": rid,
    }


def _twin_payloads() -> tuple[dict, dict, dict, dict]:
    sid_a = "source_event:t:a"
    sid_b = "source_event:t:b"
    rid = "report_event:t:r"

    def events() -> list[dict]:
        return [
            _event(sid_a, rid, source_file="a.md", title="A"),
            _event(sid_b, rid, source_file="b.md", title="B"),
        ]

    def reports() -> list[dict]:
        return [{
            "report_event_id": rid,
            "date": "2026-01-01",
            "body_sha256": "abc",
            "source_event_ids": [sid_a, sid_b],
        }]

    b_lin = _lineage("t", "phase16_event_lineage_validation", events())
    c_lin = _lineage("t", "phase17_event_provenance_repeatability", events())
    b_corr = _corr("t", "phase16_event_lineage_validation", reports(), source_count=2)
    c_corr = _corr("t", "phase17_event_provenance_repeatability", reports(), source_count=2)
    return b_lin, b_corr, c_lin, c_corr


def test_compare_stable_twins():
    b_lin, b_corr, c_lin, c_corr = _twin_payloads()
    report = cmp_mod.compare_event_provenance_stability(
        baseline_lineage=b_lin,
        baseline_correlation=b_corr,
        candidate_lineage=c_lin,
        candidate_correlation=c_corr,
        required_baseline_run_id="phase16_event_lineage_validation",
    )
    assert report["status"] == "STABLE"
    assert report["source_to_report_equal"] is True
    assert report["report_to_sources_equal"] is True


def test_compare_detects_body_hash_drift():
    b_lin, b_corr, c_lin, c_corr = _twin_payloads()
    c_lin["events"][0]["body_sha256"] = "changed"
    report = cmp_mod.compare_event_provenance_stability(
        baseline_lineage=b_lin,
        baseline_correlation=b_corr,
        candidate_lineage=c_lin,
        candidate_correlation=c_corr,
        required_baseline_run_id="phase16_event_lineage_validation",
    )
    assert report["status"] == "DRIFT"
    assert report["changed_records"]


def test_compare_rejects_cross_topic():
    b_lin, b_corr, c_lin, c_corr = _twin_payloads()
    c_lin["topic"] = "other"
    c_corr["topic"] = "other"
    try:
        cmp_mod.compare_event_provenance_stability(
            baseline_lineage=b_lin,
            baseline_correlation=b_corr,
            candidate_lineage=c_lin,
            candidate_correlation=c_corr,
            required_baseline_run_id="phase16_event_lineage_validation",
        )
        raise AssertionError("expected StabilityEvidenceError")
    except cmp_mod.StabilityEvidenceError as exc:
        assert "topic mismatch" in str(exc)


def test_compare_rejects_duplicate_source_ids():
    b_lin, b_corr, c_lin, c_corr = _twin_payloads()
    b_lin["events"].append(dict(b_lin["events"][0]))
    try:
        cmp_mod.compare_event_provenance_stability(
            baseline_lineage=b_lin,
            baseline_correlation=b_corr,
            candidate_lineage=c_lin,
            candidate_correlation=c_corr,
            required_baseline_run_id="phase16_event_lineage_validation",
        )
        raise AssertionError("expected StabilityEvidenceError")
    except cmp_mod.StabilityEvidenceError as exc:
        assert "duplicate source_event_id" in str(exc)


def test_compare_run_dirs_writes_reserved_output_only(tmp_path):
    b_lin, b_corr, c_lin, c_corr = _twin_payloads()
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    out = tmp_path / "phase17_provenance_stability"
    baseline.mkdir()
    candidate.mkdir()
    (baseline / "event_lineage.json").write_text(json.dumps(b_lin), encoding="utf-8")
    (baseline / "event_correlation.json").write_text(json.dumps(b_corr), encoding="utf-8")
    (candidate / "event_lineage.json").write_text(json.dumps(c_lin), encoding="utf-8")
    (candidate / "event_correlation.json").write_text(json.dumps(c_corr), encoding="utf-8")

    code, report = cmp_mod.compare_run_dirs(
        baseline_run_dir=baseline,
        candidate_run_dir=candidate,
        output_dir=out,
        required_baseline_run_id="phase16_event_lineage_validation",
    )
    assert code == 0
    assert report is not None
    assert (out / "provenance_stability.json").is_file()
    assert not (candidate / "provenance_stability.json").exists()
    assert not (baseline / "provenance_stability.json").exists()

    code2, _ = cmp_mod.compare_run_dirs(
        baseline_run_dir=baseline,
        candidate_run_dir=candidate,
        output_dir=out,
        required_baseline_run_id="phase16_event_lineage_validation",
    )
    assert code2 == 2


def test_compare_run_dirs_drift_writes_atomic_report(tmp_path):
    b_lin, b_corr, c_lin, c_corr = _twin_payloads()
    c_lin["events"][0]["body_sha256"] = "drifted"
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    out = tmp_path / "stability"
    baseline.mkdir()
    candidate.mkdir()
    (baseline / "event_lineage.json").write_text(json.dumps(b_lin), encoding="utf-8")
    (baseline / "event_correlation.json").write_text(json.dumps(b_corr), encoding="utf-8")
    (candidate / "event_lineage.json").write_text(json.dumps(c_lin), encoding="utf-8")
    (candidate / "event_correlation.json").write_text(json.dumps(c_corr), encoding="utf-8")
    code, report = cmp_mod.compare_run_dirs(
        baseline_run_dir=baseline,
        candidate_run_dir=candidate,
        output_dir=out,
        required_baseline_run_id="phase16_event_lineage_validation",
    )
    assert code == 1
    assert report["status"] == "DRIFT"
    saved = json.loads((out / "provenance_stability.json").read_text(encoding="utf-8"))
    assert saved["status"] == "DRIFT"


def test_compare_run_dirs_invalid_leaves_no_partial(tmp_path):
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    out = tmp_path / "stability"
    baseline.mkdir()
    candidate.mkdir()
    (baseline / "event_lineage.json").write_text("{}", encoding="utf-8")
    code, report = cmp_mod.compare_run_dirs(
        baseline_run_dir=baseline,
        candidate_run_dir=candidate,
        output_dir=out,
        required_baseline_run_id="phase16_event_lineage_validation",
    )
    assert code == 2
    assert report is None
    assert not (out / "provenance_stability.json").exists()
