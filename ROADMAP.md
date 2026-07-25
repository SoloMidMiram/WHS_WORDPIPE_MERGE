# 🗺️ Project Roadmap

> **Date (Gregorian):** 2026-07-09
> **Date (Shamsi/Jalali):** 1405-04-18
> **Last Updated:** 2026-07-25
> **Branch:** `main`

Current stabilization status:
- Chronicle dependency ownership is declared through the `chronicle` extra.
- Chronicle ingest/merge/categorize/verify logic is canonical under `wordpipe/chronicle/`.
- `pipeline/` and `tools/pipeline-chronicle/` are compatibility/operator CLI surfaces, not runtime import surfaces.
- WordPipe orchestration is step-based; read/style failures are fatal.
- `index` remains in `pipeline/` and is deferred from canonical extraction.
- Historical P0–P2 remediation baseline: **105 tests passed** on 2026-07-09;
  see [`docs/engineering/P0_P2_VALIDATION_REPORT.md`](docs/engineering/P0_P2_VALIDATION_REPORT.md).
- Current validation results are recorded by dated activity in `JOURNAL.md` and
  `VERIFICATION.md`; transient test/file counts are not architecture claims.
- Generic topic-runner workflow validated on InsuranceChatbot: 3 Markdown
  inputs, 200 staged/merged events, 194 events with theme tags, 0
  warnings/errors, trend comparison, source attribution, and ontology evidence.
  Evidence: [`WordHorrorStories/insurancechatbot/output/phase13_trend_validation/RUN_SUMMARY.md`](WordHorrorStories/insurancechatbot/output/phase13_trend_validation/RUN_SUMMARY.md).
- Phase 14 genericity remediation is validated on the second topic; root layout
  is enforced by `tools/check_root_layout.py`. See the
  [implementation alignment audit](docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md).
- **2026-07-25: Third-wave P0/P1 remediation complete.** All 5 additional findings
  (ingest rejection manifest with provenance, flatten preflight + abort-on-failure,
  source coverage wildcard parser, dedup defaults aligned end-to-end, sibling
  heading context in both implementations) are fixed. CI includes DOCX extra,
  real DOCX CLI test, and real chain.ps1 execution. 270 tests pass.
- **2026-07-25: Second-wave P0/P1 remediation complete.** All 7 additional findings
  (flattener fallback decoupling, chain.ps1 abort-on-failure, verify_integrity
  fail-closed default, provenance defects, REVIEW verdict enforcement, API doc
  alignment, catalog v2 schema) are fixed. See
  [`docs/engineering/SECOND_WAVE_P0P1_VALIDATION.md`](docs/engineering/SECOND_WAVE_P0P1_VALIDATION.md)
  for results.
- **2026-07-24: P0 reliability remediation complete.** All 6 verified P0 defects
  (verify-integrity strict mode, malformed event heading validation, ComFlattener
  eager fail, TOC adapter explicit failure, CLI error propagation,
  `--in`/`--out` path guard) are fixed. See
  [`VERIFICATION.md`](VERIFICATION.md) for results.

---

## 🔭 Vision

Transform this workspace into a **maintainable, evidence-backed, ontology-grounded project** where:
- **`tools/`** evidence pipeline is reliable, portable, and independently runnable
- **`wordpipe/`** is a clean, import-safe library for TraceLedger integration
- **`pipeline/`** chronicle automation is end-to-end operational (ingest -> merge -> categorize -> index)
- **Documentation** is accurate, verifiable, and cross-referenced (no stale/lost paths)
- **An ontological model** describes the project's structure, phases, claims, and evidence
- **Journal and roadmap** anchor planning against disruption and chaos

---

## 🎯 Core Goals

