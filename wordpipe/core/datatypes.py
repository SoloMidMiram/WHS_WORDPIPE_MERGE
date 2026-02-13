# ===================================
# file: wordpipe/core/datatypes.py
# ===================================
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import datetime as dt
from typing import Optional, Sequence


@dataclass(slots=True, frozen=True, order=True)
class ChangeNote:
    dt_local: dt.datetime
    author: str
    change_type: str
    location: str
    excerpt: str
    dt_jalali: str = ""

    def to_row(self) -> tuple[str, str, str, str, str]:
        greg = self.dt_local.strftime("%Y-%m-%d %H:%M")
        return (
            f"{greg} | {self.dt_jalali}",
            self.author,
            self.change_type,
            self.location,
            self.excerpt[:500],
        )


@dataclass(slots=True, frozen=True)
class Segment:
    start_p: int
    end_p: int
    h1_title: str
    hpath: str
    bk_name: Optional[str]


@dataclass(slots=True, frozen=True)
class PipelineConfig:
    in_path: Path
    out_path: Path
    do_flatten: bool = True
    prefer_win32: bool = True
    per_segment_tables: bool = True
    limit_pages: Optional[int] = None
    ai_headings: bool = False
    ai_rewrite: bool = False
    max_rewrite_per_section: int = 40


@dataclass(slots=True)
class RunReport:
    out_path: Path
    notes: Sequence[ChangeNote] = field(default_factory=list)
    segments: Sequence[Segment] = field(default_factory=list)
    seconds: float = 0.0
    errors: list[str] = field(default_factory=list)
