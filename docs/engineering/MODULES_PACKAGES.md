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
  plugins/          # optional registry and entrypoint loading
  cli/              # optional CLI entrypoint
  pipeline/         # compatibility wrappers (legacy import paths)
  flatteners/       # compatibility wrappers (legacy import paths)
```

## Import Boundary Rules
Hard rules:
- `import wordpipe` must succeed with only standard library + core available.
- Optional dependencies must be imported lazily inside adapter methods or runtime call sites.
- Core must never import adapters.

Where lazy imports are expected:
- `wordpipe.adapters.docx.*` imports `docx` inside methods.
- `wordpipe.adapters.ai.*` expects an explicit OpenAI client; it does not construct one implicitly.
- Legacy flattening/TOC update imports are attempted only when called and only on Windows where relevant.

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
Import-safety test (blocks optional deps and verifies imports):
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
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