| # | Goal | Priority | Status |
|---|------|----------|--------|
| G1 | **Path portability**: Operational docs use repo-relative paths or placeholders | P0 | ✅ Verified after 2026-07-16 cleanup |
| G2 | **Doc accuracy verification**: Verify all `.md` descriptions match actual code/modules | P0 | ✅ Done (P0–P2 validation pass, 2026-07-09) |
| G3 | **Ontological model**: Build a structured ontology of project entities, periods, claims, evidence | P1 | 🟡 Partial — model and per-run spine exist; project-level topic-run instances outstanding |
| G4 | **Journal system**: Create dated journal tracking periods of activity with claims/results/verification | P1 | ✅ Done |
| G5 | **Roadmap anchor**: Single source of truth for planned vs completed work | P0 | ✅ Done |
| G6 | **Comprehensive architecture reference**: ARCHITECTURE_AND_MODULES.md covering all 3 subsystems | P0 | ✅ Done |
| G7 | **NLP/ontology grounding**: Evaluate NLP/POS tagging for extracting ontology from project text | P2 | 🔴 OUTSTANDING |
| G8 | **TraceLedger alignment**: WordPipe as a library consumable by TraceLedger | P1 | 🟡 PARTIAL — protocols/library boundary exist; external integration not validated here |
| G9 | **Chronicle automation**: Composable CLI pipeline to ingest, merge, categorize, index deep-search files | P3 | ✅ Done |
| G10 | **P0/P1 stabilization**: Chronicle deps, canonical verify, fail-fast orchestration, step tests, CI | P0/P1 | ✅ Done |
| G11 | **Topic-neutral report performance loop**: Stage non-Chronicle Markdown bundles, measure extraction/tagging/runtime, and iterate from evidence | P1 | ✅ Done (template + InsuranceChatbot run) |
| G12 | **Generic topic runner and ontology spine**: Run any configured topic with one audited command, trend metrics, and minimal ontology outputs | P1 | ✅ Done (Phase 13) |

---

## 🚧 Constraints

| # | Constraint | Impact |
|---|------------|--------|
| C1 | Limited/unstable internet access | Cannot rely on `pip install`, GitHub API, or external NLP services |
| C2 | Windows environment with PowerShell | Tooling must be Win32-compatible; paths use backslash in shell, forward in code |
| C3 | Existing massive doc set (many `.md` files) | Risk of redundancy, contradiction, and path rot |
| C4 | Absolute paths (`F:\Git\...`) embedded in docs | Breaks for any other clone location or user |
| C5 | Evidence files in `_ARCHIVE/` are append-only or replace-on-run | Must preserve historical evidence |
| C6 | `_WORK/snapshot` is immutable input | Must not modify source snapshot |

---

## 📋 Phases (Newest First)

Status labels: **VERIFIED** means implementation plus proportionate evidence;
**PARTIAL** means meaningful work exists but the stated outcome is incomplete;
**OUTSTANDING** means planned behavior/evidence is absent; **SUPERSEDED** means a
later implementation satisfies the intent differently. Detailed crosswalk:
[`docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md`](docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md).

### Phase 14 — Second Topic Adapter & Multi-Topic Ontology Readiness (P1)
> Goal: Add a second topic through the Phase 13 generic runner, proving reusability and providing multi-topic evidence before any strategic ontology expansion.
> **Date:** 2026-07-16 | **Status:** ✅ Completed

| Slice | Task | Status |
|-------|------|--------|
| 14.1 | Identify and validate a second Markdown topic | ✅ Done (pipelinechronicle: `_ARCHIVE/pipeline-chronicle/`, 5 files) |
| 14.2 | Create generic Markdown-section adapter (`tools/prepare_generic_markdown_chronicle.py`) | ✅ Done |
| 14.3 | Register adapter in `ADAPTER_REGISTRY` and add topic folder (manifest, themes, README) | ✅ Done |
| 14.4 | Baseline + trend runs through the generic runner | ✅ Done |
| 14.5 | Validate ontology spine with multi-topic evidence | ✅ Done |
| 14.6 | Add adapter tests and runner registry tests | ✅ Done |
| 14.7 | Update docs and assess Phase 15 readiness | ✅ Done |
| 14.8 | Remediate genericity review findings and map Phase 14 context | ✅ Done (dynamic month headings, manifest topic summaries, `##` boundary documented) |
| 14.9 | Audit roadmap claims, label outstanding work, and enforce root organization | ✅ VERIFIED (alignment audit + root checker) |

Phase 14 output: `WordHorrorStories/pipelinechronicle/output/phase14_baseline_validation/`
and `phase14_trend_validation/` — 50 staged/merged/tagged events, 0 errors, PASS verdict.
Trend COMPARED against baseline. Both topics (insurancechatbot + pipelinechronicle)
have identical ontology spine coverage.

Genericity remediation evidence: `phase14_genericity_fix_baseline/` and
`phase14_genericity_fix_trend/` preserve the 50/50/50 PASS baseline while
proving date-derived month headings and manifest-derived summary titles.

Phase 15 (semantic ontology expansion) is now justified — see
[Phase 14 doc](docs/PHASE14_SECOND_TOPIC_ONTOLOGY_READINESS.md) for the readiness assessment.

