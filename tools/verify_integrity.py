"""Verify integrity and coverage of legacy/current/meta copies."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from pipeline_contracts import (
    StagePaths,
    StageResult,
    emit_required_path_error,
    resolve_path,
    resolve_workspace_root,
    write_summary_json,
)
from tool_common import auto_normalize_root, sha256_file


def resolve_norm(path: str) -> str:
    return str(Path(path).resolve()).lower()


def rel_to_workspace(path: str, workspace_abs: str) -> str:
    """Return a repo-relative path (forward slashes) when under workspace_abs."""
    if not path:
        return path
    try:
        path_abs = os.path.abspath(path)
        workspace_abs = os.path.abspath(workspace_abs)
        common = os.path.normcase(os.path.commonpath([path_abs, workspace_abs]))
        if common != os.path.normcase(workspace_abs):
            return path
        return os.path.relpath(path_abs, workspace_abs).replace(os.sep, "/")
    except ValueError:
        return path


def row_path(
    row: dict,
    *,
    rel_key: str,
    abs_key: str,
    workspace_abs: str,
    portable: bool,
) -> str | None:
    """Prefer a row's portable path while retaining absolute-path compatibility."""
    if portable and row.get(rel_key):
        return resolve_path(workspace_abs, row[rel_key])
    return row.get(abs_key)


def source_identity(row: dict, *, portable: bool) -> tuple[str, str] | None:
    """Return a normalized relocation source identity for consistency checks."""
    if portable and row.get("src_rel"):
        rel = os.path.normpath(row["src_rel"].replace("/", os.sep))
        return ("rel", rel.replace(os.sep, "/").casefold())
    if row.get("src_abs"):
        return ("abs", resolve_norm(row["src_abs"]))
    return None


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


def build_consistency(
    plan_rows: list[dict], relocation_rows: list[dict], *, portable: bool = False
) -> dict:
    plan_keys: dict[tuple[str, str], str] = {}
    for row in plan_rows:
        key = source_identity(row, portable=portable)
        src_rel = row.get("src_rel", "")
        if key:
            plan_keys[key] = src_rel

    map_keys: dict[tuple[str, str], list[dict]] = {}
    status_counts: dict[str, int] = {}
    for row in relocation_rows:
        key = source_identity(row, portable=portable)
        if key:
            map_keys.setdefault(key, []).append(row)
        status = row.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    missing_in_map = [
        src_rel for key, src_rel in sorted(plan_keys.items()) if key not in map_keys
    ]
    extra_in_map = []
    duplicate_src_in_map = []
    for key, rows in sorted(map_keys.items()):
        if key not in plan_keys:
            extra_in_map.append(rows[0].get("src_abs"))
        if len(rows) > 1:
            duplicate_src_in_map.append(rows[0].get("src_abs"))

    ok = not missing_in_map and not extra_in_map and not duplicate_src_in_map
    return {
        "plan_rows": len(plan_rows),
        "map_rows": len(relocation_rows),
        "missing_in_map": missing_in_map,
        "extra_in_map": extra_in_map,
        "duplicate_src_in_map": duplicate_src_in_map,
        "status_counts": status_counts,
        "ok": ok,
    }


