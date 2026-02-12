# ==========================================
# file: wordpipe/flatteners/base.py
# ==========================================
from pathlib import Path
import sys
from typing import List, Optional, Protocol
import warnings
from wordpipe.core.datatypes import ChangeNote


class Flattener(Protocol):
    def run(
        self, input_docx: Path, output_docx: Path, *, limit_pages: Optional[int] = None
    ) -> List[ChangeNote]: ...


def make_flattener(prefer_win32: bool) -> Flattener:
    if prefer_win32:
        if not sys.platform.startswith("win"):
            warnings.warn(
                "prefer_win32 requested on non-Windows platform; using XmlFlattener."
            )
            from .xml_flattener import XmlFlattener

            return XmlFlattener()
        try:
            from .com_flattener import ComFlattener

            return ComFlattener()
        except RuntimeError as exc:
            warnings.warn(f"COM flattener unavailable; using XmlFlattener. {exc}")
            from .xml_flattener import XmlFlattener

            return XmlFlattener()
    from .xml_flattener import XmlFlattener

    return XmlFlattener()