### Phase 15 — Provenance Foundation & Semantic Ontology Design (P1)
> Goal: Strengthen adapter preparation contracts and file-level source lineage before event-level semantic ontology expansion.
> **Date:** 2026-07-17 | **Status:** ✅ Provenance foundation complete; semantic extraction outstanding

Design doc: [`docs/PHASE15_PROJECT_SEMANTIC_ONTOLOGY_DESIGN.md`](docs/PHASE15_PROJECT_SEMANTIC_ONTOLOGY_DESIGN.md)

| Slice | Task | Status |
|-------|------|--------|
| 15.1 | Common preparation-metrics validation in the topic runner | ✅ Done |
| 15.2 | Consumed-source metrics semantics (`input_file_count` / bytes / lines) | ✅ Done |
| 15.3 | Built-in adapter file-level `source_lineage` | ✅ Done |
| 15.4 | Fail-closed prepare-contract handling before pipeline | ✅ Done |
| 15.5 | Lineage-aware aggregate `source_attribution.json` | ✅ Done |
| 15.6 | Project Phase 15 semantic design + decision gate | ✅ Done |
| 15.7 | Append-only run-directory reservation and portable run-ID validation | ✅ Done |
| 15.8 | Top-level staged-path and finite coverage validation | ✅ Done |
| 15.9 | Canonical hash-catalogued input corpus migration and CI guard | ✅ Done |
| 15.10 | Fresh paired Phase 15 closeout evidence under v2 run IDs | ✅ Done |
| 15.11 | Whole-project domain crosswalk, architecture stability gate, and static import-boundary check | ✅ Done |

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

The third-adapter and unsafe-serializer conditions are the primary triggers. Secondary signals—a defect requiring synchronized production edits on two separately audited occasions, an import-boundary violation that cannot be repaired locally, or a public contract that cannot evolve safely despite characterization tests—support but do not independently mandate broad decomposition. Repeated-defect evidence must be dated and path/test-backed in `JOURNAL.md` or the implementation-alignment audit.

This slice implements file-level provenance only (`SourceBundle → raw source → StagedSource`). Source-section locators and stable individual ReportEvent IDs are delivered in Project Phase 16 as evidence sidecars; semantic concept extraction remains outstanding.

### Phase 17 — Event-Provenance Survivor Integrity & Repeatability (P1)
> Goal: Independently verify actual merged survivor keys and prove stable SourceEvent/ReportEvent mappings across a second fresh paired run before ontology v2 design.
> **Date:** 2026-07-17 | **Status:** ✅ Done — survivor verification + paired stability; ontology emission excluded

Design doc: [`docs/PHASE17_EVENT_PROVENANCE_SURVIVOR_AND_REPEATABILITY.md`](docs/PHASE17_EVENT_PROVENANCE_SURVIVOR_AND_REPEATABILITY.md)

| Slice | Task | Status |
|-------|------|--------|
| 17.1 | Merge-note-aware actual survivor-key verification without changing merge behavior | ✅ Done |
| 17.2 | Auditable Phase 16 baseline → Phase 17 stable-id comparison | ✅ Done |
| 17.3 | Fresh paired `phase17_event_provenance_repeatability` runs after collision and preservation preflight | ✅ Done |
| 17.4 | Repeatability gate assessment; ontology emission remains excluded | ✅ Done |

Controlled evidence: `phase17_event_provenance_repeatability` and reserved `phase17_provenance_stability` under both topic output bases. Phase 16 `unmerged_source_event_count` remains keep-both count-parity history; Phase 17 uses actual survivor membership (`merged-note-aware-v1`).

The committed Git scope and boundaries are recorded in [`docs/engineering/PHASE13_17_COMMIT_DRAFT.md`](docs/engineering/PHASE13_17_COMMIT_DRAFT.md). Commit `a635ea2` closes the implementation/evidence stack that began after a Git baseline predating Phase 13; it is not a Phase 15-only change.

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

### Phase 16 — Stable Event Identity & Section-Level Provenance (P1)
> Goal: Transport section/commit locators through prepare → normalised fingerprints → merge survivors without changing Chronicle dedup or aggregate ontology emission.
> **Date:** 2026-07-17 | **Status:** ✅ Evidence sidecars implemented and closeout-tested; Phase 17 repeatability and individual ontology emission deferred

Design doc: [`docs/PHASE16_EVENT_IDENTITY_AND_SECTION_PROVENANCE.md`](docs/PHASE16_EVENT_IDENTITY_AND_SECTION_PROVENANCE.md)

