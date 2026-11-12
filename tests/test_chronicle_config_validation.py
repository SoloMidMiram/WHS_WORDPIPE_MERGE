import subprocess
import sys
from pathlib import Path

import pytest

from pipeline.index import DEFAULT_CONFIG, load_config
from wordpipe.chronicle.categorize import load_themes, match_themes
from wordpipe.chronicle.merge import parse_yaml_frontmatter


@pytest.mark.parametrize(
    "raw",
    [
        b"null", b"[]", b"true", b"\xff",
        b'{"event_snippet_max_chars": NaN}',
        b'{"no_link_registry": "false"}',
    ],
)
def test_invalid_index_config(tmp_path: Path, raw: bytes):
    path = tmp_path / "index.json"
    path.write_bytes(raw)
    assert load_config(path) == DEFAULT_CONFIG
    with pytest.raises(ValueError, match="index config"):
        load_config(path, strict=True)


def test_strict_index_cli_rejects_missing_config_before_publication(tmp_path: Path):
    tagged = tmp_path / "tagged.md"
    tagged.write_text("## Event: 2026-01-01 - Event\nBody\n", encoding="utf-8")
    output = tmp_path / "appendix"
    result = subprocess.run(
        [sys.executable, "-m", "pipeline.index", "--input", str(tagged),
         "--output-dir", str(output), "--config", str(tmp_path / "missing.json"),
         "--strict-config"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 2
    assert "Invalid index config" in result.stderr
    assert not output.exists()


def test_bundled_index_config_passes_strict_validation():
    path = Path(__file__).resolve().parents[1] / "pipeline" / "index_config.json"
    assert load_config(path, strict=True) == DEFAULT_CONFIG


def test_strict_index_config_rejects_unknown_settings(tmp_path: Path):
    path = tmp_path / "index.json"
    path.write_text('{"no_link_regsitry": true}', encoding="utf-8")
    with pytest.raises(ValueError, match="unknown setting"):
        load_config(path, strict=True)


@pytest.mark.parametrize("raw", [b"null", b"[]", b"true", b"\xff", b"- YAML list", b'{"themes": false}'])
def test_invalid_theme_config(tmp_path: Path, raw: bytes):
    path = tmp_path / "themes.json"
    path.write_bytes(raw)
    with pytest.raises(SystemExit) as error:
        load_themes(path)
    assert error.value.code == 1


def test_blank_theme_rules_have_no_effect():
    assert match_themes("API outage", {"Blank": [""], "API": ["API"]}, {"API": [" "]}) == ["API"]


def test_non_mapping_merge_metadata_preserves_body():
    body = "## Event: 2026-01-01 - Event\nBody\n"
    assert parse_yaml_frontmatter("---\n- invalid\n---\n" + body) == ({}, body)
