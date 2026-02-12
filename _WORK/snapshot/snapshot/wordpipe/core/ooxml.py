# ==============================
# file: wordpipe/core/ooxml.py
# ==============================
import re, zipfile
from lxml import etree

_XML10_BAD = re.compile(r"[^\u0009\u000A\u000D\u0020-\uD7FF\uE000-\uFFFD]")


def xml_safe(s: str | None) -> str:
    if not s:
        return ""
    s = s.replace("\x00", " ").replace("\x0b", " ")
    return _XML10_BAD.sub(" ", s)


def open_document_xml(docx_path: str) -> etree._Element:
    with zipfile.ZipFile(docx_path, "r") as z:
        xml = z.read("word/document.xml")
    return etree.fromstring(xml)


def find_xml_boundaries(docx_path: str) -> list[int]:
    root = open_document_xml(docx_path)
    ns = root.nsmap
    paras = root.findall(".//w:body/w:p", namespaces=ns)
    cuts = {0}
    for i, p in enumerate(paras):
        if p.find(".//w:pPr/w:sectPr", namespaces=ns) is not None:
            cuts.add(i)
        if p.find(".//w:pPr/w:pageBreakBefore", namespaces=ns) is not None:
            cuts.add(i)
        for r in p.findall(".//w:r", namespaces=ns):
            for br in r.findall(".//w:br", namespaces=ns):
                if br.get(f"{{{ns['w']}}}type") == "page":
                    cuts.add(min(i + 1, len(paras) - 1))
    return sorted(cuts)
