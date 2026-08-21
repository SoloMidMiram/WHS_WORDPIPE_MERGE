# Pipeline Contracts (`tools/`)

## Artifact Graph
`manifest.jsonl -> relocation_plan.jsonl -> relocation_map.jsonl -> LEGACY_INDEX.md + verify reports`

## Shared Stage Interface
All pipeline stages expose:
- CLI entrypoint (independent execution).
- Optional flags:
- `--workspace-root` (default `.`)
- `--summary-json` (optional structured stage result output)
- `--strict` (treat warnings as errors where applicable)
- Internal result model from `tools/pipeline_contracts.py`:
- `StagePaths`
- `StageResult`
- `StageError`

## Stage Contract: `make_manifest.py`
### Purpose
Generate canonical manifest files from snapshot input.

### Inputs
- Required:
- Snapshot root directory (`--root`, default `_WORK/snapshot`)
- Optional:
- Output directory (`--out-dir`, default `_ARCHIVE/manifests`)
- `--no-auto-normalize`
- Shared flags

### Outputs
- Created/overwritten:
- `_ARCHIVE/manifests/manifest.csv`
- `_ARCHIVE/manifests/manifest.jsonl`
- Appended:
- `_ARCHIVE/logs/setup.log` (auto-normalization event)

### Side Effects
- Reads snapshot tree and computes file SHA256 values.

### Exit Conditions
- Non-zero on missing required root directory or processing errors.
- With `--strict`, warning-only states become non-zero.

### Idempotency Notes
- Deterministic overwrite of manifest outputs.

### Dependencies
- Upstream: none.
- Downstream: input for `plan_legacy_reorg.py` and `verify_integrity.py`.

## Stage Contract: `plan_legacy_reorg.py`
### Purpose
Build dry-run legacy relocation plan from manifest rows.

### Inputs
- Required:
- `manifest.jsonl` (`--manifest`)
- Optional:
- Snapshot root for absolute source path materialization (`--root`)
- Output plan path (`--out`)
- Plan log path (`--log`)
- `--no-auto-normalize`
- Shared flags

### Outputs
- Created/overwritten:
- `_ARCHIVE/move_maps/relocation_plan.jsonl`
- Appended:
- `_ARCHIVE/logs/plan.log`

### Side Effects
- Derives area/stamp/rule metadata for legacy candidates.

### Exit Conditions
- Non-zero on missing manifest or stage errors.
- With `--strict`, warning-only states become non-zero.

### Idempotency Notes
- Deterministic overwrite of relocation plan output.

### Dependencies
- Upstream: `manifest.jsonl`.
- Downstream: input for `apply_legacy_reorg.py` and `verify_integrity.py`.

## Stage Contract: `apply_legacy_reorg.py`
### Purpose
Apply relocation plan via copy-only behavior with conflict-safe writes.

### Inputs
- Required:
- `relocation_plan.jsonl` (`--plan`)
- Optional:
- Snapshot root (`--root`)
- Relocation map output path (`--out-map`)
- Apply log path (`--log`)
- Conflict log path (`--conflict-log`)
- Preflight mode (`--preflight-mode warn|error|off`)
- `--no-auto-normalize`
- Shared flags

### Outputs
- Created/overwritten:
- `_ARCHIVE/move_maps/relocation_map.jsonl`
  - Each row retains `src_abs`/`dst_abs` diagnostics and also emits portable
    `src_rel`/`dst_rel` identities plus `conflict_path_rel` when applicable.
- Appended:
- `_ARCHIVE/logs/apply_reorg.log`
- `_ARCHIVE/logs/conflicts.log`

### Side Effects
- Copies current and legacy files to destination trees.
- Writes `_conflicts/` copies on hash mismatch.

### Exit Conditions
- Non-zero on missing plan, unrecoverable copy errors, or preflight abort in `error` mode.
- With `--strict`, warning-only states become non-zero.

### Idempotency Notes
- Re-runs are non-destructive; same-content destinations are skipped.
- Conflicts are preserved, not overwritten.

### Dependencies
- Upstream: `relocation_plan.jsonl`.
- Downstream: input for `build_legacy_index.py` and `verify_integrity.py`.

## Stage Contract: `build_legacy_index.py`
### Purpose
Generate navigable legacy index docs for both project roots.

### Inputs
- Required:
- Legacy root directories (defaults:
`wordpipe/legacy`, `WordHorrorStories/legacy`)
- Optional:
- Relocation map (`--relocation-map`) for confidence/label enrichment
- Index output paths:
- `--wordpipe-index-out`
- `--whs-index-out`
- Log path (`--log`)
- Shared flags

### Outputs
- Created/overwritten:
- `wordpipe/legacy/LEGACY_INDEX.md`
- `WordHorrorStories/legacy/LEGACY_INDEX.md`
- Appended:
- `_ARCHIVE/logs/legacy_index.log`

### Side Effects
- Reads relocation map and legacy tree structure to compute index sections.

### Exit Conditions
- Non-zero on hard stage errors.
- With `--strict`, warning-only states become non-zero.

### Idempotency Notes
- Deterministic overwrite of index docs.
- Append-only logging preserved.

### Dependencies
- Upstream: ideally `relocation_map.jsonl`, legacy trees.
- Downstream: none (operator/readability artifact).

## Stage Contract: `verify_integrity.py`
### Purpose
Verify integrity + coverage and emit consistency/immutability evidence.

### Inputs
- Required:
- `manifest.jsonl` (`--manifest`)
- Snapshot root directory (`--snapshot-root`)
- Optional:
- `relocation_plan.jsonl` (`--plan`)
- `relocation_map.jsonl` (`--relocation`)
- Shared flags

### Outputs
- Created/overwritten:
- `_ARCHIVE/logs/verify_report.md`
- `_ARCHIVE/logs/verify_report.json`
- `_ARCHIVE/logs/consistency_report.json`
- `_ARCHIVE/logs/immutability_report.json`

### Side Effects
- Hash scans destination trees and snapshot sources.

### Exit Conditions
- Non-zero on missing required inputs or hard stage errors.
- With `--strict`, warning-only states become non-zero.

### Idempotency Notes
- Deterministic overwrite of report outputs.

### Dependencies
- Upstream:
- `manifest.jsonl`
- optionally `relocation_plan.jsonl`, `relocation_map.jsonl`
- Downstream: quality gate / operator evidence.
