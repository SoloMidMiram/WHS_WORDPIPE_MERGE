# Modules and Packages Guide

## Public API Surface
Recommended (stable) imports for embedding apps (for example TraceLedger):
- Config and report types:
  - `from wordpipe.core.datatypes import PipelineConfig, RunReport`
- Convenience entrypoint (wires defaults):
  - `from wordpipe import process_docx_v3`
- Interfaces-only orchestration (dependency injection):
  - `from wordpipe.orchestration.pipeline import OrchestrationDeps, WordPipePipeline`
- Event sink helpers:
  - `from wordpipe.events import EventSink, make_sink`

Avoid importing adapter implementations from `wordpipe.adapters` unless you are intentionally selecting a concrete backend.

## Package Layout
Current layered layout:

```text
wordpipe/
  core/             # dependency-light datatypes + OOXML helpers
  interfaces/       # abstract service contracts
  adapters/         # concrete implementations (optional deps)
  orchestration/    # interfaces-only pipeline coordinator
  steps/            # pluggable step engine (flatten, style, segment, finalize, toc)
  plugins/          # optional registry and entrypoint loading
  cli/              # optional CLI entrypoint
  chronicle/        # importable Chronicle stage logic, including index generation
  pipeline/         # compatibility wrappers (legacy import paths)
  flatteners/       # compatibility wrappers (legacy import paths)
```

Excluded from distribution (via `pyproject.toml` `[tool.setuptools.packages.find] exclude`):
- `wordpipe.ai*` — legacy script-style AI modules (moved to `scripts/ai/`)
- `wordpipe.legacy*` — archived legacy snapshots

## Chronicle Package

`wordpipe.chronicle` provides the importable canonical implementation of chronicle pipeline logic.

| Module | Purpose |
|--------|---------|
| `wordpipe.chronicle.ingest` | Raw MD normalisation (mojibake, date parsing, event splitting) |
| `wordpipe.chronicle.merge` | Multi-file merge, dedup, conflict resolution, source coverage |
| `wordpipe.chronicle.categorize` | Theme tagging (v2: negative keywords, dry-run, legacy format) |
| `wordpipe.chronicle.verify_ingest` | Batch ingest verification (parse stderr, classify, report) |
| `wordpipe.chronicle.index` | Pure appendix index extraction, deduplication, and rendering logic |

CLI wrappers (argparse + I/O, delegating to the above modules):
- `wordpipe.chronicle.cli.ingest`
- `wordpipe.chronicle.cli.merge`
- `wordpipe.chronicle.cli.categorize`
- `wordpipe.chronicle.cli.verify_ingest`

Backward-compatible CLI entry points (thin wrappers emitting `DeprecationWarning`,
delegating only when run as `__main__` -- not import-compatible):
- `pipeline/ingest.py`, `pipeline/merge.py`, `pipeline/categorize.py`, `pipeline/verify_ingest.py`
- `tools/pipeline-chronicle/ingest.py`, `tools/pipeline-chronicle/merge.py`, `tools/pipeline-chronicle/categorize.py`, `tools/pipeline-chronicle/verify_ingest.py`

## Compatibility surface

- **Canonical imports (stable):** `from wordpipe.chronicle import ingest, merge, categorize, verify_ingest`
- **CLI entry points (deprecated):** `pipeline/*.py` and `tools/pipeline-chronicle/*.py` --
  each is a thin `if __name__ == "__main__"` wrapper only; do not import functions from them.
- **Deferred:** `index` extraction is not yet migrated to `wordpipe.chronicle`.
- **Complete:** `verify_ingest` is extracted to `wordpipe.chronicle.verify_ingest`;
  `pipeline/verify_ingest.py` and `tools/pipeline-chronicle/verify_ingest.py` are deprecation wrappers.
  Chronicle tests import canonical modules (no `sys.path` manipulation).

## AI Boundary

| Area | Role | Import-safe? |
|------|------|--------------|
| `wordpipe/interfaces/ai.py` | Runtime AI protocols/contracts | Yes |
| `wordpipe/adapters/ai/` | Runtime adapters (`DummySummarizer`, `OpenAISummarizer`) | Yes (OpenAI client passed explicitly; no env discovery) |
| `scripts/ai/` | Manual canaries and legacy script-style AI experiments | N/A — run directly, not imported by runtime |
| `wordpipe/ai/` | Deprecated stub only (`__init__.py` emits `DeprecationWarning`) | Yes — no optional deps at import time |

Public runtime AI imports:
```python
from wordpipe.interfaces.ai import ...       # contracts
from wordpipe.adapters.ai import DummySummarizer  # safe offline adapter
```

Do **not** import from `wordpipe.ai` in new code. Script modules formerly there now live under `scripts/ai/`.

## Import Boundary Rules
Hard rules:
- `import wordpipe` must succeed with only standard library + core available.
- Optional dependencies must be imported lazily inside adapter methods or runtime call sites.
- Core must never import adapters.

Where lazy imports are expected:
- `wordpipe.adapters.docx.*` imports `docx` inside methods.
- `wordpipe.adapters.ai.*` expects an explicit OpenAI client; it does not construct one implicitly.
- Legacy flattening/TOC update imports are attempted only when called and only on Windows where relevant.

### Deprecated import paths
- `from wordpipe.ai import ...` — these are legacy scripts, not public library modules.
  Use `wordpipe.interfaces.ai` or `wordpipe.adapters.ai.*` instead.
- **(Fixed)** `sys.path`-based imports from `tools/pipeline-chronicle/` — canonical imports now use `wordpipe.chronicle.*`.

## Dependency Injection Model
Orchestration contract:
- `OrchestrationDeps` defines the injected services.
- `WordPipePipeline(deps).run(cfg)` runs the pipeline using only interfaces.

Key idea:
- Orchestration depends on `wordpipe.interfaces.*` only.
- Concrete implementations are provided externally by a composition root (for example `wordpipe.orchestrator` or TraceLedger).

## Packaging and Extras
Defined in `pyproject.toml`:
- `wordpipe[core]`: dependency-light (imports only)
- `wordpipe[docx]`: python-docx adapters
- `wordpipe[ai]`: OpenAI adapters
- `wordpipe[cli]`: CLI entrypoint
- `wordpipe[full]`: docx + ai

Example installs:
```powershell
python -m pip install -e ".[core]"
python -m pip install -e ".[docx,cli]"
python -m pip install -e ".[full]"
```

## Plugin Registry
`wordpipe.plugins.registry.CapabilityRegistry` provides:
- `register(name, provider)`
- `get(name)`
- `names()`
- `load_entrypoints(group="wordpipe.plugins")` (explicit opt-in)

Rule:
- Plugins are never loaded automatically at import time.

## Tests and Validation
Authoritative test invocation:
```powershell
python -m pytest tests -q
```

Import-safety test (blocks optional deps and verifies imports):
```powershell
python -m pytest tests/test_import_safety.py -v
```

Chronicle regression tests:
```powershell
python -m pytest tests/test_pipeline_chronicle.py -v
```

Optional compile check (exclude legacy evidence):
```powershell
python -m compileall -q wordpipe -x "wordpipe\\legacy"
```

## See Also
- Architecture spec: `ARCHITECTURE.md`
- Docs index: `docs/README.md`
- TraceLedger integration contract: `docs/TRACELEDGER_INTEGRATION_CONTRACT.md`
- TraceLedger roadmap: `docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md`
- Tools contracts: `docs/PIPELINE_CONTRACTS.md`

