"""File I/O helpers for the chronicle pipeline."""

from __future__ import annotations

from pathlib import Path


def read_text(path: Path) -> str:
    """Read a text file with UTF-8 encoding."""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    """Write a text file with UTF-8 encoding."""
    path.write_text(content, encoding="utf-8")
