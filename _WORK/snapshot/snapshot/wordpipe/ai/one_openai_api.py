"""
One-function OpenAI Responses API multipurpose helper (canary, text, stream, structured, tools)

Usage examples (Python):

from one_openai_api import one

# 1) Canary
one(task="canary", expect="OK")

# 2) Plain text
txt = one(task="text", prompt="Explain attention in transformers in one sentence")
print(txt)

# 3) Streaming (prints tokens as they arrive, returns the final text)
final = one(task="stream", prompt="Write 2 haiku about late-night debugging.")

# 4) Structured JSON (uses default schema if you don’t pass one)
obj = one(task="structured", prompt="Recommend one 1990s sci‑fi movie with 2 reasons")
print(obj)

# 5) Tools demo (hypot)
ans = one(task="tools", prompt="Given legs 5 and 12, use the tool to compute the hypotenuse and report it.")
print(ans)

Environment: set OPENAI_API_KEY in your shell or a .env file.
"""

import os
import sys
import json
import math
import time
from functools import wraps

try:
    from dotenv import load_dotenv  # optional
except Exception:  # pragma: no cover
    load_dotenv = lambda *a, **k: None

from openai import OpenAI
from openai import APIStatusError, RateLimitError, APITimeoutError


def one(
    task: str,
    prompt: str | None = None,
    *,
    key: str | None = None,
    model: str = "gpt-4.1-mini",
    expect: str = "OK",
    schema: dict | None = None,
    tools: list[dict] | None = None,
    stream: bool | None = None,
    verbose: bool = True,
    timeout: float = 20.0,
    disable_proxies: bool = False,
    proxy: (
        str | None
    ) = None,  # NEW: "http://127.0.0.1:10809" or "socks5h://127.0.0.1:10808"
):
    """
    A single entry point for common OpenAI Responses API workflows.

    Parameters
    ----------
    task : str
        One of: "canary", "text", "stream", "structured", "tools".
    prompt : str | None
        The user instruction / content for the model.
    key : str | None
        API key; falls back to OPENAI_API_KEY env.
    model : str
        Model name; default "gpt-4.1-mini" for cost/latency.
    expect : str
        For canary: the exact string expected from the model.
    schema : dict | None
        JSON schema for structured outputs. If None, a small demo schema is used.
    tools : list[dict] | None
        Tool definitions for function-calling. If None, a demo hypot tool is used.
    stream : bool | None
        Force streaming behavior where relevant. If None, inferred by task.
    verbose : bool
        Print helpful info to stdout.

    Returns
    -------
    Any
        - canary: returns True on success (raises on failure)
        - text: str
        - stream: str (final text)
        - structured: dict (parsed JSON)
        - tools: str (final narrated answer)
    """

    # 0) Key + client
    load_dotenv()
    api_key = key or os.getenv("OPENAI_API_KEY")
    assert api_key and api_key.startswith("sk-"), "OPENAI_API_KEY missing or malformed"

    # Optional: disable proxies that can cause TLS handshakes to hang
    if disable_proxies:
        for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
            if os.environ.pop(v, None) and verbose:
                print(f"[net] unset {v}")

    if (
        any(
            os.getenv(v)
            for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy")
        )
        and verbose
    ):
        print(
            "[net] Proxy vars detected; if you see TLS hangs, try disable_proxies=True or --no-proxy"
        )

    # Respect explicit proxy if given; else let env vars drive it
    http_client = None
    if proxy:
        import httpx

        http_client = httpx.Client(proxies=proxy, timeout=timeout)

    client = OpenAI(api_key=api_key, timeout=timeout, http_client=http_client)

    # 1) Retry wrapper for transient errors
    def with_backoff(max_retries=5, base=0.5, factor=2.0):
        def deco(fn):
            @wraps(fn)
            def wrapped(*a, **kw):
                attempt, delay = 0, base
                while True:
                    try:
                        return fn(*a, **kw)
                    except (RateLimitError, APITimeoutError, APIStatusError) as e:
                        msg = str(e)
                        # Fast-fail on non-retriable conditions
                        non_retriable = (
                            "insufficient_quota" in msg
                            or "invalid_api_key" in msg
                            or ("401" in msg and "Invalid" in msg)
                        )
                        if non_retriable:
                            raise
                        attempt += 1
                        if attempt > max_retries:
                            raise
                        if verbose:
                            print(
                                f"[retry] {type(e).__name__} → sleep {delay:.2f}s (attempt {attempt}/{max_retries})"
                            )
                        time.sleep(delay)
                        delay *= factor

            return wrapped

        return deco

    # 2) Mode handlers (as inner blocks to honor the "one function" request)

    if task == "canary":
        assert prompt is None or isinstance(prompt, str)

        @with_backoff()
        def _call():
            try:
                return client.responses.create(
                    model=model, input=f"Return exactly '{expect}'."
                )
            except RateLimitError as e:
                if "insufficient_quota" in str(e):
                    raise RuntimeError(
                        "[CANARY] FAIL — Insufficient quota on this API key"
                    ) from e
                raise

        r = _call()
        text = r.output_text.strip()
        if verbose:
            print(f"[CANARY] reply={text!r}")
        assert text == expect, f"Unexpected reply: {text!r} (expected {expect!r})"
        if verbose:
            print("[CANARY] PASS")
        return True

    if task == "text":
        assert isinstance(prompt, str) and prompt.strip(), "prompt required"

        @with_backoff()
        def _call():
            return client.responses.create(model=model, input=prompt)

        r = _call()
        return r.output_text

    if task == "stream":
        assert isinstance(prompt, str) and prompt.strip(), "prompt required"

        # streaming prints deltas to stdout, returns final text
        text_parts: list[str] = []
        try:
            with client.responses.stream(model=model, input=prompt) as stream_obj:
                for event in stream_obj:
                    if event.type == "response.output_text.delta":
                        sys.stdout.write(event.delta)
                        sys.stdout.flush()
                        text_parts.append(event.delta)
                final = stream_obj.get_final_response()
        except (RateLimitError, APITimeoutError, APIStatusError):
            raise
        final_text = (
            "".join(text_parts) if text_parts else (final.output_text if final else "")
        )
        if verbose:
            print("\n[STREAM] done")
        return final_text

    if task == "structured":
        assert isinstance(prompt, str) and prompt.strip(), "prompt required"

        schema = schema or {
            "name": "MoviePick",
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "year": {"type": "integer"},
                    "reasons": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title", "year", "reasons"],
                "additionalProperties": False,
            },
        }

        @with_backoff()
        def _call():
            return client.responses.parse(
                model=model,
                input=prompt,
                response_format={"type": "json_schema", "json_schema": schema},
            )

        r = _call()
        return r.output_parsed

    if task == "tools":
        assert isinstance(prompt, str) and prompt.strip(), "prompt required"

        tools = tools or [
            {
                "type": "function",
                "name": "hypot",
                "description": "Compute sqrt(a^2 + b^2)",
                "parameters": {
                    "type": "object",
                    "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                    "required": ["a", "b"],
                },
            }
        ]

        @with_backoff()
        def _first():
            return client.responses.create(model=model, input=prompt, tools=tools)

        r1 = _first()

        # inspect for tool call
        tool_result = None
        for item in getattr(r1, "output", []) or []:
            if getattr(item, "type", None) == "tool_call":
                name = getattr(item, "name", None)
                args = getattr(item, "arguments", {})
                if name == "hypot":
                    a = float(args.get("a"))
                    b = float(args.get("b"))
                    tool_result = math.hypot(a, b)
                    break

        if tool_result is None:
            # No tool call, just return the text
            return r1.output_text

        # Send tool result back for a narrated response
        @with_backoff()
        def _second():
            return client.responses.create(
                model=model,
                input=[
                    {"role": "user", "content": "Report the numeric result clearly."},
                    {"role": "tool", "name": "hypot", "content": str(tool_result)},
                ],
            )

        r2 = _second()
        return r2.output_text

    raise ValueError(f"Unknown task: {task!r}")


if __name__ == "__main__":
    # Minimal CLI for quick manual runs
    import argparse

    p = argparse.ArgumentParser(description="One-function OpenAI helper")
    p.add_argument(
        "task",
        nargs="?",
        choices=["canary", "text", "stream", "structured", "tools"],
        default="canary",
    )
    p.add_argument("--prompt", dest="prompt", help="User prompt / input", default=None)
    p.add_argument("--model", dest="model", default="gpt-4.1-mini")
    p.add_argument("--expect", dest="expect", default="OK")
    p.add_argument("--timeout", dest="timeout", type=float, default=20.0)
    p.add_argument("--no-proxy", dest="no_proxy", action="store_true")
    p.add_argument("--verbose", action="store_true")
    # ... inside __main__:
    p.add_argument("--proxy", dest="proxy", default=None)  # NEW

    args = p.parse_args()

    out = one(
        task=args.task,
        prompt=args.prompt,
        model=args.model,
        expect=args.expect,
        timeout=args.timeout,
        disable_proxies=args.no_proxy,
        verbose=args.verbose,
        proxy=args.proxy,
    )
    if out is True:
        pass
    elif isinstance(out, (dict, list)):
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif out is not None:
        print(out)
