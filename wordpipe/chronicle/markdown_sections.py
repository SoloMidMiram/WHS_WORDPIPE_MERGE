"""MD-01 parser mode names and source coordinates for the generic adapter."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


LEGACY_MODE = "legacy-v1"
STRUCTURAL_MODE = "structural-v1"
MARKDOWN_MODES = (LEGACY_MODE, STRUCTURAL_MODE)
STRUCTURAL_RAW_SCHEMA = "markdown-structural-prepare-v1"
STRUCTURAL_LINEAGE_SCHEMA = "event-lineage-structural-v1"
STRUCTURAL_CORRELATION_SCHEMA = "event-correlation-structural-v1"


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
    for token in MarkdownIt("commonmark").enable("table").parse(text):
        if token.type == "fence":
            fences.append(tuple(token.map))
        if (
            token.type == "heading_open"
            and token.level == 0
            and token.markup.startswith("#")
            and len(token.markup) in heading_levels
        ):
            start, end = token.map
            # Derive the original heading from the source, retaining inline
            # markup. Drop only ATX opening and optional closing markers.
            title = source.lines[start].lstrip().removeprefix(token.markup).strip()
            title = re.sub(r"(?:^|[ \t])#+[ \t]*$", "", title).strip()
            headings.append((start, end, len(token.markup), title))
    return frontmatter_end, diagnostic, headings, fences
