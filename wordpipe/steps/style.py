"""Style step: apply document styles and format code blocks.

This step reads the document from the working path, applies styles,
and returns the in-memory document object for downstream steps.
"""
# wordpipe/steps/style.py
# Created: 2026-02-14 (Jalali: 1404/11/25)
# Modified: 2026-02-14 (Jalali: 1404/11/25)
# Purpose: Style step for the WordPipe pipeline.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from wordpipe.core.datatypes import PipelineConfig
from wordpipe.events import EventSink, NullSink
from wordpipe.interfaces.documents import DocumentReader, DocumentStyler


@dataclass(slots=True)
class StyleResult:
    """Result of the style step."""

    doc: Any
    error: Optional[str] = None


def style_step(
    cfg: PipelineConfig,
    working: Path,
    reader: DocumentReader,
    styler: DocumentStyler,
    sink: EventSink | None = None,
) -> StyleResult:
    """Read the document and apply styles.

    Args:
        cfg: Pipeline configuration.
        working: Path to the working document.
        reader: Document reader implementation.
        styler: Document styler implementation.
        sink: Event sink for telemetry.

    Returns:
        StyleResult with the styled in-memory document.
    """
    sink = sink or NullSink()

    try:
        sink.emit("INFO", "style_read_begin", {"path": str(working)})
        doc = reader.read(working)
        sink.emit("INFO", "style_read_done", {})

        sink.emit("INFO", "style_ensure_styles_begin", {})
        styler.ensure_styles(doc, logger=sink)
        sink.emit("INFO", "style_ensure_styles_done", {})

        sink.emit("INFO", "style_code_blocks_begin", {})
        styler.style_code_blocks(doc, logger=sink)
        sink.emit("INFO", "style_code_blocks_done", {})

        return StyleResult(doc=doc)
    except Exception as e:
        msg = f"Style step failed: {e}"
        sink.emit("ERROR", "style_fail", {"error": str(e)})
        return StyleResult(doc=None, error=msg)
