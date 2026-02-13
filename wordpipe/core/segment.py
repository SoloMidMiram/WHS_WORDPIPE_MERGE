"""Deprecated: DOCX segmentation is an adapter, not core logic.

Use `wordpipe.adapters.docx.DocxSegmenter` instead.
"""

from __future__ import annotations

from wordpipe.core.datatypes import Segment


def segment_document(_docx_path: str) -> list[Segment]:
    raise RuntimeError(
        "wordpipe.core.segment.segment_document is no longer part of the core layer. "
        "Use wordpipe.adapters.docx.DocxSegmenter().segment(Path(...))."
    )

