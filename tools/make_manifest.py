"""Generate manifest CSV/JSONL for files under a snapshot root."""

import argparse
import csv
import hashlib
import json
import os
import re
from datetime import datetime, timezone, timedelta

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None

from jalali import format_jalali, gregorian_to_jalali

LEGACY_TOKENS = ["\\legacy\\", "/legacy/", "save ", "- copy", "legacy", "v2", "old"]

DATE_TIME_RE = re.compile(r"(14\d{6})[ _-]?(\d{4})")
DATE_ONLY_RE = re.compile(r"(?<!\d)(14\d{6})(?!\d)")


def get_tehran_tz():
    if ZoneInfo is not None:
        try:
            return ZoneInfo("Asia/Tehran")
        except Exception:
            pass
    return timezone(timedelta(hours=3, minutes=30))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def detect_stamp_from_name(rel_path: str):
    lower = rel_path.lower()
    m = DATE_TIME_RE.search(lower)
    if m:
        return f"{m.group(1)} {m.group(2)}", "name", "high"
    m = DATE_ONLY_RE.search(lower)
    if m:
        return m.group(1), "name", "high"
    return "", "", ""


def is_legacy_candidate(rel_path: str) -> bool:
    lower = rel_path.lower()
    for token in LEGACY_TOKENS:
        if token in lower:
            return True
    return False


def bucket_from_stamp_or_mtime(stamp: str, dt_teh: datetime, legacy: bool) -> str:
    if not legacy:
        return "current/"

    if stamp:
        if " " in stamp:
            date_part, time_part = stamp.split(" ", 1)
        else:
            date_part, time_part = stamp, "0000"
        jy = int(date_part[0:4])
        jm = int(date_part[4:6])
        jd = int(date_part[6:8])
        hh = int(time_part[0:2])
        mm = int(time_part[2:4])
        return f"legacy/{jy:04d}/{jm:02d}/{jd:02d}/{hh:02d}{mm:02d}"

    jy, jm, jd = gregorian_to_jalali(dt_teh.year, dt_teh.month, dt_teh.day)
    return f"legacy/{jy:04d}/{jm:02d}/{jd:02d}/{dt_teh.hour:02d}{dt_teh.minute:02d}"


def iter_files(root: str):
    for base, _dirs, files in os.walk(root):
        for name in files:
            yield os.path.join(base, name)


def _auto_normalize_root(root: str) -> tuple[str, bool]:
    try:
        entries = [e for e in os.scandir(root) if e.is_dir()]
    except FileNotFoundError:
        return root, False

    if len(entries) != 1:
        return root, False
    if entries[0].name != "snapshot":
        return root, False

    candidate = os.path.join(root, "snapshot")
    if os.path.isdir(os.path.join(candidate, "WordHorrorStories")) or os.path.isdir(
        os.path.join(candidate, "wordpipe")
    ):
        return candidate, True
    return root, False


def _append_setup_log(msg: str) -> None:
    log_path = os.path.abspath(os.path.join(os.getcwd(), "_ARCHIVE", "logs", "setup.log"))
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="_WORK/snapshot")
    parser.add_argument("--out-dir", default="_ARCHIVE/manifests")
    parser.add_argument(
        "--no-auto-normalize",
        action="store_true",
        help="Disable auto-normalization for nested snapshot/snapshot roots.",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    effective_root = root
    if not args.no_auto_normalize:
        normalized_root, did_normalize = _auto_normalize_root(root)
        if did_normalize:
            effective_root = normalized_root
            msg = f"AUTO_NORMALIZE_ROOT: {root} -> {effective_root}"
            print(msg)
            _append_setup_log(msg)

    csv_path = os.path.join(out_dir, "manifest.csv")
    jsonl_path = os.path.join(out_dir, "manifest.jsonl")

    tz_teh = get_tehran_tz()

    fieldnames = [
        "rel_path",
        "size_bytes",
        "sha256",
        "mtime_iso",
        "mtime_tehran",
        "jalali_date_time",
        "detected_stamp_from_name",
        "detected_stamp_source",
        "stamp_confidence",
        "legacy_candidate",
        "suggested_bucket",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f_csv, open(
        jsonl_path, "w", encoding="utf-8"
    ) as f_jsonl:
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        writer.writeheader()

        for path in iter_files(effective_root):
            rel_path = os.path.relpath(path, effective_root).replace("\\", "/")
            st = os.stat(path)
            size_bytes = st.st_size
            sha256 = sha256_file(path)

            dt_utc = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
            dt_teh = dt_utc.astimezone(tz_teh)

            mtime_iso = dt_utc.isoformat()
            mtime_tehran = dt_teh.isoformat()
            jalali_date_time = format_jalali(dt_teh)

            stamp, source, confidence = detect_stamp_from_name(rel_path)
            if stamp:
                detected_stamp_source = "name"
                stamp_confidence = "high"
            else:
                detected_stamp_source = "mtime"
                stamp_confidence = "medium"

            legacy_candidate = is_legacy_candidate(rel_path)
            suggested_bucket = bucket_from_stamp_or_mtime(
                stamp, dt_teh, legacy_candidate
            )

            row = {
                "rel_path": rel_path,
                "size_bytes": size_bytes,
                "sha256": sha256,
                "mtime_iso": mtime_iso,
                "mtime_tehran": mtime_tehran,
                "jalali_date_time": jalali_date_time,
                "detected_stamp_from_name": stamp,
                "detected_stamp_source": detected_stamp_source,
                "stamp_confidence": stamp_confidence,
                "legacy_candidate": str(legacy_candidate).lower(),
                "suggested_bucket": suggested_bucket,
            }

            writer.writerow(row)
            f_jsonl.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
