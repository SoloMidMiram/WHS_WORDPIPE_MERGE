# ================================
# file: wordpipe/core/styles.py
# ================================
from docx import Document
from docx.shared import Pt
from wordpipe.config import (
    CHANGE_NOTE_STYLE,
    CHANGE_LOG_HEADING_STYLE,  # ← add this
    CODE_STYLE,
    ENTRY_DATE_STYLE,
    AI_HEADING_STYLE,
    KEYWORD_STYLE,
)


def ensure_styles(doc: Document) -> None:
    """Create styles if missing. Safe to call multiple times."""
    existing = {s.name for s in doc.styles}

    def mk(
        name: str,
        *,
        base: str = "Normal",
        font: str = "Calibri",
        size: int = 10,
        bold=False,
        italic=False,
    ):
        if name in existing:
            return
        try:
            st = doc.styles.add_style(name, 1)  # paragraph style
            st.base_style = doc.styles[base]
            st.font.name = font
            st.font.size = Pt(size)
            st.font.bold = bold
            st.font.italic = italic
        except Exception:
            pass

    mk(CHANGE_NOTE_STYLE, size=9, italic=True)
    mk(CHANGE_LOG_HEADING_STYLE, base="Heading 2", size=12, bold=True)
    mk(AI_HEADING_STYLE, base="Heading 2")
    mk(KEYWORD_STYLE, size=10, bold=True)
    mk(CODE_STYLE, base="Normal", font="Consolas", size=9)
    mk(ENTRY_DATE_STYLE, size=11, italic=True)
