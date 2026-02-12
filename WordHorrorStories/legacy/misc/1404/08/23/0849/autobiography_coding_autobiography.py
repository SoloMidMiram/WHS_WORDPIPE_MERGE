# coding_autobiography.py
from __future__ import annotations

import argparse
import json
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Iterator, List, Sequence

from docx import Document
from docx.enum.style import WD_STYLE_TYPE

# ── DATA MODELS ──

@dataclass(frozen=True)
class LogEntry:
    version: str
    id: str
    session_id: str
    ts_iso: str
    ts_jalali: str
    source: str
    model: str | None = None
    project_path: str | None = None
    workspace: str | None = None
    user: str | None = None
    q_text: str = ''
    a_text: str = ''
    q_summary: str | None = None
    a_summary: str | None = None
    language_guess: str | None = None
    tags: List[str] | None = None

    def jalali_date(self) -> str:
        return self.ts_jalali.split()[0] if ' ' in self.ts_jalali else self.ts_jalali

    def jalali_time(self) -> str:
        return self.ts_jalali.split()[1] if ' ' in self.ts_jalali else ''

@dataclass(frozen=True)
class ChronicleConfig:
    input_paths: List[Path]
    output_docx: Path
    group_field: str = 'jalali_date'

@dataclass(frozen=True)
class DocxConfig:
    title: str = 'Coding Autobiography'
    heading_styles: dict[str, str] = field(default_factory=lambda: {'group': 'Heading 1', 'entry': 'Heading 2'})
    summary_labels: dict[str, str] = field(default_factory=lambda: {'prompt': 'Prompt summary', 'answer': 'Answer summary'})
    section_labels: dict[str, str] = field(default_factory=lambda: {'prompt': 'Prompt (full)', 'answer': 'Answer (full)'})
    separator: str = '---'
    include_workspace: bool = True
    include_project_path: bool = True

# ── READER ──

class LogFileReader:
    def __init__(self, paths: Sequence[Path | str]) -> None:
        self.paths = [Path(p) for p in paths]

    def __iter__(self) -> Iterator[LogEntry]:
        for path in self.paths:
            if not path.exists():
                raise FileNotFoundError(f'Input file not found: {path}')
            with path.open('r', encoding='utf-8') as handle:
                for line_no, raw in enumerate(handle, 1):
                    line = raw.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise ValueError(f'Invalid JSON on {path}:{line_no}: {exc}') from exc
                    yield self._to_entry(payload, path, line_no)

    def _to_entry(self, payload: dict[str, Any], path: Path, line_no: int) -> LogEntry:
        required = ['version', 'id', 'session_id', 'ts_iso', 'ts_jalali', 'source', 'q_text', 'a_text']
        missing = [field for field in required if field not in payload]
        if missing:
            raise KeyError(f'Missing {missing} in {path}:{line_no}')
        tags = payload.get('tags')
        if tags is not None and not isinstance(tags, list):
            raise TypeError(f'Field "tags" must be a list in {path}:{line_no}')
        return LogEntry(
            version=payload['version'],
            id=payload['id'],
            session_id=payload['session_id'],
            ts_iso=payload['ts_iso'],
            ts_jalali=payload['ts_jalali'],
            source=payload['source'],
            model=payload.get('model'),
            project_path=payload.get('project_path'),
            workspace=payload.get('workspace'),
            user=payload.get('user'),
            q_text=payload.get('q_text', ''),
            a_text=payload.get('a_text', ''),
            q_summary=payload.get('q_summary'),
            a_summary=payload.get('a_summary'),
            language_guess=payload.get('language_guess'),
            tags=tags
        )

# ── COLLECTION ──

