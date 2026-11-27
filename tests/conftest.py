"""Select a trusted origin before the test modules are collected."""

import json
import runpy
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption("--wordpipe-origin", choices=("source", "wheel"), default="source")
    parser.addoption("--wordpipe-wheel-prefix", type=Path)


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    root = Path(__file__).resolve().parents[1]
    checker = runpy.run_path(str(root / "pipeline" / "_import_origin.py"))
    prefix = session.config.getoption("--wordpipe-wheel-prefix")
    context = {
        "mode": session.config.getoption("--wordpipe-origin"),
        "checkout": str(root),
        "prefix": str(prefix) if prefix is not None else None,
    }
    modules = (
        "wordpipe.execution", "wordpipe.chronicle.index", "wordpipe.chronicle.markdown_sections",
        "pipeline.index", "tools.compare_markdown_modes", "tools.prepare_generic_markdown_chronicle",
        "tools.run_topic_report",
    )
    if context["mode"] == "source":
        modules += ("tools.pipeline_contracts",)
    try:
        report = checker["verify"](**context, modules=modules)
    except (OSError, TypeError, ValueError, AttributeError) as exc:
        raise pytest.UsageError(f"CI-01: {exc}") from None
    print("CI-01 session origin:", json.dumps(report, sort_keys=True))
    # Stages validate in their own process using the session's explicit roots.
    patch = pytest.MonkeyPatch()
    patch.setenv(checker["CONTEXT_ENV"], json.dumps(context))
    session.config.add_cleanup(patch.undo)
