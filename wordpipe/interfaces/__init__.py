"""Abstract service contracts (dependency-light).

Core and orchestration code must depend only on interfaces + core datatypes.
Concrete implementations live under `wordpipe.adapters`.
"""

from wordpipe.interfaces.ai import AISummarizer
from wordpipe.interfaces.config import ConfigProvider
from wordpipe.interfaces.documents import (
    DocumentReader,
    DocumentSegmenter,
    DocumentStyler,
    DocumentWriter,
)
from wordpipe.interfaces.logging import Logger
from wordpipe.interfaces.transforms import Flattener, TocUpdater

__all__ = [
    "AISummarizer",
    "ConfigProvider",
    "DocumentReader",
    "DocumentSegmenter",
    "DocumentStyler",
    "DocumentWriter",
    "Flattener",
    "Logger",
    "TocUpdater",
]

