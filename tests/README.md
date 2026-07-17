# WordPipe Tests

## Authoritative test suite

Run from repo root:

```powershell
python -m pytest tests -q
```

This is the canonical test invocation. It runs only tests under `tests/` and
produces the project's health signal.

## Quick check

Import-safety only:

```powershell
python -m pytest tests/test_import_safety.py -v
```

WordPipe orchestration and step behavior:

```powershell
python -m pytest tests/test_steps.py tests/test_orchestration_pipeline.py -v
```

(The older `tests/test_wordpipe_steps.py` has been consolidated into `tests/test_steps.py` and `tests/test_orchestration_pipeline.py`.)

Core-only import-safety tests need no extra dependencies.

Topic adapter preparation:

```powershell
python -m pytest tests/test_prepare_insurancechatbot_chronicle.py -v
python -m pytest tests/test_prepare_generic_markdown_chronicle.py -v
python -m pytest tests/test_run_topic_report.py -v
```

This covers InsuranceChatbot commit-heading parsing, mojibake cleanup, fallback
dates, and staged Markdown compatibility with Chronicle ingestion.

Event identity, survivor integrity, and repeatability:

```powershell
python -m pytest tests/test_phase16_event_identity_characterization.py -v
python -m pytest tests/test_phase16_event_lineage_runner.py -v
python -m pytest tests/test_phase17_survivor_verification.py -v
python -m pytest tests/test_phase17_provenance_stability.py -v
```

The Phase 17 comparator is an operator command, not a pytest discovery surface:

```powershell
python tools/compare_event_provenance_stability.py --baseline-run-dir <phase16-run> --candidate-run-dir <phase17-run> --output-dir <fresh-stability-dir>
```

It must receive a fresh output directory and must not write into either topic
run directory.

Root organization policy:

```powershell
python -m pytest tests/test_root_layout.py -v
python tools/check_root_layout.py --root .
```

Canonical input provenance:

```powershell
python -m pytest tests/test_input_catalog.py -v
python tools/check_input_catalog.py --root .
```

This verifies the 19 active corpus inputs against their recorded SHA-256,
layout, format, and duplicate/derived classifications.

Production import-boundary policy:

```powershell
python -m pytest tests/test_architecture_boundaries.py -v
python tools/check_architecture_boundaries.py --root .
```

This is a static AST boundary guard, not a complete call graph. It ignores
test-only and `TYPE_CHECKING`-only imports and permits only the reviewed path
roles in the checker's centralized exception registry.

## Chronicle pipeline tests

```powershell
python -m pytest tests/test_pipeline_chronicle.py -v
```

Requires the `chronicle` extra (`pyyaml` and `python-dateutil`):

```powershell
python -m pip install -e ".[chronicle]"
```

Chronicle unit tests import canonical modules from `wordpipe.chronicle.*`.
Subprocess integration tests call `tools/pipeline-chronicle/*.py` as `__main__`;
those legacy script locations remain thin compatibility wrappers around the
canonical package.

`verify_ingest` imports through the canonical `wordpipe.chronicle` package.

## What root `python -m pytest -q` means

After the `testpaths = ["tests"]` configuration was added to `pyproject.toml`:

- **Pass** = packaged modules import correctly and the chronicle pipeline logic is regression-tested.
- Historical validation reports retain their dated counts (for example, 105 in
  the P0-P2 report). Use the latest `pytest -q` output for the current count.
- **Fail** = a change broke an import contract or regression test.

Scripts in `scripts/`, `wordpipe/legacy/`, `_WORK/`, `_ARCHIVE/`, and `inputs/`
are excluded from auto-discovery and are not part of the health signal.
