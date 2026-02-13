from __future__ import annotations

from typing import Any, Protocol


class Logger(Protocol):
    """Structured event emitter interface (TraceLedger-friendly)."""

    def emit(self, level: str, event: str, fields: dict[str, Any]) -> None: ...

