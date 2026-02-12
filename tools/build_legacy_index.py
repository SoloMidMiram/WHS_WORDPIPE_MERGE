"""Build legacy index docs for wordpipe and WordHorrorStories."""

import json
import os
from datetime import datetime
from pathlib import Path


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
                norm = str(Path(dst_abs).resolve()).lower()
                mapping[norm] = row
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
    rel = os.path.relpath(bucket_path, root).replace("\\", "/")
    return rel


def _collect_buckets(legacy_root: str) -> dict[str, dict]:
    buckets = {}
    for base, dirs, files in os.walk(legacy_root):
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
):
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
    legacy_root: str,
    index_path: str,
    rel_map: dict[str, dict],
    log_lines: list[str],
):
    tree = _tree_lines(legacy_root, 5)
    buckets = _collect_buckets(legacy_root)

    lines = []
    lines.append("# LEGACY_INDEX")
    lines.append("")
    lines.append(f"Root: {legacy_root}")
    lines.append("")
    lines.append("## Tree (depth=5)")
    lines.append("```text")
    lines.extend(tree)
    lines.append("```")
    lines.append("")
    lines.append("## Buckets")

    bucket_missing = 0
    for bucket_rel in sorted(buckets.keys()):
        bucket = buckets[bucket_rel]
        files = bucket["files"]
        bucket_path = bucket["path"]
        area = _bucket_area(bucket_rel)
        confidence, labels, mapped_count = _compute_bucket_stats(
            bucket_path, files, rel_map
        )
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

    project_name = os.path.basename(os.path.dirname(legacy_root))
    log_lines.append(f"project: {project_name}")
    log_lines.append(f"index_written: {index_path}")
    log_lines.append(f"bucket_count: {len(buckets)}")
    log_lines.append(f"files_indexed: {sum(len(b['files']) for b in buckets.values())}")
    log_lines.append(f"buckets_missing_map: {bucket_missing}")


def main() -> None:
    workspace = os.path.abspath(".")
    legacy_roots = [
        os.path.join(workspace, "wordpipe", "legacy"),
        os.path.join(workspace, "WordHorrorStories", "legacy"),
    ]
    rel_map_path = os.path.join(workspace, "_ARCHIVE", "move_maps", "relocation_map.jsonl")
    rel_map = _load_relocation_map(rel_map_path)
    rel_map_loaded = bool(rel_map)

    log_lines = [
        f"relocation_map_loaded: {str(rel_map_loaded).lower()}",
        f"relocation_map_path: {rel_map_path}",
    ]

    outputs = [
        os.path.join(workspace, "wordpipe", "legacy", "LEGACY_INDEX.md"),
        os.path.join(workspace, "WordHorrorStories", "legacy", "LEGACY_INDEX.md"),
    ]

    for legacy_root, out_path in zip(legacy_roots, outputs):
        _write_index(legacy_root, out_path, rel_map, log_lines)

    log_path = os.path.join(workspace, "_ARCHIVE", "logs", "legacy_index.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] build_legacy_index summary\n")
        for line in log_lines:
            f.write(line + "\n")

    print("\n".join(log_lines))


if __name__ == "__main__":
    main()
