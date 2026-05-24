"""Finalize step: write the styled document to the output path and clean up.

This step:
1. Writes the in-memory document to the final output path
2. Cleans up the intermediate working file (if different from input)
"""
# wordpipe/steps/finalize.py
# Created: 2026-02-14 (Jalali: 1404/11/25)
# Modified: 2026-02-14 (Jalali: 1404/11/25)
# Purpose: Finalize step for the WordPipe pipeline.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from wordpipe.core.datatypes import PipelineConfig
from wordpipe.events import EventSink, NullSink
from wordpipe.interfaces.documents import DocumentWriter


@dataclass(slots=True)
class FinalizeResult:
    """Result of the finalize step."""

    out_path: Path
    error: Optional[str] = None


def finalize_step(
    cfg: PipelineConfig,
    doc: Any,
    working: Path,
    writer: DocumentWriter,
    sink: EventSink | None = None,
) -> FinalizeResult:
    """Write the document and clean up the working file.

    Args:
        cfg: Pipeline configuration.
        doc: The in-memory document to write.
        working: The working file path (may be intermediate).
        writer: Document writer implementation.
        sink: Event sink for telemetry.

    Returns:
        FinalizeResult with the output path.
    """
    sink = sink or NullSink()
    out = Path(cfg.out_path)

    try:
        sink.emit("INFO", "write_begin", {"path": str(out)})
        writer.write(doc, out)
        sink.emit("INFO", "write_done", {"path": str(out)})
    except Exception as e:
        msg = f"Write failed: {e}"
        sink.emit("ERROR", "write_fail", {"error": str(e)})
        return FinalizeResult(out_path=out, error=msg)

    # Clean up intermediate working file
    if working != Path(cfg.in_path):
        try:
            working.unlink()
            sink.emit("INFO", "cleanup_done", {"path": str(working)})
        except OSError as e:
            sink.emit("WARNING", "cleanup_fail", {"path": str(working), "error": str(e)})

    return FinalizeResult(out_path=out)
