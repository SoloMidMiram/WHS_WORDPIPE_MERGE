"""Phase 17 survivor verification: merge-note-aware actual key checks."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from wordpipe.chronicle.merge import compute_body_hash, extract_events, merge_files, parse_yaml_frontmatter

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "run_topic_report.py"
SPEC = importlib.util.spec_from_file_location("run_topic_report_phase17", MODULE_PATH)
runner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


def _norm_file(path: Path, *, source: str, date: str, title: str, body: str) -> None:
    path.write_text(
        f"---\nsource: {source}\nevent_count: 1\n---\n\n"
        f"## Event: {date} – {title}\n\n{body}\n",
        encoding="utf-8",
    )


def _lineage_for_staged(entries: list[tuple[str, str, str, str]]) -> dict:
    """entries: (staged_file, source_event_id, date, title)"""
    events = []
    for ordinal, (staged, sid, date, title) in enumerate(entries, start=1):
        events.append({
            "locator_kind": "markdown_section",
            "source_file": f"{staged}.src",
            "candidate_ordinal": 1,
            "heading_level": 2,
            "original_heading_text": title,
            "staged_file": staged,
            "staged_event_ordinal": 1 if staged.count("_") else ordinal,
            "date": date,
            "title": title,
            "source_event_id": sid,
            "body_sha256": None,
        })
    # Fix staged ordinals per file
    by_file: dict[str, int] = {}
    fixed = []
    for ev in events:
        sf = ev["staged_file"]
        by_file[sf] = by_file.get(sf, 0) + 1
        ev = dict(ev)
        ev["staged_event_ordinal"] = by_file[sf]
        fixed.append(ev)
    return {"$schema": "event-lineage-v1", "topic": "t", "run_id": "r1", "events": fixed}


def test_strip_real_merge_keep_both_output(tmp_path):
    a = tmp_path / "01_a.md"
    b = tmp_path / "02_b.md"
    _norm_file(a, source="a", date="2026-01-01", title="One", body="alpha body")
    _norm_file(b, source="b", date="2026-01-01", title="Two", body="beta body")
    merged_md, _, _, _ = merge_files([a, b], conflict_mode="keep-both")
    assert runner.KEEP_BOTH_CONFLICT_NOTE in merged_md
    _, body = parse_yaml_frontmatter(merged_md)
    cleaned = runner.strip_keep_both_conflict_notes(body)
    assert runner.KEEP_BOTH_CONFLICT_NOTE not in cleaned
    events = extract_events(cleaned)
    assert len(events) == 2
    hashes = {compute_body_hash(ev["body"]) for ev in events}
    assert compute_body_hash("alpha body") in hashes
    assert compute_body_hash("beta body") in hashes


def test_strip_preserves_whitespace_only_blank_lines_lf_and_crlf():
    note = runner.KEEP_BOTH_CONFLICT_NOTE
    for blank in ("\n", "\r\n", "\n \n", "\r\n\t\r\n"):
        body = (
            f"## Event: 2026-01-01 – One\n\nalpha\n\n"
            f"{note}{blank}"
            f"## Event: 2026-01-01 – Two\n\nbeta\n"
        )
        cleaned = runner.strip_keep_both_conflict_notes(body)
        assert note not in cleaned
        assert len(extract_events(cleaned)) == 2


def test_strip_preserves_mid_body_and_different_date_note():
    note = runner.KEEP_BOTH_CONFLICT_NOTE
    mid = (
        f"## Event: 2026-01-01 – One\n\n"
        f"intro\n{note}\nstill body\n\n"
        f"## Event: 2026-01-02 – Two\n\nbeta\n"
    )
    cleaned = runner.strip_keep_both_conflict_notes(mid)
    assert note in cleaned
    assert "still body" in extract_events(cleaned)[0]["body"]

    different_date = (
        f"## Event: 2026-01-01 – One\n\nalpha\n\n"
        f"{note}\n"
        f"## Event: 2026-01-02 – Two\n\nbeta\n"
    )
    cleaned2 = runner.strip_keep_both_conflict_notes(different_date)
    assert note in cleaned2


def test_strip_ambiguous_body_ending_with_note_before_same_date_fails():
    note = runner.KEEP_BOTH_CONFLICT_NOTE
    body = (
        f"## Event: 2026-01-01 – One\n\n"
        f"alpha\n{note}\n\n"
        f"{note}\n"
        f"## Event: 2026-01-01 – Two\n\nbeta\n"
    )
    with pytest.raises(runner.ProvenanceError, match="ambiguous_merge_note_vs_body_content"):
        runner.strip_keep_both_conflict_notes(body)


def test_correlate_three_keep_both_same_date(tmp_path):
    run_dir = tmp_path / "run"
    norm = run_dir / "pipeline" / "normalised"
    norm.mkdir(parents=True)
    files = []
    entries = []
    for idx, (title, body) in enumerate(
        [("A", "body-a"), ("B", "body-b"), ("C", "body-c")], start=1
    ):
        path = norm / f"0{idx}_{title}.md"
        _norm_file(path, source=title.lower(), date="2026-02-01", title=title, body=body)
        files.append(path)
        entries.append((path.name, f"source_event:t:{title}", "2026-02-01", title))
    merged_md, _, _, _ = merge_files(files, conflict_mode="keep-both")
    (run_dir / "pipeline" / "merged.md").write_text(merged_md, encoding="utf-8")
    corr = runner.correlate_event_provenance(
        run_dir, _lineage_for_staged(entries), topic="t", run_id="r1"
    )
    assert corr["report_event_count"] == 3
    assert corr["unmerged_source_event_count"] == 0
    assert corr["survivor_verification"]["method"] == "merged-note-aware-v1"
    assert corr["survivor_verification"]["missing_key_count"] == 0
    assert corr["survivor_verification"]["unexpected_key_count"] == 0


def test_correlate_true_duplicate_mixed_with_conflict(tmp_path):
    run_dir = tmp_path / "run"
    norm = run_dir / "pipeline" / "normalised"
    norm.mkdir(parents=True)
    shared = "shared body"
    a = norm / "01_a.md"
    b = norm / "02_b.md"
    c = norm / "03_c.md"
    _norm_file(a, source="a", date="2026-03-01", title="Dup", body=shared)
    _norm_file(b, source="b", date="2026-03-01", title="Dup", body=shared)
    _norm_file(c, source="c", date="2026-03-01", title="Other", body="other body")
    merged_md, _, _, _ = merge_files([a, b, c], conflict_mode="keep-both")
    (run_dir / "pipeline" / "merged.md").write_text(merged_md, encoding="utf-8")
    lineage = _lineage_for_staged([
        ("01_a.md", "source_event:t:a", "2026-03-01", "Dup"),
        ("02_b.md", "source_event:t:b", "2026-03-01", "Dup"),
        ("03_c.md", "source_event:t:c", "2026-03-01", "Other"),
    ])
    corr = runner.correlate_event_provenance(run_dir, lineage, topic="t", run_id="r1")
    assert corr["source_event_count"] == 3
    assert corr["report_event_count"] == 2
    assert corr["unmerged_source_event_count"] == 0


def test_equal_count_substitution_fails(tmp_path):
    """Same heading count as expected, but one key swapped — must fail."""
    run_dir = tmp_path / "run"
    norm = run_dir / "pipeline" / "normalised"
    norm.mkdir(parents=True)
    a = norm / "01_a.md"
    b = norm / "02_b.md"
    _norm_file(a, source="a", date="2026-04-01", title="One", body="alpha")
    _norm_file(b, source="b", date="2026-04-01", title="Two", body="beta")
    merged_md, _, _, _ = merge_files([a, b], conflict_mode="keep-both")
    # Substitute second event body in merged.md while keeping two headings.
    _, body = parse_yaml_frontmatter(merged_md)
    cleaned = runner.strip_keep_both_conflict_notes(body)
    events = extract_events(cleaned)
    assert len(events) == 2
    # Rebuild merged with unexpected body for second event
    fake = (
        "---\nsources: [a, b]\nevent_count: 2\n---\n\n"
        f"{events[0]['block'].strip()}\n\n"
        f"## Event: 2026-04-01 – Two\n\nUNEXPECTED SUBSTITUTE\n"
    )
    (run_dir / "pipeline" / "merged.md").write_text(fake, encoding="utf-8")
    lineage = _lineage_for_staged([
        ("01_a.md", "source_event:t:a", "2026-04-01", "One"),
        ("02_b.md", "source_event:t:b", "2026-04-01", "Two"),
    ])
    with pytest.raises(runner.ProvenanceError, match="survivor key set mismatch"):
        runner.correlate_event_provenance(run_dir, lineage, topic="t", run_id="r1")


def test_correlate_conflict_pollution_fixture_reports_method(tmp_path):
    run_dir = tmp_path / "run"
    norm = run_dir / "pipeline" / "normalised"
    norm.mkdir(parents=True)
    a = norm / "01_a.md"
    b = norm / "02_b.md"
    _norm_file(a, source="a", date="2026-01-01", title="One", body="alpha body")
    _norm_file(b, source="b", date="2026-01-01", title="Two", body="beta body")
    merged_md, _, _, _ = merge_files([a, b], conflict_mode="keep-both")
    (run_dir / "pipeline" / "merged.md").write_text(merged_md, encoding="utf-8")
    lineage = _lineage_for_staged([
        ("01_a.md", "source_event:t:a", "2026-01-01", "One"),
        ("02_b.md", "source_event:t:b", "2026-01-01", "Two"),
    ])
    corr = runner.correlate_event_provenance(run_dir, lineage, topic="t", run_id="r1")
    assert corr["survivor_verification"]["method"] == "merged-note-aware-v1"
    assert corr["survivor_verification"]["parsed_event_count"] == 2
    assert corr["survivor_verification"]["raw_heading_count"] == 2
    assert corr["report_event_count"] == 2
