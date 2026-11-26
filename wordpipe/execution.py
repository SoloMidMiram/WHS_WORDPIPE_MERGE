"""Bounded execution policy and evidence for Chronicle native stages."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


MAX_CAPTURE = 1 << 20
CLEANUP_BUDGET = 5.0


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
    INHERITED = "verified_by_outer_owner"
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
