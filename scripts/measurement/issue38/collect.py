"""Summarize the registered smoke without opening source text or raw logs."""
import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import median, quantiles

BASE = "1295ad15cc085732391a6d1dfe8069de32752ad1"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def distribution(values):
    m = median(values)
    q1, _, q3 = quantiles(values, method="inclusive") if len(values) > 1 else (m, m, m)
    return dict(n=len(values), minimum=min(values), maximum=max(values),
                median=m, iqr=q3-q1, mad=median(abs(v-m) for v in values))


def timing(value, *, zero=False):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (not zero and value == 0):
        raise ValueError("invalid elapsed measurement")
    return value


def attempts(path, expected):
    seen = set()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        row = json.loads(line)
        if not isinstance(row, dict) or not {"mode", "id", "exit", "elapsed", "attempt", "utc"} <= row.keys():
            raise ValueError("malformed attempt")
        if type(row["mode"]) is not str or type(row["id"]) is not str:
            raise ValueError("invalid run identity")
        key = row["mode"], row["id"]
        if key in seen or key not in expected:
            raise ValueError(f"duplicate or invalid attempt: {key}")
        if type(row["exit"]) is not int or type(row["attempt"]) is not int or row["attempt"] < 1 or type(row["utc"]) is not str:
            raise ValueError(f"invalid terminal measurement: {key}")
        if datetime.fromisoformat(row["utc"]).utcoffset() is None:
            raise ValueError(f"timestamp missing offset: {key}")
        timing(row["elapsed"])
        seen.add(key)
        yield row
    if expected != seen:
        raise ValueError(f"missing registered terminal measurements: {sorted(expected - seen)}")


