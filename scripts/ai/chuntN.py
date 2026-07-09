# file: wordpipe/core/chunkN.py
from __future__ import annotations
from pathlib import Path
from docx import Document
from chunker import chunk_ranges_by_page_breaks

FILENAME = "Modular word pipeline.docx"


def resolve_docx(filename=FILENAME) -> Path:
    here = Path(__file__).resolve()
    # project root = two levels up from wordpipe/<subdir>/script.py
    proj = here.parents[2] if "wordpipe" in here.parts else here.parent

    candidates = [
        proj / "data" / filename,
        proj / "data" / "inputs" / filename,
        Path(filename),  # as-given
        proj / filename,  # at root
    ]
    for c in candidates:
        if c.exists():
            return c

    # last resort: search under project
    for p in proj.rglob("*.docx"):
        if p.name.lower() == filename.lower():
            return p

    raise FileNotFoundError(f"Could not find {filename} under {proj}")


def main():
    docx_path = resolve_docx()
    doc = Document(str(docx_path))
    chunks = chunk_ranges_by_page_breaks(doc)
    print(f"Resolved: {docx_path}")
    print(f"Chunks: {len(chunks)}")
    print(f"Manual page breaks: {len(chunks) - 1}")


if __name__ == "__main__":
    main()
