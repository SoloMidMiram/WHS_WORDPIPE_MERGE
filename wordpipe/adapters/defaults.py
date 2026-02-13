from __future__ import annotations

from typing import Optional

from wordpipe.adapters.docx import (
    DocxDocumentReader,
    DocxDocumentWriter,
    DocxSegmenter,
    DocxStyler,
)
from wordpipe.adapters.transforms import LegacyFlattenerAdapter, Win32MergedpipelineV3TocUpdater
from wordpipe.core.datatypes import PipelineConfig
from wordpipe.events import make_sink
from wordpipe.adapters.flatteners.base import make_flattener
from wordpipe.orchestration.pipeline import OrchestrationDeps


def build_default_deps(
    cfg: PipelineConfig, *, logger=None, jsonl_path: Optional[str] = None
) -> OrchestrationDeps:
    """Default dependency wiring for "docx + optional legacy flattening".

    This is a composition helper for convenience entrypoints. TraceLedger (or any
    embedding app) should typically provide its own dependencies and sink.
    """

    sink = make_sink(logger=logger, jsonl_path=jsonl_path)
    fl = make_flattener(cfg.prefer_win32) if cfg.do_flatten else None
    fl_adapter = LegacyFlattenerAdapter(fl) if fl is not None else None

    return OrchestrationDeps(
        reader=DocxDocumentReader(),
        writer=DocxDocumentWriter(),
        styler=DocxStyler(),
        segmenter=DocxSegmenter(),
        logger=sink,
        flattener=fl_adapter,
        toc_updater=Win32MergedpipelineV3TocUpdater(),
        ai=None,
    )
