from __future__ import annotations

import argparse
import sys
from pathlib import Path

from wordpipe.core.datatypes import PipelineConfig
from wordpipe.orchestrator import process_docx_v3


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wordpipe")
    parser.add_argument("--in", dest="in_path", required=True, help="Input .docx path")
    parser.add_argument("--out", dest="out_path", required=True, help="Output .docx path")
    parser.add_argument(
        "--flatten",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Run the flatten step (requires the legacy MergedpipelineV3 module).",
    )
    parser.add_argument(
        "--prefer-win32",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Prefer win32 flattener/TOC updater when available.",
    )
    args = parser.parse_args(argv)

    # P0.6: Guard against identical input and output paths.
    in_resolved = Path(args.in_path).resolve()
    out_resolved = Path(args.out_path).resolve()
    if in_resolved == out_resolved:
        parser.error(f"--in and --out must differ, both resolve to {in_resolved}")

    cfg = PipelineConfig(
        in_path=in_resolved,
        out_path=out_resolved,
        do_flatten=args.flatten,
        prefer_win32=args.prefer_win32,
    )
    rep = process_docx_v3(cfg)
    if rep.errors:
        for err in rep.errors:
            print(f"Pipeline error: {err}", file=sys.stderr)
        return 1
    print(f"Written {rep.out_path} — {len(rep.notes)} notes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
