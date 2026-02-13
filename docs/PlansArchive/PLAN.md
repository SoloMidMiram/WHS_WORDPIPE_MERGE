# Merge Reviews + TraceLedger-Ready Debug/Enhancement Roadmap

## Summary
Produce one consolidated, organized review document that merges your v1/v2/v3 reviews into a single coherent architecture assessment, then define a decision-complete debug + enhancement plan to evolve this repo into a **reusable helper package** inside the broader chronology logger project **TraceLedger**.

You chose:
- TraceLedger integration style: **Library API**
- Packaging: **Yes (pyproject + extras)**
- Quality gates: **Configurable profiles** (`runtime` default, `evidence` optional)

---

## Deliverables
1. **Merged review file**
- Create: `docs/REPOSITORY_REVIEW_MERGED_2026-02-13.md`
- Audience: mixed (exec summary + engineering actionable items)
- Inputs: your v1/v2/v3 text plus current repo reality (file/path evidence)

2. **Enhancement plan file**
- Create: `docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md`
- Contains: phased roadmap, interfaces, module boundaries, acceptance criteria, and CI profiles.

3. **(Optional but recommended) TraceLedger integration contract**
- Create: `docs/TRACELEDGER_INTEGRATION_CONTRACT.md`
- Defines event sink interface, run report envelope, and dependency inversion rules.

---

## Phase 1 — Ground Truth (Repo-Facts-Only, No Design Yet)
### 1.1 Confirm key current architecture facts (evidence-backed)
Use repo evidence (paths + excerpts) to anchor the merged review:
- `wordpipe/code_style.py` has duplicate `style_code_blocks()` definitions (one no-op placeholder, one real).
- `wordpipe/orchestrator.py` (`process_docx_v3`) mixes flattening, styling, segmentation, save, cleanup, TOC update, and telemetry.
- `wordpipe/ai/ailoader.py` is script-centric and uses fragile imports (`from helpers import ...`) and silent exception swallowing.
- `wordpipe/logging_tools.py` has duplicate imports and calls `os.makedirs(os.path.dirname(jsonl_path))` which breaks for filename-only paths.
- `wordpipe/core/segment.py` uses `build_hpath()` scanning from start per segment boundary (O(n^2) worst-case).
- Tools pipeline already has `StageResult`/`StagePaths` in `tools/pipeline_contracts.py` and consistent CLI patterns in `tools/`.

Acceptance criteria:
- Each “finding” in the merged review has at least one concrete pointer (file path + what it does).

---

## Phase 2 — Create the Merged Review Document
### 2.1 File structure (single organized narrative)
`docs/REPOSITORY_REVIEW_MERGED_2026-02-13.md` sections:

1. **Executive Summary**
- What is strong today (stage contracts, copy-only apply, documentation posture)
- What is risky (runtime vs evidence mixing, fragile AI module structure, portability and silent exceptions)

2. **Current Architecture Snapshot**
- Tools pipeline: `tools/*` stage contract + artifacts
- Runtime pipeline: `wordpipe/*`
- Evidence/archives: `_WORK/`, `_ARCHIVE/`, `wordpipe/legacy/`, `WordHorrorStories/chatgpt-chronicle/*`

3. **Boundary Clarity: Runtime vs Evidence**
- Explicitly classify directories into:
  - `runtime` (must compile/lint/test)
  - `evidence` (must be preserved; excluded from most gates)
  - `optional` (tools/ops)

4. **Findings + Recommendations (merged from v1/v2/v3)**
Grouped exactly by themes from your drafts:
- Modularity
- Integration consistency (tools orchestrate vs wordpipe orchestrator)
- Robustness (silent catches, portability, warning semantics)
- Duplicate governance (policy + tiers)
- Optimization (hashing, segmentation complexity, scan reuse)
- Security posture (env-only; scanning; history hygiene)

Each finding includes:
- Evidence reference (file path)
- Why it matters
- Concrete recommendation
- Suggested severity: `P0/P1/P2`