| Slice | Task | Status |
|-------|------|--------|
| 16.0 | Permanent characterization tests (ingest comment→body, hashes, empties) | ✅ Done |
| 16.1 | Adapter raw `event_lineage` emit + pointer + pre-pipeline envelope | ✅ Done |
| 16.2 | Post-pipeline correlation before summarize + provenance exit + summary section | ✅ Done |
| 16.3 | Design doc, roadmap sync, controlled runs (`phase16_event_lineage_validation`) | ✅ Done |
| 16.4 | Aggregate→individual ontology migration gate (design only; no emission) | ✅ Done |

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

Controlled evidence: `WordHorrorStories/insurancechatbot/output/phase16_event_lineage_validation/` and
`WordHorrorStories/pipelinechronicle/output/phase16_event_lineage_validation/`.

### Phase 13 — Generic Topic Report Runner & Performance Trends (P1)
> Goal: Convert the InsuranceChatbot-specific report workflow into a reusable topic-runner with manifests, one-command execution, trend comparison, source attribution, and a minimal ontology spine.
> **Date:** 2026-07-16 | **Status:** ✅ Completed

Roadmap doc: [`docs/PHASE13_GENERIC_TOPIC_REPORT_RUNNER_ROADMAP.md`](docs/PHASE13_GENERIC_TOPIC_REPORT_RUNNER_ROADMAP.md)

| Slice | Task | Status |
|-------|------|--------|
| 13.1 | Define topic-run manifest schema: topic name, input directory, adapter, theme config, output policy, and quality gates | ✅ Done |
| 13.2 | Add one-command runner for prepare -> pipeline -> summarize -> trend update | ✅ Done |
| 13.3 | Refactor InsuranceChatbot preparation into the first registry-backed adapter | ✅ Done |
| 13.4 | Add trend comparison across repeated runs for the same topic | ✅ Done |
| 13.5 | Emit `topic_run_manifest.json` and `topic_run_ontology.json` for each run | ✅ Done |
| 13.6 | Improve source attribution in appendix output and/or a source sidecar JSON | ✅ Done (`source_attribution.json`) |
| 13.7 | Add tests for manifest parsing, dry-run execution, trend comparison, and ontology-spine output | ✅ Done |
| 13.8 | Update docs with the generic runner command and migration path from bespoke adapters | ✅ Done |

Historical Phase 13 validation: `pytest -q` reported 124 passed. Controlled runs
`phase13_baseline_validation` and `phase13_trend_validation` prove repeated-run
trend comparison. The trend run emits `RUN_SUMMARY.md`, `run_metrics.json`,
`topic_run_manifest.json`, `topic_run_ontology.json`, `trend_report.json`,
`trend_report.md`, and `source_attribution.json`.

Ontology stance: Phase 13 is the right time to define the strategic ontology
spine, but not the right time for full ontology population. The minimum model
should cover `Topic`, `SourceBundle`, `TopicAdapter`, `TopicRun`,
`StagedSource`, `ReportEvent`, `Theme`, `Metric`, `EvidenceArtifact`, and
`Verdict`. Larger semantic ontology work should wait until multiple different
topics have passed through the generic runner.

### Phase 12 — Topic Adapter Performance Loop (P1)
> Goal: Make the Chronicle pipeline usable for arbitrary long Markdown topics through staging adapters, topic-specific themes, and repeatable performance checks.
> **Date:** 2026-07-16 | **Status:** ✅ Completed

| Slice | Task | Status |
|-------|------|--------|
| 12.1 | Add InsuranceChatbot preparation tool for commit history, project digest, and roadmap Markdown | ✅ Done |
| 12.2 | Add InsuranceChatbot theme config for knowledge base, retrieval, runtime, ontology, scraper/release, CI, docs, data quality, and operations tags | ✅ Done |
| 12.3 | Fix Chronicle ingest ISO-date heading extraction for staged topic events | ✅ Done |
| 12.4 | Add focused topic-adapter tests; suite now passes with 105 tests | ✅ Done |
| 12.5 | Run measured InsuranceChatbot report and publish `RUN_SUMMARY.md`, `run_metrics.json`, logs, and appendices | ✅ Done |
| 12.6 | Add topic-neutral iterative performance check template for future subjects | ✅ Done |

Observed performance: 195,293 input bytes across 3 files; 169 commit headings and
31 section candidates; 200 staged events; 200 merged events; 194 tagged events;
0 duplicate/conflict entries; 0 warnings/errors; 6.96s wall time.

