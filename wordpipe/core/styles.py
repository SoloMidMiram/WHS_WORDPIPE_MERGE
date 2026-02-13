"""Deprecated: DOCX style helpers are adapters, not core logic.

Use `wordpipe.adapters.docx.DocxStyler` instead.
"""

from __future__ import annotations

from typing import Any


def ensure_styles(_doc: Any) -> None:
    raise RuntimeError(
        "wordpipe.core.styles.ensure_styles is no longer part of the core layer. "
        "Use wordpipe.adapters.docx.DocxStyler().ensure_styles(doc)."
    )

