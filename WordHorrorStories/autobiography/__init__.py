from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

from docx import Document

from .collection import LogCollection
from .config import DocxConfig
from .docx_builder import builder_for_config
from .log_reader import LogFileReader
from .models import LogEntry

__all__ = [
  'DocxConfig',
  'LogEntry',
  'LogCollection',
  'LogFileReader',
  'build_autobiography_from_logs',
]


def build_autobiography_from_logs(
  jsonl_paths: Sequence[Path | str],
  *,
  base_doc: Optional[Document] = None,
  config: Optional[DocxConfig] = None,
) -> Document:
  """High level helper to build or append to an autobiography document."""
  cfg = config or DocxConfig()
  reader = LogFileReader(jsonl_paths)
  collection = LogCollection(reader).unique().sort_by_iso()
  grouped = collection.group_by(cfg.group_field)
  builder = builder_for_config(cfg)
  return builder.build_document(grouped, base_doc)
