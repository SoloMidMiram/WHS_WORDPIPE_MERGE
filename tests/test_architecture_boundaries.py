"""Tests for the narrow AST-based architecture boundary guard."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "check_architecture_boundaries.py"
SPEC = importlib.util.spec_from_file_location("check_architecture_boundaries", MODULE_PATH)
checker = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _rendered_violations(root: Path) -> list[str]:
    violations, errors, _ = checker.find_violations(root)
    return errors + [item.render() for item in violations]


def test_current_repository_satisfies_v1_boundaries():
    violations, errors, count = checker.find_violations(MODULE_PATH.parents[1])
    assert errors == []
    assert violations == []
    assert count > 0


def test_wordpipe_cannot_import_tools_or_pipeline(tmp_path):
    _write(tmp_path, "wordpipe/a.py", "import tools.runner\n")
    _write(tmp_path, "wordpipe/b.py", "from pipeline import index\n")
    rendered = _rendered_violations(tmp_path)
    assert len(rendered) == 2
    assert any("tools.runner" in item for item in rendered)
    assert any("pipeline" in item for item in rendered)


def test_core_and_interfaces_cannot_import_outward_layers(tmp_path):
    _write(tmp_path, "wordpipe/core/a.py", "from wordpipe.adapters import defaults\n")
    _write(
        tmp_path,
        "wordpipe/interfaces/b.py",
        "from wordpipe.orchestrator import process_docx_v3\n",
    )
    rendered = _rendered_violations(tmp_path)
    assert len(rendered) == 2
    assert all("dependency-inward" in item for item in rendered)


def test_chronicle_cannot_import_topic_runner_or_docx_adapter(tmp_path):
    _write(
        tmp_path,
        "wordpipe/chronicle/a.py",
        "from tools import run_topic_report\n",
    )
    _write(
        tmp_path,
        "wordpipe/chronicle/b.py",
        "from wordpipe.adapters.docx import io\n",
    )
    rendered = _rendered_violations(tmp_path)
    assert len(rendered) == 2
    assert any("tools" in item for item in rendered)
    assert any("DOCX-runtime-neutral" in item for item in rendered)


def test_expected_inward_and_chronicle_imports_are_allowed(tmp_path):
    _write(
        tmp_path,
        "wordpipe/interfaces/a.py",
        "from pathlib import Path\nfrom wordpipe.core.datatypes import Segment\n",
    )
    _write(
        tmp_path,
        "wordpipe/chronicle/a.py",
        "from wordpipe.chronicle.ingest import split_into_events\n",
    )
    assert _rendered_violations(tmp_path) == []


def test_registered_composition_and_wrapper_roles_are_centralized_and_specific(tmp_path):
    assert checker.active_v1_bypass_count() == 0
    reason = checker.exception_reason(
        "wordpipe/orchestrator.py", "wordpipe.adapters.defaults"
    )
    assert reason and "composition root" in reason
    assert checker.exception_reason(
        "wordpipe/random.py", "wordpipe.adapters.defaults"
    ) is None
    assert checker.exception_reason(
        "wordpipe/orchestrator.py", "tools.run_topic_report"
    ) is None
    _write(
        tmp_path,
        "wordpipe/orchestrator.py",
        "from wordpipe.adapters import defaults\n",
    )
    _write(
        tmp_path,
        "pipeline/ingest.py",
        "from wordpipe.chronicle import ingest\n",
    )
    assert _rendered_violations(tmp_path) == []


def test_type_checking_imports_and_tests_are_outside_v1_runtime_scan(tmp_path):
    _write(
        tmp_path,
        "wordpipe/a.py",
        "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    import tools.runner\n",
    )
    _write(tmp_path, "tests/test_dynamic.py", "import tools.runner\n")
    _write(tmp_path, "wordpipe/tests/test_fixture.py", "import tools.runner\n")
    assert _rendered_violations(tmp_path) == []


def test_unregistered_forbidden_edge_is_not_suppressed(tmp_path):
    _write(tmp_path, "wordpipe/random.py", "import tools.run_topic_report\n")
    rendered = _rendered_violations(tmp_path)
    assert len(rendered) == 1
    assert "tools.run_topic_report" in rendered[0]
