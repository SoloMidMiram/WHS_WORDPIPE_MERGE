"""Build legacy index docs for wordpipe and WordHorrorStories."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from pipeline_contracts import (
    StagePaths,
    StageResult,
    resolve_path,
    resolve_workspace_root,
    write_summary_json,
)
from tool_common import append_log_block

TOKENS = ["after", "chunks", "no ai", "save"]


def _load_relocation_map(path: str) -> dict[str, dict]:
    if not os.path.isfile(path):
        return {}
    mapping = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            dst_abs = row.get("dst_abs")
            if dst_abs:
                mapping[str(Path(dst_abs).resolve()).lower()] = row
    return mapping


def _tree_lines(root: str, max_depth: int) -> list[str]:
    lines = []

    def recurse(path: str, depth: int):
        if depth > max_depth:
            return
        try:
            items = sorted(
                os.listdir(path),
                key=lambda n: (not os.path.isdir(os.path.join(path, n)), n.lower()),
            )
        except FileNotFoundError:
            return
        for name in items:
            full = os.path.join(path, name)
            indent = "  " * depth
            if os.path.isdir(full):
                lines.append(f"{indent}{name}/")
                recurse(full, depth + 1)
            else:
                lines.append(f"{indent}{name}")

    lines.append(f"{os.path.basename(root)}/")
    recurse(root, 1)
    return lines


def _is_bucket(path_parts: list[str]) -> bool:
    if len(path_parts) == 5:
        jy, jm, jd, hhmm = path_parts[1:]
    elif len(path_parts) == 6:
        jy, jm, jd, hhmm = path_parts[-4:]
    else:
        return False
    return (
        len(jy) == 4
        and len(jm) == 2
        and len(jd) == 2
        and len(hhmm) == 4
        and jy.isdigit()
        and jm.isdigit()
        and jd.isdigit()
        and hhmm.isdigit()
    )


def _normalize_text(text: str) -> str:
    normalized = text.lower().replace("_", " ").replace("-", " ")
    return " ".join(normalized.split())


def _bucket_key(root: str, bucket_path: str) -> str:
    return os.path.relpath(bucket_path, root).replace("\\", "/")


def _collect_buckets(legacy_root: str) -> dict[str, dict]:
    buckets = {}
    for base, _dirs, files in os.walk(legacy_root):
        parts = os.path.relpath(base, legacy_root).split(os.sep)
        if parts == ["."]:
            continue
        if _is_bucket(parts):
            bucket_rel = _bucket_key(legacy_root, base)
            bucket_files = [f for f in files if os.path.isfile(os.path.join(base, f))]
            buckets[bucket_rel] = {
                "path": base,
                "files": sorted(bucket_files, key=lambda n: n.lower()),
            }
    return buckets


def _bucket_area(bucket_rel: str) -> str:
    parts = bucket_rel.split("/")
    return parts[0] if parts else "unknown"


def _compute_bucket_stats(
    bucket_path: str, files: list[str], rel_map: dict[str, dict]
) -> tuple[dict[str, int], set[str], int]:
    confidence = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
    labels = set()
    mapped_count = 0

    for name in files:
        dst_abs = str(Path(bucket_path, name).resolve()).lower()
        rel = rel_map.get(dst_abs)
        if rel:
            conf = rel.get("stamp", {}).get("confidence", "unknown")
            confidence[conf] = confidence.get(conf, 0) + 1
            src_abs = rel.get("src_abs", "")
            text = _normalize_text(src_abs)
            for token in TOKENS:
                if token in text:
                    labels.add(token)
            mapped_count += 1
        else:
            confidence["unknown"] += 1
            text = _normalize_text(dst_abs)
            for token in TOKENS:
                if token in text:
                    labels.add(token)

    return confidence, labels, mapped_count


def _write_index(
    *,
    legacy_root: str,
    index_path: str,
    rel_map: dict[str, dict],
) -> dict[str, int]:
    tree = _tree_lines(legacy_root, 5)
    buckets = _collect_buckets(legacy_root)

    lines = [
        "# LEGACY_INDEX",
        "",
        f"Root: {legacy_root}",
        "",
        "## Tree (depth=5)",
        "```text",
    ]
    lines.extend(tree)
    lines.extend(["```", "", "## Buckets"])

    bucket_missing = 0
    files_indexed = 0
    for bucket_rel in sorted(buckets.keys()):
        bucket = buckets[bucket_rel]
        files = bucket["files"]
        bucket_path = bucket["path"]
        area = _bucket_area(bucket_rel)
        confidence, labels, mapped_count = _compute_bucket_stats(
            bucket_path, files, rel_map
        )
        files_indexed += len(files)
        label_line = "Label: (none)"
        if labels:
            label_line = "Label: " + ", ".join(sorted(labels))
        if mapped_count == 0 and rel_map:
            bucket_missing += 1

        lines.append(f"### {bucket_rel}")
        lines.append(f"Files: {len(files)}")
        lines.append(f"Areas: {area}")
        lines.append(
            "Confidence: "
            f"high={confidence['high']}, "
            f"medium={confidence['medium']}, "
            f"low={confidence['low']}, "
            f"unknown={confidence['unknown']}"
        )
        lines.append(label_line)
        lines.append("Top 5:")
        for name in files[:5]:
            lines.append(f"- {name}")
        lines.append("")

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return {
        "bucket_count": len(buckets),
        "files_indexed": files_indexed,
        "buckets_missing_map": bucket_missing,
    }


def run_stage(
    *,
    workspace_root: str,
    relocation_map: str,
    wordpipe_legacy_root: str,
    whs_legacy_root: str,
    wordpipe_index_out: str,
    whs_index_out: str,
    log: str,
    strict: bool,
) -> StageResult:
    workspace_abs = resolve_workspace_root(workspace_root)
    relocation_map_path = resolve_path(workspace_abs, relocation_map)
    wordpipe_legacy_abs = resolve_path(workspace_abs, wordpipe_legacy_root)
    whs_legacy_abs = resolve_path(workspace_abs, whs_legacy_root)
    wordpipe_index_abs = resolve_path(workspace_abs, wordpipe_index_out)
    whs_index_abs = resolve_path(workspace_abs, whs_index_out)
    log_path = resolve_path(workspace_abs, log)

    result = StageResult(
        stage="build_legacy_index",
        paths=StagePaths(
            workspace_root=workspace_abs,
            inputs={
                "relocation_map": relocation_map_path,
                "wordpipe_legacy_root": wordpipe_legacy_abs,
                "whs_legacy_root": whs_legacy_abs,
            },
            outputs={
                "wordpipe_index": wordpipe_index_abs,
                "whs_index": whs_index_abs,
                "legacy_index_log": log_path,
            },
        ),
    )

    rel_map = _load_relocation_map(relocation_map_path)
    rel_map_loaded = bool(rel_map)
    if not rel_map_loaded:
        result.add_warning(
            f"relocation map not found or empty: {relocation_map_path}; confidence labels may be incomplete"
        )

    if not os.path.isdir(wordpipe_legacy_abs):
        result.add_warning(f"legacy root missing: {wordpipe_legacy_abs}")
    if not os.path.isdir(whs_legacy_abs):
        result.add_warning(f"legacy root missing: {whs_legacy_abs}")

    wp_stats = _write_index(
        legacy_root=wordpipe_legacy_abs,
        index_path=wordpipe_index_abs,
        rel_map=rel_map,
    )
    whs_stats = _write_index(
        legacy_root=whs_legacy_abs,
        index_path=whs_index_abs,
        rel_map=rel_map,
    )

    log_lines = [
        f"relocation_map_loaded: {str(rel_map_loaded).lower()}",
        f"relocation_map_path: {relocation_map_path}",
        f"project: wordpipe",
        f"index_written: {wordpipe_index_abs}",
        f"bucket_count: {wp_stats['bucket_count']}",
        f"files_indexed: {wp_stats['files_indexed']}",
        f"buckets_missing_map: {wp_stats['buckets_missing_map']}",
        f"project: WordHorrorStories",
        f"index_written: {whs_index_abs}",
        f"bucket_count: {whs_stats['bucket_count']}",
        f"files_indexed: {whs_stats['files_indexed']}",
        f"buckets_missing_map: {whs_stats['buckets_missing_map']}",
    ]
    append_log_block(log_path, "build_legacy_index summary", log_lines)

    result.counters = {
        "wordpipe_bucket_count": wp_stats["bucket_count"],
        "wordpipe_files_indexed": wp_stats["files_indexed"],
        "wordpipe_buckets_missing_map": wp_stats["buckets_missing_map"],
        "whs_bucket_count": whs_stats["bucket_count"],
        "whs_files_indexed": whs_stats["files_indexed"],
        "whs_buckets_missing_map": whs_stats["buckets_missing_map"],
    }
    result.generated_paths = {
        "wordpipe_index": wordpipe_index_abs,
        "whs_index": whs_index_abs,
        "legacy_index_log": log_path,
    }
    result.details["summary_lines"] = log_lines

    return result.finalize(strict=strict)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument(
        "--relocation-map", default="_ARCHIVE/move_maps/relocation_map.jsonl"
    )
    parser.add_argument("--wordpipe-legacy-root", default="wordpipe/legacy")
    parser.add_argument("--whs-legacy-root", default="WordHorrorStories/legacy")
    parser.add_argument("--wordpipe-index-out", default="wordpipe/legacy/LEGACY_INDEX.md")
    parser.add_argument(
        "--whs-index-out", default="WordHorrorStories/legacy/LEGACY_INDEX.md"
    )
    parser.add_argument("--log", default="_ARCHIVE/logs/legacy_index.log")
    parser.add_argument("--summary-json", default="")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    result = run_stage(
        workspace_root=args.workspace_root,
        relocation_map=args.relocation_map,
        wordpipe_legacy_root=args.wordpipe_legacy_root,
        whs_legacy_root=args.whs_legacy_root,
        wordpipe_index_out=args.wordpipe_index_out,
        whs_index_out=args.whs_index_out,
        log=args.log,
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
