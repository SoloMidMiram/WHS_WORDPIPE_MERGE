"""Bounded execution policy and evidence for Chronicle native stages."""

from __future__ import annotations

import json
import math
import os
import signal
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable


MAX_CAPTURE = 1 << 20
CLEANUP_BUDGET = 5.0
_CONTEXT_ENV = "WORDPIPE_EXECUTION_OWNER"
_POLL_SECONDS = 0.01


class Outcome(str, Enum):
    SUCCESS = "success"
    NATIVE_FAILURE = "native_failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    LAUNCH_FAILURE = "launch_failure"
    CLEANUP_FAILURE = "cleanup_failure"


class Cleanup(str, Enum):
    NOT_STARTED = "not_started"
    VERIFIED = "verified"
    INHERITED = "outer_owner"
    UNVERIFIED = "unverified"


@dataclass
class Cancellation:
    """One-shot request on the same monotonic clock as the supervisor."""

    clock: Callable[[], float] = time.monotonic
    requested_at: float | None = field(default=None, init=False)

    def request(self) -> None:
        if self.requested_at is None:
            self.requested_at = self.clock()


@dataclass(frozen=True)
class Ownership:
    """Inherited kernel boundary and absolute deadline supplied by the owner."""

    group: int | str
    deadline: float | None


@dataclass(frozen=True)
class ExecutionPolicy:
    timeout: float | None = None
    cleanup_grace: float = 0.5
    stdout_limit: int = MAX_CAPTURE
    stderr_limit: int = MAX_CAPTURE
    cancellation: Cancellation | None = None
    inherited: Ownership | None = None

    def __post_init__(self) -> None:
        if self.timeout is not None and not (
            type(self.timeout) in (int, float) and math.isfinite(self.timeout) and self.timeout > 0
        ):
            raise ValueError("execution timeout must be finite and positive")
        if not (type(self.cleanup_grace) in (int, float) and math.isfinite(self.cleanup_grace)
                and 0 <= self.cleanup_grace < CLEANUP_BUDGET):
            raise ValueError("cleanup grace must be nonnegative and less than five seconds")
        if any(type(limit) is not int or not 0 <= limit <= MAX_CAPTURE
               for limit in (self.stdout_limit, self.stderr_limit)):
            raise ValueError("stream retention limits must be integers between zero and 1 MiB")
        if self.inherited is not None and self.timeout is not None:
            raise ValueError("inherited execution uses the enclosing deadline")


@dataclass(frozen=True)
class Capture:
    retained: bytes = b""
    observed: int = 0

    @property
    def truncated(self) -> bool:
        return self.observed > len(self.retained)

    def evidence(self) -> dict:
        return {
            "retained_bytes": len(self.retained),
            "observed_bytes": self.observed,
            "truncated": self.truncated,
        }

    def text(self, limit: int = MAX_CAPTURE) -> str:
        # Replacement characters can expand malformed UTF-8. Keep the
        # serialized UTF-8 diagnostic within the original retention bound.
        data = self.retained.decode("utf-8", "replace").encode("utf-8")
        return data[:limit].decode("utf-8", "ignore").replace("\r\n", "\n").replace("\r", "\n")


@dataclass(frozen=True)
class ExecutionResult:
    outcome: Outcome
    trigger: Outcome
    native_code: int | None
    elapsed: float
    stdout: Capture = Capture()
    stderr: Capture = Capture()
    cleanup: Cleanup = Cleanup.NOT_STARTED
    detail: str | None = None
    exited_records: int = 0

    @property
    def exit_code(self) -> int:
        if self.outcome == Outcome.SUCCESS:
            return 0
        if self.outcome == Outcome.NATIVE_FAILURE:
            assert self.native_code
            return self.native_code
        return {
            Outcome.TIMEOUT: 124,
            Outcome.CANCELLED: 130,
            Outcome.LAUNCH_FAILURE: 125,
            Outcome.CLEANUP_FAILURE: 125,
        }[self.outcome]

    def evidence(self) -> dict:
        return {
            "schema": "exec-01-v1", "outcome": self.outcome.value, "trigger": self.trigger.value,
            "native_exit_code": self.native_code, "exit_code": self.exit_code,
            "elapsed_seconds": self.elapsed, "stdout": self.stdout.evidence(),
            "stderr": self.stderr.evidence(), "cleanup": self.cleanup.value,
            "detail": self.detail, "exited_process_records": self.exited_records,
        }


