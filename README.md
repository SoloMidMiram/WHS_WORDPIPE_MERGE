# WHS WordPipe Merge

> Evidence-first Chronicle tooling, copy-only archival tooling, and a modular
> DOCX processing library.

## Overview

This repository contains three active subsystems plus preserved evidence trees:

| Subsystem | Role | Primary location |
|-----------|------|------------------|
| Chronicle library and CLI | Importable ingest, merge, categorize, and verify logic for Chronicle files | `wordpipe/chronicle/`, `pipeline/` |
| Evidence pipeline | Copy-only archival, manifest generation, and integrity verification | `tools/` |
| WordPipe runtime | Import-safe DOCX processing library for TraceLedger-style integration | `wordpipe/` |

`pipeline/` is operator CLI tooling, not a runtime import surface. `_ARCHIVE/`,
`_WORK/`, `_META/`, `_SECURITY/`, `inputs/`, and `WordHorrorStories/` are
preserved evidence or working trees and should not be treated as packaged
runtime code.

**Third-wave reliability status:** commit `777c62a` records five additional
P0/P1 fixes and 270 passing tests; `7d8e114` corrects the CI chain fixture to
use raw Chronicle input. The current work and follow-up gates are tracked in
[`docs/engineering/OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md`](docs/engineering/OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md).

## Quick Start

### Chronicle Library / CLI

```powershell
python -m pip install -e ".[chronicle]"

python -m wordpipe.chronicle.cli.ingest --help
python -m wordpipe.chronicle.cli.merge --help
python -m wordpipe.chronicle.cli.categorize --help
python -m wordpipe.chronicle.cli.verify_ingest --help
```

### Topic Report Workflow

For long Markdown bundles that are not already in Chronicle event format, run a
topic manifest through the generic report runner. The runner resolves the topic
adapter, stages source Markdown, runs the standard Chronicle pipeline, captures
logs/timing, summarizes metrics, compares against the previous run, and emits a
minimal ontology spine.

```powershell
python tools\run_topic_report.py `
  --manifest WordHorrorStories\insurancechatbot\topic_manifest.json `
  --run-id phase13_trend_validation

python tools\run_topic_report.py `
  --manifest WordHorrorStories\pipelinechronicle\topic_manifest.json `
  --run-id phase14_trend_validation
```

Reference runs:
- `WordHorrorStories/insurancechatbot/output/phase13_trend_validation/` (200 events, trend compared)
- `WordHorrorStories/pipelinechronicle/output/phase14_genericity_fix_trend/` (50 events, trend compared, dynamic date headings, manifest-topic summary)
- `WordHorrorStories/*/output/phase15_lineage_validation_v2/` (authoritative collision-protected provenance closeout runs)

Core runner artifacts include `RUN_SUMMARY.md`, `run_metrics.json`,
`topic_run_manifest.json`, `topic_run_ontology.json`, `trend_report.json`,
`trend_report.md`, and `source_attribution.json`. Use
[`docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md`](docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md)
to repeat the same measurement loop for other topics.

### Evidence Pipeline

```powershell
python tools/orchestrate.py --root _WORK/snapshot
python tools/orchestrate.py --root _WORK/snapshot --dry-run
```

### WordPipe Library

```powershell
python -m pip install -e ".[docx,cli]"
python -m pip install -e ".[full]"

wordpipe --in "input.docx" --out "output.docx" --no-flatten
```

Flattening is opt-in: it requires the legacy `MergedpipelineV3` module.
Pass `--flatten` only after installing that module; the example above uses
`--no-flatten` for the dependency-free default path.

## Pre-Push Checks

The third-wave full-suite result was **270 passed** on 2026-07-25. It is
historical evidence, not a substitute for rerunning this command before a new
push. The Chronicle ingest CLI also supports `--allow-undated` when partial
output plus a rejection manifest is explicitly intended.

```powershell
python -m pytest tests -q
python tools/check_root_layout.py --root .
python tools/check_input_catalog.py --root .
python tools/check_architecture_boundaries.py --root .
python tools/docs_link_check.py
python tools/security_scan.py --root . --fail-on-findings
```

## Project Map

