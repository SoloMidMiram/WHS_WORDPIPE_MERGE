"""Run the public WHS #8 fixture suite against actual synthetic Chronicle outputs."""
import argparse
from collections import Counter
import json
import os
import re
from pathlib import Path
import statistics
import subprocess
import sys
import time
import tracemalloc

from scripts.experiments import chronicle_context_pack as b1
from scripts.experiments import ncm_flowers_pilot as b0

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def synthetic_run(fixture, work):
    work.mkdir()
    source = work / "source"
    source.mkdir()
    for name, text in fixture["sources"].items():
        if Path(name).name != name or not name.endswith(".md"):
            raise ValueError("fixture must provide Markdown basenames")
        (source / name).write_bytes(text.encode("utf-8"))
    source_pins = {p.name: b1.digest(p.read_bytes()) for p in sorted(source.glob("*.md"))}
    manifest = work / "manifest.json"
    write_json(manifest, {
        "schema_version": 1, "topic": "synthetic_context_pack",
        "input_dir": str(source),
        "adapter": {"id": "prepare_generic_markdown_chronicle"},
        "themes_config": "pipeline/themes.json", "index_config": "pipeline/index_config.json",
        "output": {"base_dir": str(work / "runs"), "run_id_format": "timestamp"},
        "quality_gates": {
            "min_extraction_coverage_percent": 0, "min_theme_tag_percent": 0, "max_error_count": 0,
        },
    })
    proc = subprocess.run([sys.executable, "tools/run_topic_report.py", "--manifest", str(manifest),
                           "--run-id", "20261119_000001", "--allow-review"],
                          cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT)}, capture_output=True, timeout=120)
    (work / "runner.log").write_bytes(proc.stdout + proc.stderr)
    if proc.returncode != 0:
        raise RuntimeError(f"synthetic Chronicle exited {proc.returncode}; see {work / 'runner.log'}")
    run = work / "runs" / "20261119_000001"
    files = b1.REQUIRED | {
        file.relative_to(run).as_posix() for file in (run / "pipeline/appendix").glob("chronicle_tagged_anchored*.md")
    }
    pins = {name: b1.digest((run / name).read_bytes()) for name in sorted(files)}
    receipt = {"schema": "whs-context-receipt-v1", "artifacts": pins, "sources": source_pins}
    write_json(work / "receipt.json", receipt)
    return run, source, receipt


def fault_run(fault, run, receipt, destination):
    if not fault or fault == "small_budget":
        return run, receipt
    # Copy the synthetic artifacts. The original run and its receipt remain immutable.
    pins = dict(receipt["artifacts"])
    for name in pins:
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((run / name).read_bytes())
    if fault in {"stale_anchor", "missing_anchor"}:
        path = destination / b1.INDEX
        text = path.read_text(encoding="utf-8")
        changed = re.sub(r"#event-[0-9-]+-[a-f0-9]{64}", "#missing", text, count=1)
        if text == changed:
            raise ValueError("missing synthetic index anchor for fault injection")
        path.write_text(changed, encoding="utf-8")
        if fault == "missing_anchor":
            pins[b1.INDEX] = b1.digest(path.read_bytes())
    elif fault == "rejected_ingest":
        path = destination / b1.CHAIN
        chain = read_json(path)
        chain["ingest_files"][0]["rejected"] = 1
        write_json(path, chain)
        pins[b1.CHAIN] = b1.digest(path.read_bytes())
    else:
        raise ValueError(f"unsupported fixture fault: {fault}")
    return destination, {**receipt, "artifacts": pins}


def baseline_packet(run, query):
    sources = []
    raw_count = 0
    for source in run["sources"]:
        case = {"title": source["file"], "lines": source["text"].splitlines(), "query": query,
                "id": source["file"], "source_reference": source["file"]}
        extracted, route = b0.extractive_packet(case)
        raw = route == "no_keyword_match_raw"
        raw_count += raw
        sources.append({**source, "text": source["text"] if raw else extracted["text"]})
    if raw_count == len(sources):
        return b1.raw_packet(run, query, "baseline_no_keyword_match")
    return b1.packet(run, query, "baseline", "frozen_top_two", sources=sources)


def measure(make_packet, reference, count, run):
    tracemalloc.start()
    start = time.perf_counter_ns()
    try:
        packet = make_packet()
        wire = b1.serialize(packet)
        elapsed = (time.perf_counter_ns() - start) / 1e6
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    evidence = [*packet["sources"], *packet["units"]]
    texts = [item["text"] for item in evidence]
    raw = {item["file"]: item for item in run["sources"]}
    known = {unit["anchor"]: unit for unit in run["units"]}
    identity_ok = packet["run"] == run["identity"] and all(
        item["sha256"] == raw[item["file"]]["sha256"] for item in packet["sources"]
    ) and all(
        {k: v for k, v in unit.items() if k != "selection"} == known.get(unit["anchor"])
        for unit in packet["units"]
    )
    unsupported = sum(
        any(line not in raw[item["file"]]["text"] for line in item["text"].splitlines())
        for item in packet["sources"]
    ) + sum(unit["text"] != known[unit["anchor"]]["text"] for unit in packet["units"])
    misses = {
        key: [fact for fact in reference[key] if not any(fact in text for text in texts)]
        for key in ("critical", "additional")
    }
    metadata = {**packet, **{key: [{**item, "text": ""} for item in packet[key]]
                             for key in ("sources", "units")}}
    delivered = packet["route"] != "refused"
    return {
        "route": packet["route"], "reason": packet["reason"], "delivered": delivered,
        "misses": misses, "identity_ok": identity_ok, "unsupported_units": unsupported,
        "tokens": count(wire) if count and delivered else None,
        "metadata_tokens": count(b1.serialize(metadata)) if count and delivered else None,
        "raw_fallback_tokens": count(wire) if count and packet["route"] == "raw" and packet["reason"] != "complete_source" else None,
        "bytes": len(wire.encode("utf-8")) if delivered else 0,
        "packet_sha256": b1.digest(wire.encode("utf-8")),
        "elapsed_ms": round(elapsed, 4), "peak_python_bytes": peak,
    }


