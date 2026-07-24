"""Tests for ``pipeline_contracts.StageResult.finalize()``.

Verifies the strict/non-strict behaviour: under strict mode, warnings are
elevated to errors; under non-strict, warnings stay as warnings.
"""

from __future__ import annotations

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
