# 📋 Project Plan

> **Purpose:** Immutable log of intentions and completions. This is NOT analysis or description.
> **Date System:** Jalali (Shamsi) only
> **Created:** 1404-11-25
> **Ontology Ref:** See `ONTOLOGY.md` for concept definitions

---

## Rules

1. All dates are Jalali (Shamsi): `YYYY/MM/DD`
2. Tasks move from phase sections to "Completed" when done
3. Completed tasks replace `- [ ]` with `- [x]` and append `(completed: YYYY/MM/DD)`
4. Each task may link to ontology concepts in parentheses: `(concept: Artifact, Claim)`
5. This file is strictly a log of intentions and completions

---

## Backlog

- [x] Create topic-neutral iterative performance check template for arbitrary Markdown report subjects (concept: Verification, Doc) (completed: 1405/04/25 — docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md)
- [x] Add InsuranceChatbot topic adapter and measured report run summary (concept: Command, Evidence) (completed: 1405/04/25 — WordHorrorStories/insurancechatbot/output/20260716_091000/RUN_SUMMARY.md)
- [x] Generalize topic adapter execution into a single audited command wrapper (concept: Command, Verification) (completed: 1405/04/25 — tools/run_topic_report.py)
- [x] Add config-driven adapter registry for future non-Chronicle Markdown topics (concept: ConfigFile, Command) (completed: 1405/04/25 — prepare_insurancechatbot_chronicle registered)
- [x] Add trend comparison across repeated topic runs (concept: Evidence, Verification) (completed: 1405/04/25 — trend_report.json/md)
- [x] Define minimal ontology spine for generic topic runs before full ontology population (concept: Entity, Evidence) (completed: 1405/04/25 — topic_run_ontology.json)
- [x] Verify all doc descriptions match actual source files (concept: Claim, Verification) (completed: 1404/12/05 — P0-P2 validation pass)
- [ ] Map existing labor notes, reports, and plans into ontology (concept: ActivityPeriod, Artifact)
- [ ] Evaluate NLP/POS tagging approach for ontology population (concept: Entity)
- [ ] Add `--portable` flag to `verify_integrity.py` (concept: Verification, Command)
- [ ] Add `src_rel`/`dst_rel` fields to relocation map (concept: Artifact, Evidence)
- [ ] Fix absolute-path drift in verification reports (concept: Artifact, Evidence)
- [x] Remove duplicate `style_code_blocks()` in `wordpipe/code_style.py` (concept: SourceFile) (completed: 1404/12/05 — one active definition remains)
- [x] Fix `os.makedirs()` bug in `wordpipe/logging_tools.py` (concept: SourceFile) (superseded: 1404/12/05 — module is now an EventSink compatibility wrapper with no directory creation)
- [x] Fix duplicate imports in `wordpipe/logging_tools.py` (concept: SourceFile) (completed: 1404/12/05)
- [x] Split `process_docx_v3` into step modules (concept: SourceFile, ActivityPeriod) (completed: 1404/11/25 — phase 5/PLAN.md, wordpipe/steps/)
- [x] Refactor `wordpipe/ai/ailoader.py` into reusable modules (concept: SourceFile) (superseded: 1404/12/05 — AI scripts quarantined to scripts/ai/, wordpipe/ai/ is a deprecation stub)
- [x] Optimize `wordpipe/core/segment.py` to O(n) heading context (concept: SourceFile) (superseded: 1404/12/05 — O(n) optimization landed in adapters/docx/segmenter.py; core/segment.py is a different path)
- [ ] Create `tools/duplicate_scan.py` (concept: DuplicateSet, Command)
- [ ] Add CI profiles (`runtime`, `evidence`) (concept: Verification)
- [ ] Remote refs audit for leaked keys in old branches (concept: Verification)
- [x] Decide stable individual ReportEvent IDs and source-section locators before semantic emission (concept: Entity, Evidence) (completed: 1405/04/26 — event-lineage-v1 / event-correlation-v1 sidecars; ontology individuals deferred per Phase 16.4 gate)
- [ ] Canonicalize `pipeline/index.py` under `wordpipe.chronicle` with a thin operator wrapper (concept: SourceFile, Command)
- [ ] Map Phase 13/14/15/16 TopicRun evidence into project-level `ontology.json` activity instances (concept: ActivityPeriod, Evidence)

## P0/P1 Third-Wave Remediation — Completed: 1405/05/03

