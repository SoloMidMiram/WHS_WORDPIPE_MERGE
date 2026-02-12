
# autobiography/cli.py
from __future__ import annotations

import argparse
from pathlib import Path

from .config import ChronicleConfig, DocxConfig
from .log_reader import LogFileReader
from .collection import LogCollection
from .docx_builder import builder_for_config

def parse_args() -> ChronicleConfig:
    parser = argparse.ArgumentParser(description="Build a Coding Autobiography from Codex/Continue logs.")
    parser.add_argument("input_jsonl", nargs="+", help="One or more JSONL log files")
    parser.add_argument("output_docx", help="Destination DOCX file")
    parser.add_argument(
        "--group-by",
        default="jalali_date",
        help="Field or LogEntry method to group entries by (default: jalali_date)",
    )
    parser.add_argument(
        "--layout",
        choices=["single_column", "two_column"],
        default="single_column",
        help="Docx layout (single_column or two_column).",
    )
    args = parser.parse_args()
    return ChronicleConfig(
        input_paths=[Path(p) for p in args.input_jsonl],
        output_docx=Path(args.output_docx),
        group_field=args.group_by,
        layout=args.layout,
    )

def main() -> None:
    cli_cfg = parse_args()
    reader = LogFileReader(cli_cfg.input_paths)
    collection = LogCollection(reader).unique().sort_by_iso()
    grouped = collection.group_by(cli_cfg.group_field)
    docx_cfg = DocxConfig(layout=cli_cfg.layout)
    builder = builder_for_config(docx_cfg)
    builder.save(grouped, cli_cfg.output_docx)
    total = sum(len(v) for v in grouped.values())
    print(f"Written {total} entries into {cli_cfg.output_docx}")

if __name__ == "__main__":
    main()
