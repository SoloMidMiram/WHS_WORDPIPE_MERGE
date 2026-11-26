"""EXEC-01 policy and deterministic arbitration regressions."""
import pytest

from wordpipe.execution import Cancellation, ExecutionPolicy, Outcome, select_trigger


@pytest.mark.parametrize(
    ("completed", "cancelled", "deadline", "now", "code", "expected"),
    [
        (1, 2, 2, 3, 0, (Outcome.SUCCESS, 1)),
        (1, None, 2, 3, 7, (Outcome.NATIVE_FAILURE, 1)),
        (2, None, 2, 3, 0, (Outcome.TIMEOUT, 2)),
        (2, 2, 2, 3, 0, (Outcome.CANCELLED, 2)),
        (3, 2, 1, 4, 0, (Outcome.TIMEOUT, 1)),
        (None, None, 2, 1, None, None),
    ],
)
def test_arbitration(completed, cancelled, deadline, now, code, expected):
    assert select_trigger(completed, cancelled, deadline, now, code) == expected


@pytest.mark.parametrize("kwargs", [
    {"timeout": 0}, {"timeout": float("nan")}, {"timeout": True},
    {"cleanup_grace": 5}, {"stdout_limit": 1_048_577}, {"stderr_limit": -1},
])
def test_invalid_policy(kwargs):
    with pytest.raises(ValueError):
        ExecutionPolicy(**kwargs)


def test_cancellation_is_one_shot():
    values = iter([1., 2.])
    cancellation = Cancellation(lambda: next(values))
    cancellation.request()
    cancellation.request()
    assert cancellation.requested_at == 1.
