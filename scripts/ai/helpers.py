# ai/helpers.py — OpenAI-backed comprehension with cost/usage logging
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Protocol, Literal, List, Tuple
import json, os, re, math
from time import perf_counter
from logging_tools import evt

# --- make exception imports safe if openai isn't installed ---
try:
    from openai import (
        APIStatusError,
        APIConnectionError,
        AuthenticationError,
        RateLimitError,
    )
except Exception:  # fallback so Dummy works without openai installed
    APIStatusError = APIConnectionError = AuthenticationError = RateLimitError = (
        Exception
    )

StyleLabel = Literal["Body", "Code", "Bullet", "Quote"]


# ---------- Data shapes ----------
@dataclass(frozen=True)
class AnalysisOut:
    text: str
    style: StyleLabel = "Body"
    heading: Optional[str] = None
    keypoints: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class OverviewOut:
    abstract: str
    keypoints: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


class AIProvider(Protocol):
    def suggest_heading(self, text: str) -> Optional[str]: ...
    def rewrite_paragraph(self, text: str) -> Optional[str]: ...
    def analyze(self, text: str) -> Optional[AnalysisOut]: ...

    # optional but used by orchestrator now:
    def overview(self, text: str) -> Optional[OverviewOut]: ...


# ---------- Rough estimator (fallback only) ----------
def _tok_est(s: str) -> int:
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


# ---------- Simple meter for “caps” ----------
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


# ---------- Dummy (offline) ----------
class DummyProvider:
    def __init__(self, meter: Optional[AICallMeter] = None, prefix: str = "AI", **_):
        self.meter = meter or AICallMeter()
        self.prefix = prefix
        self._usage = {"calls": 0, "in": 0, "out": 0, "cost": 0.0}

    # no costs/tokens in dummy; we just simulate small spend in meter
    def _bump(self, prompt: str, out: str = ""):
        self._usage["calls"] += 1
        self.meter.spend(_tok_est(prompt))

    def suggest_heading(self, text: str) -> Optional[str]:
        if not text:
            return None
        first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "Untitled")
        self._bump(text)
        return f"{self.prefix} — {first[:100].strip(' #')}".strip()

    def rewrite_paragraph(self, text: str) -> Optional[str]:
        if not text or len(text.strip()) < 8:
            return None
        self._bump(text, text)
        return f"[clarified] {text.strip()}"

    def analyze(self, text: str) -> Optional[AnalysisOut]:
        if not text or len(text.strip()) < 8:
            return None
        t = text.strip()
        looks_code = (
            any(sym in t for sym in ("def ", "class ", "{", "}", ";")) or "```" in t
        )
        looks_bul = t.lstrip().startswith(("-", "*", "•"))
        style = "Code" if looks_code else ("Bullet" if looks_bul else "Body")
        heading = f"{self.prefix} — Summary" if len(t) > 60 and not looks_code else None
        pts = [s.strip() for s in re.split(r"[.!?]\s+", t) if s.strip()][:3]
        tags = [w for w in re.findall(r"[A-Za-z]{4,}", t)[:5]]
        self._bump(t)
        return AnalysisOut(
            text=f"[clarified] {t}",
            style=style,
            heading=heading,
            keypoints=pts,
            keywords=tags,
        )

    def overview(self, text: str) -> Optional[OverviewOut]:
        if not text or len(text.strip()) < 8:
            return None
        self._bump(text)
        head = "High-level summary of document sections."
        pts = [p.strip() for p in re.split(r"[.!?]\s+", text) if p.strip()][:5]
        kws = list({w.lower() for w in re.findall(r"[A-Za-z]{5,}", text)})[:10]
        return OverviewOut(abstract=head, keypoints=pts, keywords=kws)

    def get_usage(self) -> dict:
        return dict(self._usage)


