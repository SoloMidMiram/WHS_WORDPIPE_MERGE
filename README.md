# WHS WordPipe Merge

> Evidence-first document intelligence: transform source documents into traceable,
> reproducible Chronicles, preserve archival evidence, and process DOCX through a modular library.

**Preserve. Structure. Deliver.**

## How WHS works

- **Preserve:** copy-only archival and source integrity verification.
- **Structure:** deterministic document processing into Chronicles, events, lineage and source references.
- **Deliver (research):** provenance-bound context for downstream consumers; fidelity remains unqualified.

Source documents → deterministic extraction and merge → verified event references → experimental context delivery.

## Project status and direction

**Development foundation (package metadata 0.1.0); v0.2 is not release-qualified.** Chronicle provides deterministic ingest, merge, categorization, indexing and source/survivor navigation. Provenance-bound context delivery is experimental: G1 failed qualification; semantic ontology and optional AI assistance are future work. DOCX readiness is assessed separately.

| Current work | Status |
|---|---|
| [MD-01 #15](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/15) | Structural Markdown integrated as opt-in; intended-input qualification pending |
| [CLI-01 #34](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/34) | Installed workflow and evidence-safe publication, characterization only |
| [SEC-01 #17](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/17) | Public release assurance audit |
| [G1 / #8](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/8) | REVISE; B3 deferred pending re-entry evidence; mandatory v0.2 blocker |

[CI baseline: c0a6d1fac7dc, five jobs passed](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/45948321058). This is dated evidence, not a release certification. See the [roadmap](ROADMAP.md) and [delivery gates](docs/engineering/DELIVERY_PHASES_AND_GATES.md) for authoritative scope and priorities.

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

## Quick Start — development checkout

The examples below are checkout workflows, not a standalone wheel-install guarantee. CLI-01 will qualify the distributed driver and complete installed workflow. Use disposable or copied inputs and distinct output paths; never target original evidence.

### Installation modes

| Mode | Status |
|---|---|
| Editable development checkout | Documented below |
| Non-editable wheel | Component replays verified; complete standalone workflow qualification pending CLI-01 |
| Distributed topic driver | Distribution contract undecided; checkout invocation below is not a standalone installation |

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
  --run-id local_demo_insurancechatbot

python tools\run_topic_report.py `
  --manifest WordHorrorStories\pipelinechronicle\topic_manifest.json `
  --run-id local_demo_pipelinechronicle
```

Choose a fresh, unused run ID for each invocation; the examples are checkout-only.

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

Flattening remains enabled by default for backward compatibility and requires
the legacy `MergedpipelineV3` module. Use `--no-flatten` when that module is not
installed; the example above selects this dependency-free path explicitly.

## Contributor validation

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
| Chronicle dependency contract | The `chronicle` extra declares `pyyaml`, `python-dateutil`, and `markdown-it-py`. |
| Canonical Chronicle package | `ingest`, `verify_ingest`, `merge`, `categorize`, and `index` have canonical modules under `wordpipe.chronicle`. `pipeline/index.py` preserves the operator entry point and compatibility exports. |
| Topic report runner | Manifest-driven generic runner with adapter registry, trend reports, source attribution, and ontology spine |
| Legacy Chronicle scripts | Compatibility wrappers; not runtime import surfaces |
| WordPipe orchestration | Step-based; read/style failures are fatal |
| Third-wave acceptance | Five P0/P1 findings are covered by `tests/test_acceptance_remediation.py`; the dated full-suite result is 270 passed |
| Test command | `python -m pytest tests -q` — use the latest command/CI result for the current count |
| CI | [GitHub Actions](.github/workflows/ci.yml) runs Windows tests on Python 3.10 and 3.11, a Windows Python 3.11 job for the DOCX CLI and PowerShell chain integration, and separate Linux build and test jobs on Python 3.11. |
| Validation report | [`docs/engineering/P0_P2_VALIDATION_REPORT.md`](docs/engineering/P0_P2_VALIDATION_REPORT.md) |
| Root organization | Enforced by `python tools/check_root_layout.py --root .` |
| Corpus inputs | Hash-catalogued under `inputs/`; enforce with `python tools/check_input_catalog.py --root .` |
| Architecture boundaries | Narrow production import directions enforced by `python tools/check_architecture_boundaries.py --root .` |

Package metadata is `0.1.0`. Release readiness is tracked in the
[delivery gates](docs/engineering/DELIVERY_PHASES_AND_GATES.md#proposed-release-boundaries).
DOCX save and optional TOC update are implemented steps. Experimental
`ai_headings` and `ai_rewrite` flags have no wired steps; see the
[configuration contract](docs/TRACELEDGER_INTEGRATION_CONTRACT.md).

## Security

- Secrets are env-only (`.env` file, gitignored).
- Use `tools/security_scan.py` for high-confidence pattern scanning.
- See [`docs/SECURITY_HARDENING.md`](docs/SECURITY_HARDENING.md) for policy and incident response.

## License

See `pyproject.toml` for package metadata.
