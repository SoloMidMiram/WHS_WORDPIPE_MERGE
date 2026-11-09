"""Executable regression tests for the Chronicle PowerShell chain."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHAIN_PS1 = REPO_ROOT / "pipeline" / "chain.ps1"

# chain.ps1 invokes ``python.exe`` by name, which is Windows-specific, so the
# test is skipped on environments that cannot run the script at all.
_POWERSHELL: str | None = shutil.which("pwsh") or shutil.which("powershell")
_PYTHON_EXE: str | None = shutil.which("python.exe")


def _run_chain(
    args: list[str], cwd: Path, script: Path = CHAIN_PS1,
) -> subprocess.CompletedProcess[str]:
    assert _POWERSHELL is not None
    return subprocess.run(
        [_POWERSHELL, "-NoProfile", "-File", str(script), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
    )


@pytest.mark.skipif(
    _POWERSHELL is None or _PYTHON_EXE is None,
    reason="chain.ps1 requires PowerShell and python.exe",
)
def test_chain_allow_partial_ingest_reused_output_dir(tmp_path: Path) -> None:
    """A partial run over a reused output dir merges only fresh normalised files."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    out_dir = tmp_path / "out"

    alpha = raw_dir / "alpha.md"
    beta = raw_dir / "beta.md"

    # Run 1: only a valid dated file.
    alpha.write_text(
        textwrap.dedent("""\
        # Source

        - **2025-01-10 - Alpha Outage:** alpha outage body
        """),
        encoding="utf-8",
    )
    first = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir),
         "-SkipCategorize", "-SkipIndex"],
        cwd=REPO_ROOT,
    )
    assert first.returncode == 0, first.stdout + first.stderr
    normalised_alpha = out_dir / "normalised" / "alpha.md"
    merged = out_dir / "merged.md"
    assert normalised_alpha.exists(), "Run 1 should normalise alpha.md"
    assert merged.exists(), "Run 1 should produce merged.md"
    assert "Alpha Outage" in merged.read_text(encoding="utf-8")

    # Run 2: alpha is now undated (ingest fails) and beta is a new valid file.
    alpha.write_text(
        textwrap.dedent("""\
        # Source

        - **unknown - Alpha Outage:** alpha outage body
        """),
        encoding="utf-8",
    )
    beta.write_text(
        textwrap.dedent("""\
        # Source

        - **2025-02-20 - Beta Launch:** beta launch body
        """),
        encoding="utf-8",
    )
    second = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir),
         "-AllowPartialIngest", "-SkipCategorize", "-SkipIndex"],
        cwd=REPO_ROOT,
    )
    assert second.returncode == 0, second.stdout + second.stderr
    merged_text = merged.read_text(encoding="utf-8")
    assert "Beta Launch" in merged_text, "New valid file's event must be merged"
    assert "Alpha Outage" not in merged_text, (
        "Stale event from the previous run's normalised file must not be merged"
    )

    verified = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir),
         "-AllowPartialIngest", "-Verify", "-SkipCategorize"],
        cwd=REPO_ROOT,
    )
    assert verified.returncode == 2, verified.stdout + verified.stderr
    assert "Verification failed" in verified.stdout


@pytest.mark.skipif(
    _POWERSHELL is None or _PYTHON_EXE is None,
    reason="chain.ps1 requires PowerShell and python.exe",
)
def test_chain_all_five_stages_with_verify(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "events.md").write_text(
        "- **2025-01-10 - Alpha Outage:** first event\n"
        "- **2025-01-11 - Beta Launch:** second event\n",
        encoding="utf-8",
    )
    (raw_dir / "overview.md").write_text("# Overview\n\nNarrative only.\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    result = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir),
         "-Verify", "-Verbose"],
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Total events extracted: 2" in result.stdout
    assert "WARNING: No dates found in content" in result.stdout
    assert "Files with issues: 0" in result.stdout
    merged = (out_dir / "merged.md").read_text(encoding="utf-8")
    assert "Alpha Outage" in merged
    assert "Beta Launch" in merged
    tagged = json.loads((out_dir / "chronicle_tagged.tagged.json").read_text(encoding="utf-8"))
    assert len(tagged) == 2
    appendix = out_dir / "appendix"
    index = (appendix / "event_index.md").read_text(encoding="utf-8")
    assert index.count("Alpha Outage") == 1
    assert index.count("Beta Launch") == 1
    for name in ("theme_index.md", "source_manifest.md", "link_registry.md"):
        assert (appendix / name).is_file()