Template: [`docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md`](docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md)

### Phase 11 — P0–P2 Repository Review Remediation (P0/P1/P2)
> Goal: Stabilize packaging contract, doc trust, canonical verify, orchestration fail-fast, step tests, segmenter perf, CI
> **Date:** 2026-07-09 | **Status:** ✅ Completed

| Slice | Task | Status |
|-------|------|--------|
| P0-1 | Declare `chronicle` optional extra (`pyyaml`, `python-dateutil`) | ✅ Done |
| P0-2 | Fix README/ROADMAP stale metadata; fix docs link checker false positives | ✅ Done |
| P1-1 | Extract `verify_ingest` to `wordpipe.chronicle` + CLI wrappers | ✅ Done |
| P1-2 | Orchestrator fail-fast on style/finalize errors | ✅ Done |
| P1-3 | Step module unit tests | ✅ Done |
| P2-1 | Segmenter heading-path O(n) precompute | ✅ Done |
| P2-2 | Add `.github/workflows/ci.yml` health gate | ✅ Done |
| P2-3 | Authoritative doc crosswalk + validation report | ✅ Done |

Validation: [`docs/engineering/P0_P2_VALIDATION_REPORT.md`](docs/engineering/P0_P2_VALIDATION_REPORT.md)

### Phase 10 — Documentation Architecture & Module Reference (P0)
> Goal: Single source of truth for architecture, modules, integration, flow, logic, goals, and constraints  
> **Date:** 1404/11/25 | **Status:** ✅ Completed
> **Sub-phase 10b (1404/11/25):** Archived 6 stale root docs to `_ARCHIVE/root-docs/`; moved `output/` to `_ARCHIVE/evidence/`; fixed 3 missing pipeline files; updated INDEX.md with pipeline/ section; updated OBSOLETE_DOCS.md with archived root docs

| Task | Description | Status |
|------|-------------|--------|
| 10.1 | Create `ARCHITECTURE_AND_MODULES.md` — comprehensive 3-subsystem reference | ✅ Done |
| 10.2 | Create `docs/OBSOLETE_DOCS.md` — index of superseded vs preserved docs | ✅ Done |
| 10.3 | Update `docs/README.md` — redirect to current source of truth | ✅ Done |
| 10.4 | Update `ROADMAP.md`, `JOURNAL.md`, `ONTOLOGY_MODEL.md`, `PLAN.md` for new phase | ✅ Done |

### Phase 9 — Chronicle Automation Pipeline (P3)
> Goal: Automate deep-search → normalised → merged → categorised → indexed → referenced workflow  
> **Date:** 1404/11/25 | **Status:** ✅ Sub-phase 9a/b completed, 9c pending

**Sub-phase 9a: Tool Completion & Archival (✅ Completed)**
| Task | Description | Status |
|------|-------------|--------|
| 9a.1 | Build `tools/pipeline-chronicle/ingest.py` — deep-search → normalised MD | ✅ Done |
| 9a.2 | Build `tools/pipeline-chronicle/merge.py` — merge N MDs, dedup by hash+date | ✅ Done |
| 9a.3 | Build `tools/pipeline-chronicle/categorize.py` v1 — tag with ontology + themes | ✅ Done |
| 9a.4 | Build `tools/pipeline-chronicle/chain.ps1` v1 — 4-stage orchestrator | ✅ Done |
| 9a.5 | Build `tools/pipeline-chronicle/verify_ingest.py` — batch verification | ✅ Done |
| 9a.6 | Create `tests/test_pipeline_chronicle.py` — 59 tests | ✅ Done |
| 9a.7 | Archive all 5 tools to `_ARCHIVE/pipeline-chronicle/` with ARCHIVE_REPORT.md | ✅ Done |
| 9a.8 | Tag quality review: 61 events, 96.7% coverage, 29.5% over-tagging, 2 false negatives | ✅ Done |

