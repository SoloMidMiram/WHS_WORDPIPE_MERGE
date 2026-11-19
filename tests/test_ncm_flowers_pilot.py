"""Synthetic contract tests with fakes and standard-library worker processes."""
import json
import sys

import pytest

from scripts.experiments import ncm_flowers_pilot as pilot


@pytest.fixture
def case():
    return pilot.load_cases()[2]


def fake_encode(text):
    return list(text.encode("utf-8"))


def accepts_review(_, __):
    return True


def response(case, summary="Water only after the surface dries.", *, input_token_count=None):
    return {
        "summary": summary, "source": pilot.identity(case),
        "input_token_count": len(fake_encode(pilot.source_text(case))) if input_token_count is None else input_token_count,
    }


def evaluate(case, backend, review=None, **options):
    options.setdefault("encode_input", fake_encode)
    return pilot.evaluate_candidate(case, backend, review, **options)


def test_comparison_keeps_raw_source_and_reports_absent_backend():
    cases = pilot.load_cases()
    values = pilot.comparison(cases, pilot.load_gold(cases))
    assert len(values["cases"]) == 8
    assert values["median_c_vs_b_token_reduction_pct"] is None
    for row in values["cases"]:
        assert row["arm_a"]["missing_literals"] == []
        assert row["arm_b"]["source_integrity"]
        assert row["arm_c"]["status"] == "not_run"
        assert row["arm_c_metrics"] is None


