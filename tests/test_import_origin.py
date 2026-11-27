"""Deterministic CI-01 negative controls for the actual qualification entry points."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "pipeline" / "_import_origin.py"
CONTEXT = "WORDPIPE_ORIGIN_QUALIFICATION"


def _package(root, initializer=""):
    package = root / "wordpipe"
    (package / "chronicle").mkdir(parents=True)
    (package / "__init__.py").write_text(initializer, encoding="utf-8")
    for name in ("execution.py", "chronicle/__init__.py", "chronicle/index.py",
                 "chronicle/markdown_sections.py"):
        (package / name).touch()
    return package


def test_source_session_checks_origin_before_collection(tmp_path):
    intended = tmp_path / "intended"
    foreign = tmp_path / "intended-other"
    ran = tmp_path / "collected"
    imported = tmp_path / "foreign-initializer"
    _package(intended)
    _package(foreign, f"from pathlib import Path; Path({str(imported)!r}).touch()")
    (intended / "tests").mkdir()
    (intended / "pipeline").mkdir()
    shutil.copyfile(GUARD, intended / "pipeline" / GUARD.name)
    shutil.copyfile(ROOT / "tests" / "conftest.py", intended / "tests" / "conftest.py")
    (intended / "tests" / "test_marker.py").write_text(
        f"from pathlib import Path\nPath({str(ran)!r}).touch()\ndef test_marker(): pass\n",
        encoding="utf-8",
    )
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    argv = [sys.executable, "-m", "pytest", "-q", "--wordpipe-origin=source", str(intended / "tests")]
    bad = subprocess.run(argv, cwd=tmp_path, env=dict(env, PYTHONPATH=str(foreign)),
                         capture_output=True, text=True, timeout=30)
    assert bad.returncode == 4, bad.stdout + bad.stderr
    assert "CI-01: foreign origin for wordpipe" in bad.stderr
    assert intended.name in bad.stderr and foreign.name in bad.stderr
    assert not ran.exists() and not imported.exists()
    happy = subprocess.run(argv, cwd=tmp_path, env=dict(env, PYTHONPATH=str(intended / ".." / intended.name)),
                           capture_output=True, text=True, timeout=30)
    assert happy.returncode == 0, happy.stdout + happy.stderr
    assert ran.exists()


@pytest.mark.parametrize(("setup", "diagnostic"), [
    ("", "missing origin"),
    ("sys.modules['wordpipe'] = types.ModuleType('wordpipe')", "invalid origin"),
    ("sys.path.insert(0, sys.argv[2]); import wordpipe; wordpipe.__path__.append(sys.argv[3])", "mixed origin"),
])
def test_missing_invalid_and_mixed_origins(tmp_path, setup, diagnostic):
    intended = tmp_path / "intended"
    foreign = tmp_path / "outside"
    _package(intended)
    package = _package(foreign)
    check = (
        "import runpy,sys,types\n" + setup
        + "\nrunpy.run_path(sys.argv[1])['verify']('source', sys.argv[2])"
    )
    result = subprocess.run([sys.executable, "-I", "-S", "-c", check, str(GUARD), str(intended), str(package)],
                            capture_output=True, text=True, timeout=15)
    assert result.returncode != 0
    assert f"{diagnostic} for wordpipe" in result.stderr


@pytest.mark.parametrize("script", ["pipeline/index.py", "tools/run_topic_report.py"])
def test_actual_child_rejects_foreign_origin_before_bootstrap(tmp_path, script):
    foreign = tmp_path / "foreign"
    imported = tmp_path / "foreign-initializer"
    _package(foreign, f"from pathlib import Path; Path({str(imported)!r}).touch()")
    # A healthy pytest session can still spawn a child with a different search path.
    import wordpipe

    assert Path(wordpipe.__file__).resolve().is_relative_to(ROOT / "wordpipe")
    env = dict(os.environ, PYTHONPATH=str(foreign))
    result = subprocess.run([sys.executable, str(ROOT / script), "--help"],
                            cwd=ROOT, env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode != 0
    assert "CI-01: foreign origin for wordpipe" in result.stderr
    assert "usage:" not in result.stdout and not imported.exists()


def test_powershell_stage_records_foreign_origin_before_ingest(tmp_path):
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        pytest.skip("requires the platform PowerShell launcher")
    foreign = tmp_path / "foreign"
    _package(foreign)
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "one.md").write_text("- **2025-01-01 - Test:** body\n", encoding="utf-8")
    out = tmp_path / "run"
    env = dict(os.environ, PYTHONPATH=str(foreign),
               PATH=os.pathsep.join((str(Path(sys.executable).parent), os.environ["PATH"])))
    result = subprocess.run(
        [shell, "-NoProfile", "-NonInteractive", "-File", str(ROOT / "pipeline" / "chain.ps1"),
         "-InputDir", str(raw), "-OutputDir", str(out)],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "CI-01: foreign origin for wordpipe" in result.stdout
    assert not list((out / "normalised").glob("*.md"))
    run = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert run["status"] == "failed"
    assert run["stages"][2]["status"] == "not_run"
