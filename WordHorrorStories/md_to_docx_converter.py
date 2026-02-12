"""
md_to_docx_converter.py
=======================

Tiny helper to turn a Markdown file back into a Word (.docx) document
using Pandoc. It is the inverse of `docx_to_md_converter.py` and is
useful when you want to edit the generated Markdown by hand and render
it into a nicely headed Word document.
"""

import argparse
import subprocess
from pathlib import Path
from typing import Optional


def run_pandoc(md_path: Path, docx_path: Path, reference_doc: Optional[Path]) -> None:
    """
    Convert a Markdown file to a DOCX using Pandoc.
    """
    cmd = [
        "pandoc",
        str(md_path),
        "-f",
        "gfm",
        "-t",
        "docx",
        "--standalone",
        "--resource-path",
        str(md_path.parent),
        "-o",
        str(docx_path),
    ]

    if reference_doc:
        cmd.extend(["--reference-doc", str(reference_doc)])

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Pandoc failed for {md_path} with exit code {result.returncode}:\n{result.stderr}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Markdown to DOCX using Pandoc.")
    parser.add_argument("file", help="Input Markdown file (GitHub-flavored).")
    parser.add_argument(
        "-o",
        "--output",
        help="Output DOCX path. Defaults to the Markdown stem with .docx.",
    )
    parser.add_argument(
        "--reference-doc",
        help="Optional reference DOCX for styling (Pandoc template).",
    )
    args = parser.parse_args()

    md_path = Path(args.file)
    if not md_path.is_file():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    docx_path = Path(args.output) if args.output else md_path.with_suffix(".docx")
    reference_doc = Path(args.reference_doc) if args.reference_doc else None

    run_pandoc(md_path, docx_path, reference_doc)
    print(f"Wrote DOCX to {docx_path}")


if __name__ == "__main__":
    main()
