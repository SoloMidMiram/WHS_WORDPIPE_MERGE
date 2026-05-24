"""Flatten step: reduce complex DOCX to a simpler intermediate format.

This step is optional — it only runs when:
1. `cfg.do_flatten` is True
2. A Flattener implementation is available
"""
# wordpipe/steps/flatten.py
# Created: 2026-02-14 (Jalali: 1404/11/25)
# Modified: 2026-02-14 (Jalali: 1404/11/25)
# Purpose: Flatten step for the WordPipe pipeline.

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from wordpipe.core.datatypes import ChangeNote, PipelineConfig
from wordpipe.events import EventSink, NullSink
from wordpipe.interfaces.transforms import Flattener


@dataclass(slots=True)
class FlattenResult:
    """Result of the flatten step."""

    working_path: Path
    notes: list[ChangeNote] = field(default_factory=list)
    skipped: bool = False
    error: Optional[str] = None


def flatten_step(
    cfg: PipelineConfig,
    flattener: Optional[Flattener],
    sink: EventSink | None = None,
) -> FlattenResult:
    """Run the flatten step if configured.

    Args:
        cfg: Pipeline configuration.
        flattener: The flattener implementation, or None to skip.
        sink: Event sink for telemetry.

    Returns:
        FlattenResult with the working path (may differ from input if flattened).
    """
    sink = sink or NullSink()
    working = Path(cfg.in_path)

    if not cfg.do_flatten or flattener is None:
        sink.emit("INFO", "flatten_skip", {"reason": "not_configured"})
        return FlattenResult(working_path=working, skipped=True)

    tmp = Path(str(cfg.out_path) + ".work.docx")
    try:
        sink.emit(
            "INFO",
            "flatten_begin",
            {
                "mode": flattener.__class__.__name__,
                "limit_pages": cfg.limit_pages,
            },
        )
        notes = flattener.flatten(working, tmp, limit_pages=cfg.limit_pages)
        sink.emit(
            "INFO",
            "flatten_done",
            {
                "mode": flattener.__class__.__name__,
                "notes": len(notes),
            },
        )
        return FlattenResult(working_path=tmp, notes=notes)
    except Exception as e:
        msg = f"Flatten failed: {e}"
        sink.emit("WARNING", "flatten_fail", {"error": str(e)})
        return FlattenResult(working_path=working, error=msg)
