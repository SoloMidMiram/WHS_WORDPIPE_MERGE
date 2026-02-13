"""Shared stage contracts and helpers for tools pipeline scripts."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class StageError:
    code: str
    message: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class StagePaths:
    workspace_root: str
    inputs: dict[str, str] = field(default_factory=dict)
    outputs: dict[str, str] = field(default_factory=dict)


@dataclass
class StageResult:
    stage: str
    paths: StagePaths
    status: str = "success"
    counters: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[StageError] = field(default_factory=list)
    generated_paths: dict[str, str] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_error(
        self, code: str, message: str, context: dict[str, Any] | None = None
    ) -> None:
        self.errors.append(StageError(code=code, message=message, context=context or {}))

    def finalize(self, strict: bool = False) -> "StageResult":
        if strict and self.warnings and not self.errors:
            self.add_error(
                "STRICT_WARNINGS",
                "Strict mode treats warnings as errors.",
                {"warnings_count": len(self.warnings)},
            )
        if self.errors:
            self.status = "error"
        elif self.warnings:
            self.status = "warning"
        else:
            self.status = "success"
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def resolve_workspace_root(value: str) -> str:
    return os.path.abspath(value)


def resolve_path(workspace_root: str, value: str) -> str:
    if os.path.isabs(value):
        return os.path.abspath(value)
    return os.path.abspath(os.path.join(workspace_root, value))


def emit_required_path_error(
    result: StageResult,
    *,
    label: str,
    abs_path: str,
    kind: str = "file",
) -> None:
    message = f"required {label} not found: {abs_path}"
    print(f"ERROR: {message}", file=sys.stderr)
    result.add_error(
        "MISSING_REQUIRED_INPUT",
        message,
        {"label": label, "path": abs_path, "kind": kind},
    )


def write_summary_json(path: str, result: StageResult) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
