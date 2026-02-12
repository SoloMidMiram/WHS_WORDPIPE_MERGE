"""Verify integrity and coverage of legacy/current/meta copies."""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_norm(path: str) -> str:
    return str(Path(path).resolve()).lower()


def load_jsonl(path: str) -> list[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def iter_files(root: str):
    for base, _dirs, files in os.walk(root):
        for name in files:
            yield os.path.join(base, name)


def main() -> None:
    workspace = Path(".").resolve()
    manifest_path = workspace / "_ARCHIVE" / "manifests" / "manifest.jsonl"
    relocation_path = workspace / "_ARCHIVE" / "move_maps" / "relocation_map.jsonl"
    meta_root = workspace / "_META" / "from_snapshot_20260211_205716"

    report_md = workspace / "_ARCHIVE" / "logs" / "verify_report.md"
    report_json = workspace / "_ARCHIVE" / "logs" / "verify_report.json"
    report_md.parent.mkdir(parents=True, exist_ok=True)

    manifest_rows = load_jsonl(str(manifest_path))
    relocation_rows = load_jsonl(str(relocation_path)) if relocation_path.exists() else []

    # Part A: Integrity
    status_counts = {}
    area_counts = {}
    failures = []

    for row in relocation_rows:
        status = row.get("status", "unknown")
        area = row.get("area", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        area_counts[area] = area_counts.get(area, 0) + 1

        if status in {"copied", "skipped_same"}:
            dst_abs = row.get("dst_abs")
            expected = row.get("sha256")
            if not dst_abs or not os.path.isfile(dst_abs):
                failures.append(
                    {"type": "missing_dst", "dst_abs": dst_abs, "status": status}
                )
                continue
            actual = sha256_file(dst_abs)
            if actual != expected:
                failures.append(
                    {
                        "type": "hash_mismatch",
                        "dst_abs": dst_abs,
                        "expected": expected,
                        "actual": actual,
                    }
                )
        elif status == "conflict":
            conflict_path = row.get("conflict_path")
            if not conflict_path or not os.path.isfile(conflict_path):
                failures.append(
                    {
                        "type": "missing_conflict",
                        "conflict_path": conflict_path,
                    }
                )

    integrity = {
        "status_counts": status_counts,
        "area_counts": area_counts,
        "failures": failures,
    }

    # Part B: Coverage
    accounted = {}
    scan_roots = [
        workspace / "wordpipe",
        workspace / "WordHorrorStories",
        workspace / "_META",
    ]
    for root in scan_roots:
        if not root.exists():
            continue
        for path in iter_files(str(root)):
            h = sha256_file(path)
            accounted.setdefault(h, []).append(resolve_norm(path))

    unaccounted = []
    for row in manifest_rows:
        h = row.get("sha256")
        if h not in accounted:
            unaccounted.append(row.get("rel_path"))

    duplicates_map = {h: paths for h, paths in accounted.items() if len(paths) > 1}
    duplicate_present = [
        {"sha256": h, "paths": paths} for h, paths in sorted(duplicates_map.items())
    ]

    coverage = {
        "total_manifest_files": len(manifest_rows),
        "accounted_files": len(manifest_rows) - len(unaccounted),
        "unaccounted_files": len(unaccounted),
        "duplicates_count": len(duplicates_map),
        "unaccounted": unaccounted,
        "duplicate_present": duplicate_present,
    }

    output = {"integrity": integrity, "coverage": coverage}
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Markdown report
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md_lines = [
        "# Verify Report",
        "",
        f"Generated: {now}",
        "",
        "## Integrity",
        f"- Status counts: {status_counts}",
        f"- Area counts: {area_counts}",
        f"- Failures: {len(failures)}",
    ]
    if failures:
        md_lines.append("")
        md_lines.append("### Failure Details")
        for fail in failures:
            md_lines.append(f"- {fail}")

    md_lines.extend(
        [
            "",
            "## Coverage",
            f"- Total manifest files: {coverage['total_manifest_files']}",
            f"- Accounted files: {coverage['accounted_files']}",
            f"- Unaccounted files: {coverage['unaccounted_files']}",
            f"- Duplicates count: {coverage['duplicates_count']}",
        ]
    )
    if unaccounted:
        md_lines.append("")
        md_lines.append("### Unaccounted rel_paths")
        for rel in unaccounted:
            md_lines.append(f"- {rel}")
    if duplicate_present:
        md_lines.append("")
        md_lines.append("### Duplicates (sha256)")
        for dup in duplicate_present:
            md_lines.append(f"- {dup['sha256']}:")
            for p in dup["paths"]:
                md_lines.append(f"  - {p}")

    with open(report_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"Wrote {report_md}")
    print(f"Wrote {report_json}")


if __name__ == "__main__":
    main()
