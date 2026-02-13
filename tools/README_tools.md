# Tools (WHS_WORDPIPE_MERGE)

## Documentation
- `docs/README.md`
- `docs/operations/README.md`
- `docs/engineering/README.md`
- `docs/architecture/README.md`
- `docs/LABOR_REPORT.md`
- `docs/PIPELINE_CONTRACTS.md`
- `docs/PIPELINE_RUNBOOK.md`
- `docs/INTEGRATION_MAP_BEFORE_AFTER.md`
- `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md`
- `docs/REPOSITORY_REVIEW_MERGED_2026-02-13.md`
- `docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md`
- `docs/TRACELEDGER_INTEGRATION_CONTRACT.md`
- `docs/SECURITY_HARDENING.md`
- `docs/DOC_STYLE_GUIDE.md`
- `docs/DUPLICATE_POLICY.md`

## Shared CLI flags (pipeline stages)
All 5 pipeline stages support:
- `--workspace-root` (default `.`)
- `--summary-json <path>` (optional `StageResult` JSON output)
- `--strict` (treat warnings as errors)

## One-command pipeline
Run the standard 5-stage flow:

```powershell
python tools/orchestrate.py --root _WORK/snapshot
```

Dry run (no writes):

```powershell
python tools/orchestrate.py --root _WORK/snapshot --dry-run
```

Optional route step after apply:

```powershell
python tools/orchestrate.py --root _WORK/snapshot --run-route-unmapped
```

## Stage tools

### `make_manifest.py`
Generates manifests for files under snapshot root.

```powershell
python tools/make_manifest.py --workspace-root . --root _WORK/snapshot --out-dir _ARCHIVE/manifests
```

Outputs:
- `_ARCHIVE/manifests/manifest.csv`
- `_ARCHIVE/manifests/manifest.jsonl`

### `plan_legacy_reorg.py`
Builds dry-run plan for legacy candidates from manifest.

```powershell
python tools/plan_legacy_reorg.py --workspace-root . --root _WORK/snapshot --manifest _ARCHIVE/manifests/manifest.jsonl
```

Output:
- `_ARCHIVE/move_maps/relocation_plan.jsonl`

### `apply_legacy_reorg.py`
Applies copy-only relocation plan with conflict-safe writes.

```powershell
python tools/apply_legacy_reorg.py --workspace-root . --root _WORK/snapshot
```

New options:
- `--preflight-mode warn|error|off` (default: `warn`)
- `--conflict-log _ARCHIVE/logs/conflicts.log`

Outputs:
- `_ARCHIVE/move_maps/relocation_map.jsonl`
- `_ARCHIVE/logs/apply_reorg.log`
- `_ARCHIVE/logs/conflicts.log`

### `build_legacy_index.py`
Generates legacy index docs.

```powershell
python tools/build_legacy_index.py --workspace-root .
```

Outputs:
- `wordpipe/legacy/LEGACY_INDEX.md`
- `WordHorrorStories/legacy/LEGACY_INDEX.md`

### `verify_integrity.py`
Verifies integrity + coverage and writes consistency/immutability evidence.

```powershell
python tools/verify_integrity.py --workspace-root . --snapshot-root _WORK/snapshot
```

Key options:
- `--plan _ARCHIVE/move_maps/relocation_plan.jsonl`
- `--relocation _ARCHIVE/move_maps/relocation_map.jsonl`
- `--snapshot-root _WORK/snapshot`

Outputs:
- `_ARCHIVE/logs/verify_report.md`
- `_ARCHIVE/logs/verify_report.json`
- `_ARCHIVE/logs/consistency_report.json`
- `_ARCHIVE/logs/immutability_report.json`

### `route_unmapped_misc.py` (optional)
Routes snapshot-root docs (`README.md`, `MERGE_MAP.md`) into `_META` copy-only.

```powershell
python tools/route_unmapped_misc.py --root _WORK/snapshot
```

Output:
- `_ARCHIVE/logs/route_unmapped.log`

### `security_scan.py`
Runs high-confidence secret scanning on text files.

```powershell
python tools/security_scan.py --root . --fail-on-findings
```

### `docs_link_check.py`
Validates that `docs/<...>.md` references in markdown files point to real files.

```powershell
python tools/docs_link_check.py
```

## Notes
- Jalali conversion uses `tools/jalali.py`.
- Tehran timezone uses `Asia/Tehran` when available; otherwise fixed `+03:30`.