class LogCollection:
    def __init__(self, entries: Iterable[LogEntry]) -> None:
        self.entries = list(entries)

    def unique(self) -> LogCollection:
        seen: set[str] = set()
        unique_entries: List[LogEntry] = []
        for entry in self.entries:
            if entry.id in seen:
                continue
            seen.add(entry.id)
            unique_entries.append(entry)
        self.entries = unique_entries
        return self

    def sort_by_iso(self) -> LogCollection:
        self.entries.sort(key=lambda e: self._parse_iso(e.ts_iso))
        return self

    def group_by(self, field: str) -> OrderedDict[str, List[LogEntry]]:
        groups: OrderedDict[str, List[LogEntry]] = OrderedDict()
        for entry in self.entries:
            key = self._resolve_group_key(entry, field)
            groups.setdefault(key, []).append(entry)
        return groups

    def _parse_iso(self, value: str) -> datetime:
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return datetime.min

    def _resolve_group_key(self, entry: LogEntry, field: str) -> str:
        if field == 'jalali_date':
            return entry.jalali_date()
        attr = getattr(entry, field, None)
        if callable(attr):
            attr = attr()
        if attr is None or attr == '':
            return 'UNKNOWN'
        return str(attr)

# ── DOCX BUILDER ──

class DocxBuilder:
    def __init__(self, config: DocxConfig) -> None:
        self.config = config

    def append_entries(self, grouped: OrderedDict[str, List[LogEntry]], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = Document(str(output_path)) if output_path.exists() else Document()
        if not output_path.exists():
            doc.add_heading(self.config.title, level=0)
        self._ensure_heading_styles(doc)
        for group_key, entries in grouped.items():
            self._add_group(doc, group_key, entries)
        doc.save(str(output_path))

    def _ensure_heading_styles(self, doc: Document) -> None:
        for style_name in self.config.heading_styles.values():
            if style_name in doc.styles:
                continue
            style = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
            style.font.bold = True

    def _add_group(self, doc: Document, group_key: str, entries: List[LogEntry]) -> None:
        para = doc.add_paragraph(group_key)
        para.style = self.config.heading_styles['group']
        for entry in entries:
            self._add_entry(doc, entry)

    def _add_entry(self, doc: Document, entry: LogEntry) -> None:
        title_bits = [f'[{entry.jalali_time()}]', entry.source]
        if entry.model:
            title_bits.append(entry.model)
        if self.config.include_workspace and entry.workspace:
            title_bits.append(f'workspace={entry.workspace}')
        if self.config.include_project_path and entry.project_path:
            title_bits.append(entry.project_path)
        title_para = doc.add_paragraph(' '.join(bit for bit in title_bits if bit.strip()))
        title_para.style = self.config.heading_styles['entry']

        if entry.q_summary:
            doc.add_paragraph(f"{self.config.summary_labels['prompt']}:")
            doc.add_paragraph(entry.q_summary)
        if entry.a_summary:
            doc.add_paragraph(f"{self.config.summary_labels['answer']}:")
            doc.add_paragraph(entry.a_summary)

        doc.add_paragraph(f"{self.config.section_labels['prompt']}:")
        doc.add_paragraph(entry.q_text)
        doc.add_paragraph(f"{self.config.section_labels['answer']}:")
        doc.add_paragraph(entry.a_text)

        if self.config.separator:
            doc.add_paragraph(self.config.separator)

# ── CLI / MAIN ──

def parse_args() -> ChronicleConfig:
    parser = argparse.ArgumentParser(description='Build a Coding Autobiography from Codex/Continue logs.')
    parser.add_argument('input_jsonl', nargs='+', help='One or more JSONL log files')
    parser.add_argument('output_docx', help='Destination DOCX file')
    parser.add_argument('--group-by', default='jalali_date', help='Field to group entries by (default: jalali_date)')
    args = parser.parse_args()
    return ChronicleConfig(
        input_paths=[Path(p) for p in args.input_jsonl],
        output_docx=Path(args.output_docx),
        group_field=args.group_by
    )

def main() -> None:
    cli_cfg = parse_args()
    reader = LogFileReader(cli_cfg.input_paths)
    collection = LogCollection(reader).unique().sort_by_iso()
    grouped = collection.group_by(cli_cfg.group_field)
    builder = DocxBuilder(DocxConfig())
    builder.append_entries(grouped, cli_cfg.output_docx)
    total = sum(len(batch) for batch in grouped.values())
    print(f'Written {total} entries into {cli_cfg.output_docx}')

if __name__ == '__main__':
    main()
