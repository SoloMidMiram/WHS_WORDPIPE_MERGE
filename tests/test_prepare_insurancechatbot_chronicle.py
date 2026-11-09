import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "prepare_insurancechatbot_chronicle.py"
SPEC = importlib.util.spec_from_file_location("prepare_insurancechatbot_chronicle", MODULE_PATH)
prep = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = prep
SPEC.loader.exec_module(prep)


def test_commit_heading_with_timestamp_becomes_event():
    text = """# Commit history

## 6cb6634 — 2026-05-14T20:31:44+03:30

chore: initial commit — Insurance FAQ Knowledge Base

- 231 unique Persian FAQ pairs
"""
    events, lineage, candidates = prep.parse_commit_history(text)

    assert candidates == 1
    assert len(events) == 1
    assert len(lineage) == 1
    assert events[0].date == "2026-05-14"
    assert events[0].title == "6cb6634 - chore: initial commit — Insurance FAQ Knowledge Base"
    assert "Timestamp: 2026-05-14T20:31:44+03:30" in events[0].body
    assert lineage[0]["locator_kind"] == "commit_heading"
    assert lineage[0]["commit_sha"] == "6cb6634"


def test_mojibake_dash_in_commit_heading_is_normalized():
    text = """# Commit history

## caa148c ΓÇö 2026-05-15T09:40:21+03:30

Phase 5b: Deep Search KB expansion
"""
    events, lineage, candidates = prep.parse_commit_history(text)

    assert candidates == 1
    assert len(events) == 1
    assert len(lineage) == 1
    assert events[0].date == "2026-05-15"
    assert events[0].title == "caa148c - Phase 5b: Deep Search KB expansion"


def test_roadmap_section_without_date_uses_document_fallback_date():
    text = """# Roadmap
> Last reviewed: 2026-07-14

## Current snapshot

The runtime and retrieval work are active.
"""
    events, lineage, candidates = prep.parse_roadmap(text)

    assert candidates == 1
    assert len(events) == 1
    assert len(lineage) == 1
    assert events[0].date == "2026-07-14"
    assert events[0].title == "Current snapshot"


def test_prepare_writes_three_staged_files_and_metrics(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "staged"
    metrics_path = tmp_path / "prepare_metrics.json"
    input_dir.mkdir()
    (input_dir / prep.COMMIT_FILE).write_text(
        """# Commit history

## 6cb6634 — 2026-05-14T20:31:44+03:30

chore: initial commit — Insurance FAQ Knowledge Base
""",
        encoding="utf-8",
    )
    (input_dir / prep.DIGEST_FILE).write_text(
        """---
generated_at: "2026-07-05T13:06:57+03:30"
---

# Project Git History Digest

### Initial knowledge base and API

The project added FastAPI and a knowledge base.
""",
        encoding="utf-8",
    )
    (input_dir / prep.ROADMAP_FILE).write_text(
        """# Roadmap
> Last reviewed: 2026-07-14

## Current snapshot

Ontology and retrieval remain active.
""",
        encoding="utf-8",
    )

    metrics = prep.prepare(input_dir, output_dir, metrics_path)

    assert (output_dir / "01_commit_history.md").exists()
    assert (output_dir / "02_project_digest.md").exists()
    assert (output_dir / "03_roadmap.md").exists()
    assert metrics["input_file_count"] == 3
    assert metrics["candidate_commit_headings"] == 1
    assert metrics["staged_event_count"] == 3
    assert metrics["extraction_coverage_percent"] == 100.0
    assert "- **2026-05-14 - 6cb6634" in (output_dir / "01_commit_history.md").read_text(encoding="utf-8")

    assert metrics["staged_files"] == [
        "01_commit_history.md",
        "02_project_digest.md",
        "03_roadmap.md",
    ]
    lineage = metrics["source_lineage"]
    assert len(lineage) == 3
    assert [item["staged_file"] for item in lineage] == metrics["staged_files"]
    assert lineage[0]["source_file"] == prep.COMMIT_FILE
    assert lineage[1]["source_file"] == prep.DIGEST_FILE
    assert lineage[2]["source_file"] == prep.ROADMAP_FILE
    assert sum(item["candidate_count"] for item in lineage) == metrics["candidate_total_sections"]
    assert sum(item["staged_event_count"] for item in lineage) == metrics["staged_event_count"]
    assert metrics["event_lineage_file"] == prep.EVENT_LINEAGE_FILENAME
    event_lineage_path = metrics_path.parent / prep.EVENT_LINEAGE_FILENAME
    assert event_lineage_path.is_file()
    event_lineage = json.loads(event_lineage_path.read_text(encoding="utf-8"))
    assert len(event_lineage["events"]) == metrics["staged_event_count"]
    assert all("source_event_id" not in item for item in event_lineage["events"])
    assert all("topic" not in item for item in event_lineage["events"])


def test_prepare_ignores_unrelated_fourth_markdown_for_consumed_metrics(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "staged"
    metrics_path = tmp_path / "prepare_metrics.json"
    input_dir.mkdir()
    (input_dir / prep.COMMIT_FILE).write_text(
        """# Commit history

## 6cb6634 — 2026-05-14T20:31:44+03:30

chore: initial commit — Insurance FAQ Knowledge Base
""",
        encoding="utf-8",
    )
    (input_dir / prep.DIGEST_FILE).write_text(
        """---
generated_at: "2026-07-05T13:06:57+03:30"
---

# Project Git History Digest

### Initial knowledge base and API

The project added FastAPI and a knowledge base.
""",
        encoding="utf-8",
    )
    (input_dir / prep.ROADMAP_FILE).write_text(
        """# Roadmap
> Last reviewed: 2026-07-14

## Current snapshot

Ontology and retrieval remain active.
""",
        encoding="utf-8",
    )

    baseline = prep.prepare(input_dir, output_dir, metrics_path)
    (input_dir / "unrelated_notes.md").write_text(
        "# Unrelated\n\nThis file must not be consumed.\n" + ("x" * 500),
        encoding="utf-8",
    )
    again = prep.prepare(input_dir, output_dir, metrics_path)

    assert again["input_file_count"] == 3
    assert again["input_file_count"] == baseline["input_file_count"]
    assert again["input_total_bytes"] == baseline["input_total_bytes"]
    assert again["input_total_lines"] == baseline["input_total_lines"]
    assert again["source_lineage"] == baseline["source_lineage"]
    assert again["staged_event_count"] == baseline["staged_event_count"]


def test_staged_iso_date_round_trips_through_chronicle_ingest():
    from wordpipe.chronicle.ingest import split_into_events

    staged = """# InsuranceChatbot Commit History

## July 2026

- **2026-05-14 - 6cb6634 - chore: initial commit - Insurance FAQ Knowledge Base:** Timestamp: 2026-05-14T20:31:44+03:30

* **Nested bold bullet:** preserved as body, not a new event.
"""

    events = split_into_events(staged)[0]

    assert len(events) == 1
    assert events[0]["date"] == "2026-05-14"
    assert events[0]["title"] == "6cb6634 - chore: initial commit - Insurance FAQ Knowledge Base"
    assert "Nested bold bullet" in events[0]["body"]
