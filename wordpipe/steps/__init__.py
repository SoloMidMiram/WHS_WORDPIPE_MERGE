"""Step modules for the WordPipe pipeline.

Each step is a standalone function that:
- Accepts a PipelineConfig and EventSink
- Returns a typed result dataclass
- Is unit-testable in isolation with a fake EventSink
- Does NOT swallow exceptions silently — failures propagate with context
"""
# wordpipe/steps/__init__.py
# Created: 2026-02-14 (Jalali: 1404/11/25)
# Modified: 2026-02-14 (Jalali: 1404/11/25)
# Purpose: Step modules for the WordPipe pipeline.

from wordpipe.steps.flatten import FlattenResult, flatten_step
from wordpipe.steps.style import StyleResult, style_step
from wordpipe.steps.segment import SegmentResult, segment_step
from wordpipe.steps.finalize import FinalizeResult, finalize_step
from wordpipe.steps.toc import TocResult, toc_step

__all__ = [
    "FlattenResult",
    "flatten_step",
    "StyleResult",
    "style_step",
    "SegmentResult",
    "segment_step",
    "FinalizeResult",
    "finalize_step",
    "TocResult",
    "toc_step",
]
