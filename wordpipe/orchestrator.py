# ============================================
# file: wordpipe/pipeline/orchestrator.py
# ============================================
from __future__ import annotations
from pathlib import Path
from typing import Optional
from time import perf_counter
from docx import Document
from wordpipe.core.datatypes import ChangeNote, PipelineConfig, RunReport
from wordpipe.core.styles import ensure_styles
from wordpipe.core.segment import segment_document
from wordpipe.code_style import style_code_blocks
from wordpipe.flatteners.base import make_flattener
from wordpipe.logging_tools import evt


# Use your existing COM TOC updater while migrating
try:
    from MergedpipelineV3 import update_tocs_win32  # noqa: F401
except Exception:  # pragma: no cover

    def update_tocs_win32(_):
        pass


def process_docx_v3(
    cfg: PipelineConfig, logger=None, jsonl_path: Optional[str] = None
) -> RunReport:
    t0 = perf_counter()
    evt(
        logger,
        jsonl_path,
        "INFO",
        "start",
        **{k: str(v) for k, v in cfg.__dict__.items()},
    )

    working = Path(cfg.in_path)
    notes: list[ChangeNote] = []

    # 1) Flatten
    if cfg.do_flatten:
        tmp = Path(str(cfg.out_path) + ".work.docx")
        fl = make_flattener(cfg.prefer_win32)
        try:
            evt(
                logger,
                jsonl_path,
                "INFO",
                "flatten_begin",
                mode=fl.__class__.__name__,
                limit_pages=cfg.limit_pages,
            )
            notes = fl.run(working, tmp, limit_pages=cfg.limit_pages)
            evt(
                logger,
                jsonl_path,
                "INFO",
                "flatten_done",
                mode=fl.__class__.__name__,
                notes=len(notes),
            )
            working = tmp
        except Exception as e:
            evt(logger, jsonl_path, "WARNING", "flatten_fail", error=str(e))
            from wordpipe.flatteners.xml_flattener import XmlFlattener

            fl = XmlFlattener()
            notes = fl.run(Path(cfg.in_path), tmp, limit_pages=cfg.limit_pages)
            working = tmp

    # 2) Styles + code formatting
    doc = Document(str(working))
    ensure_styles(doc)
    style_code_blocks(doc)

    # 3) Segmentation
    segments = segment_document(str(working))

    # TODO: 4) AI (optional) – inject AIProvider when you’re ready
    # TODO: 5) Per‑segment tables – reuse v3 logic; ensure xml_safe() on writes

    # 6) Save + clean
    doc.save(str(cfg.out_path))
    if working != cfg.in_path:
        try:
            Path(working).unlink()
        except OSError:
            pass
    try:
        update_tocs_win32(str(cfg.out_path))
    except Exception:
        pass

    secs = perf_counter() - t0
    evt(logger, jsonl_path, "INFO", "done", notes=len(notes), seconds=round(secs, 2))
    return RunReport(
        out_path=Path(cfg.out_path), notes=notes, segments=segments, seconds=secs
    )


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
    """Back‑compat shim that mirrors your current loader call.
    Prefer the PipelineConfig + RunReport API going forward.
    """
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