- [x] F1 (P0): Structured rejection manifest from `split_into_events()`; `--allow-undated` flag in CLI; three-mode ingest (fail-no-output, partial-with-manifest, complete-manifest) (completed: 1405/05/03)
- [x] F2 (P1): Preflight check for `_UnavailableFlattener` in `build_default_deps()`; abort pipeline on runtime flatten failure — no output created or overwritten (completed: 1405/05/03)
- [x] F3 (P1): Broadened `build_source_manifest()` index parser to accept both numbered and un-numbered coverage formats; reject zero-valid-row coverage; preserve zero-event sources (completed: 1405/05/03)
- [x] F4 (P1): Changed dedup default to `date_title` in `DEFAULT_CONFIG`, `deduplicate_events()` parameter, unknown-method fallback, CLI help text, and `pipeline/index_config.json` (completed: 1405/05/03)
- [x] F5 (P1): Removed `is None` guards in both `_precompute_heading_states()` and `_build_hpath()`; sibling H2/H3 transitions now update context unconditionally (completed: 1405/05/03)
- [x] CI: Added DOCX extra to matrix; added real DOCX CLI test; added real chain.ps1 execution test (completed: 1405/05/03)
- [x] Acceptance tests: 12 new tests covering all decisive gates (ingest rejection, flatten preflight, coverage parse, dedup, heading sibling, DOCX CLI) (completed: 1405/05/03)
- [x] Removed tracked `tools/__pycache__/jalali.cpython-311.pyc` (already cleaned); `__pycache__/` gitignored (completed: 1405/05/03)
- [x] Updates: ROADMAP, PLAN, JOURNAL, VERIFICATION, IMPLEMENTATION_ALIGNMENT_AUDIT (completed: 1405/05/03)

## P0/P1 Second-Wave Remediation — Completed: 1405/05/03

- [x] Add `_can_import_mergedpipeline()` probe and `_UnavailableFlattener` stub so `make_flattener()` fails clearly before processing when `MergedpipelineV3` is absent (concept: SourceFile, Verification) (completed: 1405/05/03)
- [x] Change `chain.ps1` abort condition from `$IngestCount -eq 0` to `$IngestFailures -gt 0`; add `-AllowPartialIngest` switch (concept: Command, Verification) (completed: 1405/05/03)
- [x] Flip `verify_integrity.py` warnings to fatal by default; replace `--strict` with `--diagnostic-only`; update orchestration and docs (concept: Verification, Command) (completed: 1405/05/03)
- [x] Fix ingest provenance: skip undated events instead of emitting `## Event: unknown` (concept: SourceFile) (completed: 1405/05/03)
- [x] Fix categorize preamble preservation: preserve text between frontmatter and first event heading (concept: SourceFile) (completed: 1405/05/03)
- [x] Fix SourceCoverage: pass `--source-coverage` to merge CLI from chain.ps1 when requested (concept: Command, Verification) (completed: 1405/05/03)
- [x] Make REVIEW verdict enforceable in `run_topic_report.py`: return exit 2 when verdict is REVIEW unless `--allow-review` passed (concept: Verification, Command) (completed: 1405/05/03)
- [x] Align `docs/TRACELEDGER_INTEGRATION_CONTRACT.md` with actual `process_docx_v3(cfg, logger, jsonl_path)` signature (concept: Doc) (completed: 1405/05/03)
- [x] Bump catalog schema to v2 with explicit `hash_mode` field; update checker and tests (concept: ConfigFile, Verification) (completed: 1405/05/03)
- [x] Document TOC adapter three-case contract in `wordpipe/steps/toc.py` docstring (concept: Doc) (completed: 1405/05/03)

## P0 Reliability Remediation — Completed: 1405/05/02