**Sub-phase 9b: Keyword Tuning & Index Builder (✅ Completed)**
| Task | Description | Status |
|------|-------------|--------|
| 9b.1 | Tighten keywords: "exploit"→"prompt exploit", "crash"→"server crash", "error"→"server error"; add "Linux terminal", "simulating", "mega-viral", "interface"; add negative_keywords per theme | ✅ Done |
| 9b.2 | Create `pipeline/categorize.py` v2 — negative keyword support, `--dry-run`, backward-compatible config loading | ✅ Done |
| 9b.3 | Create `pipeline/themes.json` — external theme config (6 themes, 62 positive + 16 negative keywords) | ✅ Done |
| 9b.4 | Build `pipeline/index.py` — generate 4 appendix files with Jinja2 templates + fallback formatting | ✅ Done |
| 9b.5 | Create `pipeline/index_config.json` — configurable output dir, templates dir, dedup method, theme sort | ✅ Done |
| 9b.6 | Create `pipeline/templates/` — 4 Jinja2 templates (event_index, theme_index, source_manifest, link_registry) with fallback string formatting | ✅ Done |
| 9b.7 | Update `pipeline/chain.ps1` v2 — 5 stages with `-SkipIndex`, `-NoLinkRegistry`, `-SourceCoverage`, `-IndexConfig` switches | ✅ Done |
| 9b.8 | Re-run pipeline: 100% coverage (was 96.7%), over-tagging 18.0% (was 29.5%), false negatives eliminated | ✅ Done |

**Sub-phase 9c: Reference Builder & Ontology Wiring (🟡 PARTIAL / OUTSTANDING)**
| Task | Description | Status |
|------|-------------|--------|
| 9c.1 | Build `pipeline/reference.py` — secondary TOC, topic model, stable anchor IDs | 🔴 OUTSTANDING |
| 9c.2 | Wire chronicle pipeline into ontology | 🟡 PARTIAL — P9 ActivityPeriod exists; topic-run instances remain outstanding |
| 9c.3 | Validate against existing manual merge (`ChatGPT_Incidents_Merged.md`) | 🔴 OUTSTANDING |
| 9c.4 | Generalize topic adapter pattern beyond InsuranceChatbot with a config-driven adapter registry | ✅ Superseded by Phase 13 |
| 9c.5 | Add a command wrapper that runs prep, pipeline, summary, and metrics in one audited invocation | ✅ Superseded by Phase 13 |

### Phase 7 — WordPipe Modular Refactor (P1)
> Goal: Refactor wordpipe into clean, import-safe layered architecture  
> **Date:** 1404/11/25 | **Status:** ✅ Completed

| Task | Description | Status |
|------|-------------|--------|
| 7.1 | Create layered architecture (core → interfaces → adapters → orchestration → CLI/plugins) | ✅ Done |
| 7.2 | Create `pyproject.toml` with extras (openai, dotenv, cli, docx) | ✅ Done |
| 7.3 | Create `tests/test_import_safety.py` | ✅ Done |
| 7.4 | Add backward-compatible wrappers in `wordpipe/pipeline/` and `wordpipe/flatteners/` | ✅ Done |
| 7.5 | Pipeline step module refactor: flatten, style, segment, finalize, toc | ✅ Done |
| 7.6 | Add fail-fast read/style behavior and focused step/orchestration tests | ✅ Done |

### Phase 6 — Foundation Fixes & Ontology Building (P0)
> Goal: Make the project portable, navigable, and self-consistent  
> **Date:** 1404/11/25 | **Status:** ✅ Completed

| Task | Description | Status |
|------|-------------|--------|
| 6.1 | Replace absolute Windows paths in docs with relative paths | ✅ Done |
| 6.2 | Create `ROADMAP.md`, `JOURNAL.md`, `ONTOLOGY_MODEL.md`, `INDEX.md`, `README.md` | ✅ Done |
| 6.3 | Create `tools/add_standard_headers.py` — apply standard Jalali-date headers | ✅ Done |
| 6.4 | Apply standard headers to all 82 active Python files | ✅ Done |
| 6.5 | Clean 45 files with duplicate headers | ✅ Done |
| 6.6 | Analyze duplicates (60+ mirror pairs, 8 compatibility wrappers, 18 legacy versions) | ✅ Done |
| 6.7 | Remove BOM from `tools/jalali.py` | ✅ Done |

### Phase 5 — Documentation Pack (P2)
> Goal: Comprehensive documentation with role-based entrypoints  
> **Date:** 1404/11/24 | **Status:** ✅ Completed

| Task | Description | Status |
|------|-------------|--------|
| 5.1 | Create `docs/` directory hierarchy (architecture/, engineering/, operations/, PlansArchive/) | ✅ Done |
| 5.2 | Create `docs/README.md`, `DOC_STYLE_GUIDE.md`, `DUPLICATE_POLICY.md` | ✅ Done |
| 5.3 | Create TraceLedger docs (LOGIC_FLOW, DEBUG_ENHANCEMENT_PLAN, INTEGRATION_CONTRACT, REPOSITORY_REVIEW) | ✅ Done |
| 5.4 | Create `tools/docs_link_check.py` | ✅ Done |
| 5.5 | Add EventSink protocol (`wordpipe/events.py`) | ✅ Done |

