"""Generate manifest CSV/JSONL for files under a snapshot root."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None

from jalali import format_jalali, gregorian_to_jalali
from pipeline_contracts import (
    StagePaths,
    StageResult,
    emit_required_path_error,
    resolve_path,
    resolve_workspace_root,
    write_summary_json,
)
from tool_common import auto_normalize_root, append_log_block, sha256_file

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


def detect_stamp_from_name(rel_path: str):
    lower = rel_path.lower()
    m = DATE_TIME_RE.search(lower)
    if m:
        return f"{m.group(1)} {m.group(2)}"
    m = DATE_ONLY_RE.search(lower)
    if m:
        return m.group(1)
    return ""


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


def run_stage(
    *,
    workspace_root: str,
    root: str,
    out_dir: str,
    no_auto_normalize: bool,
    strict: bool,
) -> StageResult:
    workspace_abs = resolve_workspace_root(workspace_root)
    root_abs = resolve_path(workspace_abs, root)
    out_dir_abs = resolve_path(workspace_abs, out_dir)
    setup_log_path = resolve_path(workspace_abs, "_ARCHIVE/logs/setup.log")
    csv_path = os.path.join(out_dir_abs, "manifest.csv")
    jsonl_path = os.path.join(out_dir_abs, "manifest.jsonl")

    result = StageResult(
        stage="make_manifest",
        paths=StagePaths(
            workspace_root=workspace_abs,
            inputs={"root": root_abs},
            outputs={
                "manifest_csv": csv_path,
                "manifest_jsonl": jsonl_path,
                "setup_log": setup_log_path,
            },
        ),
    )

    if not os.path.isdir(root_abs):
        emit_required_path_error(
            result, label="snapshot root directory", abs_path=root_abs, kind="directory"
        )
        return result.finalize(strict=strict)

    os.makedirs(out_dir_abs, exist_ok=True)

    effective_root = root_abs
    auto_normalize_msg = ""
    if not no_auto_normalize:
        normalized_root, did_normalize = auto_normalize_root(root_abs)
        if did_normalize:
            effective_root = normalized_root
            auto_normalize_msg = f"AUTO_NORMALIZE_ROOT: {root_abs} -> {effective_root}"
            append_log_block(setup_log_path, "make_manifest", [auto_normalize_msg])

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

    row_count = 0
    with open(csv_path, "w", newline="", encoding="utf-8") as f_csv, open(
        jsonl_path, "w", encoding="utf-8"
    ) as f_jsonl:
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        writer.writeheader()

        for path in iter_files(effective_root):
            try:
                rel_path = os.path.relpath(path, effective_root).replace("\\", "/")
                st = os.stat(path)
                size_bytes = st.st_size
                sha256 = sha256_file(path)
                dt_utc = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
                dt_teh = dt_utc.astimezone(tz_teh)
                mtime_iso = dt_utc.isoformat()
                mtime_tehran = dt_teh.isoformat()
                jalali_date_time = format_jalali(dt_teh)
                stamp = detect_stamp_from_name(rel_path)
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
                row_count += 1
            except Exception as exc:
                result.add_error(
                    "MANIFEST_ROW_ERROR",
                    f"Failed to process file for manifest: {path}",
                    {"error": str(exc)},
                )

    result.counters["manifest_rows"] = row_count
    result.generated_paths = {
        "manifest_csv": csv_path,
        "manifest_jsonl": jsonl_path,
    }

    summary_lines = []
    if auto_normalize_msg:
        summary_lines.append(auto_normalize_msg)
    summary_lines.extend(
        [
            f"manifest_rows: {row_count}",
            f"manifest_csv: {csv_path}",
            f"manifest_jsonl: {jsonl_path}",
        ]
    )
    result.details["summary_lines"] = summary_lines

    return result.finalize(strict=strict)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="_WORK/snapshot")
    parser.add_argument("--out-dir", default="_ARCHIVE/manifests")
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--summary-json", default="")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--no-auto-normalize",
        action="store_true",
        help="Disable auto-normalization for nested snapshot/snapshot roots.",
    )
    args = parser.parse_args()

    result = run_stage(
        workspace_root=args.workspace_root,
        root=args.root,
        out_dir=args.out_dir,
        no_auto_normalize=args.no_auto_normalize,
        strict=args.strict,
    )

    for line in result.details.get("summary_lines", []):
        print(line)

    if args.summary_json:
        summary_json_path = resolve_path(result.paths.workspace_root, args.summary_json)
        write_summary_json(summary_json_path, result)

    raise SystemExit(1 if result.status == "error" else 0)


if __name__ == "__main__":
    main()
