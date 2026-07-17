# Repository Organization & Modularization Plan

> **Date:** 2026-02-14 (Jalali: 1404-11-25)
> **Purpose:** Comprehensive plan for goals, constraints, integrations, and modularization of the WHS WordPipe Merge repository.

> **Current-status note (2026-07-16):** This file preserves the original
> modularization intent. Current placement rules are authoritative in
> `ROOT_ORGANIZATION.md`; implementation status and corrected historical flaw
> claims are in `docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md`.

---

## 1. Ultimate Goal

Transform this workspace into a **maintainable, evidence-backed, ontology-grounded project** where:

- **`tools/`** evidence pipeline is reliable, portable, and independently runnable
- **`wordpipe/`** is a clean, import-safe library consumable by TraceLedger
- **Topic adapters** can stage non-Chronicle Markdown bundles into measurable report runs
- **Documentation** is accurate, verifiable, and cross-referenced
- **An ontological model** describes the project's structure, phases, claims, and evidence
- **Journal and roadmap** anchor planning against disruption and chaos

---

## 2. Core Values

| # | Value | Meaning |
|---|-------|---------|
| V1 | **Evidence over opinion** | Every claim should point to a file, a log, or a run |
| V2 | **Portability** | No absolute paths, no environment-dependent behavior |
| V3 | **Idempotency** | Re-running the same pipeline produces the same result |
| V4 | **Non-destructive** | Copy-only, conflict-safe, append-only where historical |
| V5 | **Backward compatibility** | Changes must not break existing stage contracts |
| V6 | **Traceability** | Every phase, task, and decision links to a journal entry |
| V7 | **Import safety** | `import wordpipe` must work with only stdlib available |
| V8 | **Separation of concerns** | tools/ (pipeline) and wordpipe/ (library) are independent |
| V9 | **Measured iteration** | Report quality changes are compared through stable run metrics, not impressions |

---

## 3. Constraints

| # | Constraint | Impact | Mitigation |
|---|------------|--------|------------|
| C1 | Limited/unstable internet access | Cannot rely on pip install, GitHub API, or external NLP services | All tooling must be offline-capable; use stdlib where possible |
| C2 | Windows environment with PowerShell | Tooling must be Win32-compatible | Use forward slashes in paths; test on both shells |
| C3 | Existing massive doc set (22 .md files in docs/) | Risk of redundancy, contradiction, and path rot | VERIFICATION.md cross-references all claims; stale docs get flagged |
| C4 | Absolute paths (F:\Git\...) embedded in docs | Breaks for any other clone location or user | Already fixed (Phase 8); PATH_FIX_LOG.md documents remaining evidence paths |
| C5 | Evidence files in _ARCHIVE/ are append-only | Must preserve historical evidence | Pipeline stages must not modify _ARCHIVE/ content |
| C6 | _WORK/snapshot is immutable input | Must not modify source snapshot | All pipeline stages are copy-only from _WORK/ |
| C7 | 60+ mirror pairs between active and snapshot | Confusion about authoritative version | INDEX.md and ONTOLOGY_MODEL.md document each pair |
| C8 | 8 compatibility wrappers (re-exports) | Code duplication, maintenance burden | Documented in DUPLICATE_POLICY.md; plan to deprecate |
| C9 | wordpipe/ai/ has fragile imports (`from logging_tools import evt`) | Breaks when module structure changes | **Superseded (1404-12-05):** AI scripts quarantined to scripts/ai/; wordpipe/ai/ is now a deprecation stub |
| C10 | wordpipe/orchestrator.py mixes 7+ responsibilities | Hard to test, maintain, or extend | **Resolved (1404-11-25):** Split into wordpipe/steps/ step modules and wordpipe/orchestration/ orchestrator |

---

