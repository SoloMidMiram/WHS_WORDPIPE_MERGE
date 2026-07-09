# Chronicle Pipeline — Canonical Source Decision

> **Date:** 2026-07-08  
> **Status:** Adopted  
> **Supersedes:** ambiguous dual location in `pipeline/` and `tools/pipeline-chronicle/`

## Background

The chronicle pipeline (5-stage CLI: ingest → verify → merge → categorize → index)
has accumulated in three generations across four locations:

| Location | Gen | Contents |
|----------|-----|----------|
| `_ARCHIVE/pipeline-chronicle/tools/` | Gen-1 | Frozen archive — not active |
| `tools/pipeline-chronicle/` | Gen-2 | Committed v1 of ingest, merge, verify, categorize, chain.ps1 |
| `pipeline/` | Gen-3 | Post-archival development: refactored categorize v2, new index.py, themes, templates, chain.ps1 v2. ingest/merge/verify copied byte-identical from `tools/pipeline-chronicle/`. |

## File Duplication Audit

| Tool | pipeline/ | tools/pipeline-chronicle/ | Verdict |
|------|-----------|---------------------------|---------|
| `ingest.py` | 16504 bytes (copy) | 16504 bytes (source) | Byte-identical |
| `merge.py` | 17345 bytes (copy) | 17345 bytes (source) | Byte-identical |
| `verify_ingest.py` | Not audited | Exists | Need check |
| `categorize.py` | 17683 bytes (v2) | 13188 bytes (v1) | **Diverged** — v2 is canonical |
| `index.py` | Exists (v1) | Does not exist | Unique to pipeline/ |
| `chain.ps1` | v2 (5-stage) | v1 (4-stage) | **Diverged** — v2 is canonical |

## Decision

1. **Create `wordpipe.chronicle`** as the single importable library for all chronicle
   stage logic (ingest, merge, categorize, verify, index). This follows the same
   pattern as the rest of `wordpipe/` — interfaces in core modules, thin CLI
   wrappers elsewhere.

2. **`pipeline/`** remains the **operator CLI directory** — `chain.ps1` calls thin
   wrappers that delegate to `wordpipe.chronicle.*`. No duplicate `.py` copies live
   here after migration.

3. **`tools/pipeline-chronicle/`** becomes frozen — no new edits. Contains the v1
   snapshots for reference. Tests that currently `sys.path`-hack into this directory
   (verify_ingest) will be updated to import `wordpipe.chronicle.*` in a future phase.

### Compatibility surface

- **Canonical imports (stable):** `from wordpipe.chronicle import ingest, merge, categorize`
- **CLI entry points (deprecated):** `pipeline/*.py` and `tools/pipeline-chronicle/*.py` are
  thin `if __name__ == "__main__"` wrappers only -- not import surfaces.
- **Deferred:** `verify_ingest` tests still import from `tools/pipeline-chronicle/` via
  `sys.path`; `index` is not yet extracted.

4. **Migration source of truth:**
   - Ingest, merge, verify: extract from `tools/pipeline-chronicle/` (committed,
     stable v1 contracts).
   - Categorize, index, chain: extract from `pipeline/` (refactored v2, the working
     versions).

## Timeline

| Slice | What | Source | Status |
|-------|------|--------|--------|
| 3a | `wordpipe.chronicle.ingest` + `wordpipe.chronicle.models` | tools/pipeline-chronicle/ingest.py | Complete |
| 3b | `wordpipe.chronicle.merge` | tools/pipeline-chronicle/merge.py | Complete |
| 3c | `wordpipe.chronicle.categorize` | pipeline/categorize.py (v2) | Complete |
| 3d | Thin wrappers in `pipeline/`; deprecation notices on `tools/pipeline-chronicle/` | All | Complete |
| 3e | Remove duplicate `.py` copies | After one release window | Pending |

## Excluded from packaging

Per the updated `pyproject.toml`, `wordpipe.ai*` and `wordpipe.legacy*` are excluded
from the distribution. Once the `wordpipe.chronicle` package is created, it will be
included in the distribution via the existing `wordpipe*` include glob.
