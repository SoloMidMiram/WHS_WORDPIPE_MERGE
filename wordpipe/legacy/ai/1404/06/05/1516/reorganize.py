# ai/reorganize.py — AI comprehension + styling with JSONL logging
from __future__ import annotations
from datetime import datetime

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

from timefmt import tehran_timestamp_line
from chunker import chunk_ranges_by_page_breaks
from helpers import AIProvider, AnalysisOut
from logging_tools import evt


# ---- XML sanitizer ----------------------------------------------------------
def xml_safe(s: str) -> str:
    if not s:
        return ""
    return "".join(ch for ch in s if ch >= " " or ch in "\t\r\n")


# ---- Styles -----------------------------------------------------------------
def _ensure_styles(doc: Document) -> None:
    styles = doc.styles
    if "ENTRY_DATE_STYLE" not in [s.name for s in styles]:
        s = styles.add_style("ENTRY_DATE_STYLE", WD_STYLE_TYPE.PARAGRAPH)
        s.font.name, s.font.size = "Calibri", Pt(12)
        s.font.bold = True
    if "AI_HEADING_STYLE" not in [s.name for s in styles]:
        s = styles.add_style("AI_HEADING_STYLE", WD_STYLE_TYPE.PARAGRAPH)
        s.font.name, s.font.size = "Calibri", Pt(12)
        s.font.bold = True
        s.font.italic = True
    if "AI_CODE_STYLE" not in [s.name for s in styles]:
        s = styles.add_style("AI_CODE_STYLE", WD_STYLE_TYPE.PARAGRAPH)
        s.font.name, s.font.size = "Consolas", Pt(10.5)
    if "AI_QUOTE_STYLE" not in [s.name for s in styles]:
        s = styles.add_style("AI_QUOTE_STYLE", WD_STYLE_TYPE.PARAGRAPH)
        s.font.italic, s.font.size = True, Pt(11)
    if "AI_BULLET_STYLE" not in [s.name for s in styles]:
        s = styles.add_style("AI_BULLET_STYLE", WD_STYLE_TYPE.PARAGRAPH)
        s.font.name, s.font.size = "Calibri", Pt(11)


STYLE_MAP = {
    "Body": None,
    "Code": "AI_CODE_STYLE",
    "Quote": "AI_QUOTE_STYLE",
    "Bullet": "AI_BULLET_STYLE",
}


# ---- Core API ---------------------------------------------------------------
def reorganize_document(
    in_path: str,
    out_path: str,
    ai: AIProvider | None = None,
    *,
    cap_per_chunk: int = 8,
    logger=None,
    jsonl_path: str | None = None,
) -> str:
    """AI-driven re-organization with comprehension & styling."""
    src = Document(in_path)
    dst = Document()
    _ensure_styles(dst)

    chunks = chunk_ranges_by_page_breaks(src)
    now = datetime.utcnow()

    evt(logger, jsonl_path, "INFO", "doc_begin", chunks=len(chunks))

    for idx, (start, end) in enumerate(chunks, start=1):
        section_id = f"chunk-{idx}"
        evt(
            logger,
            jsonl_path,
            "INFO",
            "chunk_begin",
            section=section_id,
            start=start,
            end=end,
        )

        # 1) Timestamp banner
        banner = tehran_timestamp_line(now)
        p = dst.add_paragraph(banner)
        try:
            p.style = "ENTRY_DATE_STYLE"
        except Exception:
            pass

        # 2) Chunk-level comprehension
        if ai:
            sample_lines = []
            for psrc in src.paragraphs[start : min(end, start + 10)]:
                t = (psrc.text or "").strip()
                if t:
                    sample_lines.append(t)
            sample_text = "\n".join(sample_lines)[:6000]
            if sample_text:
                chunk_analysis: AnalysisOut | None = ai.analyze(sample_text)
                if chunk_analysis:
                    evt(
                        logger,
                        jsonl_path,
                        "INFO",
                        "chunk_heading",
                        section=section_id,
                        heading=chunk_analysis.heading,
                        points=len(chunk_analysis.keypoints or []),
                    )
                    if chunk_analysis.heading:
                        h = dst.add_paragraph(xml_safe(chunk_analysis.heading))
                        try:
                            h.style = "AI_HEADING_STYLE"
                        except Exception:
                            pass
                    for bp in chunk_analysis.keypoints or []:
                        bl = dst.add_paragraph("• " + xml_safe(bp))
                        try:
                            bl.style = "AI_BULLET_STYLE"
                        except Exception:
                            pass

        # 3) Paragraph-level comprehension & rewrite (capped by cap_per_chunk and provider meter)
        rewrites_left = cap_per_chunk
        provider_meter = getattr(ai, "meter", None) if ai else None

        for psrc in src.paragraphs[start:end]:
            text_in = psrc.text or ""
            if ai and text_in.strip() and rewrites_left > 0:
                # honor provider per-section cap if present
                if provider_meter and hasattr(provider_meter, "section_can_rewrite"):
                    if not provider_meter.section_can_rewrite(section_id):
                        evt(logger, jsonl_path, "INFO", "cap_hit", section=section_id)
                        ai_allowed = False
                    else:
                        ai_allowed = True
                else:
                    ai_allowed = True

                if ai_allowed:
                    analysis = ai.analyze(text_in)
                    if analysis:
                        evt(
                            logger,
                            jsonl_path,
                            "INFO",
                            "para_rewrite",
                            section=section_id,
                            style=analysis.style,
                        )
                        if analysis.heading:
                            h2 = dst.add_paragraph(xml_safe(analysis.heading))
                            try:
                                h2.style = "AI_HEADING_STYLE"
                            except Exception:
                                pass
                        out_txt = xml_safe(analysis.text)
                        pnew = dst.add_paragraph(out_txt)
                        try:
                            sname = STYLE_MAP.get(analysis.style)
                            if sname:
                                pnew.style = sname
                            if analysis.style == "Bullet" and not out_txt.startswith(
                                "• "
                            ):
                                pnew.text = "• " + pnew.text
                        except Exception:
                            pass
                        for bp in analysis.keypoints or []:
                            bl = dst.add_paragraph("• " + xml_safe(bp))
                            try:
                                bl.style = "AI_BULLET_STYLE"
                            except Exception:
                                pass
                        rewrites_left -= 1
                        if provider_meter and hasattr(
                            provider_meter, "note_section_rewrite"
                        ):
                            provider_meter.note_section_rewrite(section_id)
                        continue

            # No AI or cap reached: copy sanitized
            dst.add_paragraph(xml_safe(text_in))

        dst.add_paragraph("")
        evt(logger, jsonl_path, "INFO", "chunk_done", section=section_id)

    # 4) Footer footnote (fixed convention)
    foot = dst.add_paragraph("FootNote — Tehran (IRDT) vs London (BST):")
    foot.alignment = WD_ALIGN_PARAGRAPH.LEFT
    foot2 = dst.add_paragraph(tehran_timestamp_line(now))
    foot2.alignment = WD_ALIGN_PARAGRAPH.LEFT

    dst.save(out_path)
    evt(logger, jsonl_path, "INFO", "doc_done", out=out_path)
    return out_path
