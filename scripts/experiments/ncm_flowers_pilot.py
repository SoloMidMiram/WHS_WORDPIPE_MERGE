"""Compare disclosure-safe synthetic Flowers context packets."""
import argparse
import hashlib
import json
import os
import re
import signal
import statistics
import subprocess
import tempfile
import time
import tracemalloc
from importlib.metadata import version
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "ncm_flowers_synthetic.json"
GOLD = FIXTURES.with_name("ncm_flowers_synthetic_gold.json")
GPT2_SHA256 = "8414cab924d8b9b33013f0d221c5862f365ee9be39c5c2bfae8a5a9e970478a6"
MAX_INPUT_BYTES = 16_384
MAX_OUTPUT_BYTES = 4_096
MAX_RESPONSE_BYTES = 32_768
X_SUM_PREFIX_TOKENS = 512
X_SUM_OUTPUT_SLOTS = 48


def source_text(case):
    return "## " + case["title"] + "\n\n" + "\n".join(case["lines"])


def source_digest(case):
    return hashlib.sha256(source_text(case).encode("utf-8")).hexdigest()


def load_cases():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    if data["scope"] != "synthetic" or data["schema"] != "whs-ncm-pilot-source-v2":
        raise ValueError("Only the reviewed synthetic suite is supported")
    cases = data["cases"]
    if len({case["source_reference"] for case in cases}) != len(cases):
        raise ValueError("Duplicate source reference")
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("Duplicate case identifier")
    return cases


def load_gold(cases):
    data = json.loads(GOLD.read_text(encoding="utf-8"))
    gold = data["facts"]
    if data["schema"] != "whs-ncm-pilot-gold-v1" or set(gold) != {case["id"] for case in cases}:
        raise ValueError("Gold references do not match the synthetic suite")
    for case in cases:
        if any(not fact["literal"] or fact["literal"] not in source_text(case) for fact in gold[case["id"]]):
            raise ValueError(f"Annotation missing from source for {case['id']}")
    return gold


def identity(case):
    return {"reference": case["source_reference"], "section": case["id"], "sha256": source_digest(case)}


def packet(case, text, protected=()):
    return {
        "task": "Answer using the supplied source. Keep constraints and uncertainty intact.",
        "query": case["query"],
        "source": identity(case),
        "text": text,
        "protected_source_lines": list(protected),
    }


def terms(text):
    return set(re.findall(r"\w+", text.casefold()))


def extractive_packet(case):
    query = terms(case["query"])
    hits = [(len(terms(line) & query), i) for i, line in enumerate(case["lines"])]
    ranked = sorted((hit for hit in hits if hit[0]), key=lambda hit: (-hit[0], hit[1]))
    if not ranked:
        return packet(case, source_text(case)), "no_keyword_match_raw"
    lines = [case["lines"][i] for _, i in sorted(ranked[:2], key=lambda hit: hit[1])]
    return packet(case, "\n".join(lines)), "extracted"


def subprocess_backend(argv, *, cwd):
    """Adapt a qualified worker that must use input_ids and report the number it consumed."""
    argv = tuple(argv)
    if not argv or not Path(argv[0]).is_absolute():
        raise ValueError("Worker executable must be an explicit absolute path")
    environment = {key: os.environ[key] for key in ("SYSTEMROOT",) if key in os.environ}

    def run(request, *, timeout_seconds):
        # A file avoids pipe deadlock on timeout; the external isolation owns disk limits.
        with tempfile.TemporaryFile() as stdin, tempfile.TemporaryFile() as stdout:
            stdin.write(serialize(request).encode("utf-8"))
            stdin.seek(0)
            with subprocess.Popen(
                argv, cwd=cwd, env=environment, start_new_session=os.name == "posix",
                stdin=stdin, stdout=stdout, stderr=subprocess.DEVNULL,
            ) as child:
                try:
                    code = child.wait(timeout=timeout_seconds)
                except subprocess.TimeoutExpired as exc:
                    try:
                        if os.name == "posix":
                            os.killpg(child.pid, signal.SIGKILL)
                        else:
                            child.kill()
                    except ProcessLookupError:
                        pass
                    child.wait()
                    raise TimeoutError("Worker deadline exceeded") from exc
                if code != 0:
                    raise OSError(f"Worker exited with status {code}")
            stdout.seek(0)
            raw = stdout.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ValueError("Worker response exceeds its byte limit")
            return json.loads(raw)

    return run


def evaluate_candidate(case, backend=None, review=None, *, encode_input=None, timeout_seconds=30):
    if backend is None:
        return {"status": "not_run", "reason": "backend_not_configured", "candidate": None, "effective": None}
    if not 0 < timeout_seconds <= 300:
        raise ValueError("Timeout must be positive and at most 300 seconds")

    def fallback(reason, candidate=None):
        return {"status": "fallback", "reason": reason, "route": "raw",
                "candidate": candidate, "effective": packet(case, source_text(case))}

    text = source_text(case)
    if not text.strip() or len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        return fallback("input_limit")
    if encode_input is None:
        return fallback("tokenizer_unavailable")
    input_ids = encode_input(text)
    if not 0 < len(input_ids) <= X_SUM_PREFIX_TOKENS:
        return fallback("input_limit")
    request = {
        "text": text,
        "input_ids": input_ids,
        "source": identity(case),
        "load_policy": {"weights_only": True, "map_location": "cpu"},
        "max_input_tokens": X_SUM_PREFIX_TOKENS,
        "max_output_slots": X_SUM_OUTPUT_SLOTS,
    }
    try:
        response = backend(request, timeout_seconds=timeout_seconds)
    except TimeoutError:
        return fallback("timeout")
    except FileNotFoundError:
        return fallback("missing_checkpoint")
    except (OSError, ValueError):
        return fallback("backend_error")

    if not isinstance(response, dict) or not isinstance(response.get("summary"), str):
        return fallback("invalid_response")
    if response.get("source") != identity(case):
        return fallback("source_mismatch")
    consumed = response.get("input_token_count")
    if type(consumed) is not int or consumed != len(input_ids):
        return fallback("input_token_count_mismatch")
    summary = response["summary"]
    if not summary.strip() or len(summary.encode("utf-8")) > MAX_OUTPUT_BYTES:
        return fallback("output_limit")
    candidate = packet(case, summary)
    if review is None or review(case, candidate) is not True:
        return fallback("independent_review_not_passed", candidate)
    return {"status": "accepted", "reason": None, "candidate": candidate, "effective": candidate}


