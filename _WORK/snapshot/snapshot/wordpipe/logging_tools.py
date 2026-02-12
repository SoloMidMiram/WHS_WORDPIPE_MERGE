# placeholder
# ==================================
# file: wordpipe/logging_tools.py
# ==================================
from __future__ import annotations
import json, logging
from typing import Optional
import json, logging, os


def evt(logger, jsonl_path: Optional[str], level: str, event: str, **fields) -> None:
    """Unified event emitter: console + JSONL line.
    - `logger` is a stdlib logger; we write a compact human line.
    - `jsonl_path` (optional) writes structured data suitable for analysis.
    """
    # Console
    if logger:
        lvl = getattr(logging, level.upper(), logging.INFO)  # ← safer
        logger.log(
            lvl, f"{event} | " + ", ".join(f"{k}={v}" for k, v in fields.items())
        )

    # JSONL

    if jsonl_path:
        os.makedirs(os.path.dirname(jsonl_path), exist_ok=True)
        with open(jsonl_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {"level": level, "event": event, **fields}, ensure_ascii=False
                )
                + "\n"
            )
