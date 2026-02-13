# Documentation Style Guide

Status: Draft (living document)

## Purpose
This guide defines a small "house style" for Markdown docs in this repository so the documentation pack stays navigable and consistent.

## Document Header Convention
- Start with a single H1 title: `# <Title>`
- If the doc is part of the main pack (not `docs/PlansArchive/`), add `## See Also` near the top when there are natural cross-links.
- Prefer ASCII punctuation (straight quotes `'` and `"`; `-` and `--`) to avoid encoding/rendering issues across environments.

## Cross-Linking Rules
- Use repo-relative paths in backticks for references, for example: `docs/README.md`.
- When referencing artifacts, use workspace-relative paths, for example: `_ARCHIVE/logs/verify_report.json`.
- Avoid renaming existing docs; prefer additive docs and links.

## Baseline Banner (When Applicable)
Docs that describe the evidence pipeline should include a short baseline banner (counts and "frozen metrics") when a stable regression baseline exists.

Example fields:
- `total_files`
- `legacy_candidates`
- `apply` counters
- `verify` counters

## Output Policy Vocabulary
Use consistent terms:
- `artifact`: a generated file consumed by downstream stages
- `audit log`: append-only operational trace
- `report`: replace-on-run deterministic output
- `warning`: non-fatal condition (may become fatal under `--strict`)
- `error`: fatal condition (non-zero exit)

## Append-Only vs Replace-On-Run
- Append-only: `setup.log`, `plan.log`, `apply_reorg.log`, `legacy_index.log`, `conflicts.log`
- Replace-on-run: `verify_report.md`, `verify_report.json`, `consistency_report.json`, `immutability_report.json`

## Placeholders in Examples
Use placeholders first, then one concrete example.

Preferred placeholders:
- `<WORKSPACE_ROOT>`
- `<SNAPSHOT_ROOT>`
- `<MANIFEST_PATH>`
- `<PLAN_PATH>`
- `<MAP_PATH>`

