import json

import pytest

from scripts.experiments import chronicle_context_pack as pack
from tools.run_topic_report import compute_individual_report_event_id, compute_source_event_id
from wordpipe.chronicle.merge import compute_body_hash


@pytest.fixture
def example(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    run = tmp_path / "run"
    entries = [
        ("Pump AA-1", "12 bar maximum.\n\nDo not open the bypass."),
        ("Conditions", "Use only at 19 °C."),
        ("Pump AA-10", "This different component is retired."),
        ("Routine register", "Unrelated observations about packaging and inventory. " * 90),
    ]
    original = ("# Notes\n\n2025-04-01\n\n" + "".join(
        f"## {title}\n\n{body}\n\n" for title, body in entries
    )).replace("\n", "\r\n")
    source_file = source / "notes.md"
    source_file.write_bytes(original.encode("utf-8"))
    topic, run_id, date = "test", "run", "2025-04-01"
    identity = {"topic": topic, "run_id": run_id}
    tagged, index, tags, records, correlations = [], [], [], [], []
    for index_no, (title, line, body) in enumerate(pack._sections(original), 1):
        body_hash = compute_body_hash(body)
        report_id, _ = compute_individual_report_event_id(topic, date, body_hash)
        record = {
            "locator_kind": "markdown_section", "source_file": "notes.md", "heading_level": 2,
            "candidate_ordinal": index_no, "original_heading_text": title, "start_line": line,
            "report_event_id": report_id, "date": date, "body_sha256": body_hash,
        }
        source_id, _ = compute_source_event_id(topic, record)
        record["source_event_id"] = source_id
        records.append(record)
        correlations.append({"report_event_id": report_id, "date": date, "body_sha256": body_hash,
                             "source_event_ids": [source_id]})
        anchor = f"event-{date}-{body_hash}"
        tagged.append(f'## Event: {date} - {title}\n\n<a id="{anchor}"></a>\n\n{body}\n\n')
        index.append(f"[{title}](../chronicle_tagged.md#{anchor})\n")
        tags.append({"title": title, "date": date, "themes": []})
    docs = {
        pack.MANIFEST: {**identity, "schema_version": 1, "adapter": {"id": "prepare_generic_markdown_chronicle"},
                        "exit_codes": dict.fromkeys(("prepare", "pipeline", "provenance", "summarize"), 0)},
        pack.LINEAGE: {**identity, "$schema": "event-lineage-v1", "events": records},
        pack.CORRELATION: {**identity, "$schema": "event-correlation-v1", "report_events": correlations,
                           "ambiguous_matches": [], "unmerged_source_event_count": 0,
                           "report_event_count": 4, "source_event_count": 4,
                           "survivor_verification": {"expected_key_count": 4, "actual_key_count": 4,
                                                     "missing_key_count": 0, "unexpected_key_count": 0}},
        pack.TAGS: tags, pack.CHAIN: {"status": "ok", "ingest_files": [{"rejected": 0}]},
    }
    artifacts = {**{name: json.dumps(data) for name, data in docs.items()},
                 pack.TAGGED: "".join(tagged), pack.INDEX: "\n".join(index)}
    receipt = {"schema": "whs-context-receipt-v1",
               "artifacts": {name: pack.digest(text.encode("utf-8")) for name, text in artifacts.items()},
               "sources": {source_file.name: pack.digest(source_file.read_bytes())}}
    for name, text in artifacts.items():
        path = run / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return run, source, receipt, original


def test_complete_event_and_adjacent_conditions_keep_exact_ids(example):
    run, source, receipt, _ = example
    checked = pack.load_run(run, source, receipt)
    packet = pack.export(checked, "AA-1", 10_000)
    assert packet["route"] == "structural"
    assert [u["selection"] for u in packet["units"]] == ["exact_term_match", "adjacent_qualification"]
    assert packet["units"][0]["anchor"] == checked["units"][0]["anchor"]
    assert "12 bar maximum.\n\nDo not open the bypass." in packet["units"][0]["text"]
    assert "Use only at 19 °C." in packet["units"][1]["text"]
    assert "AA-10" not in pack.serialize(packet)
    assert packet == pack.export(pack.load_run(run, source, receipt), "AA-1", 10_000)
    assert "gold" not in packet


def test_raw_fallback_preserves_crlf_and_enforces_budget(example):
    run, source, receipt, original = example
    checked = pack.load_run(run, source, receipt)
    fallback = pack.export(checked, "not found anywhere", 10_000)
    assert fallback["route"] == "raw"
    assert fallback["sources"][0]["text"] == original
    assert checked["source_reread_bytes"] == len(original.encode("utf-8"))
    assert pack.export(checked, "not found anywhere", 128)["route"] == "refused"


def test_source_hash_change_rejects_even_with_unchanged_locator(example):
    run, source, receipt, original = example
    (source / "notes.md").write_bytes(original.replace("12 bar", "13 bar").encode("utf-8"))
    with pytest.raises(pack.ProvenanceError, match="pinned hash mismatch"):
        pack.load_run(run, source, receipt)


@pytest.mark.parametrize(("name", "change", "retry_hash", "reason"), [
    (pack.INDEX, lambda text: text.replace("#event-", "#other-", 1), False, "pinned hash mismatch"),
    (pack.INDEX, lambda text: text.replace("#event-", "#other-", 1), True, "event navigation"),
    (pack.CORRELATION, lambda text: text.replace('"ambiguous_matches": []', '"ambiguous_matches": [{}]'),
     True, "ambiguous or incomplete"),
])
def test_invalid_artifacts_rejected(example, name, change, retry_hash, reason):
    run, source, receipt, _ = example
    path = run / name
    path.write_bytes(change(path.read_text(encoding="utf-8")).encode("utf-8"))
    if retry_hash:
        receipt["artifacts"][name] = pack.digest(path.read_bytes())
    with pytest.raises(pack.ProvenanceError, match=reason):
        pack.load_run(run, source, receipt)


def test_rejected_ingest_uses_raw_fallback(example):
    run, source, receipt, _ = example
    path = run / pack.CHAIN
    data = json.loads(path.read_bytes())
    data["ingest_files"][0]["rejected"] = 1
    path.write_bytes(json.dumps(data).encode("utf-8"))
    receipt["artifacts"][pack.CHAIN] = pack.digest(path.read_bytes())
    result = pack.export(pack.load_run(run, source, receipt), "AA-1", 10_000)
    assert result["route"] == "raw"
    assert result["reason"] == "rejected_ingest"
