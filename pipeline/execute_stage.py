"""PowerShell bridge for one bounded native Chronicle stage."""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from runpy import run_path


def _write_response(request, evidence, stdout="", stderr=""):
    with Path(request["response"]).open("x", encoding="utf-8") as response:
        json.dump({**evidence, "stdout_text": stdout, "stderr_text": stderr}, response, ensure_ascii=True)


def _record_rejected_launch(request, detail, elapsed):
    # Match the existing pre-launch terminal record without importing an
    # executor whose origin has just failed verification.
    empty = {"retained_bytes": 0, "observed_bytes": 0, "truncated": False}
    evidence = {
        "schema": "exec-01-v1", "outcome": "launch_failure", "trigger": "launch_failure",
        "native_exit_code": None, "exit_code": 125, "elapsed_seconds": elapsed,
        "stdout": empty, "stderr": empty, "cleanup": "not_started",
        "detail": detail[:512], "exited_process_records": 0,
    }
    with Path(request["evidence"]).open("x", encoding="utf-8") as handle:
        json.dump(evidence, handle, ensure_ascii=True)
        handle.write("\n")
    _write_response(request, evidence)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    argv = request["argv"]
    if not argv:
        parser.error("a command is required")
    if "WORDPIPE_ORIGIN_QUALIFICATION" in os.environ:
        started = time.monotonic()
        try:
            run_path(str(Path(__file__).with_name("_import_origin.py")))["require_driver"](
                __file__, "wordpipe.execution",
            )
        except (OSError, SystemExit) as exc:
            detail = f"CI-01: bridge verifier unavailable: {exc}" if isinstance(exc, OSError) else str(exc)
            _record_rejected_launch(request, detail, time.monotonic() - started)
            return 0  # The transport delivered a failed stage record.
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from wordpipe.execution import (
        ExecutionPolicy, ExecutionResult, Outcome, execute, inherited_context, write_terminal_evidence,
    )

    try:
        policy = ExecutionPolicy(timeout=request["timeout"], inherited=inherited_context())
    except (OSError, ValueError) as exc:
        policy = ExecutionPolicy()
        result = ExecutionResult(Outcome.LAUNCH_FAILURE, Outcome.LAUNCH_FAILURE, None, 0.,
                                 detail=str(exc)[:512])
    else:
        result = execute(argv, policy)
    write_terminal_evidence(Path(request["evidence"]), result, policy)
    _write_response(request, result.evidence(), result.stdout.text(), result.stderr.text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
