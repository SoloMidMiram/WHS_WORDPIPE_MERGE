from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from wordpipe.core.datatypes import ChangeNote, PipelineConfig, RunReport, Segment
from wordpipe.interfaces.ai import AISummarizer
from wordpipe.interfaces.documents import (
    DocumentReader,
    DocumentSegmenter,
    DocumentStyler,
    DocumentWriter,
)
from wordpipe.interfaces.logging import Logger
from wordpipe.interfaces.transforms import Flattener, TocUpdater


class _NullLogger:
    def emit(self, level: str, event: str, fields: dict) -> None:
        return


@dataclass(slots=True)
class OrchestrationDeps:
    reader: DocumentReader
    writer: DocumentWriter
    styler: DocumentStyler
    segmenter: DocumentSegmenter
    logger: Logger | None = None
    flattener: Flattener | None = None
    toc_updater: TocUpdater | None = None
    ai: AISummarizer | None = None


class WordPipePipeline:
    """Core pipeline orchestrator (interfaces-only, dependency-injected)."""

    def __init__(self, deps: OrchestrationDeps):
        self._deps = deps

    def run(self, cfg: PipelineConfig) -> RunReport:
        sink: Logger = self._deps.logger or _NullLogger()
        t0 = perf_counter()
        sink.emit("INFO", "start", {k: str(v) for k, v in cfg.__dict__.items()})

        working = Path(cfg.in_path)
        notes: list[ChangeNote] = []

        # 1) Flatten (optional)
        if cfg.do_flatten and self._deps.flattener is not None:
            tmp = Path(str(cfg.out_path) + ".work.docx")
            try:
                sink.emit(
                    "INFO",
                    "flatten_begin",
                    {
                        "mode": self._deps.flattener.__class__.__name__,
                        "limit_pages": cfg.limit_pages,
                    },
                )
                notes = self._deps.flattener.flatten(
                    working, tmp, limit_pages=cfg.limit_pages
                )
                sink.emit(
                    "INFO",
                    "flatten_done",
                    {
                        "mode": self._deps.flattener.__class__.__name__,
                        "notes": len(notes),
                    },
                )
                working = tmp
            except Exception as e:
                sink.emit("WARNING", "flatten_fail", {"error": str(e)})

        # 2) Read + style
        doc = self._deps.reader.read(working)
        self._deps.styler.ensure_styles(doc, logger=sink)
        self._deps.styler.style_code_blocks(doc, logger=sink)

        # 3) Segmentation
        segments: list[Segment] = self._deps.segmenter.segment(working)

        # 4) AI (optional) - injected, but intentionally no default behavior yet.
        if self._deps.ai is not None:
            sink.emit("INFO", "ai_present", {"impl": self._deps.ai.__class__.__name__})

        # 5) Save + cleanup
        self._deps.writer.write(doc, Path(cfg.out_path))
        if working != Path(cfg.in_path):
            try:
                working.unlink()
            except OSError:
                pass
        if self._deps.toc_updater is not None:
            try:
                self._deps.toc_updater.update(Path(cfg.out_path))
            except Exception as e:
                sink.emit("WARNING", "toc_update_fail", {"error": str(e)})

        secs = perf_counter() - t0
        sink.emit("INFO", "done", {"notes": len(notes), "seconds": round(secs, 2)})
        return RunReport(
            out_path=Path(cfg.out_path),
            notes=notes,
            segments=segments,
            seconds=secs,
        )

