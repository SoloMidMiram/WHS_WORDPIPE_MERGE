# Engineering Docs

This folder is the engineer-facing entrypoint for changing pipeline stages, verifying contracts, and keeping integration behavior consistent.

## Start Here
- Stage IO contracts: `docs/PIPELINE_CONTRACTS.md`
- Full tools module catalog: `docs/TOOLS_MODULES_INTEGRATION_REPORT.md`
- Before/after integration view: `docs/INTEGRATION_MAP_BEFORE_AFTER.md`
- WordPipe modules/packages guide: `docs/engineering/MODULES_PACKAGES.md`
- Repository boundaries: `docs/engineering/REPOSITORY_BOUNDARIES.md`
- Current outstanding-work and optimization map: `docs/engineering/OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md`
- Current Phase 13–17 commit draft: `docs/engineering/PHASE13_17_COMMIT_DRAFT.md`

## Validation Checks
- P0–P2 remediation report (stages, claims, commit map):
  - `docs/engineering/P0_P2_VALIDATION_REPORT.md`
- Current implementation alignment and pending commit scope:
  - `docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md`
  - `docs/engineering/PHASE13_17_COMMIT_DRAFT.md`
- Docs reference integrity:
  - `python tools/docs_link_check.py`
- Secret scan (high confidence):
  - `python tools/security_scan.py --root . --fail-on-findings`
- Orchestrator sanity (no writes):
  - `python tools/orchestrate.py --root _WORK/snapshot --dry-run`

## See Also
- Docs index: `docs/README.md`
- Logic flow (TraceLedger direction): `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md`
