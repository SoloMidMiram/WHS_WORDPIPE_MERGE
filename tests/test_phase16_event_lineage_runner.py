"""Phase 16 event lineage finalize + correlation unit tests."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "run_topic_report.py"
SPEC = importlib.util.spec_from_file_location("run_topic_report_phase16", MODULE_PATH)
runner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


def _metrics_with_lineage(*, staged_event_count: int = 1) -> dict:
    return {
        "input_file_count": 1,
        "candidate_total_sections": 1,
        "staged_event_count": staged_event_count,
        "extraction_coverage_percent": 100.0,
        "staged_files": ["01_doc.md"],
        "source_lineage": [{
            "source_file": "doc.md",
            "staged_file": "01_doc.md",
            "candidate_count": 1,
            "staged_event_count": staged_event_count,
        }],
        "event_lineage_file": "event_lineage.json",
    }


def test_finalize_event_lineage_adds_topic_run_and_source_event_id(tmp_path):
    metrics_path = tmp_path / "prepare_metrics.json"
    metrics = _metrics_with_lineage()
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
    (tmp_path / "event_lineage.json").write_text(
        json.dumps({
            "events": [{
                "locator_kind": "markdown_section",
                "source_file": "doc.md",
                "candidate_ordinal": 1,
                "heading_level": 2,
                "original_heading_text": "Alpha",
                "staged_file": "01_doc.md",
                "staged_event_ordinal": 1,
                "date": "2026-01-01",
                "title": "Alpha",
                "start_line": 3,
            }],
        }),
        encoding="utf-8",
    )

    envelope = runner.validate_and_finalize_event_lineage(
        metrics,
        metrics_path,
        topic="t",
        run_id="r1",
        require_event_lineage=True,
    )
    assert envelope is not None
    assert envelope["$schema"] == "event-lineage-v1"
    assert envelope["topic"] == "t"
    assert envelope["run_id"] == "r1"
    assert envelope["events"][0]["source_event_id"].startswith("source_event:t:")
    assert envelope["events"][0]["body_sha256"] is None
    saved = json.loads((tmp_path / "event_lineage.json").read_text(encoding="utf-8"))
    assert saved["$schema"] == "event-lineage-v1"


def test_registered_adapter_requires_event_lineage_pointer(tmp_path):
    metrics_path = tmp_path / "prepare_metrics.json"
    metrics = _metrics_with_lineage()
    del metrics["event_lineage_file"]
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
    try:
        runner.validate_and_finalize_event_lineage(
            metrics,
            metrics_path,
            topic="t",
            run_id="r1",
            require_event_lineage=True,
        )
        raise AssertionError("expected AdapterMetricsError")
    except runner.AdapterMetricsError as exc:
        assert "event_lineage_file" in str(exc)


def test_custom_adapter_may_omit_event_lineage(tmp_path):
    metrics_path = tmp_path / "prepare_metrics.json"
    metrics = {
        "input_file_count": 0,
        "candidate_total_sections": 0,
        "staged_event_count": 0,
        "extraction_coverage_percent": 0.0,
        "staged_files": [],
    }
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
    result = runner.validate_and_finalize_event_lineage(
        metrics,
        metrics_path,
        topic="t",
        run_id="r1",
        require_event_lineage=False,
    )
    assert result is None


def test_correlate_many_to_one_is_not_ambiguous(tmp_path):
    run_dir = tmp_path / "run"
    norm = run_dir / "pipeline" / "normalised"
    norm.mkdir(parents=True)
    block = (
        "---\nsource: a\nevent_count: 1\n---\n\n"
        "## Event: 2026-01-01 – Same\n\nshared body\n"
    )
    (norm / "01_a.md").write_text(block, encoding="utf-8")
    (norm / "02_b.md").write_text(
        block.replace("source: a", "source: b"),
        encoding="utf-8",
    )
    from wordpipe.chronicle.merge import merge_files

    merged_md, _dup, _c, _s = merge_files(
        [norm / "01_a.md", norm / "02_b.md"],
        conflict_mode="keep-both",
    )
    (run_dir / "pipeline" / "merged.md").write_text(merged_md, encoding="utf-8")

    sid_a = "source_event:t:aaa"
    sid_b = "source_event:t:bbb"
    lineage = {
        "$schema": "event-lineage-v1",
        "topic": "t",
        "run_id": "r1",
        "events": [
            {
                "locator_kind": "markdown_section",
                "source_file": "a.md",
                "candidate_ordinal": 1,
                "heading_level": 2,
                "original_heading_text": "A",
                "staged_file": "01_a.md",
                "staged_event_ordinal": 1,
                "date": "2026-01-01",
                "title": "A",
                "source_event_id": sid_a,
                "body_sha256": None,
            },
            {
                "locator_kind": "markdown_section",
                "source_file": "b.md",
                "candidate_ordinal": 1,
                "heading_level": 2,
                "original_heading_text": "B",
                "staged_file": "02_b.md",
                "staged_event_ordinal": 1,
                "date": "2026-01-01",
                "title": "B",
                "source_event_id": sid_b,
                "body_sha256": None,
            },
        ],
    }
    correlation = runner.correlate_event_provenance(
        run_dir, lineage, topic="t", run_id="r1"
    )
    assert correlation["$schema"] == "event-correlation-v1"
    assert correlation["source_event_count"] == 2
    assert correlation["report_event_count"] == 1
    assert correlation["unmerged_source_event_count"] == 0
    assert correlation["ambiguous_matches"] == []
    assert correlation["survivor_verification"]["method"] == "merged-note-aware-v1"
    assert set(correlation["report_events"][0]["source_event_ids"]) == {sid_a, sid_b}
    assert (run_dir / "event_correlation.json").is_file()


def test_correlate_ignores_merged_conflict_comment_pollution(tmp_path):
    """keep-both notes attach to prior bodies when re-parsed; do not use them."""
    run_dir = tmp_path / "run"
    norm = run_dir / "pipeline" / "normalised"
    norm.mkdir(parents=True)
    (norm / "01_a.md").write_text(
        "---\nsource: a\nevent_count: 1\n---\n\n"
        "## Event: 2026-01-01 – One\n\nalpha body\n",
        encoding="utf-8",
    )
    (norm / "02_b.md").write_text(
        "---\nsource: b\nevent_count: 1\n---\n\n"
        "## Event: 2026-01-01 – Two\n\nbeta body\n",
        encoding="utf-8",
    )
    from wordpipe.chronicle.merge import merge_files

    merged_md, _d, _c, _s = merge_files(
        [norm / "01_a.md", norm / "02_b.md"], conflict_mode="keep-both"
    )
    assert "Duplicate date" in merged_md
    (run_dir / "pipeline" / "merged.md").write_text(merged_md, encoding="utf-8")
    lineage = {
        "$schema": "event-lineage-v1",
        "topic": "t",
        "run_id": "r1",
        "events": [
            {
                "locator_kind": "markdown_section",
                "source_file": "a.md",
                "candidate_ordinal": 1,
                "heading_level": 2,
                "original_heading_text": "One",
                "staged_file": "01_a.md",
                "staged_event_ordinal": 1,
                "date": "2026-01-01",
                "title": "One",
                "source_event_id": "source_event:t:a",
                "body_sha256": None,
            },
            {
                "locator_kind": "markdown_section",
                "source_file": "b.md",
                "candidate_ordinal": 1,
                "heading_level": 2,
                "original_heading_text": "Two",
                "staged_file": "02_b.md",
                "staged_event_ordinal": 1,
                "date": "2026-01-01",
                "title": "Two",
                "source_event_id": "source_event:t:b",
                "body_sha256": None,
            },
        ],
    }
    correlation = runner.correlate_event_provenance(
        run_dir, lineage, topic="t", run_id="r1"
    )
    assert correlation["report_event_count"] == 2
    assert correlation["unmerged_source_event_count"] == 0
    assert correlation["survivor_verification"]["method"] == "merged-note-aware-v1"


def test_append_event_provenance_summary(tmp_path):
    summary = tmp_path / "RUN_SUMMARY.md"
    summary.write_text("# Summary\n\nStatus: PASS\n", encoding="utf-8")
    runner.append_event_provenance_summary(
        tmp_path,
        {
            "source_event_count": 2,
            "report_event_count": 1,
            "unmerged_source_event_count": 0,
            "ambiguous_matches": [],
        },
    )
    text = summary.read_text(encoding="utf-8")
    assert "## Event Provenance" in text
    assert "Source events: 2" in text
