"""Acceptance tests for third-wave P0/P1 remediation.

Covers all decisive acceptance gates per the remediation plan.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, List

import pytest

from wordpipe.chronicle.ingest import (
    REASON_MISSING_EVENT_DATE,
    split_into_events,
)


# ==============================================================================
# F1 — Ingest rejection manifest tests
# ==============================================================================


def test_ingest_mixed_undated_fails_no_output(tmp_path: Path) -> None:
    """Mixed dated/undated input without --allow-undated -> exit 1,
    no normalized output, rejection manifest exists."""
    md = tmp_path / "input.md"
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **2025-01-01 - Dated Event:** body text
        - **unknown - Bad Event:** undated body
        - **2025-01-02 - Another Dated:** more body
        """),
        encoding="utf-8",
    )

    out = tmp_path / "output.md"
    result = subprocess.run(
        [sys.executable, "-m", "wordpipe.chronicle.cli.ingest",
         "--input", str(md), "--output", str(out)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"
    # No normalized output should exist
    assert not out.exists(), "Normalized output should not exist when undated events present"
    # Rejection manifest should exist
    manifest_path = out.with_suffix(".rejections.json")
    assert manifest_path.exists(), "Rejection manifest should exist"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["manifest_type"] == "complete"
    assert manifest["accepted_event_count"] == 2
    assert manifest["rejected_event_count"] == 1


def test_ingest_allow_undated_has_partial_output_and_manifest(tmp_path: Path) -> None:
    """Mixed input with --allow-undated -> exit 0, partial output,
    partial manifest."""
    md = tmp_path / "input.md"
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **2025-01-01 - Dated Event:** body text
        - **unknown - Bad Event:** undated body
        """),
        encoding="utf-8",
    )

    out = tmp_path / "output.md"
    result = subprocess.run(
        [sys.executable, "-m", "wordpipe.chronicle.cli.ingest",
         "--input", str(md), "--output", str(out), "--allow-undated"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}: {result.stderr}"
    assert out.exists(), "Normalized output should exist"
    manifest_path = out.with_suffix(".rejections.json")
    assert manifest_path.exists(), "Rejection manifest should exist"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["manifest_type"] == "partial"
    assert manifest["accepted_event_count"] == 1
    assert manifest["rejected_event_count"] == 1


def test_ingest_all_undated_partial_keeps_only_overview(tmp_path: Path) -> None:
    md = tmp_path / "input.md"
    md.write_text(
        "# Source\n\nOverview to preserve.\n\n"
        "  - **unknown - First:** body one\n"
        "    continuation of body one\n"
        "- **TBD - Second:** body two\n",
        encoding="utf-8",
    )
    out = tmp_path / "output.md"
    result = subprocess.run(
        [sys.executable, "-m", "wordpipe.chronicle.cli.ingest",
         "--input", str(md), "--output", str(out), "--allow-undated"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    normalized = out.read_text(encoding="utf-8")
    assert "event_count: 0" in normalized
    assert "> **Overview:** Overview to preserve." in normalized
    assert "First" not in normalized
    assert "Second" not in normalized
    assert "body one" not in normalized
    assert "body two" not in normalized
    manifest = json.loads(out.with_suffix(".rejections.json").read_text(encoding="utf-8"))
    assert manifest["manifest_type"] == "partial"
    assert manifest["accepted_event_count"] == 0
    assert manifest["rejected_event_count"] == 2
    assert [record["rejected_body"] for record in manifest["rejected_events"]] == [
        "body one\n    continuation of body one", "body two",
    ]


def test_ingest_all_undated_fails_no_output(tmp_path: Path) -> None:
    """Entirely undated input -> exit 1, no output, complete manifest."""
    md = tmp_path / "input.md"
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **unknown - First:** body one
        - **TBD - Second:** body two
        """),
        encoding="utf-8",
    )

    out = tmp_path / "output.md"
    result = subprocess.run(
        [sys.executable, "-m", "wordpipe.chronicle.cli.ingest",
         "--input", str(md), "--output", str(out)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"
    assert not out.exists(), "Normalized output should not exist"
    manifest_path = out.with_suffix(".rejections.json")
    assert manifest_path.exists(), "Rejection manifest should exist"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["manifest_type"] == "complete"
    assert manifest["accepted_event_count"] == 0
    assert manifest["rejected_event_count"] == 2


def test_ingest_rejection_manifest_structured(tmp_path: Path) -> None:
    """Rejection manifest JSON has required fields."""
    md = tmp_path / "input.md"
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **unknown - Bad Event:** undated body
        """),
        encoding="utf-8",
    )

    _, rejections = split_into_events(md.read_text(encoding="utf-8"))
    assert len(rejections) == 1
    rec = rejections[0]
    assert "input_file" in rec
    assert "line_number" in rec
    assert "event_index" in rec
    assert "raw_heading" in rec
    assert "rejected_body" in rec
    assert rec["reason_code"] == REASON_MISSING_EVENT_DATE
    assert rec["event_index"] == 1


def test_ingest_rejection_preserves_multiline_body(tmp_path: Path) -> None:
    """Undated heading accumulates continuation lines into rejected_body."""
    md = tmp_path / "input.md"
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **unknown - Bad Event:** undated body
          continuation line 1
          continuation line 2
        """),
        encoding="utf-8",
    )

    _, rejections = split_into_events(md.read_text(encoding="utf-8"))
    assert len(rejections) == 1
    body = rejections[0]["rejected_body"]
    assert "undated body" in body
    assert "continuation line 1" in body
    assert "continuation line 2" in body


