#!/usr/bin/env python3
"""Minimal, reusable API canary for OpenAI Responses API.

Run:
  python scripts/ai/canary_openai.py --model gpt-4o-mini

Env:
  OPENAI_API_KEY=sk-... [required]
  OPENAI_BASE_URL=https://api.openai.com/v1 (optional override)
  OPENAI_ORG=org_... (optional)

Exit code 0 on success; non-zero on failure.

NOTE: This is an executable script, not a pytest module.
The name deliberately avoids the ``test_`` prefix so pytest does not
auto-discover it at repo root.
"""

import os
import sys
import time
import argparse
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


@dataclass
class CanaryResult:
    ok: bool
    latency_ms: int | None = None
    text: str | None = None
    error: str | None = None


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    base = os.getenv("OPENAI_BASE_URL")  # optional
    org = os.getenv("OPENAI_ORG")  # optional
    kw = {"api_key": api_key}
    if base:
        kw["base_url"] = base
    if org:
        kw["organization"] = org
    return OpenAI(**kw)


def canary_prompt(model: str) -> CanaryResult:
    client = get_client()
    try:
        t0 = time.perf_counter()
        resp = client.responses.create(
            model=model, input="Say 'pong' exactly once. No punctuation."
        )
        dt = int((time.perf_counter() - t0) * 1000)
        text = resp.output_text.strip() if hasattr(resp, "output_text") else ""
        return CanaryResult(ok=(text.lower() == "pong"), latency_ms=dt, text=text)
    except Exception as e:
        return CanaryResult(ok=False, error=str(e))


def canary_reasoning_summary(model: str) -> CanaryResult:
    client = get_client()
    try:
        t0 = time.perf_counter()
        resp = client.responses.create(
            model=model,
            input="In one short line, answer: 2+2=?",
            reasoning={"effort": "low"},
            temperature=0,
        )
        dt = int((time.perf_counter() - t0) * 1000)
        text = resp.output_text.strip() if hasattr(resp, "output_text") else ""
        return CanaryResult(ok=("4" in text), latency_ms=dt, text=text)
    except Exception as e:
        return CanaryResult(ok=False, error=str(e))


def pretty(r: CanaryResult, title: str):
    print(f"=== {title}: {'OK' if r.ok else 'FAIL'} ===")
    if r.latency_ms is not None:
        print("latency_ms:", r.latency_ms)
    if r.text is not None:
        print("text:", r.text)
    if r.error:
        print("error:", r.error)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()

    try:
        _ = get_client()
    except Exception as e:
        print("FATAL: cannot create OpenAI client:", e, file=sys.stderr)
        sys.exit(2)

    r1 = canary_prompt(args.model)
    pretty(r1, "canary_prompt")
    code = 0 if r1.ok else 1

    if args.summary:
        r2 = canary_reasoning_summary(args.model)
        pretty(r2, "canary_reasoning_summary")
        code = code or (0 if r2.ok else 1)

    sys.exit(code)


if __name__ == "__main__":
    main()
