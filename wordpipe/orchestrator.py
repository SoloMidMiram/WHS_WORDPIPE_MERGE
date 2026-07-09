"""Convenience entrypoints for running the WordPipe pipeline.

This module is a composition root: it wires default adapters and calls the
interfaces-only orchestrator (`wordpipe.orchestration`).

Import boundary rule:
- This module must remain import-safe with only stdlib + core installed.
- Optional dependencies (python-docx, OpenAI, etc.) must be imported lazily by
  adapters at call time.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from wordpipe.adapters.defaults import build_default_deps
from wordpipe.core.datatypes import PipelineConfig, RunReport, warn_experimental_config
from wordpipe.orchestration.pipeline import WordPipePipeline


def process_docx_v3(
    cfg: PipelineConfig, logger=None, jsonl_path: Optional[str] = None
) -> RunReport:
    warn_experimental_config(cfg)
    deps = build_default_deps(cfg, logger=logger, jsonl_path=jsonl_path)
    return WordPipePipeline(deps).run(cfg)


def process_docx_v3_simple(
    *,
    in_path: str,
    out_path: str,
    do_flatten: bool = True,
    prefer_win32: bool = True,
    per_segment_tables: bool = True,
    ai_client=None,
    ai_headings: bool = False,
    ai_rewrite: bool = False,
    logger=None,
    jsonl_path: Optional[str] = None,
    limit_pages: Optional[int] = None,
    max_rewrite_per_section: int = 40,
) -> tuple[str, int]:
    """Back-compat shim that mirrors the historical loader call."""

    cfg = PipelineConfig(
        Path(in_path),
        Path(out_path),
        do_flatten,
        prefer_win32,
        per_segment_tables,
        limit_pages,
        ai_headings,
        ai_rewrite,
        max_rewrite_per_section,
    )
    rep = process_docx_v3(cfg, logger=logger, jsonl_path=jsonl_path)
    return str(rep.out_path), len(rep.notes)