def write_terminal_evidence(path: Path, result: ExecutionResult, policy: ExecutionPolicy) -> None:
    record = result.evidence()
    record["policy"] = {
        "timeout_seconds": policy.timeout,
        "cleanup_budget_seconds": CLEANUP_BUDGET,
        "cleanup_grace_seconds": policy.cleanup_grace,
        "stdout_limit": policy.stdout_limit,
        "stderr_limit": policy.stderr_limit,
        "ownership": "inherited" if policy.inherited else "owned",
        "has_deadline": policy.timeout is not None or (
            policy.inherited is not None and policy.inherited.deadline is not None
        ),
    }
    with path.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=True)
        handle.write("\n")


def select_trigger(
    completed_at: float | None, cancelled_at: float | None, deadline: float | None,
    now: float, native_code: int | None,
) -> tuple[Outcome, float] | None:
    """Pick the earliest observed event, with cancellation winning ties."""
    candidates = (
        (cancelled_at, Outcome.CANCELLED),
        (deadline, Outcome.TIMEOUT),
        (completed_at, Outcome.NATIVE_FAILURE if native_code else Outcome.SUCCESS),
    )
    observed = [(stamp, outcome) for stamp, outcome in candidates if stamp is not None and stamp <= now]
    if not observed:
        return None
    stamp, outcome = min(observed, key=lambda event: event[0])
    return outcome, stamp


def _backend():
    if sys.platform == "win32":
        from wordpipe import _execution_windows

        return _execution_windows
    if sys.platform == "linux":
        from wordpipe import _execution_posix

        return _execution_posix
    raise ValueError("owned execution is supported on Windows and Linux")


def inherited_context() -> Ownership | None:
    """Validate the reported context against the current kernel membership."""
    value = os.environ.get(_CONTEXT_ENV)
    if value is None:
        return None
    if len(value) > 512:
        raise ValueError("invalid inherited execution context")
    record = json.loads(value)
    if not isinstance(record, dict):
        raise ValueError("invalid inherited execution context")
    pid, token, deadline = record.get("issuer"), record.get("token"), record.get("deadline")
    if (type(pid) is not int or pid <= 0 or not isinstance(token, str)
            or (deadline is not None and (
                type(deadline) not in (float, int) or not math.isfinite(deadline) or deadline <= 0
            ))):
        raise ValueError("invalid inherited execution context")
    return Ownership(_backend().verify_inherited(pid, token), deadline)


@contextmanager
def _interrupts(cancellation):
    previous = {}
    if cancellation is not None and threading.current_thread() is threading.main_thread():
        signals = [signal.SIGINT, signal.SIGTERM]
        if hasattr(signal, "SIGBREAK"):
            signals.append(signal.SIGBREAK)
        for signum in signals:
            previous[signum] = signal.signal(signum, lambda *_: cancellation.request())
    try:
        yield
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)


def execute(argv: list[str], policy: ExecutionPolicy = ExecutionPolicy(), *, publish_owner: bool = False) -> ExecutionResult:
    """Run one stage and report only its single terminal transition."""
    cancel = None if policy.inherited else policy.cancellation or Cancellation()
    with _interrupts(cancel):
        return _execute(argv, policy, cancel, publish_owner)


