"""PowerShell bridge for one bounded native Chronicle stage."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wordpipe.execution import (
    ExecutionPolicy, ExecutionResult, Outcome, execute, inherited_context, write_terminal_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    argv = request["argv"]
    if not argv:
        parser.error("a command is required")
    try:
        policy = ExecutionPolicy(timeout=request["timeout"], inherited=inherited_context())
    except (OSError, ValueError) as exc:
        policy = ExecutionPolicy()
        result = ExecutionResult(Outcome.LAUNCH_FAILURE, Outcome.LAUNCH_FAILURE, None, 0.,
                                 detail=str(exc)[:512])
    else:
        result = execute(argv, policy)
    write_terminal_evidence(Path(request["evidence"]), result, policy)
    with Path(request["response"]).open("x", encoding="utf-8") as response:
        json.dump({
            **result.evidence(), "stdout_text": result.stdout.text(), "stderr_text": result.stderr.text(),
        }, response, ensure_ascii=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
