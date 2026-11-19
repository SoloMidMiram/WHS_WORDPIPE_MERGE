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


def test_real_git_checkout_and_linked_worktree(tmp_path):
    import subprocess
    repo = tmp_path / "ordinary"
    linked = tmp_path / "linked"
    def git(*args):
        subprocess.run(["git", *map(str, args)], check=True, capture_output=True)
    git("init", repo)
    git("-C", repo, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-m", "initial")
    assert checker.find_violations(repo) == []
    git("-C", repo, "worktree", "add", "--detach", linked)
    assert (linked / ".git").is_file()
    assert checker.find_violations(linked) == []
    (linked / "unexpected.txt").write_text("not allowed")
    assert checker.find_violations(linked) == ["unexpected.txt"]
    (linked / ".git").unlink()
    (linked / ".git").write_text("gitdir: missing\n")
    assert checker.find_violations(linked) == [".git", "unexpected.txt"]


def test_malformed_git_pointer_is_not_exempt(tmp_path):
    for text in ["", "arbitrary", "gitdir: missing", "gitdir: .\nextra", "gitdir: ."]:
        (tmp_path / ".git").write_text(text)
        assert checker.find_violations(tmp_path) == [".git"]