def serialize(context):
    return json.dumps(context, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def retention(case, context, facts):
    outputs = [context["text"], *context["protected_source_lines"]]
    missing = [f["literal"] for f in facts if not any(f["literal"] in x for x in outputs)]
    critical_missing = [f["literal"] for f in facts if f["critical"] and f["literal"] in missing]
    return {
        "retained_facts": len(facts) - len(missing),
        "annotated_facts": len(facts),
        "retained_critical_facts": sum(f["critical"] for f in facts) - len(critical_missing),
        "annotated_critical_facts": sum(f["critical"] for f in facts),
        "missing_literals": missing,
        "missing_critical_literals": critical_missing,
        "source_integrity": context["source"] == identity(case),
    }


def measure(case, make_packet, count_tokens, facts):
    tracemalloc.start()
    started = time.perf_counter()
    try:
        context = make_packet()
        wire = serialize(context)
        result = {
            "characters": len(wire),
            "utf8_bytes": len(wire.encode("utf-8")),
            "estimated_consumer_tokens": count_tokens(wire) if count_tokens else None,
            **retention(case, context, facts),
        }
        result["wall_ms"] = round((time.perf_counter() - started) * 1000, 4)
        result["peak_python_bytes"] = tracemalloc.get_traced_memory()[1]
        return result
    finally:
        tracemalloc.stop()


def load_tokenizer(path):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != GPT2_SHA256:
        raise ValueError("Tokenizer asset SHA-256 mismatch")
    from tokenizers import Tokenizer

    tokenizer = Tokenizer.from_str(raw.decode("utf-8"))
    tokenizer.no_truncation()
    tokenizer.no_padding()
    return (
        lambda text: tokenizer.encode(text, add_special_tokens=False).ids,
        {"name": "GPT-2 BPE", "kind": "consumer-token estimate",
         "asset_sha256": GPT2_SHA256, "engine": f"tokenizers {version('tokenizers')}"},
    )


def comparison(cases, gold, *, encode_input=None, tokenizer=None, backend=None, review=None, timeout_seconds=30):
    count_tokens = (lambda text: len(encode_input(text))) if encode_input else None
    rows = []
    for case in cases:
        before = identity(case)
        facts = gold[case["id"]]
        a = measure(case, lambda: packet(case, source_text(case)), count_tokens, facts)
        _, b_route = extractive_packet(case)
        b = measure(case, lambda: extractive_packet(case)[0], count_tokens, facts)
        started = time.perf_counter()
        c = evaluate_candidate(case, backend, review, encode_input=encode_input, timeout_seconds=timeout_seconds)
        c_elapsed = round((time.perf_counter() - started) * 1000, 4) if backend else None
        effective = c["effective"]
        c_metrics = measure(case, lambda: effective, count_tokens, facts) if effective is not None else None
        if identity(case) != before or not b["source_integrity"] or not a["source_integrity"]:
            raise ValueError("Source identity changed")
        rows.append({"source": before, "arm_a": a, "arm_b": b, "arm_b_route": b_route,
                     "arm_c": c, "arm_c_metrics": c_metrics, "arm_c_wall_ms": c_elapsed})

    def median_reduction(baseline, candidate, key):
        ratios = [
            1 - row[candidate][key] / row[baseline][key] for row in rows
            if row[candidate] is not None and row[baseline][key] and row[candidate][key] is not None
        ]
        return round(100 * statistics.median(ratios), 2) if ratios else None

    return {
        "schema": "whs-ncm-pilot-metrics-v2",
        "scope": "independently authored synthetic fixtures",
        "arm_b_mode": "unassisted",
        "cases": rows,
        "tokenizer": tokenizer or {"kind": "unavailable", "name": None},
        "median_b_vs_a_byte_reduction_pct": median_reduction("arm_a", "arm_b", "utf8_bytes"),
        "median_b_vs_a_token_reduction_pct": median_reduction("arm_a", "arm_b", "estimated_consumer_tokens"),
        "median_c_vs_b_token_reduction_pct": median_reduction(
            "arm_b", "arm_c_metrics", "estimated_consumer_tokens"
        ),
        "arm_c_fallback_rate": (
            sum(row["arm_c"]["status"] == "fallback" for row in rows) / len(rows) if rows and backend else None
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gpt2-tokenizer", type=Path, help="Use the pinned local GPT-2 tokenizer for estimates")
    args = parser.parse_args()
    encode_input, tokenizer = load_tokenizer(args.gpt2_tokenizer) if args.gpt2_tokenizer else (None, None)
    cases = load_cases()
    print(json.dumps(comparison(cases, load_gold(cases), encode_input=encode_input, tokenizer=tokenizer), indent=2))


if __name__ == "__main__":
    main()
