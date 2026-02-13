"""Core (dependency-light) building blocks.

The core layer must avoid optional third-party dependencies.
"""

from wordpipe.core.datatypes import ChangeNote, PipelineConfig, RunReport, Segment
from wordpipe.core.ooxml import find_xml_boundaries, xml_safe

__all__ = [
    "ChangeNote",
    "PipelineConfig",
    "RunReport",
    "Segment",
    "find_xml_boundaries",
    "xml_safe",
]
