"""Shared data models for the chronicle pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ChronicleEvent:
    """A single event extracted from a raw chronicle markdown file."""

    date: str  # YYYY-MM-DD
    title: str
    body: str = ""


@dataclass
class NormalisedDocument:
    """The structured representation of a normalised chronicle file."""

    source: str
    title: str
    input_file: str
    events: list[ChronicleEvent] = field(default_factory=list)
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    preamble: str = ""


@dataclass
class MergeResult:
    """Result of merging two or more normalised documents."""

    sources: list[str]
    events: list[ChronicleEvent]
    date_range: tuple[Optional[str], Optional[str]]
