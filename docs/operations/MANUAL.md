# Operations Manual

## Quickstart (Tools Evidence Pipeline)
From repo root:

```powershell
python tools/orchestrate.py --root _WORK/snapshot
```

Dry-run (prints commands only, no writes):

```powershell
python tools/orchestrate.py --root _WORK/snapshot --dry-run
```

Stage-by-stage:

```powershell
python tools/make_manifest.py --workspace-root . --root _WORK/snapshot
python tools/plan_legacy_reorg.py --workspace-root . --root _WORK/snapshot
python tools/apply_legacy_reorg.py --workspace-root . --root _WORK/snapshot
python tools/build_legacy_index.py --workspace-root .
python tools/verify_integrity.py --workspace-root . --snapshot-root _WORK/snapshot
```

## Quickstart (WordPipe CLI)
Install (editable) with docx extras:

```powershell
python -m pip install -e ".[docx,cli]"
```

Run:

```powershell
wordpipe --in "input.docx" --out "output.docx"
```

## Tools Pipeline: Inputs/Outputs and Where Evidence Lives
Inputs:
- Snapshot root: `_WORK/snapshot` (treat as immutable input)

Primary outputs:
- Manifest:
  - `_ARCHIVE/manifests/manifest.jsonl`
  - `_ARCHIVE/manifests/manifest.csv`
- Relocation plan/map:
  - `_ARCHIVE/move_maps/relocation_plan.jsonl`
  - `_ARCHIVE/move_maps/relocation_map.jsonl`
- Logs and reports:
  - `_ARCHIVE/logs/conflicts.log` (append-only)
  - `_ARCHIVE/logs/verify_report.md` (replace-on-run)
  - `_ARCHIVE/logs/verify_report.json` (replace-on-run)
  - `_ARCHIVE/logs/consistency_report.json` (replace-on-run)
  - `_ARCHIVE/logs/immutability_report.json` (replace-on-run)

Policy:
- Audit logs are append-only evidence (do not rewrite).
- Reports are replace-on-run and represent the current verification state.

## WordPipe Runtime: Installation Profiles and Basic Use
Install profiles (extras) are defined in `pyproject.toml`:
- `wordpipe[core]`: dependency-light (import-safe, no docx/ai)
- `wordpipe[docx]`: enables python-docx adapters
- `wordpipe[ai]`: enables OpenAI adapter(s) (requires `openai`, `python-dotenv`)
- `wordpipe[cli]`: enables CLI entrypoint
- `wordpipe[full]`: docx + ai

Library usage (recommended for TraceLedger embedding):
```python
from pathlib import Path
from wordpipe.core.datatypes import PipelineConfig
from wordpipe.orchestration.pipeline import OrchestrationDeps, WordPipePipeline
from wordpipe.adapters.docx import DocxDocumentReader, DocxDocumentWriter, DocxSegmenter, DocxStyler
from wordpipe.events import make_sink

cfg = PipelineConfig(Path("in.docx"), Path("out.docx"), do_flatten=False)
deps = OrchestrationDeps(
    reader=DocxDocumentReader(),
    writer=DocxDocumentWriter(),
    styler=DocxStyler(),
    segmenter=DocxSegmenter(),
    logger=make_sink(logger=None, jsonl_path=None),
)
report = WordPipePipeline(deps).run(cfg)
```

Convenience entrypoint (wires defaults):
```python
from pathlib import Path
from wordpipe.core.datatypes import PipelineConfig
from wordpipe import process_docx_v3

cfg = PipelineConfig(Path("in.docx"), Path("out.docx"), do_flatten=True)
report = process_docx_v3(cfg)
```

## Troubleshooting
Common pipeline checks:
- Docs references:
  - `python tools/docs_link_check.py`
- Secrets scan:
  - `python tools/security_scan.py --root . --fail-on-findings`
- Import safety:
  - `python -m unittest discover -s tests -p "test_*.py" -v`

If apply aborts due to preflight:
- Re-run with:
  - `python tools/apply_legacy_reorg.py --preflight-mode warn ...`
  - or `--preflight-mode off` if you knowingly want to copy into non-empty trees.

## Pre-Push Checks
Run before committing or pushing:

```powershell
python tools/docs_link_check.py
python tools/security_scan.py --root . --fail-on-findings
python -m unittest discover -s tests -p "test_*.py" -v
```

## See Also
- Docs index: `docs/README.md`
- Tools runbook: `docs/PIPELINE_RUNBOOK.md`
- Tools contracts: `docs/PIPELINE_CONTRACTS.md`
- Tools integration: `docs/INTEGRATION_MAP_BEFORE_AFTER.md`
- TraceLedger direction: `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md`
- Security policy: `docs/SECURITY_HARDENING.md`
- WordPipe deep spec: `ARCHITECTURE.md`

