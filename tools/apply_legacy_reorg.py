"""Apply legacy relocation plan: copy-only, dedupe, conflict-safe."""

import argparse
import hashlib
import json
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


def _safe_copy(src: str, dst: str) -> tuple[str, str | None]:
    """Copy src -> dst. If dst exists, compare sha256.
    Returns (status, conflict_path).
    status: copied | skipped_same | conflict
    """
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


def _iter_files(root: str):
    for base, _dirs, files in os.walk(root):
        for name in files:
            yield os.path.join(base, name)


def _log_append(log_path: str, lines: list[str]) -> None:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] apply_legacy_reorg summary\n")
        for line in lines:
            f.write(line + "\n")


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

    plan_path = os.path.abspath(args.plan)
    out_map_path = os.path.abspath(args.out_map)
    log_path = os.path.abspath(args.log)

    os.makedirs(os.path.dirname(out_map_path), exist_ok=True)

    with open(plan_path, "r", encoding="utf-8") as f_plan:
        plan_rows = [json.loads(line) for line in f_plan]

    legacy_src_rel = {row["src_rel"] for row in plan_rows}

    # Create clean roots
    os.makedirs("wordpipe", exist_ok=True)
    os.makedirs("WordHorrorStories", exist_ok=True)

    # Copy current files
    copied_current = 0
    skipped_current_same = 0
    current_conflicts = 0
    unmapped_misc = 0
    errors = 0

    for path in _iter_files(effective_root):
        rel = os.path.relpath(path, effective_root).replace("\\", "/")
        rel_lower = rel.lower()
        if rel in legacy_src_rel:
            continue
        if "/legacy/" in rel_lower:
            continue

        if rel_lower.startswith("wordpipe/"):
            sub = rel[len("wordpipe/") :]
            dst = os.path.join("wordpipe", sub)
        elif rel_lower.startswith("wordhorrorstories/"):
            sub = rel[len("wordhorrorstories/") :]
            dst = os.path.join("WordHorrorStories", sub)
        else:
            unmapped_misc += 1
            continue

        try:
            status, _conflict = _safe_copy(path, dst)
            if status == "copied":
                copied_current += 1
            elif status == "skipped_same":
                skipped_current_same += 1
            else:
                current_conflicts += 1
        except Exception:
            errors += 1

    # Apply legacy plan
    legacy_copied = 0
    legacy_skipped_same = 0
    legacy_conflicts = 0
    largest_legacy = []

    with open(out_map_path, "w", encoding="utf-8") as f_out:
        for row in plan_rows:
            src_abs = row["src_abs"]
            dst_rel = row["dst_rel"]
            dst_abs = os.path.abspath(dst_rel)
            try:
                status, conflict_path = _safe_copy(src_abs, dst_abs)
                if status == "copied":
                    legacy_copied += 1
                    largest_legacy.append((row["size_bytes"], row["src_rel"]))
                elif status == "skipped_same":
                    legacy_skipped_same += 1
                else:
                    legacy_conflicts += 1

                out_row = {
                    "src_abs": src_abs,
                    "dst_abs": dst_abs,
                    "sha256": row["sha256"],
                    "status": status,
                    "conflict_path": conflict_path,
                    "stamp": row["stamp"],
                    "area": row["area"],
                    "rule_hits": row["rule_hits"],
                }
                f_out.write(json.dumps(out_row, ensure_ascii=False) + "\n")
            except Exception:
                errors += 1

    largest_legacy_sorted = sorted(largest_legacy, key=lambda x: x[0], reverse=True)[:10]

    summary = [
        f"copied_current: {copied_current}",
        f"skipped_current_same: {skipped_current_same}",
        f"current_conflicts: {current_conflicts}",
        f"unmapped_misc: {unmapped_misc}",
        f"legacy_copied: {legacy_copied}",
        f"legacy_skipped_same: {legacy_skipped_same}",
        f"legacy_conflicts: {legacy_conflicts}",
        f"errors: {errors}",
        "top_10_largest_legacy_copied:",
    ]
    for size, rel in largest_legacy_sorted:
        summary.append(f"  {size} {rel}")

    _log_append(log_path, summary)
    print("\n".join(summary))


if __name__ == "__main__":
    main()
