# Project Summary

## What This Repository Contains
This repository contains two main subsystems:
- `tools/`: an evidence-oriented, copy-only archival pipeline that produces `_ARCHIVE/` artifacts and verifies integrity.
- `wordpipe/`: a modular runtime DOCX processing helper package intended for embedding (TraceLedger-oriented).

It also contains preserved evidence trees (`_WORK/`, `_ARCHIVE/`, `wordpipe/legacy/`, `WordHorrorStories/chatgpt-chronicle/**`) that should not be treated as "runtime code".

## System Boundaries
- Evidence pipeline (`tools/`):
  - CLI oriented
  - Produces audit logs and verification reports
  - Copy-only, conflict-safe behavior
- Runtime pipeline (`wordpipe/`):
  - Library oriented (import-safe, dependency-injected orchestration)
  - Optional adapters (docx, ai) via extras
  - Emits structured events via `EventSink` helpers
- TraceLedger (external consumer):
  - Owns run envelopes and event storage
  - Consumes WordPipe as a helper library and provides an event sink adapter

## Data Flow (Evidence Pipeline)
Canonical artifact chain:

```text
manifest.jsonl -> relocation_plan.jsonl -> relocation_map.jsonl -> LEGACY_INDEX.md + verify outputs
```

Key evidence outputs:
- `_ARCHIVE/manifests/manifest.jsonl`
- `_ARCHIVE/move_maps/relocation_plan.jsonl`
- `_ARCHIVE/move_maps/relocation_map.jsonl`
- `_ARCHIVE/logs/verify_report.md`
- `_ARCHIVE/logs/verify_report.json`

## Control Flow (How Operators and CI Run It)
Operators typically run:
- `python tools/orchestrate.py --root _WORK/snapshot`

CI/operator checks:
- Docs reference integrity:
  - `python tools/docs_link_check.py`
- Secrets scan:
  - `python tools/security_scan.py --root . --fail-on-findings`
- Import safety:
  - `python -m unittest discover -s tests -p "test_*.py" -v`

## Runtime Flow (How TraceLedger Consumes WordPipe)
TraceLedger should integrate with WordPipe as a library:

```text
TraceLedger
  -> WordPipePipeline(deps).run(cfg)
     -> returns RunReport
     -> emits structured events to the provided sink
```

The composition root (TraceLedger) decides:
- which adapters to use (docx, ai, legacy flatteners)
- where events go (TraceLedger storage, JSONL, stdout logger)

## Safety/Security Posture
Evidence pipeline:
- Copy-only and conflict-safe (does not destructively overwrite).
- Append-only audit logs and replace-on-run reports.

Repo security posture:
- Secrets are env-based; scanning is available via `tools/security_scan.py`.
- Logs and event sinks apply redaction as defense in depth.

## Where To Start
- Docs index: `docs/README.md`
- Operations manual: `docs/operations/MANUAL.md`
- Modules/packages guide: `docs/engineering/MODULES_PACKAGES.md`
- Architecture spec: `ARCHITECTURE.md`

