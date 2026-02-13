from __future__ import annotations

from pathlib import Path
from typing import Any


class DocxDocumentReader:
    def read(self, path: Path) -> Any:
        # Lazy import: python-docx is an optional dependency.
        from docx import Document

        return Document(str(path))


class DocxDocumentWriter:
    def write(self, doc: Any, path: Path) -> None:
        doc.save(str(path))

