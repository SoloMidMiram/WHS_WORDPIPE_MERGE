"""EXEC-01 deterministic policy and finite real-process regressions."""
import os
import signal
import sys
import threading
import time

import pytest

from wordpipe.execution import (
    MAX_CAPTURE, Cancellation, Cleanup, ExecutionPolicy, Outcome, execute,
    inherited_context, select_trigger,
)


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


def stage(code, policy=ExecutionPolicy()):
    return execute([sys.executable, "-c", code], policy)


def test_native_results_and_missing_executable(tmp_path):
    assert stage("pass").exit_code == 0
    result = stage("raise SystemExit(7)")
    assert (result.outcome, result.native_code, result.exit_code) == (Outcome.NATIVE_FAILURE, 7, 7)
    result = execute([str(tmp_path / "missing-executable")])
    assert result.outcome == Outcome.LAUNCH_FAILURE and result.exit_code != 0


def test_concurrent_stream_caps_and_invalid_utf8():
    result = stage(
        "import os,threading;"
        "t=threading.Thread(target=os.write,args=(2,b'Z'*1100000));"
        "t.start();os.write(1,b'\\xff'+b'A'*1100000);t.join()",
    )
    assert result.outcome == Outcome.SUCCESS
    assert len(result.stdout.retained) == len(result.stderr.retained) == MAX_CAPTURE
    assert (result.stdout.observed, result.stderr.observed) == (1_100_001, 1_100_000)
    assert result.stdout.truncated and result.stderr.truncated
    assert result.stdout.retained.decode("utf-8", errors="replace").startswith("\ufffd")


def test_two_second_deadline_with_descendant_held_pipes(tmp_path):
    heartbeat = tmp_path / "child-heartbeat"
    child = (
        "import signal,time;from pathlib import Path;"
        "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
        "signal.signal(getattr(signal,'SIGBREAK',signal.SIGTERM),signal.SIG_IGN);"
        f"path=Path({str(heartbeat)!r});"
        "\nfor n in range(150):\n path.write_text(str(n));time.sleep(.05)"
    )
    result = stage(
        f"import subprocess,sys;subprocess.Popen([sys.executable,'-c',{child!r}])",
        ExecutionPolicy(timeout=2),
    )
    assert (result.outcome, result.trigger, result.cleanup) == (Outcome.TIMEOUT, Outcome.TIMEOUT, Cleanup.VERIFIED)
    assert 2 <= result.elapsed <= 7
    observed = heartbeat.read_bytes()
    time.sleep(.15)
    assert heartbeat.read_bytes() == observed
    print(f"EXEC-01 deadline cleanup: {result.elapsed - 2:.3f}s")


def test_cooperative_cancellation():
    cancel = Cancellation()
    timer = threading.Timer(.3, cancel.request)
    timer.start()
    try:
        result = stage("import time;time.sleep(7)", ExecutionPolicy(cancellation=cancel))
    finally:
        timer.cancel()
        timer.join()
    assert (result.outcome, result.cleanup) == (Outcome.CANCELLED, Cleanup.VERIFIED)
    assert time.monotonic() - cancel.requested_at <= 5


def test_unvalidated_environment_cannot_claim_ownership(monkeypatch):
    monkeypatch.setenv("WORDPIPE_EXECUTION_OWNER", '{"issuer":1,"token":"fake","deadline":null}')
    with pytest.raises((ValueError, OSError)):
        inherited_context()
    assert stage("import os;assert 'WORDPIPE_EXECUTION_OWNER' not in os.environ").exit_code == 0


@pytest.mark.skipif(sys.platform != "win32", reason="Windows kernel ownership case")
def test_failed_windows_job_assignment_never_runs_child(tmp_path, monkeypatch):
    from wordpipe import _execution_windows

    def rejected(*args):
        raise OSError("injected Job Object assignment failure")

    monkeypatch.setattr(_execution_windows, "assign_job", rejected)
    marker = tmp_path / "child-ran"
    result = stage(f"from pathlib import Path; Path({str(marker)!r}).touch()")
    assert result.outcome == Outcome.LAUNCH_FAILURE
    assert not marker.exists()


@pytest.mark.skipif(sys.platform != "win32", reason="Windows kernel ownership case")
def test_windows_job_inside_existing_job():
    code = (
        "import sys; from wordpipe.execution import execute;"
        "r=execute([sys.executable,'-c','print(45678)']);"
        "assert r.exit_code==0 and r.stdout.retained.strip()==b'45678',r;"
        "print('nested job verified')"
    )
    result = stage(code)
    assert result.exit_code == 0, result.stderr.retained
    assert b"nested job verified" in result.stdout.retained
