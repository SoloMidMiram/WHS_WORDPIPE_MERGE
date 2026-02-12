# wordpipe/ai/helpers.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Protocol
import os

# ── Public protocol (stable) ─────────────────────────────────────────────────


class AIProvider(Protocol):
    """Tiny, swappable interface the orchestrator depends on."""

    def suggest_heading(self, text: str) -> Optional[str]: ...
    def rewrite_paragraph(self, text: str) -> Optional[str]: ...


# ── Lightweight budgeting (orchestrator can read/update) ─────────────────────


# ai/helpers.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Protocol


class AIProvider(Protocol):
    def suggest_heading(self, text: str) -> Optional[str]: ...
    def rewrite_paragraph(self, text: str) -> Optional[str]: ...


@dataclass
class AICallMeter:
    max_tokens: int = 50000
    used_tokens: int = 0
    per_section_cap: int = 40
    per_section_counts: Dict[str, int] = field(default_factory=dict)

    def can_spend(self, n: int) -> bool:
        return self.used_tokens + max(1, n) <= self.max_tokens

    def spend(self, n: int) -> None:
        self.used_tokens += max(1, n)


class DummyProvider:
    """Offline, deterministic; good for smoke tests."""

    def __init__(self, meter: Optional[AICallMeter] = None, prefix: str = "AI"):
        self.meter = meter or AICallMeter()
        self.prefix = prefix

    def suggest_heading(self, text: str) -> Optional[str]:
        if not text:
            return None
        line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "Untitled")
        self.meter.spend(max(1, len(text) // 8))
        return f"{self.prefix} — {line[:100].strip(' #')}"

    def rewrite_paragraph(self, text: str) -> Optional[str]:
        if not text or len(text.strip()) < 8:
            return None
        self.meter.spend(max(1, len(text) // 6))
        return f"[clarified] {text.strip()}"


__all__ = ["AIProvider", "AICallMeter", "DummyProvider"]


@dataclass
class AICallMeter:
    max_tokens: int = 50_000  # session ceiling (rough)
    used_tokens: int = 0
    per_section_cap: int = 40  # mirror PipelineConfig.max_rewrite_per_section
    per_section_counts: Dict[str, int] = field(default_factory=dict)

    def can_spend(self, est_tokens: int) -> bool:
        return (self.used_tokens + max(1, est_tokens)) <= self.max_tokens

    def spend(self, est_tokens: int) -> None:
        self.used_tokens += max(1, est_tokens)

    def section_can_rewrite(self, section_id: str) -> bool:
        return self.per_section_counts.get(section_id, 0) < self.per_section_cap

    def note_section_rewrite(self, section_id: str) -> None:
        self.per_section_counts[section_id] = (
            self.per_section_counts.get(section_id, 0) + 1
        )


def _estimate_tokens(s: str) -> int:
    """Very rough token estimate (~4 chars/token)."""
    if not s:
        return 1
    return max(1, len(s) // 4)


def _trim(s: Optional[str], n: int) -> Optional[str]:
    return (s or "")[:n] if s else None


# ── Providers ────────────────────────────────────────────────────────────────


class DummyProvider:
    """
    Zero-dependency provider for offline tests/dev.
    Deterministic; never touches the network.
    """

    def __init__(self, meter: Optional[AICallMeter] = None, prefix: str = "AI"):
        self.meter = meter or AICallMeter()
        self.prefix = prefix

    def suggest_heading(self, text: str) -> Optional[str]:
        if not text:
            return None
        line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "Untitled")
        out = f"{self.prefix} — {line}".strip(" #")
        self.meter.spend(_estimate_tokens(text) // 10)
        return out[:120]

    def rewrite_paragraph(self, text: str) -> Optional[str]:
        if not text or len(text.strip()) < 8:
            return None
        out = f"[clarified] {text.strip()}"
        self.meter.spend(_estimate_tokens(text) // 8)
        return out


class OpenAIProvider:
    """
    Minimal OpenAI-backed provider.
    Uses Responses API if available, else Chat Completions.
    Soft-fails to None on any error so the pipeline keeps moving.
    """

    def __init__(
        self, client, model: Optional[str] = None, meter: Optional[AICallMeter] = None
    ):
        if client is None:
            raise RuntimeError("OpenAI client is required")
        self.client = client
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.meter = meter or AICallMeter()

    def _complete(self, prompt: str, temperature: float = 0.2) -> Optional[str]:
        est_in = _estimate_tokens(prompt)
        if not self.meter.can_spend(est_in):
            return None
        try:
            out: Optional[str] = None

            # Prefer Responses API
            if hasattr(self.client, "responses"):
                r = self.client.responses.create(
                    model=self.model, input=prompt, temperature=temperature
                )
                out = getattr(r, "output_text", None)

            # Fallback: Chat Completions
            if (
                not out
                and hasattr(self.client, "chat")
                and hasattr(self.client.chat, "completions")
            ):
                cr = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                )
                if getattr(cr, "choices", None):
                    out = (cr.choices[0].message.content or "").strip()

            if out:
                self.meter.spend(est_in + _estimate_tokens(out))
                return out.strip()
        except Exception:
            return None
        return None

    def suggest_heading(self, text: str) -> Optional[str]:
        if not text:
            return None
        body = _trim(text, 4000) or ""
        prompt = (
            "Propose a concise H2 title (≤10 words) for the following passage. "
            "Return only the title, no markdown, no leading symbols:\n\n" + body
        )
        out = self._complete(prompt, temperature=0.1)
        if not out:
            return None
        return out.splitlines()[0].strip(" #\t")[:120]

    def rewrite_paragraph(self, text: str) -> Optional[str]:
        if not text or len(text.strip()) < 8:
            return None
        body = _trim(text, 8000) or ""
        prompt = (
            "Rewrite the paragraph for clarity and flow while preserving meaning. "
            "Keep it 2–4 sentences. No markdown, no headings:\n\n" + body
        )
        return self._complete(prompt, temperature=0.2)


__all__ = ["AIProvider", "AICallMeter", "DummyProvider", "OpenAIProvider"]
