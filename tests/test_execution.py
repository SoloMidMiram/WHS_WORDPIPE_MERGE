"""EXEC-01 deterministic policy and finite real-process regressions."""
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

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
    cut = stage("import os;os.write(1,b'A\\xe2\\x82\\xac')", ExecutionPolicy(stdout_limit=3))
    assert cut.outcome == Outcome.SUCCESS
    assert cut.stdout.truncated and cut.stdout.observed == 4
    assert cut.stdout.retained == b"A\xe2\x82"
    assert len(cut.stdout.text(3).encode("utf-8")) <= 3


def is_live_fixture(pid):
    if sys.platform == "win32":
        import _winapi

        try:
            handle = _winapi.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
        except OSError as exc:
            if exc.winerror == 87:  # no such process
                return False
            raise
        try:
            return _winapi.WaitForSingleObject(handle, 0) != _winapi.WAIT_OBJECT_0
        finally:
            _winapi.CloseHandle(handle)
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except FileNotFoundError:
        return False
    return stat.rsplit(")", 1)[1].split()[0] not in ("Z", "X")


@pytest.mark.parametrize("leader_exits", [True, False])
def test_two_second_deadline_with_descendant_held_pipes(tmp_path, leader_exits):
    heartbeat = tmp_path / "child-heartbeat"
    pid_file = tmp_path / "child-pid"
    child = (
        "import os,signal,time;from pathlib import Path;"
        "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
        "signal.signal(getattr(signal,'SIGBREAK',signal.SIGTERM),signal.SIG_IGN);"
        f"Path({str(pid_file)!r}).write_text(str(os.getpid()));"
        f"path=Path({str(heartbeat)!r});"
        "\nfor n in range(150):\n path.write_text(str(n));time.sleep(.05)"
    )
    launch = f"import subprocess,sys;subprocess.Popen([sys.executable,'-c',{child!r}]);"
    if not leader_exits:
        launch += ("import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                   "signal.signal(getattr(signal,'SIGBREAK',signal.SIGTERM),signal.SIG_IGN);time.sleep(7)")
    result = stage(launch, ExecutionPolicy(timeout=2))
    assert (result.outcome, result.trigger, result.cleanup) == (Outcome.TIMEOUT, Outcome.TIMEOUT, Cleanup.VERIFIED)
    assert 2 <= result.elapsed <= 7
    assert not is_live_fixture(int(pid_file.read_text()))
    observed = heartbeat.read_bytes()
    time.sleep(.15)
    assert heartbeat.read_bytes() == observed
    print(f"EXEC-01 deadline cleanup: {result.elapsed - 2:.3f}s")


def test_cancellation_during_launch_is_arbitrated(monkeypatch):
    from wordpipe import execution

    cancel = Cancellation()

    class Backend:
        @staticmethod
        def Process(*args):
            cancel.request()
            raise OSError("injected failure while launching")

    monkeypatch.setattr(execution, "_backend", lambda: Backend)
    result = stage("pass", ExecutionPolicy(cancellation=cancel))
    assert result.outcome == result.trigger == Outcome.CANCELLED
    assert result.cleanup == Cleanup.NOT_STARTED


def test_cleanup_uncertainty_retains_trigger_with_one_budget(monkeypatch):
    from wordpipe import execution

    class Process:
        streams = (object(), object())

        def read(self, stream, size):
            return b""

        def code(self):
            return 0

        def remaining(self):
            raise OSError("injected inability to verify ownership")

        def stop(self, force):
            attempts.append((now[0], force))

        def close(self, exited):
            assert exited

    now, attempts = [2.], []
    monkeypatch.setattr(execution.time, "monotonic", lambda: now[0])

    def advance(seconds):
        now[0] += .125

    monkeypatch.setattr(execution.time, "sleep", advance)
    result = execution._supervise(Process(), ExecutionPolicy(timeout=2), None, 0., 2.)
    assert (result.outcome, result.trigger) == (Outcome.CLEANUP_FAILURE, Outcome.TIMEOUT)
    assert result.elapsed == 7 and attempts == [(2., False), (2.5, True)]


def test_inherited_execution_uses_kernel_membership_and_deadline():
    code = (
        "import sys;from wordpipe.execution import execute,inherited_context,ExecutionPolicy;"
        "owner=inherited_context();assert owner is not None and owner.deadline is not None;"
        "r=execute([sys.executable,'-c','print(45678)'],ExecutionPolicy(inherited=owner));"
        "assert r.cleanup.value=='outer_owner' and r.stdout.retained.strip()==b'45678',r"
    )
    result = execute([sys.executable, "-c", code], ExecutionPolicy(timeout=2), publish_owner=True)
    assert result.exit_code == 0, result.stderr.retained


@pytest.mark.skipif(sys.platform != "linux", reason="POSIX SIGINT delivery fixture")
def test_keyboard_interrupt_records_cancelled(tmp_path):
    ready = tmp_path / "ready"
    child = f"from pathlib import Path;import time;Path({str(ready)!r}).touch();time.sleep(6)"
    supervisor = (
        "import sys;from wordpipe.execution import execute;"
        f"result=execute([sys.executable,'-c',{child!r}]);"
        "assert result.outcome.value=='cancelled' and result.cleanup.value=='verified',result"
    )
    with subprocess.Popen([sys.executable, "-c", supervisor], start_new_session=True) as proc:
        try:
            limit = time.monotonic() + 4
            while not ready.exists() and proc.poll() is None and time.monotonic() < limit:
                time.sleep(.01)
            assert ready.exists()
            start = time.monotonic()
            os.kill(proc.pid, signal.SIGINT)
            assert proc.wait(timeout=5) == 0
            assert time.monotonic() - start <= 5
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=2)


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
