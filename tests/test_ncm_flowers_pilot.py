"""Synthetic backend contract tests. No model runtime or corpus files are loaded."""
import pytest

from scripts.experiments import ncm_flowers_pilot as pilot


@pytest.fixture
def case():
    return pilot.load_cases()[2]


def accepts_review(_, __):
    return True


def response(case, summary="Water only after the surface dries."):
    return {"summary": summary, "source": pilot.identity(case)}


def test_comparison_preserves_critical_facts_and_discloses_absent_c():
    values = pilot.comparison(pilot.load_cases())
    assert len(values["cases"]) == 8
    assert values["ncm_generation_ms"] is None
    assert values["ncm_median_c_vs_b_token_reduction_pct"] is None
    for row in values["cases"]:
        assert row["arm_a"]["missing_literals"] == []
        assert row["arm_b"]["missing_critical_literals"] == []
        assert row["arm_b"]["source_integrity"]
        assert row["arm_c"]["status"] == "not_run"
        assert row["arm_c"]["effective"] is None


@pytest.mark.parametrize(("output", "reason"), [
    ([], "invalid_response"),
    ({"summary": 3}, "invalid_response"),
    ({"summary": "fabricated", "source": {"reference": "unrelated"}}, "source_mismatch"),
])
def test_invalid_response_uses_exact_source_fallback(case, output, reason):
    result = pilot.evaluate_candidate(case, lambda *_args, **_kw: output, accepts_review)
    assert result["reason"] == reason
    assert result["effective"]["source"] == pilot.identity(case)


@pytest.mark.parametrize("summary", ["", " \n ", "é" * (pilot.MAX_OUTPUT_BYTES // 2 + 1)])
def test_empty_or_oversize_response(case, summary):
    result = pilot.evaluate_candidate(case, lambda *_args, **_kw: response(case, summary), accepts_review)
    assert result["reason"] == "output_limit"


def test_oversize_input_stops_before_backend(case):
    case = {**case, "lines": ["é" * (pilot.MAX_INPUT_BYTES // 2 + 1)]}

    def unused(*_args, **_kw):
        pytest.fail("Backend received oversize input")

    assert pilot.evaluate_candidate(case, unused)["reason"] == "input_limit"


@pytest.mark.parametrize(("exc", "reason"), [(TimeoutError, "timeout"), (FileNotFoundError, "missing_checkpoint")])
def test_execution_failure_preserves_fallback(case, exc, reason):
    def fail(*_args, **_kw):
        raise exc()

    result = pilot.evaluate_candidate(case, fail)
    assert result["reason"] == reason
    assert not pilot.retention(case, result["effective"])["missing_critical_literals"]


def test_restricted_cpu_policy_and_protected_fact_packet(case):
    def backend(request, *, timeout_seconds):
        assert request["load_policy"] == {"weights_only": True, "map_location": "cpu"}
        assert request["max_input_tokens"] == 512
        assert request["max_output_slots"] == 48
        assert request["source"]["sha256"] == pilot.source_digest(case)
        assert timeout_seconds == 3
        return response(case)

    result = pilot.evaluate_candidate(case, backend, accepts_review, timeout_seconds=3)
    assert result["status"] == "accepted"
    assert not pilot.retention(case, result["effective"])["missing_critical_literals"]


def test_independent_review_cannot_be_replaced_by_exact_fact_sidecar(case):
    def backend(*_args, **_kw):
        return response(case, "Leave standing water in the saucer.")

    result = pilot.evaluate_candidate(case, backend)
    assert result["reason"] == "independent_review_not_passed"
    assert result["candidate"]["text"] == "Leave standing water in the saucer."
    assert result["effective"] != result["candidate"]


def test_unmatched_extraction_remains_identity_checked_raw_fallback(case):
    case = {**case, "query": "unmatched"}
    bundle, route = pilot.extractive_packet(case)
    assert route == "no_keyword_match_raw"
    assert bundle["text"] == pilot.source_text(case)
    assert bundle["source"] == pilot.identity(case)
