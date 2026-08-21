"""Apply legacy relocation plan: copy-only, dedupe, conflict-safe."""

from __future__ import annotations

import argparse
import json
import os

from pipeline_contracts import (
    StagePaths,
    StageResult,
    emit_required_path_error,
    resolve_path,
    resolve_workspace_root,
    write_summary_json,
)
from tool_common import auto_normalize_root, append_log_block, safe_copy_with_conflict


def _iter_files(root: str):
    for base, _dirs, files in os.walk(root):
        for name in files:
            yield os.path.join(base, name)


def _count_existing_files(root: str) -> int:
    if not os.path.isdir(root):
        return 0
    count = 0
    for _base, _dirs, files in os.walk(root):
        count += len(files)
    return count


def _write_conflict_log(conflict_log_path: str, conflict_rows: list[dict]) -> None:
    lines = []
    for row in conflict_rows:
        lines.append(
            "phase={phase} src={src} dst={dst} conflict_path={conflict_path} "
            "src_sha256={src_sha256} dst_sha256={dst_sha256}".format(
                phase=row["phase"],
                src=row["src"],
                dst=row["dst"],
                conflict_path=row["conflict_path"],
                src_sha256=row["src_sha256"],
                dst_sha256=row["dst_sha256"],
            )
        )
    lines.append(f"conflicts_total: {len(conflict_rows)}")
    append_log_block(conflict_log_path, "apply_legacy_reorg conflicts", lines)


