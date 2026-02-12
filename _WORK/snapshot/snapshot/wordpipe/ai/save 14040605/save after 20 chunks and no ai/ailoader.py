# ai/ailoader.py — AI-only runner with JSONL logging via logging_tools.evt
from __future__ import annotations

import os, logging
from logging import StreamHandler, FileHandler, Formatter
from pathlib import Path
from datetime import datetime

from timefmt import tehran_filename_stamp

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

from helpers import OpenAIProvider, DummyProvider, AICallMeter
from reorganize import reorganize_document
from logging_tools import evt

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

IN_PATH = os.getenv("AI_IN", "Word Horror Stories.docx")
OUT_DIR = os.getenv("AI_OUT_DIR", "data/outputs")
OUT_PREFIX = os.getenv("AI_PREFIX", "ai_")
TOKEN_BUDGET = int(os.getenv("AI_TOKEN_BUDGET", "5000"))
CAP_REWRITES_PER_CHUNK = int(os.getenv("AI_CAP_PER_CHUNK", "8"))


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

    # sanitize stem for safety (remove characters illegal on Windows)
    safe_stem = "".join(ch for ch in stem if ch not in '<>:"/\\|?*')

    stamp = tehran_filename_stamp()  # e.g., 1404-05-23_13-45_Tehran
    return str((base / f"{prefix}{safe_stem}__{stamp}.docx").resolve())


def _build_ai():
    meter = AICallMeter(max_tokens=TOKEN_BUDGET, per_section_cap=CAP_REWRITES_PER_CHUNK)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key and OpenAI is not None:
        try:
            client = OpenAI(api_key=api_key)
            return OpenAIProvider(client, meter=meter)
        except Exception:
            pass
    return DummyProvider(meter=meter)


def main():
    logger, jsonl_path = _make_logger()
    in_abs = _resolve_in_path(IN_PATH)
    out_abs = _make_out_path(in_abs, OUT_DIR, OUT_PREFIX)
    ai = _build_ai()

    evt(
        logger,
        jsonl_path,
        "INFO",
        "start",
        in_path=in_abs,
        out_path=out_abs,
        provider=ai.__class__.__name__,
    )

    final = reorganize_document(
        in_path=in_abs,
        out_path=out_abs,
        ai=ai,
        cap_per_chunk=CAP_REWRITES_PER_CHUNK,
        logger=logger,
        jsonl_path=jsonl_path,
    )

    evt(
        logger,
        jsonl_path,
        "INFO",
        "done",
        out=final,
        tokens_used=getattr(getattr(ai, "meter", None), "used_tokens", None),
    )


if __name__ == "__main__":
    main()
