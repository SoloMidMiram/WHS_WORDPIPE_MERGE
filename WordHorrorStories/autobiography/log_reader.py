# autobiography/log_reader.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator, Sequence

from .models import LogEntry

class LogFileReader:
    """Iterates over one or more JSONL files and yields validated LogEntry objects."""

    def __init__(self, paths: Sequence[Path | str]) -> None:
        self.paths = [Path(p) for p in paths]

    def __iter__(self) -> Iterator[LogEntry]:
        for path in self.paths:
            if not path.exists():
                raise FileNotFoundError(f"Input file not found: {path}")
            with path.open("r", encoding="utf-8") as handle:
                for line_no, raw in enumerate(handle, 1):
                    line = raw.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise ValueError(f"Invalid JSON on {path}:{line_no}: {exc}") from exc
                    yield self._to_entry(payload, path, line_no)

    def _to_entry(self, payload: dict[str, Any], path: Path, line_no: int) -> LogEntry:
        required = ["version", "id", "session_id", "ts_iso", "ts_jalali", "source", "q_text", "a_text"]
        missing = [fld for fld in required if fld not in payload]
        if missing:
            raise KeyError(f"Missing {missing} in {path}:{line_no}")

        tags = payload.get("tags")
        if tags is not None:
            if not isinstance(tags, list):
                raise TypeError(f'Field "tags" must be a list in {path}:{line_no}')
            tags = [str(tag) for tag in tags]

        return LogEntry(
            version=str(payload["version"]),
            id=str(payload["id"]),
            session_id=str(payload["session_id"]),
            ts_iso=str(payload["ts_iso"]),
            ts_jalali=str(payload["ts_jalali"]),
            source=str(payload["source"]),
            model=payload.get("model"),
            project_path=payload.get("project_path"),
            workspace=payload.get("workspace"),
            user=payload.get("user"),
            q_text=payload.get("q_text", "") or "",
            a_text=payload.get("a_text", "") or "",
            q_summary=payload.get("q_summary"),
            a_summary=payload.get("a_summary"),
            language_guess=payload.get("language_guess"),
            tags=tags or None,
        )