# Operations Docs

This folder is the operator-facing entrypoint for running and triaging the `tools/` evidence pipeline.

## Start Here
- Primary runbook: `docs/PIPELINE_RUNBOOK.md`
- Tools CLI reference: `tools/README_tools.md`
- Security policy + incident steps: `docs/SECURITY_HARDENING.md`
- Operations manual: `docs/operations/MANUAL.md`
- Ops labor notes: `docs/operations/LABOR.md`

## Evidence Artifacts
Key outputs live under `_ARCHIVE/`:
- `_ARCHIVE/manifests/manifest.jsonl`
- `_ARCHIVE/move_maps/relocation_plan.jsonl`
- `_ARCHIVE/move_maps/relocation_map.jsonl`
- `_ARCHIVE/logs/conflicts.log`
- `_ARCHIVE/logs/verify_report.md`
- `_ARCHIVE/logs/verify_report.json`

## See Also
- Docs index: `docs/README.md`
- Integration/data flow: `docs/INTEGRATION_MAP_BEFORE_AFTER.md`
