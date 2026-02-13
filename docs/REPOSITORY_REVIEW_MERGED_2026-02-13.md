# Repository Review (Merged): Modularity, Integration, Robustness, Duplication, Optimization
Date: 2026-02-13

## See Also
- `docs/README.md`
- `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md`
- `docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md`
- `docs/TRACELEDGER_INTEGRATION_CONTRACT.md`

## Executive Summary
This repository is already strong in its **tools pipeline**: it has a consistent stage contract (`StageResult` / `StagePaths`), copy-only reorg semantics, and unusually complete operational documentation.

The highest risks are concentrated in the **runtime package (`wordpipe/`) boundary clarity**:
- Runtime code is mixed alongside intentionally historical/evidence trees (`_WORK/`, `_ARCHIVE/`, `wordpipe/legacy/`), which can pollute quality gates and portability.
- Some runtime modules blend multiple responsibilities (flattening, styling, segmentation, TOC, telemetry) into single functions.
- Several modules rely on broad exception swallowing and script-style imports, which weakens reliability when consumed as a library.

The recommended direction for TraceLedger is to treat WordPipe as a **library-first helper package** with:
- a stable API (`PipelineConfig`, `RunReport`, `process_docx_v3`)
- explicit dependency inversion for logging/event emission (EventSink)
- runtime-only quality gates by default, with separate evidence checks.

## Current Architecture Snapshot
### Tools Pipeline (`tools/`)
Core characteristics:
- Stage contract: `tools/pipeline_contracts.py` defines `StageResult`, strict-mode escalation, and standardized missing-input errors.
- Pipeline stages: `make_manifest.py -> plan_legacy_reorg.py -> apply_legacy_reorg.py -> build_legacy_index.py -> verify_integrity.py`.
- Orchestration: `tools/orchestrate.py` composes stages and supports `--dry-run`.
- Security: `tools/security_scan.py` provides a high-confidence secret scan.

### Runtime Pipeline (`wordpipe/`)
Core characteristics:
- Public API: `wordpipe/__init__.py` exports `PipelineConfig`, `RunReport`, and `process_docx_v3`.
- Orchestration: `wordpipe/orchestrator.py` runs flatten + styles + segmentation + save + TOC update.
- Utilities: `wordpipe/core/*` provides datatypes, styles, segmentation and OOXML helpers.
- AI area: `wordpipe/ai/*` includes provider helpers, document reorganizer, and an AI runner (`ailoader.py`).

### Evidence / Archives
These trees are intentionally historical:
- `_WORK/` (snapshot extraction)
- `_ARCHIVE/` (manifests, plans/maps, logs/reports)
- `wordpipe/legacy/` and `WordHorrorStories/legacy/` (bucketized legacy copies)
- `WordHorrorStories/chatgpt-chronicle/*` (canon/evidence)

## Boundary Clarity: Runtime vs Evidence
Recommended classification:
- **runtime (default gates)**:
  - `tools/`
  - `wordpipe/`
  - `WordHorrorStories/autobiography/`
- **evidence (preserve; exclude from default gates)**:
  - `_WORK/`
  - `_ARCHIVE/`
  - `wordpipe/legacy/`
  - `WordHorrorStories/chatgpt-chronicle/sources/raw/**`
- **optional (ops / docs)**:
  - `docs/`
  - `WordHorrorStories/instructions/`

## Findings + Recommendations (Merged)
Severity convention:
- **P0**: correctness/safety portability risk; fix immediately
- **P1**: structural issue blocking reuse/testing; fix next
- **P2**: optimization and governance improvements; schedule

### 1) Modularity
**Finding (P1): `wordpipe/orchestrator.py` mixes multiple responsibilities.**
- Evidence: `wordpipe/orchestrator.py` `process_docx_v3` runs flattening, styles, segmentation, save/cleanup, and TOC update.
- Why it matters: makes testing hard, complicates extension (AI injection, per-segment tables), hides integration failures.
- Recommendation: split into step modules (`steps/flatten`, `steps/style`, `steps/segment`, `steps/finalize`, `steps/toc`) returning typed results.

