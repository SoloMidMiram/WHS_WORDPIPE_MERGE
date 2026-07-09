# Repository Boundaries

> **Purpose:** Explicit classification of every top-level directory — what is runtime product, what is tooling, what is archive/evidence, and what is experimental/manual material.
> **See also:** `pyproject.toml` for packaging and pytest config; `docs/engineering/MODULES_PACKAGES.md` for import rules within `wordpipe/`.

---

## Directory Classification

| Directory | Classification | Packaged? | Pytest-collected? | Importable by runtime code? |
|-----------|----------------|-----------|-------------------|-----------------------------|
| `wordpipe/` | Importable runtime library | Yes (`wordpipe*` via setuptools) | No (outside `testpaths`) | N/A (is runtime) |
| `pipeline/` | Chronicle CLI tooling | No | No | No |
| `tools/` | Admin / evidence tools | No | No | No |
| `scripts/` | Manual dev scripts, canaries | No | No (excluded via `norecursedirs`) | No |
| `docs/` | Documentation | No | No | No |
| `_ARCHIVE/` | Immutable evidence / history | No | No (excluded via `norecursedirs`) | No |
| `_WORK/` | Work snapshots | No | No (excluded via `norecursedirs`) | No |
| `_META/` | Snapshot metadata | No | No | No |
| `_SECURITY/` | Security scan reports | No | No | No |
| `_INBOX/` | Reserved for incoming files | No | No | No |
| `inputs/` | Sample / user input documents | No | No (excluded via `norecursedirs`) | No |
| `0209-*` (and similar dated dirs) | Dated pipeline run artifacts | No | No (excluded via `norecursedirs`) | No |
| `WordHorrorStories/` | Content archive (legacy experiments) | No | No (`WordHorrorStories/legacy` excluded via `norecursedirs`) | No |
| `tests/` | Unit tests | No | Yes (`testpaths = ["tests"]`) | No |

---

## Packaging Rules

Configured in `[tool.setuptools.packages.find]` in `pyproject.toml`:

- **Include:** `wordpipe*` — only the runtime library ships.
- **Exclude:** `wordpipe.ai*` (moved to `scripts/ai/`), `wordpipe.legacy*` (archived snapshots).

All other top-level directories (`pipeline/`, `tools/`, `scripts/`, `docs/`, `_ARCHIVE/`, `_WORK/`, `_META/`, `_SECURITY/`, `_INBOX/`, `inputs/`, `0209-*`, `WordHorrorStories/`, `tests/`) are **not packaged**.

---

## Pytest Collection Rules

Configured in `[tool.pytest.ini_options]` in `pyproject.toml`:

- **`testpaths = ["tests"]`** — only the `tests/` directory is scanned for tests.
- **`norecursedirs`** — pytest will not descend into: `_WORK`, `_ARCHIVE`, `inputs`, `0209-*`, `.git`, `wordpipe/legacy`, `WordHorrorStories/legacy`, `scripts`.

This means:
- Manual canary scripts in `scripts/ai/` are never collected.
- Archive and snapshot directories are never inspected.
- Legacy directories are excluded from both packaging and test discovery.
- The authoritative command is `python -m pytest tests -q` (or `python -m pytest -q` from repo root).

---

## Import Boundary Rules

Runtime code (anything under `wordpipe/`) **must never import** from:

| Source | Reason |
|--------|--------|
| `pipeline/.*` | CLI tooling, not a library; may have unguarded optional deps |
| `tools/.*` | Admin / evidence tools with side effects |
| `scripts/.*` | Manual scripts with top-level optional deps |
| `WordHorrorStories/.*` | Legacy content, no import contract |
| `_ARCHIVE/`, `_WORK/`, `_META/`, `_SECURITY/`, `_INBOX/` | Non-code directories |
| `inputs/`, `0209-*` | Data directories, not code |

Runtime code may import from:
- `wordpipe.*` (its own packages)
- `tests/` helpers (only in test context, never in production code)
- `docs/` is documentation-only and not importable.

---

## Rules for Future Files

