from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional, Tuple

from wordpipe.core.datatypes import Segment
from wordpipe.core.ooxml import find_xml_boundaries


_HeadingState = Tuple[str, Optional[str], Optional[str], Optional[int]]


def _precompute_heading_states(doc: Any) -> List[_HeadingState]:
    """Single-pass precomputation of heading context for every paragraph index.

    Returns a list parallel to ``doc.paragraphs`` where each entry is
    ``(h1_title, h2_title, h3_title, h1_index_or_None)`` — the heading
    context *at* that paragraph, read left-to-right with no repeated scans.
    """
    states: list[_HeadingState] = []
    h1: Optional[str] = None
    h2: Optional[str] = None
    h3: Optional[str] = None
    h1_counter = 0
    found_h1 = False
    for p in doc.paragraphs:
        s = p.style.name if p.style else ""
        if s.startswith("Heading 1"):
            h1_counter += 1
            found_h1 = True
            h1 = p.text.strip()
            h2 = None
            h3 = None
        elif s.startswith("Heading 2"):
            h2 = p.text.strip()
            h3 = None
        elif s.startswith("Heading 3"):
            h3 = p.text.strip()
        states.append((h1 or "(No H1)", h2, h3, h1_counter if found_h1 else None))
    return states


def _build_hpath_from_state(
    h1_title: str,
    h2: Optional[str],
    h3: Optional[str],
    h1_index: Optional[int],
) -> Tuple[str, str, Optional[str]]:
    """Build (h1_title, hpath, bk) from precomputed heading state."""
    parts = [f"H1: {h1_title}"]
    if h2:
        parts.append(f"H2: {h2}")
    if h3:
        parts.append(f"H3: {h3}")
    bk = f"H1_{h1_index}" if h1_index is not None else None
    return h1_title, " > ".join(parts), bk


def _build_hpath(doc: Any, p_idx: int) -> Tuple[str, str, Optional[str]]:
    """Legacy repeated-scan builder (kept for backward compat)."""
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
            h2 = None
            h3 = None
        elif s.startswith("Heading 2"):
            h2 = p.text.strip()
            h3 = None
        elif s.startswith("Heading 3"):
            h3 = p.text.strip()
    h1 = h1 or "(No H1)"
    parts = [f"H1: {h1}"]
    if h2:
        parts.append(f"H2: {h2}")
    if h3:
        parts.append(f"H3: {h3}")
    bk = f"H1_{h1_index}" if h1_index is not None else None
    return h1, " > ".join(parts), bk


class DocxSegmenter:
    def segment(self, path: Path) -> list[Segment]:
        # Lazy import: python-docx is an optional dependency.
        from docx import Document

        from wordpipe.adapters.docx.styler import DocxStyler

        doc = Document(str(path))
        DocxStyler().ensure_styles(doc)

        h1_starts = [
            i
            for i, p in enumerate(doc.paragraphs)
            if p.style and p.style.name.startswith("Heading 1")
        ]
        xml_cuts = find_xml_boundaries(str(path))
        cuts = sorted(set(h1_starts) | set(xml_cuts)) if h1_starts else xml_cuts
        cuts = [c for c in cuts if c < len(doc.paragraphs)]
        if not cuts:
            cuts = [0]
        cuts.append(len(doc.paragraphs))

        # Precompute heading states once (O(n) single pass).
        heading_states = _precompute_heading_states(doc)

        segs: list[Segment] = []
        for a, b in zip(cuts, cuts[1:]):
            h1_title, h2, h3, h1_index = heading_states[a]
            h1_title, hpath, bk = _build_hpath_from_state(h1_title, h2, h3, h1_index)
            segs.append(Segment(a, b, h1_title, hpath, bk))
        return segs