STAGE_SCRIPTS = ("ingest", "verify_ingest", "merge", "categorize", "index")


@pytest.fixture
def isolated_chain(tmp_path: Path) -> tuple[Path, Path, Path]:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    chain = scripts / CHAIN_PS1.name
    shutil.copyfile(CHAIN_PS1, chain)
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "input.md").write_text("fixture", encoding="utf-8")
    for stage in STAGE_SCRIPTS:
        (scripts / f"{stage}.py").write_text(
            "import sys\n"
            "from pathlib import Path\n"
            f"Path({stage!r}).touch()\n"
            f"print('WARNING: diagnostic from {stage}', file=sys.stderr)\n",
            encoding="utf-8",
        )
    return chain, raw_dir, tmp_path / "out"


@pytest.mark.skipif(
    _POWERSHELL is None or _PYTHON_EXE is None,
    reason="chain.ps1 requires PowerShell and python.exe",
)
@pytest.mark.parametrize("stage_code", range(1, 6))
def test_chain_maps_native_failure_to_operator_code(isolated_chain, stage_code: int) -> None:
    chain, raw_dir, out_dir = isolated_chain
    stage = STAGE_SCRIPTS[stage_code - 1]
    with (chain.parent / f"{stage}.py").open("a", encoding="utf-8") as script:
        script.write("raise SystemExit(23)\n")
    result = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir), "-Verify", "-Verbose"],
        cwd=raw_dir.parent,
        script=chain,
    )
    assert result.returncode == stage_code, result.stdout + result.stderr
    assert "native_exit, exit code 23" in result.stdout
    assert f"WARNING: diagnostic from {stage}" in result.stdout
    assert [name for name in STAGE_SCRIPTS if (raw_dir.parent / name).exists()] == list(
        STAGE_SCRIPTS[:stage_code]
    )


@pytest.mark.skipif(_POWERSHELL is None, reason="chain.ps1 requires PowerShell")
def test_chain_missing_python_is_launch_failure_with_stale_exit_code(isolated_chain) -> None:
    chain, raw_dir, out_dir = isolated_chain
    result = subprocess.run(
        [_POWERSHELL, "-NoProfile", "-Command",
         "$global:LASTEXITCODE = 23; "
         "& $env:TEST_CHAIN -InputDir $env:TEST_INPUT -OutputDir $env:TEST_OUTPUT; "
         "exit $LASTEXITCODE"],
        cwd=raw_dir.parent,
        env={**os.environ, "PATH": str(raw_dir), "TEST_CHAIN": str(chain),
             "TEST_INPUT": str(raw_dir), "TEST_OUTPUT": str(out_dir)},
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "launch_error" in result.stdout
    assert "python.exe" in result.stdout
    assert "native_exit" not in result.stdout
    assert not (raw_dir.parent / "ingest").exists()


@pytest.mark.skipif(_POWERSHELL is None, reason="chain.ps1 requires PowerShell")
def test_chain_reports_normalised_directory_collision(isolated_chain) -> None:
    chain, raw_dir, out_dir = isolated_chain
    out_dir.mkdir()
    (out_dir / "normalised").write_text("existing file", encoding="utf-8")
    result = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir)],
        cwd=raw_dir.parent,
        script=chain,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "Ingestion setup failed" in result.stderr
    assert "normalised" in result.stderr
    assert not (raw_dir.parent / "ingest").exists()
