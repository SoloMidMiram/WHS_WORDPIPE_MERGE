# Obsolete Documentation Index

> **Purpose:** Index of documentation files that have been superseded by newer, more comprehensive docs.
> **Principle:** Old docs are preserved in-place (not deleted) for historical reference, but should not be used as current source of truth.
> **Date:** 2026-02-14 (Jalali: 1404-11-25)

---

## Rule

If you are looking for documentation, start with these **current** sources:
- `ARCHITECTURE_AND_MODULES.md` — Full architecture, modules, integration, data flow, logic flow, goals, constraints
- `PLAN.md` — Immutable log of intentions and completions
- `ROADMAP.md` — Project roadmap with phases, milestones, constraints
- `JOURNAL.md` — Dated period journal with claims and verification
- `ONTOLOGY_MODEL.md` — Formal entity-relationship model
- `INDEX.md` — Full project file index

The docs listed below are **preserved for historical/audit purposes only**. They may contain:
- Absolute paths that are broken
- References to tools that have been archived
- Claims that are no longer accurate
- Plans that have been superseded

---

## Superseded Docs

| Old Doc | Superseded By | Reason for Obsolescence |
|---------|---------------|------------------------|
| `docs/architecture/PROJECT_SUMMARY.md` | `ARCHITECTURE_AND_MODULES.md` | Only covered tools/ + wordpipe/; missing chronicle pipeline (pipeline/); stale data flow diagrams |
| `docs/PIPELINE_CONTRACTS.md` | `ARCHITECTURE_AND_MODULES.md` (§6) | Only covered tools/ pipeline; missing chronicle pipeline contracts |
| `docs/PIPELINE_RUNBOOK.md` | `ARCHITECTURE_AND_MODULES.md` (§2-3) | Only covered tools/ pipeline; missing chronicle pipeline runbook |
| `docs/TOOLS_MODULES_INTEGRATION_REPORT.md` | `ARCHITECTURE_AND_MODULES.md` (§3) | Only covered tools/ modules; missing chronicle pipeline modules |
| `docs/INTEGRATION_MAP_BEFORE_AFTER.md` | `ARCHITECTURE_AND_MODULES.md` (§5) | Only covered tools/ integration; missing cross-subsystem integration |
| `docs/operations/MANUAL.md` | `ARCHITECTURE_AND_MODULES.md` (§2.5, 3.5) | Stale commands; missing chain.ps1 and chronicle pipeline quickstart |
| `docs/engineering/MODULES_PACKAGES.md` | `ARCHITECTURE_AND_MODULES.md` (§4) | Still accurate for wordpipe/ layout, but superseded by comprehensive reference |
| `docs/PlansArchive/PLAN.md` | `PLAN.md` (root) | Historical plan snapshot; current plan is at root |

---

## Preserved Docs (Still Current)

These docs remain relevant and have not been superseded:

| Doc | Purpose |
|-----|---------|
| `docs/SECURITY_HARDENING.md` | Security policies and incident response |
| `docs/DUPLICATE_POLICY.md` | Duplicate governance rules |
| `docs/DOC_STYLE_GUIDE.md` | Documentation conventions |
| `docs/REPOSITORY_REVIEW_MERGED_2026-02-13.md` | Consolidated architectural review |
| `docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md` | TraceLedger implementation roadmap |
| `docs/TRACELEDGER_INTEGRATION_CONTRACT.md` | TraceLedger library contract |
| `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md` | TraceLedger logic flow narrative |
| `docs/LABOR_REPORT.md` | Labor and effort tracking |
| `docs/operations/LABOR.md` | Operations labor notes |
| `docs/PlansArchive/` | Historical plan snapshots (archive) |
| `VERIFICATION.md` | Project verification plan with cross-reference claims |
| `WORKSPACE_OVERVIEW.md` | Workspace manual for copy-only merge operations |

## Archived Root-Level Docs

The following root-level `.md` files were superseded and have been moved to `_ARCHIVE/root-docs/`:

| Doc | Superseded By | Archive Location |
|-----|---------------|------------------|
| `ROADMAP_1404-11-25.md` | `ROADMAP.md` | `_ARCHIVE/root-docs/ROADMAP_1404-11-25.md` |
| `ONTOLOGY.md` | `ONTOLOGY_MODEL.md` | `_ARCHIVE/root-docs/ONTOLOGY.md` |
| `ARCHITECTURE.md` | `ARCHITECTURE_AND_MODULES.md` | `_ARCHIVE/root-docs/ARCHITECTURE.md` |
| `CODEX_LOG.md` | `JOURNAL.md` | `_ARCHIVE/root-docs/CODEX_LOG.md` |
| `PATH_FIX_LOG.md` | `JOURNAL.md` | `_ARCHIVE/root-docs/PATH_FIX_LOG.md` |
| `PROJECT_INDEX.md` | `INDEX.md` | `_ARCHIVE/root-docs/PROJECT_INDEX.md` |

---

## Change Log

| Date (Gregorian) | Date (Jalali) | Change |
|------------------|---------------|--------|
| 2026-02-14 | 1404-11-25 | Fixed ARCHITECTURE_AND_MODULES.md §2 — corrected ingest/merge/verify paths to tools/pipeline-chronicle/ |
| 2026-02-14 | 1404-11-25 | Initial creation — all old docs indexed as superseded or preserved |
