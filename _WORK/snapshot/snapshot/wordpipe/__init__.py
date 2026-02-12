"""package init"""

# =============================
# file: wordpipe/__init__.py
# =============================

from wordpipe.core.datatypes import ChangeNote, PipelineConfig, RunReport, Segment
from wordpipe.orchestrator import process_docx_v3, process_docx_v3_simple

__all__ = [
    "ChangeNote",
    "Segment",
    "PipelineConfig",
    "RunReport",
    "process_docx_v3",
    "process_docx_v3_simple",
]
