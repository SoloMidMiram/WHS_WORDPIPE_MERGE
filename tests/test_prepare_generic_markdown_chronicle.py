"""Tests for the generic Markdown section adapter (tools/prepare_generic_markdown_chronicle.py)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "prepare_generic_markdown_chronicle.py"
SPEC = importlib.util.spec_from_file_location("prepare_generic_markdown_chronicle", MODULE_PATH)
adapter = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = adapter
SPEC.loader.exec_module(adapter)


# ---------------------------------------------------------------------------
# Section splitting and source labelling
# ---------------------------------------------------------------------------


def test_source_label_from_filename():
    assert "knowledge base" in adapter.source_label("Knowledge_Base.md").lower()
    assert adapter.source_label("2025-08-06-project_activity_summary.md") == "project activity summary"
    assert adapter.source_label("README.md") == "README"
    assert adapter.source_label("ARCHIVE_REPORT.md") == "ARCHIVE REPORT"


def test_split_sections():
    text = """# Top

## Section One

Content for one.

## Section Two

Content for two.
"""
    sections = adapter.split_sections(text, heading_levels=(2,))
    assert len(sections) == 2
    assert sections[0][0] == "Section One"
    assert "Content for one" in sections[0][1]
    assert sections[1][0] == "Section Two"
    assert "Content for two" in sections[1][1]


def test_split_sections_skips_h1_and_h4():
    text = """# Top

## Section A

Body A

### Subsection A1

Body A1

#### Ignored

