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
    parser.add_argument("--timeout", type=float)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("argv", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    argv = args.argv[1:] if args.argv and args.argv[0] == "--" else args.argv
    if not argv:
        parser.error("a command is required")
    try:
        policy = ExecutionPolicy(timeout=args.timeout, inherited=inherited_context())
    except (OSError, ValueError) as exc:
        policy = ExecutionPolicy()
        result = ExecutionResult(Outcome.LAUNCH_FAILURE, Outcome.LAUNCH_FAILURE, None, 0.,
                                 detail=str(exc)[:512])
    else:
        result = execute(argv, policy)
    write_terminal_evidence(args.evidence, result, policy)
    print(json.dumps({
        **result.evidence(), "stdout_text": result.stdout.text(), "stderr_text": result.stderr.text(),
    }, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
