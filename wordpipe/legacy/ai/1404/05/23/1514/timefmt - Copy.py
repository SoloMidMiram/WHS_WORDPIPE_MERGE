# ai/timefmt.py — Tehran timestamp line (+03:30 from London), Jalali if available
from __future__ import annotations
from datetime import datetime, timezone, timedelta

try:
    from persiantools.jdatetime import JalaliDate  # pip install persiantools
except Exception:
    JalaliDate = None  # fallback: no Jalali string


def tehran_timestamp_line(dt: datetime | None = None) -> str:
    tehran = timezone(timedelta(hours=3, minutes=30))  # fixed +03:30 from London
    now = (dt or datetime.utcnow()).astimezone(tehran)
    g_line = now.strftime("%Y-%m-%d %H:%M")
    if JalaliDate:
        j = JalaliDate.to_jalali(now.date())
        j_line = f"{j.year:04d}-{j.month:02d}-{j.day:02d}"
    else:
        j_line = ""
    return f"{g_line} Tehran (+03:30 from London) | {j_line}"
