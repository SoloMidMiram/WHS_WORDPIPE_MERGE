"""python-docx based implementations (optional extra: `wordpipe[docx]`)."""

from wordpipe.adapters.docx.io import DocxDocumentReader, DocxDocumentWriter
from wordpipe.adapters.docx.segmenter import DocxSegmenter
from wordpipe.adapters.docx.styler import DocxStyler

__all__ = ["DocxDocumentReader", "DocxDocumentWriter", "DocxSegmenter", "DocxStyler"]

