# TraceLedger Integration Contract (WordPipe Helper)

## See Also
- `docs/README.md`
- `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md`
- `docs/REPOSITORY_REVIEW_MERGED_2026-02-13.md`
- `docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md`

## Purpose
Define how TraceLedger should consume this repository as a helper package without relying on repo-root execution context.

## Design Goals
- Library-first: TraceLedger calls Python functions, not subprocesses, for runtime processing.
- Dependency inversion: WordPipe emits structured events; TraceLedger decides where they go.
- Portable paths: runtime outputs and evidence reports should not be tied to absolute machine paths.
- Backward compatibility: keep existing entrypoints while introducing new contracts.

## Stable Public API Surface (WordPipe)
The minimum stable interface TraceLedger should depend on:
- `wordpipe.PipelineConfig`
- `wordpipe.RunReport`
- `wordpipe.process_docx_v3(cfg, sink=..., artifacts=...) -> RunReport`

Optional compatibility helper:
- `wordpipe.process_docx_v3_simple(...)`

### Config flag status

| Flag | Status | Notes |
|------|--------|-------|
| `do_flatten` | **Stable** | |
| `prefer_win32` | **Stable** | Falls back to XML flattener on non-Windows |
| `per_segment_tables` | **Experimental** | Flag accepted but no step wired yet |
| `ai_headings` | **Experimental** | Flag accepted but no step wired yet |
| `ai_rewrite` | **Experimental** | Flag accepted but no step wired yet |
| `max_rewrite_per_section` | **Experimental** | Flag accepted but no step wired yet |
| `limit_pages` | **Stable** | |

## Event Sink Interface
TraceLedger should provide an event sink adapter to capture WordPipe runtime events.

Contract:
- `EventSink.emit(level: str, event: str, fields: dict) -> None`

Rules:
- `level` uses `INFO|WARNING|ERROR` strings.
- `event` is a stable short string key (`start`, `flatten_begin`, `flatten_fail`, `done`, etc.).
- `fields` is JSON-serializable.
- WordPipe must not import TraceLedger. TraceLedger may import WordPipe.

## Artifact and Path Policy
- TraceLedger passes explicit paths in `PipelineConfig` (no probing relative to CWD).
- WordPipe treats absolute paths as diagnostic only in evidence reports; relative derivation must be possible.
- Evidence trees (`_WORK/`, `_ARCHIVE/`) are optional at runtime and must not be required for library import.

## Capability Reporting
WordPipe emits a one-time capability report at the start of a run:
- `com_available`
- `toc_updater_available`
- `openai_available`
- `dotenv_available`

TraceLedger should record this once per run for debuggability.

## Versioning and Compatibility
- The Python package distribution name may differ from import module name.
- Breaking changes require major version bump and a deprecation window.
