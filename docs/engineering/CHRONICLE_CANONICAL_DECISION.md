# Chronicle Pipeline - Canonical Source Decision

> **Date:** 2026-07-08
> **Status:** Adopted; P0/P1 stabilization updated 2026-07-09
> **Supersedes:** ambiguous dual location in `pipeline/` and `tools/pipeline-chronicle/`

## Background

The Chronicle pipeline is a five-stage CLI flow:

```text
ingest -> verify -> merge -> categorize -> index
```

It accumulated across three generations:

| Location | Generation | Current role |
|----------|------------|--------------|
| `_ARCHIVE/pipeline-chronicle/tools/` | Gen 1 | Frozen archive; not active |
| `tools/pipeline-chronicle/` | Gen 2 | Legacy/reference CLI location; Python entry points are wrappers where canonical modules exist |
| `pipeline/` | Gen 3 | Operator CLI surface, `chain.ps1`, config, templates, and index compatibility wrapper |
| `wordpipe/chronicle/` | Current | Canonical importable Chronicle library |

## Decision

1. `wordpipe.chronicle` is the single importable library for reusable Chronicle stage logic.
2. `pipeline/` remains operator CLI tooling. It is not a runtime import surface.
3. `tools/pipeline-chronicle/` remains a legacy/reference CLI location. Python entry points delegate to canonical modules where migration is complete.
4. `wordpipe.chronicle.index` owns reusable index logic. `pipeline/index.py` retains the operator CLI and compatibility exports.

## Canonical Modules

| Stage | Canonical module | Status |
|-------|------------------|--------|
| Ingest | `wordpipe.chronicle.ingest` | Complete |
| Verify ingest | `wordpipe.chronicle.verify_ingest` | Complete |
| Merge | `wordpipe.chronicle.merge` | Complete |
| Categorize | `wordpipe.chronicle.categorize` | Complete |
| Index | `wordpipe.chronicle.index` | Complete |

## Compatibility Surface

- Stable imports: `from wordpipe.chronicle import ingest, merge, categorize, verify_ingest`
- Stable direct modules: `wordpipe.chronicle.ingest`, `wordpipe.chronicle.merge`, `wordpipe.chronicle.categorize`, `wordpipe.chronicle.verify_ingest`
- Operator compatibility wrappers: `pipeline/*.py` and `tools/pipeline-chronicle/*.py`. Consumer characterization and a separate compatibility decision precede any retirement.
- Wrappers are CLI surfaces only; runtime code must not import from `pipeline/` or `tools/`.

## Dependency Contract

The canonical Chronicle import surface requires the `chronicle` extra:

```powershell
python -m pip install -e ".[chronicle]"
```

That extra owns:

- `pyyaml`
- `python-dateutil`
- `markdown-it-py`

`jinja2` is not part of the `chronicle` extra because the index renderer has fallback formatting.

## Timeline

| Slice | Work | Status |
|-------|------|--------|
| 3a | Extract `wordpipe.chronicle.ingest` and models | Complete |
| 3b | Extract `wordpipe.chronicle.merge` | Complete |
| 3c | Extract `wordpipe.chronicle.categorize` from the v2 path | Complete |
| 3d | Convert Python CLI entry points to wrappers | Complete |
| 3e | Extract `wordpipe.chronicle.verify_ingest` | Complete |
| 3f | Update Chronicle tests to import canonical modules | Complete |
| 3g | Extract `wordpipe.chronicle.index` | Complete |

## Packaging

`wordpipe.chronicle` is included by the existing `wordpipe*` setuptools package
include rule. `wordpipe.ai*` and `wordpipe.legacy*` remain excluded.
