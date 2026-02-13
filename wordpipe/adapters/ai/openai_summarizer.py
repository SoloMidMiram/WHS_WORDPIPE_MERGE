from __future__ import annotations

from typing import Any


class OpenAISummarizer:
    """OpenAI-backed summarizer (requires `openai` extra).

    This adapter is intentionally thin and requires an explicit client to avoid
    environment-based implicit discovery inside core/orchestration code.
    """

    def __init__(self, client: Any, *, model: str):
        self._client = client
        self._model = model

    def summarize(self, text: str) -> str:
        t = (text or "").strip()
        if not t:
            return ""

        # Lazy import: openai package is optional, but the passed client should be compatible.
        if not hasattr(self._client, "responses"):
            raise RuntimeError("OpenAI client is missing `responses` API surface")

        prompt = "Summarize the following text in 3-6 bullet points:\n\n" + t
        r = self._client.responses.create(model=self._model, input=prompt, temperature=0.2)
        out = getattr(r, "output_text", None) or ""
        return out.strip()

