"""Generate a dry-run relocation plan for legacy candidates."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime

from pipeline_contracts import (
    StagePaths,
    StageResult,
    emit_required_path_error,
    resolve_path,
    resolve_workspace_root,
    write_summary_json,
)
from tool_common import auto_normalize_root, append_log_block


def _area_from_rel(rel_path: str) -> str:
    rp = rel_path.replace("\\", "/")
    lower = rp.lower()
    if lower.startswith("wordpipe/ai/"):
        return "ai"
    if lower.startswith("wordpipe/core/"):
        return "core"
    if lower.startswith("wordpipe/flatteners/"):
        return "flatteners"
    if lower.startswith("wordhorrorstories/autobiography/"):
        return "autobiography"
    if lower.startswith("wordhorrorstories/chatgpt-chronicle/"):
        return "chronicle"
    if lower.startswith("wordhorrorstories/tools/"):
        return "tools"
    filename = os.path.basename(rp)
    if filename in ("docx_to_md_converter.py", "md_to_docx_converter.py"):
        return "tools"
    return "misc"


def _rule_hits(rel_path: str) -> list[str]:
    lower = rel_path.lower()
    hits = []
    if "/legacy/" in lower or "\\legacy\\" in lower:
        hits.append("rule:legacy-path")
    if "save " in lower:
        hits.append("rule:save-folder")
    if "- copy" in lower:
        hits.append("rule:copy-suffix")
    if "legacy" in lower:
        hits.append("rule:legacy-word")
    if "v2" in lower:
        hits.append("rule:v2")
    if "old" in lower:
        hits.append("rule:old")
    return sorted(set(hits))


def _parse_mtime_tehran(mtime_tehran: str) -> datetime:
    return datetime.fromisoformat(mtime_tehran)


def _jalali_parts_from_stamp(
    stamp: str, mtime_teh: datetime, jalali_date_time: str
) -> tuple[str, int, int, int, int, int]:
    if stamp:
        if " " in stamp:
            date_part, time_part = stamp.split(" ", 1)
            hh = int(time_part[0:2])
            mm = int(time_part[2:4])
        else:
            date_part = stamp
            hh = mtime_teh.hour
            mm = mtime_teh.minute
        jy = int(date_part[0:4])
        jm = int(date_part[4:6])
        jd = int(date_part[6:8])
        jalali_str = f"{jy:04d}/{jm:02d}/{jd:02d} {hh:02d}:{mm:02d}"
        return jalali_str, jy, jm, jd, hh, mm

    date_part, time_part = jalali_date_time.split(" ")
    jy, jm, jd = [int(x) for x in date_part.split("/")]
    hh, mm = [int(x) for x in time_part.split(":")]
    return jalali_date_time, jy, jm, jd, hh, mm


def run_stage(
    *,
    workspace_root: str,
    root: str,
    manifest: str,
    out: str,
    log: str,
    no_auto_normalize: bool,
    strict: bool,
) -> StageResult:
    workspace_abs = resolve_workspace_root(workspace_root)
    root_abs = resolve_path(workspace_abs, root)
    manifest_path = resolve_path(workspace_abs, manifest)
    out_path = resolve_path(workspace_abs, out)
    log_path = resolve_path(workspace_abs, log)

    result = StageResult(
        stage="plan_legacy_reorg",
        paths=StagePaths(
            workspace_root=workspace_abs,
            inputs={"root": root_abs, "manifest_jsonl": manifest_path},
            outputs={"relocation_plan": out_path, "plan_log": log_path},
        ),
    )

    if not os.path.isfile(manifest_path):
        emit_required_path_error(
            result, label="manifest.jsonl", abs_path=manifest_path, kind="file"
        )
        return result.finalize(strict=strict)

    effective_root = root_abs
    auto_normalize_msg = ""
    if not no_auto_normalize:
        normalized_root, did_normalize = auto_normalize_root(root_abs)
        if did_normalize:
            effective_root = normalized_root
            auto_normalize_msg = f"AUTO_NORMALIZE_ROOT: {root_abs} -> {effective_root}"

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    total_files = 0
    legacy_count = 0
    area_counts: dict[str, int] = {}
    conf_counts: dict[str, int] = {}
    legacy_rows = []

    with open(manifest_path, "r", encoding="utf-8") as f_in, open(
        out_path, "w", encoding="utf-8"
    ) as f_out:
        for line in f_in:
            total_files += 1
            row = json.loads(line)
            if row.get("legacy_candidate") != "true":
                continue

            legacy_count += 1
            src_rel = row["rel_path"]
            src_abs = os.path.join(effective_root, src_rel.replace("/", os.sep))
            size_bytes = int(row["size_bytes"])
            sha256 = row["sha256"]

            mtime_teh = _parse_mtime_tehran(row["mtime_tehran"])
            stamp = row.get("detected_stamp_from_name", "")
            jalali_str, jy, jm, jd, hh, mm = _jalali_parts_from_stamp(
                stamp, mtime_teh, row["jalali_date_time"]
            )

            if stamp:
                stamp_source = "name"
                confidence = "high"
            else:
                stamp_source = "mtime"
                confidence = "medium"

            area = _area_from_rel(src_rel)
            area_counts[area] = area_counts.get(area, 0) + 1
            conf_counts[confidence] = conf_counts.get(confidence, 0) + 1

            filename = os.path.basename(src_rel)
            if src_rel.lower().startswith("wordpipe/"):
                dst_rel = (
                    f"wordpipe/legacy/{area}/{jy:04d}/{jm:02d}/{jd:02d}/"
                    f"{hh:02d}{mm:02d}/{filename}"
                )
            elif src_rel.lower().startswith("wordhorrorstories/"):
                dst_rel = (
                    f"WordHorrorStories/legacy/{area}/{jy:04d}/{jm:02d}/{jd:02d}/"
                    f"{hh:02d}{mm:02d}/{filename}"
                )
            else:
                dst_rel = (
                    f"legacy/{area}/{jy:04d}/{jm:02d}/{jd:02d}/"
                    f"{hh:02d}{mm:02d}/{filename}"
                )

            plan_row = {
                "src_rel": src_rel,
                "src_abs": src_abs,
                "sha256": sha256,
                "size_bytes": size_bytes,
                "legacy_candidate": True,
                "stamp": {
                    "jalali": jalali_str,
                    "tehran": row["mtime_tehran"],
                    "source": stamp_source,
                    "confidence": confidence,
                },
                "area": area,
                "dst_rel": dst_rel,
                "rule_hits": _rule_hits(src_rel),
            }

            legacy_rows.append(plan_row)
            f_out.write(json.dumps(plan_row, ensure_ascii=False) + "\n")

    legacy_rows_sorted = sorted(legacy_rows, key=lambda r: r["size_bytes"], reverse=True)
    top10 = legacy_rows_sorted[:10]

    summary_lines = []
    if auto_normalize_msg:
        summary_lines.append(auto_normalize_msg)
    summary_lines.extend(
        [
            f"total_files: {total_files}",
            f"legacy_candidates: {legacy_count}",
            "breakdown_by_area:",
        ]
    )
    for area in sorted(area_counts):
        summary_lines.append(f"  {area}: {area_counts[area]}")
    summary_lines.append("breakdown_by_confidence:")
    for conf in sorted(conf_counts):
        summary_lines.append(f"  {conf}: {conf_counts[conf]}")
    summary_lines.append("top_10_largest_legacy:")
    for row in top10:
        summary_lines.append(f"  {row['size_bytes']} {row['src_rel']}")

    append_log_block(log_path, "plan_legacy_reorg summary", summary_lines)

    result.counters = {
        "total_files": total_files,
        "legacy_candidates": legacy_count,
    }
    result.generated_paths = {"relocation_plan": out_path}
    result.details["area_counts"] = area_counts
    result.details["confidence_counts"] = conf_counts
    result.details["summary_lines"] = summary_lines

    return result.finalize(strict=strict)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", default="_WORK/snapshot", help="Snapshot root (pre-normalization)."
    )
    parser.add_argument(
        "--manifest",
        default="_ARCHIVE/manifests/manifest.jsonl",
        help="Path to manifest.jsonl",
    )
    parser.add_argument(
        "--out",
        default="_ARCHIVE/move_maps/relocation_plan.jsonl",
        help="Output relocation plan jsonl",
    )
    parser.add_argument(
        "--log",
        default="_ARCHIVE/logs/plan.log",
        help="Summary log path",
    )
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
        manifest=args.manifest,
        out=args.out,
        log=args.log,
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
