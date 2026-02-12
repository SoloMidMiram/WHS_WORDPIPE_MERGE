# autobiography/models.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class LogEntry:
    version: str
    id: str
    session_id: str
    ts_iso: str
    ts_jalali: str
    source: str
    model: Optional[str] = None
    project_path: Optional[str] = None
    workspace: Optional[str] = None
    user: Optional[str] = None
    q_text: str = ""
    a_text: str = ""
    q_summary: Optional[str] = None
    a_summary: Optional[str] = None
    language_guess: Optional[str] = None
    tags: Optional[List[str]] = None

    def jalali_date(self) -> str:
        if " " in self.ts_jalali:
            return self.ts_jalali.split(" ", 1)[0]
        return self.ts_jalali

    def jalali_time(self) -> str:
        if " " in self.ts_jalali:
            return self.ts_jalali.split(" ", 1)[1]
        return ""