When adding new files, place them according to their kind:

| Kind | Destination |
|------|-------------|
| Reusable library module | `wordpipe/<area>/` |
| CLI tool / pipeline stage | `pipeline/` or `tools/` |
| Manual dev script or one-off experiment | `scripts/<area>/` |
| Documentation | `docs/<area>/` |
| Sample input data | `inputs/<project>/` |
| Pipeline run output | `0209-<date>/` (or similar dated dir) |
| Evidence / audit artifacts | `_ARCHIVE/<area>/` |
| Work-in-progress snapshots | `_WORK/<area>/` |

---

## Quick Reference

```
wordpipe/              # packaged runtime library      (pytest: no,  import: yes)
pipeline/              # chronicle CLI tooling          (pytest: no,  import: no)
tools/                 # admin/evidence tools           (pytest: no,  import: no)
scripts/               # manual scripts, canaries       (pytest: no,  import: no)
docs/                  # documentation                  (pytest: no,  import: no)
tests/                 # unit tests                     (pytest: yes, import: no)
_ARCHIVE/              # immutable evidence             (pytest: no,  import: no)
_WORK/                 # work snapshots                 (pytest: no,  import: no)
_META/                 # snapshot metadata              (pytest: no,  import: no)
_SECURITY/             # security scan reports          (pytest: no,  import: no)
_INBOX/                # reserved for incoming          (pytest: no,  import: no)
inputs/                # sample/user input documents    (pytest: no,  import: no)
0209-*/                # dated pipeline run artifacts   (pytest: no,  import: no)
WordHorrorStories/     # content archive (legacy)       (pytest: no,  import: no)
```

## Chronicle Pipeline

The canonical implementation of chronicle pipeline logic lives in `wordpipe/chronicle/`:

| Module | Role |
|--------|------|
| `wordpipe/chronicle/ingest.py` | Raw MD normalisation |
| `wordpipe/chronicle/merge.py` | Multi-file merge and dedup |
| `wordpipe/chronicle/categorize.py` | Theme tagging (v2 with negative keywords) |
| `wordpipe/chronicle/cli/` | CLI wrappers (argparse + I/O, delegate to above) |

Backward-compatible CLI entry points (`pipeline/*.py`, `tools/pipeline-chronicle/*.py`)
are thin wrappers that emit `DeprecationWarning` and delegate to `wordpipe.chronicle.cli.*`
_only when run as `__main__`_. They are CLI surfaces, not import surfaces -- do not
import functions from them.

---

## AI Boundary

Three distinct areas handle AI-related code. Do not mix them.

| Area | Purpose | Packaged? | Import-safe? |
|------|---------|-----------|--------------|
| `wordpipe/interfaces/ai.py` | Runtime protocols/contracts | Yes | Yes |
| `wordpipe/adapters/ai/` | Runtime adapters (`DummySummarizer`, `OpenAISummarizer`) | Yes | Yes (optional deps lazy) |
| `scripts/ai/` | Manual canaries, one-off OpenAI scripts, legacy experiments | No | N/A (run directly) |
| `wordpipe/ai/` | **Deprecated** compatibility stub only (`__init__.py`, docs) | No (`wordpipe.ai*` excluded) | Yes (no optional deps) |

Rules:
- Runtime code must use `wordpipe.interfaces.ai` and `wordpipe.adapters.ai` only.
- Manual AI scripts live in `scripts/ai/` and are never imported by `wordpipe/`.
- `from wordpipe.ai import ...` is deprecated; script modules were moved to `scripts/ai/`.
- `scripts/ai/` is excluded from pytest via `norecursedirs`.

---

## See Also

- `pyproject.toml` — Actual packaging and pytest configuration
- `docs/engineering/MODULES_PACKAGES.md` — Internal module structure and import safety
- `docs/engineering/CHRONICLE_CANONICAL_DECISION.md` — Canonical source decision for chronicle pipeline
- `ARCHITECTURE_AND_MODULES.md` — Comprehensive 3-subsystem architecture reference
- `INDEX.md` — Full project file map