**Finding (P0): `wordpipe/code_style.py` contains duplicate function definitions.**
- Evidence: `wordpipe/code_style.py` defines a no-op `style_code_blocks()` and later a real implementation.
- Why it matters: signals weak hygiene; increases risk of calling the wrong implementation in refactors.
- Recommendation: remove placeholder definition; keep one authoritative implementation.

**Finding (P1): AI runner is script-centric and import-fragile.**
- Evidence: `wordpipe/ai/ailoader.py` uses non-package imports (`from helpers import ...`) and includes orchestration, provider build, dotenv loading.
- Why it matters: breaks when imported as a library or run as `python -m`.
- Recommendation: split into `ai/config.py`, `ai/provider_factory.py`, `ai/logging_setup.py`, `ai/runtime.py`, `ai/cli.py` and convert imports to package-safe.

### 2) Integration Consistency
**Finding (P1): Two orchestration layers with different contracts.**
- Evidence: `tools/orchestrate.py` (workspace pipeline) vs `wordpipe/orchestrator.py` (doc transform pipeline).
- Why it matters: TraceLedger wants one consistent "run envelope" and event schema.
- Recommendation: add a shared runtime event sink contract and unify event emission in runtime.

**Finding (P1): Optional dependency capabilities are not surfaced.**
- Evidence: TOC update uses optional `MergedpipelineV3` import with broad fallback.
- Why it matters: operators don't know if COM/TOC/AI is active.
- Recommendation: emit a one-time capability report per run.

### 3) Robustness
**Finding (P0): Silent exception swallowing.**
- Evidence: multiple `except Exception: pass` patterns in runtime pipeline and AI runner.
- Why it matters: hides actionable failures and produces "success" runs with degraded behavior.
- Recommendation: replace silent catches with warning events (aggregate counts to avoid spam).

**Finding (P0): JSONL logging mkdir bug on filename-only paths.**
- Evidence: `wordpipe/logging_tools.py` calls `os.makedirs(os.path.dirname(jsonl_path), exist_ok=True)` which breaks if dirname is empty.
- Why it matters: crashes when passing `jsonl_path="run.jsonl"` from CWD.
- Recommendation: guard dirname creation; only mkdir when dirname is non-empty.

### 4) Duplicate Governance
**Finding (P2): Duplicate reporting exists but no policy.**
- Evidence: `tools/verify_integrity.py` reports duplicate hash groups.
- Why it matters: duplicates in evidence are fine; duplicates in runtime can be a bug. Policy needed for CI signal.
- Recommendation: define duplicate classes and CI enforcement for runtime-only duplicates.

### 5) Optimization
**Finding (P2): Segmentation heading path computation is potentially O(n^2).**
- Evidence: `wordpipe/core/segment.py` `build_hpath()` scans from 0..p_idx for every segment boundary.
- Why it matters: slows on large docs.
- Recommendation: precompute heading context once, preserve existing semantics.

### 6) Security Posture
**Finding (P0/P1): Secrets must stay env-only and must be scanned before commit.**
- Evidence: `tools/security_scan.py` exists; `.env.example` exists; `.gitignore` ignores `.env` and local scan outputs.
- Recommendation: enforce `tools/security_scan.py --fail-on-findings` in runtime CI profile and document rotation + history purge steps.

## Prioritized Roadmap
### Quick wins (1-2 days)
- Remove duplicate code definitions in runtime files.
- Fix JSONL path dirname guard and reduce silent exception swallowing.
- Convert `wordpipe/ai/*` imports to package-safe form; move dotenv loading into CLI only.

### Medium (1 sprint)
- Split `process_docx_v3` into typed step functions.
- Introduce `EventSink` contract with stdlib + JSONL implementations.
- Add portable verification mode and relative path fields to relocation map.

### Longer-term (1-2 weeks)
- Duplicate policy + runtime-only duplicate gate.
- Segmentation optimization without semantic changes.
- Optional hashing cache/parallel hashing for verify stages.

## Suggested CI Gate Profiles
### `runtime` (default)
- compile/lint/test runtime-only trees
- secret scan
- orchestrator dry-run

### `evidence` (manual/optional)
- run verify integrity on evidence trees and compare generated reports
