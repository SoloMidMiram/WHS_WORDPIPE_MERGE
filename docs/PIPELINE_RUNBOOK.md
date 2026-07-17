# Pipeline Runbook (`tools/`)

## Happy Path
From repository root:

```powershell
python tools/orchestrate.py --root _WORK/snapshot
```

From any working directory:

```powershell
python tools/orchestrate.py --workspace-root <WORKSPACE_ROOT> --root _WORK/snapshot
```

## Dry-Run Mode
Prints resolved command sequence without writing outputs:

```powershell
python tools/orchestrate.py --root _WORK/snapshot --dry-run
```

## Stage-by-Stage Manual Execution
```powershell
python tools/make_manifest.py --workspace-root . --root _WORK/snapshot
python tools/plan_legacy_reorg.py --workspace-root . --root _WORK/snapshot
python tools/apply_legacy_reorg.py --workspace-root . --root _WORK/snapshot
python tools/build_legacy_index.py --workspace-root .
python tools/verify_integrity.py --workspace-root . --snapshot-root _WORK/snapshot
```

## Optional Machine-Readable Stage Summary
Every stage supports `--summary-json`:

```powershell
python tools/apply_legacy_reorg.py --summary-json _ARCHIVE/logs/apply_summary.json
```

## Failure Triage Matrix
| Error text pattern | Typical cause | Operator action |
|---|---|---|
| `ERROR: required ... not found: <abs_path>` | Missing required input path or wrong workspace root | Verify `--workspace-root`, then verify path existence and rerun stage |
| `destination trees are non-empty; rerun with --preflight-mode warn or off` | Apply stage in `--preflight-mode error` with existing outputs | Re-run with `--preflight-mode warn` (default) for copy-only incremental behavior |
| `consistency report is not OK` (strict failure) | Plan/map mismatch | Regenerate plan + apply sequence, inspect `_ARCHIVE/logs/consistency_report.json` |
| `immutability report is not OK` (strict failure) | Snapshot content drift vs manifest hashes | Re-run manifest on current source of truth or restore immutable snapshot source |
| `integrity failures: N` (strict failure) | Missing/corrupt destination artifacts | Inspect `_ARCHIVE/logs/verify_report.md`, rerun apply and verify |

## Do / Don't Policy
### Do
- Treat `_ARCHIVE/raw_zips/snapshot_*.zip` and extracted snapshot input as immutable evidence sources.
- Keep append-only logs as historical evidence (`setup.log`, `plan.log`, `apply_reorg.log`, `legacy_index.log`, `conflicts.log`).
- Use `--workspace-root` explicitly when running from outside repo root.
- Use `--strict` for CI-like enforcement.

### Don't
- Don't delete or rewrite historical append-only logs.
- Don't use destructive file operations in destination trees; pipeline is copy-only by design.
- Don't modify canonical source content in place under the snapshot input during verification windows.

## Key Evidence Outputs
- `_ARCHIVE/manifests/manifest.jsonl`
- `_ARCHIVE/move_maps/relocation_plan.jsonl`
- `_ARCHIVE/move_maps/relocation_map.jsonl`
- `_ARCHIVE/logs/conflicts.log`
- `_ARCHIVE/logs/verify_report.md`
- `_ARCHIVE/logs/verify_report.json`
- `_ARCHIVE/logs/consistency_report.json`
- `_ARCHIVE/logs/immutability_report.json`
