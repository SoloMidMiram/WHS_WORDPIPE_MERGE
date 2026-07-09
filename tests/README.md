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

(The older `tests/test_wordpipe_steps.py` covers similar ground and is kept for transitional coverage.)

Core-only import-safety tests need no extra dependencies.

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
- **Fail** = a change broke an import contract or regression test.

Scripts in `scripts/`, `wordpipe/legacy/`, `_WORK/`, `_ARCHIVE/`, and `inputs/`
are excluded from auto-discovery and are not part of the health signal.
