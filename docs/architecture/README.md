# Architecture Docs

This folder is the architecture-facing entrypoint for TraceLedger alignment and runtime modularity direction (WordPipe as a reusable helper package).

## Start Here
- Consolidated review: `docs/REPOSITORY_REVIEW_MERGED_2026-02-13.md`
- Debug/enhancement roadmap: `docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md`
- Integration contract: `docs/TRACELEDGER_INTEGRATION_CONTRACT.md`
- Before/after logic flow narrative: `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md`
- Whole-project summary: `docs/architecture/PROJECT_SUMMARY.md`
- Deep architecture spec: `ARCHITECTURE.md`

## Key Boundary Principle
- `tools/` is the evidence/audit pipeline (CLI oriented, produces `_ARCHIVE/` artifacts).
- `wordpipe/` is the runtime library surface TraceLedger should consume (in-process).

## See Also
- Docs index: `docs/README.md`
- Duplicate governance placeholder: `docs/DUPLICATE_POLICY.md`
