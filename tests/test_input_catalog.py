"""Tests for canonical corpus-input layout and provenance checks."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "check_input_catalog.py"
SPEC = importlib.util.spec_from_file_location("check_input_catalog", MODULE_PATH)
checker = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(checker)


def _write_valid_catalog(root: Path, *, rel: str = "inputs/demo/markdown/source.md") -> Path:
    source = root / rel
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("source", encoding="utf-8")
    payload = source.read_bytes()
    catalog = {
        "schema_version": 1,
        "entries": [{
            "corpus": "demo",
            "format": "markdown",
            "path": rel,
            "size_bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "classification": "source",
        }],
    }
    catalog_path = root / "inputs" / "catalog.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    return catalog_path


def test_current_input_catalog_is_valid():
    assert checker.find_violations(MODULE_PATH.parents[1]) == []


def test_catalog_detects_hash_drift(tmp_path):
    _write_valid_catalog(tmp_path)
    (tmp_path / "inputs/demo/markdown/source.md").write_text("changed", encoding="utf-8")
    violations = checker.find_violations(tmp_path)
    assert any("size differs" in item or "SHA-256 differs" in item for item in violations)


def test_catalog_detects_unlisted_and_missing_inputs(tmp_path):
    _write_valid_catalog(tmp_path)
    (tmp_path / "inputs/demo/markdown/extra.md").write_text("extra", encoding="utf-8")
    (tmp_path / "inputs/demo/markdown/source.md").unlink()
    violations = checker.find_violations(tmp_path)
    assert any("unlisted input" in item for item in violations)
    assert any("missing input" in item for item in violations)


def test_catalog_rejects_nested_format_file_and_wrong_extension(tmp_path):
    catalog_path = _write_valid_catalog(
        tmp_path, rel="inputs/demo/markdown/nested/source.docx"
    )
    violations = checker.find_violations(tmp_path, catalog_path)
    assert any("top-level-file" in item for item in violations)


def test_catalog_rejects_legacy_input_location(tmp_path):
    _write_valid_catalog(tmp_path)
    legacy = tmp_path / checker.LEGACY_INPUT_DIRS[1]
    legacy.mkdir(parents=True)
    violations = checker.find_violations(tmp_path)
    assert any("legacy input location" in item for item in violations)


def test_catalog_v2_with_valid_hash_mode_passes(tmp_path):
    """A v2 catalog with valid hash_mode is accepted."""
    source = tmp_path / "inputs/demo/markdown/source.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("source", encoding="utf-8")
    payload = source.read_bytes()
    catalog = {
        "schema_version": 2,
        "hash_mode": "lf_normalized_utf8",
        "entries": [{
            "corpus": "demo",
            "format": "markdown",
            "path": "inputs/demo/markdown/source.md",
            "size_bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "classification": "source",
        }],
    }
    catalog_path = tmp_path / "inputs" / "catalog.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    assert checker.find_violations(tmp_path) == []


def test_catalog_v2_missing_hash_mode_fails(tmp_path):
    """A v2 catalog without hash_mode returns a violation."""
    source = tmp_path / "inputs/demo/markdown/source.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("source", encoding="utf-8")
    catalog = {
        "schema_version": 2,
        "entries": [{
            "corpus": "demo",
            "format": "markdown",
            "path": "inputs/demo/markdown/source.md",
            "size_bytes": 6,
            "sha256": "0000",
            "classification": "source",
        }],
    }
    catalog_path = tmp_path / "inputs" / "catalog.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    violations = checker.find_violations(tmp_path)
    assert any("hash_mode" in item for item in violations)


def test_catalog_v2_invalid_hash_mode_fails(tmp_path):
    """A v2 catalog with wrong hash_mode returns a violation."""
    source = tmp_path / "inputs/demo/markdown/source.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("source", encoding="utf-8")
    catalog = {
        "schema_version": 2,
        "hash_mode": "raw_bytes",
        "entries": [{
            "corpus": "demo",
            "format": "markdown",
            "path": "inputs/demo/markdown/source.md",
            "size_bytes": 6,
            "sha256": "0000",
            "classification": "source",
        }],
    }
    catalog_path = tmp_path / "inputs" / "catalog.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    violations = checker.find_violations(tmp_path)
    assert any("hash_mode" in item for item in violations)


def test_catalog_rejects_non_object_catalog(tmp_path):
    """A list-shaped catalog returns a normal catalog diagnostic, not a traceback."""
    catalog_path = tmp_path / "inputs" / "catalog.json"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text("[]", encoding="utf-8")
    violations = checker.find_violations(tmp_path, catalog_path)
    assert len(violations) == 1
    assert violations[0].startswith("catalog:")


def test_catalog_docx_hashes_raw_binary(tmp_path):
    """DOCX (binary ZIP) entries are hashed raw, not CRLF-normalized."""
    docx = tmp_path / "inputs/demo/docx/sample.docx"
    docx.parent.mkdir(parents=True, exist_ok=True)
    # Binary content containing CRLF pairs; normalizing them would change both
    # the size and the SHA-256, so the checker must hash DOCX bytes verbatim.
    payload = b"PK\x03\x04\x0d\x0a\x00\x00content\r\nmore\x00"
    docx.write_bytes(payload)
    catalog = {
        "schema_version": 2,
        "hash_mode": "lf_normalized_utf8",
        "entries": [{
            "corpus": "demo",
            "format": "docx",
            "path": "inputs/demo/docx/sample.docx",
            "size_bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "classification": "source",
        }],
    }
    catalog_path = tmp_path / "inputs" / "catalog.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    assert checker.find_violations(tmp_path) == []
