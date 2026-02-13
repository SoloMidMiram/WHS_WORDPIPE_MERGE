from __future__ import annotations

from pathlib import Path
from typing import Optional, Protocol

from wordpipe.core.datatypes import ChangeNote


class Flattener(Protocol):
    def flatten(
        self, input_docx: Path, output_docx: Path, *, limit_pages: Optional[int] = None
    ) -> list[ChangeNote]: ...


class TocUpdater(Protocol):
    def update(self, docx_path: Path) -> None: ...