def test_ingest_no_undated_no_manifest(tmp_path: Path) -> None:
    """Zero undated events -> no rejection manifest, normal behavior."""
    md = tmp_path / "input.md"
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **2025-01-01 - Dated Event:** body text
        """),
        encoding="utf-8",
    )

    _, rejections = split_into_events(md.read_text(encoding="utf-8"))
    assert len(rejections) == 0


def test_ingest_date_override_accepts_undated(tmp_path: Path) -> None:
    """--date-override applies to undated events instead of rejecting them."""
    md = tmp_path / "input.md"
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **unknown - Bad Event:** undated body
        - **TBD - Second:** body two
        """),
        encoding="utf-8",
    )

    out = tmp_path / "output.md"
    result = subprocess.run(
        [sys.executable, "-m", "wordpipe.chronicle.cli.ingest",
         "--input", str(md), "--output", str(out),
         "--date-override", "2025-03-15"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert "2025-03-15" in out.read_text(encoding="utf-8")
    assert not out.with_suffix(".rejections.json").exists()


def test_ingest_clean_run_removes_stale_manifest(tmp_path: Path) -> None:
    """A clean run over a reused output path removes a stale rejection manifest."""
    md = tmp_path / "input.md"
    out = tmp_path / "output.md"
    manifest = out.with_suffix(".rejections.json")

    # First run: undated -> manifest written (exit 1 before normalized output).
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **unknown - Bad Event:** undated body
        """),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "wordpipe.chronicle.cli.ingest",
         "--input", str(md), "--output", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert manifest.exists()

    # Second run: fully dated -> stale manifest removed, normalized output valid.
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **2025-01-01 - Dated Event:** body text
        """),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "wordpipe.chronicle.cli.ingest",
         "--input", str(md), "--output", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert not manifest.exists()
    assert out.exists()


def test_ingest_stale_manifest_removed_after_clean_write(tmp_path: Path) -> None:
    """A clean run over a reused output path removes the stale rejection
    manifest only after the normalized output write succeeds (ordering fix)."""
    md = tmp_path / "input.md"
    out = tmp_path / "output.md"
    manifest = out.with_suffix(".rejections.json")

    # First run: mixed dated/undated with --allow-undated -> partial output
    # plus a rejection manifest (exit 0).
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **2025-01-01 - Dated Event:** body text
        - **unknown - Bad Event:** undated body
        """),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "wordpipe.chronicle.cli.ingest",
         "--input", str(md), "--output", str(out), "--allow-undated"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert manifest.exists()

    # Second run: fully dated input into the same output path -> stale
    # manifest removed, normalized output valid.
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **2025-02-02 - Clean Event:** clean body
        """),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "wordpipe.chronicle.cli.ingest",
         "--input", str(md), "--output", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert not manifest.exists(), "Stale rejection manifest should be removed"
    content = out.read_text(encoding="utf-8")
    assert "## Event: 2025-02-02" in content
    assert "event_count: 1" in content


