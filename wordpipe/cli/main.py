from __future__ import annotations

import argparse

from wordpipe import process_docx_v3_simple


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wordpipe")
    parser.add_argument("--in", dest="in_path", required=True, help="Input .docx path")
    parser.add_argument("--out", dest="out_path", required=True, help="Output .docx path")
    parser.add_argument("--no-flatten", action="store_true", help="Disable flatten step")
    parser.add_argument(
        "--prefer-win32",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Prefer win32 flattener/TOC updater when available.",
    )
    args = parser.parse_args(argv)

    process_docx_v3_simple(
        in_path=args.in_path,
        out_path=args.out_path,
        do_flatten=not args.no_flatten,
        prefer_win32=args.prefer_win32,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
