# 🗺️ Project Roadmap

> **Date (Gregorian):** 2026-02-14  
> **Date (Shamsi/Jalali):** 1404-11-25  
> **Last Updated:** 2026-02-14  
> **Branch:** `main`  
> **Commit:** `HEAD` (working tree has untracked `pipeline/` files)

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
| G1 | **Path portability**: All doc paths relative, no absolute `F:\...` references | P0 | ✅ Done |
| G2 | **Doc accuracy verification**: Verify all `.md` descriptions match actual code/modules | P0 | 🔴 Not started |
| G3 | **Ontological model**: Build a structured ontology of project entities, periods, claims, evidence | P1 | ✅ Done |
| G4 | **Journal system**: Create dated journal tracking periods of activity with claims/results/verification | P1 | ✅ Done |
| G5 | **Roadmap anchor**: Single source of truth for planned vs completed work | P0 | ✅ Done |
| G6 | **Comprehensive architecture reference**: ARCHITECTURE_AND_MODULES.md covering all 3 subsystems | P0 | ✅ Done |
| G7 | **NLP/ontology grounding**: Evaluate NLP/POS tagging for extracting ontology from project text | P2 | 🔴 Not started |
| G8 | **TraceLedger alignment**: WordPipe as a library consumable by TraceLedger | P1 | 🟡 Planned |
| G9 | **Chronicle automation**: Composable CLI pipeline to ingest, merge, categorize, index deep-search files | P3 | ✅ Done |

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

**Sub-phase 9c: Reference Builder & Ontology Wiring (🔴 Pending)**
| Task | Description | Status |
|------|-------------|--------|
| 9c.1 | Build `pipeline/reference.py` — secondary TOC, topic model, stable anchor IDs | 🔴 |
| 9c.2 | Wire chronicle pipeline into ontology: add P9 ActivityPeriod instances to ontology.json | 🔴 |
| 9c.3 | Validate against existing manual merge (`ChatGPT_Incidents_Merged.md`) | 🔴 |

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
> **Date:** 1404/11/22 | **Status:** ✅ Completed

| Task | Description | Status |
|------|-------------|--------|
| 4.1 | Redact leaked API keys from workspace and .gitignore | ✅ Done |
| 4.2 | Create `.env.example` | ✅ Done |
| 4.3 | Create `tools/security_scan.py` | ✅ Done |
| 4.4 | Create `tools/pipeline_contracts.py` with StagePaths/StageResult/StageError | ✅ Done |
| 4.5 | Create `tools/orchestrate.py` for one-command pipeline | ✅ Done |
| 4.6 | Create pipeline docs (RUNBOOK, CONTRACTS, SECURITY, TOOLS_MODULES, INTEGRATION_MAP, LABOR_REPORT) | ✅ Done |

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

## 🏁 Milestones (Newest First)

| MS# | Milestone | Phase | Target Date | Status |
|-----|-----------|-------|-------------|--------|
| M10 | Comprehensive architecture reference published, old docs indexed as obsolete | Ph10 | 1404-11-25 | ✅ |
| M9 | Tag quality: 100% coverage, <=20% over-tagging | Ph9 | 1404-12-20 | ✅ |
| M8 | Chronicle pipeline operational — ingest→merge→categorize→index works end-to-end | Ph9 | 1404-12-20 | ✅ |
| M7 | WordPipe passes import-safety + unit tests | Ph7 | 1404-12-20 | ✅ |
| M6 | Foundation files (ROADMAP, JOURNAL, ONTOLOGY, INDEX, README) published | Ph6 | 1404-11-25 | ✅ |
| M5 | Documentation pack with role-based entrypoints | Ph5 | 1404-11-24 | ✅ |
| M4 | Security posture improved, pipeline contracts operational | Ph4 | 1404-11-22 | ✅ |
| M3 | Evidence pipeline established with 98 files inventoried | Ph3 | 1404-11-21 | ✅ |
| M2 | Doc accuracy verified — all `.md` claims match code | Ph10 | 1404-12-05 | 🔴 |
| M1 | All doc paths are relative, no `F:\...` in docs | Ph6 | 1404-11-25 | ✅ |

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
- [`docs/OBSOLETE_DOCS.md`](docs/OBSOLETE_DOCS.md) — Index of superseded vs preserved documentation
- [`docs/README.md`](docs/README.md) — Documentation entrypoint (redirects to current source of truth)
