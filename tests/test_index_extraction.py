"""Characterization tests for the Chronicle index stage (pipeline/index.py).

These pin the observable behavior of the index logic before its pure seam is
extracted to ``wordpipe/chronicle/index.py``. They import through
``pipeline.index`` so the same tests also verify the thin-wrapper re-export
after extraction.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from pipeline.index import (
    DEFAULT_CONFIG,
    build_event_index,
    build_theme_index,
    deduplicate_events,
    extract_events_from_tagged,
    load_config,
    render_template,
)

TAGGED_MD = textwrap.dedent("""\
    ## Event: 2025-01-01 - Alpha Outage
    <!-- themes: api, outage -->
    First body with https://example.com link.

    ## Event: 2025-01-02 - Beta Bug
    <!-- themes: web -->
    Second body.
""")


def test_load_config_defaults_when_none(tmp_path: Path):
    cfg = load_config(None)
    assert cfg == DEFAULT_CONFIG
    assert load_config(tmp_path / "missing.json") == DEFAULT_CONFIG


def test_load_config_merges_json_overrides(tmp_path: Path):
    cfg_path = tmp_path / "index_config.json"
    cfg_path.write_text(json.dumps({"dedup_method": "title", "no_link_registry": True}))
    cfg = load_config(cfg_path)
    assert cfg["dedup_method"] == "title"
    assert cfg["no_link_registry"] is True
    assert cfg["output_dir"] == DEFAULT_CONFIG["output_dir"]


def test_load_config_malformed_falls_back(tmp_path: Path):
    cfg_path = tmp_path / "bad.json"
    cfg_path.write_text("{not json", encoding="utf-8")
    assert load_config(cfg_path) == DEFAULT_CONFIG


def test_extract_events_from_tagged():
    events = extract_events_from_tagged(TAGGED_MD)
    assert len(events) == 2
    first = events[0]
    assert first["date"] == "2025-01-01"
    assert first["title"] == "Alpha Outage"
    assert first["themes"] == ["api", "outage"]
    assert "First body" in first["body"]
    assert first["anchor"]
    assert first["snippet"]


def test_deduplicate_events_title_merges_same_title():
    events = [
        {"date": "2025-01-01", "title": "Outage", "body": "short", "themes": ["api"], "sources": ["a"], "snippet": "short"},
        {"date": "2025-01-02", "title": "Outage", "body": "a longer body", "themes": ["web"], "sources": ["b"], "snippet": "a longer body"},
    ]
    result = deduplicate_events(events, method="title")
    assert len(result) == 1
    assert result[0]["body"] == "a longer body"
    assert set(result[0]["themes"]) == {"api", "web"}


def test_deduplicate_events_date_title_keeps_both():
    events = [
        {"date": "2025-01-01", "title": "Outage", "body": "a", "themes": [], "sources": [], "snippet": "a"},
        {"date": "2025-01-02", "title": "Outage", "body": "b", "themes": [], "sources": [], "snippet": "b"},
    ]
    result = deduplicate_events(events, method="date_title")
    assert len(result) == 2


def test_deduplicate_events_keeps_first_seen_order_across_hash_seeds():
    script = """
import json
from wordpipe.chronicle.index import deduplicate_events

common = dict(date="2025-01-01", title="Outage", body="body", snippet="body")
events = [
    dict(common, themes=["web", "api"], sources=["b", "a"]),
    dict(common, themes=["api", "cache"], sources=["a", "c"]),
]
print(json.dumps(deduplicate_events(events)))
"""
    for seed in ("1", "2"):
        output = subprocess.check_output(
            [sys.executable, "-c", script],
            env={**os.environ, "PYTHONHASHSEED": seed},
            text=True,
        )
        (event,) = json.loads(output)
        assert event["themes"] == ["web", "api", "cache"]
        assert event["sources"] == ["b", "a", "c"]


def test_build_event_index_sorts_and_ranges():
    events = [
        {"date": "2025-01-02", "title": "Later", "themes": []},
        {"date": "2025-01-01", "title": "Earlier", "themes": []},
    ]
    ctx = build_event_index(events)
    assert [e["date"] for e in ctx["events"]] == ["2025-01-01", "2025-01-02"]
    assert ctx["date_range_start"] == "2025-01-01"
    assert ctx["date_range_end"] == "2025-01-02"


def test_build_theme_index_groups_by_theme():
    events = [
        {"date": "2025-01-01", "title": "A", "themes": ["api"]},
        {"date": "2025-01-02", "title": "B", "themes": ["api", "web"]},
    ]
    ctx = build_theme_index(events)
    assert set(ctx["themes"]) == {"api", "web"}
    assert len(ctx["themes"]["api"]) == 2
    assert len(ctx["themes"]["web"]) == 1


def test_render_template_falls_back_without_templates(tmp_path: Path):
    ctx = build_event_index(extract_events_from_tagged(TAGGED_MD))
    # Nonexistent templates_dir forces the fallback renderer.
    out = render_template(
        "event_index.md.j2", ctx, templates_dir=str(tmp_path / "no_templates")
    )
    assert "Alpha Outage" in out


def test_cli_generates_appendix_files(tmp_path: Path):
    inp = tmp_path / "tagged.md"
    inp.write_text(TAGGED_MD, encoding="utf-8")
    out_dir = tmp_path / "appendix"

    result = subprocess.run(
        [sys.executable, "pipeline/index.py", "--input", str(inp),
         "--output-dir", str(out_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    for name in ("event_index.md", "theme_index.md", "source_manifest.md", "link_registry.md"):
        assert (out_dir / name).exists(), name


def test_cli_missing_input_exits_1(tmp_path: Path):
    result = subprocess.run(
        [sys.executable, "pipeline/index.py", "--input", str(tmp_path / "nope.md"),
         "--output-dir", str(tmp_path / "out")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
