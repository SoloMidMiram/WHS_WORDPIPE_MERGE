"""MD-01 parser mode names and source coordinates for the generic adapter."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from importlib.metadata import version


LEGACY_MODE = "legacy-v1"
STRUCTURAL_MODE = "structural-v1"
MARKDOWN_MODES = (LEGACY_MODE, STRUCTURAL_MODE)
STRUCTURAL_RAW_SCHEMA = "markdown-structural-prepare-v2"
STRUCTURAL_LINEAGE_SCHEMA = "event-lineage-structural-v2"
STRUCTURAL_CORRELATION_SCHEMA = "event-correlation-structural-v2"
PARSER_ENGINE = "markdown-it-py"
PARSER_PRESET = "commonmark"
PARSER_EXTENSIONS = ("table",)
PARSER_CONTRACT_VERSION = 1


def parser_configuration(heading_levels: tuple[int, ...]) -> dict:
    return {
        "engine": PARSER_ENGINE,
        "preset": PARSER_PRESET,
        "enabled_extensions": list(PARSER_EXTENSIONS),
        "mode": STRUCTURAL_MODE,
        "contract_version": PARSER_CONTRACT_VERSION,
        "heading_levels": sorted(set(heading_levels)),
    }


def parser_provenance(heading_levels: tuple[int, ...]) -> dict:
    configuration = parser_configuration(heading_levels)
    return {**configuration, "distribution_version": version(configuration["engine"])}


def validate_parser_provenance(record: object, heading_levels: tuple[int, ...]) -> dict:
    """Validate the producer record without substituting the reader's version."""
    if not isinstance(record, dict):
        raise ValueError("missing structural parser provenance")
    installed = record.get("distribution_version")
    if not isinstance(installed, str) or not re.fullmatch(r"[0-9][0-9A-Za-z!+._-]*", installed):
        raise ValueError("invalid structural parser distribution version")
    expected = parser_configuration(heading_levels)
    if type(record.get("contract_version")) is not int or record != {**expected, "distribution_version": installed}:
        raise ValueError("unsupported structural parser configuration or heading levels")
    if any(type(level) is not int for level in record["heading_levels"]):
        raise ValueError("invalid structural parser heading levels")
    return record


@dataclass(frozen=True)
class SourceLines:
    """Coordinates in immutable input bytes, independent of parser normalization."""

    text: str
    lines: tuple[str, ...]
    offsets: tuple[int, ...]
    sha256: str

    @classmethod
    def from_bytes(cls, data: bytes) -> SourceLines:
        # Markdown line boundaries are CR, LF and CRLF. Python splitlines also
        # splits on Unicode paragraph separators, which Markdown treats as text.
        raw_lines = tuple(re.findall(rb"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+$", data))
        lines = tuple(line.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n") for line in raw_lines)
        offsets = [0]
        for line in raw_lines:
            offsets.append(offsets[-1] + len(line))
        return cls("".join(lines), lines, tuple(offsets), hashlib.sha256(data).hexdigest())

    def span(self, start: int, end: int) -> dict[str, int]:
        """Convert zero-based half-open ranges to inclusive lines and byte ranges."""
        return {
            "start_line": start + 1,
            "end_line": end,
            "start_byte": self.offsets[start],
            "end_byte": self.offsets[end],
        }


def leading_frontmatter(lines: tuple[str, ...]) -> tuple[int, str | None]:
    """Return consumed lines and an optional diagnostic for a leading opener."""
    import yaml

    if not lines or lines[0].rstrip("\n") != "---":
        return 0, None
    for index, line in enumerate(lines[1:], 1):
        if line.rstrip("\n") == "---":
            try:
                metadata = yaml.safe_load("".join(lines[1:index]))
            except yaml.YAMLError:
                return 0, "invalid_frontmatter"
            if not isinstance(metadata, dict):
                return 0, "invalid_frontmatter"
            return index + 1, None
    return 0, "unterminated_frontmatter"


def section_boundaries(source: SourceLines, heading_levels: tuple[int, ...]):
    """Find selected top-level ATX headings and fenced-code source ranges."""
    from markdown_it import MarkdownIt

    frontmatter_end, diagnostic = leading_frontmatter(source.lines)
    # Blanking the prefix preserves parser map coordinates.
    text = "\n" * frontmatter_end + "".join(source.lines[frontmatter_end:])
    headings = []
    fences = []
    configuration = parser_configuration(heading_levels)
    parser = MarkdownIt(configuration["preset"]).enable(configuration["enabled_extensions"])
    for token in parser.parse(text):
        if token.type == "fence":
            fences.append(tuple(token.map))
        if (
            token.type == "heading_open"
            and token.level == 0
            and token.markup.startswith("#")
            and len(token.markup) in configuration["heading_levels"]
        ):
            start, end = token.map
            # Derive the original heading from the source, retaining inline
            # markup. Drop only ATX opening and optional closing markers.
            title = source.lines[start].lstrip().removeprefix(token.markup).strip()
            title = re.sub(r"(?:^|[ \t])#+[ \t]*$", "", title).strip()
            headings.append((start, end, len(token.markup), title))
    return frontmatter_end, diagnostic, headings, fences
