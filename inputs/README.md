# Canonical Corpus Inputs

This directory contains source documents consumed by project pipelines. Inputs
are grouped as `inputs/<corpus>/<format>/<filename>` and registered in
`catalog.json` with byte size, SHA-256, and provenance classification.

- `chatgpt-chronicle/markdown/`: the established 16-file, 224-event corpus.
- `insurancechatbot/markdown/`: the three sources consumed by its topic adapter.
- Future source DOCX files belong in `inputs/<corpus>/docx/` and must be added to
  the catalog. No source DOCX is currently present.

Project documentation does not belong here. Generated DOCX reports belong in
`_WORK/generated-reports/`, or in `_ARCHIVE/evidence/` when deliberately
curated. Run `python tools/check_input_catalog.py --root .` after any intentional
input addition or replacement.
