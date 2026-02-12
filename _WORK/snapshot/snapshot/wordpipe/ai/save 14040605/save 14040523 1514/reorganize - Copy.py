# ai/reorganize.py — stand-alone re-org using AI comprehension
# Flow per chunk:
#   1) Add timestamp banner (Tehran/Jalali).
#   2) Ask AI to analyze a chunk sample → heading + keypoints (bullets).
#   3) For each paragraph, ask AI to analyze → text + style (+optional heading).
#   4) Append a footnote with same Tehran/Jalali line.
#
# Notes:
# - We keep writing simple: no run-level cloning. Safe, portable.
# - Bullets: we prefix "• " and apply AI_BULLET_STYLE (created below).
# - Always sanitize text with xml_safe() before inserting.

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

from timefmt import tehran_timestamp_line
from chunker import chunk_ranges_by_page_breaks, chunk_preview
from helpers import AIProvider, AnalysisOut


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
    "Body": None,  # default paragraph style
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
) -> str:
    """AI-driven re-organization with comprehension & styling.”

    Args:
        in_path:  source .docx
        out_path: destination .docx (will be overwritten)
        ai:       AIProvider (OpenAI or Dummy). If None, no AI changes applied.
        cap_per_chunk: max paragraphs to rewrite per chunk (budget control)
    """
    src = Document(in_path)
    dst = Document()
    _ensure_styles(dst)

    # Prepare chunk list using page breaks
    chunks = chunk_ranges_by_page_breaks(src)
    now = datetime.utcnow()

    for idx, (start, end) in enumerate(chunks, start=1):
        # 1) Timestamp banner
        banner = tehran_timestamp_line(now)
        p = dst.add_paragraph(banner)
        try:
            p.style = "ENTRY_DATE_STYLE"
        except Exception:
            pass

        # 2) Chunk-level comprehension (heading + keypoints)
        if ai:
            # Use first ~10 paragraphs of the chunk as a summary context
            sample_lines = []
            for psrc in src.paragraphs[start : min(end, start + 10)]:
                t = (psrc.text or "").strip()
                if t:
                    sample_lines.append(t)
            sample_text = "\n".join(sample_lines)[:6000]

            if sample_text:
                # Analyze the chunk to produce a top H2 + bullets
                chunk_analysis: AnalysisOut | None = ai.analyze(sample_text)
                if chunk_analysis:
                    if chunk_analysis.heading:
                        h = dst.add_paragraph(xml_safe(chunk_analysis.heading))
                        try:
                            h.style = "AI_HEADING_STYLE"
                        except Exception:
                            pass
                    # Keypoints as bullets
                    for bp in chunk_analysis.keypoints or []:
                        bl = dst.add_paragraph("• " + xml_safe(bp))
                        try:
                            bl.style = "AI_BULLET_STYLE"
                        except Exception:
                            pass

        # 3) Paragraph-level comprehension & rewrite (capped)
        rewrites_left = cap_per_chunk
        for psrc in src.paragraphs[start:end]:
            text_in = psrc.text or ""
            if ai and text_in.strip() and rewrites_left > 0:
                analysis = ai.analyze(text_in)
                if analysis:
                    # Optional inline heading for this paragraph (rare; short)
                    if analysis.heading:
                        h2 = dst.add_paragraph(xml_safe(analysis.heading))
                        try:
                            h2.style = "AI_HEADING_STYLE"
                        except Exception:
                            pass

                    # Paragraph text + style
                    out_txt = xml_safe(analysis.text)
                    pnew = dst.add_paragraph(out_txt)
                    try:
                        sname = STYLE_MAP.get(analysis.style)
                        if sname:
                            pnew.style = sname
                        if analysis.style == "Bullet" and not out_txt.startswith("• "):
                            pnew.text = "• " + pnew.text
                    except Exception:
                        pass

                    # Optional inline bullets from paragraph analysis (if any)
                    for bp in analysis.keypoints or []:
                        bl = dst.add_paragraph("• " + xml_safe(bp))
                        try:
                            bl.style = "AI_BULLET_STYLE"
                        except Exception:
                            pass

                    rewrites_left -= 1
                    continue

            # No AI or no rewrite: copy as-is (sanitized)
            dst.add_paragraph(xml_safe(text_in))

        # Spacer between chunks
        dst.add_paragraph("")

    # 4) Footer footnote (your fixed convention)
    foot = dst.add_paragraph("FootNote — Tehran (IRDT) vs London (BST):")
    foot.alignment = WD_ALIGN_PARAGRAPH.LEFT
    foot2 = dst.add_paragraph(tehran_timestamp_line(now))
    foot2.alignment = WD_ALIGN_PARAGRAPH.LEFT

    dst.save(out_path)
    return out_path