- [x] Add `--strict` flag to `verify_integrity.py` invocation in `tools/orchestrate.py` (concept: Verification, Command) (completed: 1405/05/02)
- [x] Add malformed event heading pre-scan in `wordpipe/chronicle/merge.py` that rejects any `## Event:` line not matching canonical ISO format (concept: Verification, SourceFile) (completed: 1405/05/02)
- [x] Move `MergedpipelineV3` import from `run()` to `__init__()` in `ComFlattener` for eager failure at construction time (concept: SourceFile, Command) (completed: 1405/05/02)
- [x] Remove bare `except Exception: return` blocks in `Win32MergedpipelineV3TocUpdater.update()`; conditionalize `toc_updater` in `build_default_deps()` to supply `None` on non-Windows (concept: SourceFile, Verification) (completed: 1405/05/02)
- [x] Rewrite WordPipe CLI to call `process_docx_v3` directly and return non-zero exit code when `RunReport.errors` is non-empty (concept: Command, Verification) (completed: 1405/05/02)
- [x] Add `--in`/`--out` resolved-path guard to WordPipe CLI, rejecting identical input/output paths before any mutation (concept: Command, Verification) (completed: 1405/05/02)
- [x] Add test files: `test_p0_cli.py` (orchestration `--strict`, CLI exit code, path guard), `test_pipeline_contracts.py` (`StageResult.finalize` strict/non-strict), `test_flatteners.py` (import-safety, construction-fail, fallback), plus P0.2 validation tests in `test_pipeline_chronicle.py` and P0.4 adapter test in `test_steps.py` (concept: Verification) (completed: 1405/05/02)

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

The third-adapter and unsafe-serializer conditions are primary triggers. Secondary signals require audited evidence and do not mandate decomposition from one occurrence; repeated cross-module defects must have two dated, path- and test-backed records in `JOURNAL.md` or the implementation-alignment audit.

- [x] Common preparation-metrics validation and fail-closed prepare contract (concept: Verification, Command) (completed: 1405/04/26 — tools/run_topic_report.py)
- [x] Consumed-source metrics semantics and built-in file-level source_lineage (concept: Evidence, Artifact) (completed: 1405/04/26 — both prepare adapters)
- [x] Lineage-aware aggregate source attribution (concept: Evidence) (completed: 1405/04/26 — source_attribution.json)
- [x] Project Phase 15 semantic ontology design document (concept: Doc, Entity) (completed: 1405/04/26 — docs/PHASE15_PROJECT_SEMANTIC_ONTOLOGY_DESIGN.md)
- [x] Enforce append-only run IDs, safe staged filenames, and finite preparation coverage (concept: Verification, Command) (completed: 1405/04/26)
- [x] Migrate and hash-catalog the 19 active Markdown inputs without changing corpus membership (concept: Artifact, Evidence) (completed: 1405/04/26 — inputs/catalog.json)
- [x] Add repository agent evidence protocol and CI input-catalog guard (concept: Verification, Doc) (completed: 1405/04/26 — AGENTS.md)
- [x] Replace superseded Phase 15 evidence with fresh collision-protected v2 runs (concept: Evidence, Verification) (completed: 1405/04/26)
- [x] Define the whole-project domain crosswalk, refactor eligibility gate, and enforce narrow production import boundaries without restructuring production modules (concept: Doc, Verification) (completed: 1405/04/26 — ARCHITECTURE_AND_MODULES.md, tools/check_architecture_boundaries.py)
- [x] Project Phase 16 characterization tests for ingest/merge identity behavior (concept: Verification) (completed: 1405/04/26 — tests/test_phase16_event_identity_characterization.py)
- [x] Adapter raw event_lineage emit + runner pre-pipeline envelope (`event-lineage-v1`) (concept: Evidence, Command) (completed: 1405/04/26)
- [x] Post-pipeline normalised fingerprint correlation (`event-correlation-v1`) before summarize with provenance fail-closed exit (concept: Evidence, Verification) (completed: 1405/04/26)
- [x] Project Phase 16 design doc and aggregate→individual ontology migration gate (concept: Doc, Entity) (completed: 1405/04/26 — docs/PHASE16_EVENT_IDENTITY_AND_SECTION_PROVENANCE.md)
- [x] Fresh paired Phase 16 controlled runs under `phase16_event_lineage_validation` (concept: Evidence, Verification) (completed: 1405/04/26)
- [x] Add merge-note-aware actual survivor-key verification without changing Chronicle merge behavior (concept: Verification, Evidence) (completed: 1405/04/26 — merged-note-aware-v1 in tools/run_topic_report.py)
- [x] Compare Phase 16 and a fresh paired Phase 17 run for exact SourceEvent/ReportEvent id stability (concept: Verification, Evidence) (completed: 1405/04/26 — tools/compare_event_provenance_stability.py + phase17_provenance_stability)
- [x] Assess the Phase 17 repeatability gate before any individual ontology ReportEvent design or emission (concept: Entity, Verification) (completed: 1405/04/26 — docs/PHASE17_EVENT_PROVENANCE_SURVIVOR_AND_REPEATABILITY.md)
- [x] Inventory, map, and commit the actual Phase 13–17 dirty-tree scope (concept: Doc, Verification) (completed: 1405/04/26 — docs/engineering/PHASE13_17_COMMIT_DRAFT.md; commit `a635ea2`)