def run_stage(
    *,
    workspace_root: str,
    root: str,
    plan: str,
    out_map: str,
    log: str,
    conflict_log: str,
    preflight_mode: str,
    no_auto_normalize: bool,
    strict: bool,
) -> StageResult:
    workspace_abs = resolve_workspace_root(workspace_root)
    root_abs = resolve_path(workspace_abs, root)
    plan_path = resolve_path(workspace_abs, plan)
    out_map_path = resolve_path(workspace_abs, out_map)
    log_path = resolve_path(workspace_abs, log)
    conflict_log_path = resolve_path(workspace_abs, conflict_log)
    wordpipe_root = resolve_path(workspace_abs, "wordpipe")
    whs_root = resolve_path(workspace_abs, "WordHorrorStories")

    result = StageResult(
        stage="apply_legacy_reorg",
        paths=StagePaths(
            workspace_root=workspace_abs,
            inputs={"root": root_abs, "relocation_plan": plan_path},
            outputs={
                "relocation_map": out_map_path,
                "apply_log": log_path,
                "conflict_log": conflict_log_path,
            },
        ),
    )

    if not os.path.isfile(plan_path):
        emit_required_path_error(
            result, label="relocation_plan.jsonl", abs_path=plan_path, kind="file"
        )
        return result.finalize(strict=strict)

    effective_root = root_abs
    auto_normalize_msg = ""
    if not no_auto_normalize:
        normalized_root, did_normalize = auto_normalize_root(root_abs)
        if did_normalize:
            effective_root = normalized_root
            auto_normalize_msg = f"AUTO_NORMALIZE_ROOT: {root_abs} -> {effective_root}"

    os.makedirs(os.path.dirname(out_map_path), exist_ok=True)
    with open(plan_path, "r", encoding="utf-8") as f_plan:
        plan_rows = [json.loads(line) for line in f_plan]

    legacy_src_rel = {row["src_rel"] for row in plan_rows}

    preflight_wordpipe_files = _count_existing_files(wordpipe_root)
    preflight_wordhorrorstories_files = _count_existing_files(whs_root)
    preflight_total = preflight_wordpipe_files + preflight_wordhorrorstories_files

    preflight_lines = [
        f"preflight_mode: {preflight_mode}",
        f"preflight_wordpipe_files: {preflight_wordpipe_files}",
        f"preflight_WordHorrorStories_files: {preflight_wordhorrorstories_files}",
    ]
    if preflight_mode == "off":
        preflight_lines.append("preflight_decision: skipped")
    elif preflight_total == 0:
        preflight_lines.append("preflight_decision: continue")
    elif preflight_mode == "warn":
        msg = "destination trees are non-empty; copy-only apply continues"
        preflight_lines.append("preflight_decision: continue_with_warning")
        preflight_lines.append(f"preflight_warning: {msg}")
        result.add_warning(msg)
    else:
        preflight_lines.append("preflight_decision: abort_non_empty_destinations")
        _write_conflict_log(conflict_log_path, [])
        aborted_summary = preflight_lines + [
            "copied_current: 0",
            "skipped_current_same: 0",
            "current_conflicts: 0",
            "unmapped_misc: 0",
            "legacy_copied: 0",
            "legacy_skipped_same: 0",
            "legacy_conflicts: 0",
            "errors: 1",
            "top_10_largest_legacy_copied:",
        ]
        append_log_block(log_path, "apply_legacy_reorg summary", aborted_summary)
        result.add_error(
            "PREFLIGHT_ABORT",
            "destination trees are non-empty; rerun with --preflight-mode warn or off",
            {
                "wordpipe_files": preflight_wordpipe_files,
                "wordhorrorstories_files": preflight_wordhorrorstories_files,
            },
        )
        result.counters = {
            "copied_current": 0,
            "skipped_current_same": 0,
            "current_conflicts": 0,
            "unmapped_misc": 0,
            "legacy_copied": 0,
            "legacy_skipped_same": 0,
            "legacy_conflicts": 0,
            "errors": 1,
        }
        result.details["summary_lines"] = (
            [auto_normalize_msg] if auto_normalize_msg else []
        ) + aborted_summary
        return result.finalize(strict=strict)

    os.makedirs(wordpipe_root, exist_ok=True)
    os.makedirs(whs_root, exist_ok=True)

    copied_current = 0
    skipped_current_same = 0
    current_conflicts = 0
    unmapped_misc = 0
    errors = 0
    conflict_rows: list[dict] = []

    for path in _iter_files(effective_root):
        rel = os.path.relpath(path, effective_root).replace("\\", "/")
        rel_lower = rel.lower()
        if rel in legacy_src_rel:
            continue
        if "/legacy/" in rel_lower:
            continue

        if rel_lower.startswith("wordpipe/"):
            sub = rel[len("wordpipe/") :]
            dst = os.path.join(wordpipe_root, sub)
        elif rel_lower.startswith("wordhorrorstories/"):
            sub = rel[len("wordhorrorstories/") :]
            dst = os.path.join(whs_root, sub)
        else:
            unmapped_misc += 1
            continue

        try:
            status, conflict_path, src_hash, dst_hash = safe_copy_with_conflict(path, dst)
            if status == "copied":
                copied_current += 1
            elif status == "skipped_same":
                skipped_current_same += 1
            else:
                current_conflicts += 1
                conflict_rows.append(
                    {
                        "phase": "current",
                        "src": path,
                        "dst": os.path.abspath(dst),
                        "conflict_path": conflict_path,
                        "src_sha256": src_hash,
                        "dst_sha256": dst_hash,
                    }
                )
        except Exception as exc:
            errors += 1
            result.add_error(
                "CURRENT_COPY_ERROR",
                f"Failed copying current file: {path}",
                {"error": str(exc)},
            )

    legacy_copied = 0
    legacy_skipped_same = 0
    legacy_conflicts = 0
    largest_legacy = []

    with open(out_map_path, "w", encoding="utf-8") as f_out:
        for row in plan_rows:
            src_abs = row["src_abs"]
            dst_rel = row["dst_rel"]
            dst_abs = resolve_path(workspace_abs, dst_rel)
            try:
                status, conflict_path, src_hash, dst_hash = safe_copy_with_conflict(
                    src_abs, dst_abs
                )
                if status == "copied":
                    legacy_copied += 1
                    largest_legacy.append((row["size_bytes"], row["src_rel"]))
                elif status == "skipped_same":
                    legacy_skipped_same += 1
                else:
                    legacy_conflicts += 1
                    conflict_rows.append(
                        {
                            "phase": "legacy",
                            "src": src_abs,
                            "dst": dst_abs,
                            "conflict_path": conflict_path,
                            "src_sha256": src_hash,
                            "dst_sha256": dst_hash,
                        }
                    )

                out_row = {
                    "src_rel": row["src_rel"],
                    "src_abs": src_abs,
                    "dst_rel": dst_rel,
                    "dst_abs": dst_abs,
                    "sha256": row["sha256"],
                    "status": status,
                    "conflict_path": conflict_path,
                    "conflict_path_rel": (
                        os.path.relpath(conflict_path, workspace_abs).replace(
                            os.sep, "/"
                        )
                        if conflict_path
                        else None
                    ),
                    "stamp": row["stamp"],
                    "area": row["area"],
                    "rule_hits": row["rule_hits"],
                }
                f_out.write(json.dumps(out_row, ensure_ascii=False) + "\n")
            except Exception as exc:
                errors += 1
                result.add_error(
                    "LEGACY_COPY_ERROR",
                    f"Failed applying relocation row for source: {src_abs}",
                    {"error": str(exc)},
                )

    _write_conflict_log(conflict_log_path, conflict_rows)

    largest_legacy_sorted = sorted(largest_legacy, key=lambda x: x[0], reverse=True)[:10]
    summary = []
    if auto_normalize_msg:
        summary.append(auto_normalize_msg)
    summary.extend(
        preflight_lines
        + [
            f"copied_current: {copied_current}",
            f"skipped_current_same: {skipped_current_same}",
            f"current_conflicts: {current_conflicts}",
            f"unmapped_misc: {unmapped_misc}",
            f"legacy_copied: {legacy_copied}",
            f"legacy_skipped_same: {legacy_skipped_same}",
            f"legacy_conflicts: {legacy_conflicts}",
            f"errors: {errors}",
            f"conflict_log: {conflict_log_path}",
            "top_10_largest_legacy_copied:",
        ]
    )
    for size, rel in largest_legacy_sorted:
        summary.append(f"  {size} {rel}")

    append_log_block(log_path, "apply_legacy_reorg summary", summary)

    result.counters = {
        "copied_current": copied_current,
        "skipped_current_same": skipped_current_same,
        "current_conflicts": current_conflicts,
        "unmapped_misc": unmapped_misc,
        "legacy_copied": legacy_copied,
        "legacy_skipped_same": legacy_skipped_same,
        "legacy_conflicts": legacy_conflicts,
        "errors": errors,
    }
    result.generated_paths = {
        "relocation_map": out_map_path,
        "conflict_log": conflict_log_path,
    }
    result.details["summary_lines"] = summary

    return result.finalize(strict=strict)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="_WORK/snapshot")
    parser.add_argument(
        "--plan",
        default="_ARCHIVE/move_maps/relocation_plan.jsonl",
        help="Relocation plan input.",
    )
    parser.add_argument(
        "--out-map",
        default="_ARCHIVE/move_maps/relocation_map.jsonl",
        help="Relocation map output.",
    )
    parser.add_argument(
        "--log",
        default="_ARCHIVE/logs/apply_reorg.log",
        help="Apply log output.",
    )
    parser.add_argument(
        "--conflict-log",
        default="_ARCHIVE/logs/conflicts.log",
        help="Conflict summary log output.",
    )
    parser.add_argument(
        "--preflight-mode",
        choices=("warn", "error", "off"),
        default="warn",
        help="How to handle non-empty destination trees.",
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
        plan=args.plan,
        out_map=args.out_map,
        log=args.log,
        conflict_log=args.conflict_log,
        preflight_mode=args.preflight_mode,
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
