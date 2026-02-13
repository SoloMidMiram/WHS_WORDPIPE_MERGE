# Labor Notes (Operations)

## What Changed (High Level)
- Tools pipeline documentation pack added under `docs/` with role-based entrypoints.
- Tools pipeline includes a reproducible docs link checker (`tools/docs_link_check.py`) and a secrets scanner (`tools/security_scan.py`).
- WordPipe runtime was refactored into strict layers with import-boundary hardening, interfaces, adapters, and orchestration to support TraceLedger embedding.
- Import-safety is enforced by a unittest that blocks optional dependencies and verifies imports still succeed.

## Key Save Points (Commits)
- `cb8a6d2` docs pack + navigation + docs reference validation
- `9aadd2f` WordPipe EventSink + unified `evt(...)` emission
- `6cd976d` WordPipe modular refactor (interfaces/adapters/orchestration) + packaging + import-safety test

## Frozen Baseline Metrics (Tools Evidence Pipeline)
Frozen regression baseline (evidence pipeline):
- total_files: 98
- legacy_candidates: 25 (ai: 18, misc: 7)
- apply: copied_current=71, legacy_copied=25, errors=0
- verify: failures=0, accounted=98/98, duplicate_groups=9

## Operator Impact
What operators run:
- One-command pipeline runner:
  - `python tools/orchestrate.py --root _WORK/snapshot`
- Stage-by-stage is still valid (see `docs/PIPELINE_RUNBOOK.md`).

What operators can validate quickly:
- Docs references:
  - `python tools/docs_link_check.py`
- Secrets scan:
  - `python tools/security_scan.py --root . --fail-on-findings`
- Import-safety:
  - `python -m unittest discover -s tests -p "test_*.py" -v`

## See Also
- Full labor report: `docs/LABOR_REPORT.md`
- Operations manual: `docs/operations/MANUAL.md`
- Runbook: `docs/PIPELINE_RUNBOOK.md`
- Security: `docs/SECURITY_HARDENING.md`
- TraceLedger plan: `docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md`

