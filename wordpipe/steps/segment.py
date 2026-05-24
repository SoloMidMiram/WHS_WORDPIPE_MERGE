"""Segment step: split the document into logical segments by heading.

This step operates on the file path (not the in-memory doc) because
segmentation is typically done by re-reading the file.
"""
# wordpipe/steps/segment.py
# Created: 2026-02-14 (Jalali: 1404/11/25)
# Modified: 2026-02-14 (Jalali: 1404/11/25)
# Purpose: Segment step for the WordPipe pipeline.

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from wordpipe.core.datatypes import PipelineConfig, Segment
from wordpipe.events import EventSink, NullSink
from wordpipe.interfaces.documents import DocumentSegmenter


@dataclass(slots=True)
class SegmentResult:
    """Result of the segment step."""

    segments: list[Segment] = field(default_factory=list)
    error: Optional[str] = None


def segment_step(
    cfg: PipelineConfig,
    working: Path,
    segmenter: DocumentSegmenter,
    sink: EventSink | None = None,
) -> SegmentResult:
    """Segment the working document.

    Args:
        cfg: Pipeline configuration.
        working: Path to the working document.
        segmenter: Document segmenter implementation.
        sink: Event sink for telemetry.

    Returns:
        SegmentResult with the list of segments.
    """
    sink = sink or NullSink()

    try:
        sink.emit("INFO", "segment_begin", {"path": str(working)})
        segments = segmenter.segment(working)
        sink.emit(
            "INFO",
            "segment_done",
            {"count": len(segments)},
        )
        return SegmentResult(segments=segments)
    except Exception as e:
        msg = f"Segment step failed: {e}"
        sink.emit("ERROR", "segment_fail", {"error": str(e)})
        return SegmentResult(error=msg)
