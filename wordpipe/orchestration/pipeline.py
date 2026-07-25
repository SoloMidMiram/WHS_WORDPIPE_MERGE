"""Interfaces-only pipeline orchestrator using pluggable steps."""

from __future__ import annotations

from dataclasses import asdict, dataclass
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
    unit-testable in isolation. Recoverable errors are collected into
    ``RunReport.errors``; read/style failures are fatal because downstream
    steps require a valid in-memory document.
    """

    def __init__(self, deps: OrchestrationDeps):
        self._deps = deps

    def run(self, cfg: PipelineConfig) -> RunReport:
        sink: EventSink = self._deps.logger or NullSink()  # type: ignore[assignment]
        t0 = perf_counter()
        sink.emit("INFO", "start", {k: str(v) for k, v in asdict(cfg).items()})

        errors: list[str] = []

        # ---- Step 1: Flatten (optional) ----
        fr: FlattenResult = flatten_step(cfg, self._deps.flattener, sink)
        if fr.error:
            errors.append(fr.error)
            # Abort immediately on flatten failure — do not continue with original
            # input or create/overwrite any output.
            work_artifact = Path(str(cfg.out_path) + ".work.docx")
            if work_artifact.exists():
                work_artifact.unlink()
            secs = perf_counter() - t0
            sink.emit("ERROR", "flatten_fatal", {"seconds": round(secs, 2)})
            sink.emit("INFO", "done", {"notes": 0, "seconds": round(secs, 2)})
            return RunReport(
                out_path=cfg.out_path,
                notes=[],
                segments=[],
                seconds=secs,
                errors=errors,
            )
        else:
            working = fr.working_path
        notes = fr.notes

        # ---- Step 2: Read + style (critical - fail fast) ----
        sr: StyleResult = style_step(cfg, working, self._deps.reader, self._deps.styler, sink)
        if sr.error:
            errors.append(sr.error)
            secs = perf_counter() - t0
            sink.emit("ERROR", "fatal_style_failure", {"seconds": round(secs, 2)})
            sink.emit("INFO", "done", {"notes": len(notes), "seconds": round(secs, 2)})
            return RunReport(
                out_path=cfg.out_path,
                notes=notes,
                segments=[],
                seconds=secs,
                errors=errors,
            )
        doc = sr.doc
        if doc is None:
            errors.append("style_step returned doc=None without error")
            secs = perf_counter() - t0
            sink.emit("WARN", "aborted", {"reason": "style_step returned None", "seconds": round(secs, 2)})
            return RunReport(
                out_path=cfg.out_path,
                notes=notes,
                segments=[],
                seconds=secs,
                errors=errors,
            )

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
            secs = perf_counter() - t0
            sink.emit("WARN", "aborted", {"reason": "finalize_step failed", "seconds": round(secs, 2)})
            return RunReport(
                out_path=cfg.out_path,
                notes=notes,
                segments=segments,
                seconds=secs,
                errors=errors,
            )

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
