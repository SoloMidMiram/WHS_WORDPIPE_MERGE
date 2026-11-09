"""Tests for the repository-root organization policy."""

from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "check_root_layout.py"
SPEC = importlib.util.spec_from_file_location("check_root_layout", MODULE_PATH)
checker = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(checker)


def test_current_repository_root_matches_allowlist():
    assert checker.find_violations(MODULE_PATH.parents[1]) == []


def test_unknown_root_artifact_is_reported(tmp_path):
    (tmp_path / "unexpected-output.docx").write_bytes(b"test")
    assert checker.find_violations(tmp_path) == ["unexpected-output.docx"]


def test_generated_cache_exemptions_are_explicit(tmp_path):
    cache = tmp_path / ".ruff_cache"
    cache.mkdir()
    (cache / "entry").write_bytes(b"cache")
    assert checker.find_violations(tmp_path) == []
    (tmp_path / ".gitignore").write_text("unexpected-cache/\n")
    (tmp_path / "unexpected-cache").mkdir()
    assert checker.find_violations(tmp_path) == ["unexpected-cache/"]
