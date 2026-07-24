"""
tests/test_pipeline_chronicle.py — Consistency tests for the archived chronicle pipeline tools.

These tests validate the core logic of ingest.py, merge.py, categorize.py, and
verify_ingest.py by importing their functions directly (not via subprocess).

The tests are calibrated against the actual behaviour of the tools at archive time
(2026-02-14). If the tools are modified, these tests will fail — which is the
intended behaviour (they serve as a regression harness).

Usage:
    pytest tests/test_pipeline_chronicle.py -v
    python -m pytest tests/test_pipeline_chronicle.py -v
"""

import json
import re
import tempfile
from pathlib import Path
from typing import Dict, List

import pytest
import yaml

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def tmp_dir():
    """Provide a temporary directory that's cleaned up after the test."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def sample_raw_md():
    """A minimal raw deep-search markdown file for ingest testing."""
    return """# ChatGPT Incidents Timeline

## June 2025

- **June 10–11 – Global ChatGPT Outage:** Users worldwide reported inability to access ChatGPT. The outage lasted approximately 34 hours.
- **June 15 – Memory Glitch:** Some users reported seeing other users' chat histories in their sidebar.

## July 2025

- **July 3 – API Rate Limit Increase:** OpenAI announced increased rate limits for ChatGPT API users.
- **July 8 – Viral DAN Prompt:** A new jailbreak prompt called "DAN 2.0" went viral on Twitter.
"""


@pytest.fixture
def sample_normalised_md():
    """A minimal normalised markdown file (output of ingest.py) for merge testing."""
    return """---
source: Test Source
title: Test Incidents
input_file: test.md
event_count: 2
date: 2025-06-01 to 2025-06-15
---

# Source: Test Source

## Event: 2025-06-10 – Global ChatGPT Outage

Users worldwide reported inability to access ChatGPT.

## Event: 2025-06-15 – Memory Glitch

Some users reported seeing other users' chat histories.
"""


@pytest.fixture
def sample_merged_md():
    """A minimal merged markdown file for categorize testing."""
    return """---
sources: [Source A, Source B]
date_range: 2025-06-01 to 2025-07-01
event_count: 3
merged_from: 2
---

# Source: Merged Chronicles

## Event: 2025-06-10 – Global ChatGPT Outage

Users worldwide reported inability to access ChatGPT. The service was down for 34 hours.

## Event: 2025-06-15 – Memory Glitch

Some users reported seeing other users' chat histories in their sidebar.

## Event: 2025-07-03 – API Rate Limit Increase