def summarize(pilot, out):
    pin = load(pilot / "source-pin.json")
    source = next((pilot / "sources").glob("*.md"))
    if not digest(source) == digest(Path(pin["source"])) == pin["sha256"]:
        raise ValueError("snapshot or original source digest mismatch")
    receipt = load(pilot / "pilot-receipt.json")
    def normalize(obj):
        if isinstance(obj, dict):
            return {k: normalize(v) for k, v in obj.items() if k != "run_id"}
        if isinstance(obj, list):
            return list(map(normalize, obj))
        return obj
    expected = {(mode, f"measure38-{i}") for mode in ("legacy", "structural") for i in range(1, 4)}
    rows = list(attempts(out / "attempts.jsonl", expected))
    on_disk = {(mode, run.name) for mode in ("legacy", "structural")
               for run in (pilot / mode).glob("measure38-*") if run.is_dir()}
    if on_disk != {(row["mode"], row["id"]) for row in rows}:
        raise ValueError("registered run lacks a terminal measurement or run directory")
    groups = {}
    with (out / "run.jsonl").open("x", encoding="utf-8") as stream:
        for row in rows:
            mode = row["mode"]
            run = pilot / mode / row["id"]
            manifest = load(pilot / f"{mode}.json")
            identity = dict(schema_version=1, run_id=f"{mode}:{row['id']}", main=BASE,
                            fixture_sha256=pin["sha256"], parser_mode=manifest["adapter"]["markdown_mode"],
                            config_sha256=digest(pilot / f"{mode}.json"),
                            environment_sha256=digest(out / "environment.json"),
                            attempt=row["attempt"], cache="primed-uncontrolled")
            seq = 0
            def emit(event, **fields):
                nonlocal seq
                seq += 1
                record = dict(identity, seq=seq, utc=datetime.now(timezone.utc).isoformat(), event=event, **fields)
                stream.write(json.dumps(record, separators=(",", ":")) + "\n")
            emit("RUN_START", outcome=None, elapsed_seconds=0, observed_start_utc=row["utc"])
            stages = {}
            stage_success = True
            for stagefile in sorted((run / "exec-01").glob("*.json")):
                stage = load(stagefile)
                stage_success &= stage["outcome"] == "success"
                stages[stagefile.stem] = timing(stage["elapsed_seconds"], zero=True)
                emit("STAGE_END", stage=stagefile.stem, elapsed_seconds=stage["elapsed_seconds"],
                     outcome=stage["outcome"], source=str(stagefile))
            emit("USAGE", outcome=None, elapsed_seconds=None, cpu_seconds=None,
                 peak_tree_rss_bytes=None, model_tokens=0, model_calls=0)
            metrics = load(run / "run_metrics.json") if (run / "run_metrics.json").exists() else {}
            integrity = bool(metrics) and all(
                (run / f"{name}.json").exists() and
                normalize(load(run / f"{name}.json")) == normalize(load(pilot / mode / "replay" / f"{name}.json"))
                for name in ("event_lineage", "event_correlation"))
            success = row["exit"] == 0 and integrity and stage_success and set(stages) == {"prepare", "pipeline", "summarize"}
            if not success:
                emit("FAILURE", outcome="failure_or_incomplete", elapsed_seconds=row["elapsed"])
            emit("RUN_END", elapsed_seconds=row["elapsed"], outcome="success" if success else "failure",
                 exit_code=row["exit"], integrity=integrity)
            groups.setdefault(mode, []).append(dict(row, success=success, stages=stages,
                                                    input_bytes=source.stat().st_size,
                                                    output_bytes=sum(f.stat().st_size for f in run.rglob("*") if f.is_file()),
                                                    events=metrics.get("merged_event_count")))
    stats = {}
    for mode, batch in groups.items():
        good = [r for r in batch if r["success"]]
        stats[mode] = dict(attempts=len(batch), failure_rate=1-len(good)/len(batch), rows=batch,
                           wall_seconds=distribution([r["elapsed"] for r in good]) if good else None,
                           stages={k:distribution([r["stages"][k] for r in good]) for k in good[0]["stages"]} if good else {},
                           events_per_second=distribution([r["events"]/r["elapsed"] for r in good]) if good else None,
                           mib_per_second=distribution([r["input_bytes"]/1048576/r["elapsed"] for r in good]) if good else None)
    result = dict(groups=stats, historical_reference=receipt["runtime"], tails="insufficient",
                  cpu_seconds=None, peak_tree_rss_bytes=None, context_comparison="blocked",
                  matched_engineering_comparison="unmeasured")
    (out / "summary.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:{f:v[f] for f in ("attempts","failure_rate","wall_seconds")} for k,v in stats.items()}))


def replay_sanitized(folder):
    """Validate published summary inputs without requiring local raw logs."""
    identity = load(folder / "smoke-identity.json")
    registered = {(r["mode"], r["id"]): r["attempt"] for r in identity["registration"]}
    if len(registered) != len(identity["registration"]):
        raise ValueError("duplicate registration")
    batches = {}
    for row in attempts(folder / "smoke-attempts.jsonl", registered.keys()):
        if row["attempt"] != registered[row["mode"], row["id"]]:
            raise ValueError("attempt number differs from registration")
        if type(row.get("success")) is not bool or (row["success"] and row["exit"] != 0):
            raise ValueError("invalid integrity verdict")
        for elapsed in row["stages"].values():
            timing(elapsed, zero=True)
        if row["success"] and set(row["stages"]) != {"prepare", "pipeline", "summarize"}:
            raise ValueError("successful run lacks stage evidence")
        for field in ("input_bytes", "output_bytes", "events"):
            value = row[field]
            if value is None and field == "events" and not row["success"]:
                continue
            if type(value) is not int or value < 0:
                raise ValueError(f"invalid {field}")
        batches.setdefault(row["mode"], []).append(row)
    result = {}
    for mode, rows in batches.items():
        successful = [r for r in rows if r["success"]]
        metrics = {
            "wall_seconds": [r["elapsed"] for r in successful],
            "events_per_second": [r["events"]/r["elapsed"] for r in successful],
            "mib_per_second": [r["input_bytes"]/1048576/r["elapsed"] for r in successful],
        }
        for stage in ("prepare", "pipeline", "summarize"):
            metrics[f"{stage}_seconds"] = [r["stages"][stage] for r in successful]
        result[mode] = dict(attempts=len(rows), failure_rate=1-len(successful)/len(rows),
                            **{k: distribution(v) if v else None for k, v in metrics.items()})
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pilot", type=Path)
    parser.add_argument("out", nargs="?", type=Path)
    args = parser.parse_args()
    if args.out is None:
        print(json.dumps(replay_sanitized(args.pilot), indent=2, sort_keys=True))
    else:
        summarize(args.pilot, args.out)
