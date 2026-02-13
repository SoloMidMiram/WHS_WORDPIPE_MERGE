from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from wordpipe.core.datatypes import ChangeNote


class LegacyFlattenerAdapter:
    """Adapter from the historical flattener API (`run`) to `Flattener.flatten`."""

    def __init__(self, legacy_flattener):
        self._legacy = legacy_flattener

    def flatten(
        self, input_docx: Path, output_docx: Path, *, limit_pages: Optional[int] = None
    ) -> list[ChangeNote]:
        return self._legacy.run(input_docx, output_docx, limit_pages=limit_pages)


class Win32MergedpipelineV3TocUpdater:
    """Optional TOC updater for Windows environments with legacy integration."""

    def update(self, docx_path: Path) -> None:
        if not sys.platform.startswith("win"):
            return
        try:
            from MergedpipelineV3 import update_tocs_win32  # type: ignore
        except Exception:
            return
        try:
            update_tocs_win32(str(docx_path))
        except Exception:
            return

