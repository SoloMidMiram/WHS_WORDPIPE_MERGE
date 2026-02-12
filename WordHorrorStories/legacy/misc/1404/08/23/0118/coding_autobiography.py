# coding_autobiography.py
from __future__ import annotations

import argparse
import json
from collections import defaultdict, OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, List, Optional

from docx import Document
from docx.enum.style import WD_STYLE_TYPE

# ─── DATA MODELS ──────────────────────────────────────────────────────────────

@dataclass
class LogEntry:
  version: str
  id: str
  session_id: str
  ts_iso: str
  ts_jalali: str
  source: str
  model: Optional[str] = None
  project_path: Optional[str] = None
  workspace: Optional[str] = None
  user: Optional[str] = None
  q_text: str = ''
  a_text: str = ''
  q_summary: Optional[str] = None
  a_summary: Optional[str] = None
  language_guess: Optional[str] = None
  tags: Optional[List[str]] = None

  def jalali_date(self) -> str:
    return self.ts_jalali.split()[0] if ' ' in self.ts_jalali else self.ts_jalali

  def jalali_time(self) -> str:
    return self.ts_jalali.split()[1] if ' ' in self.ts_jalali else ''

# ─── READER ──────────────────────────────────────────────────────────────────

class LogFileReader:
  def __init__(self, paths: List[str]) -> None:
    self.paths = [Path(p) for p in paths]

  def __iter__(self) -> Iterator[LogEntry]:
    for path in self.paths:
      if not path.exists():
        raise FileNotFoundError(f'Input file not found: {path}')
      with path.open('r', encoding='utf-8') as f:
        for line_no, line in enumerate(f, 1):
          line = line.strip()
          if not line:
            continue
          try:
            obj = json.loads(line)
          except json.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON on {path}:{line_no}: {e}') from e
          yield self.validate(obj)

  def validate(self, obj: dict) -> LogEntry:
    required = ['version', 'id', 'session_id', 'ts_iso', 'ts_jalali', 'source', 'q_text', 'a_text']
    missing = [k for k in required if k not in obj]
    if missing:
      raise KeyError(f'Missing required keys {missing} in entry {obj.get("id")}')
    return LogEntry(**obj)  # type: ignore[arg-type]

# ─── COLLECTION ──────────────────────────────────────────────────────────────

class LogCollection:
  def __init__(self, entries: Iterable[LogEntry]) -> None:
    self.entries = list(entries)

  def unique(self) -> 'LogCollection':
    seen = set()
    unique_entries: List[LogEntry] = []
    for e in self.entries:
      if e.id not in seen:
        seen.add(e.id)
        unique_entries.append(e)
    self.entries = unique_entries
    return self

  def sort_by_iso(self) -> 'LogCollection':
    self.entries.sort(key=lambda e: self._parse_iso(e.ts_iso))
    return self

  def _parse_iso(self, ts: str) -> datetime:
    try:
      return datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except Exception:
      return datetime.min

  def group_by(self, field: str) -> OrderedDict[str, List[LogEntry]]:
    groups: defaultdict[str, List[LogEntry]] = defaultdict(list)
    for e in self.entries:
      key: str
      if field == 'jalali_date':
        key = e.jalali_date()
      elif hasattr(e, field):
        key = getattr(e, field) or 'UNKNOWN'
      else:
        key = 'UNKNOWN'
      groups[key].append(e)
    # preserve chronological order of groups based on first entry in each
    ordered = OrderedDict()
    for k in sorted(groups.keys(), key=lambda k: self._parse_iso(groups[k][0].ts_iso)):
      ordered[k] = groups[k]
    return ordered

# ─── DOCX CONFIG & BUILDER ───────────────────────────────────────────────────

@dataclass
class DocxConfig:
  title: str = 'Coding Autobiography'
  group_field: str = 'jalali_date'
  heading_styles: dict[str, str] = field(default_factory=lambda: {'h1': 'Heading 1', 'h2': 'Heading 2'})

class DocxBuilder:
  def __init__(self, config: DocxConfig) -> None:
    self.config = config

  def ensure_heading_styles(self, doc: Document) -> None:
    styles = doc.styles
    # create missing heading styles if necessary
    for level, name in [('Heading 1', 'h1'), ('Heading 2', 'h2')]:
      if level not in styles:
        s = styles.add_style(level, WD_STYLE_TYPE.PARAGRAPH)
        s.font.bold = True

  def append_entries(self, grouped: OrderedDict[str, List[LogEntry]], output_path: str) -> None:
    doc_path = Path(output_path)
    doc: Document
    if doc_path.exists():
      doc = Document(str(doc_path))
    else:
      doc = Document()
      doc.add_heading(self.config.title, level=0)
    self.ensure_heading_styles(doc)
    for group_key, entries in grouped.items():
      doc.add_heading(group_key, level=1)
      for entry in entries:
        time_part = entry.jalali_time()
        h2_title = f'[{time_part}] {entry.source} | {entry.model or "unknown"}'
        if entry.project_path:
          h2_title += f' @ {entry.project_path}'
        doc.add_heading(h2_title, level=2)
        if entry.q_summary:
          doc.add_paragraph('Prompt summary:')
          doc.add_paragraph(entry.q_summary)
        if entry.a_summary:
          doc.add_paragraph('Answer summary:')
          doc.add_paragraph(entry.a_summary)
        doc.add_paragraph('Prompt (full):')
        doc.add_paragraph(entry.q_text)
        doc.add_paragraph('Answer (full):')
        doc.add_paragraph(entry.a_text)
        doc.add_paragraph('---')
    doc.save(str(doc_path))

# ─── MAIN CLI ────────────────────────────────────────────────────────────────

@dataclass
class ChronicleConfig:
  input_jsonl_paths: List[str]
  output_docx_path: str
  group_by: str = 'jalali_date'

def parse_args() -> ChronicleConfig:
  parser = argparse.ArgumentParser(description='Build Coding Autobiography from Codex/Continue logs.')
  parser.add_argument('input_jsonl', nargs='+', help='One or more JSONL log files')
  parser.add_argument('output_docx', help='Output DOCX file')
  parser.add_argument('--group-by', default='jalali_date', help='Field to group entries by (default: jalali_date)')
  args = parser.parse_args()
  return ChronicleConfig(
    input_jsonl_paths=args.input_jsonl,
    output_docx_path=args.output_docx,
    group_by=args.group_by
  )

def main() -> None:
  cfg = parse_args()
  reader = LogFileReader(cfg.input_jsonl_paths)
  collection = LogCollection(reader).unique().sort_by_iso()
  grouped = collection.group_by(cfg.group_by)
  builder = DocxBuilder(DocxConfig(group_field=cfg.group_by))
  builder.append_entries(grouped, cfg.output_docx_path)
  print(f'Written {sum(len(v) for v in grouped.values())} entries into {cfg.output_docx_path}')

if __name__ == '__main__':
  main()
