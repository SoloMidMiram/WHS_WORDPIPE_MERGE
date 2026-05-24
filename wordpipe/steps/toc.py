"""TOC step: update the table of contents in the output document.

This step is optional — it only runs when a TocUpdater implementation
is available. It operates on the final output file path.
"""
# wordpipe/steps/toc.py
# Created: 2026-02-14 (Jalali: 1404/11/25)
# Modified: 2026-02-14 (Jalali: 1404/11/25)
# Purpose: TOC step for the WordPipe pipeline.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from wordpipe.core.datatypes import PipelineConfig
from wordpipe.events import EventSink, NullSink
from wordpipe.interfaces.transforms import TocUpdater


@dataclass(slots=True)
class TocResult:
    """Result of the TOC update step."""

    updated: bool = False
    error: Optional[str] = None


def toc_step(
    cfg: PipelineConfig,
    out_path: Path,
    toc_updater: Optional[TocUpdater],
    sink: EventSink | None = None,
) -> TocResult:
    """Update the table of contents if a TocUpdater is available.

    Args:
        cfg: Pipeline configuration.
        out_path: Path to the output document.
        toc_updater: The TOC updater implementation, or None to skip.
        sink: Event sink for telemetry.

    Returns:
        TocResult indicating whether the TOC was updated.
    """
    sink = sink or NullSink()

    if toc_updater is None:
        sink.emit("INFO", "toc_skip", {"reason": "not_configured"})
        return TocResult(updated=False)

    try:
        sink.emit("INFO", "toc_update_begin", {"path": str(out_path)})
        toc_updater.update(out_path)
        sink.emit("INFO", "toc_update_done", {})
        return TocResult(updated=True)
    except Exception as e:
        msg = f"TOC update failed: {e}"
        sink.emit("WARNING", "toc_update_fail", {"error": str(e)})
        return TocResult(updated=False, error=msg)
