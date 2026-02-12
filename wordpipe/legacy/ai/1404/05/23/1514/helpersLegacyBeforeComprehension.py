# -*- coding: utf-8 -*-
"""
AI helpers for the Word pipeline.

This module is intentionally self-contained and safe to develop separately from
the rest of the codebase. The orchestrator can *optionally* import this and
inject a provider instance. If the orchestrator finds a provider with
`rewrite_rich(...)`, it uses it for structured restyling; otherwise it falls
back to `rewrite_paragraph(...)` (plain text) and/or `suggest_heading(...)`.

Key ideas
---------
• Stable Protocol (AIProvider) — tiny, swappable interface.
• Token budgeting (AICallMeter) — coarse budgeting that works even if you don't
  wire a tokenizer yet.
• Structured output (rewrite_rich) — LLM returns JSON: {text, style, heading}.
  The pipeline applies real Word styles; no markdown parsing required.
• Defensive parsing — tolerate code-fence wrappers, minor JSON glitches.
• Soft-fail — all provider calls return None on error so the pipeline keeps going.

Integration hints for the orchestrator
--------------------------------------
if hasattr(ai_provider, "rewrite_rich"):
    data = ai_provider.rewrite_rich(p_text)
    if data:
        if data.heading: insert_heading2(xml_safe(data.heading))
        p.text = xml_safe(data.text)
        apply_style_from_label(p, data.style)  # 'Body'|'Code'|'Bullet'|'Quote'
else:
    # fallback to classic behavior
    new = ai_provider.rewrite_paragraph(p_text)
    if new: p.text = xml_safe(new)

Note: Always run LLM output through xml_safe() at write sinks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Protocol, Literal
import json
import os
import re


# ── Public protocol (stable) ──────────────────────────────────────────────────
class AIProvider(Protocol):
    """Tiny, swappable interface the pipeline depends on.

    Implementations may also offer `rewrite_rich` (preferred). The orchestrator
    should check via `hasattr(provider, "rewrite_rich")` to keep this optional.
    """

    def suggest_heading(self, text: str) -> Optional[str]: ...
    def rewrite_paragraph(self, text: str) -> Optional[str]: ...

    # Optional, but recommended. Returns structured text + styling intent.
    def rewrite_rich(self, text: str) -> Optional["RichRewriteOut"]: ...


# ── Structured output types ───────────────────────────────────────────────────
StyleLabel = Literal["Body", "Code", "Bullet", "Quote"]


@dataclass(frozen=True)
class RichRewriteOut:
    """What the model should return for 'restyle + rewrite'.

    text:    final plain text, no markdown fences or headings
    style:   label for downstream styling in Word
    heading: optional concise H2 to insert *above* the paragraph
    """

    text: str
    style: StyleLabel = "Body"
    heading: Optional[str] = None


# ── Lightweight budgeting ─────────────────────────────────────────────────────
@dataclass
class AICallMeter:
    """Very rough budgeting & per-section caps (no tokenizer dependency)."""

    max_tokens: int = 50_000  # per run/session ceiling
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
    """Coarse 4 chars/token estimator (replace with tiktoken later if desired)."""
    if not s:
        return 1
    return max(1, len(s) // 4)


def _trim(s: Optional[str], n: int) -> str:
    return (s or "")[:n]


def _strip_code_fence(s: str) -> str:
    """Strip ```json ... ``` or ``` ... ``` wrappers if present."""
    s = s.strip()
    fence = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL | re.IGNORECASE)
    m = fence.match(s)
    return m.group(1).strip() if m else s


def _coerce_style(label: str) -> StyleLabel:
    """Normalize common synonyms to our canonical style labels."""
    val = (label or "").strip().lower()
    if val in {"code", "mono", "monospace", "pre", "preformatted"}:
        return "Code"
    if val in {"bullet", "bulleted", "list", "listitem"}:
        return "Bullet"
    if val in {"quote", "blockquote", "citation"}:
        return "Quote"
    # Default bucket for prose
    return "Body"


# ── Providers ─────────────────────────────────────────────────────────────────
class DummyProvider:
    """
    Zero-dependency provider for offline tests/dev.
    Deterministic, safe, and fast. Never touches the network.
    """

    def __init__(self, meter: Optional[AICallMeter] = None, prefix: str = "AI"):
        self.meter = meter or AICallMeter()
        self.prefix = prefix

    # --- classic outputs ---
    def suggest_heading(self, text: str) -> Optional[str]:
        if not text:
            return None
        line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "Untitled")
        self.meter.spend(_estimate_tokens(text) // 10)
        return f"{self.prefix} — {line}"[:120].strip(" #")

    def rewrite_paragraph(self, text: str) -> Optional[str]:
        if not text or len(text.strip()) < 8:
            return None
        self.meter.spend(_estimate_tokens(text) // 8)
        return f"[clarified] {text.strip()}"

    # --- structured output (recommended path) ---
    def rewrite_rich(self, text: str) -> Optional[RichRewriteOut]:
        if not text or len(text.strip()) < 8:
            return None
        self.meter.spend(_estimate_tokens(text) // 8)
        # Trivial heuristic demo: code-ish lines → Code, bullets → Bullet
        t = text.strip()
        looks_code = (
            any(sym in t for sym in ("def ", "class ", "{", "}", ";")) or "```" in t
        )
        looks_bullet = t.lstrip().startswith(("-", "*", "•"))
        style: StyleLabel = (
            "Code" if looks_code else ("Bullet" if looks_bullet else "Body")
        )
        # A toy heading suggestion for demo purposes
        heading = None
        if len(t) > 60 and not looks_code:
            heading = f"{self.prefix} — Summary"
        return RichRewriteOut(text=f"[clarified] {t}", style=style, heading=heading)


class OpenAIProvider:
    """
    Minimal OpenAI-backed provider.

    • Works with either the Responses API (preferred) or Chat Completions.
    • Soft-fails to None on error (pipeline keeps moving).
    • Keeps prompts tight to respect budgets and reduce latency.
    """

    def __init__(
        self, client, model: Optional[str] = None, meter: Optional[AICallMeter] = None
    ):
        if client is None:
            raise RuntimeError("OpenAI client is required")
        self.client = client
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.meter = meter or AICallMeter()

    # ---- private helpers -----------------------------------------------------
    def _complete(self, prompt: str, *, temperature: float = 0.2) -> Optional[str]:
        est_in = _estimate_tokens(prompt)
        if not self.meter.can_spend(est_in):
            return None
        try:
            out: Optional[str] = None
            # Prefer Responses API if available
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

    def _complete_json(
        self, prompt: str, *, temperature: float = 0.2
    ) -> Optional[dict]:
        """Ask the model for JSON and parse it defensively."""
        raw = self._complete(prompt, temperature=temperature)
        if not raw:
            return None
        try:
            cleaned = _strip_code_fence(raw)
            # Try direct parse first
            return json.loads(cleaned)
        except Exception:
            # Last resort: extract the first {...} block
            m = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if not m:
                return None
            try:
                return json.loads(m.group(0))
            except Exception:
                return None

    # ---- classic outputs -----------------------------------------------------
    def suggest_heading(self, text: str) -> Optional[str]:
        if not text:
            return None
        body = _trim(text, 4000)
        prompt = (
            "Propose a concise H2 title (≤10 words) for the passage below. "
            "Return only the title, no markdown, no leading symbols:\n\n" + body
        )
        out = self._complete(prompt, temperature=0.1)
        if not out:
            return None
        return out.splitlines()[0].strip(" #\t")[:120] or None

    def rewrite_paragraph(self, text: str) -> Optional[str]:
        if not text or len(text.strip()) < 8:
            return None
        body = _trim(text, 8000)
        prompt = (
            "Rewrite the paragraph for clarity and flow while preserving meaning. "
            "Produce plain text only (no markdown, no headings).\n\n" + body
        )
        return self._complete(prompt, temperature=0.2)

    # ---- structured output (recommended path) --------------------------------
    def rewrite_rich(self, text: str) -> Optional[RichRewriteOut]:
        """Ask the model to rewrite + suggest style + optional H2, as JSON.

        Expected JSON shape:
            {
              "text":   "<final plain text>",
              "style":  "Body" | "Code" | "Bullet" | "Quote",
              "heading":"<optional concise H2 (≤10 words)>"  # omit or "" if none
            }
        """
        if not text or len(text.strip()) < 8:
            return None

        body = _trim(text, 6000)
        prompt = (
            "Rewrite the following paragraph for clarity and coherence while preserving meaning. "
            "Then decide the appropriate style label from this set: "
            '["Body","Code","Bullet","Quote"]. '
            "If a concise Heading 2 would help the reader, include it (≤10 words). "
            "Return *only JSON* with keys exactly: text, style, heading. "
            "Do not include markdown fences or extra commentary.\n\n"
            f"{body}\n"
        )

        data = self._complete_json(prompt, temperature=0.2)
        if not data or not isinstance(data, dict):
            return None

        # Defensive normalization
        text_out = (data.get("text") or "").strip()
        if not text_out:
            return None

        style_out = _coerce_style(str(data.get("style") or "Body"))
        heading_out_raw = (data.get("heading") or "").strip()
        heading_out = heading_out_raw[:120] if heading_out_raw else None

        return RichRewriteOut(text=text_out, style=style_out, heading=heading_out)


# ── Convenience re-exports ────────────────────────────────────────────────────
__all__ = [
    "AIProvider",
    "AICallMeter",
    "RichRewriteOut",
    "DummyProvider",
    "OpenAIProvider",
]
