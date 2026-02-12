# autobiography/collection.py
from __future__ import annotations
from collections import OrderedDict
from datetime import datetime
from typing import Iterable, List

from .models import LogEntry

class LogCollection:
    """Utility wrapper for deduplicating, sorting, and grouping log entries."""

    def __init__(self, entries: Iterable[LogEntry]) -> None:
        self.entries = list(entries)

    def unique(self) -> "LogCollection":
        seen: set[str] = set()
        deduped: List[LogEntry] = []
        for entry in self.entries:
            if entry.id in seen:
                continue
            seen.add(entry.id)
            deduped.append(entry)
        self.entries = deduped
        return self

    def sort_by_iso(self) -> "LogCollection":
        self.entries.sort(key=lambda e: self._parse_iso(e.ts_iso))
        return self

    def group_by(self, field: str) -> OrderedDict[str, List[LogEntry]]:
        buckets: dict[str, List[LogEntry]] = {}
        order: list[str] = []
        for entry in self.entries:
            key = self._resolve_group_key(entry, field)
            if key not in buckets:
                buckets[key] = []
                order.append(key)
            buckets[key].append(entry)
        order.sort(key=lambda key: self._parse_iso(buckets[key][0].ts_iso))
        return OrderedDict((key, buckets[key]) for key in order)

    def _parse_iso(self, value: str) -> datetime:
        try:
            norm = value.replace("Z", "+00:00")
            return datetime.fromisoformat(norm)
        except Exception:
            return datetime.min

    def _resolve_group_key(self, entry: LogEntry, field: str) -> str:
        """Invoke callables or access field; fallback to 'UNKNOWN'."""
        attr = getattr(entry, field, None)
        # Always commit to calling if callable; the default field is "jalali_date"
        if callable(attr):
            attr = attr()
        if attr is None or (isinstance(attr, str) and not attr.strip()):
            return "UNKNOWN"
        return str(attr)