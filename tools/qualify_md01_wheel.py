#!/usr/bin/env python3
"""Qualify the MD-01 wheel with the checkout's thin Chronicle driver scripts."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, help="Fresh directory for paired-run artifacts")
    args = parser.parse_args()
    pytest_args = []
    if args.evidence_dir is not None:
        evidence_dir = args.evidence_dir.resolve()
        evidence_dir.mkdir(parents=True, exist_ok=False)
        pytest_args = ["--basetemp", str(evidence_dir / "pytest")]
    root = Path(__file__).resolve().parents[1]
    shell = "powershell" if os.name == "nt" else "pwsh"
    if not shutil.which(shell):
        raise SystemExit(f"MD-01 qualification requires {shell}")
    with tempfile.TemporaryDirectory(prefix="md01-wheel-") as work:
        work = Path(work)
        wheels = work / "wheels"
        venv = work / "venv"
        checkout = work / "drivers"
        build_source = work / "build-source"
        shutil.copytree(root / "wordpipe", build_source / "wordpipe", ignore=shutil.ignore_patterns("__pycache__"))
        (build_source / "docs").mkdir()
        shutil.copyfile(root / "docs/README.md", build_source / "docs/README.md")
        shutil.copyfile(root / "pyproject.toml", build_source / "pyproject.toml")
        subprocess.run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir", str(wheels), str(build_source)],
            check=True,
        )
        wheel, = wheels.glob("wordpipe-*.whl")
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        bin_dir = venv / ("Scripts" if os.name == "nt" else "bin")
        python = bin_dir / ("python.exe" if os.name == "nt" else "python")
        subprocess.run(
            [str(python), "-m", "pip", "install", f"wordpipe[chronicle,test] @ {wheel.as_uri()}"],
            check=True,
        )
        shutil.copytree(root / "pipeline", checkout / "pipeline")
        for name in (
            "tools/compare_markdown_modes.py",
            "tools/prepare_generic_markdown_chronicle.py",
            "tools/run_topic_report.py",
            "tests/test_md01_markdown_modes.py",
            "tests/fixtures/md01_structure.md",
            "tests/fixtures/md01_identity_legacy.json",
            "WordHorrorStories/flowers/topic_manifest.json",
            "WordHorrorStories/flowers/themes.flowers.json",
        ):
            destination = checkout / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, destination)
        env = dict(os.environ, PATH=os.pathsep.join((str(bin_dir), os.environ["PATH"])))
        subprocess.run(
            [str(python), "-c",
             "from pathlib import Path; import sys, wordpipe.chronicle.markdown_sections as m; "
             "origin = Path(m.__file__).resolve(); print('MD-01 installed origin:', origin); "
             "assert origin.is_relative_to(Path(sys.prefix).resolve())"],
            cwd=checkout, env=env, check=True,
        )
        subprocess.run(
            [str(python), "-m", "pytest", "-q", "-s", *pytest_args,
             "tests/test_md01_markdown_modes.py::test_paired_replay"],
            cwd=checkout, env=env, check=True,
        )


if __name__ == "__main__":
    main()
