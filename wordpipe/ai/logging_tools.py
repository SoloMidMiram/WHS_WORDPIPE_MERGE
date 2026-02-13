"""Compatibility wrapper for AI-side event emission.

Prefer `wordpipe.events` for new integrations.
"""

from __future__ import annotations

from typing import Optional

from wordpipe.events import make_sink


def evt(logger, jsonl_path: Optional[str], level: str, event: str, **fields) -> None:
    sink = make_sink(logger=logger, jsonl_path=jsonl_path)
    sink.emit(level, event, fields)

