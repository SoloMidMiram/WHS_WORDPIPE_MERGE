"""Shared helpers used by workspace tooling scripts."""

import hashlib
import os
import re
import shutil
from datetime import datetime


_SECRET_LITERAL_PATTERNS = [
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "<REDACTED_OPENAI_KEY>"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"), "<REDACTED_GITHUB_TOKEN>"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "<REDACTED_GITHUB_TOKEN>"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "<REDACTED_AWS_KEY_ID>"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"), "<REDACTED_SLACK_TOKEN>"),
]
_SECRET_KEY_VALUE_PATTERNS = [
    re.compile(r"(?i)\b(authorization\s*:\s*bearer\s+)(\S+)"),
    re.compile(r"(?i)\b((?:api[_-]?key|token|secret|password)\s*[:=]\s*)(\S+)"),
]


def redact_secrets(text: str) -> str:
    redacted = text
    for pattern, replacement in _SECRET_LITERAL_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    for pattern in _SECRET_KEY_VALUE_PATTERNS:
        redacted = pattern.sub(lambda match: f"{match.group(1)}<REDACTED>", redacted)
    return redacted


def auto_normalize_root(root: str) -> tuple[str, bool]:
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


def append_log_block(log_path: str, header: str, lines: list[str]) -> None:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {redact_secrets(header)}\n")
        for line in lines:
            f.write(redact_secrets(line) + "\n")


def safe_copy_with_conflict(
    src: str, dst: str
) -> tuple[str, str | None, str | None, str | None]:
    """Copy src -> dst, preserving conflicts in _conflicts.

    Returns (status, conflict_path, src_hash, dst_hash).
    status is one of copied | skipped_same | conflict.
    """
    if os.path.exists(dst):
        src_hash = sha256_file(src)
        dst_hash = sha256_file(dst)
        if src_hash == dst_hash:
            return "skipped_same", None, src_hash, dst_hash
        base, ext = os.path.splitext(os.path.basename(dst))
        conflict_name = f"{base}__{src_hash[:8]}{ext}"
        conflict_path = os.path.join(os.path.dirname(dst), "_conflicts", conflict_name)
        os.makedirs(os.path.dirname(conflict_path), exist_ok=True)
        shutil.copy2(src, conflict_path)
        return "conflict", conflict_path, src_hash, dst_hash

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return "copied", None, None, None
