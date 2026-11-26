"""MD-01 contract checks, including full paired runs where PowerShell is installed."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import pytest

from tools import compare_markdown_modes as comparison
from tools import prepare_generic_markdown_chronicle as adapter
from tools import run_topic_report as runner
from wordpipe.chronicle.markdown_sections import (
    STRUCTURAL_LINEAGE_SCHEMA,
    STRUCTURAL_MODE,
    validate_parser_provenance,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"
FROZEN_SHA = "c7fdcfe34300f7bf55f4950455e24b08db41eb1ee8237a3e665c7295c75ccda5"


def test_byte_accounting_newlines_and_duplicate_headings(tmp_path):
    fixture = (FIXTURES / "md01_adversarial.md").read_text(encoding="utf-8")
    path = tmp_path / "mixed.md"
    previous = None
    for newline in ("\n", "\r\n", "\r"):
        raw = fixture.replace("\n", newline).encode()
        path.write_bytes(raw)
        events, lineage, report = adapter.parse_structural_file(path)
        assert path.read_bytes() == raw
        assert report["source_sha256"] == hashlib.sha256(raw).hexdigest()
        assert [r["original_heading_text"] for r in report["candidates"]] == ["Repeat", "Repeat", "Empty", "Ending"]
        assert [r["candidate_ordinal"] for r in lineage] == [1, 2, 4]
        assert [r["staged_event_ordinal"] for r in lineage] == [1, 2, 3]
        assert report["diagnostics"][0]["code"] == "invalid_frontmatter"
        assert len(report["fences"]) == 2
        assert "Quoted literal" in events[0].body and "List literal" in events[0].body
        spans = report["spans"]
        assert spans[0]["start_byte"] == 0 and spans[-1]["end_byte"] == len(raw)
        assert spans[-1]["end_line"] == report["line_count"]
        for left, right in zip(spans, spans[1:]):
            assert left["end_byte"] == right["start_byte"]
            assert left["end_line"] + 1 == right["start_line"]
        ids = [runner.compute_source_event_id("fixture", row, markdown_mode=STRUCTURAL_MODE)[0] for row in lineage]
        assert len(set(ids)) == 3
        assert previous in (None, ids)
        previous = ids


def test_unterminated_frontmatter_and_configured_h3(tmp_path):
    path = tmp_path / "front.md"
    path.write_text("---\ntitle: no closer\n## Parent\nbody\n### Child\ntext\n", encoding="utf-8")
    _, _, report = adapter.parse_structural_file(path, (2, 3))
    assert report["diagnostics"][0]["code"] == "unterminated_frontmatter"
    assert [row["heading_level"] for row in report["candidates"]] == [2, 3]


def test_prepare_preserves_actual_parser_configuration(tmp_path):
    sources = tmp_path / "sources"
    sources.mkdir()
    (sources / "config.md").write_text("## Parent\ncontent\n### Child\ncontent\n", encoding="utf-8")
    run = tmp_path / "run"
    run.mkdir()
    metrics_path = run / "prepare_metrics.json"
    metrics = adapter.prepare(
        sources, run / "staged_input", metrics_path, markdown_mode=STRUCTURAL_MODE, heading_levels=(3, 2),
    )
    expected = {
        "engine": "markdown-it-py", "distribution_version": version("markdown-it-py"),
        "preset": "commonmark", "enabled_extensions": ["table"], "mode": STRUCTURAL_MODE,
        "contract_version": 1, "heading_levels": [2, 3],
    }
    raw = json.loads((run / "event_lineage.json").read_text(encoding="utf-8"))
    assert raw["parser_provenance"] == metrics["parser_provenance"] == expected
    assert [event["heading_level"] for event in raw["events"]] == [2, 3]
    finalized = runner.validate_and_finalize_event_lineage(
        metrics, metrics_path, topic="t", run_id="run", require_event_lineage=True,
        markdown_mode=STRUCTURAL_MODE, heading_levels=(3, 2),
    )
    assert finalized["parser_provenance"] == expected
    for incompatible in (None, {**expected, "enabled_extensions": []}, {**expected, "contract_version": 2}):
        with pytest.raises(ValueError, match="structural parser"):
            validate_parser_provenance(incompatible, (3, 2))
    historical_producer = {**expected, "distribution_version": "3.0.0"}
    assert validate_parser_provenance(historical_producer, (3, 2)) == historical_producer
    for schema in (STRUCTURAL_LINEAGE_SCHEMA, "event-lineage-structural-v1"):
        with pytest.raises(runner.ProvenanceError, match="provenance|schema"):
            runner.correlate_event_provenance(
                run, {"$schema": schema, "markdown_mode": STRUCTURAL_MODE, "events": []},
                topic="t", run_id="run", markdown_mode=STRUCTURAL_MODE,
            )


def manifest(tmp_path, *, structural):
    config = json.loads((ROOT / "WordHorrorStories/flowers/topic_manifest.json").read_text(encoding="utf-8"))
    config["topic"] = "md01_synthetic"
    config["input_dir"] = str(tmp_path / "sources")
    config["output"]["base_dir"] = str(tmp_path / ("structural" if structural else "legacy"))
    config["quality_gates"].update(min_extraction_coverage_percent=0, min_theme_tag_percent=0)
    if structural:
        config["adapter"]["markdown_mode"] = STRUCTURAL_MODE
        config["output"]["legacy_base_dir"] = str(tmp_path / "legacy")
    path = tmp_path / ("structural.json" if structural else "legacy.json")
    path.write_text(json.dumps(config), encoding="utf-8")
    return runner.load_manifest(path, repo_root=ROOT)


def test_resolved_alias_and_claimed_roots(tmp_path):
    (tmp_path / "sources").mkdir()
    structural = manifest(tmp_path, structural=True)
    legacy = manifest(tmp_path, structural=False)
    root = tmp_path / "structural"
    structural["output"]["base_dir"] = str(tmp_path / "elsewhere/../legacy")
    with pytest.raises(runner.RunDirectoryCollisionError, match="overlaps"):
        runner.run_report(structural, dry_run=True)
    alias = tmp_path / "alias"
    (tmp_path / "legacy").mkdir()
    if os.name == "nt":
        # Windows junctions exercise resolved aliases without requiring
        # Developer Mode or symbolic-link creation privileges.
        result = os.system(f'cmd /c mklink /J "{alias}" "{tmp_path / "legacy"}" >nul')
        assert result == 0
    else:
        alias.symlink_to(tmp_path / "legacy", target_is_directory=True)
    structural["output"]["base_dir"] = str(alias)
    with pytest.raises(runner.RunDirectoryCollisionError, match="overlaps"):
        runner.run_report(structural, dry_run=True)
    structural["output"]["base_dir"] = str(root)
    runner.check_markdown_output_root(structural, claim=True)
    legacy["output"]["base_dir"] = str(root / "nested")
    with pytest.raises(runner.RunDirectoryCollisionError, match="inside"):
        runner.run_report(legacy, dry_run=True)


def test_partial_run_and_no_fallback(tmp_path):
    sources = tmp_path / "sources"
    sources.mkdir()
    (sources / "bad.md").write_bytes(b"## Heading\n\xff")
    state = manifest(tmp_path, structural=True)
    result = runner.run_report(state, run_id="bad")
    run = Path(result["run_dir"])
    assert result["exit_codes"] == {"prepare": 1}
    assert "UnicodeDecodeError" in (run / "run.log").read_text(encoding="utf-8")
    assert not (run / "event_correlation.json").exists()
    with pytest.raises(ValueError, match="incomplete or failed"):
        comparison.load_completed_run(run, STRUCTURAL_MODE)
    with pytest.raises(runner.RunDirectoryCollisionError, match="already exists"):
        runner.run_report(state, run_id="bad")


def test_reserved_framing_is_rejected_without_silent_body_loss(tmp_path):
    sources = tmp_path / "sources"
    sources.mkdir()
    (sources / "reserved.md").write_text("## Heading\n\n```md\n## June 2025\n```\n", encoding="utf-8")
    run = tmp_path / "run"
    run.mkdir()
    with pytest.raises(ValueError, match="reserved Chronicle framing"):
        adapter.prepare(sources, run / "staged_input", run / "prepare_metrics.json", markdown_mode=STRUCTURAL_MODE)


def test_explicit_errors_for_schema_mode_and_ambiguous_heading(tmp_path):
    record = {"candidate_ordinal": 1, "heading_span": {"start_byte": 0, "end_byte": 2}}
    with pytest.raises(ValueError, match="ambiguous candidate"):
        comparison.candidates_by_heading([record, record], [])
    with pytest.raises(runner.ProvenanceError, match="unsupported event lineage"):
        runner.correlate_event_provenance(tmp_path, {"$schema": "event-lineage-v1"}, topic="t", run_id="x", markdown_mode=STRUCTURAL_MODE)
    with pytest.raises(runner.ManifestError, match="markdown_mode"):
        runner.resolve_adapter({"id": "prepare_generic_markdown_chronicle", "markdown_mode": "unknown"}, ROOT)
    with pytest.raises(runner.ManifestError, match="heading_levels"):
        runner.resolve_adapter({"id": "prepare_generic_markdown_chronicle", "heading_levels": [3]}, ROOT)


def without_run_id(value):
    if isinstance(value, dict):
        return {key: without_run_id(item) for key, item in value.items() if key != "run_id"}
    if isinstance(value, list):
        return [without_run_id(item) for item in value]
    return value


@pytest.mark.skipif(
    not shutil.which("powershell" if sys.platform == "win32" else "pwsh"),
    reason="paired Chronicle replay requires platform PowerShell",
)
def test_paired_replay(tmp_path):
    sources = tmp_path / "sources"
    sources.mkdir()
    fixture = (FIXTURES / "md01_structure.md").read_text(encoding="utf-8").encode()
    assert hashlib.sha256(fixture).hexdigest() == FROZEN_SHA
    source = sources / "md01_structure.md"
    source.write_bytes(fixture)
    runs = {}
    old_bytes = {}
    for structural in (False, True):
        config = manifest(tmp_path, structural=structural)
        runs[structural] = []
        for run_id in ("one", "two"):
            if not structural and run_id == "two":
                config["adapter"]["markdown_mode"] = "legacy-v1"
            result = runner.run_report(config, run_id=run_id)
            run = Path(result["run_dir"])
            assert all(code == 0 for code in result["exit_codes"].values()), (run / "run.log").read_text(encoding="utf-8")
            runs[structural].append(run)
        for name in ("event_lineage.json", "event_correlation.json"):
            first, second = [json.loads((path / name).read_text(encoding="utf-8")) for path in runs[structural]]
            assert without_run_id(first) == without_run_id(second)
        if not structural:
            old_bytes = {path: path.read_bytes() for run in runs[False] for path in run.rglob("*") if path.is_file()}
    old, new = runs[False][0], runs[True][0]
    frozen = json.loads((FIXTURES / "md01_identity_legacy.json").read_text(encoding="utf-8"))
    baseline = json.loads((old / "event_lineage.json").read_text(encoding="utf-8"))["events"]
    assert [{key: actual[key] for key in expected} for expected, actual in zip(frozen, baseline, strict=True)] == frozen
    evidence = comparison.compare(old, new, sources)
    assert evidence["structural_parser_provenance"]["distribution_version"] == version("markdown-it-py")
    for path in (new / "prepare_metrics.json", new / "event_lineage.json", new / "event_correlation.json"):
        assert json.loads(path.read_text(encoding="utf-8"))["parser_provenance"] == evidence["structural_parser_provenance"]
        assert "parser_provenance" not in json.loads((old / path.name).read_text(encoding="utf-8"))
    assert evidence == comparison.compare(old, new, sources)
    sidecar = tmp_path / "markdown_mode_comparison.json"
    compare_command = [
        sys.executable, str(ROOT / "tools/compare_markdown_modes.py"), "--legacy-run", str(old),
        "--structural-run", str(new), "--input-dir", str(sources), "--output", str(sidecar),
    ]
    subprocess.run(compare_command, check=True)
    assert json.loads(sidecar.read_text(encoding="utf-8")) == evidence
    assert subprocess.run(compare_command, capture_output=True).returncode == 1
    print("MD-01 paired replay: 4 legacy events, 2 structural events, 2 removed false headings")
    candidates = evidence["candidates"]
    assert [row["disposition"] for row in candidates] == [
        "changed_payload", "removed_fenced_heading", "removed_fenced_heading", "matched_heading", "matched_heading",
    ]
    assert [(row["legacy"]["candidate_ordinal"], row["structural"]["candidate_ordinal"])
            for row in candidates if row["structural"]] == [(1, 1), (4, 2), (5, 3)]
    for field in ("source_event_id", "report_event_id"):
        legacy_ids = {row["legacy"][field] for row in candidates if field in row["legacy"]}
        structural_ids = {row["structural"][field] for row in candidates if row["structural"] and field in row["structural"]}
        assert len(legacy_ids) == 4 and len(structural_ids) == 2 and legacy_ids.isdisjoint(structural_ids)
    assert source.read_bytes() == fixture
    assert all(path.read_bytes() == content for path, content in old_bytes.items())
