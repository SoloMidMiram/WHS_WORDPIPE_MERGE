# TraceLedger Debug + Enhancement Plan (WordPipe Helper Package)

## See Also
- `docs/README.md`
- `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md`
- `docs/REPOSITORY_REVIEW_MERGED_2026-02-13.md`
- `docs/TRACELEDGER_INTEGRATION_CONTRACT.md`

## Summary
This plan turns the repository into a reusable helper package for TraceLedger by:
- stabilizing a minimal library API
- introducing an EventSink contract (dependency inversion)
- modularizing orchestration into typed steps
- improving portability, robustness, and quality-gate boundaries

## Phase A (P0): Correctness and Hygiene
### A1. Remove duplicate runtime definitions
- Fix `wordpipe/code_style.py` to keep a single `style_code_blocks()` implementation.

### A2. Fix JSONL mkdir guard and import hygiene
- Fix `wordpipe/logging_tools.py` dirname handling (`os.makedirs()` only when dirname non-empty).
- Remove duplicate imports and add minimal redaction hook (optional).

### A3. Reduce silent exception swallowing
- Replace `except Exception: pass` in runtime paths with aggregated warning events (avoid per-paragraph spam).

Acceptance criteria:
- `python -c "import wordpipe"` works.
- Runtime compile checks pass for `wordpipe/` and `tools/` only.

## Phase B (P1): TraceLedger Library Integration
### B1. Add `wordpipe/events.py`
- Define `EventSink` protocol:
  - `emit(level: str, event: str, fields: dict) -> None`
- Provide sinks:
  - `StdlibLoggerSink`
  - `JsonlSink` (portable + safe)
  - `CompositeSink`

### B2. Keep `evt(...)` as a compatibility shim
- Update `wordpipe/logging_tools.py` to delegate to an EventSink.

Acceptance criteria:
- TraceLedger can inject an EventSink adapter.
- WordPipe emits structured events consistently.

## Phase C (P1): Modularize `process_docx_v3` into Step Modules
Create `wordpipe/steps/`:
- `flatten.py`: `flatten_step(cfg, sink) -> FlattenResult`
- `style.py`: `style_step(doc, cfg, sink) -> StyleResult`
- `segment.py`: `segment_step(path, cfg, sink) -> list[Segment]`
- `toc.py`: `toc_step(path, cfg, sink) -> TocResult`
- `finalize.py`: `finalize_step(doc, cfg, sink, working_path) -> None`

Update `wordpipe/orchestrator.py`:
- Keep `process_docx_v3` public, but compose steps.
- Emit capability report once at start.

Acceptance criteria:
- Step units are importable and individually testable.
- Orchestrator failures emit warnings/errors with context.

## Phase D (P1): Refactor AI Runner into Reusable Modules
Split `wordpipe/ai/ailoader.py`:
- `ai/config.py`: env parsing + validation (no side effects)
- `ai/provider_factory.py`: provider construction (OpenAI or Dummy)
- `ai/logging_setup.py`: logger/jsonl output config
- `ai/runtime.py`: canary + run orchestration
- `ai/cli.py`: argparse and optional dotenv loading

Acceptance criteria:
- Importing `wordpipe.ai` does not load dotenv or require OpenAI.
- `python -m wordpipe.ai.cli` runs with env.

## Phase E (P1/P2): Tools Portability and Verification
- Extend relocation map output rows to include `src_rel` and `dst_rel`.
- Update verify to prefer relative paths resolved against `--workspace-root`.
- Add `--portable` verification mode.

Acceptance criteria:
- Verify outputs are stable across machines for same workspace layout.

## Phase F (P2): Duplicate Governance and CI Profiles
- Add `docs/DUPLICATE_POLICY.md`
- Add `tools/duplicate_scan.py` (runtime-only default) producing actionable report.
- Add CI profile scripts:
  - runtime gates (compile + security scan)
  - evidence gates (verify + artifact checks)

Acceptance criteria:
- Runtime CI is low-noise.
- Evidence CI can be run manually when needed.

## Packaging
Add `pyproject.toml` with extras:
- base: `python-docx`
- extras: `openai`, `dotenv`, `httpx`, `win32` (optional)

Acceptance criteria:
- `pip install .` installs and imports `wordpipe`.
- `pip install .[openai]` enables OpenAI provider wiring.
