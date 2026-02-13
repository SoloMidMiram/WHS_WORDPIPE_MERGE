# =============================================
# file: wordpipe/flatteners/com_flattener.py
# =============================================
from pathlib import Path
from typing import Optional, List
from wordpipe.core.datatypes import ChangeNote


class ComFlattener:
    def run(
        self, input_docx: Path, output_docx: Path, *, limit_pages: Optional[int] = None
    ) -> List[ChangeNote]:
        # Lazy import: this depends on optional legacy win32 integration modules.
        try:
            from MergedpipelineV3 import flatten_revisions_inline_win32 as _run  # type: ignore
        except Exception as exc:  # pragma: no cover
            missing = getattr(exc, "name", None) or "MergedpipelineV3"
            raise RuntimeError(
                "COM flattener unavailable: missing module "
                f"'{missing}' while importing legacy 'MergedpipelineV3'. "
                "This path requires legacy Windows-only functions and pywin32. "
                "Install pywin32 and ensure the missing module is available."
            ) from exc

        return _run(str(input_docx), str(output_docx), limit_pages=limit_pages)
