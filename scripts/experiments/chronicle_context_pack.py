"""Read-only generic-Markdown Chronicle context packs (WHS issue #8)."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

from tools.prepare_generic_markdown_chronicle import (
    ChronicleEvent, SECTION_HEADING_RE, escape_nested_event_bullets, first_date,
    render_staged_markdown, sanitize_title, source_label,
)
from tools.run_topic_report import compute_individual_report_event_id, compute_source_event_id
from wordpipe.chronicle.index import extract_events_from_tagged, rendered_navigation
from wordpipe.chronicle.ingest import clean_mojibake, format_event, split_into_events
from wordpipe.chronicle.merge import compute_body_hash, extract_events

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
REFERENCE = {"earlier", "above", "previous", "same", "described", "refers", "see", "aforementioned", "پیشین", "قبلی", "همان"}
CONSTRAINT = QUALIFIERS | {
    "qualification", "condition", "restriction", "correction", "disputed", "contradicts",
    "only", "must", "never", "unless", "prohibited", "required", "نه", "فقط", "نباید", "ممنوع",
}
COMMON_SUBJECTS = STOP | REFERENCE | CONSTRAINT | {
    "it", "this", "that", "with", "from", "at", "on", "before", "after", "was", "as",
    "trial", "run", "test", "notes", "record", "status", "review", "use", "approved",
    "decision", "protocol", "report", "all", "no", "not", "section",
}
IDENTIFIER = re.compile(r"[a-z][a-z0-9]*-[0-9][a-z0-9-]*", re.ASCII)
IMPLICIT_HEADINGS = QUALIFIERS | {"addendum", "appendix", "notice", "clarification"}
NUMBER = re.compile(r"\d+(?:[.,]\d+)?")
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


def _canonical_section_keys(name, source, sections):
    """Replay the existing adapter and ingest body transformations in memory."""
    fallback = first_date(source)
    label = source_label(name) or Path(name).stem
    prefix = source_label(name)
    staged = []
    for index, (title, _, body) in enumerate(sections, 1):
        if body:
            date = first_date(f"{title}\n{body}", fallback)
            staged_title = f"{prefix} - {sanitize_title(title)}" if prefix else sanitize_title(title)
            staged.append((index, ChronicleEvent(date, staged_title[:180], body)))
    markdown = render_staged_markdown(label, [event for _, event in staged])
    ingested, rejected = split_into_events(clean_mojibake(markdown))
    canonical = extract_events("\n".join(format_event(event) for event in ingested))
    require(not rejected and len(canonical) == len(ingested) == len(staged),
            "source replay does not map one-to-one to normalized events")
    keys = {}
    for (index, original), event in zip(staged, canonical, strict=True):
        body_hash = compute_body_hash(event["body"])
        expected = clean_mojibake(escape_nested_event_bullets(original.body))
        require(event["date"] == original.date and body_hash == compute_body_hash(expected),
                "canonical replay dropped or changed source section content")
        keys[index] = (event["date"], body_hash)
    return keys


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
    """Verify the receipt and bind every delivered source section to its canonical body."""
    return _load_run(run_dir, source_root, receipt, verify_body=True)


def _load_run(run_dir, source_root, receipt, *, verify_body):
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
    canonical_keys = {
        name: _canonical_section_keys(name, text, sections[name]) for name, text in sources.items()
    } if verify_body else {}
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
        if verify_body:
            require(canonical_keys[name].get(ordinal) == (record["date"], record["body_sha256"]),
                    "source-to-survivor body mismatch")
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
        "outside": [
            text[:next((m.start() for m in SECTION_HEADING_RE.finditer(text) if m["marks"] == "##"), len(text))]
            for text in sources.values()
        ] + [
            f"{title}\n{body}" for name, items in sections.items()
            for ordinal, (title, _, body) in enumerate(items, 1) if (name, ordinal) not in seen_locations
        ],
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


def _subjects(words):
    return {word for word in words - COMMON_SUBJECTS
            if len(word) >= 3 and all(c.isalpha() for c in word)}


def _qualifications(run, reasons, wanted):
    """Scan each other unit once. Keep distinct entities separate and abstain on weak links."""
    seeds = [run["units"][index] for index, reason in reasons.items() if reason == "exact_term_match"]
    seed_files = {loc["file"] for unit in seeds for loc in unit["sources"]}
    seed_text = "\n".join(unit["text"] for unit in seeds)
    seed_words = terms(seed_text)
    seed_ids = {word for word in seed_words | wanted if IDENTIFIER.fullmatch(word)}
    title_words = _subjects(wanted | set().union(*(terms(u["text"].splitlines()[0]) for u in seeds)))
    seed_subjects = _subjects(seed_words)
    seed_numbers = set(NUMBER.findall(seed_text))
    for text in run["outside"]:
        words = terms(text)
        shared = _subjects(words) & title_words
        if words & wanted or (shared and words & (REFERENCE | CONSTRAINT)):
            return "relevant_material_outside_units"

    owners = {
        (loc["file"], loc["section"]): {word for word in terms(unit["text"]) if IDENTIFIER.fullmatch(word)}
        for unit in run["units"] for loc in unit["sources"]
    }
    additions = {}
    for index, unit in enumerate(run["units"]):
        if index in reasons:
            continue
        words = terms(unit["text"])
        other_ids = {word for word in words if IDENTIFIER.fullmatch(word)}
        if other_ids and not other_ids & seed_ids:
            continue
        shared_titles = _subjects(words) & title_words
        shared_body = _subjects(words) & seed_subjects
        refers = bool(words & REFERENCE)
        qualifies = bool(words & CONSTRAINT)
        numbers = set(NUMBER.findall(unit["text"])) & seed_numbers
        if other_ids & seed_ids or (
            (shared_titles or len(shared_body) >= 2)
            and ((refers and qualifies) or (numbers and qualifies))
        ):
            additions[index] = "related_qualification"
        elif (shared_titles and (qualifies or refers)) or (
            refers and qualifies and terms(unit["text"].splitlines()[0]) & IMPLICIT_HEADINGS
            and any(loc["file"] in seed_files and not (
                owners.get((loc["file"], loc["section"] - 1), set()) - seed_ids
            ) for loc in unit["sources"])
        ):
            # Preserve an implicit or ambiguous reference without declaring it linked.
            return "ambiguous_qualification"
    reasons.update(additions)
    return None


def export_b1(run, query, max_bytes):
    """Replay the historical B1 selection rules for comparison only."""
    return _export(run, query, max_bytes, close_qualifications=False)


def export(run, query, max_bytes):
    """B2 selects complete units with bounded qualification closure or returns verified raw."""
    return _export(run, query, max_bytes, close_qualifications=True)


def _export(run, query, max_bytes, *, close_qualifications):
    if type(max_bytes) is not int or not 1 <= max_bytes <= MAX_INPUT_BYTES:
        raise ValueError("max_bytes must be between 1 and 32 MiB")
    if not query.strip() or len(query.encode("utf-8")) > 2048:
        if close_qualifications:
            return packet(run, query, "refused", "invalid_query")
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
            other_ids = {word for word in terms(unit["text"]) if IDENTIFIER.fullmatch(word)}
            compatible = not close_qualifications or not wanted_ids or not other_ids or bool(other_ids & wanted_ids)
            if compatible and index not in reasons and terms(unit["text"].splitlines()[0]) & QUALIFIERS and any(
                (s["file"], s["section"]) in adjoining for s in unit["sources"]
            ):
                reasons[index] = "adjacent_qualification"
    def size(value):
        return len(serialize(value).encode("utf-8"))
    reason = "rejected_ingest" if run["rejected"] else "insufficient_exact_evidence"
    closure_reason = _qualifications(run, reasons, wanted) if close_qualifications and reasons else None
    if closure_reason:
        reason = closure_reason
    if not closure_reason and reasons and wanted <= set().union(*(matches[i] for i in reasons)):
        result = packet(run, query, "structural", "matching_structural_units", units=[
            {**run["units"][index], "selection": reasons[index]} for index in sorted(reasons)
        ])
        if size(result) <= max_bytes and size(result) < size(raw_packet(run, query)):
            return result
        reason = "structural_packet_not_compact"
    result = raw_packet(run, query, reason)
    if size(result) > max_bytes:
        return packet(run, query, "refused", "verified_raw_exceeds_budget")
    if close_qualifications:
        source_terms = set().union(*(terms(source["text"]) for source in run["sources"]))
        query_evidence = wanted - COMMON_SUBJECTS or wanted
        if not query_evidence & source_terms or not wanted_ids <= source_terms:
            return packet(run, query, "refused", "no_verified_query_evidence")
    return result


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