---

## Phase 10: Documentation Architecture & Module Reference (P0) — Target: 1404/11/25

- [x] Create `ARCHITECTURE_AND_MODULES.md` — comprehensive reference covering all 3 subsystems (chronicle, evidence, wordpipe) with architecture, modules, data flow, logic flow, goals, constraints, integration, contracts (completed: 1404/11/25) (concept: Doc)
- [x] Create `docs/OBSOLETE_DOCS.md` — index of superseded vs preserved documentation (completed: 1404/11/25) (concept: Doc)
- [x] Update `docs/README.md` — redirect to current source of truth, reference ARCHITECTURE_AND_MODULES.md (completed: 1404/11/25) (concept: Doc)
- [x] Update `ROADMAP.md` — add reference to ARCHITECTURE_AND_MODULES.md (completed: 1404/11/25) (concept: Doc)
- [x] Update `JOURNAL.md` — add Phase 7 to newest-first activity list; add Period 10? (completed: 1404/11/25) (concept: Doc)
- [x] Update `ONTOLOGY_MODEL.md` — add chronicle pipeline artifacts, claims C11-C18, Phase 7 and P9/P9b/P9c activity periods (completed: 1404/11/25) (concept: Doc)

## Phase 11: Topic Adapter Performance Loop (P1) — Target: 1405/04/25

- [x] Create `tools/prepare_insurancechatbot_chronicle.py` to stage commit history, project digest, and roadmap files for Chronicle ingestion (completed: 1405/04/25) (concept: SourceFile, Command)
- [x] Create `WordHorrorStories/insurancechatbot/themes.insurancechatbot.json` for InsuranceChatbot-specific report tags (completed: 1405/04/25) (concept: ConfigFile)
- [x] Fix ISO-date event extraction in `wordpipe/chronicle/ingest.py` for staged topic events (completed: 1405/04/25) (concept: SourceFile)
- [x] Create `tests/test_prepare_insurancechatbot_chronicle.py` for topic adapter parsing and staged-event compatibility (completed: 1405/04/25) (concept: Verification, SourceFile)
- [x] Run measured InsuranceChatbot report: 3 inputs, 200 staged events, 200 merged events, 194 tagged events, 0 warnings/errors, 6.96s wall time (completed: 1405/04/25) (concept: Evidence, Verification)
- [x] Create `docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md` for future topic performance checks (completed: 1405/04/25) (concept: Doc, Verification)

## Phase 13: Generic Topic Report Runner & Performance Trends (P1) — Target: 1405/04/25

- [x] Define topic-run manifest schema with topic name, input directory, adapter, theme config, output policy, and quality gates (concept: ConfigFile) (completed: 1405/04/25)
- [x] Build one-command runner for prepare -> pipeline -> summarize -> trend update (concept: Command, Verification) (completed: 1405/04/25)
- [x] Refactor InsuranceChatbot preparation into first registry-backed adapter (concept: SourceFile, Command) (completed: 1405/04/25)
- [x] Add trend comparison using previous run metrics for the same topic (concept: Evidence, Verification) (completed: 1405/04/25)
- [x] Emit `topic_run_manifest.json` and `topic_run_ontology.json` per run (concept: Evidence, Entity) (completed: 1405/04/25 — minimal spine; full ontology population deferred)
- [x] Improve source attribution in appendix output or sidecar JSON (concept: Evidence, Artifact) (completed: 1405/04/25 — source_attribution.json)
- [x] Add tests for manifest parsing, dry-run execution, trend comparison, source attribution, and ontology-spine output (concept: Verification) (completed: 1405/04/25)
- [x] Sync README/ROADMAP/architecture docs with the generic runner command after implementation (concept: Doc) (completed: 1405/04/25)

## Phase 14: Second Topic Adapter & Multi-Topic Ontology Readiness (P1) — Target: 1405/04/25

