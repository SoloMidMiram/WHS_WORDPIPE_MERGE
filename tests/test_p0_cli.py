"""Tests for P0.1 (orchestration --strict), P0.5 (CLI exit code), P0.6 (path guard).

Tests are organised into three classes mirroring the three P0 findings:

1. ``TestOrchestrateDryRun`` — verifies the orchestration command builder includes
   ``--strict`` for ``verify_integrity.py``.
2. ``TestCliExitCode`` — verifies ``wordpipe`` exits 0 on success and non-zero
   on pipeline errors.
3. ``TestCliInOutGuard`` — verifies the ``--in``/``--out`` resolved-path guard
   rejects identical paths (absolute, relative-vs-absolute, case-insensitive)
   and accepts distinct paths.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from wordpipe.core.datatypes import RunReport


# ==============================================================================
# P0.1 — Orchestration command includes --strict
# ==============================================================================


class TestOrchestrateDryRun:
    """Verify ``tools/orchestrate.py --dry-run`` prints ``--strict`` for
    ``verify_integrity.py``."""

    def test_dry_run_includes_verify_strict(self) -> None:
        """Run subprocess on tools/orchestrate.py --dry-run; verify output
        includes --strict for verify_integrity.py."""
        result = subprocess.run(
            [sys.executable, "tools/orchestrate.py", "--dry-run"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Find the verify_integrity line and check for --strict
        lines = result.stdout.strip().splitlines()
        verify_lines = [ln for ln in lines if "verify_integrity" in ln]
        assert len(verify_lines) >= 1, (
            f"No verify_integrity command found in dry-run output: {lines}"
        )
        for vl in verify_lines:
            assert "--strict" in vl, (
                f"verify_integrity command missing --strict: {vl}"
            )


# ==============================================================================
# P0.5 — CLI exit code reflects RunReport.errors
# ==============================================================================


class TestCliExitCode:
    """Verify the ``wordpipe`` CLI exits 0 on success and 1 when pipeline errors
    are present."""

    def test_success_exits_0(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Process with OK deps returns 0."""
        in_file = tmp_path / "in.docx"
        out_file = tmp_path / "out.docx"
        in_file.write_text("fake docx content", encoding="utf-8")

        def _fake_process(cfg, logger=None, jsonl_path=None):
            return RunReport(out_path=cfg.out_path, notes=[], errors=[])

        # main.py does `from wordpipe.orchestrator import process_docx_v3`,
        # so we must patch the reference already bound in wordpipe.cli.main.
        import wordpipe.cli.main as cli_main

        monkeypatch.setattr(cli_main, "process_docx_v3", _fake_process)

        exit_code = cli_main.main(["--in", str(in_file), "--out", str(out_file)])
        assert exit_code == 0

    def test_error_exits_nonzero(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Process with failing pipeline returns 1."""
        in_file = tmp_path / "in.docx"
        out_file = tmp_path / "out.docx"
        in_file.write_text("fake docx content", encoding="utf-8")

        def _fake_process(cfg, logger=None, jsonl_path=None):
            return RunReport(
                out_path=cfg.out_path, notes=[], errors=["flatten failed"]
            )

        import wordpipe.cli.main as cli_main

        monkeypatch.setattr(cli_main, "process_docx_v3", _fake_process)

        exit_code = cli_main.main(["--in", str(in_file), "--out", str(out_file)])
        assert exit_code == 1


# ==============================================================================
# P0.6 — --in / --out guard
# ==============================================================================


class TestCliInOutGuard:
    """Verify the CLI rejects identical input and output paths before
    mutating any files."""

    def test_same_path_rejected(self, tmp_path: Path) -> None:
        """Same resolved path fails with SystemExit(2) from parser.error()."""
        from wordpipe.cli.main import main

        same = tmp_path / "doc.docx"
        same.write_text("fake", encoding="utf-8")

        with pytest.raises(SystemExit) as exc_info:
            main(["--in", str(same), "--out", str(same)])
        assert exc_info.value.code == 2, (
            f"Expected exit 2 from parser.error, got {exc_info.value.code}"
        )

    def test_relative_vs_absolute_same_file(self, monkeypatch, tmp_path: Path) -> None:
        """Relative and absolute paths pointing to the same file fail."""
        from wordpipe.cli.main import main

        doc = tmp_path / "doc.docx"
        doc.write_text("fake", encoding="utf-8")

        # Change cwd to tmp_path so the relative path resolves inside tmp_path.
        monkeypatch.chdir(tmp_path)

        abs_path = str(doc.resolve())
        rel_path = "doc.docx"
        with pytest.raises(SystemExit) as exc_info:
            main(["--in", abs_path, "--out", rel_path])
        assert exc_info.value.code == 2

    @pytest.mark.skipif(
        not sys.platform.startswith("win"),
        reason="case-insensitive filesystem test is Windows-specific",
    )
    def test_case_insensitive_same_file(self, tmp_path: Path) -> None:
        """Case-varied paths resolving to the same file fail on Windows."""
        from wordpipe.cli.main import main

        doc = tmp_path / "MyDoc.docx"
        doc.write_text("fake", encoding="utf-8")

        lower = str(doc.resolve())
        upper = str(doc.with_name("MYDOC.DOCX").resolve())
        with pytest.raises(SystemExit) as exc_info:
            main(["--in", lower, "--out", upper])
        assert exc_info.value.code == 2

    def test_distinct_paths_accepted(self, monkeypatch, tmp_path: Path) -> None:
        """Different files pass."""
        import wordpipe.cli.main as cli_main

        in_file = tmp_path / "in.docx"
        out_file = tmp_path / "out.docx"
        in_file.write_text("fake", encoding="utf-8")
        out_file.write_text("fake", encoding="utf-8")

        # Patch the pipeline call to avoid real processing.
        def _fake_process(cfg, logger=None, jsonl_path=None):
            return RunReport(out_path=cfg.out_path, notes=[], errors=[])

        monkeypatch.setattr(cli_main, "process_docx_v3", _fake_process)

        exit_code = cli_main.main(["--in", str(in_file), "--out", str(out_file)])
        # Guard passed — exit_code should be 0 (success).
        assert exit_code == 0, f"Expected 0, got {exit_code}"
