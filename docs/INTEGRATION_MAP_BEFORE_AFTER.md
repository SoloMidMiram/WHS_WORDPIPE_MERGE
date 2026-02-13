# Integration Map and Data Flow (Before vs After)

## See Also
- `docs/README.md`
- `docs/TOOLS_MODULES_INTEGRATION_REPORT.md`
- `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md`

## Scope
This map covers the `tools/` pipeline only:
- `make_manifest.py`
- `plan_legacy_reorg.py`
- `apply_legacy_reorg.py`
- `build_legacy_index.py`
- `verify_integrity.py`
- `orchestrate.py`

## Before Integration Map
### Control Flow
Operator-driven manual sequence:

1. `python tools/make_manifest.py`
2. `python tools/plan_legacy_reorg.py`
3. `python tools/apply_legacy_reorg.py`
4. `python tools/build_legacy_index.py`
5. `python tools/verify_integrity.py`

### Module Coupling
- Stages were primarily coupled by fixed relative paths and current working directory assumptions.
- `build_legacy_index.py` used implicit workspace discovery (`os.path.abspath(".")`).
- No shared stage result contract for machine-readable per-stage integration.

### Data Flow
```text
_WORK/snapshot
  -> make_manifest.py
     -> _ARCHIVE/manifests/manifest.csv
     -> _ARCHIVE/manifests/manifest.jsonl

manifest.jsonl
  -> plan_legacy_reorg.py
     -> _ARCHIVE/move_maps/relocation_plan.jsonl

relocation_plan.jsonl + _WORK/snapshot
  -> apply_legacy_reorg.py
     -> _ARCHIVE/move_maps/relocation_map.jsonl
     -> wordpipe/** (copy-only)
     -> WordHorrorStories/** (copy-only)
     -> _ARCHIVE/logs/conflicts.log

relocation_map.jsonl + legacy trees
  -> build_legacy_index.py
     -> wordpipe/legacy/LEGACY_INDEX.md
     -> WordHorrorStories/legacy/LEGACY_INDEX.md

manifest.jsonl + relocation_plan.jsonl + relocation_map.jsonl + snapshot
  -> verify_integrity.py
     -> _ARCHIVE/logs/verify_report.md
     -> _ARCHIVE/logs/verify_report.json
     -> _ARCHIVE/logs/consistency_report.json
     -> _ARCHIVE/logs/immutability_report.json
```

## After Integration Map
### Control Flow Options
Option A: orchestrated execution:

`python tools/orchestrate.py --workspace-root <repo> --root _WORK/snapshot`

Option B: independent stage execution:

Each stage can run standalone with explicit `--workspace-root`.

### Module Integration Contract
All pipeline stages now expose:
- `run_stage(...) -> StageResult`
- shared optional flags:
- `--workspace-root`
- `--summary-json`
- `--strict`

Shared contract module:
- `tools/pipeline_contracts.py`
  - `StagePaths`
  - `StageResult`
  - `StageError`
  - path-resolution and summary-json helpers

### Data Flow (After)
```text
[Input Root]
_WORK/snapshot

  -> make_manifest.py
     outputs:
       _ARCHIVE/manifests/manifest.csv
       _ARCHIVE/manifests/manifest.jsonl
     optional integration output:
       --summary-json -> StageResult JSON

  -> plan_legacy_reorg.py (consumes manifest.jsonl)
     outputs:
       _ARCHIVE/move_maps/relocation_plan.jsonl
     optional integration output:
       --summary-json -> StageResult JSON

  -> apply_legacy_reorg.py (consumes relocation_plan.jsonl + snapshot)
     outputs:
       _ARCHIVE/move_maps/relocation_map.jsonl
       _ARCHIVE/logs/conflicts.log
       copy-only destination trees
     gate:
       --preflight-mode warn|error|off
     optional integration output:
       --summary-json -> StageResult JSON

  -> build_legacy_index.py (consumes relocation_map + legacy roots)
     outputs:
       wordpipe/legacy/LEGACY_INDEX.md
       WordHorrorStories/legacy/LEGACY_INDEX.md
     explicit integration inputs:
       --relocation-map
       --wordpipe-legacy-root
       --whs-legacy-root
       --wordpipe-index-out
       --whs-index-out
       --log
     optional integration output:
       --summary-json -> StageResult JSON

  -> verify_integrity.py (consumes manifest + optional plan/map + snapshot)
     outputs:
       _ARCHIVE/logs/verify_report.md
       _ARCHIVE/logs/verify_report.json
       _ARCHIVE/logs/consistency_report.json
       _ARCHIVE/logs/immutability_report.json
     optional integration output:
       --summary-json -> StageResult JSON
```

## Before vs After Delta
| Area | Before | After |
|---|---|---|
| Stage interface | CLI-only, inconsistent machine outputs | Unified `StageResult` contract + optional summary JSON |
| Workspace binding | Mixed implicit/explicit pathing | Consistent `--workspace-root` path resolution |
| Stage independence | Usable, but one stage depended on implicit CWD | All stages independently runnable with explicit IO |
| Integration observability | Logs + reports only | Logs + reports + per-stage `StageResult` JSON |
| Index stage configurability | Limited explicit inputs | Fully explicit configurable IO flags |
| Orchestration | Manual sequencing | Manual or `orchestrate.py` composition |

## Integration Entry Points
- Orchestrator: `tools/orchestrate.py`
- Stage contracts: `tools/pipeline_contracts.py`
- Stage runbook: `docs/PIPELINE_RUNBOOK.md`
- Stage contract reference: `docs/PIPELINE_CONTRACTS.md`

## Execution Context and Argument Passing
`tools/orchestrate.py` runs each stage as a subprocess with:
- subprocess working directory: `cwd=<abs(--workspace-root)>`
- `--root <snapshot_root>` passed through to root-aware stages (make/plan/apply and optional route step)
- `--snapshot-root <snapshot_root>` passed to `verify_integrity.py`

Today, `tools/orchestrate.py` does not forward:
- `--workspace-root` (stages rely on `cwd` implicitly in orchestrated runs)
- `--strict`
- `--summary-json`
- stage-specific overrides (for example custom `--manifest`, `--plan`, output paths)

Operator patterns:
- If you need `--strict` or `--summary-json`, run the stage directly.
- If you need stage-specific overrides, run the stage directly.
- Future extension (not implemented): add explicit pass-through flags to `tools/orchestrate.py`.

## Job Model (Who Runs What)
- Operator job:
  - Run the pipeline (stage-by-stage or orchestrated) and inspect `_ARCHIVE/logs/*` reports.
- CI job:
  - Run docs link check (`python tools/docs_link_check.py`) and secret scan (`python tools/security_scan.py --root . --fail-on-findings`).
  - Optionally run `python tools/orchestrate.py --dry-run` for interface sanity.
- Evidence job:
  - Preserve append-only audit logs and deterministic reports under `_ARCHIVE/`.
  - Treat `_ARCHIVE/` artifacts as evidence; avoid rewriting historical logs.

## TraceLedger Impact
TraceLedger's primary integration target is the **WordPipe runtime** (`wordpipe/`) as a library API. The `tools/` pipeline remains evidence/audit oriented, intended for archival verification workflows and operational audits rather than in-process library calls.