def summarize(rows, count):
    summary = {}
    for arm in ("A", "B0", "B1"):
        evaluated = [r[arm] for r in rows if arm in r]
        eligible = [r for r in rows if arm in r]
        scores = [m for m in evaluated if m["delivered"]]
        critical = sum(len(r["reference"]["critical"]) for r in eligible)
        overall = critical + sum(len(r["reference"]["additional"]) for r in eligible)
        missed = sum(len(m["misses"]["critical"]) for m in evaluated)
        missed_all = missed + sum(len(m["misses"]["additional"]) for m in evaluated)
        totals = {}
        if count:
            for key in ("tokens", "metadata_tokens", "raw_fallback_tokens"):
                totals[key] = sum(m[key] or 0 for m in scores)
            # Refusal earns zero savings; this preserves all cases in the median.
            ratios = [1 - r[arm]["tokens"] / r["A"]["tokens"]
                      if r.get(arm, {}).get("tokens") and r.get("A", {}).get("tokens")
                      else 0 for r in rows]
            totals["median_token_reduction_pct"] = round(100 * statistics.median(ratios), 2)
        summary[arm] = {
            "critical": [critical - missed, critical], "overall": [overall - missed_all, overall],
            "provenance_ok": [sum(m["identity_ok"] for m in scores), len(scores)],
            "unsupported_units": sum(m["unsupported_units"] for m in scores),
            "routes": dict(Counter(m["route"] for m in evaluated)),
            "provenance_refusals": len(rows) - len(evaluated),
            "median_wall_ms": statistics.median(m["elapsed_ms"] for m in evaluated),
            "max_peak_python_bytes": max(m["peak_python_bytes"] for m in evaluated),
            **totals,
        }
    return summary


def benchmark(fixture, gold, work, encode=None, tokenizer=None):
    case_ids = [case["id"] for case in fixture["cases"]]
    if fixture["schema"] != "whs-context-benchmark-v1" or fixture["partition"] != gold["partition"] \
            or len(case_ids) != 12 or len(set(case_ids)) != 12 or set(case_ids) != gold["references"].keys():
        raise ValueError("fixture partition or gold roster mismatch")
    run, source, receipt = synthetic_run(fixture, work)
    count = (lambda text: len(encode(text))) if encode else None
    checked = b1.load_run(run, source, receipt)
    rows = []
    for case in fixture["cases"]:
        query, reference = case["query"], gold["references"][case["id"]]
        row = {"case": case["id"], "reference": reference}
        fixture_run, pins = fault_run(case.get("fault"), run, receipt, work / "faults" / case["id"])
        try:
            current = checked if fixture_run == run else b1.load_run(fixture_run, source, pins)
        except b1.ProvenanceError as exc:
            row["refusal"] = str(exc)
        else:
            budget = 128 if case.get("fault") == "small_budget" else 65_536
            methods = {
                "A": lambda: b1.raw_packet(current, query),
                "B0": lambda: baseline_packet(current, query),
                "B1": lambda: b1.export(current, query, budget),
            }
            if not row.get("refusal") and not all(
                fact in "\n".join(item["text"] for item in current["sources"])
                for key in ("critical", "additional") for fact in reference[key]
            ):
                raise ValueError(f"gold literal missing for {case['id']}")
            for arm, method in methods.items():
                row[arm] = measure(method, reference, count, current)
                if b1.digest(b1.serialize(method()).encode("utf-8")) != row[arm]["packet_sha256"]:
                    raise ValueError("non-deterministic packet replay")
        expected = reference.get("expected")
        if expected and expected != row.get("B1", {}).get("route", "refused"):
            row["unexpected_route"] = expected
        rows.append(row)
    assert all(b1.digest((source / n).read_bytes()) == value for n, value in receipt["sources"].items())
    assert all(b1.digest((run / n).read_bytes()) == value for n, value in receipt["artifacts"].items())
    return {"partition": fixture["partition"], "case_count": len(rows), "tokenizer": tokenizer,
            "source_reread_bytes_once": checked["source_reread_bytes"], "consumer_source_reread_tokens": 0,
            "deterministic_replay": True, "input_hashes_unchanged": True,
            "summary": summarize(rows, count), "cases": rows}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--partition", choices=("tuning", "holdout"), required=True)
    cli.add_argument("--work", type=Path, required=True)
    cli.add_argument("--gpt2-tokenizer", type=Path)
    args = cli.parse_args()
    name = f"whs_context_{args.partition}"
    suite = read_json(FIXTURES / f"{name}.json")
    gold = read_json(FIXTURES / f"{name}_gold.json")
    encode, tokenizer = b0.load_tokenizer(args.gpt2_tokenizer) if args.gpt2_tokenizer else (None, None)
    result = benchmark(suite, gold, args.work.resolve(), encode, tokenizer)
    write_json(args.work / "case-results.json", result)
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
