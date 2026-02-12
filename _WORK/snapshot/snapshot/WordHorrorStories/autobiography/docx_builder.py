from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import List, Optional

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Inches

from .config import DocxConfig
from .models import LogEntry


class AnswerRenderer:
  """Very small Markdown-ish renderer for assistant answers."""

  CODE_STYLE_NAME = 'AutobiographyCode'

  def __init__(self, doc: Document) -> None:
    self.doc = doc
    self._ensure_code_style()

  def render(self, text: str) -> None:
    if not text:
      return
    code_buffer: List[str] = []
    in_code = False
    for raw in text.splitlines():
      stripped = raw.strip()
      if stripped.startswith('```'):
        if in_code:
          self._add_code_block('\n'.join(code_buffer))
          code_buffer.clear()
          in_code = False
        else:
          in_code = True
        continue
      if in_code:
        code_buffer.append(raw)
        continue
      if stripped.startswith('###'):
        self._add_heading(stripped[3:].strip(), level=3)
      elif stripped.startswith('##'):
        self._add_heading(stripped[2:].strip(), level=2)
      elif stripped.startswith('#'):
        self._add_heading(stripped[1:].strip(), level=1)
      elif stripped.startswith('- '):
        para = self.doc.add_paragraph(stripped[2:].strip())
        para.style = 'List Bullet'
      elif stripped == '':
        self.doc.add_paragraph('')
      else:
        self.doc.add_paragraph(raw)
    if in_code and code_buffer:
      self._add_code_block('\n'.join(code_buffer))

  def _ensure_code_style(self) -> None:
    if self.CODE_STYLE_NAME in self.doc.styles:
      return
    style = self.doc.styles.add_style(self.CODE_STYLE_NAME, WD_STYLE_TYPE.PARAGRAPH)
    style.font.name = 'Consolas'

  def _add_heading(self, text: str, level: int) -> None:
    level = max(1, min(level, 4))
    self.doc.add_heading(text, level=level)

  def _add_code_block(self, text: str) -> None:
    para = self.doc.add_paragraph(text)
    para.style = self.CODE_STYLE_NAME


class BaseDocxBuilder:
  """Common functionality for the different layout builders."""

  def __init__(self, config: DocxConfig) -> None:
    self.config = config

  def build_document(
    self,
    grouped: OrderedDict[str, List[LogEntry]],
    doc: Optional[Document] = None,
  ) -> Document:
    doc = self._prepare_document(doc)
    for group_key, entries in grouped.items():
      self._add_group(doc, group_key, entries)
    return doc

  def save(self, grouped: OrderedDict[str, List[LogEntry]], output_path: Path | str) -> Path:
    out_path = Path(output_path)
    doc = self.build_document(grouped)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    return out_path

  def _prepare_document(self, doc: Optional[Document]) -> Document:
    if doc is None:
      doc = Document()
      doc.add_heading(self.config.title, level=0)
    self._ensure_heading_styles(doc)
    return doc

  def _ensure_heading_styles(self, doc: Document) -> None:
    for style_name in self.config.heading_styles.values():
      if style_name in doc.styles:
        continue
      style = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
      style.font.bold = True

  def _add_group(self, doc: Document, group_key: str, entries: List[LogEntry]) -> None:
    para = doc.add_paragraph(group_key)
    para.style = self.config.heading_styles.get('group', 'Heading 1')
    for entry in entries:
      self._add_entry(doc, entry)

  def _add_entry(self, doc: Document, entry: LogEntry) -> None:  # pragma: no cover - abstract
    raise NotImplementedError


class DocxBuilder(BaseDocxBuilder):
  """Default single-column layout."""

  def _add_entry(self, doc: Document, entry: LogEntry) -> None:
    renderer = AnswerRenderer(doc) if self.config.render_markdown_answers else None
    title_bits: List[str] = []
    time = entry.jalali_time()
    if time:
      title_bits.append(f'[{time}]')
    title_bits.append(entry.source)
    if entry.model:
      title_bits.append(entry.model)
    if self.config.include_workspace and entry.workspace:
      title_bits.append(f'workspace={entry.workspace}')
    if self.config.include_project_path and entry.project_path:
      title_bits.append(entry.project_path)
    title_para = doc.add_paragraph(' '.join(b for b in title_bits if b.strip()))
    title_para.style = self.config.heading_styles.get('entry', 'Heading 2')

    if entry.q_summary:
      doc.add_paragraph(f"{self.config.summary_labels['prompt']}:")
      doc.add_paragraph(entry.q_summary)
    if entry.a_summary:
      doc.add_paragraph(f"{self.config.summary_labels['answer']}:")
      doc.add_paragraph(entry.a_summary)

    doc.add_paragraph(f"{self.config.section_labels['prompt']}:")
    doc.add_paragraph(entry.q_text)
    doc.add_paragraph(f"{self.config.section_labels['answer']}:")
    if renderer and entry.a_text:
      renderer.render(entry.a_text)
    else:
      doc.add_paragraph(entry.a_text)

    if self.config.separator:
      doc.add_paragraph(self.config.separator)


class DocxBuilderTwoColumn(BaseDocxBuilder):
  """Two-column layout where prompt and summary share a row."""

  def _add_entry(self, doc: Document, entry: LogEntry) -> None:
    heading = doc.add_paragraph(f"[{entry.jalali_time()}] {entry.source}")
    heading.style = self.config.heading_styles.get('entry', 'Heading 2')
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    prompt_width = max(0.2, min(0.8, self.config.two_column_prompt_ratio))
    table.columns[0].width = Inches(6 * prompt_width)
    table.columns[1].width = Inches(6 * (1 - prompt_width))

    left_cell = table.cell(0, 0)
    right_cell = table.cell(0, 1)
    left_cell.text = entry.q_text
    summary_text = entry.a_summary or entry.a_text or ''
    right_cell.text = summary_text

    if self.config.separator:
      doc.add_paragraph(self.config.separator)


def builder_for_config(config: DocxConfig) -> BaseDocxBuilder:
  if config.layout.lower() == 'two_column':
    return DocxBuilderTwoColumn(config)
  return DocxBuilder(config)
