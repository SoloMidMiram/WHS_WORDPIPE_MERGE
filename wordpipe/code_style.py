# =========================================
# file: wordpipe/pipeline/code_style.py
# =========================================
import re
from docx import Document
from wordpipe.config import CODE_STYLE, CHANGE_LOG_HEADING_STYLE
from wordpipe.events import EventSink

_CODE_KEYWORDS = (
    r"\b(def|class|import|using|package|public |private |SELECT|INSERT|UPDATE|DELETE)\b"
)
_CODE_SYMBOLS = r"[{}();`]|::|->|=>"
CODE_LINE_RE = re.compile(rf"^.*({_CODE_KEYWORDS}|{_CODE_SYMBOLS}).*$")
MIN_CODE_RUN = 3


def _looks_like_code_line(s: str) -> bool:
    if not s or len(s) < 3:
        return False
    if s.strip().startswith("```"):
        return True
    return bool(CODE_LINE_RE.search(s))


def style_code_blocks(
    doc: Document, min_run: int = MIN_CODE_RUN, sink: EventSink | None = None
) -> None:
    in_fence = False
    run_buf = []
    style_failures = 0

    def flush():
        nonlocal run_buf, in_fence, style_failures
        if in_fence or len(run_buf) >= min_run:
            for p in run_buf:
                try:
                    p.style = CODE_STYLE
                except Exception:
                    style_failures += 1
        run_buf = []

    for p in doc.paragraphs:
        t = (p.text or "").rstrip()
        if t.strip().startswith("```"):
            in_fence = not in_fence
            p.text = ""
            flush()
            continue
        name = getattr(getattr(p, "style", None), "name", "") or ""
        if name.lower().startswith("heading") or name == CHANGE_LOG_HEADING_STYLE:
            flush()
            continue
        if in_fence or _looks_like_code_line(t):
            run_buf.append(p)
        else:
            flush()
    flush()

    if sink is not None and style_failures:
        sink.emit(
            "WARNING",
            "code_style_apply_failed",
            {"failures": style_failures, "code_style": CODE_STYLE},
        )