5. **Prioritized Roadmap**
- Quick wins (1–2 days)
- Medium (1 sprint)
- Longer-term (1–2 weeks)
Aligned with TraceLedger adoption constraints.

6. **Suggested CI Gate Profiles**
- `runtime` profile (default)
- `evidence` profile (optional/manual)

Acceptance criteria:
- Review replaces v1/v2/v3 without losing any unique recommendation.
- Review explicitly flags which items are “repo reality” vs “future design”.

---

## Phase 3 — TraceLedger-Oriented Debug + Enhancement Plan (Decision Complete)
### 3.1 Define the target: “WordPipe as a helper library inside TraceLedger”
Core constraint: TraceLedger should be able to call WordPipe **as a library**, not depend on “run from repo root” behavior.

#### Public API (stabilize)
Expose a minimal, stable surface:
- `wordpipe.PipelineConfig`
- `wordpipe.RunReport`
- `wordpipe.process_docx_v3(cfg, sink=..., artifacts=...) -> RunReport` (retain name for compat, but refactor internals)
- `wordpipe.process_docx_v3_simple(...)` remains as a thin wrapper (deprecate later)

### 3.2 Event model: invert dependency to TraceLedger
Add `wordpipe/events.py`:
- `class EventSink(Protocol): def emit(self, level: str, event: str, fields: dict) -> None`
Provide implementations:
- `StdlibLoggerSink` (writes to `logging.Logger`)
- `JsonlSink` (writes to JSONL safely)
- `CompositeSink`

Update `wordpipe/logging_tools.py`:
- Make it either:
  - a compatibility wrapper that delegates to `EventSink`, or
  - replaced by `events.py` and kept as deprecated shim.

Acceptance criteria:
- No WordPipe runtime module imports TraceLedger.
- TraceLedger can provide an EventSink adapter.

### 3.3 Modular refactors (concrete file/module plan)

#### 3.3.1 Fix immediate correctness/hygiene (P0)
- `wordpipe/code_style.py`
  - Remove the duplicate no-op `style_code_blocks` definition.
  - Replace broad `except Exception: pass` when applying style with narrow exceptions + warning event via sink.
- `wordpipe/logging_tools.py`
  - Remove duplicate imports.
  - Guard `os.makedirs()` call: only mkdir when dirname is non-empty.
  - Add optional redaction hook (reusing pattern from tools, but keep WordPipe independent).
- `wordpipe/core/datatypes.py`
  - Fix minor lint hygiene issues (duplicate imports, naming).
- `wordpipe/ai/*`
  - Convert imports to package-safe (`from wordpipe.ai.helpers import ...` or relative imports).

#### 3.3.2 Split `process_docx_v3` into step modules (P1)
Create internal step functions returning typed results:
- `wordpipe/steps/flatten.py`: `flatten_step(cfg, sink) -> FlattenResult`
- `wordpipe/steps/style.py`: `style_step(doc, cfg, sink) -> None`
- `wordpipe/steps/segment.py`: `segment_step(path, cfg, sink) -> list[Segment]`
- `wordpipe/steps/finalize.py`: `finalize_step(doc, cfg, sink) -> None`
- `wordpipe/steps/toc.py`: `toc_step(path, cfg, sink) -> TocResult` (capability-driven)

Update `wordpipe/orchestrator.py`:
- Keep `process_docx_v3` as orchestrator that composes steps and emits one “capability report” event at start:
  - `com_available`, `openai_available`, `dotenv_available`, etc.

Acceptance criteria:
- Each step is unit-testable in isolation.
- Orchestrator has no broad silent exception swallowing; failures become warnings/errors with context.

#### 3.3.3 Refactor `wordpipe/ai/ailoader.py` into reusable modules (P1)
Split into:
- `wordpipe/ai/config.py`: env parsing + validation (no side effects)
- `wordpipe/ai/provider_factory.py`: constructs OpenAI/Dummy provider (no logging setup)
- `wordpipe/ai/logging_setup.py`: logger/jsonl output configuration
- `wordpipe/ai/runtime.py`: canary + reorganize orchestration (pure functions as much as possible)
- `wordpipe/ai/cli.py`: argparse-only; optional dotenv loading (only here)

