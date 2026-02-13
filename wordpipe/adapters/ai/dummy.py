from __future__ import annotations


class DummySummarizer:
    """Offline placeholder summarizer."""

    def __init__(self, max_chars: int = 400):
        self.max_chars = max_chars

    def summarize(self, text: str) -> str:
        t = (text or "").strip()
        if not t:
            return ""
        if len(t) <= self.max_chars:
            return t
        return t[: self.max_chars].rstrip() + "..."