### Phase 4 — Security Hardening & Pipeline Contracts (P1)
> Goal: Redact leaked keys, add secrets scanner, standardize stage interfaces  
> **Date:** 1404/11/22 | **Status:** 🟡 PARTIAL — local hardening/contracts verified; remote-history audit outstanding

| Task | Description | Status |
|------|-------------|--------|
| 4.1 | Redact leaked API keys from workspace and .gitignore | ✅ Done |
| 4.2 | Create `.env.example` | ✅ Done |
| 4.3 | Create `tools/security_scan.py` | ✅ Done |
| 4.4 | Create `tools/pipeline_contracts.py` with StagePaths/StageResult/StageError | ✅ Done |
| 4.5 | Create `tools/orchestrate.py` for one-command pipeline | ✅ Done |
| 4.6 | Create pipeline docs (RUNBOOK, CONTRACTS, SECURITY, TOOLS_MODULES, INTEGRATION_MAP, LABOR_REPORT) | ✅ Done |
| 4.7 | Audit remote refs/history for previously leaked keys | 🔴 OUTSTANDING — local scanner does not prove remote-history cleanup |

### Phase 3 — Initial Snapshot & Evidence Pipeline (P0)
> Goal: Extract snapshot, create initial workspace, establish evidence pipeline  
> **Date:** 1404/11/21 | **Status:** ✅ Completed

| Task | Description | Status |
|------|-------------|--------|
| 3.1 | Extract `snapshot_20260211_205716.zip` | ✅ Done |
| 3.2 | Create manifest.jsonl/csv | ✅ Done |
| 3.3 | Generate relocation plan and map | ✅ Done |
| 3.4 | Apply legacy reorganization | ✅ Done |
| 3.5 | Build legacy index | ✅ Done |
| 3.6 | Verify integrity | ✅ Done |

---

## 🧭 Outstanding Works

These are the active items after the Project Phase 17 survivor-integrity gate.
Completed Phase 13–17 foundation work is intentionally excluded.

| Priority | Work | Why It Matters | Current Evidence |
|----------|------|----------------|------------------|
| P1 | Map Phase 13/14/15/16/17 topic runs into the project-level ontology/activity model | Per-run ontologies exist, but `ontology.json` lacks TopicRun instances | Phase 14–17 prove stable 10-entity/7-relation coverage |
| P1 | Complete evidence-pipeline portability (`--portable`, `src_rel`/`dst_rel` relocation output, relative report fields) | Older organization phases planned these contracts but current relocation evidence remains absolute-only | `verify_integrity.py` has no `--portable`; relocation output omits relative fields |
| P1 | Validate the documented TraceLedger consumer integration | Protocol and import boundary exist, but this repository does not prove an external consumer run | EventSink and public library APIs are implemented |
| P2 | Canonicalize `pipeline/index.py` under `wordpipe.chronicle` | `index` is still the deferred Chronicle stage | Existing Phase 9c deferral |
| P2 | Build `pipeline/reference.py` / stable secondary TOC | Long reports need stronger navigational references | Existing Phase 9c item |
| P2 | Validate reference output against the existing manual merge | Phase 9c acceptance evidence is missing | `ChatGPT_Incidents_Merged.md` comparison remains unperformed |
| P2 | Audit remote refs/history for leaked credentials | Local scanning cannot validate remote history | Local security scan is green |
| P2 | Add governed duplicate scanning and separate runtime/evidence CI profiles | Original organization Phase 6 deliverables remain incomplete | Minimal combined CI exists; `tools/duplicate_scan.py` does not |
| P2 | Emit individual ReportEvent entities after Phase 16.4 / Phase 17 gate | Section→event evidence + two-run stability exist; ontology individuals deferred | Phase 16/17 design docs |
| P3 | Emit SemanticConcept / derived_from / mentions after schema decision | Candidate future additions only; not approved schema yet | Project Phase 15/16 design docs |
| P3 | Evaluate offline NLP/POS ontology population | Must not hardcode one topic | Two-topic evidence + section lineage now exist |
| Conditional | Broad topic-runner decomposition | Reconsider only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe | Not an active Project Phase 15 deliverable |

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

---

## 🏁 Milestones (Newest First)

