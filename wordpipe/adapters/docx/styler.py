from __future__ import annotations

from typing import Any

from wordpipe.config import (
    AI_HEADING_STYLE,
    CHANGE_LOG_HEADING_STYLE,
    CHANGE_NOTE_STYLE,
    CODE_STYLE,
    ENTRY_DATE_STYLE,
    KEYWORD_STYLE,
)
from wordpipe.interfaces.logging import Logger


class DocxStyler:
    def ensure_styles(self, doc: Any, *, logger: Logger | None = None) -> None:
        """Create styles if missing. Safe to call multiple times."""
        # Lazy import: python-docx is an optional dependency.
        from docx.shared import Pt

        existing = {s.name for s in doc.styles}
        failures = 0

        def mk(
            name: str,
            *,
            base: str = "Normal",
            font: str = "Calibri",
            size: int = 10,
            bold: bool = False,
            italic: bool = False,
        ) -> None:
            nonlocal failures
            if name in existing:
                return
            try:
                st = doc.styles.add_style(name, 1)  # paragraph style
                st.base_style = doc.styles[base]
                st.font.name = font
                st.font.size = Pt(size)
                st.font.bold = bold
                st.font.italic = italic
                existing.add(name)
            except Exception:
                failures += 1

        mk(CHANGE_NOTE_STYLE, size=9, italic=True)
        mk(CHANGE_LOG_HEADING_STYLE, base="Heading 2", size=12, bold=True)
        mk(AI_HEADING_STYLE, base="Heading 2")
        mk(KEYWORD_STYLE, size=10, bold=True)
        mk(CODE_STYLE, base="Normal", font="Consolas", size=9)
        mk(ENTRY_DATE_STYLE, size=11, italic=True)

        if logger is not None and failures:
            logger.emit("WARNING", "ensure_styles_failed", {"failures": failures})

    def style_code_blocks(self, doc: Any, *, logger: Logger | None = None) -> None:
        from wordpipe.code_style import style_code_blocks

        # `Logger` matches the `EventSink` shape (emit(level, event, fields)).
        style_code_blocks(doc, sink=logger)  # type: ignore[arg-type]

