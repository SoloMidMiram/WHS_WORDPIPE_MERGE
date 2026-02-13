# Labor Report: Tools Pipeline Hardening

## See Also
- `docs/README.md`
- `docs/INTEGRATION_MAP_BEFORE_AFTER.md`
- `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md`
- `docs/SECURITY_HARDENING.md`
- `docs/REPOSITORY_REVIEW_MERGED_2026-02-13.md`

## TraceLedger Readiness Summary
- The `tools/` pipeline is already contract-consistent (`StageResult`) and can be automated as evidence generation, but TraceLedger should not depend on it as a runtime library API.
- Copy-only and conflict-safe behavior is suitable for audit/evidence workflows TraceLedger may want to schedule independently.
- Security posture is improved (env-only secrets + scanner), which is required if TraceLedger will run in CI/CD.
- WordPipe runtime modularization and an EventSink contract are planned/ongoing and will be the primary TraceLedger integration surface.
- Portability improvements (preferring relative paths in verification) are planned to reduce environment-dependent failures.

## Change Anchors
- `c778c43` (security hardening + pipeline save point)
- Note: additional documentation organization work exists in the working tree after `c778c43` and should be anchored by the next "docs organization" commit.

## Executive Summary
This workspace implements a copy-only archival pipeline that separates current content from legacy content and verifies integrity after relocation. The labor completed in this phase focused on operational safety, evidence quality, and module consistency without changing core copy-only semantics.

Outcomes:
- Added preflight safety visibility and conflict visibility.
- Added consistency and immutability verification outputs.
- Added one-command orchestration.
- Standardized stage interfaces for consistent but independent CLI modules.

Risk posture:
- Low migration risk (additive changes, backward-compatible flags).
- Operational risk reduced through explicit checks and machine-readable summaries.

## Work Performed
### Stage 1: `make_manifest.py`
- Preserved manifest generation behavior and schema.
- Added standardized stage contract output (`StageResult`).
- Added shared CLI options: `--workspace-root`, `--summary-json`, `--strict`.
- Standardized path resolution against workspace root.

### Stage 2: `plan_legacy_reorg.py`
- Preserved legacy planning logic and output format.
- Added standardized required-input error handling.
- Added shared CLI options and `StageResult` output model.

### Stage 3: `apply_legacy_reorg.py`
- Preserved copy-only + conflict-safe behavior.
- Retained `--preflight-mode` and conflict summary logging.
- Added workspace-root path resolution to eliminate implicit CWD coupling.
- Added shared CLI options and contract result output.

### Stage 4: `build_legacy_index.py`
- Added explicit CLI-configurable inputs/outputs (previously mostly implicit).
- Added shared CLI options and contract result output.
- Preserved generated `LEGACY_INDEX.md` behavior and append-only log semantics.

### Stage 5: `verify_integrity.py`
- Preserved existing `verify_report.json` top-level schema: `integrity`, `coverage`.
- Kept consistency + immutability report generation.
- Added standardized stage contract output and shared CLI options.

### Orchestration + Shared Contracts
- Added `tools/pipeline_contracts.py` for `StagePaths`, `StageResult`, `StageError`.
- Updated stage scripts to return structured results and optional `--summary-json`.
- Kept orchestrator composition-only role (`tools/orchestrate.py`).

## Evidence Snapshot (Frozen Baseline)
- Pipeline stages:
`make_manifest.py`, `plan_legacy_reorg.py`, `apply_legacy_reorg.py`, `build_legacy_index.py`, `verify_integrity.py`
- Baseline evidence:
- `total_files: 98`
- `legacy_candidates: 25` (`ai: 18`, `misc: 7`)
- `apply`: `copied_current: 71`, `legacy_copied: 25`, `errors: 0`
- `verify`: `failures: 0`, `accounted: 98/98`, `duplicates: 9`

## Behavioral Changes
- Preflight behavior in apply stage:
- `warn` (default), `error`, `off`
- Dedicated conflict summary log:
- `_ARCHIVE/logs/conflicts.log`
- Consistency report:
- `_ARCHIVE/logs/consistency_report.json`
- Immutability report:
- `_ARCHIVE/logs/immutability_report.json`
- One-command execution:
- `python tools/orchestrate.py --root _WORK/snapshot`

## Operational Impact
Before:
- Operators ran stage scripts manually with implicit workspace assumptions in some stages.

After:
- Operators can still run stage-by-stage commands.
- Operators can run one-command orchestration.
- Stages support explicit workspace-root execution and optional machine-readable summary outputs.
- Failure modes are clearer and easier to automate around.

## Known Limits and Deferred Work
- Parallel hashing optimization is deferred.
- Duplicate consolidation/hard-link strategy is deferred.
- Transactional rollback/recovery path is deferred.
- Scope is intentionally limited to `tools/` pipeline modules.

## Glossary
- Manifest:
Inventory of snapshot files including hashes and timestamps (`manifest.jsonl`/`manifest.csv`).
- Relocation plan:
Planned legacy moves with bucket metadata (`relocation_plan.jsonl`).
- Relocation map:
Applied results with status/conflict metadata (`relocation_map.jsonl`).
- Conflict:
Destination hash mismatch resolved by writing source copy into `_conflicts/`.
- Immutability proof:
Verification that source snapshot files still match manifest hashes.
