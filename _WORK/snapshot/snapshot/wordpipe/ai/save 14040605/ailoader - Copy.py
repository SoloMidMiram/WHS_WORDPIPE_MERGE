# ai/ailoader.py — wire provider logging + cost
from __future__ import annotations
import os, logging
from logging import StreamHandler, FileHandler, Formatter
from pathlib import Path
from datetime import datetime
from timefmt import tehran_filename_stamp
from helpers import OpenAIProvider, DummyProvider, AICallMeter
from reorganize import reorganize_document
from logging_tools import evt

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

# at top
import httpx


def _canary(ai):
    # tiny prompt to verify we can reach the API; safe and cheap
    try:
        if hasattr(ai, "_complete"):
            out = ai._complete(
                "ping", temperature=0.0
            )  # will log ai_call/ai_call_error
            return bool(out is not None)
    except Exception:
        return False
    return False


def _build_ai(logger, jsonl_path):
    meter = AICallMeter(max_tokens=TOKEN_BUDGET, per_section_cap=CAP_REWRITES_PER_CHUNK)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key and OpenAI is not None:
        try:
            proxy = os.getenv("HTTPS_PROXY") or os.getenv(
                "HTTP_PROXY"
            )  # use env if present
            http_client = None
            if proxy:
                http_client = httpx.Client(
                    proxies={"http://": proxy, "https://": proxy},
                    timeout=30.0,
                )
            client = (
                OpenAI(api_key=api_key, http_client=http_client)
                if http_client
                else OpenAI(api_key=api_key)
            )
            return OpenAIProvider(
                client,
                model=OPENAI_MODEL,
                meter=meter,
                logger=logger,
                jsonl_path=jsonl_path,
                price_in_per_mtok=PRICE_IN,
                price_out_per_mtok=PRICE_OUT,
            )
        except Exception:
            pass
    return DummyProvider(meter=meter)


try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

IN_PATH = os.getenv("AI_IN", "Word Horror Stories.docx")
OUT_DIR = os.getenv("AI_OUT_DIR", "data/outputs")
OUT_PREF = os.getenv("AI_PREFIX", "ai_")
TOKEN_BUDGET = int(os.getenv("AI_TOKEN_BUDGET", "5000"))
CAP_REWRITES_PER_CHUNK = int(os.getenv("AI_CAP_PER_CHUNK", "8"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
PRICE_IN = float(os.getenv("OPENAI_PRICE_IN", "0") or 0)  # USD / 1M input tokens
PRICE_OUT = float(os.getenv("OPENAI_PRICE_OUT", "0") or 0)  # USD / 1M output tokens


def _make_logger():
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    text_path = log_dir / f"ai_reorg_{ts}.log"
    jsonl_path = log_dir / f"ai_reorg_{ts}.jsonl"
    logger = logging.getLogger("ai_reorg")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    sh = StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(Formatter("%(asctime)s | %(levelname)s | %(message)s", "%H:%M:%S"))
    fh = FileHandler(text_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    )
    if not logger.handlers:
        logger.addHandler(sh)
        logger.addHandler(fh)
    return logger, str(jsonl_path)


def _resolve_in_path(p: str) -> str:
    pth = Path(p)
    probes = [Path("."), Path(".."), Path("../.."), Path("data"), Path("data/inputs")]
    if pth.is_file():
        return str(pth.resolve())
    for probe in probes:
        cand = (probe / p).resolve()
        if cand.is_file():
            return str(cand)
    raise FileNotFoundError(f"Input DOCX not found: {p}")


def _make_out_path(in_abs: str, out_dir: str, prefix: str) -> str:
    base = Path(out_dir)
    base.mkdir(parents=True, exist_ok=True)
    stem = Path(in_abs).stem
    safe = "".join(ch for ch in stem if ch not in '<>:"/\\|?*')
    stamp = tehran_filename_stamp()
    return str((base / f"{prefix}{safe}__{stamp}.docx").resolve())


def _build_ai(logger, jsonl_path):
    meter = AICallMeter(max_tokens=TOKEN_BUDGET, per_section_cap=CAP_REWRITES_PER_CHUNK)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key and OpenAI is not None:
        try:
            client = OpenAI(api_key=api_key)
            return OpenAIProvider(
                client,
                model=OPENAI_MODEL,
                meter=meter,
                logger=logger,
                jsonl_path=jsonl_path,
                price_in_per_mtok=PRICE_IN,
                price_out_per_mtok=PRICE_OUT,
            )
        except Exception:
            pass
    return DummyProvider(meter=meter)


def main():
    logger, jsonl_path = _make_logger()

    in_abs = _resolve_in_path(IN_PATH)
    out_abs = _make_out_path(in_abs, OUT_DIR, OUT_PREF)

    ai = _build_ai(logger, jsonl_path)  # ← build first

    # optional quick reachability poke; logs ai_call or ai_call_error
    ok = _canary(ai) if ai.__class__.__name__ == "OpenAIProvider" else True
    evt(logger, jsonl_path, "INFO", "ai_connectivity_ok", ok=ok)

    evt(
        logger,
        jsonl_path,
        "INFO",
        "start",
        in_path=in_abs,
        out_path=out_abs,
        provider=ai.__class__.__name__,
        model=os.getenv("OPENAI_MODEL"),
    )

    final = reorganize_document(
        in_path=in_abs,
        out_path=out_abs,
        ai=ai,
        cap_per_chunk=CAP_REWRITES_PER_CHUNK,
        logger=logger,
        jsonl_path=jsonl_path,
    )

    usage = getattr(ai, "get_usage", lambda: {})()
    evt(logger, jsonl_path, "INFO", "ai_usage_total", **usage)
    evt(logger, jsonl_path, "INFO", "done", out=final)


if __name__ == "__main__":
    main()
