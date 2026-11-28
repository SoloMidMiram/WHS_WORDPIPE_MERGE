"""Executable regression tests for the Chronicle PowerShell chain."""

from __future__ import annotations

import json
import hashlib
import os
import shutil
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHAIN_PS1 = REPO_ROOT / "pipeline" / "chain.ps1"

_POWERSHELL: str | None = shutil.which("pwsh") or shutil.which("powershell")
_PYTHON_EXE: str | None = shutil.which("python.exe" if os.name == "nt" else "python")


def _file_digests(root):
    return {p.relative_to(root): hashlib.sha256(p.read_bytes()).digest() for p in root.rglob("*") if p.is_file()}


def _read_evidence(out_dir: Path) -> dict:
    return json.loads((out_dir / "run.json").read_text(encoding="utf-8"))


def _run_chain(
    args: list[str], cwd: Path, script: Path = CHAIN_PS1,
) -> subprocess.CompletedProcess[str]:
    assert _POWERSHELL is not None
    return subprocess.run(
        [_POWERSHELL, "-NoProfile", "-File", str(script), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
    )


@pytest.mark.skipif(
    _POWERSHELL is None or _PYTHON_EXE is None,
    reason="chain.ps1 requires PowerShell and python.exe",
)
def test_chain_allow_partial_ingest_and_previous_output_preservation(tmp_path: Path) -> None:
    """A fresh partial attempt ignores seeded stale input and preserves the earlier run."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    out_dir = tmp_path / "out"

    alpha = raw_dir / "alpha.md"
    beta = raw_dir / "beta.md"

    # Run 1: only a valid dated file.
    alpha.write_text(
        textwrap.dedent("""\
        # Source

        - **2025-01-10 - Alpha Outage:** alpha outage body
        """),
        encoding="utf-8",
    )
    first = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir),
         "-SkipCategorize", "-SkipIndex"],
        cwd=REPO_ROOT,
    )
    assert first.returncode == 0, first.stdout + first.stderr
    normalised_alpha = out_dir / "normalised" / "alpha.md"
    merged = out_dir / "merged.md"
    assert normalised_alpha.exists(), "Run 1 should normalise alpha.md"
    assert merged.exists(), "Run 1 should produce merged.md"
    assert "Alpha Outage" in merged.read_text(encoding="utf-8")
    first_id = _read_evidence(out_dir)["run_id"]
    first_dir = out_dir
    first_hashes = _file_digests(first_dir)

    # Run 2: alpha is now undated (ingest fails) and beta is a new valid file.
    alpha.write_text(
        textwrap.dedent("""\
        # Source

        - **unknown - Alpha Outage:** alpha outage body
        """),
        encoding="utf-8",
    )
    beta.write_text(
        textwrap.dedent("""\
        # Source

        - **2025-02-20 - Beta Launch:** beta launch body
        """),
        encoding="utf-8",
    )
    collision = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(first_dir), "-SkipCategorize"],
        cwd=REPO_ROOT,
    )
    assert collision.returncode == 1
    assert "fresh OutputDir" in collision.stderr
    assert _file_digests(first_dir) == first_hashes
    out_dir = tmp_path / "partial"
    (out_dir / "normalised").mkdir(parents=True)
    shutil.copyfile(normalised_alpha, out_dir / "normalised" / "alpha.md")
    merged = out_dir / "merged.md"
    second = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir),
         "-AllowPartialIngest", "-SkipCategorize", "-SkipIndex"],
        cwd=REPO_ROOT,
    )
    assert second.returncode == 0, second.stdout + second.stderr
    merged_text = merged.read_text(encoding="utf-8")
    assert "Beta Launch" in merged_text, "New valid file's event must be merged"
    assert "Alpha Outage" not in merged_text, (
        "Stale event from the previous run's normalised file must not be merged"
    )
    partial = _read_evidence(out_dir)
    assert partial["run_id"] != first_id
    assert partial["status"] == "partial"
    assert partial["exit_code"] == 0
    assert partial["merge_inputs"] == ["normalised/beta.md"]
    assert [stage["status"] for stage in partial["stages"]] == [
        "partial", "skipped", "ok", "skipped", "skipped",
    ]
    assert [(item["accepted"], item["rejected"]) for item in partial["ingest_files"]] == [
        (0, 1), (1, 0),
    ]
    assert "alpha outage body" not in (out_dir / "run.json").read_text(encoding="utf-8")

    partial_hashes = _file_digests(out_dir)
    failed_dir = tmp_path / "failed"
    verified = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(failed_dir),
         "-AllowPartialIngest", "-Verify", "-SkipCategorize"],
        cwd=REPO_ROOT,
    )
    assert verified.returncode == 2, verified.stdout + verified.stderr
    assert "Verification failed" in verified.stdout
    failed = _read_evidence(failed_dir)
    assert failed["run_id"] != partial["run_id"]
    assert failed["exit_code"] == 2
    assert failed["merge_inputs"] == []
    assert [stage["status"] for stage in failed["stages"]] == [
        "partial", "failed", "not_run", "skipped", "skipped",
    ]
    assert _file_digests(out_dir) == partial_hashes
    assert _file_digests(first_dir) == first_hashes


@pytest.mark.skipif(
    _POWERSHELL is None or _PYTHON_EXE is None,
    reason="chain.ps1 requires PowerShell and python.exe",
)
def test_chain_all_five_stages_with_verify(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "events.md").write_text(
        "- **2025-01-10 - Alpha Outage:** first event\n"
        "- **2025-01-11 - Beta Launch:** second event\n",
        encoding="utf-8",
    )
    (raw_dir / "overview.md").write_text("# Overview\n\nNarrative only.\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    result = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir),
         "-Verify", "-Verbose"],
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Total events extracted: 2" in result.stdout
    assert "WARNING: No dates found in content" in result.stdout
    assert "Files with issues: 0" in result.stdout
    merged = (out_dir / "merged.md").read_text(encoding="utf-8")
    assert "Alpha Outage" in merged
    assert "Beta Launch" in merged
    tagged = json.loads((out_dir / "chronicle_tagged.tagged.json").read_text(encoding="utf-8"))
    assert len(tagged) == 2
    appendix = out_dir / "appendix"
    index = (appendix / "event_index.md").read_text(encoding="utf-8")
    assert index.count("Alpha Outage") == 1
    assert index.count("Beta Launch") == 1
    for name in ("theme_index.md", "source_manifest.md", "link_registry.md"):
        assert (appendix / name).is_file()
    evidence = _read_evidence(out_dir)
    assert evidence["schema_version"] == 1
    assert evidence["status"] == "ok"
    assert [stage["name"] for stage in evidence["stages"]] == [
        "ingest", "verify", "merge", "categorize", "index",
    ]
    assert all(stage["status"] == "ok" and stage["duration_ms"] >= 0 for stage in evidence["stages"])
    assert "chronicle_tagged.tagged.json" in evidence["stages"][3]["outputs"]
    assert "appendix/link_registry.md" in evidence["stages"][4]["outputs"]
    assert evidence["merge_inputs"] == ["normalised/events.md", "normalised/overview.md"]
    assert [(item["accepted"], item["rejected"]) for item in evidence["ingest_files"]] == [(2, 0), (0, 0)]
    assert "No dates found" not in (out_dir / "run.json").read_text(encoding="utf-8")


@pytest.mark.skipif(
    _POWERSHELL is None or _PYTHON_EXE is None,
    reason="chain.ps1 requires PowerShell and python.exe",
)
@pytest.mark.parametrize("preexisting", [False, True], ids=["absent", "stale"])
@pytest.mark.parametrize("artifact", ["sidecar", "registry"])
def test_chain_omits_optional_artifacts_not_written_this_run(
    tmp_path: Path, artifact: str, preexisting: bool,
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    out_dir = tmp_path / "out"
    args = ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir)]
    if artifact == "sidecar":
        raw_text = "# Overview\n\nNarrative only.\n"
        relative_path = "chronicle_tagged.tagged.json"
        stage_index = 3
        args += ["-SkipIndex"]
    else:
        raw_text = "- **2025-01-10 - Alpha Outage:** first event\n"
        relative_path = "appendix/link_registry.md"
        stage_index = 4
        config = tmp_path / "index.json"
        config.write_text('{"no_link_registry": true}', encoding="utf-8")
        args += ["-IndexConfig", str(config)]
    (raw_dir / "input.md").write_text(raw_text, encoding="utf-8")
    path = out_dir / relative_path
    if preexisting:
        path.parent.mkdir(parents=True)
        path.write_bytes(b"previous run")

    result = _run_chain(args, cwd=REPO_ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    stage = _read_evidence(out_dir)["stages"][stage_index]
    assert stage["status"] == "ok"
    assert relative_path not in stage["outputs"]
    if preexisting:
        assert path.read_bytes() == b"previous run"
    else:
        assert not path.exists()


STAGE_SCRIPTS = ("ingest", "verify_ingest", "merge", "categorize", "index")


@pytest.fixture
def isolated_chain(tmp_path: Path, monkeypatch) -> tuple[Path, Path, Path]:
    # These copied drivers exercise ordinary EXEC-01 behavior with synthetic
    # stages outside the qualified checkout. CI-01 covers the real bridge.
    monkeypatch.delenv("WORDPIPE_ORIGIN_QUALIFICATION", raising=False)
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    chain = scripts / CHAIN_PS1.name
    shutil.copyfile(CHAIN_PS1, chain)
    shutil.copyfile(CHAIN_PS1.with_name("chain_evidence.ps1"), scripts / "chain_evidence.ps1")
    shutil.copyfile(CHAIN_PS1.with_name("execute_stage.py"), scripts / "execute_stage.py")
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "input.md").write_text("fixture", encoding="utf-8")
    for stage in STAGE_SCRIPTS:
        (scripts / f"{stage}.py").write_text(
            "import sys\n"
            "from pathlib import Path\n"
            f"Path({stage!r}).touch()\n"
            f"print('WARNING: diagnostic from {stage}', file=sys.stderr)\n",
            encoding="utf-8",
        )
    return chain, raw_dir, tmp_path / "out"


@pytest.mark.skipif(_POWERSHELL is None or _PYTHON_EXE is None, reason="requires native PowerShell and Python")
def test_direct_chain_timeout_skips_dependents_even_in_partial_mode(isolated_chain):
    chain, raw_dir, out_dir = isolated_chain
    (chain.parent / "ingest.py").write_text("import time\ntime.sleep(7)\n", encoding="utf-8")
    result = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir),
         "-StageTimeoutSeconds", "2", "-AllowPartialIngest"],
        cwd=raw_dir.parent, script=chain,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    summary = _read_evidence(out_dir)
    invocation = summary["ingest_files"][0]
    terminal = json.loads((out_dir / invocation["execution_evidence"]).read_text(encoding="utf-8"))
    assert terminal["outcome"] == terminal["trigger"] == "timeout"
    assert terminal["cleanup"] == "verified"
    assert 2 <= terminal["elapsed_seconds"] <= 7
    assert summary["stages"][2]["status"] == "not_run"
    assert not (raw_dir.parent / "merge").exists()


@pytest.mark.skipif(_POWERSHELL is None or _PYTHON_EXE is None, reason="requires native PowerShell and Python")
@pytest.mark.parametrize("expires", [False, True])
def test_inherited_chain_waits_for_redirected_descendant(isolated_chain, monkeypatch, expires):
    from wordpipe.execution import Cleanup, ExecutionPolicy, Outcome
    from tools.run_topic_report import run_stage

    chain, raw_dir, out_dir = isolated_chain
    monkeypatch.chdir(raw_dir.parent)
    artifact = raw_dir.parent / "stage-artifact"
    ready = raw_dir.parent / "worker-ready"
    leader_exited = raw_dir.parent / "leader-exited"
    completed = raw_dir.parent / "worker-completed"
    dependent = raw_dir.parent / "dependent-started"
    early_receipt = raw_dir.parent / "ingest-reported-before-completion"
    worker = chain.parent / "worker.py"
    worker.write_text(
        textwrap.dedent(f"""\
            import sys
            import time
            from pathlib import Path

            leader = int(sys.argv[1])
            if sys.platform == 'win32':
                import _winapi
                handle = _winapi.OpenProcess(0x00100000, False, leader)  # SYNCHRONIZE

                def leader_alive():
                    return _winapi.WaitForSingleObject(handle, 0) != _winapi.WAIT_OBJECT_0
            else:
                stat = Path(f'/proc/{{leader}}/stat')

                def leader_alive():
                    try:
                        return stat.read_text().rsplit(')', 1)[1].split()[0] not in ('Z', 'X')
                    except (FileNotFoundError, ProcessLookupError):
                        return False

            artifact = Path({str(artifact)!r})
            artifact.write_text('working')
            Path({str(ready)!r}).touch()
            limit = time.monotonic() + 2
            while leader_alive():
                assert time.monotonic() < limit, 'fixture leader did not exit'
                time.sleep(0.01)
            if sys.platform == 'win32':
                _winapi.CloseHandle(handle)
            Path({str(leader_exited)!r}).touch()
            evidence_dir = Path({str(out_dir / "exec-01")!r})
            until = time.monotonic() + {7 if expires else 0.6}
            while time.monotonic() < until:
                if Path({str(dependent)!r}).exists():
                    artifact.write_text('dependent entered early')
                    raise SystemExit(0)
                time.sleep(0.01)
                artifact.write_text('working')
            if any(evidence_dir.glob('*/1.json')):
                Path({str(early_receipt)!r}).touch()
            artifact.write_text('finished')
            Path({str(completed)!r}).touch()
            """),
        encoding="utf-8",
    )
    # Keep the leader alive until the worker can observe its exit reliably.
    (chain.parent / "ingest.py").write_text(
        textwrap.dedent(f"""\
            import os, subprocess, sys, time
            from pathlib import Path

            output = Path(sys.argv[sys.argv.index('--output') + 1])
            output.write_text('synthetic normalised input')
            child = subprocess.Popen(
                [sys.executable, '-S', {str(worker)!r}, str(os.getpid())],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            ready = Path({str(ready)!r})
            limit = time.monotonic() + 2
            while not ready.exists():
                assert child.poll() is None and time.monotonic() < limit, 'worker was not ready'
                time.sleep(0.01)
            """),
        encoding="utf-8",
    )
    (chain.parent / "verify_ingest.py").write_text(
        "from pathlib import Path\n"
        f"Path({str(dependent)!r}).touch()\n"
        f"assert Path({str(completed)!r}).exists(), 'premature verification'\n"
        f"assert Path({str(artifact)!r}).read_text() == 'finished', 'premature verification'\n",
        encoding="utf-8",
    )
    receipt = raw_dir.parent / "pipeline.json"
    # The inherited deadline includes shell and bridge startup. The executor's
    # separate G5 fixtures pin the two-second requirement without that startup.
    timeout = 4 if expires else 8
    result = run_stage(
        [_POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(chain), "-InputDir", str(raw_dir),
         "-OutputDir", str(out_dir), "-Verify", "-SkipCategorize", "-SkipIndex"],
        "pipeline: chain.ps1", policy=ExecutionPolicy(timeout=timeout),
        evidence_path=receipt, publish_owner=True,
    )
    terminal = json.loads(receipt.read_text(encoding="utf-8"))
    assert terminal["cleanup"] == Cleanup.VERIFIED
    assert ready.exists() and leader_exited.exists(), result["output"]
    if expires:
        assert terminal["outcome"] == terminal["trigger"] == Outcome.TIMEOUT, result["output"]
        assert timeout <= terminal["elapsed_seconds"] <= timeout + 5
        assert not dependent.exists()
        assert not (raw_dir.parent / "merge").exists()
        assert not completed.exists()
    else:
        assert result["exit_code"] == 0, result["output"]
        assert completed.exists() and dependent.exists() and artifact.read_text() == "finished"
        assert not early_receipt.exists(), "ingest reported completion before the descendant finished"
        invocation = _read_evidence(out_dir)["ingest_files"][0]
        evidence = json.loads((out_dir / invocation["execution_evidence"]).read_text(encoding="utf-8"))
        assert evidence["outcome"] == Outcome.SUCCESS
        assert evidence["policy"]["ownership"] == "inherited"
        assert evidence["policy"]["has_deadline"]
        assert evidence["cleanup"] == Cleanup.INHERITED


def _await_worker_readiness(process, ready):
    started = time.monotonic()
    deadline = started + 6
    status = None
    while not ready.exists() and (status := process.poll()) is None and time.monotonic() < deadline:
        time.sleep(.01)
    if ready.exists():
        return None
    return {
        "reason": "launcher_exited" if status is not None else "readiness_deadline_expired",
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "launcher_returncode": status,
        "worker_ready": False,
    }


def _readiness_stream_evidence(stream):
    # Windows can peek without consuming. On POSIX, only the terminal failure
    # path reads the pipe, with nonblocking reads and no later consumer.
    limit = 2048
    try:
        if os.name == "nt":
            import _winapi
            import msvcrt

            data, available, _ = _winapi.PeekNamedPipe(msvcrt.get_osfhandle(stream.fileno()), limit)
        else:
            fd = stream.fileno()
            os.set_blocking(fd, False)
            try:
                data = os.read(fd, limit)
            except BlockingIOError:
                data = b""
            available = None
    except OSError as exc:
        return {"io_error": exc.errno, "winerror": getattr(exc, "winerror", None)}

    # Emit fixed excerpts only. Arbitrary process output can contain paths,
    # arguments, or credentials, even in an isolated test.
    markers = {
        b"Stage 1 : Ingestion": "ingestion stage",
        b"Processing: input.md": "processing fixture input",
        b"[FAIL]": "reported stage failure",
        b"Traceback (most recent call last):": "Python traceback",
        b"ModuleNotFoundError:": "Python module import failure",
        b"Bounded execution bridge did not return a terminal record": "bridge terminal record missing",
    }
    return {
        "sampled_bytes": len(data),
        "available_bytes": available,
        "sample_limit_bytes": limit,
        "markers": [label for marker, label in markers.items() if marker in data],
    }


def _readiness_failure_evidence(process, shell, out_dir, bridge_entered):
    def interpreter_evidence(executable):
        if not isinstance(executable, str) or not executable:
            return {"resolved": False}
        return {
            "resolved": True,
            "name": Path(executable).name,
            "matches_pytest": os.path.normcase(executable) == os.path.normcase(sys.executable),
        }

    execution_dir = out_dir / "exec-01"
    request = next(execution_dir.glob("*/1.json.request"), None)
    selected_python = None
    if request is not None:
        try:
            with request.open("rb") as handle:
                selected_python = json.loads(handle.read(8192))["argv"][0]
        except (OSError, ValueError, KeyError, IndexError, TypeError):
            pass
    return {
        "launcher": Path(shell).name,
        "pytest_interpreter": Path(sys.executable).name,
        "python_on_test_path": interpreter_evidence(shutil.which("python.exe" if os.name == "nt" else "python")),
        "python_in_bridge_request": interpreter_evidence(selected_python),
        "bridge_request_present": request is not None,
        "bridge_main_entered": bridge_entered.exists(),
        "bridge_response_present": next(execution_dir.glob("*/1.json.response"), None) is not None,
        "terminal_receipt_present": next(execution_dir.glob("*/1.json"), None) is not None,
        "stdout": _readiness_stream_evidence(process.stdout),
        "stderr": _readiness_stream_evidence(process.stderr),
    }


@pytest.mark.parametrize(
    ("marker_present", "exit_code", "elapsed", "reason"),
    [
        (False, 7, 1, "launcher_exited"),
        (False, None, 6, "readiness_deadline_expired"),
        (True, None, 1, None),
    ],
)
def test_worker_readiness_outcome(monkeypatch, tmp_path, marker_present, exit_code, elapsed, reason):
    from unittest.mock import Mock

    ready = tmp_path / "worker-ready"
    if marker_present:
        monkeypatch.setattr(time, "sleep", lambda _: ready.touch())
    process = Mock()
    process.poll.return_value = exit_code
    clock = iter((100, 100 + elapsed, 100 + elapsed))
    monkeypatch.setattr(time, "monotonic", lambda: next(clock))

    result = _await_worker_readiness(process, ready)

    if reason is None:
        assert result is None
        process.poll.assert_called_once_with()
    else:
        assert result == {
            "reason": reason,
            "elapsed_seconds": elapsed,
            "launcher_returncode": exit_code,
            "worker_ready": False,
        }


def test_readiness_stream_evidence_caps_and_filters_output():
    reader, writer = os.pipe()
    with os.fdopen(reader, "rb") as stream, os.fdopen(writer, "wb", buffering=0) as output:
        assert _readiness_stream_evidence(stream)["sampled_bytes"] == 0
        payload = b"Processing: input.md\n" + b"private-value " * 155
        output.write(payload)
        evidence = _readiness_stream_evidence(stream)
        assert evidence["sampled_bytes"] == 2048
        assert evidence["markers"] == ["processing fixture input"]
        assert "private-value" not in json.dumps(evidence)
        if os.name == "nt":
            assert stream.read(len(payload)) == payload


def test_readiness_evidence_reports_bridge_progress(monkeypatch, tmp_path):
    from unittest.mock import Mock

    command = "python.exe" if os.name == "nt" else "python"
    monkeypatch.setattr(shutil, "which", lambda name: sys.executable if name == command else None)
    monkeypatch.setattr(sys.modules[__name__], "_readiness_stream_evidence", lambda stream: {})
    process = Mock()
    entered = tmp_path / "bridge-entered"
    before = _readiness_failure_evidence(process, "powershell", tmp_path, entered)
    assert not before["bridge_request_present"]
    assert not before["bridge_main_entered"]
    assert not before["bridge_response_present"]
    assert not before["terminal_receipt_present"]
    assert before["python_on_test_path"]["matches_pytest"]

    stage = tmp_path / "exec-01" / "test-run" / "1.json"
    stage.parent.mkdir(parents=True)
    stage.with_suffix(".json.request").write_text(
        json.dumps({"argv": [sys.executable, "secret-argument"]}), encoding="utf-8",
    )
    stage.touch()
    entered.touch()
    after = _readiness_failure_evidence(process, "powershell", tmp_path, entered)
    assert after["bridge_request_present"]
    assert after["bridge_main_entered"]
    assert not after["bridge_response_present"]
    assert after["terminal_receipt_present"]
    assert after["python_in_bridge_request"]["matches_pytest"]
    assert "secret-argument" not in json.dumps(after)


@pytest.mark.skipif(_POWERSHELL is None or _PYTHON_EXE is None, reason="requires native PowerShell and Python")
def test_direct_chain_ctrl_c_preserves_terminal_cancellation(isolated_chain):
    chain, raw_dir, out_dir = isolated_chain
    ready = raw_dir.parent / "worker-ready"
    (chain.parent / "ingest.py").write_text(
        f"from pathlib import Path\nimport time\nPath({str(ready)!r}).touch()\ntime.sleep(7)\n",
        encoding="utf-8",
    )
    # Observe the copied bridge entering main before it attempts worker launch.
    # A marker write failure must not change the bridge's normal behavior.
    bridge_entered = raw_dir.parent / "bridge-entered"
    bridge = chain.with_name("execute_stage.py")
    entry = "def main() -> int:\n"
    source = bridge.read_text(encoding="utf-8")
    assert source.count(entry) == 1
    bridge.write_text(
        source.replace(
            entry,
            entry + f"    try:\n        Path({str(bridge_entered)!r}).touch()\n    except OSError:\n        pass\n",
            1,
        ),
        encoding="utf-8",
    )
    if os.name == "nt":
        # Deliver a real Ctrl+C only to the fixture's private, hidden console.
        shell = shutil.which("powershell")
        assert shell is not None
        startup = subprocess.STARTUPINFO(dwFlags=subprocess.STARTF_USESHOWWINDOW, wShowWindow=0)
        options = {"creationflags": subprocess.CREATE_NEW_CONSOLE, "startupinfo": startup}
    else:
        shell = _POWERSHELL
        options = {"start_new_session": True}
    process = subprocess.Popen(
        [shell, "-NoProfile", "-File", str(chain), "-InputDir", str(raw_dir),
         "-OutputDir", str(out_dir), "-AllowPartialIngest"],
        cwd=raw_dir.parent, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **options,
    )
    try:
        failure = _await_worker_readiness(process, ready)
        if failure is not None:
            failure.update(_readiness_failure_evidence(process, shell, out_dir, bridge_entered))
            pytest.fail(json.dumps(failure, sort_keys=True))
        start = time.monotonic()
        if os.name == "nt":
            code = (
                "import ctypes,time;k=ctypes.WinDLL('kernel32',use_last_error=True);"
                "k.FreeConsole();"
                f"assert k.AttachConsole({process.pid}),ctypes.get_last_error();"
                "assert k.SetConsoleCtrlHandler(None,True),ctypes.get_last_error();"
                "assert k.GenerateConsoleCtrlEvent(0,0),ctypes.get_last_error();time.sleep(.1)"
            )
            subprocess.run([sys.executable, "-S", "-c", code], check=True, timeout=3,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            os.killpg(process.pid, signal.SIGINT)
        stdout, stderr = process.communicate(timeout=5)
        assert process.returncode != 0, stdout + stderr
        assert time.monotonic() - start <= 5
    finally:
        try:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=2)
        finally:
            process.stdout.close()
            process.stderr.close()
    summary = _read_evidence(out_dir)
    assert summary["status"] == "failed"
    assert summary["stages"][2]["status"] == "not_run"
    stage_evidence, = (out_dir / "exec-01").rglob("*.json")
    terminal = json.loads(stage_evidence.read_text(encoding="utf-8"))
    assert terminal["outcome"] == "cancelled" and terminal["cleanup"] == "verified"


@pytest.mark.skipif(
    _POWERSHELL is None or _PYTHON_EXE is None,
    reason="chain.ps1 requires PowerShell and python.exe",
)
@pytest.mark.parametrize("stale", [False, True])
def test_chain_rejects_zero_exit_without_fresh_index_outputs(isolated_chain, stale):
    chain, raw_dir, out_dir = isolated_chain
    if stale:
        appendix = out_dir / "appendix"
        appendix.mkdir(parents=True)
        for name in ("event_index.md", "theme_index.md", "source_manifest.md"):
            (appendix / name).write_text("previous output", encoding="utf-8")
    result = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir)],
        cwd=raw_dir.parent,
        script=chain,
    )
    assert result.returncode == 5, result.stdout + result.stderr
    evidence = _read_evidence(out_dir)
    assert evidence["status"] == "failed"
    index_stage = evidence["stages"][-1]
    assert index_stage["status"] == "failed"
    assert index_stage["native_exit_code"] == 0
    assert index_stage["outputs"] == []
    assert index_stage["diagnostics"] == ["missing_or_stale_index_artifact"]


@pytest.mark.skipif(
    _POWERSHELL is None or _PYTHON_EXE is None,
    reason="chain.ps1 requires PowerShell and python.exe",
)
@pytest.mark.parametrize("stage_code", range(1, 6))
def test_chain_maps_native_failure_to_operator_code(isolated_chain, stage_code: int) -> None:
    chain, raw_dir, out_dir = isolated_chain
    stage = STAGE_SCRIPTS[stage_code - 1]
    with (chain.parent / f"{stage}.py").open("a", encoding="utf-8") as script:
        script.write("raise SystemExit(23)\n")
    result = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir), "-Verify", "-Verbose"],
        cwd=raw_dir.parent,
        script=chain,
    )
    assert result.returncode == stage_code, result.stdout + result.stderr
    assert "native_exit, exit code 23" in result.stdout
    assert f"WARNING: diagnostic from {stage}" in result.stdout
    assert [name for name in STAGE_SCRIPTS if (raw_dir.parent / name).exists()] == list(
        STAGE_SCRIPTS[:stage_code]
    )
    evidence = _read_evidence(out_dir)
    assert evidence["status"] == "failed"
    assert evidence["exit_code"] == stage_code
    assert [stage["status"] for stage in evidence["stages"]] == (
        ["ok"] * (stage_code - 1) + ["failed"] + ["not_run"] * (5 - stage_code)
    )
    assert evidence["stages"][stage_code - 1]["diagnostics"] == ["native_exit"]
    assert f"diagnostic from {stage}" not in (out_dir / "run.json").read_text(encoding="utf-8")


@pytest.mark.skipif(_POWERSHELL is None, reason="chain.ps1 requires PowerShell")
def test_chain_missing_python_is_launch_failure_with_stale_exit_code(isolated_chain) -> None:
    chain, raw_dir, out_dir = isolated_chain
    result = subprocess.run(
        [_POWERSHELL, "-NoProfile", "-Command",
         "$global:LASTEXITCODE = 23; "
         "& $env:TEST_CHAIN -InputDir $env:TEST_INPUT -OutputDir $env:TEST_OUTPUT; "
         "exit $LASTEXITCODE"],
        cwd=raw_dir.parent,
        env={**os.environ, "PATH": str(raw_dir), "TEST_CHAIN": str(chain),
             "TEST_INPUT": str(raw_dir), "TEST_OUTPUT": str(out_dir)},
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "launch_error" in result.stdout
    python_name = "python.exe" if os.name == "nt" else "'python'"
    assert python_name in result.stdout
    assert "native_exit" not in result.stdout
    assert not (raw_dir.parent / "ingest").exists()
    assert _read_evidence(out_dir)["stages"][0]["diagnostics"] == ["launch_error"]


@pytest.mark.skipif(_POWERSHELL is None, reason="chain.ps1 requires PowerShell")
def test_chain_reports_normalised_directory_collision(isolated_chain) -> None:
    chain, raw_dir, out_dir = isolated_chain
    out_dir.mkdir()
    (out_dir / "normalised").write_text("existing file", encoding="utf-8")
    result = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir)],
        cwd=raw_dir.parent,
        script=chain,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "Ingestion setup failed" in result.stderr
    assert "normalised" in result.stderr
    assert not (raw_dir.parent / "ingest").exists()
    assert _read_evidence(out_dir)["stages"][0]["diagnostics"] == ["stage_setup_error"]


@pytest.mark.skipif(
    _POWERSHELL is None or _PYTHON_EXE is None,
    reason="chain.ps1 requires PowerShell and python.exe",
)
@pytest.mark.parametrize("metadata", ["bad_front_matter", "bad_manifest", "stale_manifest"])
def test_chain_evidence_disregards_bad_artifacts(isolated_chain, metadata: str) -> None:
    chain, raw_dir, out_dir = isolated_chain
    out_dir.mkdir()
    old_summary = out_dir / "run.json"
    old_summary.write_text('{"run_id":"previous"}', encoding="utf-8")
    script = chain.parent / "ingest.py"
    setup = (
        "import sys\n"
        "from pathlib import Path\n"
        "output = Path(sys.argv[sys.argv.index('--output') + 1])\n"
        "assert not (output.parent.parent / 'run.json').exists()\n"
    )
    if metadata == "bad_front_matter":
        behavior = "output.write_text('---\\nevent_count: 4\\nevent_count: bad\\n---\\n')\n"
        expected_exit = 0
    else:
        manifest = '{"manifest_type":"complete","input_file":"input.md",'
        if metadata == "stale_manifest":
            normalized = out_dir / "normalised"
            normalized.mkdir()
            manifest += '"accepted_event_count":20,"rejected_event_count":1,"rejected_events":[{}]}'
            (normalized / "input.rejections.json").write_text(manifest, encoding="utf-8")
            behavior = "raise SystemExit(23)\n"
        else:
            manifest += '"accepted_event_count":true,"rejected_event_count":1,"rejected_events":[{}]}'
            behavior = (
                f"output.with_suffix('.rejections.json').write_text({manifest!r})\n"
                "raise SystemExit(23)\n"
            )
        expected_exit = 1
    script.write_text(setup + behavior, encoding="utf-8")
    result = _run_chain(
        ["-InputDir", str(raw_dir), "-OutputDir", str(out_dir), "-SkipIndex"],
        cwd=raw_dir.parent,
        script=chain,
    )
    assert result.returncode == expected_exit, result.stdout + result.stderr
    evidence = _read_evidence(out_dir)
    assert evidence["run_id"] != "previous"
    (entry,) = evidence["ingest_files"]
    assert entry["accepted"] is None
    assert entry["rejected"] is None
    assert "metadata_unavailable" in entry["diagnostics"]
    assert evidence["stages"][-1]["status"] == "skipped"
    assert not list(out_dir.glob("run.json.*.tmp"))


@pytest.mark.skipif(_POWERSHELL is None, reason="chain.ps1 requires PowerShell")
def test_chain_replaces_summary_on_input_preflight_failure(isolated_chain) -> None:
    chain, raw_dir, out_dir = isolated_chain
    out_dir.mkdir()
    (out_dir / "run.json").write_text('{"run_id":"previous"}', encoding="utf-8")
    result = _run_chain(
        ["-InputDir", str(raw_dir / "missing"), "-OutputDir", str(out_dir)],
        cwd=raw_dir.parent,
        script=chain,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    evidence = _read_evidence(out_dir)
    assert evidence["run_id"] != "previous"
    assert evidence["exit_code"] == 1
    assert evidence["status"] == "failed"
    assert evidence["ingest_files"] == []
    assert evidence["merge_inputs"] == []
    assert [stage["status"] for stage in evidence["stages"]] == [
        "failed", "skipped", "not_run", "not_run", "not_run",
    ]