| MS# | Milestone | Phase | Target Date | Status |
|-----|-----------|-------|-------------|--------|
| M19 | Third-wave P0/P1 remediation (5 findings + CI gap) | — | 1405-05-03 | ✅ |
| M18 | Second-wave P0/P1 remediation (7 additional findings) | — | 1405-05-03 | ✅ |
| M16 | Project Phase 17 survivor integrity and stable-id repeatability | Ph17 | 1405-04-26 | ✅ |
| M17 | P0 reliability remediation (6 verified defects fixed) | — | 1405-05-02 | ✅ |
| M15 | Project Phase 16 section provenance sidecars and correlation | Ph16 | 1405-04-26 | ✅ |
| M14 | Project Phase 15 provenance foundation and semantic design gate | Ph15 | 1405-04-26 | ✅ |
| M13 | Second-topic genericity remediation and root organization enforcement | Ph14 | 1405-04-25 | ✅ |
| M12 | Generic topic runner supports manifest-driven one-command runs and trend comparison | Ph13 | 1405-04-25 | ✅ |
| M11 | Topic-adapter performance loop validated on InsuranceChatbot and template published | Ph12 | 1405-04-25 | ✅ |
| M10 | Comprehensive architecture reference published, old docs indexed as obsolete | Ph10 | 1404-11-25 | ✅ |
| M9 | Tag quality: 100% coverage, <=20% over-tagging | Ph9 | 1404-12-20 | ✅ |
| M8 | Chronicle pipeline operational — ingest→merge→categorize→index works end-to-end | Ph9 | 1404-12-20 | ✅ |
| M7 | WordPipe passes import-safety + unit tests | Ph7 | 1404-12-20 | ✅ |
| M6 | Foundation files (ROADMAP, JOURNAL, ONTOLOGY, INDEX, README) published | Ph6 | 1404-11-25 | ✅ |
| M5 | Documentation pack with role-based entrypoints | Ph5 | 1404-11-24 | ✅ |
| M4 | Security posture improved, pipeline contracts operational | Ph4 | 1404-11-22 | ✅ |
| M3 | Evidence pipeline established with 98 files inventoried | Ph3 | 1404-11-21 | ✅ |
| M2 | Dated doc-accuracy pass completed; later drift reconciled by current alignment audit | Ph10/14 | 1405-04-25 | ✅ |
| M1 | Operational documentation uses relative paths/placeholders | Ph6/14 | 1405-04-25 | ✅ |

---

## 📊 Values & Principles

1. **Evidence over opinion** — every claim should point to a file, a log, or a run
2. **Portability** — no absolute paths, no environment-dependent behavior
3. **Idempotency** — re-running the same pipeline produces the same result
4. **Non-destructive** — copy-only, conflict-safe, append-only where historical
5. **Backward compatibility** — changes must not break existing stage contracts
6. **Traceability** — every phase, task, and decision links to a journal entry

---

## 🔗 See Also

- [`ARCHITECTURE_AND_MODULES.md`](ARCHITECTURE_AND_MODULES.md) — Comprehensive reference: architecture, modules, data flow, logic flow, goals, constraints for all 3 subsystems
- [`PLAN.md`](PLAN.md) — Immutable log of intentions and completions
- [`INDEX.md`](INDEX.md) — Full project file index
- [`JOURNAL.md`](JOURNAL.md) — Dated period journal with claims and verification
- [`ONTOLOGY_MODEL.md`](ONTOLOGY_MODEL.md) — Formal entity/relation model
- [`pipeline/CODEX_WORKING.md`](pipeline/CODEX_WORKING.md) — Working code reference with evolution timeline and known issues
- [`docs/PHASE13_GENERIC_TOPIC_REPORT_RUNNER_ROADMAP.md`](docs/PHASE13_GENERIC_TOPIC_REPORT_RUNNER_ROADMAP.md) — Completed generic runner, trend, and ontology-spine roadmap
- [`docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md`](docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md) — Topic-neutral report run performance checklist
- [`WordHorrorStories/insurancechatbot/output/phase13_trend_validation/RUN_SUMMARY.md`](WordHorrorStories/insurancechatbot/output/phase13_trend_validation/RUN_SUMMARY.md) — Latest measured generic topic-runner run
- [`docs/OBSOLETE_DOCS.md`](docs/OBSOLETE_DOCS.md) — Index of superseded vs preserved documentation
- [`docs/README.md`](docs/README.md) — Documentation entrypoint (redirects to current source of truth)
