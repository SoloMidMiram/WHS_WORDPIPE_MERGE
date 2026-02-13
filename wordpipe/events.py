"""Runtime event emission interfaces for TraceLedger integration.

WordPipe must not depend on TraceLedger; TraceLedger can depend on WordPipe by
providing an EventSink adapter.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol


class EventSink(Protocol):
    def emit(self, level: str, event: str, fields: dict[str, Any]) -> None: ...


class NullSink:
    def emit(self, level: str, event: str, fields: dict[str, Any]) -> None:
        return


_SECRET_LITERAL_PATTERNS = [
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "<REDACTED_OPENAI_KEY>"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"), "<REDACTED_GITHUB_TOKEN>"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "<REDACTED_GITHUB_TOKEN>"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "<REDACTED_AWS_KEY_ID>"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"), "<REDACTED_SLACK_TOKEN>"),
]


def _redact_text(text: str) -> str:
    redacted = text
    for pattern, replacement in _SECRET_LITERAL_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def _redact_value(value: Any) -> Any:
    if isinstance(value, str):
        return _redact_text(value)
    return value


def redact_fields(fields: dict[str, Any]) -> dict[str, Any]:
    return {k: _redact_value(v) for k, v in fields.items()}


@dataclass
class StdlibLoggerSink:
    logger: logging.Logger

    def emit(self, level: str, event: str, fields: dict[str, Any]) -> None:
        lvl = getattr(logging, (level or "INFO").upper(), logging.INFO)
        safe_fields = redact_fields(fields)
        msg = f"{event} | " + ", ".join(f"{k}={v}" for k, v in safe_fields.items())
        self.logger.log(lvl, msg)


@dataclass
class JsonlSink:
    path: str

    def emit(self, level: str, event: str, fields: dict[str, Any]) -> None:
        safe_fields = redact_fields(fields)
        payload = {
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "event": event,
            **safe_fields,
        }
        parent = os.path.dirname(self.path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")


@dataclass
class CompositeSink:
    sinks: list[EventSink]

    def emit(self, level: str, event: str, fields: dict[str, Any]) -> None:
        for sink in self.sinks:
            sink.emit(level, event, fields)


def make_sink(*, logger: logging.Logger | None, jsonl_path: str | None) -> EventSink:
    sinks: list[EventSink] = []
    if logger is not None:
        sinks.append(StdlibLoggerSink(logger))
    if jsonl_path:
        sinks.append(JsonlSink(jsonl_path))
    if not sinks:
        return NullSink()
    if len(sinks) == 1:
        return sinks[0]
    return CompositeSink(sinks)

