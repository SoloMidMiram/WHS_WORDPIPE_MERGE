# =============================================
# file: wordpipe/flatteners/com_flattener.py
# =============================================
from pathlib import Path
from typing import Optional, List
from wordpipe.core.datatypes import ChangeNote

# Adapter to your current implementation; migrate internals later.
try:
    from MergedpipelineV3 import flatten_revisions_inline_win32 as _run
except ImportError as exc:
    missing = getattr(exc, "name", None) or "MergedpipelineV3"
    raise RuntimeError(
        "COM flattener unavailable: missing module "
        f"'{missing}' while importing legacy 'MergedpipelineV3'. "
        "This path requires legacy Windows-only functions and pywin32. "
        "Install pywin32 and ensure the missing module is available."
    ) from exc


class ComFlattener:
    def run(
        self, input_docx: Path, output_docx: Path, *, limit_pages: Optional[int] = None
    ) -> List[ChangeNote]:
        return _run(str(input_docx), str(output_docx), limit_pages=limit_pages)