def test_gold_changes_score_only(case, monkeypatch, tmp_path):
    original = pilot.load_gold(pilot.load_cases())[case["id"]]
    before = pilot.extractive_packet(case)
    baseline = pilot.comparison([case], {case["id"]: original})
    path = tmp_path / "gold.json"
    path.write_text(
        json.dumps({"schema": "whs-ncm-pilot-gold-v1", "facts": {case["id"]: []}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(pilot, "GOLD", path)
    revised = pilot.comparison([case], pilot.load_gold([case]))
    assert pilot.extractive_packet(case) == before
    assert baseline["cases"][0]["arm_b"]["annotated_facts"] > revised["cases"][0]["arm_b"]["annotated_facts"]
    assert baseline["cases"][0]["arm_b"]["utf8_bytes"] == revised["cases"][0]["arm_b"]["utf8_bytes"]
    assert before[0]["protected_source_lines"] == []


@pytest.mark.parametrize(("output", "reason"), [
    ([], "invalid_response"),
    ({"summary": 3}, "invalid_response"),
    ({"summary": "fabricated", "source": {"reference": "unrelated"}}, "source_mismatch"),
])
def test_invalid_response_uses_exact_source_fallback(case, output, reason):
    result = evaluate(case, lambda *_args, **_kw: output, accepts_review)
    assert result["reason"] == reason
    assert result["effective"] == pilot.packet(case, pilot.source_text(case))


@pytest.mark.parametrize("summary", ["", " \n ", "é" * (pilot.MAX_OUTPUT_BYTES // 2 + 1)])
def test_empty_or_oversize_response(case, summary):
    result = evaluate(case, lambda *_args, **_kw: response(case, summary), accepts_review)
    assert result["reason"] == "output_limit"


def never_called(*_args, **_kwargs):
    pytest.fail("Oversize or unavailable-tokenizer input reached the worker")


def test_oversize_byte_input_stops_before_encoder_and_backend(case):
    huge = {**case, "lines": ["é" * (pilot.MAX_INPUT_BYTES // 2 + 1)]}
    assert evaluate(huge, never_called, encode_input=never_called)["reason"] == "input_limit"


def test_token_overflow_rejected_without_silent_truncation(case):
    assert evaluate(case, never_called, encode_input=lambda _: [1] * 513)["reason"] == "input_limit"
    assert evaluate(case, never_called, encode_input=None)["reason"] == "tokenizer_unavailable"


@pytest.mark.parametrize(("exc", "reason"), [(TimeoutError, "timeout"), (FileNotFoundError, "missing_checkpoint")])
def test_execution_failure_preserves_complete_raw_fallback(case, exc, reason):
    def fail(*_args, **_kw):
        raise exc()

    result = evaluate(case, fail)
    assert result["reason"] == reason
    assert result["effective"] == pilot.packet(case, pilot.source_text(case))


def test_restricted_cpu_policy_and_exact_token_limit(case):
    ids = list(range(512))

    def backend(request, *, timeout_seconds):
        assert request["load_policy"] == {"weights_only": True, "map_location": "cpu"}
        assert request["input_ids"] == ids
        assert request["max_input_tokens"] == 512
        assert request["max_output_slots"] == 48
        assert request["source"] == pilot.identity(case)
        assert "facts" not in request
        assert timeout_seconds == 3
        return response(case, input_token_count=len(ids))

    result = evaluate(case, backend, accepts_review, encode_input=lambda _: ids, timeout_seconds=3)
    assert result["status"] == "accepted"
    assert result["effective"]["protected_source_lines"] == []


def test_missing_semantic_review_uses_original_even_with_well_formed_summary(case):
    result = evaluate(case, lambda *_args, **_kw: response(case, "Leave standing water in the saucer."))
    assert result["reason"] == "independent_review_not_passed"
    assert result["candidate"]["text"] == "Leave standing water in the saucer."
    assert result["effective"] == pilot.packet(case, pilot.source_text(case))


def test_unmatched_extraction_returns_original(case):
    case = {**case, "query": "unmatched"}
    bundle, route = pilot.extractive_packet(case)
    assert route == "no_keyword_match_raw"
    assert bundle == pilot.packet(case, pilot.source_text(case))


def test_comparison_can_use_subprocess_with_only_source_inputs(case, tmp_path):
    script = (
        "import json, sys;"
        "r=json.load(sys.stdin);"
        "assert 'facts' not in r and r['input_ids'];"
        "print(json.dumps({'summary':'Wait until dry.', 'source':r['source'],'input_token_count':len(r['input_ids'])}))"
    )
    backend = pilot.subprocess_backend([sys.executable, "-I", "-S", "-c", script], cwd=tmp_path)
    result = pilot.comparison(
        [case], {case["id"]: []}, encode_input=fake_encode, backend=backend, review=accepts_review,
    )
    row = result["cases"][0]
    assert row["arm_c"]["status"] == "accepted"
    assert row["arm_c_metrics"]["source_integrity"]
    assert result["median_c_vs_b_token_reduction_pct"] is not None


def test_subprocess_deadline_returns_fallback(case, tmp_path):
    backend = pilot.subprocess_backend(
        [sys.executable, "-I", "-S", "-c", "import time; time.sleep(30)"], cwd=tmp_path,
    )
    assert evaluate(case, backend, timeout_seconds=0.1)["reason"] == "timeout"


def test_subprocess_response_size_is_bounded(case, tmp_path):
    backend = pilot.subprocess_backend(
        [sys.executable, "-I", "-S", "-c", f"print('x' * {pilot.MAX_RESPONSE_BYTES})"], cwd=tmp_path,
    )
    assert evaluate(case, backend)["reason"] == "backend_error"


def test_worker_partial_input_is_rejected_and_raw_fallback_is_counted(case):
    def backend(request, *, timeout_seconds):
        return response(case, input_token_count=len(request["input_ids"]) - 1)

    result = pilot.comparison(
        [case], {case["id"]: []}, encode_input=fake_encode, backend=backend, review=accepts_review,
    )
    row = result["cases"][0]
    assert row["arm_c"]["reason"] == "input_token_count_mismatch"
    assert row["arm_c_metrics"]["estimated_consumer_tokens"] == row["arm_a"]["estimated_consumer_tokens"]
    assert result["arm_c_fallback_rate"] == 1
