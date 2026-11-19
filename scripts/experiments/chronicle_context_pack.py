"""Read-only generic-Markdown Chronicle context packs (WHS issue #8)."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

from tools.prepare_generic_markdown_chronicle import SECTION_HEADING_RE, first_date
from tools.run_topic_report import compute_individual_report_event_id, compute_source_event_id
from wordpipe.chronicle.index import extract_events_from_tagged, rendered_navigation
from wordpipe.chronicle.merge import compute_body_hash

MANIFEST = "topic_run_manifest.json"
LINEAGE = "event_lineage.json"
CORRELATION = "event_correlation.json"
TAGGED = "pipeline/chronicle_tagged.md"
TAGS = "pipeline/chronicle_tagged.tagged.json"
INDEX = "pipeline/appendix/event_index.md"
CHAIN = "pipeline/run.json"
REQUIRED = {MANIFEST, LINEAGE, CORRELATION, TAGGED, TAGS, INDEX, CHAIN}
ANCHORED = re.compile(r"pipeline/appendix/chronicle_tagged_anchored(?:-\d+)?\.md")
TERM = re.compile(r"[^\W_]+(?:[-_/][^\W_]+)*")
STOP = {"a", "an", "and", "are", "for", "in", "is", "of", "the", "to", "what", "which"}
QUALIFIERS = {"conditions", "qualification", "exception", "limits", "correction", "counterclaim", "شرط", "استثنا"}
MAX_INPUT_BYTES = 32 * 1024 * 1024


class ProvenanceError(ValueError):
    """Pinned artifacts or their canonical identities could not be reconciled."""


def serialize(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(value).hexdigest()


def require(condition, reason):
    if not condition:
        raise ProvenanceError(reason)


def _read_pinned(root, pins, remaining):
    texts = {}
    for name, expected in sorted(pins.items()):
        path = root / name
        require(path.resolve().is_relative_to(root) and path.is_file(), f"invalid pinned path: {name}")
        with path.open("rb") as stream:
            raw = stream.read(remaining + 1)
        require(len(raw) <= remaining, "pinned input exceeds 32 MiB")
        require(digest(raw) == expected, f"pinned hash mismatch: {name}")
        remaining -= len(raw)
        texts[name] = raw.decode("utf-8")
    return texts, remaining


def _normalize_newlines(text):
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _sections(text):
    text = _normalize_newlines(text)
    matches = [m for m in SECTION_HEADING_RE.finditer(text) if m["marks"] == "##"]
    return [
        (match["title"].strip(), text[:match.start()].count("\n") + 1,
         text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)].strip())
        for index, match in enumerate(matches)
    ]


def _navigation(artifacts, events):
    target = next((name for name in artifacts if ANCHORED.fullmatch(name)), TAGGED)
    anchors, _ = rendered_navigation(artifacts[target])
    _, links = rendered_navigation(artifacts[INDEX])
    counts = Counter(anchors)
    prefix = ("../chronicle_tagged.md" if target == TAGGED else Path(target).name) + "#"
    links = Counter(url for url, _ in links)
    for event in events:
        anchor = event["anchor"]
        require(event["has_anchor"] and counts[anchor] == 1 and links[prefix + anchor] == 1,
                "missing, duplicate or stale event navigation")
    return target


def load_run(run_dir, source_root, receipt):
    """Verify one trusted receipt and bind every survivor to its exact source locators."""
    require(receipt.get("schema") == "whs-context-receipt-v1", "unsupported receipt")
    artifact_pins, source_pins = receipt["artifacts"], receipt["sources"]
    extra = set(artifact_pins) - REQUIRED
    require(REQUIRED <= artifact_pins.keys() and len(extra) <= 1
            and all(ANCHORED.fullmatch(name) for name in extra), "unexpected or missing run artifacts")
    require(all(Path(name).name == name and re.fullmatch(r"[^/\\:]+\.md", name) for name in source_pins),
            "expected generic Markdown source basenames")
    root = source_root.resolve()
    require(set(source_pins) == {path.name for path in root.glob("*.md")}, "source set differs from receipt")
    artifacts, source_allowance = _read_pinned(run_dir.resolve(), artifact_pins, MAX_INPUT_BYTES)
    artifacts = {name: _normalize_newlines(value) for name, value in artifacts.items()}
    sources, remaining = _read_pinned(root, source_pins, source_allowance)
    manifest, lineage, correlation, chain = (json.loads(artifacts[name]) for name in (MANIFEST, LINEAGE, CORRELATION, CHAIN))
    topic, run_id = manifest["topic"], manifest["run_id"]
    for doc, schema in ((lineage, "event-lineage-v1"), (correlation, "event-correlation-v1")):
        require(doc["$schema"] == schema and (doc["topic"], doc["run_id"]) == (topic, run_id),
                "run or sidecar identity mismatch")
    require(manifest["schema_version"] == 1
            and manifest["adapter"]["id"] == "prepare_generic_markdown_chronicle"
            and all(manifest["exit_codes"].get(stage) == 0
                    for stage in ("prepare", "pipeline", "provenance", "summarize"))
            and chain["status"] == "ok", "unsupported or incomplete run")
    sv = correlation["survivor_verification"]
    require(not correlation["ambiguous_matches"] and correlation["unmerged_source_event_count"] == 0
            and sv["missing_key_count"] == sv["unexpected_key_count"] == 0, "ambiguous or incomplete survivor map")
    events = extract_events_from_tagged(artifacts[TAGGED])
    tagged = [{"date": e["date"], "title": e["title"], "themes": e["themes"]} for e in events]
    require(json.loads(artifacts[TAGS]) == tagged, "tagged JSON diverges from tagged Markdown")
    target = _navigation(artifacts, events)
    sources_by_event = defaultdict(list)
    seen_ids = set()
    seen_locations = set()
    sections = {name: _sections(value) for name, value in sources.items()}
    fallbacks = {name: first_date(value) for name, value in sources.items()}
    for record in lineage["events"]:
        name, ordinal = record["source_file"], record["candidate_ordinal"]
        require(record["locator_kind"] == "markdown_section" and record["heading_level"] == 2
                and type(ordinal) is int and 1 <= ordinal <= len(sections.get(name, ())),
                "unknown source locator")
        title, line, body = sections[name][ordinal - 1]
        source_id, _ = compute_source_event_id(topic, record)
        report_id, _ = compute_individual_report_event_id(topic, record["date"], record["body_sha256"])
        require(body and record["original_heading_text"] == title and record["start_line"] == line
                and first_date(f"{title}\n{body}", fallbacks[name]) == record["date"]
                and record["source_event_id"] == source_id and record["report_event_id"] == report_id
                and source_id not in seen_ids and (name, ordinal) not in seen_locations,
                "stale or ambiguous source identity")
        seen_ids.add(source_id)
        seen_locations.add((name, ordinal))
        sources_by_event[report_id].append({
            "file": name, "sha256": source_pins[name], "start_line": line, "section": ordinal,
            "source_event_id": source_id,
        })
    by_id = {}
    for row in correlation["report_events"]:
        report_id = row["report_event_id"]
        linked = sources_by_event.get(report_id, ())
        require(report_id not in by_id and linked
                and Counter(row["source_event_ids"]) == Counter(item["source_event_id"] for item in linked),
                "correlation does not match lineage")
        by_id[report_id] = (row["date"], row["body_sha256"], linked)
    units = []
    ids = set()
    for event in events:
        date, body_hash = event["date"], compute_body_hash(event["body"])
        report_id, _ = compute_individual_report_event_id(topic, date, body_hash)
        require(report_id in by_id and by_id[report_id][:2] == (date, body_hash), "stale survivor identity")
        ids.add(report_id)
        locators = by_id[report_id][2]
        raw_sections = [sections[s["file"]][s["section"] - 1] for s in locators]
        # Multiple source locations can share a survivor. Keep all distinct exact source sections.
        texts = list(dict.fromkeys(f"## {title}\n\n{body}" for title, _, body in raw_sections))
        units.append({"anchor": event["anchor"], "date": date,
                      "sources": [{k: v for k, v in locator.items() if k != "source_event_id"}
                                  for locator in locators],
                      "text": "\n\n".join(texts)})
    require(len(units) == len(ids) == len(by_id) == correlation["report_event_count"]
            == sv["expected_key_count"] == sv["actual_key_count"]
            and ids == by_id.keys() == sources_by_event.keys()
            and len(seen_ids) == correlation["source_event_count"], "survivor count or key mismatch")
    return {
        "identity": {"topic": topic, "run_id": run_id,
                     "receipt_sha256": digest(serialize(receipt).encode("utf-8"))},
        "target": target, "units": units,
        "source_reread_bytes": source_allowance - remaining,
        "sources": [{"file": name, "sha256": source_pins[name], "text": value} for name, value in sources.items()],
        "rejected": sum(row.get("rejected") or 0 for row in chain["ingest_files"]),
    }


def terms(text):
    return set(TERM.findall(unicodedata.normalize("NFKC", text).casefold())) - STOP


def packet(run, query, route, reason, *, sources=(), units=()):
    return {"schema": "whs-context-pack-v1", "run": run["identity"], "query": query,
            "instruction": "Use original evidence. Preserve conditions, disagreements and uncertainty. Chronicle dates are not publication dates.",
            "route": route, "reason": reason, "navigation_target": run["target"],
            "sources": list(sources), "units": list(units)}


def raw_packet(run, query, reason="complete_source"):
    return packet(run, query, "raw", reason, sources=run["sources"])


def export(run, query, max_bytes):
    """Select complete matching events and adjoining named qualifications, or abstain."""
    if type(max_bytes) is not int or not 1 <= max_bytes <= MAX_INPUT_BYTES:
        raise ValueError("max_bytes must be between 1 and 32 MiB")
    if not query.strip() or len(query.encode("utf-8")) > 2048:
        raise ValueError("query must contain 1–2048 UTF-8 bytes")
    wanted = terms(query)
    matches = [terms(u["text"]) & wanted for u in run["units"]]
    wanted_ids = {token for token in wanted if any(c.isdigit() for c in token) and "-" in token}
    complete = set().union(*matches) == wanted and bool(wanted)
    reasons = {}
    if complete and not run["rejected"]:
        adjoining = set()
        for index, found in enumerate(matches):
            if found and (not wanted_ids or found & wanted_ids):
                reasons[index] = "exact_term_match"
                for locator in run["units"][index]["sources"]:
                    adjoining.update((locator["file"], locator["section"] + delta) for delta in (-1, 1))
        for index, unit in enumerate(run["units"]):
            if index not in reasons and terms(unit["text"].splitlines()[0]) & QUALIFIERS and any(
                (s["file"], s["section"]) in adjoining for s in unit["sources"]
            ):
                reasons[index] = "adjacent_qualification"
    def size(value):
        return len(serialize(value).encode("utf-8"))
    reason = "rejected_ingest" if run["rejected"] else "insufficient_exact_evidence"
    if reasons and wanted <= set().union(*(matches[i] for i in reasons)):
        result = packet(run, query, "structural", "matching_structural_units", units=[
            {**run["units"][index], "selection": reasons[index]} for index in sorted(reasons)
        ])
        if size(result) <= max_bytes and size(result) < size(raw_packet(run, query)):
            return result
        reason = "structural_packet_not_compact"
    result = raw_packet(run, query, reason)
    if size(result) <= max_bytes:
        return result
    return packet(run, query, "refused", "verified_raw_exceeds_budget")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--query", required=True)
    parser.add_argument("--max-bytes", required=True, type=int)
    args = parser.parse_args()
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        result = export(load_run(args.run_dir, args.source_root, receipt), args.query, args.max_bytes)
    except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
        print(f"context export refused: {exc}", file=sys.stderr)
        return 2
    if result["route"] == "refused":
        print(f"context export refused: {result['reason']}", file=sys.stderr)
        return 2
    sys.stdout.buffer.write(serialize(result).encode("utf-8") + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
