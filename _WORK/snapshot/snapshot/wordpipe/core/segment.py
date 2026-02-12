# =================================
# file: wordpipe/core/segment.py
# =================================
from docx import Document
from wordpipe.core.datatypes import Segment
from wordpipe.core.ooxml import find_xml_boundaries
from wordpipe.core.styles import ensure_styles


def build_hpath(doc: Document, p_idx: int) -> tuple[str, str, str | None]:
    h1 = h2 = h3 = None
    h1_index = None
    counter = 0
    for j in range(0, p_idx + 1):
        p = doc.paragraphs[j]
        s = p.style.name if p.style else ""
        if s.startswith("Heading 1"):
            counter += 1
            h1 = p.text.strip()
            h1_index = counter
        elif s.startswith("Heading 2") and not h2:
            h2 = p.text.strip()
        elif s.startswith("Heading 3") and not h3:
            h3 = p.text.strip()
    h1 = h1 or "(No H1)"
    parts = [f"H1: {h1}"]
    if h2:
        parts.append(f"H2: {h2}")
    if h3:
        parts.append(f"H3: {h3}")
    bk = f"H1_{h1_index}" if h1_index is not None else None
    return h1, " > ".join(parts), bk


def segment_document(docx_path: str) -> list[Segment]:
    doc = Document(docx_path)
    ensure_styles(doc)
    h1_starts = [
        i
        for i, p in enumerate(doc.paragraphs)
        if p.style and p.style.name.startswith("Heading 1")
    ]
    xml_cuts = find_xml_boundaries(docx_path)
    cuts = sorted(set(h1_starts) | set(xml_cuts)) if h1_starts else xml_cuts
    cuts = [c for c in cuts if c < len(doc.paragraphs)]
    if not cuts:
        cuts = [0]
    cuts.append(len(doc.paragraphs))
    segs: list[Segment] = []
    for a, b in zip(cuts, cuts[1:]):
        h1_title, hpath, bk = build_hpath(doc, a)
        segs.append(Segment(a, b, h1_title, hpath, bk))
    return segs
