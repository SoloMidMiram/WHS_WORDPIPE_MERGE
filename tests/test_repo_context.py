"""Verify bounded retrieval excludes untracked and restricted evidence."""
import importlib.util
from pathlib import Path
import subprocess


SPEC = importlib.util.spec_from_file_location("repo_context", Path(__file__).resolve().parents[1] / "tools/repo_context.py")
context = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(context)


def test_search_is_literal_bounded_and_scoped(tmp_path):
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    for name, text in {
        "tools/example.py": "literal.* first\nliteral.* second\nliteral.* third\n",
        "tools/untracked.py": "literal.* UNTRACKED_SENTINEL\n",
        "inputs/restricted.md": "literal.* RESTRICTED_SENTINEL\n",
        "wordpipe/legacy/old.py": "literal.* LEGACY_SENTINEL\n",
    }.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "tools/example.py", "inputs/", "wordpipe/"], check=True)
    result = context.find(tmp_path, ["literal.*"], list(context.SCOPES), 2)
    assert len(result["matches"]) == 2
    assert result["truncated"] is True
    full = context.find(tmp_path, ["literal.*"], list(context.SCOPES), 100)
    assert len(full["matches"]) == 3
    assert full["truncated"] is False
    assert context.find(tmp_path, ["literalXYZ"], ["tools"], 20)["matches"] == []


def test_snapshot_reports_detached_head_and_dirty_paths(tmp_path):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(tmp_path), *args], text=True).strip()
    git("init")
    git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-m", "initial")
    head = git("rev-parse", "HEAD")
    git("checkout", "--detach", head)
    (tmp_path / "untracked.txt").write_text("private content")
    result = context.snapshot(tmp_path)
    assert result["head"] == head
    assert result["branch"] == "DETACHED"
    assert result["dirty_entries"] == 1
    assert "private content" not in str(result)