| File | Purpose |
|------|---------|
| [`ARCHITECTURE_AND_MODULES.md`](ARCHITECTURE_AND_MODULES.md) | Current comprehensive architecture reference for the three active subsystems |
| [`docs/engineering/REPOSITORY_BOUNDARIES.md`](docs/engineering/REPOSITORY_BOUNDARIES.md) | Packaging, import, test discovery, and directory boundary rules |
| [`docs/engineering/CHRONICLE_CANONICAL_DECISION.md`](docs/engineering/CHRONICLE_CANONICAL_DECISION.md) | Canonical Chronicle package and wrapper migration decision |
| [`docs/engineering/P0_P2_VALIDATION_REPORT.md`](docs/engineering/P0_P2_VALIDATION_REPORT.md) | P0–P2 remediation validation report (stages, claims, CI readiness) |
| [`INDEX.md`](INDEX.md) | Curated map of canonical files, subsystems, evidence, and governance artifacts |
| [`ROADMAP.md`](ROADMAP.md) | Goals, phases, constraints, and milestones |
| [`JOURNAL.md`](JOURNAL.md) | Dated period-based activity journal |
| [`ONTOLOGY_MODEL.md`](ONTOLOGY_MODEL.md) | Formal entity-relationship model |
| [`docs/README.md`](docs/README.md) | Documentation index with role-based entry points |
| [`docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md`](docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md) | Topic-neutral template for repeated report performance checks |
| [`ROOT_ORGANIZATION.md`](ROOT_ORGANIZATION.md) | Root allowlist, placement rules, and generated-output policy |
| [`docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md`](docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md) | Phase evidence crosswalk, corrected flaw claims, and outstanding work |
| [`docs/engineering/OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md`](docs/engineering/OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md) | Prioritized outstanding work, PR-review closure, and refactor/optimization gates |
| [`docs/engineering/PHASE13_17_COMMIT_DRAFT.md`](docs/engineering/PHASE13_17_COMMIT_DRAFT.md) | Phase 13–17 committed scope, trace map, staging guardrails, and closeout commit record |

## Documentation Entry Points

| Role | Start here |
|------|------------|
| Operator | [`ARCHITECTURE_AND_MODULES.md`](ARCHITECTURE_AND_MODULES.md), [`docs/engineering/REPOSITORY_BOUNDARIES.md`](docs/engineering/REPOSITORY_BOUNDARIES.md) |
| Engineer | [`docs/engineering/MODULES_PACKAGES.md`](docs/engineering/MODULES_PACKAGES.md), [`docs/engineering/CHRONICLE_CANONICAL_DECISION.md`](docs/engineering/CHRONICLE_CANONICAL_DECISION.md) |
| Architect | [`docs/TRACELEDGER_INTEGRATION_CONTRACT.md`](docs/TRACELEDGER_INTEGRATION_CONTRACT.md), [`ARCHITECTURE_AND_MODULES.md`](ARCHITECTURE_AND_MODULES.md) |
| Security | [`docs/SECURITY_HARDENING.md`](docs/SECURITY_HARDENING.md) |

## Current Status

| Area | Status |
|------|--------|
| Chronicle dependency contract | Declared through the `chronicle` extra: `pyyaml` and `python-dateutil` |
| Canonical Chronicle package | `ingest`, `merge`, `categorize`, `verify_ingest` have canonical modules (`wordpipe.chronicle`); `index` remains in `pipeline/` (deferred) |
| Topic report runner | Manifest-driven generic runner with adapter registry, trend reports, source attribution, and ontology spine |
| Legacy Chronicle scripts | Compatibility wrappers; not runtime import surfaces |
| WordPipe orchestration | Step-based; read/style failures are fatal |
| Third-wave acceptance | Five P0/P1 findings are covered by `tests/test_acceptance_remediation.py`; the dated full-suite result is 270 passed |
| Test command | `python -m pytest tests -q` — use the latest command/CI result for the current count |
| CI | Windows GitHub Actions workflow in `.github/workflows/ci.yml`: Python 3.10/3.11 base jobs plus a Python 3.11 DOCX-extra integration job |
| Validation report | [`docs/engineering/P0_P2_VALIDATION_REPORT.md`](docs/engineering/P0_P2_VALIDATION_REPORT.md) |
| Root organization | Enforced by `python tools/check_root_layout.py --root .` |
| Corpus inputs | Hash-catalogued under `inputs/`; enforce with `python tools/check_input_catalog.py --root .` |
| Architecture boundaries | Narrow production import directions enforced by `python tools/check_architecture_boundaries.py --root .` |

## Security

- Secrets are env-only (`.env` file, gitignored).
- Use `tools/security_scan.py` for high-confidence pattern scanning.
- See [`docs/SECURITY_HARDENING.md`](docs/SECURITY_HARDENING.md) for policy and incident response.

## License

See `pyproject.toml` for package metadata.
