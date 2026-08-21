"""Tests for the generic topic report runner (tools/run_topic_report.py)."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "run_topic_report.py"
SPEC = importlib.util.spec_from_file_location("run_topic_report", MODULE_PATH)
runner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _repo_root() -> str:
    return str(Path(__file__).resolve().parents[1])


def _valid_manifest_dict(repo_root: str | None = None) -> dict:
    """Return a valid manifest dict. Paths are repo-root-absolute."""
    if repo_root is None:
        repo_root = _repo_root()
    return {
        "schema_version": 1,
        "topic": "insurancechatbot",
        "input_dir": str(Path(repo_root) / "inputs" / "insurancechatbot" / "markdown"),
        "adapter": {
            "id": "prepare_insurancechatbot_chronicle",
            "script": str(Path(repo_root) / "tools" / "prepare_insurancechatbot_chronicle.py"),
        },
        "themes_config": str(
            Path(repo_root) / "WordHorrorStories" / "insurancechatbot" / "themes.insurancechatbot.json"
        ),
        "index_config": str(Path(repo_root) / "pipeline" / "index_config.json"),
        "output": {
            "base_dir": str(Path(repo_root) / "WordHorrorStories" / "insurancechatbot" / "output"),
            "run_id_format": "timestamp",
        },
        "quality_gates": {
            "min_extraction_coverage_percent": 95.0,
            "min_theme_tag_percent": 85.0,
            "max_error_count": 0,
        },
        "_repo_root": repo_root,
    }


def _write_manifest_and_anchor(
    tmp_path: Path,
    manifest_data: dict,
) -> Path:
    """Write a manifest JSON plus a ``pipeline/chain.ps1`` anchor so
    ``find_repo_root`` resolves correctly. Returns path to manifest."""
    anchor = tmp_path / "pipeline" / "chain.ps1"
    anchor.parent.mkdir(parents=True, exist_ok=True)
    anchor.write_text("# dummy", encoding="utf-8")

    manifest_path = tmp_path / "topic_manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    return manifest_path


def _valid_manifest_file(tmp_path: Path) -> tuple[Path, dict]:
    """Write a valid manifest to a temp file (with repo anchor) and return
    ``(manifest_path, manifest_data)``."""
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "dummy.md").write_text("x", encoding="utf-8")

    adapter_script = tmp_path / "adapter.py"
    adapter_script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

    themes_cfg = tmp_path / "themes.json"
    themes_cfg.write_text(
        json.dumps({"themes": {"ThemeA": {"keywords": ["a"]}, "ThemeB": {"keywords": ["b"]}}}),
        encoding="utf-8",
    )

    index_cfg = tmp_path / "index_config.json"
    index_cfg.write_text("{}", encoding="utf-8")

    out_base = tmp_path / "output"
    out_base.mkdir(parents=True, exist_ok=True)

    manifest_data = {
        "schema_version": 1,
        "topic": "testtopic",
        "input_dir": str(input_dir.resolve()),
        "adapter": {"id": "test_adapter", "script": str(adapter_script.resolve())},
        "themes_config": str(themes_cfg.resolve()),
        "index_config": str(index_cfg.resolve()),
        "output": {"base_dir": str(out_base.resolve()), "run_id_format": "timestamp"},
        "quality_gates": {
            "min_extraction_coverage_percent": 95.0,
            "min_theme_tag_percent": 85.0,
            "max_error_count": 0,
        },
    }

    manifest_path = _write_manifest_and_anchor(tmp_path, manifest_data)
    return manifest_path, manifest_data


# ---------------------------------------------------------------------------
# Manifest loading & validation
# ---------------------------------------------------------------------------


def test_load_valid_manifest(tmp_path):
    manifest_path, _ = _valid_manifest_file(tmp_path)
    result = runner.load_manifest(str(manifest_path))
    assert result["topic"] == "testtopic"
    assert result["schema_version"] == 1
    assert "_repo_root" in result


def test_load_manifest_resolves_registered_adapter_without_script(tmp_path):
    repo_root = Path(_repo_root())
    manifest = _valid_manifest_dict(str(repo_root))
    manifest["adapter"] = {"id": "prepare_insurancechatbot_chronicle"}
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = runner.load_manifest(str(manifest_path), repo_root=str(repo_root))

    assert result["adapter"]["script"].endswith("tools\\prepare_insurancechatbot_chronicle.py") or result[
        "adapter"
    ]["script"].endswith("tools/prepare_insurancechatbot_chronicle.py")
    assert result["adapter"]["registry_backed"] is True


def test_load_manifest_resolves_generic_adapter_from_registry(tmp_path):
    repo_root = Path(_repo_root())
    manifest = _valid_manifest_dict(str(repo_root))
    manifest["adapter"] = {"id": "prepare_generic_markdown_chronicle"}
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = runner.load_manifest(str(manifest_path), repo_root=str(repo_root))

    assert result["adapter"]["script"].endswith("tools\\prepare_generic_markdown_chronicle.py") or result[
        "adapter"
    ]["script"].endswith("tools/prepare_generic_markdown_chronicle.py")
    assert result["adapter"]["registry_backed"] is True


def test_load_manifest_requires_script_for_unregistered_adapter(tmp_path):
    repo_root = Path(_repo_root())
    manifest = _valid_manifest_dict(str(repo_root))
    manifest["adapter"] = {"id": "unknown_adapter"}
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    try:
        runner.load_manifest(str(manifest_path), repo_root=str(repo_root))
        assert False, "Expected ManifestError"
    except runner.ManifestError as exc:
        assert "adapter.script" in str(exc)


def test_load_manifest_file_not_found():
    try:
        runner.load_manifest("/nonexistent/path/manifest.json")
        assert False, "Expected ManifestError"
    except runner.ManifestError as exc:
        assert "not found" in str(exc).lower()


def test_load_manifest_not_a_dict(tmp_path):
    p = _write_manifest_and_anchor(tmp_path, "just a string")
    try:
        runner.load_manifest(str(p))
        assert False, "Expected ManifestError"
    except runner.ManifestError as exc:
        assert "object" in str(exc).lower() or "dict" in str(exc).lower()


def test_load_manifest_missing_required_key(tmp_path):
    p = _write_manifest_and_anchor(tmp_path, {"schema_version": 1})
    try:
        runner.load_manifest(str(p))
        assert False, "Expected ManifestError"
    except runner.ManifestError as exc:
        assert "Missing required key" in str(exc)


def test_load_manifest_bad_schema_version(tmp_path):
    # Files needed for path validation.
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "d.md").write_text("x", encoding="utf-8")
    p = _write_manifest_and_anchor(
        tmp_path,
        {
            "schema_version": 0,
            "topic": "t",
            "input_dir": str(input_dir.resolve()),
            "adapter": {"id": "a", "script": str(input_dir / "d.md")},
            "themes_config": str(input_dir / "d.md"),
            "index_config": str(input_dir / "d.md"),
            "output": {"base_dir": str(input_dir), "run_id_format": "ts"},
            "quality_gates": {
                "min_extraction_coverage_percent": 90,
                "min_theme_tag_percent": 80,
                "max_error_count": 1,
            },
        },
    )
    try:
        runner.load_manifest(str(p))
        assert False, "Expected ManifestError"
    except runner.ManifestError as exc:
        assert "positive" in str(exc).lower()


def test_load_manifest_bad_quality_gates(tmp_path):
    # Create real-looking dirs/files so path validation doesn't fail first.
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "d.md").write_text("x", encoding="utf-8")
    adapter_script = tmp_path / "a.py"
    adapter_script.write_text("", encoding="utf-8")

    p = _write_manifest_and_anchor(
        tmp_path,
        {
            "schema_version": 1,
            "topic": "t",
            "input_dir": str(input_dir.resolve()),
            "adapter": {"id": "a", "script": str(adapter_script.resolve())},
            "themes_config": str(adapter_script.resolve()),
            "index_config": str(adapter_script.resolve()),
            "output": {"base_dir": str(input_dir), "run_id_format": "ts"},
            "quality_gates": {
                "min_extraction_coverage_percent": -1,
                "min_theme_tag_percent": 85.0,
                "max_error_count": 0,
            },
        },
    )
    try:
        runner.load_manifest(str(p))
        assert False, "Expected ManifestError"
    except runner.ManifestError as exc:
        assert ">=" in str(exc) or "must be" in str(exc).lower()


def test_load_manifest_with_explicit_repo_root(tmp_path):
    """When ``repo_root`` is passed explicitly, ``find_repo_root`` is skipped."""
    manifest_data = {
        "schema_version": 1,
        "topic": "overtopic",
        "input_dir": str(tmp_path),
        "adapter": {"id": "oa", "script": str(tmp_path / "nonexistent.py")},
        "themes_config": str(tmp_path / "nonexistent.json"),
        "index_config": str(tmp_path / "nonexistent.json"),
        "output": {"base_dir": str(tmp_path), "run_id_format": "ts"},
        "quality_gates": {
            "min_extraction_coverage_percent": 90.0,
            "min_theme_tag_percent": 80.0,
            "max_error_count": 1,
        },
    }
    # Bypass path-existence validation by using a real file for all paths.
    real_file = tmp_path / "exists.txt"
    real_file.write_text("x", encoding="utf-8")
    manifest_data["adapter"]["script"] = str(real_file)
    manifest_data["themes_config"] = str(real_file)
    manifest_data["index_config"] = str(real_file)

    mpath = tmp_path / "ovr_manifest.json"
    mpath.write_text(json.dumps(manifest_data), encoding="utf-8")

    result = runner.load_manifest(str(mpath), repo_root=str(tmp_path))
    assert result["topic"] == "overtopic"
    assert result["_repo_root"] == str(tmp_path.resolve())


# ---------------------------------------------------------------------------
# Command construction
# ---------------------------------------------------------------------------


def test_build_commands_returns_three_stages(tmp_path):
    manifest = _valid_manifest_dict(_repo_root())
    run_dir = tmp_path / "my_run"
    cmds = runner.build_commands(manifest, run_dir)

    assert runner.CMD_PREPARE in cmds
    assert runner.CMD_PIPELINE in cmds
    assert runner.CMD_SUMMARIZE in cmds

    prepare_cmd = cmds[runner.CMD_PREPARE]
    assert "prepare" in prepare_cmd
    assert "--input-dir" in prepare_cmd
    assert "--output-dir" in prepare_cmd
    assert "--metrics" in prepare_cmd

    pipeline_cmd = cmds[runner.CMD_PIPELINE]
    assert "powershell" in pipeline_cmd[0].lower()
    assert "chain.ps1" in str(pipeline_cmd)

    summarize_cmd = cmds[runner.CMD_SUMMARIZE]
    assert "summarize" in summarize_cmd
    assert "--run-dir" in summarize_cmd


def test_build_commands_output_paths(tmp_path):
    manifest = _valid_manifest_dict(_repo_root())
    run_dir = tmp_path / "test_run_001"
    cmds = runner.build_commands(manifest, run_dir)

    prepare_cmd = cmds[runner.CMD_PREPARE]
    outdir_idx = prepare_cmd.index("--output-dir") + 1
    assert run_dir.name in prepare_cmd[outdir_idx]


def test_load_enrich_validate_prepare_metrics_adds_topic(tmp_path):
    metrics_path = tmp_path / "prepare_metrics.json"
    metrics_path.write_text(
        json.dumps({
            "input_file_count": 1,
            "candidate_total_sections": 2,
            "staged_event_count": 2,
            "extraction_coverage_percent": 100.0,
            "staged_files": ["01_source.md"],
            "source_lineage": [{
                "source_file": "source.md",
                "staged_file": "01_source.md",
                "candidate_count": 2,
                "staged_event_count": 2,
            }],
        }),
        encoding="utf-8",
    )

    enriched = runner.load_enrich_validate_prepare_metrics(
        metrics_path,
        topic="testtopic",
        require_lineage=True,
    )
    saved = json.loads(metrics_path.read_text(encoding="utf-8"))

    assert enriched["topic"] == "testtopic"
    assert saved == enriched
    assert saved["staged_event_count"] == 2


def test_enriching_metrics_does_not_change_adapter_command_contract(tmp_path):
    manifest = _valid_manifest_dict(_repo_root())
    summarize_cmd = runner.build_commands(manifest, tmp_path / "run")[runner.CMD_SUMMARIZE]
    prepare_cmd = runner.build_commands(manifest, tmp_path / "run")[runner.CMD_PREPARE]

    assert "--topic" not in summarize_cmd
    assert "--input-dir" in prepare_cmd
    assert "--output-dir" in prepare_cmd
    assert "--metrics" in prepare_cmd
    assert "--prepare-metrics" in summarize_cmd
    assert "--performance" in summarize_cmd
    assert "--run-log" in summarize_cmd


def test_dry_run_does_not_create_directories(tmp_path):
    manifest = _valid_manifest_dict(_repo_root())
    manifest["output"]["base_dir"] = str(tmp_path)
    result = runner.run_report(manifest, dry_run=True, run_id="dry_test")
    assert not (tmp_path / "dry_test").exists()
    assert result["run_dir"].endswith("dry_test")
    assert result["exit_codes"] == {}


def test_existing_run_directory_is_rejected_without_modification(tmp_path):
    manifest = _valid_manifest_dict(_repo_root())
    manifest["output"]["base_dir"] = str(tmp_path)
    existing = tmp_path / "existing"
    existing.mkdir()
    sentinel = existing / "sentinel.txt"
    sentinel.write_text("preserve me", encoding="utf-8")

    for dry_run in (False, True):
        try:
            runner.run_report(manifest, dry_run=dry_run, run_id="existing")
            assert False, "Expected RunDirectoryCollisionError"
        except runner.RunDirectoryCollisionError as exc:
            assert "append-only" in str(exc)
        assert sentinel.read_text(encoding="utf-8") == "preserve me"
        assert list(existing.iterdir()) == [sentinel]


def test_validate_run_id_rejects_unsafe_names():
    for value in ("", " ", ".", "..", "../escape", "a/b", "a\\b", "C:drive"):
        try:
            runner.validate_run_id(value)
            assert False, f"Expected rejection for {value!r}"
        except runner.RunDirectoryCollisionError:
            pass


def test_validate_run_id_accepts_portable_name():
    assert runner.validate_run_id("phase15_lineage-validation.v2") == "phase15_lineage-validation.v2"


# ---------------------------------------------------------------------------
# Trends and source attribution
# ---------------------------------------------------------------------------


def test_find_previous_run_uses_latest_completed_metrics(tmp_path):
    import time
    base_dir = tmp_path / "output"
    older = base_dir / "older"
    newer = base_dir / "newer"
    current = base_dir / "current"
    for run_dir in (older, newer, current):
        run_dir.mkdir(parents=True)
    (older / "run_metrics.json").write_text("{}", encoding="utf-8")
    time.sleep(0.02)
    (newer / "run_metrics.json").write_text("{}", encoding="utf-8")
    (current / "run_metrics.json").write_text("{}", encoding="utf-8")

    previous = runner.find_previous_run(base_dir, "current")

    assert previous == newer


def test_write_trend_reports_compares_previous_metrics(tmp_path):
    previous = tmp_path / "output" / "previous"
    current = tmp_path / "output" / "current"
    previous.mkdir(parents=True)
    current.mkdir(parents=True)
    (previous / "run_metrics.json").write_text(
        json.dumps({
            "staged_event_count": 10,
            "merged_event_count": 10,
            "events_with_theme_tags": 8,
            "theme_tag_percent": 80.0,
            "warning_count": 1,
            "error_count": 0,
            "duplicate_conflict_count": 0,
            "runner_timing_seconds": 3.0,
        }),
        encoding="utf-8",
    )

    trend = runner.write_trend_reports(
        current,
        {
            "staged_event_count": 12,
            "merged_event_count": 11,
            "events_with_theme_tags": 10,
            "theme_tag_percent": 90.91,
            "warning_count": 0,
            "error_count": 0,
            "duplicate_conflict_count": 0,
            "runner_timing_seconds": 4.5,
        },
        previous,
    )

    assert trend["status"] == "COMPARED"
    assert trend["previous_run_id"] == "previous"
    assert (current / "trend_report.json").is_file()
    assert (current / "trend_report.md").is_file()
    by_metric = {item["metric"]: item for item in trend["comparisons"]}
    assert by_metric["staged_event_count"]["delta"] == 2
    assert by_metric["warning_count"]["delta"] == -1


def test_write_source_attribution_counts_normalised_events(tmp_path):
    run_dir = tmp_path / "run"
    normalised = run_dir / "pipeline" / "normalised"
    normalised.mkdir(parents=True)
    (normalised / "01_source.md").write_text("---\nevent_count: 3\n---\n", encoding="utf-8")
    (run_dir / "staged_input").mkdir(parents=True)
    (run_dir / "staged_input" / "01_source.md").write_text("x", encoding="utf-8")

    attribution = runner.write_source_attribution(
        run_dir,
        {"staged_files": ["01_source.md"]},
    )

    assert attribution["source_count"] == 1
    assert attribution["total_contributed_event_count"] == 3
    assert attribution["sources"][0]["contributed_event_count"] == 3
    assert (run_dir / "source_attribution.json").is_file()


# ---------------------------------------------------------------------------
# Ontology output
# ---------------------------------------------------------------------------


def test_ontology_output_contains_ten_entity_types(tmp_path):
    manifest = _valid_manifest_dict(_repo_root())
    run_dir = tmp_path / "ont_test"
    run_dir.mkdir(parents=True, exist_ok=True)

    run_metrics = {
        "staged_files": ["01_commit_history.md", "02_digest.md"],
        "merged_event_count": 200,
        "tagged_event_count": 200,
        "events_with_theme_tags": 194,
        "extraction_coverage_percent": 100.0,
        "error_count": 0,
        "warning_count": 0,
        "input_file_count": 3,
        "staged_event_count": 200,
    }
    exit_codes = {"prepare": 0, "pipeline": 0, "summarize": 0}

    (run_dir / "trend_report.json").write_text("{}", encoding="utf-8")
    (run_dir / "trend_report.md").write_text("# Trend\n", encoding="utf-8")
    (run_dir / "source_attribution.json").write_text("{}", encoding="utf-8")

    runner.write_ontology_outputs(
        manifest,
        run_dir,
        run_metrics,
        exit_codes,
        6.96,
        trend_report={"previous_run_id": "previous_run"},
        source_attribution={"source_count": 2, "total_contributed_event_count": 200},
    )

    # topic_run_manifest.json
    manifest_path = run_dir / "topic_run_manifest.json"
    assert manifest_path.is_file()
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_data["topic"] == "insurancechatbot"
    assert "run_id" in manifest_data
    assert "commands" in manifest_data
    assert "exit_codes" in manifest_data
    assert manifest_data["schema_version"] == 1

    # topic_run_ontology.json
    ontology_path = run_dir / "topic_run_ontology.json"
    assert ontology_path.is_file()
    ontology = json.loads(ontology_path.read_text(encoding="utf-8"))

    assert ontology["topic"] == "insurancechatbot"
    assert ontology["run_id"] == "ont_test"

    # All 10 entity types present.
    entity_types = {e["type"] for e in ontology["entities"]}
    expected_types = {
        "Topic", "SourceBundle", "TopicAdapter", "TopicRun",
        "StagedSource", "ReportEvent", "Theme", "Metric",
        "EvidenceArtifact", "Verdict",
    }
    assert entity_types == expected_types, f"Missing: {expected_types - entity_types}"


    evidence_names = {
        e["name"] for e in ontology["entities"] if e["type"] == "EvidenceArtifact"
    }
    assert "topic_run_ontology.json" in evidence_names
    assert "trend_report.json" in evidence_names
    assert "trend_report.md" in evidence_names
    assert "source_attribution.json" in evidence_names

    run_entities = [e for e in ontology["entities"] if e["type"] == "TopicRun"]
    assert run_entities[0]["properties"]["previous_run"] == "previous_run"

    # All 7 relation types present.
    relation_names = {r["relation"] for r in ontology["relations"]}
    expected_relations = {
        "consumes", "uses_adapter", "produces", "contains",
        "tagged_with", "measures", "summarizes",
    }
    assert relation_names == expected_relations, f"Missing: {expected_relations - relation_names}"

    # Verdict = PASS (all gates met).
    verdict_entities = [e for e in ontology["entities"] if e["type"] == "Verdict"]
    assert len(verdict_entities) == 1
    assert verdict_entities[0]["properties"]["verdict"] == "PASS"

def test_topic_run_manifest_paths_are_repo_relative(tmp_path):
    manifest = _valid_manifest_dict(_repo_root())
    run_dir = tmp_path / "portable_test"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "trend_report.json").write_text("{}", encoding="utf-8")
    (run_dir / "trend_report.md").write_text("# Trend\n", encoding="utf-8")
    (run_dir / "source_attribution.json").write_text("{}", encoding="utf-8")

    runner.write_ontology_outputs(
        manifest, run_dir, {}, {"prepare": 0, "pipeline": 0, "summarize": 0}, 1.0
    )

    data = json.loads((run_dir / "topic_run_manifest.json").read_text(encoding="utf-8"))
    assert data["_repo_root"] == manifest["_repo_root"]
    for key in ("input_dir", "themes_config", "index_config", "output_base_dir"):
        assert not Path(data[key]).is_absolute(), key
    assert not Path(data["adapter"]["script"]).is_absolute()
    assert Path(data["input_dir_abs"]).is_absolute()
    assert Path(data["adapter_abs"]["script"]).is_absolute()



def test_ontology_verdict_fail_when_stage_fails(tmp_path):
    manifest = _valid_manifest_dict(_repo_root())
    run_dir = tmp_path / "fail_verdict"
    run_dir.mkdir(parents=True, exist_ok=True)

    run_metrics = {
        "merged_event_count": 0,
        "events_with_theme_tags": 0,
        "extraction_coverage_percent": 0.0,
        "error_count": 1,
    }
    exit_codes = {"prepare": 1, "pipeline": 0, "summarize": 0}

    runner.write_ontology_outputs(manifest, run_dir, run_metrics, exit_codes, 1.0)

    ontology = json.loads(
        (run_dir / "topic_run_ontology.json").read_text(encoding="utf-8")
    )
    verdict_entities = [e for e in ontology["entities"] if e["type"] == "Verdict"]
    assert verdict_entities[0]["properties"]["verdict"] == "FAIL"


def test_ontology_verdict_review_when_coverage_low(tmp_path):
    manifest = _valid_manifest_dict(_repo_root())
    run_dir = tmp_path / "review_cov"
    run_dir.mkdir(parents=True, exist_ok=True)

    run_metrics = {
        "merged_event_count": 100,
        "events_with_theme_tags": 30,
        "extraction_coverage_percent": 50.0,
        "error_count": 0,
    }
    exit_codes = {"prepare": 0, "pipeline": 0, "summarize": 0}

    runner.write_ontology_outputs(manifest, run_dir, run_metrics, exit_codes, 1.0)

    ontology = json.loads(
        (run_dir / "topic_run_ontology.json").read_text(encoding="utf-8")
    )
    verdict_entities = [e for e in ontology["entities"] if e["type"] == "Verdict"]
    assert verdict_entities[0]["properties"]["verdict"] == "REVIEW"


def test_synthetic_metrics_in_ontology(tmp_path):
    """Scalar metric values from run_metrics appear in ontology Metric entity."""
    manifest = _valid_manifest_dict(_repo_root())
    run_dir = tmp_path / "synthetic"
    run_dir.mkdir(parents=True, exist_ok=True)

    run_metrics = {
        "staged_event_count": 42,
        "merged_event_count": 40,
        "events_with_theme_tags": 38,
        "extraction_coverage_percent": 95.24,
        "error_count": 0,
        "warning_count": 2,
        "input_file_count": 3,
        "staged_files": ["f1.md"],
    }
    exit_codes = {"prepare": 0, "pipeline": 0, "summarize": 0}

    runner.write_ontology_outputs(manifest, run_dir, run_metrics, exit_codes, 5.0)

    ontology = json.loads(
        (run_dir / "topic_run_ontology.json").read_text(encoding="utf-8")
    )
    metric_entities = [e for e in ontology["entities"] if e["type"] == "Metric"]
    assert len(metric_entities) == 1
    props = metric_entities[0]["properties"]
    assert props["staged_event_count"] == 42
    assert props["merged_event_count"] == 40
    assert props["extraction_coverage_percent"] == 95.24


# ---------------------------------------------------------------------------
# Phase 15 preparation-metrics contract and lineage-aware attribution
# ---------------------------------------------------------------------------


def _valid_common_metrics(**overrides):
    base = {
        "input_file_count": 1,
        "candidate_total_sections": 2,
        "staged_event_count": 2,
        "extraction_coverage_percent": 100.0,
        "staged_files": ["01_source.md"],
    }
    base.update(overrides)
    return base


def _valid_lineage_metrics(**overrides):
    metrics = _valid_common_metrics(
        source_lineage=[{
            "source_file": "source.md",
            "staged_file": "01_source.md",
            "candidate_count": 2,
            "staged_event_count": 2,
        }],
    )
    metrics.update(overrides)
    return metrics


def test_validate_prepare_metrics_accepts_common_without_lineage():
    metrics = _valid_common_metrics()
    assert runner.validate_prepare_metrics(metrics) is metrics


def test_validate_prepare_metrics_accepts_valid_lineage():
    metrics = _valid_lineage_metrics()
    assert runner.validate_prepare_metrics(metrics, require_lineage=True) is metrics


def test_validate_prepare_metrics_zero_sources_empty_lineage_when_required():
    metrics = _valid_common_metrics(
        input_file_count=0,
        candidate_total_sections=0,
        staged_event_count=0,
        extraction_coverage_percent=0.0,
        staged_files=[],
        source_lineage=[],
    )
    assert runner.validate_prepare_metrics(metrics, require_lineage=True) is metrics


def test_validate_prepare_metrics_rejects_missing_field():
    metrics = _valid_common_metrics()
    del metrics["staged_event_count"]
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "staged_event_count" in str(exc)


def test_validate_prepare_metrics_rejects_non_dict_root():
    try:
        runner.validate_prepare_metrics(["not", "a", "dict"])  # type: ignore[arg-type]
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "object" in str(exc).lower()


def test_validate_prepare_metrics_rejects_wrong_scalar_type():
    metrics = _valid_common_metrics(input_file_count="3")
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "input_file_count" in str(exc)


def test_validate_prepare_metrics_rejects_bool_as_integer():
    metrics = _valid_common_metrics(staged_event_count=True)
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "bool" in str(exc).lower() or "integer" in str(exc).lower()


def test_validate_prepare_metrics_rejects_negative_counts():
    metrics = _valid_common_metrics(candidate_total_sections=-1)
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "candidate_total_sections" in str(exc)


def test_validate_prepare_metrics_rejects_coverage_below_zero():
    metrics = _valid_common_metrics(extraction_coverage_percent=-0.1)
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "extraction_coverage_percent" in str(exc)


def test_validate_prepare_metrics_rejects_coverage_above_100():
    metrics = _valid_common_metrics(extraction_coverage_percent=100.1)
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "extraction_coverage_percent" in str(exc)


def test_validate_prepare_metrics_rejects_non_finite_coverage():
    for value in (math.nan, math.inf, -math.inf):
        metrics = _valid_common_metrics(extraction_coverage_percent=value)
        try:
            runner.validate_prepare_metrics(metrics)
            assert False, f"Expected AdapterMetricsError for {value!r}"
        except runner.AdapterMetricsError as exc:
            assert "finite" in str(exc).lower()


def test_validate_prepare_metrics_rejects_staged_files_not_list():
    metrics = _valid_common_metrics(staged_files="01_source.md")
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "staged_files" in str(exc)


def test_validate_prepare_metrics_rejects_empty_staged_path():
    metrics = _valid_common_metrics(staged_files=[""])
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "non-empty" in str(exc).lower() or "staged_files" in str(exc)


def test_normalize_metrics_path_rejects_dot_only_and_separators():
    for value in (".", "./", ".\\", "/", "//"):
        try:
            runner.normalize_metrics_path(value, "path")
            assert False, f"Expected rejection for {value!r}"
        except runner.AdapterMetricsError:
            pass


def test_validate_prepare_metrics_rejects_nested_staged_paths():
    for value in ("folder/a.md", "folder\\a.md"):
        metrics = _valid_common_metrics(staged_files=[value])
        try:
            runner.validate_prepare_metrics(metrics)
            assert False, f"Expected AdapterMetricsError for {value!r}"
        except runner.AdapterMetricsError as exc:
            assert "top-level filename" in str(exc).lower()


def test_normalize_metrics_path_slash_equivalence():
    assert runner.normalize_metrics_path("folder\\a.md", "p") == "folder/a.md"
    assert runner.normalize_metrics_path("folder/a.md", "p") == "folder/a.md"


def test_nested_source_lineage_path_remains_valid():
    metrics = _valid_lineage_metrics(
        source_lineage=[{
            "source_file": "nested/source.md",
            "staged_file": "01_source.md",
            "candidate_count": 2,
            "staged_event_count": 2,
        }],
    )
    assert runner.validate_prepare_metrics(metrics, require_lineage=True) is metrics


def test_nested_lineage_staged_path_is_rejected():
    metrics = _valid_lineage_metrics(
        staged_files=["01_source.md"],
        source_lineage=[{
            "source_file": "nested/source.md",
            "staged_file": "nested/01_source.md",
            "candidate_count": 2,
            "staged_event_count": 2,
        }],
    )
    try:
        runner.validate_prepare_metrics(metrics, require_lineage=True)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "top-level filename" in str(exc).lower()


def test_normalize_metrics_path_rejects_drive_unc_leading_slash_traversal():
    for value in ("C:/a.md", "C:\\a.md", "//server/share/a.md", "/abs/a.md", "a/../b.md"):
        try:
            runner.normalize_metrics_path(value, "path")
            assert False, f"Expected rejection for {value!r}"
        except runner.AdapterMetricsError:
            pass


def test_validate_prepare_metrics_requires_lineage_when_asked():
    try:
        runner.validate_prepare_metrics(_valid_common_metrics(), require_lineage=True)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "source_lineage" in str(exc)


def test_validate_prepare_metrics_rejects_lineage_not_list():
    metrics = _valid_common_metrics(source_lineage={"source_file": "a.md"})
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "source_lineage" in str(exc)


def test_validate_prepare_metrics_rejects_missing_lineage_field():
    metrics = _valid_lineage_metrics(
        source_lineage=[{
            "source_file": "source.md",
            "staged_file": "01_source.md",
            "candidate_count": 2,
        }],
    )
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "staged_event_count" in str(exc)


def test_validate_prepare_metrics_accepts_extra_lineage_fields():
    metrics = _valid_lineage_metrics(
        source_lineage=[{
            "source_file": "source.md",
            "staged_file": "01_source.md",
            "candidate_count": 2,
            "staged_event_count": 2,
            "note": "forward-compat",
        }],
    )
    assert runner.validate_prepare_metrics(metrics, require_lineage=True) is metrics


def test_validate_prepare_metrics_rejects_duplicate_lineage_sources():
    metrics = _valid_common_metrics(
        input_file_count=2,
        candidate_total_sections=2,
        staged_event_count=2,
        staged_files=["01_a.md", "02_b.md"],
        source_lineage=[
            {
                "source_file": "same.md",
                "staged_file": "01_a.md",
                "candidate_count": 1,
                "staged_event_count": 1,
            },
            {
                "source_file": "same.md",
                "staged_file": "02_b.md",
                "candidate_count": 1,
                "staged_event_count": 1,
            },
        ],
    )
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "source_file" in str(exc)


def test_validate_prepare_metrics_rejects_duplicate_lineage_staged():
    metrics = _valid_common_metrics(
        input_file_count=2,
        candidate_total_sections=2,
        staged_event_count=2,
        staged_files=["01_a.md", "02_b.md"],
        source_lineage=[
            {
                "source_file": "a.md",
                "staged_file": "01_a.md",
                "candidate_count": 1,
                "staged_event_count": 1,
            },
            {
                "source_file": "b.md",
                "staged_file": "01_a.md",
                "candidate_count": 1,
                "staged_event_count": 1,
            },
        ],
    )
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "staged_file" in str(exc)


def test_validate_prepare_metrics_rejects_negative_lineage_count():
    metrics = _valid_lineage_metrics(
        source_lineage=[{
            "source_file": "source.md",
            "staged_file": "01_source.md",
            "candidate_count": -1,
            "staged_event_count": 2,
        }],
    )
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "candidate_count" in str(exc)


def test_validate_prepare_metrics_rejects_lineage_length_mismatch():
    metrics = _valid_lineage_metrics(input_file_count=2)
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "input_file_count" in str(exc)


def test_validate_prepare_metrics_rejects_candidate_total_mismatch():
    metrics = _valid_lineage_metrics(candidate_total_sections=99)
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "candidate_total_sections" in str(exc)


def test_validate_prepare_metrics_rejects_staged_total_mismatch():
    metrics = _valid_lineage_metrics(staged_event_count=99)
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "staged_event_count" in str(exc)


def test_validate_prepare_metrics_rejects_lineage_staged_set_mismatch():
    metrics = _valid_lineage_metrics(
        source_lineage=[{
            "source_file": "source.md",
            "staged_file": "99_other.md",
            "candidate_count": 2,
            "staged_event_count": 2,
        }],
    )
    try:
        runner.validate_prepare_metrics(metrics)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "staged_file set" in str(exc)


def test_registered_adapter_id_requires_lineage_even_with_explicit_script():
    assert "prepare_insurancechatbot_chronicle" in runner.ADAPTER_REGISTRY
    require_lineage = "prepare_insurancechatbot_chronicle" in runner.ADAPTER_REGISTRY
    try:
        runner.validate_prepare_metrics(_valid_common_metrics(), require_lineage=require_lineage)
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError as exc:
        assert "source_lineage" in str(exc)


def test_custom_adapter_may_omit_lineage():
    require_lineage = "custom_unregistered_adapter" in runner.ADAPTER_REGISTRY
    assert require_lineage is False
    metrics = _valid_common_metrics()
    assert runner.validate_prepare_metrics(metrics, require_lineage=require_lineage) is metrics


def test_load_enrich_validate_does_not_rewrite_invalid_metrics(tmp_path):
    metrics_path = tmp_path / "prepare_metrics.json"
    raw = {"staged_event_count": 1, "note": "incomplete"}
    metrics_path.write_text(json.dumps(raw), encoding="utf-8")
    before = metrics_path.read_text(encoding="utf-8")

    try:
        runner.load_enrich_validate_prepare_metrics(
            metrics_path,
            topic="t",
            require_lineage=False,
        )
        assert False, "Expected AdapterMetricsError"
    except runner.AdapterMetricsError:
        pass

    after = metrics_path.read_text(encoding="utf-8")
    assert after == before
    assert "topic" not in json.loads(after)


def test_run_report_invalid_metrics_blocks_pipeline_and_sets_prepare_fail(tmp_path, monkeypatch):
    manifest_path, _ = _valid_manifest_file(tmp_path)
    manifest = runner.load_manifest(str(manifest_path))
    # Registered ID claims the registered metrics contract even with an
    # explicit custom script path (require_lineage=True).
    manifest["adapter"]["id"] = "prepare_insurancechatbot_chronicle"
    called_labels: list[str] = []

    def fake_run_stage(cmd, label, *, dry_run=False, capture_output_to=None):
        called_labels.append(label)
        if "prepare" in label:
            run_dir = Path(manifest["output"]["base_dir"]) / "contract_fail"
            metrics_path = run_dir / "prepare_metrics.json"
            metrics_path.parent.mkdir(parents=True, exist_ok=True)
            # Valid common fields but missing required lineage for registered ID.
            metrics_path.write_text(
                json.dumps(_valid_common_metrics()),
                encoding="utf-8",
            )
            (run_dir / "staged_input").mkdir(parents=True, exist_ok=True)
            return {"exit_code": 0, "output": ""}
        raise AssertionError(f"pipeline/summarize should not run: {label}")

    monkeypatch.setattr(runner, "run_stage", fake_run_stage)

    result = runner.run_report(manifest, run_id="contract_fail")
    assert result["exit_codes"][runner.CMD_PREPARE] == 1
    assert runner.CMD_PIPELINE not in result["exit_codes"]
    assert any("prepare" in label for label in called_labels)
    assert not any("pipeline" in label for label in called_labels)

    log_text = (Path(result["run_dir"]) / "run.log").read_text(encoding="utf-8")
    assert "Adapter process exited 0" in log_text
    assert "prepare metrics contract validation failed" in log_text

    ontology = json.loads(
        (Path(result["run_dir"]) / "topic_run_ontology.json").read_text(encoding="utf-8")
    )
    verdicts = [e for e in ontology["entities"] if e["type"] == "Verdict"]
    assert verdicts and verdicts[0]["properties"].get("verdict") == "FAIL"

    # Adapter raw metrics remain without topic rewrite.
    saved = json.loads(
        (Path(result["run_dir"]) / "prepare_metrics.json").read_text(encoding="utf-8")
    )
    assert "topic" not in saved


def test_main_returns_nonzero_when_run_report_has_prepare_failure(monkeypatch, tmp_path):
    manifest_path, _ = _valid_manifest_file(tmp_path)

    def fake_run_report(manifest, *, dry_run=False, run_id=None):
        return {
            "run_dir": str(tmp_path / "out"),
            "exit_codes": {runner.CMD_PREPARE: 1},
            "run_metrics": {},
            "timing_seconds": 0.0,
        }

    monkeypatch.setattr(runner, "run_report", fake_run_report)
    monkeypatch.setattr(runner, "load_manifest", lambda path: {"topic": "t"})
    code = runner.main(["--manifest", str(manifest_path)])
    assert code == 1


def test_write_source_attribution_prefers_lineage(tmp_path):
    run_dir = tmp_path / "run"
    normalised = run_dir / "pipeline" / "normalised"
    normalised.mkdir(parents=True)
    (normalised / "01_source.md").write_text("---\nevent_count: 10\n---\n", encoding="utf-8")
    (run_dir / "staged_input").mkdir(parents=True)

    attribution = runner.write_source_attribution(
        run_dir,
        {"staged_files": ["01_source.md"]},
        source_lineage=[{
            "source_file": "ARCHIVE_REPORT.md",
            "staged_file": "01_source.md",
            "candidate_count": 11,
            "staged_event_count": 11,
        }],
    )
    entry = attribution["sources"][0]
    assert entry["source_file"] == "ARCHIVE_REPORT.md"
    assert entry["staged_event_count"] == 11
    assert entry["contributed_event_count"] == 10
    assert entry["count_mismatch"] is True
    assert attribution["total_contributed_event_count"] == 10


def test_write_source_attribution_legacy_without_lineage(tmp_path):
    run_dir = tmp_path / "run"
    normalised = run_dir / "pipeline" / "normalised"
    normalised.mkdir(parents=True)
    (normalised / "01_source.md").write_text("---\nevent_count: 3\n---\n", encoding="utf-8")

    attribution = runner.write_source_attribution(
        run_dir,
        {"staged_files": ["01_source.md"]},
    )
    entry = attribution["sources"][0]
    assert "source_file" not in entry
    assert "staged_event_count" not in entry
    assert "count_mismatch" not in entry
    assert entry["contributed_event_count"] == 3


def test_write_source_attribution_equal_counts_no_mismatch(tmp_path):
    run_dir = tmp_path / "run"
    normalised = run_dir / "pipeline" / "normalised"
    normalised.mkdir(parents=True)
    (normalised / "01_source.md").write_text("---\nevent_count: 11\n---\n", encoding="utf-8")

    attribution = runner.write_source_attribution(
        run_dir,
        {"staged_files": ["01_source.md"]},
        source_lineage=[{
            "source_file": "ARCHIVE_REPORT.md",
            "staged_file": "01_source.md",
            "candidate_count": 11,
            "staged_event_count": 11,
        }],
    )
    assert attribution["sources"][0]["count_mismatch"] is False


def test_write_source_attribution_missing_normalised_is_zero_mismatch(tmp_path):
    run_dir = tmp_path / "run"
    (run_dir / "pipeline" / "normalised").mkdir(parents=True)

    attribution = runner.write_source_attribution(
        run_dir,
        {"staged_files": ["01_source.md"]},
        source_lineage=[{
            "source_file": "ARCHIVE_REPORT.md",
            "staged_file": "01_source.md",
            "candidate_count": 5,
            "staged_event_count": 5,
        }],
    )
    entry = attribution["sources"][0]
    assert entry["contributed_event_count"] == 0
    assert entry["count_mismatch"] is True


def test_write_source_attribution_order_follows_staged_files_and_slash_lookup(tmp_path):
    run_dir = tmp_path / "run"
    normalised = run_dir / "pipeline" / "normalised"
    normalised.mkdir(parents=True)
    (normalised / "01_a.md").write_text("---\nevent_count: 1\n---\n", encoding="utf-8")
    (normalised / "02_b.md").write_text("---\nevent_count: 2\n---\n", encoding="utf-8")

    attribution = runner.write_source_attribution(
        run_dir,
        {"staged_files": ["01_a.md", "02_b.md"]},
        source_lineage=[
            {
                "source_file": "b.md",
                "staged_file": "02_b.md",
                "candidate_count": 2,
                "staged_event_count": 2,
            },
            {
                "source_file": "a.md",
                "staged_file": r"01_a.md",
                "candidate_count": 1,
                "staged_event_count": 1,
            },
        ],
    )
    assert [s["staged_filename"] for s in attribution["sources"]] == ["01_a.md", "02_b.md"]
    assert attribution["sources"][0]["source_file"] == "a.md"
    assert attribution["sources"][1]["source_file"] == "b.md"