- [x] Identify a second Markdown topic candidate (concept: Evidence) (completed: 1405/04/25 — selected `_ARCHIVE/pipeline-chronicle/`, 5 files)
- [x] Create generic Markdown-section adapter `tools/prepare_generic_markdown_chronicle.py` (concept: SourceFile, Command) (completed: 1405/04/25)
- [x] Register adapter in `ADAPTER_REGISTRY` and add topic folder with manifest, themes, and README (concept: ConfigFile, Doc) (completed: 1405/04/25)
- [x] Run baseline + trend runs for the second topic through the generic runner (concept: Evidence, Verification) (completed: 1405/04/25)
- [x] Validate ontology spine with multi-topic evidence — all 10 entity types, all 7 relation types, PASS verdict (concept: Entity, Verification) (completed: 1405/04/25)
- [x] Add adapter tests and runner registry test (concept: Verification) (completed: 1405/04/25)
- [x] Update docs and assess Phase 15 readiness (concept: Doc) (completed: 1405/04/25)
- [x] Remediate Phase 14 genericity findings: date-derived month headings, manifest-topic summaries, canonical `##` event boundaries, and context mapping (concept: SourceFile, Verification, Doc) (completed: 1405/04/25)
- [x] Audit roadmap phases against implementation, label partial/outstanding work, organize root outputs/scripts, and add enforceable root rules (concept: Verification, Doc, Artifact) (completed: 1405/04/25)

## Phase 1: Foundation Fixes (P0)

- [x] Replace absolute Windows paths in docs with relative paths (completed: 1404/11/25) (concept: Doc)
- [x] Verify each `.md` description matches actual source files (concept: Claim, Verification) (completed: 1404/12/05 — G2 verified in P0-P2 validation pass)
- [x] Create/update `README.md` with entrypoint (completed: 1404/11/25) (concept: Doc)
- [x] Create `INDEX.md` — file map of the project (completed: 1404/11/25) (concept: Doc)
- [x] Create `ROADMAP.md` (completed: 1404/11/25) (concept: Doc)
- [x] Create `REPO_ORGANIZATION_PLAN.md` — comprehensive modularization plan (completed: 1404/11/25) (concept: Doc)

## Phase 2: Ontology & Journal (P1)

- [x] Design ontological model skeleton (entities, relations, periods) (completed: 1404/11/25) (concept: Entity)
- [x] Create `ONTOLOGY_MODEL.md` with entity definitions (completed: 1404/11/25) (concept: Doc)
- [x] Create `JOURNAL.md` with period-based entries (completed: 1404/11/25) (concept: Doc, ActivityPeriod)
- [ ] Map existing labor notes, reports, and plans into ontology (concept: ActivityPeriod, Artifact)
- [ ] Evaluate NLP/POS tagging approach for ontology population (concept: Entity)

## Phase 3: Critical Bug Fixes (P0) — Target: 1404/12/05

> **Note:** Several items below target `wordpipe/ai/` files that were quarantined to `scripts/ai/` in the P0-P2 pass. The underlying bugs may still exist in those quarantined scripts but no longer affect the packaged library.

- [x] Remove duplicate `style_code_blocks()` in `wordpipe/code_style.py` (concept: SourceFile) (completed: 1404/12/05)
- [x] Fix `os.makedirs()` bug in `wordpipe/logging_tools.py` (concept: SourceFile) (superseded: compatibility wrapper no longer performs path creation)
- [x] Fix duplicate imports in `wordpipe/logging_tools.py` (concept: SourceFile) (completed: 1404/12/05)
- [ ] Fix `persiantools` lazy import in `wordpipe/ai/timefmt.py` (concept: SourceFile)

## Phase 4: AI Module Refactor (P1) — Target: 1404/12/10

> **Note:** Superseded by the AI quarantine pass (P0-P2). The `wordpipe/ai/` package is now a deprecation stub; all scripts moved to `scripts/ai/`. If these modules are needed in the library, they should be re-created as new `wordpipe/adapters/ai/` modules (not resurrected in `wordpipe/ai/`).

- [ ] Create `wordpipe/ai/config.py` — env parsing, no side effects (concept: SourceFile)
- [ ] Create `wordpipe/ai/provider_factory.py` — constructs providers (concept: SourceFile)
- [ ] Create `wordpipe/ai/logging_setup.py` — logger configuration (concept: SourceFile)
- [ ] Create `wordpipe/ai/runtime.py` — canary + reorganize orchestration (concept: SourceFile)
- [ ] Create `wordpipe/ai/cli.py` — argparse, optional dotenv (concept: SourceFile)
- [ ] Convert all `wordpipe/ai/` imports to package-safe paths (concept: SourceFile)
- [ ] Replace silent `except Exception: pass` with structured warnings (concept: SourceFile)

## Phase 5: Split Orchestrator into Steps (P1) — Target: 1404/12/15

