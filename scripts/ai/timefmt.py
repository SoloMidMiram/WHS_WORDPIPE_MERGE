# ai/timefmt.py — Tehran timestamp line (+03:30 from London), Jalali if available
from __future__ import annotations

from datetime import datetime

try:
    from persiantools.jdatetime import JalaliDate  # pip install persiantools
except Exception:
    JalaliDate = None

# at top
from datetime import datetime, timezone, timedelta


def tehran_timestamp_line(dt: datetime | None = None) -> str:
    tehran = timezone(timedelta(hours=3, minutes=30))
    now = (dt or datetime.utcnow()).astimezone(tehran)
    g_line = now.strftime("%Y-%m-%d %H:%M")
    try:
        from persiantools.jdatetime import JalaliDate

        j = JalaliDate.to_jalali(now.date())
        j_line = f"{j.year:04d}-{j.month:02d}-{j.day:02d}"
    except Exception:
        j_line = ""
    return f"{g_line} Tehran (UTC+03:30) | {j_line}"


from datetime import datetime, timezone, timedelta

# ... keep your existing imports + tehran_timestamp_line


def tehran_filename_stamp(dt: datetime | None = None) -> str:
    """
    Returns a Windows-safe stamp like: 1404-05-23_13-45_Tehran
    Uses Tehran time (fixed +03:30 from London). If persiantools is missing,
    falls back to Gregorian date instead of Jalali.
    """
    tehran = timezone(timedelta(hours=3, minutes=30))
    now = (dt or datetime.utcnow()).astimezone(tehran)
    hhmm = now.strftime("%H-%M")  # colonless for Windows

    try:
        # optional Jalali
        from persiantools.jdatetime import JalaliDate  # type: ignore

        j = JalaliDate.to_jalali(now.date())
        j_line = f"{j.year:04d}-{j.month:02d}-{j.day:02d}"
    except Exception:
        # fallback: Gregorian
        j_line = now.strftime("%Y-%m-%d")

    return f"{j_line}_{hhmm}_Tehran"