def _execute(argv, policy, cancel, publish_owner):
    started = time.monotonic()
    inherited = policy.inherited
    deadline = inherited.deadline if inherited else (
        None if policy.timeout is None else started + policy.timeout
    )
    first = select_trigger(None, cancel.requested_at if cancel else None, deadline, started, None)
    if first:
        return ExecutionResult(first[0], first[0], None, 0.)
    token = f"Local\\WordPipe-EXEC01-{uuid.uuid4().hex}" if sys.platform == "win32" else "linux-session"
    env = os.environ.copy()
    if not inherited:
        env.pop(_CONTEXT_ENV, None)
        if publish_owner:
            env[_CONTEXT_ENV] = json.dumps({"issuer": os.getpid(), "token": token, "deadline": deadline})
    elif sys.platform == "win32":
        token = str(inherited.group)
    try:
        process = _backend().Process(argv, env, inherited is not None, token)
    except (OSError, ValueError, RuntimeError) as exc:
        now = time.monotonic()
        stop = select_trigger(None, cancel.requested_at if cancel else None, deadline, now, None)
        trigger = stop[0] if stop else Outcome.LAUNCH_FAILURE
        uncertain = isinstance(exc, RuntimeError)
        return ExecutionResult(
            Outcome.CLEANUP_FAILURE if uncertain else trigger, trigger, None, now - started,
            cleanup=Cleanup.UNVERIFIED if uncertain else Cleanup.NOT_STARTED, detail=str(exc)[:512],
        )
    return _supervise(process, policy, cancel, started, deadline)


def _supervise(process, policy, cancel, started, deadline):
    buffers = [bytearray(), bytearray()]
    observed = [0, 0]
    ended = [False, False]
    limits = [policy.stdout_limit, policy.stderr_limit]
    native = None
    terminal = None
    force_sent = False
    term_sent = False
    exited_records = 0
    detail = None
    cleanup = Cleanup.UNVERIFIED
    try:
        while True:
            activity = False
            now = time.monotonic()
            if terminal is not None and now >= terminal[1] + CLEANUP_BUDGET:
                detail = detail or "absolute cleanup deadline reached before verification"
                break
            try:
                for index, stream in enumerate(process.streams):
                    if ended[index]:
                        continue
                    chunk = process.read(stream, 65536)
                    if chunk is None:
                        continue
                    activity = True
                    if not chunk:
                        ended[index] = True
                        continue
                    observed[index] += len(chunk)
                    buffers[index].extend(chunk[:limits[index] - len(buffers[index])])

                native = process.code()
                remaining, exited_records = process.remaining() if native is not None else (1, 0)
                now = time.monotonic()
                verified = remaining == 0 and all(ended)
                if terminal is None:
                    terminal = select_trigger(
                        now if verified else None,
                        cancel.requested_at if cancel else None, deadline, now, native,
                    )
                if terminal is not None and verified and now <= terminal[1] + CLEANUP_BUDGET:
                    cleanup = Cleanup.INHERITED if policy.inherited else Cleanup.VERIFIED
                    break
            except (OSError, ValueError) as exc:
                now = time.monotonic()
                detail = str(exc)[:512]
                if terminal is None:
                    terminal = select_trigger(
                        None, cancel.requested_at if cancel else None, deadline, now, native,
                    ) or (Outcome.CLEANUP_FAILURE, now)
                # A failed read/query cannot establish successful cleanup.
                ended = [True, True]

            if terminal is not None:
                if policy.inherited:
                    cleanup = Cleanup.INHERITED
                    break
                force = now >= terminal[1] + policy.cleanup_grace
                if (force and not force_sent) or (not force and not term_sent):
                    force_sent |= force
                    term_sent = True
                    try:
                        process.stop(force)
                    except OSError as exc:
                        detail = str(exc)[:512]
            if not activity:
                time.sleep(_POLL_SECONDS)
    finally:
        try:
            process.close(native is not None)
        except (OSError, ValueError) as exc:
            cleanup = Cleanup.UNVERIFIED
            detail = str(exc)[:512]

    trigger = terminal[0]
    if detail is not None and cleanup != Cleanup.INHERITED:
        cleanup = Cleanup.UNVERIFIED
    outcome = Outcome.CLEANUP_FAILURE if cleanup == Cleanup.UNVERIFIED else trigger
    return ExecutionResult(
        outcome, trigger, native, time.monotonic() - started,
        Capture(bytes(buffers[0]), observed[0]), Capture(bytes(buffers[1]), observed[1]),
        cleanup, detail, exited_records,
    )
