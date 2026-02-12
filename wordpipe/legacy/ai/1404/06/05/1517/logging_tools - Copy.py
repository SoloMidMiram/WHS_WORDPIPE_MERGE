# ai/logging_tools.py — evt logger (console + JSONL)
from __future__ import annotations
import json, logging, os
from typing import Optional


def evt(logger, jsonl_path: Optional[str], level: str, event: str, **fields) -> None:
    if logger:
        lvl = getattr(logging, level.upper(), logging.INFO)
        logger.log(
            lvl, f"{event} | " + ", ".join(f"{k}={v}" for k, v in fields.items())
        )
    if jsonl_path:
        os.makedirs(os.path.dirname(jsonl_path), exist_ok=True)
        with open(jsonl_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {"level": level, "event": event, **fields}, ensure_ascii=False
                )
                + "\n"
            )
