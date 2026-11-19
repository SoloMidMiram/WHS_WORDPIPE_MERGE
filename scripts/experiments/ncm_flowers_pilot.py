"""Compare disclosure-safe synthetic Flowers context packets."""
import argparse
import hashlib
import json
import re
import statistics
import time
import tracemalloc
from importlib.metadata import version
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "ncm_flowers_synthetic.json"


def source_text(case):
    return "## " + case["title"] + "\n\n" + "\n".join(case["lines"])


def source_digest(case):
    return hashlib.sha256(source_text(case).encode("utf-8")).hexdigest()


def load_cases():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    if data["scope"] != "synthetic" or data["schema"] != "whs-ncm-pilot-v1":
        raise ValueError("Only the reviewed synthetic suite is supported")
    cases = data["cases"]
    if len({case["source_reference"] for case in cases}) != len(cases):
        raise ValueError("Duplicate source reference")
    for case in cases:
        if any(not fact["literal"] or fact["literal"] not in source_text(case) for fact in case["facts"]):
            raise ValueError(f"Annotation missing from source: {case['id']}")
    return cases


GPT2_SHA256 = "8414cab924d8b9b33013f0d221c5862f365ee9be39c5c2bfae8a5a9e970478a6"
MAX_INPUT_BYTES = 16_384
MAX_OUTPUT_BYTES = 4_096


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


def source_lines_for_critical_facts(case, retained):
    return [
        line for line in case["lines"]
        if line not in retained
        and any(f["critical"] and f["literal"] in line for f in case["facts"])
    ]


def terms(text):
    return set(re.findall(r"\w+", text.casefold()))


def extractive_packet(case):
    query = terms(case["query"])
    hits = [(len(terms(line) & query), i) for i, line in enumerate(case["lines"])]
    ranked = sorted((score, i) for score, i in hits if score)
    if not ranked:
        return packet(case, source_text(case)), "no_keyword_match_raw"
    top = sorted(ranked, key=lambda hit: (-hit[0], hit[1]))[:2]
    lines = [case["lines"][i] for _, i in sorted(top, key=lambda hit: hit[1])]
    return packet(case, "\n".join(lines), source_lines_for_critical_facts(case, lines)), "extracted"


def evaluate_candidate(case, backend=None, review=None, *, timeout_seconds=30):
    """Exercise the backend contract. The backend owns enforcing its deadline."""
    if backend is None:
        return {"status": "not_run", "reason": "gate_a_blocked", "candidate": None, "effective": None}
    if not 0 < timeout_seconds <= 300:
        raise ValueError("Timeout must be positive and at most 300 seconds")

    def fallback(reason, candidate=None):
        effective, route = extractive_packet(case)
        return {"status": "fallback", "reason": reason, "route": route,
                "candidate": candidate, "effective": effective}

    text = source_text(case)
    if not text.strip() or len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        return fallback("input_limit")
    request = {
        "text": text,
        "source": identity(case),
        "load_policy": {"weights_only": True, "map_location": "cpu"},
        "max_input_tokens": 512,
        "max_output_slots": 48,
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
    summary = response["summary"]
    if not summary.strip() or len(summary.encode("utf-8")) > MAX_OUTPUT_BYTES:
        return fallback("output_limit")
    candidate = packet(case, summary, source_lines_for_critical_facts(case, ()))
    if review is None or review(case, candidate) is not True:
        return fallback("independent_review_not_passed", candidate)
    return {"status": "accepted", "reason": None, "candidate": candidate, "effective": candidate}


def serialize(context):
    return json.dumps(context, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def retention(case, context):
    outputs = [context["text"], *context["protected_source_lines"]]
    missing = [f["literal"] for f in case["facts"] if not any(f["literal"] in x for x in outputs)]
    critical_missing = [f["literal"] for f in case["facts"] if f["critical"] and f["literal"] in missing]
    return {
        "retained_facts": len(case["facts"]) - len(missing),
        "annotated_facts": len(case["facts"]),
        "retained_critical_facts": sum(f["critical"] for f in case["facts"]) - len(critical_missing),
        "annotated_critical_facts": sum(f["critical"] for f in case["facts"]),
        "missing_literals": missing,
        "missing_critical_literals": critical_missing,
        "source_integrity": context["source"] == identity(case),
    }


def measure(case, make_packet, count_tokens):
    tracemalloc.start()
    started = time.perf_counter()
    try:
        context = make_packet()
        wire = serialize(context)
        result = {
            "characters": len(wire),
            "utf8_bytes": len(wire.encode("utf-8")),
            "estimated_consumer_tokens": count_tokens(wire) if count_tokens else None,
            **retention(case, context),
        }
        result["wall_ms"] = round((time.perf_counter() - started) * 1000, 4)
        result["peak_python_bytes"] = tracemalloc.get_traced_memory()[1]
        return result
    finally:
        tracemalloc.stop()


def load_estimator(path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != GPT2_SHA256:
        raise ValueError("Tokenizer asset SHA-256 mismatch")
    from tokenizers import Tokenizer

    tokenizer = Tokenizer.from_file(str(path))
    return (
        lambda text: len(tokenizer.encode(text, add_special_tokens=False).ids),
        {"name": "GPT-2 BPE", "kind": "consumer-token estimate",
         "asset_sha256": GPT2_SHA256, "engine": f"tokenizers {version('tokenizers')}"},
    )


def comparison(cases, count_tokens=None, tokenizer=None):
    rows = []
    for case in cases:
        before = identity(case)
        a = measure(case, lambda: packet(case, source_text(case)), count_tokens)
        b = measure(case, lambda: extractive_packet(case)[0], count_tokens)
        if identity(case) != before or not a["source_integrity"] or not b["source_integrity"]:
            raise ValueError("Source identity changed")
        rows.append({"source": before, "arm_a": a, "arm_b": b,
                     "arm_b_route": extractive_packet(case)[1], "arm_c": evaluate_candidate(case)})

    def reductions(key):
        return [1 - row["arm_b"][key] / row["arm_a"][key] for row in rows if row["arm_a"][key]]

    return {
        "schema": "whs-ncm-pilot-metrics-v1",
        "scope": "independently authored synthetic fixtures",
        "cases": rows,
        "tokenizer": tokenizer or {"kind": "unavailable", "name": None},
        "median_b_vs_a_byte_reduction_pct": round(100 * statistics.median(reductions("utf8_bytes")), 2),
        "median_b_vs_a_token_reduction_pct": (
            round(100 * statistics.median(reductions("estimated_consumer_tokens")), 2)
            if count_tokens else None
        ),
        "ncm_median_c_vs_b_token_reduction_pct": None,
        "ncm_cold_start_ms": None,
        "ncm_generation_ms": None,
        "ncm_peak_rss_bytes": None,
        "ncm_fallback_rate": None,
        "real_flowers_status": "blocked",
        "synthetic_ncm_smoke_status": "not_run",
        "adoption_decision": "blocked_no_runtime_evidence",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gpt2-tokenizer", type=Path, help="Use the pinned local GPT-2 tokenizer for estimates")
    args = parser.parse_args()
    count_tokens, tokenizer = load_estimator(args.gpt2_tokenizer) if args.gpt2_tokenizer else (None, None)
    print(json.dumps(comparison(load_cases(), count_tokens, tokenizer), indent=2))


if __name__ == "__main__":
    main()
