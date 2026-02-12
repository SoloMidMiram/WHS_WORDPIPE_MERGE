"""Route snapshot root docs into _META (copy-only)."""

import argparse
import hashlib
import os
import shutil
from datetime import datetime


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


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _log_append(log_path: str, lines: list[str]) -> None:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] route_unmapped_misc\n")
        for line in lines:
            f.write(line + "\n")


def _safe_copy(src: str, dst: str) -> tuple[str, str | None]:
    if os.path.exists(dst):
        src_hash = sha256_file(src)
        dst_hash = sha256_file(dst)
        if src_hash == dst_hash:
            return "skipped_same", None
        base, ext = os.path.splitext(os.path.basename(dst))
        conflict_name = f"{base}__{src_hash[:8]}{ext}"
        conflict_path = os.path.join(os.path.dirname(dst), "_conflicts", conflict_name)
        os.makedirs(os.path.dirname(conflict_path), exist_ok=True)
        shutil.copy2(src, conflict_path)
        return "conflict", conflict_path

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return "copied", None


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
        normalized_root, did_normalize = _auto_normalize_root(root)
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
        status, conflict_path = _safe_copy(src, dst)
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
    _log_append(log_path, log_lines)
    print("\n".join(summary))


if __name__ == "__main__":
    main()