- [x] Create `wordpipe/steps/flatten.py` — flatten_step() (completed: 1404/11/25) (concept: SourceFile)
- [x] Create `wordpipe/steps/style.py` — style_step() (completed: 1404/11/25) (concept: SourceFile)
- [x] Create `wordpipe/steps/segment.py` — segment_step() (completed: 1404/11/25) (concept: SourceFile)
- [x] Create `wordpipe/steps/finalize.py` — finalize_step() (completed: 1404/11/25) (concept: SourceFile)
- [x] Create `wordpipe/steps/toc.py` — toc_step() (completed: 1404/11/25) (concept: SourceFile)
- [x] Refactor `WordPipePipeline.run()` to compose step modules (completed: 1404/11/25) (concept: SourceFile)

## Phase 6: Tool Hardening (P1) — Target: 1404/12/20

- [ ] Add `--portable` flag to `verify_integrity.py` (concept: Verification, Command)
- [ ] Add `src_rel`/`dst_rel` fields to relocation map (concept: Artifact, Evidence)
- [ ] Fix absolute-path drift in verification reports (concept: Artifact, Evidence)

## Phase 7: Optimization & Duplicate Governance (P2) — Target: 1404/12/25

- [x] Optimize `wordpipe/core/segment.py` to O(n) heading context (concept: SourceFile) (superseded: active algorithm moved to `wordpipe/adapters/docx/segmenter.py`; core module is a deprecation stub)
- [ ] Create `tools/duplicate_scan.py` (concept: DuplicateSet, Command)

## Phase 8: CI & Governance (P2) — Target: 1404/12/30

- [ ] Add CI profile: `runtime` (compile/lint/test tools/, wordpipe/) (concept: Verification)
- [ ] Add CI profile: `evidence` (verify integrity, check audit artifacts) (concept: Verification)
- [ ] Remote refs audit for leaked keys in old branches (concept: Verification)
- [ ] Add deprecation warnings to compatibility wrappers (concept: CompatibilityWrapper)

## Phase 9: Chronicle Automation Pipeline (P3) — Target: 1404/12/20

### Sub-phase 9a: Tool Completion & Archival (completed: 1404/11/25)

- [x] Create `tools/pipeline-chronicle/config.json` — shared config loading ontology.json + theme keywords + header taxonomy (completed: 1404/11/25) (concept: ConfigFile)
- [x] Build `tools/pipeline-chronicle/ingest.py` — deep-search → normalised MD with YAML front-matter (completed: 1404/11/25) (concept: SourceFile, Command)
- [x] Build `tools/pipeline-chronicle/verify_ingest.py` — verification script for ingest.py (completed: 1404/11/25) (concept: SourceFile, Command, Verification)
- [x] Apply P0/P1 fixes to ingest.py: preamble preservation, CLI reduction (11→5), title fallback (H1→H2→source), mojibake map cleanup (completed: 1404/11/25) (concept: SourceFile)
- [x] Build `tools/pipeline-chronicle/merge.py` — merge N normalised MDs, dedup by hash+date, 3 conflict modes, duplicates report, source coverage (completed: 1404/11/25) (concept: SourceFile, Command)
- [x] Create `tools/pipeline-chronicle/PIPELINE_PLAN.md` — revised stage-based implementation plan (completed: 1404/11/25) (concept: Doc)
- [x] Build `tools/pipeline-chronicle/categorize.py` — theme tagging with config-driven keywords, built-in defaults, JSON+YAML config, sidecar JSON (completed: 1404/11/25) (concept: SourceFile, Command)
- [x] Archive all 5 chronicle pipeline tools to `_ARCHIVE/pipeline-chronicle/` with comprehensive ARCHIVE_REPORT.md (10 sections: overview, tool inventory, architecture, CLI signatures, known issues, test results, ontology cross-reference, restoration instructions, file checksums, change log) (completed: 1404/11/25) (concept: Artifact, Doc)
- [x] Create `tests/test_pipeline_chronicle.py` — 59 tests covering ingest, merge, categorize, verify_ingest core functions + full-pipeline integration (completed: 1404/11/25) (concept: Verification, SourceFile)
- [x] Run tag quality review on `chronicle_tagged.md` — 61 events, 96.7% coverage, 29.5% over-tagging, 2 false negatives identified (completed: 1404/11/25) (concept: Verification, Claim)

### Sub-phase 9b: Keyword Tuning & Index Builder (completed: 1404/11/25)

