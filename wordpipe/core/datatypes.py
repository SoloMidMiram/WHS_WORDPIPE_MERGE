"""Core data types for the WordPipe pipeline."""

from __future__ import annotations

import datetime as dt
import warnings
from dataclasses import dataclass, field
from pathlib import Path
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
    """Pipeline configuration.

    Config flags status:
    - ``do_flatten``, ``limit_pages``, ``prefer_win32`` — **stable**
    - ``per_segment_tables``, ``ai_headings``, ``ai_rewrite``, ``max_rewrite_per_section`` — **experimental**
      These flags are accepted for backward compatibility but currently have no
      wired step behaviour. They will either be wired to real steps in a future
      release or removed with a deprecation cycle.
    """

    in_path: Path
    out_path: Path
    do_flatten: bool = True
    prefer_win32: bool = True
    per_segment_tables: bool = False
    limit_pages: Optional[int] = None
    ai_headings: bool = False
    ai_rewrite: bool = False
    max_rewrite_per_section: int = 40


def warn_experimental_config(cfg: PipelineConfig) -> None:
    """Emit deprecation warnings for experimental config flags that are no-ops."""
    experimental = {
        "per_segment_tables": cfg.per_segment_tables,
        "ai_headings": cfg.ai_headings,
        "ai_rewrite": cfg.ai_rewrite,
    }
    for name, value in experimental.items():
        if value:
            warnings.warn(
                f"PipelineConfig.{name}=True is experimental and currently has no effect. "
                f"It will be wired or removed in a future release.",
                UserWarning,
                stacklevel=2,
            )


@dataclass(slots=True)
class RunReport:
    out_path: Path
    notes: Sequence[ChangeNote] = field(default_factory=list)
    segments: Sequence[Segment] = field(default_factory=list)
    seconds: float = 0.0
    errors: list[str] = field(default_factory=list)
