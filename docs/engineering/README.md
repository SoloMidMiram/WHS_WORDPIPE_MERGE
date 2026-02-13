# Engineering Docs

This folder is the engineer-facing entrypoint for changing pipeline stages, verifying contracts, and keeping integration behavior consistent.

## Start Here
- Stage IO contracts: `docs/PIPELINE_CONTRACTS.md`
- Full tools module catalog: `docs/TOOLS_MODULES_INTEGRATION_REPORT.md`
- Before/after integration view: `docs/INTEGRATION_MAP_BEFORE_AFTER.md`
- WordPipe modules/packages guide: `docs/engineering/MODULES_PACKAGES.md`

## Validation Checks
- Docs reference integrity:
  - `python tools/docs_link_check.py`
- Secret scan (high confidence):
  - `python tools/security_scan.py --root . --fail-on-findings`
- Orchestrator sanity (no writes):
  - `python tools/orchestrate.py --root _WORK/snapshot --dry-run`

## See Also
- Docs index: `docs/README.md`
- Logic flow (TraceLedger direction): `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md`
