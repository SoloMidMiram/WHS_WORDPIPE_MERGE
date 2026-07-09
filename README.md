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

## Quick Start

### Chronicle Library / CLI

```powershell
python -m pip install -e ".[chronicle]"

python -m wordpipe.chronicle.cli.ingest --help
python -m wordpipe.chronicle.cli.merge --help
python -m wordpipe.chronicle.cli.categorize --help
python -m wordpipe.chronicle.cli.verify_ingest --help
```

### Evidence Pipeline

```powershell
python tools/orchestrate.py --root _WORK/snapshot
python tools/orchestrate.py --root _WORK/snapshot --dry-run
```

### WordPipe Library

```powershell
python -m pip install -e ".[docx,cli]"
python -m pip install -e ".[full]"

wordpipe --in "input.docx" --out "output.docx"
```

## Pre-Push Checks

```powershell
python -m pytest tests -q
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
| [`INDEX.md`](INDEX.md) | Complete file map of the repository |
| [`ROADMAP.md`](ROADMAP.md) | Goals, phases, constraints, and milestones |
| [`JOURNAL.md`](JOURNAL.md) | Dated period-based activity journal |
| [`ONTOLOGY_MODEL.md`](ONTOLOGY_MODEL.md) | Formal entity-relationship model |
| [`docs/README.md`](docs/README.md) | Documentation index with role-based entry points |

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
| Legacy Chronicle scripts | Compatibility wrappers; not runtime import surfaces |
| WordPipe orchestration | Step-based; read/style failures are fatal |
| Test command | `python -m pytest tests -q` (105 tests as of 2026-07-09) |
| CI | Windows GitHub Actions workflow in `.github/workflows/ci.yml` (matches pre-push checks) |
| Validation report | [`docs/engineering/P0_P2_VALIDATION_REPORT.md`](docs/engineering/P0_P2_VALIDATION_REPORT.md) |

## Security

- Secrets are env-only (`.env` file, gitignored).
- Use `tools/security_scan.py` for high-confidence pattern scanning.
- See [`docs/SECURITY_HARDENING.md`](docs/SECURITY_HARDENING.md) for policy and incident response.

## License

See `pyproject.toml` for package metadata.