## 4. Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     REPOSITORY ROOT                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐    ┌──────────────────────────┐   │
│  │     tools/          │    │      wordpipe/            │   │
│  │  (Evidence Pipeline)│    │    (Runtime Library)      │   │
│  │                     │    │                           │   │
│  │  make_manifest.py   │    │  core/        (stdlib)    │   │
│  │  plan_legacy_reorg  │    │  interfaces/  (protocols) │   │
│  │  apply_legacy_reorg │    │  adapters/    (impls)     │   │
│  │  build_legacy_index │    │  orchestration/(runner)   │   │
│  │  verify_integrity   │    │  cli/         (entry)     │   │
│  │  orchestrate.py     │    │  plugins/     (registry)  │   │
│  │  security_scan.py   │    │  ai/          (quarantined to scripts/) │   │
│  │  pipeline_contracts │    │  pipeline/    (wrappers)  │   │
│  │  tool_common.py     │    │  flatteners/  (wrappers)  │   │
│  │  add_standard_hdr   │    │  events.py               │   │
│  │  jalali.py          │    │  orchestrator.py          │   │
│  └─────────────────────┘    └──────────────────────────┘   │
│                                                             │
│  ┌─────────────────────┐    ┌──────────────────────────┐   │
│  │  WordHorrorStories/ │    │      docs/               │   │
│  │  (Content Archive)  │    │   (Documentation)        │   │
│  └─────────────────────┘    └──────────────────────────┘   │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │_ARCHIVE/ │  │ _WORK/   │  │ _META/   │  │_SECURITY/│  │
│  │(evidence)│  │(snapshot)│  │(metadata)│  │(reports) │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Flow (Desired)

```
wordpipe/core/       → stdlib only (ZERO external deps)
wordpipe/interfaces/ → stdlib + core
wordpipe/adapters/   → interfaces + optional deps (docx, openai)
wordpipe/orchestration/ → interfaces + adapters
wordpipe/cli/        → orchestration
wordpipe/plugins/    → interfaces

tools/               → stdlib only (independent of wordpipe/)
                     → operates on _WORK/ and _ARCHIVE/
topic adapters       → stdlib preferred; write staged inputs and metrics
                     → call pipeline through operator commands, not imports
```

### Topic Report Adapter Pattern

Topic adapters are allowed when source Markdown is not already in Chronicle
event format. They should:

- keep raw topic input in the topic folder, usually `WordHorrorStories/<topic>/input/`
- write staged Chronicle files under `WordHorrorStories/<topic>/output/<run_id>/staged_input/`
- keep topic vocabulary in a topic-local theme config
- record `prepare_metrics.json`, `run_metrics.json`, `RUN_SUMMARY.md`, and `run.log`
- use `docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md` to compare repeated runs

Current evidence: the InsuranceChatbot adapter run at
`WordHorrorStories/insurancechatbot/output/20260716_091000/` processed 3 input
files into 200 merged events with 194 tagged events, 0 warnings/errors, and
6.96s wall-clock time.

### Current Violations

| Violation | Location | Impact |
|-----------|----------|--------|
| `from logging_tools import evt` (no package prefix) | wordpipe/ai/ailoader.py, helpers.py, reorganize.py | **Stale:** AI scripts quarantined to scripts/ai/ (1404-12-05); wordpipe/ai/ is now a deprecation stub |
| `from persiantools.jdatetime import JalaliDate` | wordpipe/ai/timefmt.py | **Stale:** AI scripts quarantined; timefmt.py moved to scripts/ai/ |
| wordpipe/orchestrator.py has 7+ responsibilities | wordpipe/orchestrator.py | **Resolved:** Split into wordpipe/steps/ step modules and wordpipe/orchestration/ orchestrator |
| wordpipe/code_style.py has duplicate defs | wordpipe/code_style.py | **Resolved:** one `style_code_blocks` definition remains |
| wordpipe/logging_tools.py has os.makedirs() bug | wordpipe/logging_tools.py | **Superseded:** module is now a thin EventSink compatibility wrapper |
| wordpipe/core/segment.py O(n^2) | wordpipe/core/segment.py | **Superseded:** core path is a deprecation stub; active adapter precomputes heading state in O(n) |
| topic report runner combines multiple ontology responsibilities | tools/run_topic_report.py | **Outstanding:** split internally while preserving CLI/evidence contracts |
| generated report scripts and DOCX files occupied root | `_scripts/`, root `*.docx` | **Resolved:** scripts moved to `scripts/reporting/`, evidence archived, root allowlist enforced |

---

## 5. Integration Points

### 5.1 tools/ ↔ wordpipe/ (Should be ZERO)