Body ignored
"""
    sections = adapter.split_sections(text, heading_levels=(2, 3))
    titles = [s[0] for s in sections]
    assert "Top" not in titles
    assert "Section A" in titles
    assert "Subsection A1" in titles
    assert "Ignored" not in titles


def test_production_heading_policy_keeps_nested_headings_in_parent(tmp_path):
    md_file = tmp_path / "nested.md"
    md_file.write_text(
        "# Top\n\n## Parent\n\nParent body.\n\n### Child\n\nChild body.\n",
        encoding="utf-8",
    )

    events, lineage, candidates = adapter.parse_file(md_file)

    assert candidates == 1
    assert len(events) == 1
    assert len(lineage) == 1
    assert "### Child" in events[0].body
    assert "Child body." in events[0].body


# ---------------------------------------------------------------------------
# Date extraction
# ---------------------------------------------------------------------------


def test_first_date_finds_iso():
    text = "Some text with 2025-08-06 date"
    assert adapter.first_date(text) == "2025-08-06"


def test_first_date_falls_back():
    text = "No dates here at all"
    assert adapter.first_date(text) == adapter.DEFAULT_FALLBACK_DATE


# ---------------------------------------------------------------------------
# parse_file
# ---------------------------------------------------------------------------


def test_parse_file_creates_events(tmp_path):
    md_file = tmp_path / "test_topic.md"
    md_file.write_text(
        "# Test\n\n"
        "## First Section\n\n"
        "Content with 2025-06-15 date.\n\n"
        "## Second Section\n\n"
        "Content with 2025-06-20 date.\n",
        encoding="utf-8",
    )
    events, lineage, candidates = adapter.parse_file(md_file, heading_levels=(2,))
    assert candidates == 2
    assert len(events) == 2
    assert len(lineage) == 2
    assert events[0].date == "2025-06-15"
    assert "First Section" in events[0].title
    assert events[1].date == "2025-06-20"
    assert "Second Section" in events[1].title
    assert lineage[0]["candidate_ordinal"] == 1
    assert lineage[1]["candidate_ordinal"] == 2


def test_parse_file_prefixes_title_with_source_label(tmp_path):
    md_file = tmp_path / "2025-08-06-ChatGPTLitrature.md"
    md_file.write_text(
        "# ChatGPT\n\n"
        "## History of AI\n\n"
        "Body with 2025-07-01 date.\n",
        encoding="utf-8",
    )
    events, _, _ = adapter.parse_file(md_file, heading_levels=(2,))
    assert len(events) == 1
    # Should contain the source label prefix
    assert "ChatGPTLitrature" in events[0].title or "ChatGPT" in events[0].title


def test_parse_file_empty_section_advances_candidate_ordinal(tmp_path):
    md_file = tmp_path / "empty_section.md"
    md_file.write_text(
        "# Doc\n\n## Empty\n\n## Filled\n\nBody with 2025-01-01 date.\n",
        encoding="utf-8",
    )
    events, lineage, candidates = adapter.parse_file(md_file, heading_levels=(2,))
    assert candidates == 2
    assert len(events) == 1
    assert len(lineage) == 1
    assert lineage[0]["candidate_ordinal"] == 2
    assert lineage[0]["staged_event_ordinal"] == 1


# ---------------------------------------------------------------------------
# render_staged_markdown and escape_nested_bullets
# ---------------------------------------------------------------------------


def test_render_staged_markdown_format():
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Event:
        date: str
        title: str
        body: str

    events = [
        Event("2025-06-01", "Test Event", "Some body text."),
    ]
    rendered = adapter.render_staged_markdown("TestSource", events)
    assert "# TestSource" in rendered
    assert "## June 2025" in rendered
    assert "- **2025-06-01 - Test Event:** Some body text." in rendered


def test_render_staged_markdown_changes_month_without_reordering_events():
    events = [
        adapter.ChronicleEvent("2025-06-30", "First", "First body."),
        adapter.ChronicleEvent("2024-01-01", "Second", "Second body."),
        adapter.ChronicleEvent("2025-06-01", "Third", "Third body."),
    ]

    rendered = adapter.render_staged_markdown("Mixed", events)

    assert "## June 2025" in rendered
    assert "## January 2024" in rendered
    assert rendered.index("First:") < rendered.index("Second:") < rendered.index("Third:")
    assert rendered.count("## June 2025") == 2


def test_escape_nested_event_bullets_hides_bold_bullets():
    body = "- **original bold:** content\n- regular line"
    escaped = adapter.escape_nested_event_bullets(body)
    lines = escaped.splitlines()
    assert lines[0].startswith("* **")
    assert lines[0].lstrip().startswith("* **")
    assert "original bold" in escaped
    assert "- regular line" in escaped


# ---------------------------------------------------------------------------
# prepare writes staged files and metrics
# ---------------------------------------------------------------------------


def test_prepare_writes_staged_files_and_metrics(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "staged"
    metrics_path = tmp_path / "prepare_metrics.json"
    input_dir.mkdir()

    (input_dir / "01_first_doc.md").write_text(
        "# First\n\n## Alpha\n\nContent 2025-07-01.\n\n## Beta\n\nContent 2025-07-02.\n",
        encoding="utf-8",
    )
    (input_dir / "02_second_doc.md").write_text(
        "# Second\n\n## Gamma\n\nContent 2025-07-03.\n",
        encoding="utf-8",
    )

    metrics = adapter.prepare(input_dir, output_dir, metrics_path)

    assert metrics["input_file_count"] == 2
    assert metrics["candidate_total_sections"] == 3
    assert metrics["staged_event_count"] == 3
    assert metrics["extraction_coverage_percent"] == 100.0
    assert len(metrics["staged_files"]) == 2  # two staged output files
    assert metrics["adapter"] == "prepare_generic_markdown_chronicle"

    lineage = metrics["source_lineage"]
    assert len(lineage) == 2
    assert [item["staged_file"] for item in lineage] == metrics["staged_files"]
    assert lineage[0]["source_file"] == "01_first_doc.md"
    assert lineage[1]["source_file"] == "02_second_doc.md"
    assert lineage[0]["candidate_count"] == 2
    assert lineage[0]["staged_event_count"] == 2
    assert lineage[1]["candidate_count"] == 1
    assert lineage[1]["staged_event_count"] == 1
    assert sum(item["candidate_count"] for item in lineage) == metrics["candidate_total_sections"]
    assert sum(item["staged_event_count"] for item in lineage) == metrics["staged_event_count"]
    assert "file_metrics" in metrics

    # Verify staged files exist
    for sf in metrics["staged_files"]:
        assert (output_dir / sf).exists()

    # Verify metrics JSON was written
    assert metrics_path.is_file()
    saved = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert saved["staged_event_count"] == 3
    assert saved["source_lineage"] == lineage
    assert metrics["event_lineage_file"] == adapter.EVENT_LINEAGE_FILENAME
    event_lineage = json.loads(
        (metrics_path.parent / adapter.EVENT_LINEAGE_FILENAME).read_text(encoding="utf-8")
    )
    assert len(event_lineage["events"]) == 3
    assert all(item.get("staged_file") for item in event_lineage["events"])
    assert all("source_event_id" not in item for item in event_lineage["events"])


# ---------------------------------------------------------------------------
# Staged output round-trips through Chronicle ingest
# ---------------------------------------------------------------------------


def test_staged_output_round_trips_through_ingest():
    from wordpipe.chronicle.ingest import split_into_events

    staged = adapter.render_staged_markdown(
        "TestSource",
        [adapter.ChronicleEvent("2025-06-14", "Test - Alpha section", "Section body text.")],
    )

    events = split_into_events(staged)

    assert len(events) == 1
    assert events[0]["date"] == "2025-06-14"
    assert "Alpha section" in events[0]["title"]
    assert "Section body text" in events[0]["body"]


def test_summarize_uses_manifest_topic_from_prepare_metrics(tmp_path):
    run_dir = tmp_path / "run"
    pipeline_dir = run_dir / "pipeline"
    pipeline_dir.mkdir(parents=True)
    (pipeline_dir / "merged.md").write_text("event_count: 1\n", encoding="utf-8")
    (pipeline_dir / "chronicle_tagged.md").write_text(
        "event_count: 1\n<!-- themes: Example -->\n", encoding="utf-8"
    )
    (pipeline_dir / "merged.duplicates.json").write_text("[]\n", encoding="utf-8")
    prepare_metrics = run_dir / "prepare_metrics.json"
    prepare_metrics.write_text(
        json.dumps({
            "topic": "third-topic",
            "input_file_count": 1,
            "input_total_bytes": 1,
            "input_total_lines": 1,
            "candidate_total_sections": 1,
            "staged_event_count": 1,
            "extraction_coverage_percent": 100.0,
        }),
        encoding="utf-8",
    )
    performance = run_dir / "performance.txt"
    performance.write_text("TotalSeconds : 1\n", encoding="utf-8")
    run_log = run_dir / "run.log"
    run_log.write_text("", encoding="utf-8")

    metrics = adapter.summarize_run(run_dir, prepare_metrics, performance, run_log)
    summary = (run_dir / "RUN_SUMMARY.md").read_text(encoding="utf-8")

    assert metrics["topic"] == "third-topic"
    assert summary.startswith("# third-topic Report Run Summary")
    assert "Pipeline Chronicle" not in summary