def test_ingest_stale_manifest_preserved_on_write_failure(tmp_path: Path) -> None:
    """A failed normalized-output write must not delete the stale rejection
    manifest: cleanup runs only after the output write succeeds."""
    md = tmp_path / "input.md"
    out = tmp_path / "output.md"
    manifest = out.with_suffix(".rejections.json")

    # First run: undated input -> stale rejection manifest exists.
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **unknown - Bad Event:** undated body
        """),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "wordpipe.chronicle.cli.ingest",
         "--input", str(md), "--output", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert manifest.exists()

    # Replace the output path with a directory so the next write_text
    # deterministically raises.
    out.mkdir()

    # Second run: fully dated input -> output write fails, but the stale
    # rejection manifest must survive.
    md.write_text(
        textwrap.dedent("""\
        # Source

        - **2025-03-03 - Dated Event:** body text
        """),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "wordpipe.chronicle.cli.ingest",
         "--input", str(md), "--output", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, "Output write should have failed"
    assert manifest.exists(), "Stale manifest must survive a failed output write"


# ==============================================================================
# F2 — Flatten preflight
# ==============================================================================


def test_flatten_unavailable_blocks_before_output(monkeypatch, tmp_path) -> None:
    """do_flatten=True with unavailable flattener -> RuntimeError before output."""
    from wordpipe.adapters import defaults
    from wordpipe.adapters.flatteners.base import _UnavailableFlattener
    from wordpipe.core.datatypes import PipelineConfig

    monkeypatch.setattr(
        defaults,
        "make_flattener",
        lambda prefer_win32: _UnavailableFlattener(reason="forced unavailable"),
    )
    cfg = PipelineConfig(
        in_path=tmp_path / "in.docx",
        out_path=tmp_path / "out.docx",
        do_flatten=True,
        prefer_win32=True,
    )

    with pytest.raises(RuntimeError, match="Flattening requested"):
        defaults.build_default_deps(cfg)
    assert not cfg.out_path.exists()


def test_available_flattener_wiring(monkeypatch, tmp_path: Path) -> None:
    from wordpipe.adapters import defaults
    from wordpipe.adapters.transforms import LegacyFlattenerAdapter
    from wordpipe.core.datatypes import PipelineConfig

    calls = []

    class AvailableFlattener:
        def run(self, source, destination, *, limit_pages=None):
            calls.append((source, destination, limit_pages))
            return []

    monkeypatch.setattr(defaults, "make_flattener", lambda prefer_win32: AvailableFlattener())
    monkeypatch.setattr(defaults, "_can_import_mergedpipeline", lambda: False)
    cfg = PipelineConfig(
        in_path=tmp_path / "in.docx",
        out_path=tmp_path / "out.docx",
        do_flatten=True,
    )
    deps = defaults.build_default_deps(cfg)
    assert isinstance(deps.flattener, LegacyFlattenerAdapter)
    assert deps.toc_updater is None
    assert deps.flattener.flatten(cfg.in_path, cfg.out_path, limit_pages=2) == []
    assert calls == [(cfg.in_path, cfg.out_path, 2)]


# ==============================================================================
# F3 — Source coverage parser
# ==============================================================================


def test_source_coverage_numbered_format(tmp_path: Path) -> None:
    """Numbered format (| Number | Source | Count |) parses correctly."""
    from pipeline.index import build_source_manifest

    coverage = tmp_path / "coverage.md"
    coverage.write_text(
        textwrap.dedent("""\
        | Number | Source | Count |
        |--------|--------|-------|
        | 1 | Alpha | 5 |
        | 2 | Beta | 3 |
        """),
        encoding="utf-8",
    )

    manifest = build_source_manifest([], source_coverage_path=coverage)
    assert len(manifest["sources"]) == 2
    assert manifest["sources"][0]["name"] == "Alpha"
    assert manifest["sources"][0]["event_count"] == 5


def test_source_coverage_unnumbered_format(tmp_path: Path) -> None:
    """Un-numbered format (| Source | Unique Events | Duplicates | Status |) parses correctly."""
    from pipeline.index import build_source_manifest

    coverage = tmp_path / "coverage.md"
    coverage.write_text(
        textwrap.dedent("""\
        | Source | Unique Events | Duplicates | Status |
        |--------|--------------|------------|--------|
        | Alpha | 5 | 0 | ok |
        | Beta | 0 | 0 | no events |
        """),
        encoding="utf-8",
    )

    manifest = build_source_manifest([], source_coverage_path=coverage)
    assert len(manifest["sources"]) == 2
    # Check zero-event sources are preserved
    assert manifest["sources_without_events"] == 1
    assert manifest["sources"][1]["name"] == "Beta"
    assert manifest["sources"][1]["event_count"] == 0
    assert manifest["sources"][1]["status"] == "no events"


def test_source_coverage_malformed_raises(tmp_path: Path) -> None:
    """Malformed coverage file raises ValueError."""
    from pipeline.index import build_source_manifest

    coverage = tmp_path / "bad_coverage.md"
    coverage.write_text(
        textwrap.dedent("""\
        # Not a table
        Some random text.
        """),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="source coverage"):
        build_source_manifest([], source_coverage_path=coverage)


# ==============================================================================
# F4 — Dedup default
# ==============================================================================


def test_dedup_date_title_keeps_same_title_different_dates() -> None:
    """With date_title dedup, same title on different dates -> both survive."""
    from pipeline.index import deduplicate_events

    events = [
        {"date": "2025-01-01", "title": "Outage", "body": "a", "sources": ["src1"]},
        {"date": "2025-01-02", "title": "Outage", "body": "b", "sources": ["src1"]},
    ]

    result = deduplicate_events(events, method="date_title")
    assert len(result) == 2, "Both events should survive with date_title dedup"


def test_dedup_date_title_default_used() -> None:
    """Default dedup method preserves same-title different-date events."""
    from pipeline.index import DEFAULT_CONFIG

    assert DEFAULT_CONFIG["dedup_method"] == "date_title"


# ==============================================================================
# F5 — Heading sibling context
# ==============================================================================


def test_heading_sibling_transition(tmp_path: Path) -> None:
    """Sibling H2/H3 transitions produce correct context in both paths."""
    pytest.importorskip("docx")
    from docx import Document

    doc = Document()
    doc.add_heading("Title", level=1)
    doc.add_heading("First section", level=2)
    doc.add_heading("Subsection under A", level=3)
    doc.add_paragraph("paragraph content")
    doc.add_heading("Second section", level=2)
    doc.add_paragraph("paragraph content")
    doc.add_heading("Subsection under B", level=3)
    doc.add_paragraph("paragraph content")

    from wordpipe.adapters.docx.segmenter import (
        _build_hpath,
        _precompute_heading_states,
    )

    # Test precomputed path
    states = _precompute_heading_states(doc)
    # Paragraph under H3-A (index 3):
    # H1: Title, H2: First section, H3: Subsection under A
    assert states[3][1] == "First section", f"Expected H2=First section, got {states[3][1]}"
    assert states[3][2] == "Subsection under A", f"Expected H3=Subsection under A, got {states[3][2]}"

    # Paragraph after H2-B (index 5, before H3-B):
    # H1: Title, H2: Second section, H3: None
    assert states[5][1] == "Second section", f"Expected H2=Second section, got {states[5][1]}"
    assert states[5][2] is None, f"Expected H3=None, got {states[5][2]}"

    # Paragraph under H3-B (index 7):
    # H1: Title, H2: Second section, H3: Subsection under B
    assert states[7][1] == "Second section", f"Expected H2=Second section, got {states[7][1]}"
    assert states[7][2] == "Subsection under B", f"Expected H3=Subsection under B, got {states[7][2]}"

    # Test legacy path
    hpath_h3a = _build_hpath(doc, 3)
    assert "H2: First section" in hpath_h3a[1]
    assert "H3: Subsection under A" in hpath_h3a[1]

    hpath_h2b = _build_hpath(doc, 5)
    assert "H2: Second section" in hpath_h2b[1]
    assert "H3: Subsection" not in hpath_h2b[1], "Legacy path should not include H3 after H2 transition"

    hpath_h3b = _build_hpath(doc, 7)
    assert "H2: Second section" in hpath_h3b[1]
    assert "H3: Subsection under B" in hpath_h3b[1]
