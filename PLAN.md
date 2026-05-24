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

- [ ] Verify all doc descriptions match actual source files (concept: Claim, Verification)
- [ ] Map existing labor notes, reports, and plans into ontology (concept: ActivityPeriod, Artifact)
- [ ] Evaluate NLP/POS tagging approach for ontology population (concept: Entity)
- [ ] Add `--portable` flag to `verify_integrity.py` (concept: Verification, Command)
- [ ] Add `src_rel`/`dst_rel` fields to relocation map (concept: Artifact, Evidence)
- [ ] Fix absolute-path drift in verification reports (concept: Artifact, Evidence)
- [ ] Remove duplicate `style_code_blocks()` in `wordpipe/code_style.py` (concept: SourceFile)
- [ ] Fix `os.makedirs()` bug in `wordpipe/logging_tools.py` (concept: SourceFile)
- [ ] Fix duplicate imports in `wordpipe/logging_tools.py` (concept: SourceFile)
- [ ] Split `process_docx_v3` into step modules (concept: SourceFile, ActivityPeriod)
- [ ] Refactor `wordpipe/ai/ailoader.py` into reusable modules (concept: SourceFile)
- [ ] Optimize `wordpipe/core/segment.py` to O(n) heading context (concept: SourceFile)
- [ ] Create `tools/duplicate_scan.py` (concept: DuplicateSet, Command)
- [ ] Add CI profiles (`runtime`, `evidence`) (concept: Verification)
- [ ] Remote refs audit for leaked keys in old branches (concept: Verification)

---

## Phase 10: Documentation Architecture & Module Reference (P0) — Target: 1404/11/25

- [x] Create `ARCHITECTURE_AND_MODULES.md` — comprehensive reference covering all 3 subsystems (chronicle, evidence, wordpipe) with architecture, modules, data flow, logic flow, goals, constraints, integration, contracts (completed: 1404/11/25) (concept: Doc)
- [x] Create `docs/OBSOLETE_DOCS.md` — index of superseded vs preserved documentation (completed: 1404/11/25) (concept: Doc)
- [x] Update `docs/README.md` — redirect to current source of truth, reference ARCHITECTURE_AND_MODULES.md (completed: 1404/11/25) (concept: Doc)
- [x] Update `ROADMAP.md` — add reference to ARCHITECTURE_AND_MODULES.md (completed: 1404/11/25) (concept: Doc)
- [x] Update `JOURNAL.md` — add Phase 7 to newest-first activity list; add Period 10? (completed: 1404/11/25) (concept: Doc)
- [x] Update `ONTOLOGY_MODEL.md` — add chronicle pipeline artifacts, claims C11-C18, Phase 7 and P9/P9b/P9c activity periods (completed: 1404/11/25) (concept: Doc)

## Phase 1: Foundation Fixes (P0)

- [x] Replace absolute Windows paths in docs with relative paths (completed: 1404/11/25) (concept: Doc)
- [ ] Verify each `.md` description matches actual source files (concept: Claim, Verification)
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

- [ ] Remove duplicate `style_code_blocks()` in `wordpipe/code_style.py` (concept: SourceFile)
- [ ] Fix `os.makedirs()` bug in `wordpipe/logging_tools.py` (concept: SourceFile)
- [ ] Fix duplicate imports in `wordpipe/logging_tools.py` (concept: SourceFile)
- [ ] Fix `persiantools` lazy import in `wordpipe/ai/timefmt.py` (concept: SourceFile)

## Phase 4: AI Module Refactor (P1) — Target: 1404/12/10

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

- [ ] Optimize `wordpipe/core/segment.py` to O(n) heading context (concept: SourceFile)
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
- [ ] Wire chronicle pipeline into ontology: add P9 ActivityPeriod instances to ontology.json (concept: ActivityPeriod, Phase)
- [ ] Validate against existing manual merge (`ChatGPT_Incidents_Merged.md`) — pipeline output should match (concept: Verification)

---

## Completed

| Task | Completed Date | Ontology Links |
|------|----------------|----------------|
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
