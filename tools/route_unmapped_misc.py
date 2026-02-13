"""Route snapshot root docs into _META (copy-only)."""

import argparse
import os
from tool_common import auto_normalize_root, append_log_block, safe_copy_with_conflict


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="_WORK/snapshot")
    parser.add_argument(
        "--dest",
        default="_META/from_snapshot_20260211_205716",
        help="Destination folder for routed root docs.",
    )
    parser.add_argument(
        "--log",
        default="_ARCHIVE/logs/route_unmapped.log",
        help="Log path.",
    )
    parser.add_argument(
        "--no-auto-normalize",
        action="store_true",
        help="Disable auto-normalization for nested snapshot/snapshot roots.",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    effective_root = root
    if not args.no_auto_normalize:
        normalized_root, did_normalize = auto_normalize_root(root)
        if did_normalize:
            effective_root = normalized_root

    dest_root = os.path.abspath(args.dest)
    log_path = os.path.abspath(args.log)

    targets = ["README.md", "MERGE_MAP.md"]
    copied = 0
    skipped = 0
    conflicts = 0
    missing = 0
    log_lines = []

    for name in targets:
        src = os.path.join(effective_root, name)
        if not os.path.isfile(src):
            missing += 1
            log_lines.append(f"missing: {name}")
            continue

        dst = os.path.join(dest_root, name)
        status, conflict_path, _src_hash, _dst_hash = safe_copy_with_conflict(src, dst)
        if status == "copied":
            copied += 1
            log_lines.append(f"copied: {name} -> {dst}")
        elif status == "skipped_same":
            skipped += 1
            log_lines.append(f"skipped_same: {name}")
        else:
            conflicts += 1
            log_lines.append(f"conflict: {name} -> {conflict_path}")

    summary = [
        f"copied: {copied}",
        f"skipped_same: {skipped}",
        f"conflicts: {conflicts}",
        f"missing: {missing}",
    ]
    log_lines.extend(summary)
    append_log_block(log_path, "route_unmapped_misc", log_lines)
    print("\n".join(summary))


if __name__ == "__main__":
    main()
