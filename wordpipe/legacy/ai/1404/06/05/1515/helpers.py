# ai/helpers.py — AI helpers & protocol (with comprehension)
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Protocol, Literal, List
import json, os, re

StyleLabel = Literal["Body", "Code", "Bullet", "Quote"]


@dataclass(frozen=True)
class AnalysisOut:
    """Structured comprehension for a paragraph/section.
    text:      rewritten/plain text (no markdown fences)
    style:     downstream Word style intent
    heading:   concise H2/H3 (≤10 words)
    keypoints: bulletable highlights (3–7)
    keywords:  tags (3–10)
    """

    text: str
    style: StyleLabel = "Body"
    heading: Optional[str] = None
    keypoints: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


class AIProvider(Protocol):
    def suggest_heading(self, text: str) -> Optional[str]: ...
    def rewrite_paragraph(self, text: str) -> Optional[str]: ...
    def analyze(self, text: str) -> Optional[AnalysisOut]: ...


# ---- rough budgeting (no tokenizer dependency) ------------------------------
@dataclass
class AICallMeter:
    max_tokens: int = 50_000
    used_tokens: int = 0
    per_section_cap: int = 40
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


def _tok(s: str) -> int:
    return max(1, len(s or "") // 4)


def _coerce_style(label: str) -> StyleLabel:
    v = (label or "").strip().lower()
    if v in {"code", "mono", "monospace", "pre", "preformatted"}:
        return "Code"
    if v in {"bullet", "bulleted", "list", "listitem"}:
        return "Bullet"
    if v in {"quote", "blockquote", "citation"}:
        return "Quote"
    return "Body"


def _strip_fence(s: str) -> str:
    s = (s or "").strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", s, flags=re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else s


# ---- Dummy provider (offline) -----------------------------------------------
class DummyProvider:
    def __init__(self, meter: Optional[AICallMeter] = None, prefix: str = "AI"):
        self.meter = meter or AICallMeter()
        self.prefix = prefix

    def suggest_heading(self, text: str) -> Optional[str]:
        if not text:
            return None
        self.meter.spend(_tok(text) // 10)
        first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "Untitled")
        return f"{self.prefix} — {first[:100].strip(' #')}".strip()

    def rewrite_paragraph(self, text: str) -> Optional[str]:
        if not text or len(text.strip()) < 8:
            return None
        self.meter.spend(_tok(text) // 8)
        return f"[clarified] {text.strip()}"

    def analyze(self, text: str) -> Optional[AnalysisOut]:
        if not text or len(text.strip()) < 8:
            return None
        self.meter.spend(_tok(text) // 6)
        t = text.strip()
        looks_code = (
            any(sym in t for sym in ("def ", "class ", "{", "}", ";")) or "```" in t
        )
        looks_bul = t.lstrip().startswith(("-", "*", "•"))
        style = "Code" if looks_code else ("Bullet" if looks_bul else "Body")
        heading = f"{self.prefix} — Summary" if len(t) > 60 and not looks_code else None
        pts = [s.strip() for s in re.split(r"[.!?]\s+", t) if s.strip()][:3]
        tags = [w for w in re.findall(r"[A-Za-z]{4,}", t)[:5]]
        return AnalysisOut(
            text=f"[clarified] {t}",
            style=style,
            heading=heading,
            keypoints=pts,
            keywords=tags,
        )


# ---- OpenAI-backed provider -------------------------------------------------
class OpenAIProvider:
    def __init__(
        self, client, model: Optional[str] = None, meter: Optional[AICallMeter] = None
    ):
        if client is None:
            raise RuntimeError("OpenAI client is required")
        self.client = client
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.meter = meter or AICallMeter()

    def _complete(self, prompt: str, *, temperature: float = 0.2) -> Optional[str]:
        need = _tok(prompt)
        if not self.meter.can_spend(need):
            return None
        try:
            out = None
            if hasattr(self.client, "responses"):
                r = self.client.responses.create(
                    model=self.model, input=prompt, temperature=temperature
                )
                out = getattr(r, "output_text", None)
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
                self.meter.spend(need + _tok(out))
                return out.strip()
        except Exception:
            return None
        return None

    def _complete_json(
        self, prompt: str, *, temperature: float = 0.2
    ) -> Optional[dict]:
        raw = self._complete(prompt, temperature=temperature)
        if not raw:
            return None
        cleaned = _strip_fence(raw)
        try:
            return json.loads(cleaned)
        except Exception:
            m = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if not m:
                return None
            try:
                return json.loads(m.group(0))
            except Exception:
                return None

    def suggest_heading(self, text: str) -> Optional[str]:
        if not text:
            return None
        body = text[:4000]
        prompt = (
            "Propose a concise Heading 2 title (≤10 words) for the passage. "
            "Return only the title, no markdown:\n\n" + body
        )
        out = self._complete(prompt, temperature=0.1)
        if not out:
            return None
        return out.splitlines()[0].strip(" #\t")[:120] or None

    def rewrite_paragraph(self, text: str) -> Optional[str]:
        if not text or len(text.strip()) < 8:
            return None
        body = text[:6000]
        prompt = (
            "Rewrite the paragraph for clarity and flow, preserving meaning. "
            "Plain text only (no markdown headings/fences). 2–4 sentences.\n\n" + body
        )
        return self._complete(prompt, temperature=0.2)

    def analyze(self, text: str) -> Optional[AnalysisOut]:
        if not text or len(text.strip()) < 8:
            return None
        body = text[:6000]
        prompt = (
            "Read and comprehend the passage. Return JSON with keys:\n"
            "  text     : rewritten plain text (no markdown)\n"
            '  style    : one of ["Body","Code","Bullet","Quote"]\n'
            '  heading  : optional concise H2 (≤10 words) or ""\n'
            "  keypoints: array of 3–7 short bullet points\n"
            "  keywords : array of 3–10 single- or two-word tags\n"
            "Only JSON. No extra commentary.\n\n" + body
        )
        data = self._complete_json(prompt, temperature=0.2)
        if not isinstance(data, dict):
            return None
        txt = (data.get("text") or "").strip()
        if not txt:
            return None
        style = _coerce_style(str(data.get("style") or "Body"))
        heading_raw = (data.get("heading") or "").strip()
        heading = heading_raw[:120] if heading_raw else None
        keypoints = [
            str(x).strip() for x in (data.get("keypoints") or []) if str(x).strip()
        ][:7]
        keywords = [
            str(x).strip() for x in (data.get("keywords") or []) if str(x).strip()
        ][:10]
        return AnalysisOut(
            text=txt,
            style=style,
            heading=heading,
            keypoints=keypoints,
            keywords=keywords,
        )


__all__ = [
    "AIProvider",
    "AnalysisOut",
    "AICallMeter",
    "DummyProvider",
    "OpenAIProvider",
]