Currently: **No Python-level imports** between tools/ and wordpipe/. ✅
The only coupling is through file paths (tools/ references `wordpipe/` as a directory path for legacy operations). This is acceptable.

**Rule:** `tools/` must never `import wordpipe`. `wordpipe/` must never `import tools`.

### 5.2 wordpipe/ ↔ TraceLedger (Future)

The EventSink protocol in `wordpipe/events.py` is the integration point:

```python
class EventSink(Protocol):
    def emit(self, level: str, event: str, fields: dict) -> None: ...
```

TraceLedger provides an adapter. WordPipe never imports TraceLedger.

### 5.3 wordpipe/ ↔ External Dependencies

| Dependency | Where Used | Status |
|-----------|-----------|--------|
| python-docx | wordpipe/adapters/docx/ | Optional (docx extra) |
| openai | wordpipe/adapters/ai/openai_summarizer.py | Optional (openai extra) |
| python-dotenv | wordpipe/cli/main.py | Optional (dotenv extra) |
| persiantools | former wordpipe/ai/timefmt.py | **Superseded** — legacy AI scripts quarantined outside runtime package |
| pywin32 | wordpipe/adapters/flatteners/com_flattener.py | Optional (win32 extra) |

No runtime action remains for `timefmt.py`; new AI integrations use the
interfaces/adapters boundary and lazy optional dependencies.

### 5.4 wordpipe/ Internal Module Boundaries

```
core/       → NO imports from interfaces/, adapters/, orchestration/, ai/, cli/
interfaces/ → MAY import from core/ only
adapters/   → MAY import from interfaces/ and core/
orchestration/ → MAY import from interfaces/, adapters/, core/
cli/        → MAY import from orchestration/
plugins/    → MAY import from interfaces/
ai/         → **Superseded (1404-12-05):** AI scripts quarantined to scripts/ai/; wordpipe/ai/ is a deprecation stub
pipeline/   → LEGACY wrappers (to be deprecated)
flatteners/ → LEGACY wrappers (to be deprecated)
```

---

## 6. Modularization Plan

### Phase 1: Fix Critical Bugs (P0) — Target: 1404/12/05

| Task | File | Issue | Fix |
|------|------|-------|-----|
| 1.1 | wordpipe/code_style.py | Duplicate `style_code_blocks()` | Remove the no-op placeholder; keep the real implementation |
| 1.2 | wordpipe/logging_tools.py | `os.makedirs()` with filename-only path | Guard: only mkdir when dirname is non-empty |
| 1.3 | wordpipe/logging_tools.py | Duplicate imports | Remove duplicates |
| 1.4 | wordpipe/ai/timefmt.py | `persiantools` imported at module level | Lazy import with fallback to Birashk algorithm (from tools/jalali.py) |

**Current status:** 1.1 and 1.3 are fixed; 1.2 is superseded by the EventSink
wrapper; 1.4 is superseded by quarantining legacy AI scripts. These are not
active critical bugs.

### Phase 2: AI Module Refactor (P1) — Target: 1404/12/10

Current state: `wordpipe/ai/` has fragile imports like `from logging_tools import evt` (no package prefix).

**Target structure:**

```
wordpipe/ai/
├── __init__.py          # Public API exports
├── config.py            # Env parsing + validation (no side effects)
├── provider_factory.py  # Constructs OpenAI/Dummy provider
├── logging_setup.py     # Logger/jsonl output configuration
├── runtime.py           # Canary + reorganize orchestration (pure functions)
├── cli.py               # Argparse-only; optional dotenv loading
└── helpers.py           # Kept as compatibility shim
```

**Key changes:**
- All imports become package-safe: `from wordpipe.ai.helpers import ...`
- No `dotenv` auto-load at import time
- Silent `except Exception: pass` blocks replaced with structured warnings via EventSink

**Current status:** **SUPERSEDED.** Runtime AI contracts/adapters live under
`wordpipe/interfaces/ai.py` and `wordpipe/adapters/ai/`; manual legacy scripts
live under `scripts/ai/`.

### Phase 3: Split Orchestrator into Steps (P1) — Target: 1404/12/15

Current: `wordpipe/orchestrator.py` `process_docx_v3()` does flattening, styling, segmentation, save, cleanup, TOC update, and telemetry.

