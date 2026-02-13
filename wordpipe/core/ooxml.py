"""OOXML helpers (dependency-light).

This module intentionally avoids non-stdlib XML dependencies (for example lxml)
so that `import wordpipe` and `import wordpipe.core` remain lightweight.
"""

from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET

_XML10_BAD = re.compile(r"[^\u0009\u000A\u000D\u0020-\uD7FF\uE000-\uFFFD]")

# WordprocessingML namespace used in .docx word/document.xml
_W_URI = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_W = f"{{{_W_URI}}}"


def xml_safe(s: str | None) -> str:
    if not s:
        return ""
    s = s.replace("\x00", " ").replace("\x0b", " ")
    return _XML10_BAD.sub(" ", s)


def open_document_xml(docx_path: str) -> ET.Element:
    with zipfile.ZipFile(docx_path, "r") as z:
        xml = z.read("word/document.xml")
    return ET.fromstring(xml)


def find_xml_boundaries(docx_path: str) -> list[int]:
    root = open_document_xml(docx_path)
    paras = root.findall(f".//{_W}body/{_W}p")
    cuts = {0}
    last_idx = max(0, len(paras) - 1)

    for i, p in enumerate(paras):
        ppr = p.find(f"{_W}pPr")
        if ppr is not None:
            if ppr.find(f"{_W}sectPr") is not None:
                cuts.add(i)
            if ppr.find(f"{_W}pageBreakBefore") is not None:
                cuts.add(i)

        for br in p.findall(f".//{_W}br"):
            if br.get(f"{_W}type") == "page":
                cuts.add(min(i + 1, last_idx))

    return sorted(cuts)