- [x] Apply keyword adjustments to categorize.py built-in defaults: tighten "exploit"→"prompt exploit", "crash"→"server crash", "error"→"server error"; add "Linux terminal", "simulating", "mega-viral", "interface"; add negative_keywords per theme (completed: 1404/11/25) (concept: SourceFile)
- [x] Create `pipeline/themes.json` — external theme config with positive + negative keywords (completed: 1404/11/25) (concept: ConfigFile)
- [x] Create `pipeline/categorize.py` — updated version with negative keyword support, backward-compatible config loading, --dry-run flag (completed: 1404/11/25) (concept: SourceFile, Command)
- [x] Re-run pipeline after keyword adjustments and verify improvement: 100% coverage (was 96.7%), over-tagging 18.0% (was 29.5%), false negatives eliminated (completed: 1404/11/25) (concept: Verification)
- [x] Build `pipeline/index.py` — generates event_index.md, theme_index.md, source_manifest.md, link_registry.md; Jinja2 templates with fallback formatting; atomic file writes; dedup by title with theme/source merging (completed: 1404/11/25) (concept: SourceFile, Command, Evidence)
- [x] Create `pipeline/index_config.json` — configurable output dir, templates dir, dedup method, theme sort, link registry toggle (completed: 1404/11/25) (concept: ConfigFile)
- [x] Create `pipeline/templates/` — 4 Jinja2 templates (event_index.md.j2, theme_index.md.j2, source_manifest.md.j2, link_registry.md.j2) with fallback string formatting (completed: 1404/11/25) (concept: Artifact)
- [x] Update `pipeline/chain.ps1` — add Stage 5 (index generation) with -SkipIndex, -NoLinkRegistry, -SourceCoverage, -IndexConfig switches (completed: 1404/11/25) (concept: Command)

### Sub-phase 9c: Reference Builder & Ontology Wiring (next)

- [ ] Build `pipeline/reference.py` — secondary TOC, topic model, stable anchor IDs for future AI iteration (concept: SourceFile, Command, Doc)
- [x] Add P9 Chronicle Automation ActivityPeriod to ontology.json (concept: ActivityPeriod, Phase) (completed: 1404/11/25)
- [ ] Extend project ontology with Phase 13/14 TopicRun and evidence instances (concept: ActivityPeriod, Entity, Evidence) (OUTSTANDING)
- [ ] Validate against existing manual merge (`ChatGPT_Incidents_Merged.md`) — pipeline output should match (concept: Verification)
- [x] Generalize the InsuranceChatbot topic-adapter pattern into a reusable adapter registry and single run command (concept: Command, ConfigFile, Verification) (completed: 1405/04/25 — Phase 13)

---

## Completed

