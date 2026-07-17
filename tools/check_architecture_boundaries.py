#!/usr/bin/env python3
"""Check narrow, runtime-relevant Python import boundaries.

This is an AST import guard, not a call-graph or security scanner. Dynamic
imports, subprocess targets, plugin entry points, and test-time module loading
are deliberately outside its v1 scope.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


# Central registry for reviewed path roles. No registered entry bypasses the
# forbidden v1 edges below; these entries document intentionally privileged
# composition/wrapper surfaces for current and future boundary rules.
EXCEPTION_REGISTRY: dict[tuple[str, str], str] = {
    ("wordpipe/orchestrator.py", "wordpipe.adapters"): (
        "composition root selects concrete runtime adapters"
    ),
    ("wordpipe/pipeline/orchestrator.py", "wordpipe.orchestrator"): (
        "legacy import facade delegates to the canonical composition root"
    ),
    ("pipeline/ingest.py", "wordpipe.chronicle"): (
        "thin operator wrapper delegates to canonical Chronicle code"
    ),
    ("pipeline/merge.py", "wordpipe.chronicle"): (
        "thin operator wrapper delegates to canonical Chronicle code"
    ),
    ("pipeline/categorize.py", "wordpipe.chronicle"): (
        "thin operator wrapper delegates to canonical Chronicle code"
    ),
    ("pipeline/verify_ingest.py", "wordpipe.chronicle"): (
        "thin operator wrapper delegates to canonical Chronicle code"
    ),
}

SCAN_ROOTS = ("wordpipe", "pipeline")
EXCLUDED_PARTS = {"__pycache__", "legacy", "tests", "output", "outputs", "generated"}


@dataclass(frozen=True)
class ImportEdge:
    path: str
    line: int
    imported: str


@dataclass(frozen=True)
class BoundaryViolation:
    edge: ImportEdge
    rule: str

    def render(self) -> str:
        return (
            f"{self.edge.path}:{self.edge.line}: {self.edge.imported} "
            f"violates {self.rule}"
        )


def exception_reason(
    path: str,
    imported: str,
    registry: dict[tuple[str, str], str] | None = None,
) -> str | None:
    """Return the reviewed reason for a path/import-prefix pair, if any."""
    registry = EXCEPTION_REGISTRY if registry is None else registry
    for (registered_path, prefix), reason in registry.items():
        if path == registered_path and (
            imported == prefix or imported.startswith(prefix + ".")
        ):
            return reason
    return None


def active_v1_bypass_count(
    registry: dict[tuple[str, str], str] | None = None,
) -> int:
    """Count registered roles that would suppress a currently forbidden edge."""
    registry = EXCEPTION_REGISTRY if registry is None else registry
    return sum(
        1
        for path, imported in registry
        if classify_violation(ImportEdge(path=path, line=0, imported=imported))
        is not None
    )


def _is_type_checking_test(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Name) and node.id == "TYPE_CHECKING"
    ) or (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "typing"
        and node.attr == "TYPE_CHECKING"
    )


def _module_name(path: PurePosixPath) -> str:
    parts = list(path.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _resolve_import_from(
    path: PurePosixPath,
    module: str | None,
    level: int,
) -> str:
    if level == 0:
        return module or ""
    current = _module_name(path).split(".")
    if path.name != "__init__.py" and current:
        current.pop()
    keep = max(0, len(current) - (level - 1))
    parts = current[:keep]
    if module:
        parts.extend(module.split("."))
    return ".".join(parts)


class _ImportVisitor(ast.NodeVisitor):
    def __init__(self, path: PurePosixPath):
        self.path = path
        self.edges: list[ImportEdge] = []
        self._type_checking_depth = 0

    def visit_If(self, node: ast.If) -> None:  # noqa: N802 - ast API
        if _is_type_checking_test(node.test):
            self._type_checking_depth += 1
            for child in node.body:
                self.visit(child)
            self._type_checking_depth -= 1
            for child in node.orelse:
                self.visit(child)
            return
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802 - ast API
        if self._type_checking_depth:
            return
        for alias in node.names:
            self.edges.append(ImportEdge(self.path.as_posix(), node.lineno, alias.name))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802 - ast API
        if self._type_checking_depth:
            return
        imported = _resolve_import_from(self.path, node.module, node.level)
        if imported:
            self.edges.append(ImportEdge(self.path.as_posix(), node.lineno, imported))


def collect_imports(root: Path) -> tuple[list[ImportEdge], list[str]]:
    """Collect static production imports and parse failures."""
    root = root.resolve()
    edges: list[ImportEdge] = []
    errors: list[str] = []
    for scan_root in SCAN_ROOTS:
        base = root / scan_root
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            rel = PurePosixPath(path.relative_to(root).as_posix())
            if any(part in EXCLUDED_PARTS for part in rel.parts) or path.name.startswith(
                "test_"
            ):
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(rel))
            except (OSError, SyntaxError, UnicodeError) as exc:
                errors.append(f"{rel.as_posix()}: unable to inspect imports: {exc}")
                continue
            visitor = _ImportVisitor(rel)
            visitor.visit(tree)
            edges.extend(visitor.edges)
    return edges, errors


def _matches(imported: str, prefixes: Iterable[str]) -> bool:
    lowered = imported.casefold()
    return any(
        lowered == prefix.casefold()
        or lowered.startswith(prefix.casefold() + ".")
        for prefix in prefixes
    )


def classify_violation(edge: ImportEdge) -> str | None:
    """Return the first violated v1 boundary rule for an import edge."""
    path = PurePosixPath(edge.path)
    if not path.parts or path.parts[0] != "wordpipe":
        return None

    if _matches(edge.imported, ("tools", "pipeline", "WordHorrorStories", "_ARCHIVE")):
        return "wordpipe must not import tools/pipeline/content/archive surfaces"

    if len(path.parts) > 1 and path.parts[1] in {"core", "interfaces"}:
        if _matches(
            edge.imported,
            (
                "wordpipe.adapters",
                "wordpipe.orchestration",
                "wordpipe.orchestrator",
                "wordpipe.pipeline",
                "wordpipe.chronicle",
                "tools",
            ),
        ):
            return "wordpipe.core/interfaces must remain dependency-inward"

    if len(path.parts) > 1 and path.parts[1] == "chronicle":
        if _matches(
            edge.imported,
            (
                "tools.prepare_generic_markdown_chronicle",
                "tools.prepare_insurancechatbot_chronicle",
                "tools.run_topic_report",
                "wordpipe.adapters.docx",
            ),
        ):
            return "wordpipe.chronicle must remain topic- and DOCX-runtime-neutral"
    return None


def find_violations(root: Path) -> tuple[list[BoundaryViolation], list[str], int]:
    edges, errors = collect_imports(root)
    violations: list[BoundaryViolation] = []
    for edge in edges:
        rule = classify_violation(edge)
        if rule is None:
            continue
        # Reviewed exceptions are centralized. The current registry deliberately
        # contains no bypass for a forbidden v1 edge.
        if exception_reason(edge.path, edge.imported) is not None:
            continue
        violations.append(BoundaryViolation(edge=edge, rule=rule))
    return violations, errors, len(edges)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    violations, errors, edge_count = find_violations(args.root)
    if violations or errors:
        print("architecture_boundaries: FAIL")
        for error in errors:
            print(f"- {error}")
        for violation in violations:
            print(f"- {violation.render()}")
        return 1
    print("architecture_boundaries: OK")
    print(f"static_import_edges_scanned: {edge_count}")
    print(f"reviewed_path_roles: {len(EXCEPTION_REGISTRY)}")
    print(f"active_v1_bypasses: {active_v1_bypass_count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
