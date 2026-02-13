"""Compatibility wrapper for the legacy import path.

This module must remain import-safe when optional dependencies are not installed.
"""

from __future__ import annotations

from typing import Any

from wordpipe.events import EventSink


def style_code_blocks(doc: Any, *args, **kwargs) -> None:
    from wordpipe.code_style import style_code_blocks as _impl

    return _impl(doc, *args, **kwargs)


__all__ = ["style_code_blocks", "EventSink"]
