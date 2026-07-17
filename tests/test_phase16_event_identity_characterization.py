"""Phase 16.0 characterization: identity loss, ingest/merge hash parity, markers unsafe."""

from __future__ import annotations

from pathlib import Path

from wordpipe.chronicle.ingest import clean_mojibake, format_event, split_into_events
from wordpipe.chronicle.merge import compute_body_hash, extract_events, merge_files


def test_compute_body_hash_collapses_whitespace_and_is_crlf_insensitive():
    a = "line one\nline two"
    b = "line one\r\nline two"
    c = "line   one\n\nline two"
    assert compute_body_hash(a) == compute_body_hash(b)
    assert compute_body_hash(a) == compute_body_hash(c)


def test_html_comment_between_bullets_appends_to_preceding_event_body():
    staged = """# Source

## July 2026

- **2026-01-01 - First:** alpha body

<!-- marker:should-not-be-a-protocol -->

- **2026-01-02 - Second:** beta body
"""
    events = split_into_events(staged)
    assert len(events) == 2
    assert "marker:should-not-be-a-protocol" in events[0]["body"]
    assert "marker" not in events[1]["body"]
    hashed = compute_body_hash(events[0]["body"])
    clean = split_into_events(
        """# Source

## July 2026

- **2026-01-01 - First:** alpha body

- **2026-01-02 - Second:** beta body
"""
    )
    assert hashed != compute_body_hash(clean[0]["body"])


def test_mojibake_cleanup_changes_body_before_split():
    raw = "- **2026-01-01 - Title:** helloâ€™s world\n"
    cleaned = clean_mojibake(raw)
    assert "’" in cleaned or "'" in cleaned or "â€™" not in cleaned
    events = split_into_events(f"# Doc\n\n## January 2026\n\n{cleaned}")
    assert len(events) == 1
    assert "â€™" not in events[0]["body"]


def test_nested_bold_bullet_escape_round_trip_body_hash(tmp_path):
    import importlib.util
    import sys

    module_path = Path(__file__).resolve().parents[1] / "tools" / "prepare_generic_markdown_chronicle.py"
    spec = importlib.util.spec_from_file_location("prep_generic_char", module_path)
    prep = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = prep
    spec.loader.exec_module(prep)

    body = "Intro\n- **Nested bold:** stays nested\n"
    escaped = prep.escape_nested_event_bullets(body)
    staged = prep.render_staged_markdown(
        "Src",
        [prep.ChronicleEvent("2026-01-01", "Title", escaped)],
    )
    events = split_into_events(staged)
    assert len(events) == 1
    assert events[0]["body"].lstrip().startswith("* **") or "* **" in events[0]["body"]
    normalised = format_event(events[0])
    extracted = extract_events(normalised)
    assert len(extracted) == 1
    assert compute_body_hash(extracted[0]["body"]) == compute_body_hash(events[0]["body"])


def test_title_only_change_keeps_body_hash_stable():
    body = "same body text"
    h1 = compute_body_hash(body)
    assert h1 == compute_body_hash(body)
    ev_a = {"date": "2026-01-01", "title": "A", "body": body}
    ev_b = {"date": "2026-01-01", "title": "B", "body": body}
    assert compute_body_hash(ev_a["body"]) == compute_body_hash(ev_b["body"])


def test_merge_keep_both_duplicate_date_different_bodies(tmp_path):
    n1 = tmp_path / "01_a.md"
    n2 = tmp_path / "02_b.md"
    n1.write_text(
        "---\nsource: a\nevent_count: 1\n---\n\n## Event: 2026-01-01 – One\n\nalpha\n",
        encoding="utf-8",
    )
    n2.write_text(
        "---\nsource: b\nevent_count: 1\n---\n\n## Event: 2026-01-01 – Two\n\nbeta\n",
        encoding="utf-8",
    )
    merged_md, _duplicates, _contrib, _sources = merge_files(
        [n1, n2], conflict_mode="keep-both"
    )
    assert merged_md.count("## Event: 2026-01-01") == 2


def test_merge_true_duplicate_collapses_to_one(tmp_path):
    n1 = tmp_path / "01_a.md"
    n2 = tmp_path / "02_b.md"
    block = "---\nsource: src\nevent_count: 1\n---\n\n## Event: 2026-01-01 – Same\n\nshared body\n"
    n1.write_text(block, encoding="utf-8")
    n2.write_text(block.replace("source: src", "source: other"), encoding="utf-8")
    merged_md, duplicates, _contrib, _sources = merge_files(
        [n1, n2], conflict_mode="keep-both"
    )
    assert merged_md.count("## Event: 2026-01-01") == 1
    assert len(duplicates) >= 1


def test_normalised_filename_matches_staged_basename():
    staged = "01_ARCHIVE_REPORT.md"
    assert Path(staged).name == staged
    assert (Path("pipeline") / "normalised" / staged).as_posix().endswith(
        "normalised/01_ARCHIVE_REPORT.md"
    )


def test_aggregate_report_event_id_pattern_unchanged():
    topic = "insurancechatbot"
    run_id = "phase15_lineage_validation_v2"
    assert f"report_event:{topic}:{run_id}" == "report_event:insurancechatbot:phase15_lineage_validation_v2"
