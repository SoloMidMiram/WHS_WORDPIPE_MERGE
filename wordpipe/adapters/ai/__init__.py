"""AI adapters (optional extra: `wordpipe[ai]`)."""

from wordpipe.adapters.ai.dummy import DummySummarizer
from wordpipe.adapters.ai.openai_summarizer import OpenAISummarizer

__all__ = ["DummySummarizer", "OpenAISummarizer"]

