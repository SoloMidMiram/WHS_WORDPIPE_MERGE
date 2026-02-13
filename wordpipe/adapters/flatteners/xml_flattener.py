# =============================================
# file: wordpipe/flatteners/xml_flattener.py
# =============================================
from pathlib import Path
from typing import List, Optional
from wordpipe.core.datatypes import ChangeNote


class XmlFlattener:
    def run(
        self, input_docx: Path, output_docx: Path, *, limit_pages: Optional[int] = None
    ) -> List[ChangeNote]:
        # Lazy import: this depends on an optional legacy integration module.
        try:
            from MergedpipelineV3 import flatten_revisions_xml_approx as _run  # type: ignore
        except Exception as exc:  # pragma: no cover
            missing = getattr(exc, "name", None) or "MergedpipelineV3"
            raise RuntimeError(
                "XML flattener unavailable: missing module "
                f"'{missing}' while importing legacy 'MergedpipelineV3'."
            ) from exc

        return _run(str(input_docx), str(output_docx), limit_pages=limit_pages)