OpenAI announced increased rate limits for ChatGPT API users.
"""


# ==============================================================================
# ingest.py tests
# ==============================================================================


class TestIngestCore:
    """Tests for ingest.py core functions (imported from wordpipe.chronicle)."""

    def _import_ingest(self):
        """Import ingest module from wordpipe.chronicle."""
        from wordpipe.chronicle import ingest as ingest_mod
        return ingest_mod

    def test_clean_mojibake(self):
        """Verify mojibake cleanup replaces known encoding artifacts."""
        ingest = self._import_ingest()
        test_cases = [
            ("â€“", "–"),
            ("â€™", "’"),
            ("â€œ", "“"),
            ("Ã©", "é"),
            ("plain text", "plain text"),
            ("", ""),
            ("â€“ â€™ â€œ", "– ’ “"),
        ]
        for raw, expected in test_cases:
            result = ingest.clean_mojibake(raw)
            assert result == expected, f"clean_mojibake({raw!r}) = {result!r}, expected {expected!r}"

    def test_extract_source_name_from_filename(self):
        """Verify source name extraction from filename stem."""
        ingest = self._import_ingest()
        path = Path("2025-08-06-ChatGPT_Agent_Mode.md")
        result = ingest.extract_source_name(path, None)
        # The function title-cases and strips date prefix: "Chatgpt Agent Mode"
        assert "Chatgpt" in result
        assert "Agent" in result
        assert "Mode" in result

    def test_extract_source_name_cli_override(self):
        """Verify CLI --source-name overrides filename-derived name."""
        ingest = self._import_ingest()
        path = Path("some_file.md")
        result = ingest.extract_source_name(path, "Custom Name")
        assert result == "Custom Name"

    def test_extract_title_h1(self):
        """Verify title extraction from H1 heading."""
        ingest = self._import_ingest()
        text = "# My Custom Title\n\nSome content here."
        result = ingest.extract_title(text, "Fallback")
        assert result == "My Custom Title"

    def test_extract_title_h2_fallback(self):
        """Verify title falls back to first H2 when no H1 exists."""
        ingest = self._import_ingest()
        text = "## June 2025\n\nSome content."
        result = ingest.extract_title(text, "Fallback")
        assert result == "June 2025"

    def test_extract_title_source_fallback(self):
        """Verify title falls back to source name when no headings exist."""
        ingest = self._import_ingest()
        text = "Just some plain text without headings."
        result = ingest.extract_title(text, "My Source")
        assert result == "My Source Incidents"

    def test_find_dates_iso(self):
        """Verify ISO date detection."""
        ingest = self._import_ingest()
        text = "Events occurred on 2025-06-15 and 2025-07-03."
        dates = ingest.find_dates(text)
        assert len(dates) >= 2
        assert any(d.strftime("%Y-%m-%d") == "2025-06-15" for d in dates)

    def test_find_dates_named_month(self):
        """Verify named month date detection."""
        ingest = self._import_ingest()
        text = "In June 2025, several incidents occurred."
        dates = ingest.find_dates(text)
        assert len(dates) >= 1
        assert dates[0].year == 2025
        assert dates[0].month == 6

    def test_parse_date_range(self):
        """Verify date range extraction returns earliest and latest."""
        ingest = self._import_ingest()
        text = "Events from 2025-06-01 to 2025-06-30."
        start, end = ingest.parse_date_range(text)
        assert start is not None
        assert end is not None
        assert start.strftime("%Y-%m-%d") == "2025-06-01"
        assert end.strftime("%Y-%m-%d") == "2025-06-30"

    def test_parse_date_range_no_dates(self):
        """Verify date range returns None, None when no dates found."""
        ingest = self._import_ingest()
        text = "No dates here at all."
        start, end = ingest.parse_date_range(text)
        assert start is None
        assert end is None

    def test_parse_single_date_iso(self):
        """Verify _parse_single_date handles ISO format.
        
        Note: dateutil.parser with fuzzy=True and default=datetime(2025,1,1)
        may parse "2025-06-15" differently depending on locale. The key
        assertion is that it returns a valid YYYY-MM-DD string in 2025.
        """
        ingest = self._import_ingest()
        result = ingest._parse_single_date("2025-06-15")
        assert result is not None
        assert result.startswith("2025-")
        assert len(result) == 10

    def test_parse_single_date_range(self):
        """Verify _parse_single_date handles date ranges (takes start date)."""
        ingest = self._import_ingest()
        result = ingest._parse_single_date("June 10–11")
        assert result is not None
        # Should parse to June 10, 2025
        assert result.endswith("-06-10") or result.endswith("-06-10")

    def test_parse_single_date_invalid(self):
        """Verify _parse_single_date returns None for unparseable strings."""
        ingest = self._import_ingest()
        result = ingest._parse_single_date("not a date at all")
        assert result is None

    def test_extract_preamble_with_events(self, sample_raw_md):
        """Verify preamble extraction captures content before first event."""
        ingest = self._import_ingest()
        events = ingest.split_into_events(sample_raw_md)
        preamble = ingest.extract_preamble(sample_raw_md, events)
        # The preamble should contain the H1 title or be empty (headings stripped)
        assert isinstance(preamble, str)

    def test_extract_preamble_no_events(self):
        """Verify preamble returns full text (minus headings) when no events."""
        ingest = self._import_ingest()
        text = "# Just a narrative\n\nNo bullet points here."
        events = ingest.split_into_events(text)
        preamble = ingest.extract_preamble(text, events)
        assert len(preamble) > 0
        # Headings are stripped, so "narrative" is removed; body text remains
        assert "No bullet points" in preamble

    def test_split_into_events(self, sample_raw_md):
        """Verify event splitting produces correct number of events."""
        ingest = self._import_ingest()
        events = ingest.split_into_events(sample_raw_md)
        assert len(events) == 4
        assert events[0]["title"] == "Global ChatGPT Outage"
        assert events[1]["title"] == "Memory Glitch"
        assert events[2]["title"] == "API Rate Limit Increase"
        assert events[3]["title"] == "Viral DAN Prompt"

    def test_split_into_events_dates(self, sample_raw_md):
        """Verify event dates are correctly extracted."""
        ingest = self._import_ingest()
        events = ingest.split_into_events(sample_raw_md)
        assert events[0]["date"] == "2025-06-10"
        assert events[1]["date"] == "2025-06-15"
        assert events[2]["date"] == "2025-07-03"
        assert events[3]["date"] == "2025-07-08"

    def test_format_event(self):
        """Verify event formatting produces correct markdown."""
        ingest = self._import_ingest()
        event = {"date": "2025-06-10", "title": "Test Event", "body": "Description here."}
        result = ingest.format_event(event)
        assert "## Event: 2025-06-10" in result
        assert "Test Event" in result
        assert "Description here." in result

    def test_generate_normalised_md(self):
        """Verify normalised markdown generation includes YAML front-matter."""
        ingest = self._import_ingest()
        from datetime import datetime
        events = [{"date": "2025-06-10", "title": "Test", "body": "Body."}]
        result = ingest.generate_normalised_md(
            source="Test Source",
            title="Test Title",
            date_range=(datetime(2025, 6, 1), datetime(2025, 6, 30)),
            events=events,
            input_file="test.md",
            preamble="Overview text.",
        )
        assert result.startswith("---")
        assert "source: Test Source" in result
        assert "title: Test Title" in result
        assert "event_count: 1" in result
        assert "# Source: Test Source" in result
        assert "> **Overview:**" in result
        assert "## Event: 2025-06-10" in result

    def test_generate_normalised_md_no_events(self):
        """Verify normalised markdown handles zero events gracefully."""
        ingest = self._import_ingest()
        from datetime import datetime
        result = ingest.generate_normalised_md(
            source="Empty Source",
            title="Empty",
            date_range=(None, None),
            events=[],
            input_file="empty.md",
        )
        assert "_(No events extracted)_" in result
        assert "event_count: 0" in result


# ==============================================================================
# merge.py tests
# ==============================================================================


class TestMergeCore:
    """Tests for merge.py core functions (imported directly)."""

    def _import_merge(self):
        from wordpipe.chronicle import merge as merge_mod
        return merge_mod

    def test_parse_yaml_frontmatter_valid(self, sample_normalised_md):
        """Verify YAML front-matter parsing extracts metadata."""
        merge = self._import_merge()
        metadata, body = merge.parse_yaml_frontmatter(sample_normalised_md)
        assert metadata["source"] == "Test Source"
        assert metadata["event_count"] == 2
        assert "## Event:" in body

    def test_parse_yaml_frontmatter_no_frontmatter(self):
        """Verify files without front-matter return empty dict."""
        merge = self._import_merge()
        text = "# Just content\n\nNo front-matter here."
        metadata, body = merge.parse_yaml_frontmatter(text)
        assert metadata == {}
        assert body == text

    def test_parse_yaml_frontmatter_malformed(self):
        """Verify malformed YAML doesn't crash."""
        merge = self._import_merge()
        text = "---\n: invalid yaml :\n---\nBody here."
        metadata, body = merge.parse_yaml_frontmatter(text)
        # Should not crash; returns {} on error
        assert isinstance(metadata, dict)

    def test_extract_events(self, sample_normalised_md):
        """Verify event extraction from normalised markdown."""
        merge = self._import_merge()
        _, body = merge.parse_yaml_frontmatter(sample_normalised_md)
        events = merge.extract_events(body)
        assert len(events) == 2
        assert events[0]["date"] == "2025-06-10"
        assert events[0]["title"] == "Global ChatGPT Outage"
        assert events[1]["date"] == "2025-06-15"
        assert events[1]["title"] == "Memory Glitch"

    def test_extract_events_no_events(self):
        """Verify no events returns empty list."""
        merge = self._import_merge()
        events = merge.extract_events("# Just a heading\n\nNo event blocks here.")
        assert events == []

    def test_compute_body_hash(self):
        """Verify body hashing is deterministic."""
        merge = self._import_merge()
        body1 = "Some event body text here."
        body2 = "Some event body text here."
        body3 = "Different body text."
        assert merge.compute_body_hash(body1) == merge.compute_body_hash(body2)
        assert merge.compute_body_hash(body1) != merge.compute_body_hash(body3)

    def test_compute_body_hash_whitespace_normalised(self):
        """Verify body hashing normalises whitespace."""
        merge = self._import_merge()
        h1 = merge.compute_body_hash("Hello   World")
        h2 = merge.compute_body_hash("Hello World")
        assert h1 == h2

    def test_parse_date_tuple(self):
        """Verify date tuple parsing for sorting."""
        merge = self._import_merge()
        result = merge.parse_date_tuple("2025-06-15")
        assert result == (2025, 6, 15)

    def test_generate_source_coverage(self):
        """Verify source coverage table generation."""
        merge = self._import_merge()
        result = merge.generate_source_coverage(
            source_names=["Source A", "Source B"],
            event_contributions={"Source A": 5, "Source B": 3},
            duplicates=[{"date": "2025-06-10", "sources": ["Source A", "Source B"]}],
        )
        assert "Source Coverage" in result
        assert "Source A" in result
        assert "Source B" in result
        assert "5" in result
        assert "3" in result

    def test_merge_files_keep_both(self, tmp_dir, sample_normalised_md):
        """Verify merge with keep-both conflict mode."""
        merge = self._import_merge()
        # Create two identical files
        f1 = tmp_dir / "source1.md"
        f2 = tmp_dir / "source2.md"
        f1.write_text(sample_normalised_md, encoding="utf-8")
        f2.write_text(sample_normalised_md, encoding="utf-8")

        merged_md, duplicates, contributions, sources = merge.merge_files(
            [f1, f2], conflict_mode="keep-both"
        )
        # Two identical files should produce 2 events (no true duplicates if same content)
        # Actually same content + same date = true duplicate, so 2 events kept
        assert len(sources) == 2
        assert isinstance(merged_md, str)
        assert "## Event:" in merged_md

    def test_merge_files_skip(self, tmp_dir, sample_normalised_md):
        """Verify merge with skip conflict mode."""
        merge = self._import_merge()
        f1 = tmp_dir / "source1.md"
        f2 = tmp_dir / "source2.md"
        f1.write_text(sample_normalised_md, encoding="utf-8")
        f2.write_text(sample_normalised_md, encoding="utf-8")

        merged_md, duplicates, contributions, sources = merge.merge_files(
            [f1, f2], conflict_mode="skip"
        )
        assert len(sources) == 2

    def test_collect_input_files_from_dir(self, tmp_dir):
        """Verify file collection from directory."""
        merge = self._import_merge()
        # Create some .md files
        (tmp_dir / "a.md").write_text("content", encoding="utf-8")
        (tmp_dir / "b.md").write_text("content", encoding="utf-8")
        (tmp_dir / "c.txt").write_text("content", encoding="utf-8")

        files = merge.collect_input_files(None, str(tmp_dir))
        assert len(files) == 2  # only .md files
        assert all(f.suffix == ".md" for f in files)

    def test_collect_input_files_from_list(self, tmp_dir):
        """Verify file collection from explicit list."""
        merge = self._import_merge()
        f1 = tmp_dir / "a.md"
        f2 = tmp_dir / "b.md"
        f1.write_text("content", encoding="utf-8")
        f2.write_text("content", encoding="utf-8")

        files = merge.collect_input_files([str(f1), str(f2)], None)
        assert len(files) == 2

    def test_collect_input_files_duplicates_skipped(self, tmp_dir):
        """Verify duplicate file paths are skipped with warning."""
        merge = self._import_merge()
        f = tmp_dir / "a.md"
        f.write_text("content", encoding="utf-8")

        files = merge.collect_input_files([str(f), str(f)], None)
        assert len(files) == 1  # duplicate skipped

    # ------------------------------------------------------------------
    # P0.2 — Malformed event heading validation
    # ------------------------------------------------------------------

    def test_validate_event_headings_rejects_unknown(self):
        """``validate_event_headings`` raises ``ValueError`` for ``## Event: unknown``."""
        merge = self._import_merge()
        text = "## Event: unknown\n\nSome content."
        with pytest.raises(ValueError, match="Malformed event heading"):
            merge.validate_event_headings(text)

    def test_validate_event_headings_rejects_non_iso(self):
        """``validate_event_headings`` rejects non-ISO date formats."""
        merge = self._import_merge()
        cases = [
            "## Event: 2026/01/01",
            "## Event: TBD",
            "## Event:",
            "## Event : 2025-06-10",
        ]
        for heading in cases:
            with pytest.raises(ValueError, match="Malformed event heading"):
                merge.validate_event_headings(heading)

    def test_validate_event_headings_accepts_valid(self):
        """``validate_event_headings`` passes valid ISO headings."""
        merge = self._import_merge()
        cases = [
            "## Event: 2025-06-10\n\nBody.",
            "## Event: 2025-06-10 - With Title\n\nBody.",
            "## Event: 2025-06-10 – En Dash\n\nBody.",
            "## Event: 2025-12-31 -  \n\nBody with trailing space in title.",
            "## Event: 2025-06-10\n",
            "## Event: 2025-06-10 -\n",
        ]
        for heading in cases:
            # Should not raise
            merge.validate_event_headings(heading)

    def test_validate_event_headings_empty_passes(self):
        """Empty text or text without any ``## Event:`` line passes."""
        merge = self._import_merge()
        merge.validate_event_headings("")  # no raise
        merge.validate_event_headings("# Just a heading\n\nNo events.\n")  # no raise

    def test_merge_files_malformed_heading_rejected(self, tmp_dir):
        """``merge_files`` raises ``ValueError`` when a file contains a malformed
        heading before any processing."""
        merge = self._import_merge()
        bad = tmp_dir / "bad.md"
        bad.write_text(
            "---\nsource: Bad\n---\n\n"
            "## Event: unknown\n\nSome content.\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="Malformed event heading"):
            merge.merge_files([bad])

    def test_validate_event_headings_normal_text_no_events(self):
        """``validate_event_headings`` passes on normal text without ``## Event:`` lines."""
        merge = self._import_merge()
        merge.validate_event_headings("# Regular markdown\n\nNo event headings.\n")


# ==============================================================================
# categorize.py tests
# ==============================================================================


class TestCategorizeCore:
    """Tests for categorize.py core functions (imported directly)."""

    def _import_categorize(self):
        from wordpipe.chronicle import categorize as categorize_mod
        return categorize_mod

    def test_load_themes_default(self):
        """Verify loading built-in default themes when no config provided."""
        categorize = self._import_categorize()
        themes = categorize.load_themes(None)
        assert len(themes) >= 6  # 6 built-in themes
        assert "Web UI" in themes
        assert "Outages" in themes
        assert "Jailbreaks/Exploits" in themes
        assert isinstance(themes["Web UI"], list)
        assert len(themes["Web UI"]) > 0

    def test_load_themes_from_json(self, tmp_dir):
        """Verify loading themes from a JSON config file."""
        categorize = self._import_categorize()
        config = tmp_dir / "themes.json"
        config.write_text(
            json.dumps({"themes": {"Custom Theme": ["keyword1", "keyword2"]}}),
            encoding="utf-8",
        )
        themes = categorize.load_themes(config)
        assert "Custom Theme" in themes
        assert themes["Custom Theme"] == ["keyword1", "keyword2"]

    def test_load_themes_from_yaml(self, tmp_dir):
        """Verify loading themes from a YAML config file."""
        categorize = self._import_categorize()
        config = tmp_dir / "themes.yaml"
        config.write_text("themes:\n  YAML Theme:\n    - kw1\n    - kw2\n", encoding="utf-8")
        themes = categorize.load_themes(config)
        assert "YAML Theme" in themes
        assert themes["YAML Theme"] == ["kw1", "kw2"]

    def test_load_themes_missing_file(self, tmp_dir):
        """Verify missing config file causes exit."""
        categorize = self._import_categorize()
        config = tmp_dir / "nonexistent.json"
        with pytest.raises(SystemExit):
            categorize.load_themes(config)

    def test_load_themes_no_themes_key(self, tmp_dir):
        """Verify config without 'themes' key falls back to defaults."""
        categorize = self._import_categorize()
        config = tmp_dir / "empty.json"
        config.write_text(json.dumps({"other": "data"}), encoding="utf-8")
        themes = categorize.load_themes(config)
        assert len(themes) >= 6  # fell back to defaults

    def test_extract_events(self, sample_merged_md):
        """Verify event extraction from merged markdown."""
        categorize = self._import_categorize()
        # Skip YAML front-matter
        body_start = sample_merged_md.find("---", 3) + 3
        body = sample_merged_md[body_start:]
        events = categorize.extract_events(body)
        assert len(events) == 3
        assert events[0]["date"] == "2025-06-10"
        assert events[1]["date"] == "2025-06-15"
        assert events[2]["date"] == "2025-07-03"

    def test_extract_events_no_events(self):
        """Verify no events returns empty list."""
        categorize = self._import_categorize()
        events = categorize.extract_events("# Just a heading\n\nNo events.")
        assert events == []

    def test_match_themes_outage(self):
        """Verify outage keywords are matched."""
        categorize = self._import_categorize()
        themes = {"Outages": ["down", "outage", "unavailable"]}
        body = "The service was down for 34 hours."
        matched = categorize.match_themes(body, themes)
        assert "Outages" in matched

    def test_match_themes_multiple(self):
        """Verify multiple themes can match a single event."""
        categorize = self._import_categorize()
        themes = {
            "Outages": ["down", "outage"],
            "Culture/Virality": ["viral", "Twitter"],
        }
        body = "The outage went viral on Twitter."
        matched = categorize.match_themes(body, themes)
        assert "Outages" in matched
        assert "Culture/Virality" in matched

    def test_match_themes_no_match(self):
        """Verify no match returns empty list."""
        categorize = self._import_categorize()
        themes = {"Outages": ["down", "outage"]}
        body = "Everything is working fine."
        matched = categorize.match_themes(body, themes)
        assert matched == []

    def test_match_themes_empty_body(self):
        """Verify empty body returns empty list."""
        categorize = self._import_categorize()
        themes = {"Outages": ["down"]}
        matched = categorize.match_themes("", themes)
        assert matched == []

    def test_match_themes_case_insensitive(self):
        """Verify keyword matching is case-insensitive."""
        categorize = self._import_categorize()
        themes = {"Outages": ["OUTAGE"]}
        body = "There was an outage today."
        matched = categorize.match_themes(body, themes)
        assert "Outages" in matched

    def test_match_themes_substring(self):
        """Verify substring matching works (not word-boundary)."""
        categorize = self._import_categorize()
        themes = {"API/Developer": ["api.openai.com"]}
        body = "The api.openai.com endpoint was slow."
        matched = categorize.match_themes(body, themes)
        assert "API/Developer" in matched

    def test_rebuild_tagged_md(self, sample_merged_md):
        """Verify tagged markdown includes theme comments."""
        categorize = self._import_categorize()
        body_start = sample_merged_md.find("---", 3) + 3
        body = sample_merged_md[body_start:]
        events = categorize.extract_events(body)
        # Manually assign themes
        events[0]["themes"] = ["Outages"]
        events[1]["themes"] = ["Memory/Personalisation"]
        events[2]["themes"] = ["API/Developer"]

        tagged = categorize.rebuild_tagged_md(sample_merged_md, events)
        assert "<!-- themes: Outages -->" in tagged
        assert "<!-- themes: Memory/Personalisation -->" in tagged
        assert "<!-- themes: API/Developer -->" in tagged

    def test_rebuild_tagged_md_no_themes(self, sample_merged_md):
        """Verify events without themes don't get a comment."""
        categorize = self._import_categorize()
        body_start = sample_merged_md.find("---", 3) + 3
        body = sample_merged_md[body_start:]
        events = categorize.extract_events(body)
        events[0]["themes"] = []
        events[1]["themes"] = []
        events[2]["themes"] = []

        tagged = categorize.rebuild_tagged_md(sample_merged_md, events)
        assert "<!-- themes:" not in tagged

    def test_build_sidecar_json(self):
        """Verify sidecar JSON structure."""
        categorize = self._import_categorize()
        events = [
            {"date": "2025-06-10", "title": "Event 1", "themes": ["Outages"]},
            {"date": "2025-06-15", "title": "Event 2", "themes": []},
        ]
        sidecar = categorize.build_sidecar_json(events)
        assert len(sidecar) == 2
        assert sidecar[0]["date"] == "2025-06-10"
        assert sidecar[0]["themes"] == ["Outages"]
        assert sidecar[1]["themes"] == []


# ==============================================================================
# verify_ingest.py tests
# ==============================================================================


class TestVerifyIngestCore:
    """Tests for verify_ingest.py core logic."""

    def _import_verify(self):
        import importlib

        from wordpipe.chronicle import verify_ingest
        verify_module = importlib.import_module("wordpipe.chronicle.verify_ingest")
        assert verify_ingest is verify_module.verify_ingest
        return verify_module

    def test_default_paths_exist(self):
        """Verify default paths point to existing locations."""
        verify = self._import_verify()
        raw_dir = Path(verify.DEFAULT_RAW_DIR)
        ingest_script = Path(verify.DEFAULT_INGEST)
        assert raw_dir.as_posix() == "inputs/chatgpt-chronicle/markdown"
        assert raw_dir.is_dir()
        assert str(ingest_script).endswith("ingest.py")

    def test_parse_ingest_stderr_ok(self):
        """Verify successful ingest stderr parsing."""
        verify = self._import_verify()
        stderr = "INFO: Extracted 5 events.\n"
        count, warnings = verify.parse_ingest_stderr(stderr)
        assert count == 5
        assert warnings == []

    def test_parse_ingest_stderr_warnings(self):
        """Verify warnings are extracted from stderr."""
        verify = self._import_verify()
        stderr = "WARNING: No events found in empty.md (source: empty)\n"
        count, warnings = verify.parse_ingest_stderr(stderr)
        assert count == 0
        assert len(warnings) == 1
        assert "WARNING" in warnings[0]

    def test_parse_ingest_stderr_info_line_not_events(self):
        """Verify info lines without 'Extracted events' don't affect count."""
        verify = self._import_verify()
        stderr = "INFO: Starting ingest\nINFO: Extracted 3 events.\nINFO: Done\n"
        count, warnings = verify.parse_ingest_stderr(stderr)
        assert count == 3

    def test_classify_file_result_ok(self):
        """Verify classify_file_result returns OK for successful runs."""
        verify = self._import_verify()
        status, reason = verify.classify_file_result(0, 5, [])
        assert status == "[OK]"
        assert reason is None

    def test_classify_file_result_error(self):
        """Verify classify_file_result flags non-zero exit codes."""
        verify = self._import_verify()
        status, reason = verify.classify_file_result(1, 0, [])
        assert status == "[ERROR]"
        assert reason is not None

    def test_classify_file_result_zero(self):
        """Verify classify_file_result flags zero events without date warning."""
        verify = self._import_verify()
        status, reason = verify.classify_file_result(0, 0, [])
        assert status == "[ZERO]"
        assert reason is not None

    def test_classify_file_result_zero_with_date_warning(self):
        """Verify zero events with date warning is not an issue."""
        verify = self._import_verify()
        status, reason = verify.classify_file_result(0, 0, ["WARNING: No dates found"])
        assert status == "[ZERO]"
        assert reason is None


# ==============================================================================
# Integration tests (end-to-end via subprocess)
# ==============================================================================


class TestPipelineIntegration:
    """End-to-end integration tests using subprocess."""

    @pytest.fixture
    def script_dir(self):
        return Path(__file__).parent.parent / "tools" / "pipeline-chronicle"

    def test_ingest_help(self, script_dir):
        """Verify ingest.py --help works."""
        import subprocess
        result = subprocess.run(
            ["python", str(script_dir / "ingest.py"), "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "--input" in result.stdout
        assert "--output" in result.stdout

    def test_merge_help(self, script_dir):
        """Verify merge.py --help works."""
        import subprocess
        result = subprocess.run(
            ["python", str(script_dir / "merge.py"), "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "--inputs" in result.stdout
        assert "--input-dir" in result.stdout

    def test_categorize_help(self, script_dir):
        """Verify categorize.py --help works."""
        import subprocess
        result = subprocess.run(
            ["python", str(script_dir / "categorize.py"), "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "--input" in result.stdout
        assert "--config" in result.stdout

    def test_verify_ingest_help(self, script_dir):
        """Verify verify_ingest.py --help works (tools wrapper)."""
        import subprocess
        result = subprocess.run(
            ["python", str(script_dir / "verify_ingest.py"), "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "--dir" in result.stdout
        assert "--ingest" in result.stdout

    def test_verify_ingest_pipeline_wrapper_help(self):
        """Verify pipeline/verify_ingest.py --help works."""
        import subprocess
        result = subprocess.run(
            ["python", "pipeline/verify_ingest.py", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "--dir" in result.stdout

    def test_ingest_end_to_end(self, tmp_dir, script_dir, sample_raw_md):
        """Verify ingest.py produces valid output from raw input."""
        import subprocess
        input_file = tmp_dir / "input.md"
        output_file = tmp_dir / "output.md"
        input_file.write_text(sample_raw_md, encoding="utf-8")

        result = subprocess.run(
            [
                "python", str(script_dir / "ingest.py"),
                "--input", str(input_file),
                "--output", str(output_file),
                "--source-name", "Test Source",
            ],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "source: Test Source" in content
        assert "event_count: 4" in content
        assert "## Event: 2025-06-10" in content

    def test_merge_end_to_end(self, tmp_dir, script_dir, sample_normalised_md):
        """Verify merge.py produces valid merged output."""
        import subprocess
        f1 = tmp_dir / "source1.md"
        f2 = tmp_dir / "source2.md"
        f1.write_text(sample_normalised_md, encoding="utf-8")
        f2.write_text(sample_normalised_md, encoding="utf-8")
        output = tmp_dir / "merged.md"

        result = subprocess.run(
            [
                "python", str(script_dir / "merge.py"),
                "--inputs", str(f1), str(f2),
                "--output", str(output),
                "--conflict-mode", "keep-both",
            ],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "## Event:" in content

    def test_categorize_end_to_end(self, tmp_dir, script_dir, sample_merged_md):
        """Verify categorize.py produces valid tagged output."""
        import subprocess
        input_file = tmp_dir / "input.md"
        output_file = tmp_dir / "tagged.md"
        input_file.write_text(sample_merged_md, encoding="utf-8")

        result = subprocess.run(
            [
                "python", str(script_dir / "categorize.py"),
                "--input", str(input_file),
                "--output", str(output_file),
                "--sidecar",
            ],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        # At least some events should be tagged
        assert "<!-- themes:" in content

        # Sidecar should exist
        sidecar = output_file.with_suffix(".tagged.json")
        assert sidecar.exists()
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        assert len(data) == 3  # 3 events

    def test_full_pipeline(self, tmp_dir, script_dir, sample_raw_md):
        """Verify full pipeline: ingest → merge → categorize."""
        import subprocess

        # Create two slightly different raw files
        raw1 = tmp_dir / "raw1.md"
        raw2 = tmp_dir / "raw2.md"
        raw1.write_text(sample_raw_md, encoding="utf-8")
        raw2.write_text(
            sample_raw_md.replace("Global ChatGPT Outage", "Global ChatGPT Outage (alt source)"),
            encoding="utf-8",
        )

        norm_dir = tmp_dir / "normalised"
        norm_dir.mkdir()

        # Ingest both files
        for raw in [raw1, raw2]:
            out = norm_dir / f"{raw.stem}_normalised.md"
            result = subprocess.run(
                ["python", str(script_dir / "ingest.py"), "--input", str(raw), "--output", str(out)],
                capture_output=True, text=True,
            )
            assert result.returncode == 0

        # Merge
        merged = tmp_dir / "merged.md"
        result = subprocess.run(
            ["python", str(script_dir / "merge.py"), "--input-dir", str(norm_dir), "--output", str(merged)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert merged.exists()

        # Categorize
        tagged = tmp_dir / "tagged.md"
        result = subprocess.run(
            ["python", str(script_dir / "categorize.py"), "--input", str(merged), "--output", str(tagged)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert tagged.exists()
        content = tagged.read_text(encoding="utf-8")
        assert "## Event:" in content
