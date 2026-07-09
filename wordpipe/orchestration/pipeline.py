"""Interfaces-only pipeline orchestrator using pluggable steps."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from wordpipe.core.datatypes import PipelineConfig, RunReport, Segment
from wordpipe.events import EventSink, NullSink
from wordpipe.interfaces.ai import AISummarizer
from wordpipe.interfaces.documents import (
    DocumentReader,
    DocumentSegmenter,
    DocumentStyler,
    DocumentWriter,
)
from wordpipe.interfaces.logging import Logger
from wordpipe.interfaces.transforms import Flattener, TocUpdater
from wordpipe.steps import (
    FinalizeResult,
    FlattenResult,
    SegmentResult,
    StyleResult,
    TocResult,
    finalize_step,
    flatten_step,
    segment_step,
    style_step,
    toc_step,
)


@dataclass(slots=True)
class OrchestrationDeps:
    """Dependency container — each field is an interface, injected at composition root."""

    reader: DocumentReader
    writer: DocumentWriter
    styler: DocumentStyler
    segmenter: DocumentSegmenter
    logger: Logger | None = None
    flattener: Flattener | None = None
    toc_updater: TocUpdater | None = None
    ai: AISummarizer | None = None


class WordPipePipeline:
    """Core pipeline orchestrator (interfaces-only, dependency-injected).

    Runs a sequence of `wordpipe.steps.*` functions. Each step is
    unit-testable in isolation. Errors are collected into ``RunReport.errors``
    and do not halt the pipeline (failures are reported, not swallowed).
    """

    def __init__(self, deps: OrchestrationDeps):
        self._deps = deps

    def run(self, cfg: PipelineConfig) -> RunReport:
        sink: EventSink = self._deps.logger or NullSink()  # type: ignore[assignment]
        t0 = perf_counter()
        sink.emit("INFO", "start", {k: str(v) for k, v in cfg.__dict__.items()})

        errors: list[str] = []

        # ---- Step 1: Flatten (optional) ----
        fr: FlattenResult = flatten_step(cfg, self._deps.flattener, sink)
        if fr.error:
            errors.append(fr.error)
        working = fr.working_path
        notes = fr.notes

        # ---- Step 2: Read + style ----
        sr: StyleResult = style_step(cfg, working, self._deps.reader, self._deps.styler, sink)
        if sr.error:
            errors.append(sr.error)
        doc = sr.doc

        # ---- Step 3: Segmentation ----
        segments: list[Segment] = []
        seg_r: SegmentResult = segment_step(cfg, working, self._deps.segmenter, sink)
        if seg_r.error:
            errors.append(seg_r.error)
        else:
            segments = seg_r.segments

        # ---- Step 4: AI (optional, injected placeholder) ----
        if self._deps.ai is not None:
            sink.emit("INFO", "ai_present", {"impl": self._deps.ai.__class__.__name__})

        # ---- Step 5: Finalize (write + cleanup) ----
        fz: FinalizeResult = finalize_step(cfg, doc, working, self._deps.writer, sink)
        if fz.error:
            errors.append(fz.error)

        # ---- Step 6: TOC update (optional) ----
        tc: TocResult = toc_step(cfg, fz.out_path, self._deps.toc_updater, sink)
        if tc.error:
            errors.append(tc.error)

        secs = perf_counter() - t0
        sink.emit("INFO", "done", {"notes": len(notes), "seconds": round(secs, 2)})
        return RunReport(
            out_path=fz.out_path,
            notes=notes,
            segments=segments,
            seconds=secs,
            errors=errors,
        )
