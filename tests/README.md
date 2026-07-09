# WordPipe Tests

## Authoritative test suite

Run from repo root:

```powershell
python -m pytest tests -q
```

This is the canonical test invocation. It runs only tests under `tests/` and
produces the project's health signal.

## Quick check (import safety only)

```powershell
python -m pytest tests/test_import_safety.py -v
```

## Chronicle pipeline tests

```powershell
python -m pytest tests/test_pipeline_chronicle.py -v
```

Requires `pyyaml` (and optionally `dateutil`) for the chronicle fixtures.
Chronicle unit tests import canonical modules from `wordpipe.chronicle.*`.
Subprocess integration tests call `tools/pipeline-chronicle/*.py` as `__main__`
and therefore require `wordpipe` to be installed:

```powershell
pip install -e .
```

The `verify_ingest` test helper still imports from `tools/pipeline-chronicle/`
via `sys.path` (to be migrated in a future phase).

## What root `python -m pytest -q` means

After the `testpaths = ["tests"]` configuration was added to `pyproject.toml`:

- **Pass** = all packaged modules import correctly, chronicle pipeline logic is
  regression-tested.
- **Fail** = a change broke an import contract or regression test.

Scripts in `scripts/`, `wordpipe/legacy/`, `_WORK/`, `_ARCHIVE/`, and `inputs/`
are excluded from auto-discovery and are not part of the health signal.
