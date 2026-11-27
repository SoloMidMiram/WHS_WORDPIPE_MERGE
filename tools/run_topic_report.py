#!/usr/bin/env python3
"""Generic Topic Report Runner — Phase 13.

One-command runner that reads a topic manifest, invokes the topic's adapter
(prepare + summarize), runs the Chronicle pipeline (chain.ps1), captures
performance timing, and emits ontology-ready outputs.

Usage:
    python tools\\run_topic_report.py --manifest <path> [--dry-run] [--run-id <id>]

Design constraints:
    - Offline, Windows/PowerShell compatible (stdlib + wordpipe.chronicle for
      Phase 16 normalised fingerprinting / correlation).
    - Topic-specific parsing stays in the adapter (outside pipeline/).
    - wordpipe/ does not import tools/.
    - pipeline/index.py stays where it is.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if __name__ == "__main__" and "WORDPIPE_ORIGIN_QUALIFICATION" in os.environ:
    from runpy import run_path

    run_path(str(_REPO_ROOT_FOR_IMPORT / "pipeline" / "_import_origin.py"))["require_driver"](
        __file__, "wordpipe.execution", "wordpipe.markdown_contract",
    )

# Ensure repo root is importable when invoked as a script.
if str(_REPO_ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_FOR_IMPORT))


from wordpipe.markdown_contract import (
    LEGACY_MODE,
    MARKDOWN_MODES,
    STRUCTURAL_CORRELATION_SCHEMA,
    STRUCTURAL_LINEAGE_SCHEMA,
    STRUCTURAL_MODE,
    STRUCTURAL_RAW_SCHEMA,
)
from wordpipe.execution import Cancellation, ExecutionPolicy, Outcome, execute, write_terminal_evidence

STRUCTURAL_ROOT_MARKER = ".md01-structural-v1"
GENERIC_MARKDOWN = "prepare_generic_markdown_chronicle"
REPO_ANCHOR = Path("pipeline") / "chain.ps1"

REQUIRED_MANIFEST_KEYS: list[str] = [
    "schema_version",
    "topic",
    "input_dir",
    "adapter",
    "output",
    "quality_gates",
]
REQUIRED_ADAPTER_KEYS: list[str] = ["id"]
REQUIRED_OUTPUT_KEYS: list[str] = ["base_dir", "run_id_format"]

ADAPTER_REGISTRY: dict[str, dict[str, str]] = {
    "prepare_insurancechatbot_chronicle": {
        "script": "tools/prepare_insurancechatbot_chronicle.py",
        "prepare_command": "prepare",
        "summarize_command": "summarize",
    },
    "prepare_generic_markdown_chronicle": {
        "script": "tools/prepare_generic_markdown_chronicle.py",
        "prepare_command": "prepare",
        "summarize_command": "summarize",
    },
}

# Core evidence artifacts that every run should produce.
CORE_EVIDENCE_FILES: list[str] = [
    "RUN_SUMMARY.md",
    "run_metrics.json",
    "prepare_metrics.json",
    "run.log",
    "performance.txt",
    "topic_run_manifest.json",
    "topic_run_ontology.json",
]

OPTIONAL_EVIDENCE_FILES: list[str] = [
    "trend_report.json",
    "trend_report.md",
    "source_attribution.json",
    "event_lineage.json",
    "event_correlation.json",
]

TREND_METRICS: list[str] = [
    "staged_event_count",
    "merged_event_count",
    "events_with_theme_tags",
    "theme_tag_percent",
    "warning_count",
    "error_count",
    "duplicate_conflict_count",
    "runner_timing_seconds",
]


class ManifestError(ValueError):
    """Raised when a topic manifest is invalid."""


class AdapterMetricsError(ValueError):
    """Raised when adapter preparation metrics violate the runner contract."""


class ProvenanceError(ValueError):
    """Raised when event lineage or correlation provenance fails closed."""


class RunDirectoryCollisionError(ValueError):
    """Raised when a report run would reuse or escape its output directory."""


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def find_repo_root(manifest_path: Path) -> Path:
    """Walk up from *manifest_path* until we find the repo anchor file."""
    manifest_path = manifest_path.resolve()
    for parent in [manifest_path] + list(manifest_path.parents):
        if (parent / REPO_ANCHOR).is_file():
            return parent
    raise ManifestError(
        f"Cannot find repo root (looked for {REPO_ANCHOR}) "
        f"from manifest at {manifest_path}"
    )


def resolve_manifest_path(manifest_path: Path, repo_root: Path) -> Path:
    """Resolve a path from the manifest against the repo root.

    If *manifest_path* is already absolute it is returned as-is.
    """
    p = Path(manifest_path)
    return p if p.is_absolute() else (repo_root / p).resolve()


# ---------------------------------------------------------------------------
# Manifest loading & validation
# ---------------------------------------------------------------------------


def load_manifest(
    manifest_path: str | Path,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load and validate a topic manifest JSON file.

    If *repo_root* is ``None`` it is auto-detected by walking up from
    the manifest file until ``pipeline/chain.ps1`` is found.

    Returns the resolved manifest dict (relative paths converted to
    paths absolute). Raises ``ManifestError`` on any issue.
    """
    path = Path(manifest_path)
    if not path.is_file():
        raise ManifestError(f"Manifest file not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ManifestError("Manifest must be a JSON object (dict)")

    _require_keys(raw, REQUIRED_MANIFEST_KEYS, "manifest root")

    if not isinstance(raw["schema_version"], int) or raw["schema_version"] < 1:
        raise ManifestError(f"schema_version must be a positive int, got {raw['schema_version']!r}")

    if not isinstance(raw["topic"], str) or not raw["topic"].strip():
        raise ManifestError(f"topic must be a non-empty string, got {raw['topic']!r}")

    if not isinstance(raw["adapter"], dict):
        raise ManifestError("adapter must be a JSON object (dict)")
    _require_keys(raw["adapter"], REQUIRED_ADAPTER_KEYS, "adapter")
    _require_keys(raw["output"], REQUIRED_OUTPUT_KEYS, "output")

    # Resolve paths relative to repo root.
    if repo_root is not None:
        repo_root = Path(repo_root).resolve()
    else:
        repo_root = find_repo_root(path)
    raw["_repo_root"] = str(repo_root)

    for rel_key in ("input_dir",):
        raw[rel_key] = str(resolve_manifest_path(raw[rel_key], repo_root))

    raw["adapter"] = resolve_adapter(raw["adapter"], repo_root)
    raw["themes_config"] = str(resolve_manifest_path(raw["themes_config"], repo_root))
    raw["index_config"] = str(resolve_manifest_path(raw["index_config"], repo_root))
    raw["output"]["base_dir"] = str(resolve_manifest_path(raw["output"]["base_dir"], repo_root))
    if raw["adapter"].get("markdown_mode") == STRUCTURAL_MODE:
        legacy_dir = raw["output"].get("legacy_base_dir")
        if not isinstance(legacy_dir, str) or not legacy_dir.strip():
            raise ManifestError("structural-v1 requires output.legacy_base_dir for isolation")
        raw["output"]["legacy_base_dir"] = str(resolve_manifest_path(legacy_dir, repo_root))

    # Validate paths exist.
    _require_existing_dir(raw["input_dir"], "input_dir")
    _require_existing_file(raw["adapter"]["script"], "adapter.script")
    _require_existing_file(raw["themes_config"], "themes_config")
    _require_existing_file(raw["index_config"], "index_config")

    # Validate quality gates.
    gates = raw["quality_gates"]
    for gate_key in ("min_extraction_coverage_percent", "min_theme_tag_percent", "max_error_count"):
        val = gates.get(gate_key)
        if val is None:
            raise ManifestError(f"Missing quality_gates.{gate_key}")
        if not isinstance(val, (int, float)):
            raise ManifestError(f"quality_gates.{gate_key} must be numeric, got {type(val).__name__}")
        if val < 0:
            raise ManifestError(f"quality_gates.{gate_key} must be >= 0, got {val}")

    return raw


def resolve_adapter(adapter: dict[str, Any], repo_root: str | Path) -> dict[str, Any]:
    """Resolve adapter registry/defaults while preserving manifest overrides."""
    adapter_id = adapter.get("id")
    if not isinstance(adapter_id, str) or not adapter_id.strip():
        raise ManifestError(f"adapter.id must be a non-empty string, got {adapter_id!r}")

    if "markdown_mode" in adapter:
        if adapter_id != GENERIC_MARKDOWN or adapter["markdown_mode"] not in MARKDOWN_MODES:
            raise ManifestError("markdown_mode requires the generic Markdown adapter and legacy-v1 or structural-v1")
        if adapter["markdown_mode"] == STRUCTURAL_MODE and "script" in adapter:
            raise ManifestError("structural-v1 requires the registered generic Markdown adapter script")
    if "heading_levels" in adapter:
        levels = adapter["heading_levels"]
        if (
            adapter.get("markdown_mode") != STRUCTURAL_MODE
            or not isinstance(levels, list)
            or not levels
            or any(type(level) is not int or level not in range(2, 7) for level in levels)
            or len(set(levels)) != len(levels)
        ):
            raise ManifestError("heading_levels requires structural-v1 and unique integer levels in 2–6")
    registry_entry = ADAPTER_REGISTRY.get(adapter_id)
    script = adapter.get("script")
    if script is None:
        if registry_entry is None:
            raise ManifestError(
                f"adapter.script is required for unregistered adapter id {adapter_id!r}"
            )
        script = registry_entry["script"]

    resolved = dict(adapter)
    resolved["script"] = str(resolve_manifest_path(script, Path(repo_root)))
    resolved["prepare_command"] = str(
        adapter.get(
            "prepare_command",
            registry_entry.get("prepare_command", CMD_PREPARE) if registry_entry else CMD_PREPARE,
        )
    )
    resolved["summarize_command"] = str(
        adapter.get(
            "summarize_command",
            registry_entry.get("summarize_command", CMD_SUMMARIZE) if registry_entry else CMD_SUMMARIZE,
        )
    )
    resolved["registry_backed"] = registry_entry is not None and "script" not in adapter
    return resolved


def _require_keys(obj: dict[str, Any], keys: list[str], context: str) -> None:
    for k in keys:
        if k not in obj:
            raise ManifestError(f"Missing required key '{k}' in {context}")


def _require_existing_dir(path_str: str, label: str) -> None:
    p = Path(path_str)
    if not p.is_dir():
        raise ManifestError(f"{label} directory does not exist: {p}")


def _require_existing_file(path_str: str, label: str) -> None:
    p = Path(path_str)
    if not p.is_file():
        raise ManifestError(f"{label} file does not exist: {p}")


# ---------------------------------------------------------------------------
# Command construction
# ---------------------------------------------------------------------------


CMD_PREPARE = "prepare"
CMD_PIPELINE = "pipeline"
CMD_SUMMARIZE = "summarize"
_SUMMARY_REPORTABLE_OUTCOMES = (Outcome.SUCCESS, Outcome.NATIVE_FAILURE)
CMD_PROVENANCE = "provenance"


def build_commands(manifest: dict[str, Any], run_dir: Path) -> dict[str, list[str]]:
    """Return the argv lists for the three subprocess stages.

    Keys: ``prepare``, ``pipeline``, ``summarize``.
    """
    adapter_script = manifest["adapter"]["script"]
    staged_dir = run_dir / "staged_input"
    metrics_path = run_dir / "prepare_metrics.json"
    perf_path = run_dir / "performance.txt"
    log_path = run_dir / "run.log"
    pipeline_dir = run_dir / "pipeline"

    prepare_cmd = [
        sys.executable,
        adapter_script,
        manifest["adapter"].get("prepare_command", CMD_PREPARE),
        "--input-dir", manifest["input_dir"],
        "--output-dir", str(staged_dir),
        "--metrics", str(metrics_path),
    ]

    if "markdown_mode" in manifest["adapter"]:
        prepare_cmd.extend(["--markdown-mode", manifest["adapter"]["markdown_mode"]])
    if "heading_levels" in manifest["adapter"]:
        prepare_cmd.extend(["--heading-levels", *map(str, manifest["adapter"]["heading_levels"])])

    shell = "powershell" if os.name == "nt" or not shutil.which("pwsh") else "pwsh"
    pipeline_cmd = [
        shell, "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", str(Path(manifest["_repo_root"]) / "pipeline" / "chain.ps1"),
        "-InputDir", str(staged_dir),
        "-OutputDir", str(pipeline_dir),
        "-ThemesConfig", manifest["themes_config"],
        "-IndexConfig", manifest["index_config"],
        "-Verbose",
    ]

    summarize_cmd = [
        sys.executable,
        adapter_script,
        manifest["adapter"].get("summarize_command", CMD_SUMMARIZE),
        "--run-dir", str(run_dir),
        "--prepare-metrics", str(metrics_path),
        "--performance", str(perf_path),
        "--run-log", str(log_path),
    ]

    return {
        CMD_PREPARE: prepare_cmd,
        CMD_PIPELINE: pipeline_cmd,
        CMD_SUMMARIZE: summarize_cmd,
    }


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def run_stage(
    cmd: list[str],
    label: str,
    *,
    dry_run: bool = False,
    capture_output_to: str | None = None,
    policy: ExecutionPolicy = ExecutionPolicy(),
    evidence_path: Path | None = None,
    publish_owner: bool = False,
) -> dict[str, Any]:
    """Run a stage and return its exit code, bounded output and typed outcome.

    If *capture_output_to* is given, stdout+stderr is appended to that file.
    """
    if dry_run:
        print(f"  [DRY-RUN] {label}: {' '.join(cmd)}")
        return {"exit_code": 0, "output": "", "outcome": Outcome.SUCCESS}

    print(f"  [{label}] Starting...")

    result = execute(cmd, policy, publish_owner=publish_owner)
    if evidence_path is not None:
        evidence_path.parent.mkdir(exist_ok=True)
        write_terminal_evidence(evidence_path, result, policy)
    combined = result.stdout.text(policy.stdout_limit) + result.stderr.text(policy.stderr_limit)

    if capture_output_to:
        dest = Path(capture_output_to)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(combined)

    if result.exit_code != 0:
        print(f"  [{label}] FAILED ({result.outcome.value}, exit code {result.exit_code})")
        print(f"  [{label}] stderr snippet: {combined[-500:]}")
    else:
        print(f"  [{label}] OK (exit code {result.exit_code})")

    return {"exit_code": result.exit_code, "output": combined, "outcome": result.outcome}


def enrich_run_metrics(run_metrics: dict[str, Any], timing_seconds: float) -> dict[str, Any]:
    """Add runner-level scalar metrics used by trends and ontology output."""
    enriched = dict(run_metrics)
    merged_count = _as_number(enriched.get("merged_event_count"), default=0.0)
    tagged_count = _as_number(enriched.get("events_with_theme_tags"), default=0.0)
    enriched["theme_tag_percent"] = round((tagged_count / merged_count) * 100, 2) if merged_count else 0.0
    enriched["runner_timing_seconds"] = round(timing_seconds, 6)
    for key in ("warning_count", "error_count", "duplicate_conflict_count"):
        enriched[key] = int(_as_number(enriched.get(key), default=0.0))
    return enriched


# ---------------------------------------------------------------------------
# Preparation-metrics contract (Phase 15 provenance foundation)
# ---------------------------------------------------------------------------


def normalize_metrics_path(value: Any, field: str) -> str:
    """Normalize a portable relative metrics path for comparison (no filesystem)."""
    if not isinstance(value, str) or not value.strip():
        raise AdapterMetricsError(f"{field} must be a non-empty string")
    text = value.replace("\\", "/")
    if text.startswith("/") or text.startswith("//"):
        raise AdapterMetricsError(f"{field} must be a relative path, got {value!r}")
    if re.match(r"^[A-Za-z]:", text):
        raise AdapterMetricsError(f"{field} must not be drive-qualified, got {value!r}")
    parts: list[str] = []
    for part in text.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            raise AdapterMetricsError(f"{field} must not contain '..' path traversal, got {value!r}")
        parts.append(part)
    if not parts:
        raise AdapterMetricsError(f"{field} normalizes to an empty path, got {value!r}")
    return "/".join(parts)


def normalize_staged_filename(value: Any, field: str) -> str:
    """Return a validated top-level staged filename.

    Chronicle's pipeline consumes ``*.md`` directly from the staging directory,
    so accepting nested paths here would claim files that the pipeline ignores.
    """
    normalized = normalize_metrics_path(value, field)
    if "/" in normalized:
        raise AdapterMetricsError(
            f"{field} must be a top-level filename, got {value!r}"
        )
    return normalized


def validate_run_id(value: Any) -> str:
    """Validate a run ID as one portable directory name."""
    if not isinstance(value, str) or not value.strip():
        raise RunDirectoryCollisionError("run ID must be a non-empty string")
    if value != value.strip() or value in {".", ".."}:
        raise RunDirectoryCollisionError(f"unsafe run ID: {value!r}")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
        raise RunDirectoryCollisionError(
            "run ID must be one portable directory name containing only "
            f"letters, digits, '.', '_', or '-': {value!r}"
        )
    return value


def _require_non_bool_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AdapterMetricsError(
            f"{field} must be an integer (not bool), got {type(value).__name__}"
        )
    if value < 0:
        raise AdapterMetricsError(f"{field} must be >= 0, got {value}")
    return value


def _require_coverage_percent(value: Any, field: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AdapterMetricsError(
            f"{field} must be a number (not bool), got {type(value).__name__}"
        )
    if isinstance(value, float) and not math.isfinite(value):
        raise AdapterMetricsError(f"{field} must be finite, got {value}")
    if value < 0 or value > 100:
        raise AdapterMetricsError(f"{field} must be between 0 and 100, got {value}")
    return value


def validate_prepare_metrics(
    metrics: dict[str, Any],
    *,
    require_lineage: bool = False,
) -> dict[str, Any]:
    """Validate common preparation metrics (and lineage when present/required).

    Pure: no filesystem I/O. Returns *metrics* unchanged on success.
    """
    if not isinstance(metrics, dict):
        raise AdapterMetricsError(
            f"prepare metrics root must be a JSON object, got {type(metrics).__name__}"
        )

    for field in (
        "input_file_count",
        "candidate_total_sections",
        "staged_event_count",
    ):
        if field not in metrics:
            raise AdapterMetricsError(f"missing required field {field}")
        _require_non_bool_int(metrics[field], field)

    if "extraction_coverage_percent" not in metrics:
        raise AdapterMetricsError("missing required field extraction_coverage_percent")
    _require_coverage_percent(metrics["extraction_coverage_percent"], "extraction_coverage_percent")

    if "staged_files" not in metrics:
        raise AdapterMetricsError("missing required field staged_files")
    staged_files = metrics["staged_files"]
    if not isinstance(staged_files, list):
        raise AdapterMetricsError(
            f"staged_files must be a list, got {type(staged_files).__name__}"
        )

    normalized_staged: list[str] = []
    seen_staged: set[str] = set()
    for index, item in enumerate(staged_files):
        field = f"staged_files[{index}]"
        normalized = normalize_staged_filename(item, field)
        if normalized in seen_staged:
            raise AdapterMetricsError(f"staged_files contains duplicate path {normalized!r}")
        seen_staged.add(normalized)
        normalized_staged.append(normalized)

    lineage = metrics.get("source_lineage")
    if lineage is None:
        if require_lineage:
            raise AdapterMetricsError("source_lineage is required for registered adapters")
        return metrics

    if not isinstance(lineage, list):
        raise AdapterMetricsError(
            f"source_lineage must be a list, got {type(lineage).__name__}"
        )

    required_keys = ("source_file", "staged_file", "candidate_count", "staged_event_count")
    lineage_sources: set[str] = set()
    lineage_staged: set[str] = set()
    candidate_sum = 0
    staged_sum = 0

    for index, entry in enumerate(lineage):
        prefix = f"source_lineage[{index}]"
        if not isinstance(entry, dict):
            raise AdapterMetricsError(f"{prefix} must be an object")
        for key in required_keys:
            if key not in entry:
                raise AdapterMetricsError(f"{prefix} missing required field {key}")

        source_norm = normalize_metrics_path(entry["source_file"], f"{prefix}.source_file")
        staged_norm = normalize_staged_filename(
            entry["staged_file"], f"{prefix}.staged_file"
        )
        if source_norm in lineage_sources:
            raise AdapterMetricsError(
                f"{prefix}.source_file duplicates {source_norm!r}"
            )
        if staged_norm in lineage_staged:
            raise AdapterMetricsError(
                f"{prefix}.staged_file duplicates {staged_norm!r}"
            )
        lineage_sources.add(source_norm)
        lineage_staged.add(staged_norm)

        cand = _require_non_bool_int(entry["candidate_count"], f"{prefix}.candidate_count")
        staged_count = _require_non_bool_int(
            entry["staged_event_count"], f"{prefix}.staged_event_count"
        )
        candidate_sum += cand
        staged_sum += staged_count

    if len(lineage) != metrics["input_file_count"]:
        raise AdapterMetricsError(
            "source_lineage length must equal input_file_count "
            f"({len(lineage)} != {metrics['input_file_count']})"
        )
    if lineage_staged != set(normalized_staged):
        raise AdapterMetricsError(
            "source_lineage staged_file set must equal staged_files set"
        )
    if candidate_sum != metrics["candidate_total_sections"]:
        raise AdapterMetricsError(
            "sum of source_lineage candidate_count must equal candidate_total_sections "
            f"({candidate_sum} != {metrics['candidate_total_sections']})"
        )
    if staged_sum != metrics["staged_event_count"]:
        raise AdapterMetricsError(
            "sum of source_lineage staged_event_count must equal staged_event_count "
            f"({staged_sum} != {metrics['staged_event_count']})"
        )

    return metrics


def load_enrich_validate_prepare_metrics(
    metrics_path: Path,
    *,
    topic: str,
    require_lineage: bool,
) -> dict[str, Any]:
    """Load adapter metrics, enrich topic, validate, then rewrite once on success."""
    if not metrics_path.is_file():
        raise AdapterMetricsError(f"prepare metrics file not found: {metrics_path}")
    try:
        raw = json.loads(metrics_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AdapterMetricsError(f"prepare metrics JSON is invalid: {exc}") from exc
    if not isinstance(raw, dict):
        raise AdapterMetricsError(
            f"prepare metrics root must be a JSON object, got {type(raw).__name__}"
        )

    enriched = dict(raw)
    enriched["topic"] = topic
    validated = validate_prepare_metrics(enriched, require_lineage=require_lineage)
    metrics_path.write_text(
        json.dumps(validated, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return validated


# ---------------------------------------------------------------------------
# Phase 16 event lineage + correlation
# ---------------------------------------------------------------------------


def compute_source_event_id(
    topic: str, record: dict[str, Any], *, markdown_mode: str = LEGACY_MODE,
) -> tuple[str, str]:
    """Build ``source_event:<topic>:<sha256>`` from locator identity fields."""
    kind = record["locator_kind"]
    source_file = str(record["source_file"])
    ordinal = str(record["candidate_ordinal"])
    if kind == "markdown_section":
        parts = [
            "source-event-structural-v1" if markdown_mode == STRUCTURAL_MODE else "source-event-v1",
            source_file,
            "markdown_section",
            ordinal,
            str(record["heading_level"]),
            str(record["original_heading_text"]),
        ]
    elif kind == "commit_heading":
        parts = [
            "source-event-v1",
            source_file,
            "commit_heading",
            ordinal,
            str(record["commit_sha"]),
            str(record["original_heading_text"]),
        ]
    else:
        raise ProvenanceError(f"unsupported locator_kind: {kind!r}")
    canonical = "\0".join(parts)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"source_event:{topic}:{digest}", canonical


def compute_individual_report_event_id(
    topic: str,
    date: str,
    body_hash: str,
    *,
    markdown_mode: str = LEGACY_MODE,
) -> tuple[str, str]:
    """Build individual ReportEvent id from date + normalised body hash."""
    tag = "report-event-structural-v1" if markdown_mode == STRUCTURAL_MODE else "report-event-v1"
    canonical = "\0".join([tag, date, body_hash])
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"report_event:{topic}:{digest}", canonical


def resolve_event_lineage_path(
    metrics: dict[str, Any],
    metrics_path: Path,
    *,
    require_event_lineage: bool,
) -> Path | None:
    """Resolve ``event_lineage_file`` pointer relative to the metrics parent."""
    pointer = metrics.get("event_lineage_file")
    if pointer is None:
        if require_event_lineage:
            raise AdapterMetricsError(
                "event_lineage_file is required for registered adapters"
            )
        return None
    if not isinstance(pointer, str) or not pointer.strip():
        raise AdapterMetricsError("event_lineage_file must be a non-empty string")
    normalized = normalize_metrics_path(pointer, "event_lineage_file")
    if "/" in normalized:
        raise AdapterMetricsError(
            f"event_lineage_file must be a top-level filename, got {pointer!r}"
        )
    path = metrics_path.parent / normalized
    if not path.is_file():
        raise AdapterMetricsError(f"event_lineage_file not found: {path}")
    return path


def validate_and_finalize_event_lineage(
    metrics: dict[str, Any],
    metrics_path: Path,
    *,
    topic: str,
    run_id: str,
    require_event_lineage: bool,
    markdown_mode: str = LEGACY_MODE,
    heading_levels: tuple[int, ...] = (2,),
) -> dict[str, Any] | None:
    """Pre-pipeline gate: validate raw lineage, write event-lineage-v1 envelope."""
    lineage_path = resolve_event_lineage_path(
        metrics,
        metrics_path,
        require_event_lineage=require_event_lineage,
    )
    if lineage_path is None:
        return None

    try:
        raw = json.loads(lineage_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AdapterMetricsError(f"event_lineage JSON is invalid: {exc}") from exc
    if not isinstance(raw, dict):
        raise AdapterMetricsError(
            f"event_lineage root must be a JSON object, got {type(raw).__name__}"
        )
    structural = markdown_mode == STRUCTURAL_MODE
    if structural:
        from wordpipe.chronicle.markdown_sections import validate_parser_provenance

        if raw.get("$schema") != STRUCTURAL_RAW_SCHEMA or raw.get("markdown_mode") != STRUCTURAL_MODE:
            raise AdapterMetricsError("unsupported structural prepare lineage schema or mode")
        if not isinstance(raw.get("source_accounting"), list):
            raise AdapterMetricsError("structural lineage missing source accounting")
        try:
            provenance = validate_parser_provenance(raw.get("parser_provenance"), heading_levels)
        except ValueError as exc:
            raise AdapterMetricsError(str(exc)) from exc
        if metrics.get("parser_provenance") != provenance:
            raise AdapterMetricsError("structural prepare metrics and lineage disagree on parser provenance")
    elif "$schema" in raw or "markdown_mode" in raw:
        raise AdapterMetricsError("unsupported raw legacy lineage schema or mode")
    events = raw.get("events")
    if not isinstance(events, list):
        raise AdapterMetricsError("event_lineage.events must be a list")

    staged_files = {
        normalize_staged_filename(item, f"staged_files[{i}]")
        for i, item in enumerate(metrics.get("staged_files", []))
    }
    lineage_by_source = {
        normalize_metrics_path(item["source_file"], f"source_lineage[{i}].source_file"): item
        for i, item in enumerate(metrics.get("source_lineage") or [])
        if isinstance(item, dict) and "source_file" in item
    }

    finalized: list[dict[str, Any]] = []
    id_to_canonical: dict[str, str] = {}
    locator_keys: set[tuple[str, str, int]] = set()
    commit_sha_by_source: dict[str, set[str]] = {}
    emitted_by_staged: dict[str, int] = {}
    max_candidate_by_source: dict[str, int] = {}

    for index, entry in enumerate(events):
        prefix = f"event_lineage.events[{index}]"
        if not isinstance(entry, dict):
            raise AdapterMetricsError(f"{prefix} must be an object")

        for key in (
            "locator_kind",
            "source_file",
            "candidate_ordinal",
            "original_heading_text",
            "staged_file",
            "staged_event_ordinal",
            "date",
            "title",
        ):
            if key not in entry:
                raise AdapterMetricsError(f"{prefix} missing required field {key}")

        kind = entry["locator_kind"]
        if kind not in ("markdown_section", "commit_heading"):
            raise AdapterMetricsError(f"{prefix}.locator_kind unsupported: {kind!r}")

        source_file = normalize_metrics_path(entry["source_file"], f"{prefix}.source_file")
        staged_file = normalize_staged_filename(entry["staged_file"], f"{prefix}.staged_file")
        if staged_file not in staged_files:
            raise AdapterMetricsError(
                f"{prefix}.staged_file {staged_file!r} not in staged_files"
            )

        cand = _require_non_bool_int(entry["candidate_ordinal"], f"{prefix}.candidate_ordinal")
        staged_ord = _require_non_bool_int(
            entry["staged_event_ordinal"], f"{prefix}.staged_event_ordinal"
        )
        if cand < 1:
            raise AdapterMetricsError(f"{prefix}.candidate_ordinal must be >= 1")
        if staged_ord < 1:
            raise AdapterMetricsError(f"{prefix}.staged_event_ordinal must be >= 1")

        locator_key = (source_file, str(kind), cand)
        if locator_key in locator_keys:
            raise AdapterMetricsError(
                f"{prefix} duplicate locator identity for {locator_key}"
            )
        locator_keys.add(locator_key)

        record = dict(entry)
        record["source_file"] = source_file
        record["staged_file"] = staged_file
        record["candidate_ordinal"] = cand
        record["staged_event_ordinal"] = staged_ord
        record["original_heading_text"] = str(entry["original_heading_text"])
        record["date"] = str(entry["date"])
        record["title"] = str(entry["title"])

        if kind == "markdown_section":
            if "heading_level" not in entry:
                raise AdapterMetricsError(f"{prefix} missing required field heading_level")
            level = _require_non_bool_int(entry["heading_level"], f"{prefix}.heading_level")
            if level < 2 or level > 6:
                raise AdapterMetricsError(
                    f"{prefix}.heading_level must be 2-6, got {level}"
                )
            record["heading_level"] = level
        else:
            sha = entry.get("commit_sha")
            if not isinstance(sha, str) or not sha.strip():
                raise AdapterMetricsError(f"{prefix}.commit_sha must be a non-empty string")
            sha_norm = sha.strip().lower()
            if len(sha_norm) < 7 or not re.fullmatch(r"[0-9a-f]+", sha_norm):
                raise AdapterMetricsError(
                    f"{prefix}.commit_sha must be lowercase hex length >= 7, got {sha!r}"
                )
            seen = commit_sha_by_source.setdefault(source_file, set())
            if sha_norm in seen:
                raise AdapterMetricsError(
                    f"{prefix} duplicate commit_sha {sha_norm} in {source_file}"
                )
            seen.add(sha_norm)
            record["commit_sha"] = sha_norm

        if "start_line" in entry and entry["start_line"] is not None:
            record["start_line"] = _require_non_bool_int(
                entry["start_line"], f"{prefix}.start_line"
            )
        if "commit_timestamp" in entry and entry["commit_timestamp"] is not None:
            if not isinstance(entry["commit_timestamp"], str):
                raise AdapterMetricsError(
                    f"{prefix}.commit_timestamp must be a string when present"
                )
            record["commit_timestamp"] = entry["commit_timestamp"]

        if structural and kind != "markdown_section":
            raise AdapterMetricsError("structural lineage requires a Markdown section locator")
        source_event_id, canonical = compute_source_event_id(topic, record, markdown_mode=markdown_mode)
        if source_event_id in id_to_canonical and id_to_canonical[source_event_id] != canonical:
            raise AdapterMetricsError(
                "SHA-256 SourceEvent ID collision; refusing disambiguator. "
                f"id={source_event_id}; payloads=({id_to_canonical[source_event_id]!r}, {canonical!r})"
            )
        id_to_canonical[source_event_id] = canonical
        record["source_event_id"] = source_event_id
        record["body_sha256"] = None

        finalized.append(record)
        emitted_by_staged[staged_file] = emitted_by_staged.get(staged_file, 0) + 1
        max_candidate_by_source[source_file] = max(
            max_candidate_by_source.get(source_file, 0), cand
        )

    staged_expected = int(metrics.get("staged_event_count", -1))
    if len(finalized) != staged_expected:
        raise AdapterMetricsError(
            "event_lineage emitted count must equal staged_event_count "
            f"({len(finalized)} != {staged_expected})"
        )

    for staged_file, count in emitted_by_staged.items():
        file_lineage = next(
            (
                item for item in (metrics.get("source_lineage") or [])
                if isinstance(item, dict)
                and "staged_file" in item
                and normalize_staged_filename(
                    item["staged_file"], "source_lineage.staged_file"
                ) == staged_file
            ),
            None,
        )
        if file_lineage is None:
            raise AdapterMetricsError(
                f"event_lineage staged_file {staged_file!r} missing from source_lineage"
            )
        expected = int(file_lineage["staged_event_count"])
        if count != expected:
            raise AdapterMetricsError(
                f"event_lineage count for {staged_file} must equal "
                f"source_lineage staged_event_count ({count} != {expected})"
            )

    for source_file, max_cand in max_candidate_by_source.items():
        file_lineage = lineage_by_source.get(source_file)
        if file_lineage is None:
            raise AdapterMetricsError(
                f"event_lineage source_file {source_file!r} missing from source_lineage"
            )
        cand_count = int(file_lineage["candidate_count"])
        if max_cand > cand_count:
            raise AdapterMetricsError(
                f"candidate_ordinal {max_cand} exceeds candidate_count "
                f"{cand_count} for {source_file}"
            )

    # staged_event_ordinal must be dense 1..N within each staged file
    by_staged: dict[str, list[dict[str, Any]]] = {}
    for record in finalized:
        by_staged.setdefault(record["staged_file"], []).append(record)
    for staged_file, records in by_staged.items():
        ordinals = sorted(r["staged_event_ordinal"] for r in records)
        expected_ords = list(range(1, len(records) + 1))
        if ordinals != expected_ords:
            raise AdapterMetricsError(
                f"staged_event_ordinal must be dense 1..N for {staged_file}, "
                f"got {ordinals}"
            )

    envelope: dict[str, Any] = {
        "$schema": STRUCTURAL_LINEAGE_SCHEMA if structural else "event-lineage-v1",
        "topic": topic,
        "run_id": run_id,
        "events": finalized,
    }
    if structural:
        envelope.update(
            markdown_mode=markdown_mode, source_accounting=raw["source_accounting"],
            parser_provenance=provenance,
        )
    lineage_path.write_text(
        json.dumps(envelope, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return envelope


# Exact keep-both conflict note emitted by wordpipe.chronicle.merge (keep-both path).
KEEP_BOTH_CONFLICT_NOTE = "<!-- Duplicate date, different content -->"


def strip_keep_both_conflict_notes(body: str) -> str:
    """Preserve the topic runner's provenance failure classification."""
    try:
        from wordpipe.chronicle.merge import strip_keep_both_conflict_notes as strip_notes

        return strip_notes(body)
    except ValueError as exc:
        raise ProvenanceError(str(exc)) from exc


def _sorted_key_records(keys: set[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"date": date, "body_sha256": body_hash}
        for date, body_hash in sorted(keys, key=lambda item: (item[0], item[1]))
    ]


def correlate_event_provenance(
    run_dir: Path,
    lineage_doc: dict[str, Any],
    *,
    topic: str,
    run_id: str,
    markdown_mode: str = LEGACY_MODE,
    heading_levels: tuple[int, ...] = (2,),
) -> dict[str, Any]:
    """Post-pipeline gate: fingerprint normalised events and verify merged survivors."""
    from wordpipe.chronicle.merge import (
        compute_body_hash,
        extract_events,
        parse_yaml_frontmatter,
    )

    structural = markdown_mode == STRUCTURAL_MODE
    expected_schema = STRUCTURAL_LINEAGE_SCHEMA if structural else "event-lineage-v1"
    if lineage_doc.get("$schema") != expected_schema or lineage_doc.get("markdown_mode", LEGACY_MODE) != markdown_mode:
        raise ProvenanceError("unsupported event lineage schema or mode")
    if structural:
        from wordpipe.chronicle.markdown_sections import validate_parser_provenance

        try:
            provenance = validate_parser_provenance(lineage_doc.get("parser_provenance"), heading_levels)
        except ValueError as exc:
            raise ProvenanceError(str(exc)) from exc
    events = lineage_doc.get("events")
    if not isinstance(events, list):
        raise ProvenanceError("finalized event_lineage.events must be a list")

    by_staged: dict[str, list[dict[str, Any]]] = {}
    for record in events:
        if not isinstance(record, dict):
            raise ProvenanceError("event_lineage event records must be objects")
        staged_file = str(record["staged_file"])
        by_staged.setdefault(staged_file, []).append(record)

    for staged_file, records in by_staged.items():
        records.sort(key=lambda item: int(item["staged_event_ordinal"]))

    report_map: dict[str, dict[str, Any]] = {}
    report_canonical: dict[str, str] = {}
    correlated_keys: list[tuple[str, str]] = []
    ambiguous_matches: list[dict[str, Any]] = []
    normalised_dir = run_dir / "pipeline" / "normalised"

    for staged_file, records in by_staged.items():
        path = normalised_dir / Path(staged_file).name
        if not path.is_file():
            raise ProvenanceError(f"normalised file missing for {staged_file}: {path}")
        text = path.read_text(encoding="utf-8")
        _meta, body = parse_yaml_frontmatter(text)
        norm_events = extract_events(body)
        if len(norm_events) != len(records):
            raise ProvenanceError(
                f"normalised parity failed for {staged_file}: "
                f"{len(norm_events)} normalised vs {len(records)} lineage"
            )
        for record, nev in zip(records, norm_events, strict=True):
            body_hash = compute_body_hash(nev["body"])
            date = nev["date"]
            report_event_id, rcanonical = compute_individual_report_event_id(
                topic, date, body_hash, markdown_mode=markdown_mode,
            )
            if (
                report_event_id in report_canonical
                and report_canonical[report_event_id] != rcanonical
            ):
                raise ProvenanceError(
                    "SHA-256 ReportEvent ID collision; refusing disambiguator. "
                    f"id={report_event_id}; payloads=("
                    f"{report_canonical[report_event_id]!r}, {rcanonical!r})"
                )
            report_canonical[report_event_id] = rcanonical
            source_event_id = str(record["source_event_id"])
            entry = report_map.setdefault(
                report_event_id,
                {
                    "report_event_id": report_event_id,
                    "date": date,
                    "body_sha256": body_hash,
                    "source_event_ids": [],
                },
            )
            if entry["date"] != date or entry["body_sha256"] != body_hash:
                ambiguous_matches.append({
                    "reason": "report_event_id_payload_mismatch",
                    "report_event_id": report_event_id,
                    "source_event_id": source_event_id,
                })
            entry["source_event_ids"].append(source_event_id)
            correlated_keys.append((date, body_hash))
            record["body_sha256"] = body_hash
            record["report_event_id"] = report_event_id

    expected_keys = set(correlated_keys)

    merged_path = run_dir / "pipeline" / "merged.md"
    if not merged_path.is_file():
        raise ProvenanceError(f"merged.md missing: {merged_path}")
    merged_text = merged_path.read_text(encoding="utf-8")
    raw_heading_count = len(re.findall(r"(?m)^## Event:", merged_text))
    _merged_meta, merged_body = parse_yaml_frontmatter(merged_text)
    cleaned_body = strip_keep_both_conflict_notes(merged_body)
    actual_events = extract_events(cleaned_body)
    actual_key_list = [
        (ev["date"], compute_body_hash(ev["body"])) for ev in actual_events
    ]
    actual_keys = set(actual_key_list)
    if len(actual_key_list) != len(actual_keys):
        raise ProvenanceError(
            "duplicate survivor keys in merged output after merge-note-aware parse "
            f"(events={len(actual_key_list)}, unique={len(actual_keys)})"
        )

    missing_keys = expected_keys - actual_keys
    unexpected_keys = actual_keys - expected_keys
    unmerged = sum(1 for key in correlated_keys if key not in actual_keys)

    survivor_verification: dict[str, Any] = {
        "method": "merged-note-aware-v1",
        "expected_key_count": len(expected_keys),
        "actual_key_count": len(actual_keys),
        "missing_key_count": len(missing_keys),
        "unexpected_key_count": len(unexpected_keys),
        "missing_keys": _sorted_key_records(missing_keys),
        "unexpected_keys": _sorted_key_records(unexpected_keys),
        "raw_heading_count": raw_heading_count,
        "parsed_event_count": len(actual_events),
    }

    if missing_keys or unexpected_keys:
        raise ProvenanceError(
            "merged survivor key set mismatch: "
            f"missing={len(missing_keys)} unexpected={len(unexpected_keys)}"
        )
    if unmerged != 0:
        raise ProvenanceError(
            "unmerged_source_event_count must be 0 under keep-both "
            f"(got {unmerged})"
        )
    if ambiguous_matches:
        raise ProvenanceError(
            f"ambiguous_matches is non-empty ({len(ambiguous_matches)})"
        )

    if structural:
        attach_verified_navigation(run_dir, events, report_map, markdown_mode=markdown_mode)

    # Rewrite lineage with post-pipeline fingerprints (still event-lineage-v1).
    lineage_out = {
        "$schema": expected_schema,
        "topic": topic,
        "run_id": run_id,
        "events": events,
    }
    if structural:
        lineage_out.update(
            markdown_mode=markdown_mode, source_accounting=lineage_doc["source_accounting"],
            parser_provenance=provenance,
        )
    (run_dir / "event_lineage.json").write_text(
        json.dumps(lineage_out, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    correlation: dict[str, Any] = {
        "$schema": STRUCTURAL_CORRELATION_SCHEMA if structural else "event-correlation-v1",
        "topic": topic,
        "run_id": run_id,
        "source_event_count": len(events),
        "report_event_count": len(report_map),
        "unmerged_source_event_count": unmerged,
        "ambiguous_matches": ambiguous_matches,
        "survivor_verification": survivor_verification,
        "report_events": list(report_map.values()),
    }
    if structural:
        correlation["markdown_mode"] = markdown_mode
        correlation["parser_provenance"] = provenance
    (run_dir / "event_correlation.json").write_text(
        json.dumps(correlation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return correlation


def attach_verified_navigation(
    run_dir: Path, events: list[dict[str, Any]], reports: dict[str, dict[str, Any]],
    *, markdown_mode: str,
) -> None:
    from collections import Counter
    from wordpipe.chronicle.index import SURVIVOR_FRAGMENT_RE, rendered_navigation

    appendix = run_dir / "pipeline" / "appendix"
    targets = {
        "../chronicle_tagged.md": appendix.parent / "chronicle_tagged.md",
        "chronicle_tagged_anchored.md": appendix / "chronicle_tagged_anchored.md",
    }
    try:
        _, links = rendered_navigation((appendix / "event_index.md").read_text(encoding="utf-8"))
        counts = {}
        artifacts = {}
        expected = {f"event-{report['date']}-{report['body_sha256']}" for report in reports.values()}
        for href, _ in links:
            path, _, fragment = href.partition("#")
            if not SURVIVOR_FRAGMENT_RE.fullmatch(fragment):
                continue
            if path not in targets or fragment in artifacts:
                raise ProvenanceError(f"structural navigation has an invalid or duplicate target: {href}")
            target = targets[path].resolve()
            if not target.is_relative_to(run_dir.resolve()):
                raise ProvenanceError(f"structural navigation escapes its run: {href}")
            if path not in counts:
                counts[path] = Counter(rendered_navigation(target.read_text(encoding="utf-8"))[0])
            if counts[path][fragment] != 1:
                raise ProvenanceError(f"structural navigation has an invalid target: {href}")
            artifacts[fragment] = target.relative_to(run_dir.resolve()).as_posix()
    except (OSError, ValueError) as exc:
        raise ProvenanceError(f"structural navigation could not be read: {exc}") from exc
    if artifacts.keys() != expected:
        raise ProvenanceError("structural event index disagrees with the survivor set")
    for report in reports.values():
        fragment = f"event-{report['date']}-{report['body_sha256']}"
        report["survivor_key"] = [report["date"], report["body_sha256"]]
        report["navigation"] = {
            "markdown_mode": markdown_mode,
            "run_id": run_dir.name,
            "artifact": artifacts[fragment],
            "fragment": fragment,
        }
    for event in events:
        report = reports[event["report_event_id"]]
        event["survivor_key"] = report["survivor_key"]
        event["navigation"] = report["navigation"]


def append_event_provenance_summary(
    run_dir: Path,
    correlation: dict[str, Any],
) -> None:
    """Append runner-owned Event Provenance section to RUN_SUMMARY.md."""
    summary_path = run_dir / "RUN_SUMMARY.md"
    if not summary_path.is_file():
        return
    ambiguous = correlation.get("ambiguous_matches") or []
    survivor = correlation.get("survivor_verification") or {}
    method = survivor.get("method", "n/a")
    section = "\n".join([
        "## Event Provenance",
        "",
        f"- Schema: `{correlation.get('$schema', 'event-correlation-v1')}`",
        f"- Survivor verification: `{method}`",
        f"- Source events: {correlation.get('source_event_count', 0)}",
        f"- Report events (individual ids in sidecar): {correlation.get('report_event_count', 0)}",
        f"- Unmerged source events: {correlation.get('unmerged_source_event_count', 0)}",
        f"- Ambiguous matches: {len(ambiguous)}",
        "- Artifacts: `event_lineage.json`, `event_correlation.json`",
        "",
    ])
    existing = summary_path.read_text(encoding="utf-8").rstrip() + "\n\n"
    summary_path.write_text(existing + section, encoding="utf-8")


def _as_number(value: Any, *, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def find_previous_run(
    base_dir: Path, current_run_id: str, *, markdown_mode: str = LEGACY_MODE,
) -> Path | None:
    """Return the most recent prior completed run under *base_dir*."""
    if not base_dir.is_dir():
        return None

    candidates: list[Path] = []
    current_path = (base_dir / current_run_id).resolve()
    for child in base_dir.iterdir():
        if not child.is_dir():
            continue
        if child.resolve() == current_path:
            continue
        if markdown_mode == STRUCTURAL_MODE:
            try:
                prior = json.loads((child / "topic_run_manifest.json").read_text(encoding="utf-8"))
                if prior["adapter"].get("markdown_mode") != markdown_mode or any(prior["exit_codes"].values()):
                    continue
            except (OSError, ValueError, KeyError, AttributeError):
                continue
        if not (child / "run_metrics.json").is_file():
            continue
        execution_dir = child / "exec-01"
        try:
            terminal = json.loads((execution_dir / "summarize.json").read_text(encoding="utf-8"))
            if terminal.get("schema") != "exec-01-v1" or terminal.get("outcome") not in _SUMMARY_REPORTABLE_OUTCOMES:
                continue
        except FileNotFoundError:
            if (execution_dir / "prepare.json").is_file():
                continue  # This run has not recorded a summarization result.
            # Historical runs may predate the execution sidecar.
        except (OSError, ValueError, AttributeError):
            continue
        candidates.append(child)

    if not candidates:
        return None
    return max(candidates, key=lambda p: ((p / "run_metrics.json").stat().st_mtime, p.name))


def write_trend_reports(
    run_dir: Path,
    current_metrics: dict[str, Any],
    previous_run_dir: Path | None,
) -> dict[str, Any]:
    """Write JSON and Markdown trend reports for the current run."""
    previous_metrics: dict[str, Any] = {}
    previous_run_id: str | None = None
    if previous_run_dir is not None:
        previous_path = previous_run_dir / "run_metrics.json"
        if previous_path.is_file():
            previous_metrics = json.loads(previous_path.read_text(encoding="utf-8"))
            previous_run_id = previous_run_dir.name

    comparisons: list[dict[str, Any]] = []
    for metric in TREND_METRICS:
        current_value = _as_number(current_metrics.get(metric), default=0.0)
        previous_value = _as_number(previous_metrics.get(metric), default=0.0)
        comparisons.append({
            "metric": metric,
            "current": current_value,
            "previous": previous_value if previous_run_id else None,
            "delta": current_value - previous_value if previous_run_id else None,
        })

    trend: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_dir.name,
        "previous_run_id": previous_run_id,
        "previous_run_path": str(Path("..") / previous_run_id) if previous_run_id else None,
        "status": "COMPARED" if previous_run_id else "NO_PREVIOUS_RUN",
        "comparisons": comparisons,
    }
    (run_dir / "trend_report.json").write_text(
        json.dumps(trend, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Trend Report",
        "",
        f"- Current run: `{run_dir.name}`",
        f"- Previous run: `{previous_run_id or 'none'}`",
        f"- Status: `{trend['status']}`",
        "",
        "| Metric | Previous | Current | Delta |",
        "| --- | ---: | ---: | ---: |",
    ]
    for item in comparisons:
        previous = "" if item["previous"] is None else _format_metric(item["previous"])
        delta = "" if item["delta"] is None else _format_metric(item["delta"], signed=True)
        lines.append(
            f"| `{item['metric']}` | {previous} | {_format_metric(item['current'])} | {delta} |"
        )
    (run_dir / "trend_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return trend


def _format_metric(value: Any, *, signed: bool = False) -> str:
    if not isinstance(value, (int, float)):
        return str(value)
    if float(value).is_integer():
        return f"{value:+.0f}" if signed else f"{value:.0f}"
    return f"{value:+.2f}" if signed else f"{value:.2f}"


def write_source_attribution(
    run_dir: Path,
    run_metrics: dict[str, Any],
    *,
    source_lineage: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Write source attribution from staged files to normalised event counts.

    When *source_lineage* is provided (validated prepare metrics), prefer it for
    raw source paths and staged event counts. Without lineage, preserve the
    legacy filename-reconstruction entry shape.
    """
    staged_files = run_metrics.get("staged_files", [])
    if not isinstance(staged_files, list):
        staged_files = []

    lineage_by_staged: dict[str, dict[str, Any]] = {}
    if source_lineage:
        for item in source_lineage:
            if not isinstance(item, dict):
                continue
            try:
                key = normalize_metrics_path(item.get("staged_file"), "staged_file")
            except AdapterMetricsError:
                continue
            lineage_by_staged[key] = item

    entries: list[dict[str, Any]] = []
    total_events = 0
    for staged_name in staged_files:
        staged_filename = str(staged_name)
        try:
            staged_key = normalize_metrics_path(staged_filename, "staged_filename")
        except AdapterMetricsError:
            staged_key = staged_filename.replace("\\", "/")

        basename = Path(staged_key).name
        normalised_path = run_dir / "pipeline" / "normalised" / basename
        count = _normalised_event_count(normalised_path)
        total_events += count

        entry: dict[str, Any] = {
            "staged_source_file": str(Path("staged_input") / basename),
            "normalised_file": str(Path("pipeline") / "normalised" / basename),
            "staged_filename": basename,
            "normalised_filename": basename,
            "contributed_event_count": count,
        }

        lineage_item = lineage_by_staged.get(staged_key)
        if lineage_item is not None:
            staged_event_count = int(lineage_item.get("staged_event_count", 0))
            entry["source_file"] = str(lineage_item.get("source_file", ""))
            entry["staged_event_count"] = staged_event_count
            entry["count_mismatch"] = staged_event_count != count

        entries.append(entry)

    attribution: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_dir.name,
        "source_count": len(entries),
        "total_contributed_event_count": total_events,
        "sources": entries,
    }
    (run_dir / "source_attribution.json").write_text(
        json.dumps(attribution, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return attribution


def _normalised_event_count(path: Path) -> int:
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"(?m)^event_count:\s*(\d+)\s*$", text)
    if match:
        return int(match.group(1))
    return len(re.findall(r"(?m)^## Event:", text))


def check_markdown_output_root(manifest: dict[str, Any], *, claim: bool = False) -> None:
    base = Path(manifest["output"]["base_dir"]).resolve()
    structural = manifest["adapter"].get("markdown_mode") == STRUCTURAL_MODE
    if any((parent / STRUCTURAL_ROOT_MARKER).exists() for parent in base.parents):
        raise RunDirectoryCollisionError("output root is inside a structural-v1 output root")
    marker = base / STRUCTURAL_ROOT_MARKER
    if not structural:
        if marker.exists():
            raise RunDirectoryCollisionError("legacy mode cannot use a structural-v1 output root")
        return
    legacy_root = Path(manifest["output"]["legacy_base_dir"]).resolve()
    input_root = Path(manifest["input_dir"]).resolve()
    if any(base.is_relative_to(path) or path.is_relative_to(base) for path in (legacy_root, input_root)):
        raise RunDirectoryCollisionError("structural output overlaps the resolved legacy output or input root")
    if any((parent / "topic_run_manifest.json").exists() or (parent / "run.log").exists() for parent in base.parents):
        raise RunDirectoryCollisionError("structural output root is inside an existing topic run")
    if base.exists() and (
        not marker.is_file() or marker.is_symlink() or marker.read_text(encoding="utf-8") != STRUCTURAL_MODE
    ):
        raise RunDirectoryCollisionError("structural-v1 requires a new or previously claimed output root")
    if claim and not base.exists():
        try:
            base.mkdir(parents=True, exist_ok=False)
            with marker.open("x", encoding="utf-8") as handle:
                handle.write(STRUCTURAL_MODE)
        except FileExistsError as exc:
            raise RunDirectoryCollisionError(f"structural output root claimed concurrently: {base}") from exc


def run_report(
    manifest: dict[str, Any], *, dry_run: bool = False, run_id: str | None = None,
    stage_timeout: float | None = None,
) -> dict[str, Any]:
    """Execute the full topic report flow.

    Returns a result dict with keys: ``run_dir``, ``exit_codes``, ``run_metrics``, ``timing_seconds``.
    """
    repo_root = Path(manifest["_repo_root"])
    policy = ExecutionPolicy(timeout=stage_timeout, cancellation=Cancellation())
    base_dir = Path(manifest["output"]["base_dir"])
    markdown_mode = manifest["adapter"].get("markdown_mode", LEGACY_MODE)
    heading_levels = tuple(manifest["adapter"].get("heading_levels", (2,)))
    check_markdown_output_root(manifest)

    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = validate_run_id(run_id)
    run_dir = base_dir / run_id

    if run_dir.exists():
        raise RunDirectoryCollisionError(
            f"run directory already exists; evidence is append-only: {run_dir}"
        )

    commands = build_commands(manifest, run_dir)

    if dry_run:
        print("\nResolved commands:")
        for stage, cmd in commands.items():
            print(f"\n  [{stage}]")
            print(f"    {' '.join(cmd)}")
        print(f"\nPlanned output directory: {run_dir}")
        return {"run_dir": str(run_dir), "exit_codes": {}, "run_metrics": {}, "timing_seconds": 0.0}

    check_markdown_output_root(manifest, claim=True)
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise RunDirectoryCollisionError(
            f"run directory already exists; evidence is append-only: {run_dir}"
        ) from exc
    check_markdown_output_root(manifest)
    print(f"Output directory: {run_dir}")

    # Stage 1: Prepare
    log_path = run_dir / "run.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("", encoding="utf-8")  # clear log
    execution_dir = run_dir / "exec-01"

    prep_result = run_stage(
        commands[CMD_PREPARE], "prepare: adapter prepare",
        dry_run=False, capture_output_to=str(log_path),
        policy=policy, evidence_path=execution_dir / "prepare.json",
    )
    exit_codes: dict[str, int] = {CMD_PREPARE: prep_result["exit_code"]}
    if prep_result["exit_code"] != 0:
        print("\n[FAIL] Prepare stage failed. Aborting.")
        _write_failure_ontology(manifest, run_dir, exit_codes)
        return {"run_dir": str(run_dir), "exit_codes": exit_codes, "run_metrics": {}, "timing_seconds": 0.0}

    # Selecting a registered adapter ID claims compliance with that adapter's
    # metrics contract, even when the manifest overrides adapter.script.
    require_lineage = manifest["adapter"]["id"] in ADAPTER_REGISTRY
    metrics_path = run_dir / "prepare_metrics.json"
    try:
        validated_prepare_metrics = load_enrich_validate_prepare_metrics(
            metrics_path,
            topic=manifest["topic"],
            require_lineage=require_lineage,
        )
    except AdapterMetricsError as exc:
        reason = str(exc)
        fail_msg = (
            "[FAIL] Adapter process exited 0, but prepare metrics contract "
            f"validation failed: {reason}"
        )
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(fail_msg + "\n")
        print(f"\n{fail_msg}")
        exit_codes[CMD_PREPARE] = 1
        _write_failure_ontology(manifest, run_dir, exit_codes)
        return {
            "run_dir": str(run_dir),
            "exit_codes": exit_codes,
            "run_metrics": {},
            "timing_seconds": 0.0,
        }

    event_lineage_doc: dict[str, Any] | None = None
    try:
        event_lineage_doc = validate_and_finalize_event_lineage(
            validated_prepare_metrics,
            metrics_path,
            topic=manifest["topic"],
            run_id=run_id,
            require_event_lineage=require_lineage,
            markdown_mode=markdown_mode,
            heading_levels=heading_levels,
        )
    except AdapterMetricsError as exc:
        reason = str(exc)
        fail_msg = (
            "[FAIL] Event lineage pre-pipeline contract validation failed: "
            f"{reason}"
        )
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(fail_msg + "\n")
        print(f"\n{fail_msg}")
        exit_codes[CMD_PREPARE] = 1
        _write_failure_ontology(manifest, run_dir, exit_codes)
        return {
            "run_dir": str(run_dir),
            "exit_codes": exit_codes,
            "run_metrics": {},
            "timing_seconds": 0.0,
        }

    # Stage 2: Pipeline (timed)
    t0 = time.perf_counter()
    pipe_result = run_stage(
        commands[CMD_PIPELINE], "pipeline: chain.ps1",
        dry_run=False, capture_output_to=str(log_path),
        policy=policy, evidence_path=execution_dir / "pipeline.json", publish_owner=True,
    )
    t1 = time.perf_counter()
    timing_seconds = t1 - t0
    exit_codes[CMD_PIPELINE] = pipe_result["exit_code"]

    # Write performance.txt in the format expected by the adapter's summarize.
    perf_path = run_dir / "performance.txt"
    perf_path.write_text(
        f"TotalSeconds : {timing_seconds}\n",
        encoding="utf-8",
    )

    if pipe_result["exit_code"] != 0:
        print("\n[FAIL] Pipeline stage failed. Aborting.")
        _write_failure_ontology(manifest, run_dir, exit_codes, timing_seconds)
        return {"run_dir": str(run_dir), "exit_codes": exit_codes, "run_metrics": {}, "timing_seconds": timing_seconds}

    correlation_doc: dict[str, Any] | None = None
    if event_lineage_doc is not None:
        try:
            correlation_doc = correlate_event_provenance(
                run_dir,
                event_lineage_doc,
                topic=manifest["topic"],
                run_id=run_id,
                markdown_mode=markdown_mode,
                heading_levels=heading_levels,
            )
        except ProvenanceError as exc:
            reason = str(exc)
            fail_msg = f"[FAIL] Event provenance correlation failed: {reason}"
            with log_path.open("a", encoding="utf-8") as fh:
                fh.write(fail_msg + "\n")
            print(f"\n{fail_msg}")
            exit_codes[CMD_PROVENANCE] = 1
            _write_failure_ontology(manifest, run_dir, exit_codes, timing_seconds)
            return {
                "run_dir": str(run_dir),
                "exit_codes": exit_codes,
                "run_metrics": {},
                "timing_seconds": timing_seconds,
            }
        exit_codes[CMD_PROVENANCE] = 0

    # Stage 3: Summarize
    summary_result = run_stage(
        commands[CMD_SUMMARIZE], "summarize: adapter summarize",
        dry_run=False, capture_output_to=str(log_path),
        policy=policy, evidence_path=execution_dir / "summarize.json",
    )
    exit_codes[CMD_SUMMARIZE] = summary_result["exit_code"]
    if summary_result["outcome"] not in _SUMMARY_REPORTABLE_OUTCOMES:
        print("\n[FAIL] Summarization did not complete. Aborting.")
        _write_failure_ontology(manifest, run_dir, exit_codes, timing_seconds)
        return {
            "run_dir": str(run_dir),
            "exit_codes": exit_codes,
            "run_metrics": {},
            "timing_seconds": timing_seconds,
        }

    # A completed summarizer may report metrics and still return a native nonzero.
    if correlation_doc is not None and summary_result["exit_code"] == 0:
        append_event_provenance_summary(run_dir, correlation_doc)

    # Load run_metrics.json produced by the adapter's summarize.
    run_metrics: dict[str, Any] = {}
    run_metrics_path = run_dir / "run_metrics.json"
    if run_metrics_path.is_file():
        run_metrics = json.loads(run_metrics_path.read_text(encoding="utf-8"))
    else:
        print(f"  [WARN] run_metrics.json not found at {run_metrics_path}")

    run_metrics = enrich_run_metrics(run_metrics, timing_seconds)
    run_metrics_path.write_text(
        json.dumps(run_metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    source_attribution = write_source_attribution(
        run_dir,
        run_metrics,
        source_lineage=validated_prepare_metrics.get("source_lineage"),
    )
    previous_run_dir = find_previous_run(base_dir, run_id, markdown_mode=markdown_mode)
    trend_report = write_trend_reports(run_dir, run_metrics, previous_run_dir)

    # Stage 4: Ontology outputs
    write_ontology_outputs(
        manifest,
        run_dir,
        run_metrics,
        exit_codes,
        timing_seconds,
        trend_report=trend_report,
        source_attribution=source_attribution,
    )

    print(f"\n[DONE] Topic report complete. Output in: {run_dir}")

    verdict = _compute_verdict(manifest, run_metrics, exit_codes)
    return {
        "run_dir": str(run_dir),
        "exit_codes": exit_codes,
        "run_metrics": run_metrics,
        "timing_seconds": timing_seconds,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Failure ontology (written when a stage fails before full metrics exist)
# ---------------------------------------------------------------------------


def _write_failure_ontology(
    manifest: dict[str, Any],
    run_dir: Path,
    exit_codes: dict[str, int],
    timing_seconds: float = 0.0,
) -> None:
    """Write ontology outputs for a failed run where full metrics are unavailable."""
    write_ontology_outputs(
        manifest, run_dir, {},
        exit_codes, timing_seconds,
    )


# ---------------------------------------------------------------------------
# Ontology output (13.5 subset)
# ---------------------------------------------------------------------------


def write_ontology_outputs(
    manifest: dict[str, Any],
    run_dir: Path,
    run_metrics: dict[str, Any],
    exit_codes: dict[str, int],
    timing_seconds: float,
    *,
    trend_report: dict[str, Any] | None = None,
    source_attribution: dict[str, Any] | None = None,
) -> None:
    """Emit ``topic_run_manifest.json`` and ``topic_run_ontology.json``."""
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    topic = manifest["topic"]
    run_id = run_dir.name
    repo_root = Path(manifest["_repo_root"])

    # --- Write both JSON output files FIRST so they exist on disk ---
    def _rel(p: str) -> str:
        try:
            return Path(p).resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            return p

    adapter_rel = dict(manifest["adapter"])
    adapter_rel["script"] = _rel(adapter_rel["script"])
    structural = adapter_rel.get("markdown_mode") == STRUCTURAL_MODE
    identity_run_id = f"{STRUCTURAL_MODE}:{run_id}" if structural else run_id

    run_manifest: dict[str, Any] = {
        "schema_version": manifest["schema_version"],
        "topic": topic,
        "run_id": run_id,
        "created_at": now_iso,
        "_repo_root": str(repo_root),
        "input_dir": _rel(manifest["input_dir"]),
        "adapter": adapter_rel,
        "themes_config": _rel(manifest["themes_config"]),
        "index_config": _rel(manifest["index_config"]),
        "output_base_dir": _rel(manifest["output"]["base_dir"]),
        "quality_gates": dict(manifest["quality_gates"]),
        "commands": build_commands(manifest, run_dir),
        "exit_codes": dict(exit_codes),
        "timing_seconds": timing_seconds,
        "input_dir_abs": manifest["input_dir"],
        "adapter_abs": dict(manifest["adapter"]),
        "themes_config_abs": manifest["themes_config"],
        "index_config_abs": manifest["index_config"],
        "output_base_dir_abs": manifest["output"]["base_dir"],
    }
    (run_dir / "topic_run_manifest.json").write_text(
        json.dumps(run_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    # Write a minimal ontology file now so the evidence-artifact loop sees it.
    (run_dir / "topic_run_ontology.json").write_text(
        json.dumps({"$schema": "topic-run-ontology-v1", "topic": topic, "run_id": run_id},
                   indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # --- Build ontology entities & relations ---
    entities: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []

    # Helper to add an entity and return its id.
    _topic_id = f"topic:{topic}"
    entities.append({"id": _topic_id, "type": "Topic", "name": topic, "properties": {}})

    _source_bundle_id = f"source_bundle:{topic}"
    entities.append({
        "id": _source_bundle_id,
        "type": "SourceBundle",
        "name": f"{topic} input",
        "properties": {"path": manifest["input_dir"]},
    })

    _adapter_id = f"adapter:{manifest['adapter']['id']}"
    entities.append({
        "id": _adapter_id,
        "type": "TopicAdapter",
        "name": manifest["adapter"]["id"],
        "properties": {"script": manifest["adapter"]["script"]},
    })

    _run_entity_id = f"run:{topic}:{identity_run_id}"
    run_properties: dict[str, Any] = {
        "run_id": run_id,
        "topic": topic,
        "started_at": now_iso,
        "timing_seconds": timing_seconds,
    }
    if trend_report and trend_report.get("previous_run_id"):
        run_properties["previous_run"] = trend_report["previous_run_id"]

    entities.append({
        "id": _run_entity_id,
        "type": "TopicRun",
        "name": f"{topic} {run_id}",
        "properties": run_properties,
    })

    # Staged sources from prepare_metrics.
    staged_files = run_metrics.get("staged_files", [])
    staged_entity_ids: list[str] = []
    for sf in staged_files:
        eid = f"staged_source:{topic}:{identity_run_id}:{sf}" if structural else f"staged_source:{topic}:{sf}"
        entities.append({
            "id": eid,
            "type": "StagedSource",
            "name": sf,
            "properties": {"filename": sf},
        })
        staged_entity_ids.append(eid)

    # ReportEvent aggregate.
    merged_count: int = run_metrics.get("merged_event_count", 0) or 0
    _event_id = f"report_event:{topic}:{identity_run_id}"
    entities.append({
        "id": _event_id,
        "type": "ReportEvent",
        "name": f"{topic} events ({run_id})",
        "properties": {"count": merged_count},
    })

    # Themes from the themes config file.
    theme_entity_ids: list[str] = []
    themes_path = Path(manifest["themes_config"])
    if themes_path.is_file():
        themes_data = json.loads(themes_path.read_text(encoding="utf-8"))
        theme_dict = themes_data.get("themes", {})
        for theme_name in theme_dict:
            tid = f"theme:{topic}:{theme_name}"
            entities.append({
                "id": tid,
                "type": "Theme",
                "name": theme_name,
                "properties": {},
            })
            theme_entity_ids.append(tid)
            # tagged_with: ReportEvent -> Theme
            relations.append({
                "source": _event_id,
                "relation": "tagged_with",
                "target": tid,
            })

    # Metrics from run_metrics.json.
    metric_properties = {k: v for k, v in run_metrics.items() if isinstance(v, (int, float, str))}
    if metric_properties:
        _metric_id = f"metric:{topic}:{identity_run_id}"
        entities.append({
            "id": _metric_id,
            "type": "Metric",
            "name": f"{topic} metrics ({run_id})",
            "properties": metric_properties,
        })
        relations.append({
            "source": _metric_id,
            "relation": "measures",
            "target": _run_entity_id,
        })

    # EvidenceArtifacts. Include the ontology itself even though it is rewritten
    # below; this makes the artifact contract explicit in the final ontology.
    evidence_ids: list[str] = []
    evidence_files = [*CORE_EVIDENCE_FILES, *OPTIONAL_EVIDENCE_FILES]
    seen_evidence: set[str] = set()
    for ef_name in evidence_files:
        if ef_name in seen_evidence:
            continue
        seen_evidence.add(ef_name)
        ef_path = run_dir / ef_name
        should_include = ef_path.is_file() or ef_name == "topic_run_ontology.json"
        if should_include:
            eid = f"evidence:{topic}:{identity_run_id}:{ef_name}"
            try:
                evidence_path = os.path.relpath(ef_path, repo_root)
            except ValueError:
                evidence_path = str(ef_path.resolve())
            entities.append({
                "id": eid,
                "type": "EvidenceArtifact",
                "name": ef_name,
                "properties": {"path": evidence_path},
            })
            evidence_ids.append(eid)

    if source_attribution:
        _metric_id = f"metric:{topic}:{identity_run_id}:source_attribution"
        entities.append({
            "id": _metric_id,
            "type": "Metric",
            "name": f"{topic} source attribution ({run_id})",
            "properties": {
                "source_count": source_attribution.get("source_count", 0),
                "total_contributed_event_count": source_attribution.get(
                    "total_contributed_event_count", 0
                ),
            },
        })
        relations.append({
            "source": _metric_id,
            "relation": "measures",
            "target": _run_entity_id,
        })

    # Verdict.
    verdict = _compute_verdict(manifest, run_metrics, exit_codes)
    _verdict_id = f"verdict:{topic}:{identity_run_id}"
    entities.append({
        "id": _verdict_id,
        "type": "Verdict",
        "name": f"{topic} run {run_id}",
        "properties": {"verdict": verdict},
    })

    # Relations.
    source_relation = {"source": _run_entity_id, "relation": "consumes", "target": _source_bundle_id}
    if source_relation not in relations:
        relations.append(source_relation)

    adapter_relation = {"source": _run_entity_id, "relation": "uses_adapter", "target": _adapter_id}
    if adapter_relation not in relations:
        relations.append(adapter_relation)

    for ev_id in evidence_ids:
        relations.append({"source": _run_entity_id, "relation": "produces", "target": ev_id})

    relations.append({"source": _run_entity_id, "relation": "contains", "target": _event_id})

    summary_relation = {"source": _verdict_id, "relation": "summarizes", "target": _run_entity_id}
    if summary_relation not in relations:
        relations.append(summary_relation)

    ontology: dict[str, Any] = {
        "$schema": "topic-run-ontology-v1",
        "topic": topic,
        "run_id": run_id,
        "generated_at": now_iso,
        "entities": entities,
        "relations": relations,
    }
    (run_dir / "topic_run_ontology.json").write_text(
        json.dumps(ontology, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _compute_verdict(
    manifest: dict[str, Any],
    run_metrics: dict[str, Any],
    exit_codes: dict[str, int],
) -> str:
    """Compute PASS / REVIEW / FAIL from quality gates and exit codes."""
    if any(code != 0 for code in exit_codes.values()):
        return "FAIL"

    gates = manifest["quality_gates"]
    extraction = run_metrics.get("extraction_coverage_percent", 0)
    if isinstance(extraction, str):
        extraction = float(extraction)
    if extraction < gates.get("min_extraction_coverage_percent", 95.0):
        return "REVIEW"

    tagged = run_metrics.get("events_with_theme_tags", 0)
    merged = run_metrics.get("merged_event_count", 1) or 1
    tag_pct = (tagged / merged) * 100 if merged else 0.0
    if tag_pct < gates.get("min_theme_tag_percent", 85.0):
        return "REVIEW"

    errors = run_metrics.get("error_count", 0)
    if errors > gates.get("max_error_count", 0):
        return "REVIEW"

    return "PASS"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", "-m",
        required=True,
        type=Path,
        help="Path to the topic manifest JSON file",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Print resolved commands but do not execute",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Explicit run ID (default: auto-generated timestamp)",
    )
    parser.add_argument(
        "--allow-review",
        action="store_true",
        help="Return exit code 0 even when verdict is REVIEW",
    )
    parser.add_argument("--stage-timeout-seconds", type=float, help="Optional deadline per stage")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest(args.manifest)
    except ManifestError as exc:
        print(f"Manifest error: {exc}", file=sys.stderr)
        return 1

    try:
        result = run_report(
            manifest,
            dry_run=args.dry_run,
            run_id=args.run_id,
            **({"stage_timeout": args.stage_timeout_seconds} if args.stage_timeout_seconds is not None else {}),
        )
    except (RunDirectoryCollisionError, ValueError, OSError) as exc:
        print(f"Run error: {exc}", file=sys.stderr)
        return 1

    if not args.dry_run:
        exit_codes = result.get("exit_codes", {})
        if any(code != 0 for code in exit_codes.values()):
            print(f"\nRun had failures. Exit codes: {exit_codes}", file=sys.stderr)
            return 1
        verdict = result.get("verdict", "PASS")
        if verdict == "REVIEW" and not args.allow_review:
            print(f"\nVerdict: REVIEW (use --allow-review to skip enforcement)", file=sys.stderr)
            return 2
        timing = result.get("timing_seconds", 0.0)
        print(f"Wall-clock time: {timing:.2f}s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
