from __future__ import annotations

import sys
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
from wordpipe.adapters.flatteners.base import (
    _UnavailableFlattener,
    _can_import_mergedpipeline,
    make_flattener,
)
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

    # Preflight: if flattening was requested but the flattener is unavailable,
    # fail immediately before any processing or output creation.
    if cfg.do_flatten and isinstance(fl, _UnavailableFlattener):
        raise RuntimeError(
            f"Flattening requested but {fl._reason} "
            "(set do_flatten=False or --no-flatten to skip)"
        )

    fl_adapter = LegacyFlattenerAdapter(fl) if fl is not None else None

    # TOC updater requires MergedpipelineV3 on Windows; skip when absent.
    has_legacy = sys.platform.startswith("win") and _can_import_mergedpipeline()

    return OrchestrationDeps(
        reader=DocxDocumentReader(),
        writer=DocxDocumentWriter(),
        styler=DocxStyler(),
        segmenter=DocxSegmenter(),
        logger=sink,
        flattener=fl_adapter,
        toc_updater=Win32MergedpipelineV3TocUpdater() if has_legacy else None,
        ai=None,
    )
