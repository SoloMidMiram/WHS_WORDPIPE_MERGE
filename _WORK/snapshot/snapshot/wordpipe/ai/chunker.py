# ai/chunker.py — split a docx into ranges using <w:br type="page"> breaks
from __future__ import annotations
from docx import Document
import xml.etree.ElementTree as ET

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _run_has_page_break(run) -> bool:
    try:
        root = ET.fromstring(run._r.xml)
        for br in root.iter(f"{W_NS}br"):
            if br.attrib.get(f"{W_NS}type") == "page":
                return True
    except Exception:
        pass
    return False


def chunk_ranges_by_page_breaks(doc: Document) -> list[tuple[int, int]]:
    prs = doc.paragraphs
    breaks = []
    for i, p in enumerate(prs):
        if any(_run_has_page_break(r) for r in p.runs):
            breaks.append(i + 1)
    bounds = [0] + breaks + [len(prs)]
    return [(s, e) for s, e in zip(bounds[:-1], bounds[1:]) if e > s]


def chunk_preview(doc: Document, start: int, end: int) -> str:
    prs = doc.paragraphs[start:end]
    for p in prs:
        if "Heading" in (getattr(p.style, "name", "") or "") and p.text.strip():
            return p.text.strip()[:120]
    for p in prs:
        if p.text.strip():
            return p.text.strip()[:120]
    return ""
