# ==========================================
# file: wordpipe/flatteners/base.py
# ==========================================
from __future__ import annotations

from pathlib import Path
import sys
from typing import List, Optional, Protocol
import warnings
from wordpipe.core.datatypes import ChangeNote


class Flattener(Protocol):
    def run(
        self, input_docx: Path, output_docx: Path, *, limit_pages: Optional[int] = None
    ) -> List[ChangeNote]: ...


def _can_import_mergedpipeline() -> bool:
    """Return True if ``MergedpipelineV3`` can be imported.

    Used once at configuration time to decide whether legacy flattener or TOC
    implementations are available, so callers fail early rather than deep
    inside ``run()`` or ``update()``.
    """
    # Import safety: never fail at module level. This function is called
    # explicitly from ``make_flattener()`` and ``build_default_deps()``.
    import importlib

    try:
        importlib.import_module("MergedpipelineV3")
        return True
    except Exception:
        return False


class _UnavailableFlattener:
    """Stub returned when no flattener implementation is available.

    Raises ``RuntimeError`` on any invocation so the pipeline step catches
    it and produces a clear ``FlattenResult(error=...)`` before processing
    begins.
    """

    def __init__(self, reason: str = "no flattener available"):
        self._reason = reason

    def run(
        self, input_docx: Path, output_docx: Path, *, limit_pages: Optional[int] = None
    ) -> List[ChangeNote]:
        raise RuntimeError(self._reason)


def make_flattener(prefer_win32: bool) -> Flattener:
    if prefer_win32:
        if not sys.platform.startswith("win"):
            warnings.warn(
                "prefer_win32 requested on non-Windows platform; using XmlFlattener."
            )
            from .xml_flattener import XmlFlattener

            return XmlFlattener()
        # Both ComFlattener and XmlFlattener depend on MergedpipelineV3.
        # If it is absent, fail clearly once rather than falling back to
        # another flattener that will fail at run() time.
        if not _can_import_mergedpipeline():
            msg = (
                "Legacy flattener unavailable: MergedpipelineV3 module is missing. "
                "Neither the COM nor XML flattener can work without it. "
                "Install the legacy integration module or set --no-prefer-win32 / "
                "do_flatten=False to skip flattening."
            )
            warnings.warn(msg)
            return _UnavailableFlattener(reason=msg)
        try:
            from .com_flattener import ComFlattener

            return ComFlattener()
        except RuntimeError as exc:
            warnings.warn(f"COM flattener unavailable; using XmlFlattener. {exc}")
            from .xml_flattener import XmlFlattener

            return XmlFlattener()
    if not _can_import_mergedpipeline():
        msg = (
            "XML flattener unavailable: MergedpipelineV3 module is missing. "
            "Install the legacy integration module or set do_flatten=False."
        )
        warnings.warn(msg)
        return _UnavailableFlattener(reason=msg)
    from .xml_flattener import XmlFlattener

    return XmlFlattener()
