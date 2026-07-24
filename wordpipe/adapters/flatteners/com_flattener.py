# =============================================
# file: wordpipe/flatteners/com_flattener.py
# =============================================
from pathlib import Path
from typing import Optional, List
from wordpipe.core.datatypes import ChangeNote


class ComFlattener:
    """Legacy COM-based flattener that requires MergedpipelineV3.

    Importing the class is safe on any platform. Construction fails eagerly
    if the COM dependency is unavailable, so callers can fall back
    immediately rather than discovering the failure inside ``run()``.
    """

    def __init__(self) -> None:
        try:
            from MergedpipelineV3 import flatten_revisions_inline_win32 as _run  # type: ignore
        except Exception as exc:
            missing = getattr(exc, "name", None) or "MergedpipelineV3"
            raise RuntimeError(
                "COM flattener unavailable: missing module "
                f"'{missing}' while importing legacy 'MergedpipelineV3'. "
                "This path requires legacy Windows-only functions and pywin32. "
                "Install pywin32 and ensure the missing module is available."
            ) from exc
        self._run = _run

    def run(
        self, input_docx: Path, output_docx: Path, *, limit_pages: Optional[int] = None
    ) -> List[ChangeNote]:
        return self._run(str(input_docx), str(output_docx), limit_pages=limit_pages)
