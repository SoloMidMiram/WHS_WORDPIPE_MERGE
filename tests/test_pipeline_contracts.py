"""Tests for ``pipeline_contracts.StageResult.finalize()``.

Verifies the strict/non-strict behaviour: under strict mode, warnings are
elevated to errors; under non-strict, warnings stay as warnings.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from tools.pipeline_contracts import StageResult, StagePaths


class TestStageResultFinalize:
    """Coverage for the ``finalize(strict=...)`` contract."""

    def test_finalize_strict_warning_becomes_error(self) -> None:
        """StageResult with warnings, ``finalize(strict=True)`` → status == "error"."""
        result = StageResult(
            stage="test",
            paths=StagePaths(workspace_root="/tmp"),
            warnings=["integrity check failed"],
        )
        result.finalize(strict=True)
        assert result.status == "error"
        assert any("STRICT_WARNINGS" in err.code for err in result.errors)

    def test_finalize_nonstrict_warning_stays_warning(self) -> None:
        """StageResult with warnings, ``finalize(strict=False)`` → status == "warning"."""
        result = StageResult(
            stage="test",
            paths=StagePaths(workspace_root="/tmp"),
            warnings=["minor warning"],
        )
        result.finalize(strict=False)
        assert result.status == "warning"
        # No errors should have been added
        assert len(result.errors) == 0

    def test_finalize_strict_no_warnings_success(self) -> None:
        """StageResult with no warnings/errors, ``finalize(strict=True)`` → status == "success"."""
        result = StageResult(
            stage="test",
            paths=StagePaths(workspace_root="/tmp"),
        )
        result.finalize(strict=True)
        assert result.status == "success"
        assert len(result.errors) == 0

    def test_finalize_strict_with_real_errors(self) -> None:
        """StageResult with real errors under strict → status == "error" with original error."""
        result = StageResult(
            stage="test",
            paths=StagePaths(workspace_root="/tmp"),
        )
        result.add_error("MISSING_FILE", "required file not found")
        result.warnings.append("some warning")
        result.finalize(strict=True)
        assert result.status == "error"
        codes = [err.code for err in result.errors]
        assert "MISSING_FILE" in codes
        # STRICT_WARNINGS should not be added when real errors already exist
        assert "STRICT_WARNINGS" not in codes, (
            "STRICT_WARNINGS should not be added when real errors exist"
        )


def test_verify_integrity_help_retains_strict_flag() -> None:
    """The documented ``--strict`` CLI selector remains accepted."""
    completed = subprocess.run(
        [sys.executable, "tools/verify_integrity.py", "--strict", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "--strict" in completed.stdout
    assert "--diagnostic-only" in completed.stdout
    assert "--portable" in completed.stdout


def test_rel_to_workspace() -> None:
    tools_dir = str(Path(__file__).resolve().parents[1] / "tools")
    sys.path.insert(0, tools_dir)
    try:
        import verify_integrity as verify
    finally:
        sys.path.pop(0)

    ws = os.path.abspath(".")
    rel = verify.rel_to_workspace(os.path.join(ws, "sub", "file.txt"), ws)
    assert rel == "sub/file.txt"
    assert verify.rel_to_workspace("", ws) == ""
    outside = os.path.abspath(os.path.join(ws, "..", "outside.txt"))
    assert verify.rel_to_workspace(outside, ws) == outside


def test_apply_relocation_map_includes_portable_paths(tmp_path: Path) -> None:
    tools_dir = str(Path(__file__).resolve().parents[1] / "tools")
    sys.path.insert(0, tools_dir)
    try:
        import apply_legacy_reorg as apply_reorg
    finally:
        sys.path.pop(0)

    source = tmp_path / "snapshot" / "WordPipe" / "legacy" / "note.txt"
    source.parent.mkdir(parents=True)
    source.write_text("portable evidence\n", encoding="utf-8")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    plan = tmp_path / "plan.jsonl"
    plan_row = {
        "src_rel": "WordPipe/legacy/note.txt",
        "src_abs": str(source),
        "dst_rel": "wordpipe/legacy/note.txt",
        "sha256": digest,
        "size_bytes": source.stat().st_size,
        "stamp": "20260821T000000Z",
        "area": "wordpipe",
        "rule_hits": ["legacy"],
    }
    plan.write_text(json.dumps(plan_row) + "\n", encoding="utf-8")

    result = apply_reorg.run_stage(
        workspace_root=str(tmp_path),
        root="snapshot",
        plan="plan.jsonl",
        out_map="map.jsonl",
        log="apply.log",
        conflict_log="conflicts.log",
        preflight_mode="off",
        no_auto_normalize=True,
        strict=True,
    )

    assert result.status == "success"
    map_row = json.loads((tmp_path / "map.jsonl").read_text(encoding="utf-8"))
    assert map_row["src_rel"] == plan_row["src_rel"]
    assert map_row["dst_rel"] == plan_row["dst_rel"]
    assert map_row["conflict_path_rel"] is None


def test_portable_verify_ignores_absolute_path_drift(tmp_path: Path) -> None:
    tools_dir = str(Path(__file__).resolve().parents[1] / "tools")
    sys.path.insert(0, tools_dir)
    try:
        import verify_integrity as verify
    finally:
        sys.path.pop(0)

    content = b"same content\n"
    digest = hashlib.sha256(content).hexdigest()
    snapshot_file = tmp_path / "snapshot" / "source.txt"
    destination = tmp_path / "wordpipe" / "evidence.txt"
    snapshot_file.parent.mkdir(parents=True)
    destination.parent.mkdir(parents=True)
    snapshot_file.write_bytes(content)
    destination.write_bytes(content)

    manifest_row = {"rel_path": "source.txt", "sha256": digest}
    plan_row = {
        "src_rel": "source.txt",
        "src_abs": "/old-clone-a/snapshot/source.txt",
    }
    relocation_row = {
        "src_rel": "source.txt",
        "src_abs": "/old-clone-b/snapshot/source.txt",
        "dst_rel": "wordpipe/evidence.txt",
        "dst_abs": "/old-clone-b/wordpipe/evidence.txt",
        "sha256": digest,
        "status": "copied",
        "area": "wordpipe",
    }
    for name, row in (
        ("manifest.jsonl", manifest_row),
        ("plan.jsonl", plan_row),
        ("map.jsonl", relocation_row),
    ):
        (tmp_path / name).write_text(json.dumps(row) + "\n", encoding="utf-8")

    result = verify.run_stage(
        workspace_root=str(tmp_path),
        manifest="manifest.jsonl",
        plan="plan.jsonl",
        relocation="map.jsonl",
        snapshot_root="snapshot",
        strict=True,
        portable=True,
    )

    report = json.loads(
        (tmp_path / "_ARCHIVE" / "logs" / "verify_report.json").read_text(
            encoding="utf-8"
        )
    )
    consistency = json.loads(
        (tmp_path / "_ARCHIVE" / "logs" / "consistency_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert result.status == "success"
    assert report["integrity"]["failures"] == []
    assert consistency["ok"] is True
