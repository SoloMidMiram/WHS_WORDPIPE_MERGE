# =============================================
# file: wordpipe/flatteners/xml_flattener.py
# =============================================
from pathlib import Path
from typing import List, Optional
from wordpipe.core.datatypes import ChangeNote
from MergedpipelineV3 import flatten_revisions_xml_approx as _run


class XmlFlattener:
    def run(
        self, input_docx: Path, output_docx: Path, *, limit_pages: Optional[int] = None
    ) -> List[ChangeNote]:
        return _run(str(input_docx), str(output_docx), limit_pages=limit_pages)
