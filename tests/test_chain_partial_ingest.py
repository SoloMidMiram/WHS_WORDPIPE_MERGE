"""Regression tests for chain.ps1 -AllowPartialIngest with a reused output dir.

Covers the partial-run merge wiring: when a file that succeeded on an earlier
run fails during the current run, the merge stage must use only the normalised
outputs produced by the current run (--inputs), not scan the whole
normalised/ directory and merge stale files from the previous run.
"""

from __future__ import annotations

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


def _run_chain(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    assert _POWERSHELL is not None
    return subprocess.run(
        [_POWERSHELL, "-NoProfile", "-File", str(CHAIN_PS1), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
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
