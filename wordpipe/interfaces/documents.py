from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from wordpipe.core.datatypes import Segment
from wordpipe.interfaces.logging import Logger


class DocumentReader(Protocol):
    def read(self, path: Path) -> Any: ...


class DocumentWriter(Protocol):
    def write(self, doc: Any, path: Path) -> None: ...


class DocumentStyler(Protocol):
    def ensure_styles(self, doc: Any, *, logger: Logger | None = None) -> None: ...

    def style_code_blocks(self, doc: Any, *, logger: Logger | None = None) -> None: ...


class DocumentSegmenter(Protocol):
    def segment(self, path: Path) -> list[Segment]: ...

