"""Minimal public API surface for WordPipe.

Import-safety rule:
- `import wordpipe` must succeed with only the standard library available.
- Optional dependencies (docx, openai, etc.) must be imported lazily at call time.
"""

from __future__ import annotations

from typing import Optional

from wordpipe.core.datatypes import ChangeNote, PipelineConfig, RunReport, Segment


def process_docx_v3(cfg: PipelineConfig, logger=None, jsonl_path: Optional[str] = None) -> RunReport:
    # Lazy import to keep `import wordpipe` dependency-light.
    from wordpipe.orchestrator import process_docx_v3 as _impl

    return _impl(cfg, logger=logger, jsonl_path=jsonl_path)


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
    from wordpipe.orchestrator import process_docx_v3_simple as _impl

    return _impl(
        in_path=in_path,
        out_path=out_path,
        do_flatten=do_flatten,
        prefer_win32=prefer_win32,
        per_segment_tables=per_segment_tables,
        ai_client=ai_client,
        ai_headings=ai_headings,
        ai_rewrite=ai_rewrite,
        logger=logger,
        jsonl_path=jsonl_path,
        limit_pages=limit_pages,
        max_rewrite_per_section=max_rewrite_per_section,
    )


__all__ = ["ChangeNote", "Segment", "PipelineConfig", "RunReport", "process_docx_v3", "process_docx_v3_simple"]
