
# autobiography/config.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

@dataclass(frozen=True)
class ChronicleConfig:
    input_paths: List[Path]
    output_docx: Path
    group_field: str = "jalali_date"
    layout: str = "single_column"

@dataclass(frozen=True)
class DocxConfig:
    title: str = "Coding Autobiography"
    heading_styles: Dict[str, str] = field(
        default_factory=lambda: {"group": "Heading 1", "entry": "Heading 2"}
    )
    summary_labels: Dict[str, str] = field(
        default_factory=lambda: {"prompt": "Prompt summary", "answer": "Answer summary"}
    )
    section_labels: Dict[str, str] = field(
        default_factory=lambda: {"prompt": "Prompt (full)", "answer": "Answer (full)"}
    )
    separator: str = "---"
    include_workspace: bool = True
    include_project_path: bool = True
    layout: str = "single_column"
    render_markdown_answers: bool = True
    two_column_prompt_ratio: float = 0.5
