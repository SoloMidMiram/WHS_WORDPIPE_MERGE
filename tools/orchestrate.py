"""Run the documented workspace pipeline in one command."""

import argparse
import os
import subprocess
import sys


def command_to_text(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def run_or_exit(command: list[str], dry_run: bool, cwd: str) -> None:
    command_text = command_to_text(command)
    print(command_text, flush=True)
    if dry_run:
        return
    completed = subprocess.run(command, cwd=cwd)
    if completed.returncode != 0:
        print(
            f"ERROR: command failed with exit code {completed.returncode}: {command_text}",
            file=sys.stderr,
        )
        raise SystemExit(completed.returncode)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="Workspace root used as subprocess cwd for all stages.",
    )
    parser.add_argument(
        "--root",
        default="_WORK/snapshot",
        help="Snapshot root passed through to root-aware stages.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned commands without executing any stage.",
    )
    parser.add_argument(
        "--run-route-unmapped",
        action="store_true",
        help="Run tools/route_unmapped_misc.py after apply_legacy_reorg.py.",
    )
    args = parser.parse_args()
    workspace_root = os.path.abspath(args.workspace_root)

    commands = [
        ["python", "tools/make_manifest.py", "--root", args.root],
        ["python", "tools/plan_legacy_reorg.py", "--root", args.root],
        ["python", "tools/apply_legacy_reorg.py", "--root", args.root],
    ]
    if args.run_route_unmapped:
        commands.append(["python", "tools/route_unmapped_misc.py", "--root", args.root])
    commands.extend(
        [
            ["python", "tools/build_legacy_index.py"],
            ["python", "tools/verify_integrity.py", "--snapshot-root", args.root, "--strict"],
        ]
    )

    for command in commands:
        run_or_exit(command, args.dry_run, workspace_root)


if __name__ == "__main__":
    main()