**Target structure:**

```
wordpipe/steps/
├── __init__.py
├── flatten.py     # flatten_step(cfg, sink) -> FlattenResult
├── style.py       # style_step(doc, cfg, sink) -> None
├── segment.py     # segment_step(path, cfg, sink) -> list[Segment]
├── finalize.py    # finalize_step(doc, cfg, sink) -> None
└── toc.py         # toc_step(path, cfg, sink) -> TocResult (capability-driven)
```

**Key changes:**
- Each step is unit-testable in isolation with a fake EventSink
- `process_docx_v3` becomes a thin orchestrator that composes steps
- No broad silent exception swallowing; failures become warnings/errors with context

**Current status:** **VERIFIED COMPLETE.** `wordpipe/orchestrator.py` is a thin
composition root delegating to `wordpipe/orchestration/pipeline.py`; focused
orchestration and step tests cover fail-fast behavior.

### Phase 4: Tool Hardening (P1) — Target: 1404/12/20

| Task | File | Issue | Fix |
|------|------|-------|-----|
| 4.1 | tools/verify_integrity.py | No --portable flag | Add --portable to ignore absolute-path drift |
| 4.2 | tools/apply_legacy_reorg.py | No src_rel/dst_rel fields | Add relative path fields to relocation map |
| 4.3 | tools/verify_integrity.py | Absolute paths in reports | Prefer *_rel resolved against --workspace-root |

**Current status:** **OUTSTANDING / requires a separate evidence-pipeline
audit.** Do not infer these flags or fields from the topic-runner work.

### Phase 5: Optimization (P2) — Target: 1404/12/25

| Task | File | Issue | Fix |
|------|------|-------|-----|
| 5.1 | wordpipe/core/segment.py | O(n^2) heading context | Precompute heading state in one pass; reuse for segments |
| 5.2 | tools/ (new) | No duplicate scanner | Create tools/duplicate_scan.py with tiered classification |

**Current status:** 5.1 is **SUPERSEDED/VERIFIED** in the active DOCX adapter;
5.2 remains **OUTSTANDING**.

### Phase 6: CI & Governance (P2) — Target: 1404/12/30

| Task | Deliverable | Description |
|------|-------------|-------------|
| 6.1 | CI profile: runtime | Compile/lint/test only tools/, wordpipe/, WordHorrorStories/autobiography/ |
| 6.2 | CI profile: evidence | Run tools/verify_integrity.py and check audit artifacts |
| 6.3 | tools/duplicate_scan.py | Classify duplicates into expected_mirror, expected_boilerplate, actionable_duplicate |
| 6.4 | Remote refs audit | Ensure no old branches expose sensitive keys |

**Current status:** minimal CI exists and is verified. Separate runtime/evidence
profiles, the duplicate scanner, and remote-ref audit remain **OUTSTANDING**.

---

## 7. Directory Structure (Historical Target)

This diagram is retained as planning history and contains names later archived
or superseded. Use `ROOT_ORGANIZATION.md`,
`docs/engineering/REPOSITORY_BOUNDARIES.md`, and `INDEX.md` for current layout.

After all phases, the repository should look like:

