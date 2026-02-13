# WORKSPACE_OVERVIEW

## Purpose
Copy-only merge workspace that separates current vs legacy content and buckets legacy items by time for safe archival.

## Immutable Inputs (Do Not Modify)
- _ARCHIVE/raw_zips/snapshot_20260211_205716.zip
- _WORK/snapshot (extracted)

## Evidence / Outputs
- _ARCHIVE/manifests/manifest.csv
- _ARCHIVE/manifests/manifest.jsonl
- _ARCHIVE/move_maps/relocation_plan.jsonl
- _ARCHIVE/move_maps/relocation_map.jsonl
- wordpipe/legacy/LEGACY_INDEX.md
- WordHorrorStories/legacy/LEGACY_INDEX.md
- _ARCHIVE/logs/conflicts.log
- _ARCHIVE/logs/verify_report.md
- _ARCHIVE/logs/verify_report.json
- _ARCHIVE/logs/consistency_report.json
- _ARCHIVE/logs/immutability_report.json

## Canonical Legacy Bucket Scheme
- area/JY/JM/JD/HHMM

## Documentation
- docs/LABOR_REPORT.md
- docs/PIPELINE_CONTRACTS.md
- docs/PIPELINE_RUNBOOK.md
- docs/INTEGRATION_MAP_BEFORE_AFTER.md
- docs/SECURITY_HARDENING.md

## Re-run Commands (PowerShell)
```powershell
python tools/make_manifest.py
python tools/plan_legacy_reorg.py
python tools/apply_legacy_reorg.py
python tools/build_legacy_index.py
python tools/verify_integrity.py
```

## Evidence Policy
- Stage 3 logs are historical; never rewrite.
- Older incorrect legacy_index summary lines are preserved as evidence; newer runs supersede.
