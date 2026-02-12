"""
docx_to_md_converter.py
=======================

This module provides a small command‑line utility to convert one or more
Microsoft Word documents (`.docx`) into Markdown files.  It relies on the
Pandoc command line tool, which must already be available on the system.

The converter performs the following steps for each input document:

* **Pandoc Conversion** – Calls `pandoc` with the `gfm` (GitHub Flavored
  Markdown) output format.  This preserves headings (`#`, `##`, etc.),
  bold/italic formatting, lists, code blocks and tables.  An `--extract-media`
  option tells Pandoc to dump any embedded images into a dedicated
  subdirectory under `media/` named after the input file.  Pandoc’s
  documentation notes that converting DOCX to Markdown using `pandoc` will
  preserve headings, bold/italic text, lists, tables and images【107362646330212†L54-L64】.

* **Table of Contents removal** – If the generated Markdown contains a
  “Table of Contents” section, it is stripped out.  The removal looks for a
  heading containing the words “Table of Contents” (case‑insensitive) and
  discards all lines until the next top‑level heading.

* **Output** – The cleaned Markdown is written to a file alongside the input
  document (with a `.md` extension).  Embedded images live in
  `media/<basename>/` relative to the output Markdown.

You can optionally combine the output of multiple conversions into a single
Markdown file by specifying a `--combine` flag.  When combining, each
converted document is prefaced by an H1 heading with the original file name.

Example usage:

    python docx_to_md_converter.py MERGE\ 1\ 14040816.docx "Agent mode investigation rep 0910.docx" --combine

This will produce `MERGE_1_14040816.md`, `Agent_mode_investigation_rep_0910.md`,
and a `combined_report.md` in the current directory, extracting images into
`media/MERGE_1_14040816/` and `media/Agent_mode_investigation_rep_0910/`.
"""

import argparse
import os
import re
import subprocess
from pathlib import Path
from typing import List


def run_pandoc(docx_path: Path, md_path: Path, media_dir: Path) -> None:
    """Convert a .docx file to Markdown using pandoc.

    Parameters
    ----------
    docx_path : Path
        Location of the input Word document.
    md_path : Path
        Where to write the raw Markdown output.
    media_dir : Path
        Directory in which to store extracted media files.  Pandoc will
        populate this directory with images referenced from the document.
    """
    # Ensure the media directory exists
    media_dir.mkdir(parents=True, exist_ok=True)

    # Prepare the pandoc command.  We request GitHub Flavored Markdown (gfm)
    # because it uses pipe tables and preserves formatting well.  Use
    # --extract-media to dump images into the media directory.
    cmd = [
        "pandoc",
        str(docx_path),
        "-t",
        "gfm",
        "--extract-media",
        str(media_dir),
        "-o",
        str(md_path),
    ]

    # Execute pandoc.  Capture output to surface errors if conversion fails.
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Pandoc failed for {docx_path} with exit code {result.returncode}:\n{result.stderr}"
        )


def remove_table_of_contents(lines: List[str]) -> List[str]:
    """Remove a table of contents section from a list of Markdown lines.

    This function searches for a heading containing the words "Table of Contents"
    (case insensitive).  Once found, it drops that line and all following lines
    until the next top‑level heading (one that starts with '# ').

    Parameters
    ----------
    lines : List[str]
        The raw lines of a Markdown file.

    Returns
    -------
    List[str]
        Lines with any table of contents removed.
    """
    output = []
    in_toc = False
    toc_pattern = re.compile(r"^#+\s+Table of Contents", re.IGNORECASE)
    for line in lines:
        if not in_toc:
            # Check if this line begins the TOC
            if toc_pattern.match(line.strip()):
                in_toc = True
                continue
            else:
                output.append(line)
        else:
            # We are inside the TOC; look for the next top-level heading
            if re.match(r"^#\s", line):
                # End of TOC; include this heading and resume normal copying
                output.append(line)
                in_toc = False
    return output


def clean_markdown(md_path: Path) -> None:
    """Remove Table of Contents from a Markdown file in place."""
    text = md_path.read_text(encoding="utf-8").splitlines(True)  # keep newline characters
    cleaned = remove_table_of_contents(text)
    md_path.write_text("".join(cleaned), encoding="utf-8")


def convert_files(docx_files: List[Path], combine: bool) -> None:
    """Convert multiple docx files to Markdown, optionally combining results.

    Parameters
    ----------
    docx_files : List[Path]
        List of input Word documents to convert.
    combine : bool
        If True, write a combined report.  Each individual Markdown is still
        produced regardless of this flag.
    """
    md_paths = []
    for docx_path in docx_files:
        if not docx_path.is_file():
            raise FileNotFoundError(f"File not found: {docx_path}")
        # Normalize names: replace spaces with underscores for folder names
        base_name = docx_path.stem.replace(" ", "_")
        md_file = Path(f"{base_name}.md")
        # Use a media directory under the current working directory
        media_dir = Path("media") / base_name
        # Run pandoc to convert to Markdown and extract images
        run_pandoc(docx_path, md_file, media_dir)
        # Clean up any TOC sections
        clean_markdown(md_file)
        md_paths.append((md_file, base_name))

    if combine and md_paths:
        combined_path = Path("combined_report.md")
        with combined_path.open("w", encoding="utf-8") as out_f:
            for md_file, base_name in md_paths:
                # Write a header for each file
                out_f.write(f"# {base_name}\n\n")
                content = md_file.read_text(encoding="utf-8")
                out_f.write(content)
                out_f.write("\n\n")
        print(f"Combined report written to {combined_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert .docx files to Markdown using pandoc."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="One or more .docx files to convert",
    )
    parser.add_argument(
        "--combine",
        action="store_true",
        help="Combine all converted files into a single combined_report.md",
    )
    args = parser.parse_args()
    # Convert to Path objects
    docx_files = [Path(f) for f in args.files]
    convert_files(docx_files, args.combine)


if __name__ == "__main__":
    main()