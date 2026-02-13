from __future__ import annotations

from typing import Protocol


class AISummarizer(Protocol):
    def summarize(self, text: str) -> str: ...

