# Logic Flow (Before vs After): Tools + WordPipe + TraceLedger

## System Boundary
This workspace contains two internal subsystems plus an external consumer:
- `tools/` pipeline: evidence-oriented archival reorg + integrity verification.
- `wordpipe/` runtime: DOCX transformation pipeline (flatten, style, segment, finalize).
- `TraceLedger` (external): broader chronology logger project that will consume WordPipe as a helper library.

## Before (Current State)
### Control Flow
- Operators run the `tools/` pipeline either stage-by-stage or via `tools/orchestrate.py`.
- `wordpipe/` runtime processing is orchestrated via `wordpipe/orchestrator.py` (`process_docx_v3`).
- These orchestration layers are separate and currently have different "run envelope" conventions.

### Data Flow (Tools)
```text
_WORK/snapshot
  -> tools/make_manifest.py
     -> _ARCHIVE/manifests/manifest.jsonl

manifest.jsonl
  -> tools/plan_legacy_reorg.py
     -> _ARCHIVE/move_maps/relocation_plan.jsonl

relocation_plan.jsonl + snapshot
  -> tools/apply_legacy_reorg.py
     -> _ARCHIVE/move_maps/relocation_map.jsonl
     -> wordpipe/** and WordHorrorStories/** (copy-only)
     -> _ARCHIVE/logs/conflicts.log

relocation_map.jsonl + legacy trees
  -> tools/build_legacy_index.py
     -> legacy index docs

manifest + plan/map + snapshot
  -> tools/verify_integrity.py
     -> verify + consistency + immutability reports
```

### Data Flow (WordPipe Runtime)
```text
PipelineConfig(in_path, out_path, options...)
  -> wordpipe.process_docx_v3(...)
     -> flattened work doc (optional)
     -> styled output doc
     -> segments metadata (RunReport)
     -> optional TOC update (platform dependent)
```

### Observability
- Tools pipeline emits append-only logs and deterministic reports under `_ARCHIVE/logs/`.
- WordPipe runtime emits events via `evt(...)` helpers; historically these were logger+JSONL writers.

## Jobs and Data Ownership
- Evidence pipeline job (tools):
  - Runs as CLI stages that produce audit artifacts under `_ARCHIVE/` and copy-only destination trees under `wordpipe/` and `WordHorrorStories/`.
  - Outputs are evidence/audit oriented (append-only logs + replace-on-run reports).
- Runtime job (WordPipe):
  - Runs as an in-process library for DOCX transformation.
  - Outputs are transform products and structured events (plus an in-memory `RunReport` return).
- TraceLedger job (external consumer):
  - Owns chronology/event storage, run envelopes, and cross-run correlation.
  - Consumes WordPipe as a helper library and provides an event sink adapter.

## Argument and Config Passing (TraceLedger vs Tools)
Tools pipeline:
- Configuration is passed as CLI flags and implicit working-directory behavior in orchestrated runs.
- `tools/orchestrate.py` uses `--workspace-root` as subprocess `cwd` and passes `--root/--snapshot-root` only.

TraceLedger runtime consumption:
- Configuration is passed as explicit config objects (for example `PipelineConfig`) and explicit paths (no probing relative to CWD).
- Observability is provided via an injected sink (`EventSink`); `wordpipe/events.py` is the current implementation direction.

## After (Target State for TraceLedger)
### Control Flow
- TraceLedger calls WordPipe as a library API, not as a subprocess.
- Tools pipeline remains CLI-driven and evidence/audit oriented.
- WordPipe runtime emits structured events to a TraceLedger-provided sink.

### Data Flow
- TraceLedger passes explicit paths and configuration.
- WordPipe emits events and returns a typed `RunReport`.
- Tools pipeline continues to produce evidence artifacts for archival verification workflows.

### Key Design Contracts (Referenced)
- Event sink contract:
  - `docs/TRACELEDGER_INTEGRATION_CONTRACT.md`
- Debug/enhancement roadmap:
  - `docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md`
- Consolidated architecture review:
  - `docs/REPOSITORY_REVIEW_MERGED_2026-02-13.md`

## Integration Map (Textual)
Runtime integration wiring:
```text
TraceLedger
  -> wordpipe.process_docx_v3(cfg, sink=TraceLedgerSink, artifacts=...)
     -> returns RunReport
     -> emits structured events (INFO/WARNING/ERROR)
```

Evidence pipeline wiring:
```text
Operator/CI
  -> python tools/orchestrate.py --root _WORK/snapshot
     -> produces and verifies audit/evidence artifacts under _ARCHIVE/
```

## Compatibility + Migration Notes
- Stable runtime exports remain:
  - `wordpipe.PipelineConfig`, `wordpipe.RunReport`, `wordpipe.process_docx_v3`
- Legacy entrypoints remain but become thinner shims over time:
  - `process_docx_v3_simple`
  - `evt(...)` remains as a compatibility wrapper around the EventSink model.
- Tools pipeline doc paths remain stable; new docs are additive.

## Acceptance Criteria
- `docs/README.md` provides a clear reading path for operator, engineer, architect, and security roles.
- This doc references (does not duplicate) the TraceLedger enhancement plan.
- Before/after control flow and data flow are understandable without additional context.