```
/
├── ARCHITECTURE.md           # Architecture specification
├── WORKSPACE_OVERVIEW.md     # Workspace manual
├── README.md                 # Entry point
├── PROJECT_INDEX.md          # Navigation guide
├── ROADMAP.md                # Goals and phases
├── ROADMAP_1404-11-25.md     # Consolidated roadmap
├── JOURNAL.md                # Activity journal
├── ONTOLOGY_MODEL.md         # Detailed ontology
├── ONTOLOGY.md               # Ontology index
├── ontology.json             # Machine ontology
├── VERIFICATION.md           # Claim verification
├── PLAN.md                   # Task log
├── INDEX.md                  # File map
├── REPO_ORGANIZATION_PLAN.md # This file
├── pyproject.toml            # Package config
│
├── tools/                    # Evidence pipeline (stdlib only)
│   ├── make_manifest.py
│   ├── plan_legacy_reorg.py
│   ├── apply_legacy_reorg.py
│   ├── build_legacy_index.py
│   ├── verify_integrity.py   # + --portable flag
│   ├── orchestrate.py
│   ├── security_scan.py
│   ├── pipeline_contracts.py
│   ├── tool_common.py
│   ├── add_standard_headers.py
│   ├── duplicate_scan.py     # NEW
│   └── jalali.py
│
├── wordpipe/                 # Runtime library
│   ├── __init__.py           # Public API
│   ├── events.py             # EventSink protocol
│   ├── core/                 # stdlib only
│   ├── interfaces/           # Protocols/ABCs
│   ├── adapters/             # Concrete implementations
│   │   ├── ai/
│   │   ├── docx/
│   │   └── flatteners/
│   ├── orchestration/        # Pipeline runner
│   ├── steps/                # NEW - step modules
│   │   ├── flatten.py
│   │   ├── style.py
│   │   ├── segment.py
│   │   ├── finalize.py
│   │   └── toc.py
│   ├── cli/                  # CLI entrypoint
│   ├── plugins/              # Plugin registry
│   ├── ai/                   # Refactored
│   │   ├── config.py         # NEW
│   │   ├── provider_factory.py # NEW
│   │   ├── logging_setup.py  # NEW
│   │   ├── runtime.py        # NEW
│   │   └── cli.py            # NEW
│   ├── pipeline/             # LEGACY (deprecate)
│   └── flatteners/           # LEGACY (deprecate)
│
├── WordHorrorStories/        # Content archive
├── docs/                     # Documentation
├── tests/                    # Unit tests
├── _ARCHIVE/                 # Pipeline evidence (append-only)
├── _WORK/                    # Snapshot input (immutable)
├── _META/                    # Metadata
├── _SECURITY/                # Security reports
└── _INBOX/                   # Incoming files
```

---

## 8. Deprecation Strategy

### Compatibility Wrappers (wordpipe/pipeline/, wordpipe/flatteners/)

These are thin re-exports for backward compatibility. Strategy:

1. **Phase 4 (current):** Documented in DUPLICATE_POLICY.md as Tier 2 (expected boilerplate)
2. **Phase 6 (target):** Add deprecation warning when imported
3. **Future:** Remove after TraceLedger migration is complete

### wordpipe/orchestrator.py (legacy monolithic)

1. **Phase 3:** Split into steps/ modules; keep orchestrator.py as thin wrapper
2. **Phase 6:** Add deprecation notice; recommend using wordpipe.orchestration directly
3. **Future:** Remove after all consumers migrate

### wordpipe/ai/ (old structure)

1. **Phase 2:** Add new modules alongside old ones
2. **Phase 6:** Old modules become wrappers around new ones
3. **Future:** Remove old modules

---

## 9. Verification Gates

| Gate | What It Checks | When |
|------|---------------|------|
| G1 | No absolute paths in docs/ | Every commit |
| G2 | All .md claims match code | Weekly |
| G3 | `import wordpipe` works with stdlib only | Every commit |
| G4 | tools/security_scan.py passes | Every commit |
| G5 | tools/verify_integrity.py passes | Before release |
| G6 | No duplicate headers in Python files | Every commit |
| G7 | All internal markdown links resolve | Weekly |
| G8 | Root contains only allowlisted governance/configuration entrypoints | Every commit |

---

## 10. Quick Reference

### Commands to Run

```powershell
# Verify headers
python tools/add_standard_headers.py --path .

# Security scan
python tools/security_scan.py --root . --fail-on-findings

# Import safety
python -c "import wordpipe"

# Link check
python tools/docs_link_check.py

# Pipeline (full flow)
python tools/orchestrate.py --root _WORK/snapshot

# Tests
pytest -q

# Root organization
python tools/check_root_layout.py --root .
```

### Files to Read First

| Order | File | Why |
|-------|------|-----|
| 1 | README.md | Friendly entry point |
| 2 | INDEX.md | Navigation guide |
| 3 | ROADMAP.md | Consolidated goals and outstanding labels |
| 4 | PLAN.md | What needs doing |
| 5 | VERIFICATION.md | What's been verified |

---

## 11. Change Log

| Date (Gregorian) | Date (Jalali) | Change |
|------------------|---------------|--------|
| 2026-02-14 | 1404-11-25 | Initial organization plan created |
