# Pipeline Chronicle Topic

**Purpose:** Second topic for Phase 14 multi-topic ontology readiness.

This topic processes the archived chronicle-pipeline planning documents
from `_ARCHIVE/pipeline-chronicle/` through the generic Markdown-section
adapter (`tools/prepare_generic_markdown_chronicle.py`). The source files
are read-only — they stay in their archive location.

## Source

`_ARCHIVE/pipeline-chronicle/` — 5 long `.md` files:
- `README.md` — overview and tool inventory of the original chronicle tools
- `ARCHIVE_REPORT.md` — record of archival after Phase 9b refactor
- `ROADMAP.md` — implementation roadmap for the chronicle tools
- `PIPELINE_PLAN.md` — detailed pipeline plan with stages and priorities
- `REVIEW_PLAN.md` — review checklist for each tool

## Adapter

`tools/prepare_generic_markdown_chronicle.py` (generic, stdlib-only):
- Splits each `.md` file at `##` headings into Chronicle events
- Extracts ISO dates from section text (fallback to document date)
- Prefixes event titles with a source file label to avoid merge collisions

## Commands

```powershell
python tools\run_topic_report.py `
  --manifest WordHorrorStories\pipelinechronicle\topic_manifest.json `
  --run-id <run_id>
```