def build_immutability(
    manifest_rows: list[dict], snapshot_root: str, normalized_snapshot_root: str
) -> dict:
    missing_source_files = []
    hash_mismatches = []
    checked_rows = 0

    for row in manifest_rows:
        rel_path = row.get("rel_path", "")
        expected = row.get("sha256")
        src_abs = os.path.join(normalized_snapshot_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(src_abs):
            missing_source_files.append(rel_path)
            continue
        actual = sha256_file(src_abs)
        checked_rows += 1
        if actual != expected:
            hash_mismatches.append(
                {
                    "rel_path": rel_path,
                    "expected": expected,
                    "actual": actual,
                }
            )

    return {
        "snapshot_root": snapshot_root,
        "effective_snapshot_root": normalized_snapshot_root,
        "manifest_rows": len(manifest_rows),
        "checked_rows": checked_rows,
        "missing_source_files": missing_source_files,
        "hash_mismatches": hash_mismatches,
        "ok": not missing_source_files and not hash_mismatches,
    }


def run_stage(
    *,
    workspace_root: str,
    manifest: str,
    plan: str,
    relocation: str,
    snapshot_root: str,
    strict: bool,
    portable: bool = False,
) -> StageResult:
    workspace_abs = resolve_workspace_root(workspace_root)
    manifest_path = resolve_path(workspace_abs, manifest)
    plan_path = resolve_path(workspace_abs, plan)
    relocation_path = resolve_path(workspace_abs, relocation)
    snapshot_root_path = resolve_path(workspace_abs, snapshot_root)

    report_md = resolve_path(workspace_abs, "_ARCHIVE/logs/verify_report.md")
    report_json = resolve_path(workspace_abs, "_ARCHIVE/logs/verify_report.json")
    consistency_json = resolve_path(workspace_abs, "_ARCHIVE/logs/consistency_report.json")
    immutability_json = resolve_path(workspace_abs, "_ARCHIVE/logs/immutability_report.json")

    result = StageResult(
        stage="verify_integrity",
        paths=StagePaths(
            workspace_root=workspace_abs,
            inputs={
                "manifest_jsonl": manifest_path,
                "relocation_plan": plan_path,
                "relocation_map": relocation_path,
                "snapshot_root": snapshot_root_path,
            },
            outputs={
                "verify_report_md": report_md,
                "verify_report_json": report_json,
                "consistency_report_json": consistency_json,
                "immutability_report_json": immutability_json,
            },
        ),
    )

    if not os.path.isfile(manifest_path):
        emit_required_path_error(
            result, label="manifest.jsonl", abs_path=manifest_path, kind="file"
        )
        return result.finalize(strict=strict)
    if not os.path.isdir(snapshot_root_path):
        emit_required_path_error(
            result,
            label="snapshot root directory",
            abs_path=snapshot_root_path,
            kind="directory",
        )
        return result.finalize(strict=strict)

    if not os.path.isfile(plan_path):
        result.add_warning(f"relocation plan not found: {plan_path}")
    if not os.path.isfile(relocation_path):
        result.add_warning(f"relocation map not found: {relocation_path}")

    manifest_rows = load_jsonl(manifest_path)
    plan_rows = load_jsonl(plan_path) if os.path.isfile(plan_path) else []
    relocation_rows = load_jsonl(relocation_path) if os.path.isfile(relocation_path) else []

    status_counts = {}
    area_counts = {}
    failures = []
    for row in relocation_rows:
        status = row.get("status", "unknown")
        area = row.get("area", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        area_counts[area] = area_counts.get(area, 0) + 1
        if status in {"copied", "skipped_same"}:
            dst_abs = row_path(
                row,
                rel_key="dst_rel",
                abs_key="dst_abs",
                workspace_abs=workspace_abs,
                portable=portable,
            )
            expected = row.get("sha256")
            if not dst_abs or not os.path.isfile(dst_abs):
                entry = {"type": "missing_dst", "dst_abs": dst_abs, "status": status}
                if portable:
                    entry["dst_rel"] = rel_to_workspace(dst_abs, workspace_abs)
                failures.append(entry)
                continue
            actual = sha256_file(dst_abs)
            if actual != expected:
                entry = {
                    "type": "hash_mismatch",
                    "dst_abs": dst_abs,
                    "expected": expected,
                    "actual": actual,
                }
                if portable:
                    entry["dst_rel"] = rel_to_workspace(dst_abs, workspace_abs)
                failures.append(entry)
        elif status == "conflict":
            conflict_path = row_path(
                row,
                rel_key="conflict_path_rel",
                abs_key="conflict_path",
                workspace_abs=workspace_abs,
                portable=portable,
            )
            if not conflict_path or not os.path.isfile(conflict_path):
                entry = {
                    "type": "missing_conflict",
                    "conflict_path": conflict_path,
                }
                if portable:
                    entry["conflict_path_rel"] = rel_to_workspace(conflict_path, workspace_abs)
                failures.append(entry)

    integrity = {
        "status_counts": status_counts,
        "area_counts": area_counts,
        "failures": failures,
    }

    accounted = {}
    scan_roots = [
        resolve_path(workspace_abs, "wordpipe"),
        resolve_path(workspace_abs, "WordHorrorStories"),
        resolve_path(workspace_abs, "_META"),
    ]
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for path in iter_files(root):
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
    os.makedirs(os.path.dirname(report_json), exist_ok=True)
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    consistency = build_consistency(plan_rows, relocation_rows, portable=portable)
    with open(consistency_json, "w", encoding="utf-8") as f:
        json.dump(consistency, f, ensure_ascii=False, indent=2)

    normalized_snapshot_root, did_normalize = auto_normalize_root(snapshot_root_path)
    effective_snapshot_root = normalized_snapshot_root if did_normalize else snapshot_root_path

    immutability = build_immutability(
        manifest_rows=manifest_rows,
        snapshot_root=snapshot_root_path,
        normalized_snapshot_root=effective_snapshot_root,
    )
    with open(immutability_json, "w", encoding="utf-8") as f:
        json.dump(immutability, f, ensure_ascii=False, indent=2)

    if failures:
        result.add_warning(f"integrity failures: {len(failures)}")
    if coverage["unaccounted_files"] > 0:
        result.add_warning(f"coverage unaccounted files: {coverage['unaccounted_files']}")
    if not consistency["ok"]:
        result.add_warning("consistency report is not OK")
    if not immutability["ok"]:
        result.add_warning("immutability report is not OK")

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

    md_lines.extend(
        [
            "",
            "## Consistency",
            f"- Plan rows: {consistency['plan_rows']}",
            f"- Map rows: {consistency['map_rows']}",
            f"- Missing in map: {len(consistency['missing_in_map'])}",
            f"- Extra in map: {len(consistency['extra_in_map'])}",
            f"- Duplicate src in map: {len(consistency['duplicate_src_in_map'])}",
            f"- OK: {consistency['ok']}",
        ]
    )
    md_lines.extend(
        [
            "",
            "## Immutability",
            f"- Snapshot root: {immutability['snapshot_root']}",
            f"- Effective snapshot root: {immutability['effective_snapshot_root']}",
            f"- Manifest rows: {immutability['manifest_rows']}",
            f"- Checked rows: {immutability['checked_rows']}",
            f"- Missing source files: {len(immutability['missing_source_files'])}",
            f"- Hash mismatches: {len(immutability['hash_mismatches'])}",
            f"- OK: {immutability['ok']}",
        ]
    )
    if duplicate_present:
        md_lines.append("")
        md_lines.append("### Duplicates (sha256)")
        for dup in duplicate_present:
            md_lines.append(f"- {dup['sha256']}:")
            for p in dup["paths"]:
                md_lines.append(f"  - {p}")

    with open(report_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    result.counters = {
        "integrity_failures": len(failures),
        "total_manifest_files": coverage["total_manifest_files"],
        "accounted_files": coverage["accounted_files"],
        "unaccounted_files": coverage["unaccounted_files"],
        "duplicates_count": coverage["duplicates_count"],
        "consistency_ok": int(consistency["ok"]),
        "immutability_ok": int(immutability["ok"]),
    }
    result.generated_paths = {
        "verify_report_md": report_md,
        "verify_report_json": report_json,
        "consistency_report_json": consistency_json,
        "immutability_report_json": immutability_json,
    }
    result.details["summary_lines"] = [
        f"Wrote {report_md}",
        f"Wrote {report_json}",
        f"Wrote {consistency_json}",
        f"Wrote {immutability_json}",
    ]

    return result.finalize(strict=strict)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default="_ARCHIVE/manifests/manifest.jsonl",
        help="Manifest input path.",
    )
    parser.add_argument(
        "--plan",
        default="_ARCHIVE/move_maps/relocation_plan.jsonl",
        help="Relocation plan input path.",
    )
    parser.add_argument(
        "--relocation",
        default="_ARCHIVE/move_maps/relocation_map.jsonl",
        help="Relocation map input path.",
    )
    parser.add_argument(
        "--snapshot-root",
        default="_WORK/snapshot",
        help="Snapshot root path for immutability verification.",
    )
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--summary-json", default="")
    parser.add_argument(
        "--portable",
        action="store_true",
        help=(
            "Prefer repo-relative relocation paths resolved against --workspace-root "
            "and emit them alongside absolute diagnostics."
        ),
    )
    strictness = parser.add_mutually_exclusive_group()
    strictness.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (the default; retained for compatibility).",
    )
    strictness.add_argument(
        "--diagnostic-only",
        action="store_true",
        help="Run in diagnostic-only mode: warnings do not cause non-zero exit.",
    )
    args = parser.parse_args()

    result = run_stage(
        workspace_root=args.workspace_root,
        manifest=args.manifest,
        plan=args.plan,
        relocation=args.relocation,
        snapshot_root=args.snapshot_root,
        strict=not args.diagnostic_only,
        portable=args.portable,
    )

    for line in result.details.get("summary_lines", []):
        print(line)

    if args.summary_json:
        summary_json_path = resolve_path(result.paths.workspace_root, args.summary_json)
        write_summary_json(summary_json_path, result)

    raise SystemExit(1 if result.status == "error" else 0)


if __name__ == "__main__":
    main()