| Task | Completed Date | Ontology Links |
|------|----------------|----------------|
| Create topic-neutral iterative performance template | 1405/04/25 | Doc, Verification |
| Add InsuranceChatbot topic adapter and measured run evidence | 1405/04/25 | SourceFile, Evidence |
| Replace absolute Windows paths in docs with relative paths | 1404/11/25 | Doc |
| Create/update README.md with entrypoint | 1404/11/25 | Doc |
| Create INDEX.md — file map of the project | 1404/11/25 | Doc |
| Create ROADMAP.md | 1404/11/25 | Doc |
| Create REPO_ORGANIZATION_PLAN.md | 1404/11/25 | Doc |
| Design ontological model skeleton | 1404/11/25 | Entity |
| Create ONTOLOGY_MODEL.md with entity definitions | 1404/11/25 | Doc |
| Create JOURNAL.md with period-based entries | 1404/11/25 | Doc, ActivityPeriod |
| Create VERIFICATION.md with claim cross-reference | 1404/11/25 | Claim, Verification |
| Create ontology.json (machine-readable) | 1404/11/25 | Entity |
| Create ONTOLOGY.md (human-readable index) | 1404/11/25 | Doc |
| Create PLAN.md (this file) | 1404/11/25 | Doc |
| Create PROJECT_INDEX.md | 1404/11/25 | Doc |
| Analyze all duplicates, apply standard headers | 1404/11/25 | DuplicateSet, SourceFile |
| Fix absolute paths in PIPELINE_RUNBOOK.md and TOOLS_MODULES_INTEGRATION_REPORT.md | 1404/11/25 | Doc |
| Create tools/add_standard_headers.py | 1404/11/25 | SourceFile, Command |
| Apply standard Jalali-date headers to 82 Python files | 1404/11/25 | SourceFile |
| Clean 45 files with duplicate headers | 1404/11/25 | SourceFile |
| Remove BOM from tools/jalali.py | 1404/11/25 | SourceFile |
| Create wordpipe/steps/ (flatten, style, segment, finalize, toc) | 1404/11/25 | SourceFile |
| Refactor WordPipePipeline.run() to compose step modules | 1404/11/25 | SourceFile |
| Build tools/pipeline-chronicle/ingest.py | 1404/11/25 | SourceFile, Command |
| Build tools/pipeline-chronicle/verify_ingest.py | 1404/11/25 | SourceFile, Command, Verification |
| Apply P0/P1 fixes to ingest.py (preamble, CLI reduction, title, mojibake) | 1404/11/25 | SourceFile |
| Build tools/pipeline-chronicle/merge.py | 1404/11/25 | SourceFile, Command |
| Create tools/pipeline-chronicle/PIPELINE_PLAN.md | 1404/11/25 | Doc |
| Build tools/pipeline-chronicle/categorize.py | 1404/11/25 | SourceFile, Command |
| Archive all 5 chronicle pipeline tools to _ARCHIVE/pipeline-chronicle/ with ARCHIVE_REPORT.md | 1404/11/25 | Artifact, Doc |
| Create tests/test_pipeline_chronicle.py — 59 tests | 1404/11/25 | Verification, SourceFile |
| Run tag quality review on chronicle_tagged.md | 1404/11/25 | Verification, Claim |
| Apply keyword adjustments to categorize.py (tightened keywords, negative_keywords, external themes.json) | 1404/11/25 | SourceFile, ConfigFile |
| Build pipeline/index.py with Jinja2 templates + fallback formatting | 1404/11/25 | SourceFile, Command, Evidence |
| Create pipeline/templates/ (4 Jinja2 templates) | 1404/11/25 | Artifact |
| Update pipeline/chain.ps1 with Stage 5 (index generation) | 1404/11/25 | Command |
| Re-run pipeline: 100% coverage, 18.0% over-tagging (was 29.5%), false negatives eliminated | 1404/11/25 | Verification |
| Create ARCHITECTURE_AND_MODULES.md — comprehensive 3-subsystem reference | 1404/11/25 | Doc |
| Create docs/OBSOLETE_DOCS.md — index superseded vs preserved docs | 1404/11/25 | Doc |
| Update docs/README.md as redirect to current source of truth | 1404/11/25 | Doc |
| Update ROADMAP.md, JOURNAL.md, ONTOLOGY_MODEL.md, PLAN.md for Phase 10 | 1404/11/25 | Doc |

---

## Change Log

| Date (Jalali) | Change |
|---------------|--------|
| 1404/11/25 | Initial plan created |
| 1404/11/25 | Expanded to 8 phases with targets; added REPO_ORGANIZATION_PLAN.md |
| 1404/11/25 | Phase 5 completed: Split orchestrator into step modules (wordpipe/steps/) |
| 1404/11/25 | Phase 9: ingest.py built, verified, and P0/P1 fixes applied (preamble, CLI reduction, title, mojibake) |
| 1404/11/25 | Phase 9: merge.py built with 3 conflict modes, duplicates report, source coverage. PIPELINE_PLAN.md created. |
| 1404/11/25 | Phase 9: categorize.py built with built-in default themes, JSON+YAML config, substring matching, sidecar JSON. Critique-driven fixes applied to merge.py. |
| 1404/11/25 | Phase 9: All 5 tools archived to _ARCHIVE/pipeline-chronicle/ with ARCHIVE_REPORT.md. 59 tests created. Tag quality review completed. |
| 1404/11/25 | Phase 9b: Keyword adjustments applied (tightened keywords, negative_keywords, external themes.json). pipeline/index.py built with Jinja2 templates + fallback. pipeline/chain.ps1 updated with Stage 5. Pipeline re-run: 100% coverage, 18.0% over-tagging (was 29.5%). |
| 1404/11/25 | Phase 10: Created ARCHITECTURE_AND_MODULES.md (comprehensive 3-subsystem reference), docs/OBSOLETE_DOCS.md (superseded docs index). Updated docs/README.md (redirect), ROADMAP.md, JOURNAL.md, ONTOLOGY_MODEL.md, PLAN.md. |
| 1405/04/25 | Phase 13: Completed generic topic runner with registry-backed InsuranceChatbot adapter, trend reports, source attribution, ontology evidence hardening, 124 passing tests, and controlled runs phase13_baseline_validation / phase13_trend_validation. |
