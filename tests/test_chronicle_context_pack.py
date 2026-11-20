import json

import pytest

from scripts.experiments import benchmark_context_pack, chronicle_context_pack as pack
from tools.run_topic_report import compute_individual_report_event_id, compute_source_event_id
from wordpipe.chronicle.merge import compute_body_hash


@pytest.fixture
def example(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    run = tmp_path / "run"
    entries = [
        ("Pump AA-1", "12 bar maximum.\n\nDo not open the bypass.\n\n- **Nested instruction:** 24 Â°C."),
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
        normalized = body.replace("- **Nested instruction:**", "* **Nested instruction:**").replace("Â°", "°")
        body_hash = compute_body_hash(normalized)
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
        tagged.append(f'## Event: {date} - {title}\n\n<a id="{anchor}"></a>\n\n{normalized}\n\n')
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
    fallback = pack.export(checked, "Notes", 10_000)
    assert fallback["route"] == "raw"
    assert fallback["sources"][0]["text"] == original
    assert checked["source_reread_bytes"] == len(original.encode("utf-8"))
    budget_refusal = pack.export(checked, "Notes", 128)
    assert budget_refusal["reason"] == "verified_raw_exceeds_budget"


@pytest.mark.parametrize("query", ["not found anywhere", "pump AA-99"])
def test_unanswerable_query_does_not_dump_verified_raw(example, query):
    run, source, receipt, _ = example
    checked = pack.load_run(run, source, receipt)
    refused = pack.export(checked, query, 10_000)
    assert refused["route"] == "refused"
    assert refused["reason"] == "no_verified_query_evidence"
    assert not refused["units"] and not refused["sources"]
    assert pack.export_b1(checked, query, 10_000)["route"] == "raw"


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


def test_repinned_source_with_wrong_body_is_rejected(example):
    run, source, receipt, original = example
    file = source / "notes.md"
    file.write_bytes(original.replace("12 bar", "13 bar").encode("utf-8"))
    receipt["sources"][file.name] = pack.digest(file.read_bytes())
    # B1 checks the unchanged locator and accepts the re-pinned file under its old anchor.
    old = pack._load_run(run, source, receipt, verify_body=False)
    assert "13 bar" in old["units"][0]["text"]
    with pytest.raises(pack.ProvenanceError, match="source-to-survivor body mismatch"):
        pack.load_run(run, source, receipt)


def test_canonical_body_replay_preserves_original_display(example):
    run, source, receipt, _ = example
    unit = pack.load_run(run, source, receipt)["units"][0]
    assert "- **Nested instruction:** 24 Â°C." in unit["text"]
    assert "* **Nested instruction:** 24 °C." in (run / pack.TAGGED).read_text(encoding="utf-8")


def _unit(ordinal, text):
    return {"anchor": f"unit-{ordinal}", "date": "2025-01-01",
            "sources": [{"file": "notes.md", "section": ordinal}], "text": text}


def _retrieval_run():
    return {"identity": {"topic": "synthetic"}, "target": "index", "rejected": 0, "outside": [],
            "sources": [{"file": "notes.md", "text": "BC-81 suction chamber. " + "Raw source elsewhere. " * 500}],
            "units": [
                _unit(1, "## BC-81 suction chamber\n\nAn 18 bar chamber trial is cleared."),
                _unit(3, "## Chamber records\n\nThe earlier chamber procedure must use a gasket."),
                _unit(4, "## KS-62 chamber correction\n\nThe same chamber pressure of 18 bar requires a different valve."),
                _unit(6, "## Hose shipment\n\nThe shipment must include 18 coils."),
            ]}


def test_nonadjacent_closure_uses_subject_and_reference_not_quantity_alone():
    run = _retrieval_run()
    assert [u["anchor"] for u in pack.export_b1(run, "BC-81", 20_000)["units"]] == ["unit-1"]
    packet = pack.export(run, "BC-81", 20_000)
    assert [u["anchor"] for u in packet["units"]] == ["unit-1", "unit-3"]
    assert packet["units"][1]["selection"] == "related_qualification"


@pytest.mark.parametrize(("extra", "reason"), [
    ({"outside": ["BC-81 cannot be tested offsite."]}, "relevant_material_outside_units"),
    ({"units": [_unit(9, "## Handwritten addendum\n\nThe earlier one must remain dry.")]},
     "ambiguous_qualification"),
])
def test_outside_or_unresolved_reference_uses_raw(extra, reason):
    run = _retrieval_run()
    for key, value in extra.items():
        run[key].extend(value)
    packet = pack.export(run, "BC-81", 20_000)
    assert packet["route"] == "raw"
    assert packet["reason"] == reason


def test_g1_scores_valid_population_and_expected_refusals_separately():
    def row(case, label, route=None, tokens=None, critical=None):
        result = {"case": case, "reference": {"classification": label, "critical": critical or []},
                  "A": {"tokens": 100}}
        if route:
            result["B2"] = {"route": route, "tokens": tokens, "delivered": route != "refused",
                            "identity_ok": True, "misses": {"critical": []},
                            "missing_ids": [], "unsupported_units": 0}
        return result

    summary = benchmark_context_pack.g1_summary([
        row("selected", "valid", "structural", 50),
        row("fallback", "valid", "raw", 99),
        row("budget", "valid", "refused", critical=["required"]),
        row("stale", "expected_refusal"),
        row("unanswerable", "expected_refusal", "raw", 1),
    ])
    assert summary["valid_verified_delivery"] == [2, 3]
    assert summary["expected_refusal"] == [1, 2]
    assert summary["unexpected_deliveries"] == ["unanswerable"]
    assert summary["valid_full_population_protected_fact_misses"] == 1
    assert summary["median_valid_token_reduction_pct"] == 0
