"""Compatibility wrapper for the legacy import path.

This module must remain import-safe when optional dependencies are not installed.
"""

from __future__ import annotations

from typing import Optional

from wordpipe.core.datatypes import PipelineConfig, RunReport


def process_docx_v3(cfg: PipelineConfig, logger=None, jsonl_path: Optional[str] = None) -> RunReport:
    from wordpipe.orchestrator import process_docx_v3 as _impl

    return _impl(cfg, logger=logger, jsonl_path=jsonl_path)


def process_docx_v3_simple(**kwargs):
    from wordpipe.orchestrator import process_docx_v3_simple as _impl

    return _impl(**kwargs)


__all__ = ["process_docx_v3", "process_docx_v3_simple"]