# ---------- OpenAI Provider (with usage + cost logging) ----------
class OpenAIProvider:
    """
    Works with Responses API (preferred) or Chat Completions.
    Tracks real token usage and optional cost.
    Set prices (USD per 1M tokens) via env or kwargs:
      OPENAI_PRICE_IN, OPENAI_PRICE_OUT  (floats, e.g., 2.5 and 10.0)
    """

    def __init__(
        self,
        client,
        model: Optional[str] = None,
        meter: Optional[AICallMeter] = None,
        *,
        logger=None,
        jsonl_path: Optional[str] = None,
        price_in_per_mtok: Optional[float] = None,
        price_out_per_mtok: Optional[float] = None,
    ):
        if client is None:
            raise RuntimeError("OpenAI client is required")
        self.client = client
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.meter = meter or AICallMeter()
        self.logger = logger
        self.jsonl_path = jsonl_path
        self.usage_calls = 0
        self.usage_in = 0
        self.usage_out = 0
        self.price_in = (
            price_in_per_mtok
            if price_in_per_mtok is not None
            else float(os.getenv("OPENAI_PRICE_IN", "0") or 0)
        )
        self.price_out = (
            price_out_per_mtok
            if price_out_per_mtok is not None
            else float(os.getenv("OPENAI_PRICE_OUT", "0") or 0)
        )
        self.cost_in_usd = 0.0
        self.cost_out_usd = 0.0

    def _log_api_call(
        self,
        endpoint: str,
        in_tok: int,
        out_tok: int,
        ms: int,
        ok: bool,
        prompt_len: int,
        out_len: int,
    ):
        inc_cost_in = (in_tok / 1_000_000.0) * self.price_in if self.price_in else 0.0
        inc_cost_out = (
            (out_tok / 1_000_000.0) * self.price_out if self.price_out else 0.0
        )
        self.cost_in_usd += inc_cost_in
        self.cost_out_usd += inc_cost_out
        evt(
            self.logger,
            self.jsonl_path,
            "INFO",
            "ai_call",
            model=self.model,
            endpoint=endpoint,
            ok=ok,
            tokens_in=in_tok,
            tokens_out=out_tok,
            ms=ms,
            cost_in_usd=round(inc_cost_in, 6),
            cost_out_usd=round(inc_cost_out, 6),
            prompt_chars=prompt_len,
            out_chars=out_len,
        )

    def _complete(self, prompt: str, *, temperature: float = 0.2) -> Optional[str]:
        need_est = _tok_est(prompt)
        if not self.meter.can_spend(need_est):
            return None

        t0 = perf_counter()
        out_text, used_in, used_out, endpoint = None, 0, 0, "unknown"

        try:
            try:
                # Prefer Responses
                if hasattr(self.client, "responses"):
                    endpoint = "responses.create"
                    r = self.client.responses.create(
                        model=self.model, input=prompt, temperature=temperature
                    )
                    out_text = getattr(r, "output_text", None)
                    # usage: r.usage.input_tokens / output_tokens (OpenAI docs). :contentReference[oaicite:1]{index=1}
                    u = getattr(r, "usage", None)
                    if u:
                        used_in = (
                            getattr(u, "input_tokens", 0)
                            or getattr(u, "prompt_tokens", 0)
                            or 0
                        )
                        used_out = (
                            getattr(u, "output_tokens", 0)
                            or getattr(u, "completion_tokens", 0)
                            or 0
                        )

                # Fallback: Chat Completions
                if (
                    out_text is None
                    and hasattr(self.client, "chat")
                    and hasattr(self.client.chat, "completions")
                ):
                    endpoint = "chat.completions.create"
                    cr = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                    )
                    out_text = (cr.choices[0].message.content or "").strip()
                    # usage: cr.usage.prompt_tokens / completion_tokens. :contentReference[oaicite:2]{index=2}
                    u = getattr(cr, "usage", None)
                    if u:
                        used_in = getattr(u, "prompt_tokens", 0) or 0
                        used_out = getattr(u, "completion_tokens", 0) or 0
            except (
                APIStatusError,
                APIConnectionError,
                AuthenticationError,
                RateLimitError,
                Exception,
            ) as e:
                ms = int((perf_counter() - t0) * 1000)
                # Try to extract HTTP status and message
                status = getattr(getattr(e, "response", None), "status_code", None)
                errtxt = str(getattr(getattr(e, "response", None), "text", ""))[
                    :500
                ] or str(e)
                evt(
                    self.logger,
                    self.jsonl_path,
                    "ERROR",
                    "ai_call_error",
                    model=self.model,
                    endpoint=endpoint,
                    ms=ms,
                    status=status,
                    error=errtxt,
                )
                self._log_api_call(
                    endpoint, 0, 0, ms, ok=False, prompt_len=len(prompt), out_len=0
                )
                return None

        except Exception:
            ms = int((perf_counter() - t0) * 1000)
            self._log_api_call(
                endpoint, 0, 0, ms, ok=False, prompt_len=len(prompt), out_len=0
            )
            return None

        ms = int((perf_counter() - t0) * 1000)
        # Totals
        self.usage_calls += 1
        self.usage_in += used_in
        self.usage_out += used_out
        self.meter.spend(used_in + used_out if (used_in or used_out) else need_est)
        self._log_api_call(
            endpoint,
            used_in,
            used_out,
            ms,
            ok=out_text is not None,
            prompt_len=len(prompt),
            out_len=len(out_text or ""),
        )

        return out_text.strip() if out_text else None

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

    # ---------- Public high-level ops ----------
    def suggest_heading(self, text: str) -> Optional[str]:
        if not text:
            return None
        out = self._complete(
            "Propose a concise H2 title (≤10 words). Return only the title; no markdown.\n\n"
            + text[:4000],
            temperature=0.1,
        )
        if not out:
            return None
        return out.splitlines()[0].strip(" #\t")[:120] or None

    def rewrite_paragraph(self, text: str) -> Optional[str]:
        if not text or len(text.strip()) < 8:
            return None
        return self._complete(
            "Rewrite the paragraph for clarity and flow, preserving meaning. "
            "Plain text only (no markdown headings/fences). 2–4 sentences.\n\n"
            + text[:6000],
            temperature=0.2,
        )

    def analyze(self, text: str) -> Optional[AnalysisOut]:
        if not text or len(text.strip()) < 8:
            return None
        data = self._complete_json(
            "Read and comprehend the passage. Return JSON with keys:\n"
            "  text     : rewritten plain text (no markdown)\n"
            '  style    : one of ["Body","Code","Bullet","Quote"]\n'
            "  heading  :optional concise H2 (≤10 words)\n"
            "  keypoints: 3–7 bullet points\n"
            "  keywords : 3–10 tags (single or two words)\n"
            "Only JSON. No extra commentary.\n\n" + text[:6000],
            temperature=0.2,
        )
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

    def overview(self, text: str) -> Optional[OverviewOut]:
        if not text or len(text.strip()) < 8:
            return None
        data = self._complete_json(
            "Produce a document overview. Return JSON with:\n"
            "  abstract : 120–200 words executive summary (no markdown)\n"
            "  keypoints: 5–10 bullets of main themes\n"
            "  keywords : 8–15 topical tags\n"
            "Only JSON. No extra text.\n\n" + text[:12000],
            temperature=0.2,
        )
        if not isinstance(data, dict):
            return None
        abstract = (data.get("abstract") or "").strip()
        keypoints = [
            str(x).strip() for x in (data.get("keypoints") or []) if str(x).strip()
        ][:10]
        keywords = [
            str(x).strip() for x in (data.get("keywords") or []) if str(x).strip()
        ][:15]
        if not abstract:
            return None
        return OverviewOut(abstract=abstract, keypoints=keypoints, keywords=keywords)

    def get_usage(self) -> dict:
        total_cost = self.cost_in_usd + self.cost_out_usd
        return {
            "calls": self.usage_calls,
            "tokens_in": self.usage_in,
            "tokens_out": self.usage_out,
            "price_in_per_mtok": self.price_in,
            "price_out_per_mtok": self.price_out,
            "cost_in_usd": round(self.cost_in_usd, 6),
            "cost_out_usd": round(self.cost_out_usd, 6),
            "cost_total_usd": round(total_cost, 6),
        }


__all__ = [
    "AIProvider",
    "AnalysisOut",
    "OverviewOut",
    "AICallMeter",
    "DummyProvider",
    "OpenAIProvider",
]