Acceptance criteria:
- `wordpipe/ai` can be imported safely in any context (no dotenv auto-load at import time).
- “silent except” blocks replaced with structured warnings.

#### 3.3.4 Portability and verification (P1/P2)
Tools side (to support cross-machine TraceLedger runs):
- Extend `tools/apply_legacy_reorg.py` relocation map rows to include:
  - `src_rel`, `dst_rel` (in addition to current abs fields)
- Update `tools/verify_integrity.py` to prefer `*_rel` resolved against `--workspace-root`, using `*_abs` as diagnostic-only.
- Add `--portable` flag to verify to ignore absolute-path drift.

Acceptance criteria:
- Verify reports are stable across machines for the same workspace layout.

#### 3.3.5 Duplicate governance (P2)
Add `docs/DUPLICATE_POLICY.md` and a small detector:
- `tools/duplicate_scan.py` (runtime-only profile by default):
  - classify duplicates into `expected_mirror`, `expected_boilerplate`, `actionable_duplicate`
  - emit `duplicate_actionable.json`

Acceptance criteria:
- CI can fail only on actionable duplicates in runtime trees.

#### 3.3.6 Optimization (P2)
- Optimize `wordpipe/core/segment.py` to linear-time heading context:
  - Precompute heading state in one pass and reuse for segments.
- Tools verify hashing:
  - Optional bounded parallel hashing and/or hash cache (defer if complexity too high for first packaging cut).

Acceptance criteria:
- Segmentation runtime improves measurably on large docs without changing segment semantics.

---

## Phase 4 — Packaging + CI Profiles (TraceLedger Consumption)
### 4.1 Packaging (pyproject + extras)
Add `pyproject.toml` and extras:
- Base: minimal dependencies for non-AI/non-Windows pipeline
- Extras:
  - `openai`
  - `dotenv`
  - `win32`/`com` support if applicable
  - `tools` extras if you want tools pipeline as installable console scripts

Acceptance criteria:
- `pip install .` installs `wordpipe` cleanly.
- `pip install .[openai]` enables AI provider.
- Evidence trees are not required for installation/tests.

### 4.2 CI profiles
Add two runnable profiles (PowerShell scripts or documented commands):
- `runtime`:
  - compile/lint/test only `tools/`, `wordpipe/`, `WordHorrorStories/autobiography/`
- `evidence`:
  - runs `tools/verify_integrity.py` and checks audit artifacts

Acceptance criteria:
- Default CI has low noise and high signal.

---

## Security Note (Non-Public Concern)
This plan does not change repo visibility. “Public exposure” only happens if you change GitHub visibility manually.
However, for least-risk operation, the plan will include a final “remote refs audit” step to ensure no leftover branches/tags point at sensitive historical commits after rewrites.

---

## Test Cases and Scenarios (Engineering)
1. Import safety: `python -c "import wordpipe"` works without dotenv/openai installed.
2. Orchestrator refactor: steps unit-testable with a fake `EventSink`.
3. AI modules: `wordpipe.ai.config` parses env without side effects; CLI loads dotenv optionally.
4. Segment optimization: segment boundaries unchanged vs baseline fixtures.
5. Tools portability: verify passes on a different machine path root using `*_rel`.
6. CI profiles: `runtime` passes without `_WORK/` and `_ARCHIVE/` present.

---

## Assumptions and Defaults
- New docs are English.
- TraceLedger will provide its own event storage/chronology ledger; WordPipe only emits structured events.
- Backward compatibility is preserved via shims (`wordpipe/pipeline/*` re-exports, `process_docx_v3_simple` wrapper).
- Evidence trees remain preserved and excluded from default runtime quality gates.
