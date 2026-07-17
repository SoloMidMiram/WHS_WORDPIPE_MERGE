---
source: 03 Roadmap
title: InsuranceChatbot Roadmap
input_file: 03_roadmap.md
event_count: 20
date: 2026-05-11 to 2026-07-14
---

# Source: 03 Roadmap

## Event: 2026-07-01 – Roadmap folder integration index

Every file in `docs/roadmap/` has a role in the stack. Use this table to decide whether a file is the active queue, strategic context, scoped execution history, support evidence, or a governance index.

| File | Role in the roadmap stack |
|---|---|
| [`ROADMAP.md`](ROADMAP.md) | Active detailed roadmap, current backlog, and historical phase record |
| [`PR4_RUNTIME_REALITY_STABILIZATION_ROADMAP.md`](PR4_RUNTIME_REALITY_STABILIZATION_ROADMAP.md) | Near-term operating plan for PR #4 closure, runtime/evaluation alignment, CI retrieval acceptance, ontology reload consistency, and observability completion |
| [`PHASE21-22_CONSOLIDATED_EXECUTION_ROADMAP.md`](PHASE21-22_CONSOLIDATED_EXECUTION_ROADMAP.md) | Active ordered execution queue for diagnostics, corpus work, inherited follow-through, and gated tuning |
| [`FUTURE_OUTSTANDING_WORKS_ROADMAP.md`](FUTURE_OUTSTANDING_WORKS_ROADMAP.md) | Subject-organized future backlog for site runs, scraping, corpus comparison, FAQ quality, lifecycle full recheck, and recalculation |
| [`THROUGH_PHASE23_STRATEGIC_ROADMAP.md`](THROUGH_PHASE23_STRATEGIC_ROADMAP.md) | Strategic umbrella through Phase 23 and calculator maintainability |
| [`PREEXISTING_TEST_FAILURE_REMEDIATION_ROADMAP.md`](PREEXISTING_TEST_FAILURE_REMEDIATION_ROADMAP.md) | Inherited test-failure remediation slices and closure gates |
| [`PHASE20_RECONCILIATION_AND_TUNING_READINESS_ROADMAP.md`](PHASE20_RECONCILIATION_AND_TUNING_READINESS_ROADMAP.md) | Phase 20 reconciliation pass and tuning-readiness framing |
| [`2026-07-07_phase19_measured_retrieval_runtime_diagnostics_roadmap.md`](2026-07-07_phase19_measured_retrieval_runtime_diagnostics_roadmap.md) | Phase 19 evaluate-first retrieval and runtime diagnostics spine |
| [`2026-07-07_phase19_foundation_cursor_execution_roadmap.md`](2026-07-07_phase19_foundation_cursor_execution_roadmap.md) | Phase 19 foundation execution handoff for branch stabilization |
| [`2026-07-07_deep_search_ontology_extraction_plan.md`](2026-07-07_deep_search_ontology_extraction_plan.md) | Implemented R2/R3/R6/R7 ontology extraction plan and validation notes |
| [`2026-07-07_interface_roadmap.md`](2026-07-07_interface_roadmap.md) | Website-facing API/UI/deploy roadmap, separate from ontology/retrieval numbering |
| [`2026-07-06_phase18_practical_hardening_roadmap.md`](2026-07-06_phase18_practical_hardening_roadmap.md) | Phase 18 hardening, CI truthfulness, docs, and data-boundary contracts |
| [`2026-07-06_phase18_practical_hardening_roadmap_v2_cursor_handoff.md`](2026-07-06_phase18_practical_hardening_roadmap_v2_cursor_handoff.md) | Investigation-first Cursor handoff for Phase 18 validation and fixes |
| [`2026-06-25_remediation_sprint.md`](2026-06-25_remediation_sprint.md) | Phase 15 remediation sprint and organization execution sequence |
| [`ROADMAP_REVERSE.md`](ROADMAP_REVERSE.md) | Dependency-first reverse roadmap |
| [`ONTOLOGY_LAYERING_PLAN.md`](ONTOLOGY_LAYERING_PLAN.md) | Long-range ontology architecture and Phase 16+ layer plan |
| [`ONTOLOGY_INVENTORY.md`](ONTOLOGY_INVENTORY.md) | Phase 16a ontology inventory evidence and typed mapping source |
| [`MILESTONE_A_FOUNDATION_TASKS.md`](MILESTONE_A_FOUNDATION_TASKS.md) | Milestone A foundation checklist for core ontology and runtime wiring |
| [`DOCS_ENTRYPOINTS_INDEXES_COPILOT_ROADMAP.md`](DOCS_ENTRYPOINTS_INDEXES_COPILOT_ROADMAP.md) | Documentation stack, entrypoint map, indexes, and Copilot/review-agent guidance |
## Event: 2026-07-01 – 2026-06-25 - Phase 15: Repository Reorganization & Documentation (2026-06-25 - staged archive complete

**Status:** ✅ Staged, source folders retained for later deletion review

**Goal:** Organize 14 phases of accumulated work into coherent structure; add safe metadata and file reference mapping; establish clear dependency tracking for Phase 16+

**Implementation note:** Phase 15 is documentation-led first. Archive-safe files were copied into `archive/`, and the source folders remain in place so the repo stays auditable while cleanup is staged.

| Item | Status | Completion Date |
|:-----|:------:|:---------------:|
| Reverse-order roadmap (ROADMAP_REVERSE.md) | ✅ Complete | 2026-06-25 |
| File reference map (FILE_REFERENCE_MAP.md) | ✅ Complete | 2026-06-25 |
| Dependency graph (DEPENDENCIES.graph.mermaid) | ✅ Complete | 2026-06-25 |
| Implementation plan (2026-06-25_remediation_sprint.md) | ✅ Complete | 2026-06-25 |
| Phase 15 report (PHASE15_REORGANISATION_REPORT.md) | ✅ Complete | 2026-06-25 |
| Second-pass live review ledger (PHASE15_LIVE_REVIEW_SECOND_PASS.md) | ✅ Complete | 2026-06-25 |
| KB metadata (creation/modification dates) | ✅ Complete | 2026-06-25 |
| Investigation flags (body_addon_002, 003) | ✅ Complete | 2026-06-25 |
| Archive & organize non-critical files | ✅ Complete | 2026-06-25 |
| Update forward/reverse roadmaps | ✅ Complete | 2026-06-25 |

**Key deliverables:**
- `docs/roadmap/ROADMAP_REVERSE.md` — Phase dependency analysis (14c ← 14b ← 14a ← ... ← 0)
- `docs/FILE_REFERENCE_MAP.md` — Complete file dependency matrix (runtime critical path, test fixtures, calc engine)
- `docs/DEPENDENCIES.graph.mermaid` — Visual Mermaid diagram of data flow
- `docs/reports/PHASE15_REORGANISATION_REPORT.md` — Before/after ledger, archive review status, and future investigation notes
- `docs/reports/PHASE15_LIVE_REVIEW_SECOND_PASS.md` — Live review decision ledger for active vs cutover-applied surfaces, including the expert-review Word mirror cutover
- `docs/roadmap/2026-06-25_remediation_sprint.md` — Implementation plan with before/after framing and execution order
- `archive/README.md` — Staged archive copy ledger and deletion-review policy
- KB metadata additions — Flagged body_addon_002 & body_addon_003 for Phase 16 investigation (افت قیمت integration)
- Archive markers — Staged archive copies with `.archived.txt` tracking and review status; active sources retained pending later deletion review, including the optional expert-review Word mirror cutover

**Phase 15 will complete after:**
1. Archive copies are staged and their source folders are flagged for later deletion review
2. Implementation report and file reference map stay aligned with the staged archive paths
3. Forward/reverse roadmaps continue to point to the same report and archive ledger
4. Any data-bearing file edits are followed by the normal rebuild and test sequence

**What Phase 15 enables for Phase 16+:**
- Clear file dependency map for future features
- Reverse-order dependency tracking (understand what enables what)
- Safe metadata pattern for creation/modification tracking
- Archive organization protocol for managing accumulated files, staged copies, and review-only deletion flags
- Investigation flags visible in KB for future work prioritization

---
## Event: 2026-07-01 – Current snapshot

| Metric | Value |
|:-------|:-----:|
| Total FAQs | 554 |
| Vector index | 554 x 300 |
| Runtime profile | sample profile for CI, production profile for deploys |
| Core runtime | FastAPI + lifespan startup + readiness-gated routes |
| Retrieval baseline | TF-IDF + FAISS |
| Retrieval policy | route-aware decision layer before response assembly |
| Branch lookup | structured lookup before FAISS for contact queries |
| Metadata | JSON-first with temporary legacy pickle fallback |
| Evaluation | retrieval corpus and eval runner available |
| Current phase | Phase 21–22 consolidated execution (see [`PHASE21-22_CONSOLIDATED_EXECUTION_ROADMAP.md`](PHASE21-22_CONSOLIDATED_EXECUTION_ROADMAP.md)) |
| Release status | v14.0.1 tag line (backport-only); v14.1.0 docs drafted but tag/doc parity is still open |
| Roadmap status | Phase 19 foundation work includes retrieval/runtime ontology, trace diagnostics, observability, and implemented deep-search extraction; the active implementation queue is now the Phase 21-22 consolidated roadmap |
| Core ontology | 95 concepts after R2/R3/R6/R7 deep-search extraction |
| Retrieval ontology | 45 concept retrieval entries |
| Runtime integration ontology | 79 concept feature entries |
## Event: 2026-07-01 – Active backlog

1. Gate 0: land the documented Phase 20 reconciliation work cleanly, with the validation ledger matching the commit/PR state and the resolved `test_answer_quality` blocker called out honestly.
2. Track A: A1 candidate-lifecycle diagnostics is implemented and documented; next expand the eval corpus toward 200+ labeled cases and add decision-surface tests before any measured tuning starts.
3. Track B: finish Phase 19 follow-through by extending observability safely; the sample-profile `test_answer_quality` failure was resolved in P0 stabilization on 2026-07-10.
4. Track C: complete the remaining Phase 17+ FAQ `domain_concept_id` rollout and related bridge cleanup without coupling it to ranking changes.
5. Track D and Track E: close `v14.1.0` tag/doc parity and complete the Phase 15 archive deletion review with path-sync follow-up where needed.
6. Track F: only after Track A exit criteria are met, run small measured tuning slices with before/after eval reports and rollback discipline.
7. Track G and production safety: keep deferred policy items decision-first, and keep admin auth, CORS, rate limits, and deployment health checks fail-closed.

See [`PHASE21-22_CONSOLIDATED_EXECUTION_ROADMAP.md`](PHASE21-22_CONSOLIDATED_EXECUTION_ROADMAP.md) for the ordered queue, [`FUTURE_OUTSTANDING_WORKS_ROADMAP.md`](FUTURE_OUTSTANDING_WORKS_ROADMAP.md) for the subject-organized future backlog, [`PREEXISTING_TEST_FAILURE_REMEDIATION_ROADMAP.md`](PREEXISTING_TEST_FAILURE_REMEDIATION_ROADMAP.md) for inherited test-failure cleanup, [`../reports/phase21_candidate_lifecycle_design.md`](../reports/phase21_candidate_lifecycle_design.md) for the A1 design boundary, [`../reports/phase19_stage7_failure_taxonomy.md`](../reports/phase19_stage7_failure_taxonomy.md) for the lifecycle-tagged evidence, [`THROUGH_PHASE23_STRATEGIC_ROADMAP.md`](THROUGH_PHASE23_STRATEGIC_ROADMAP.md) for the umbrella path through Phase 23, [`2026-07-07_phase19_measured_retrieval_runtime_diagnostics_roadmap.md`](2026-07-07_phase19_measured_retrieval_runtime_diagnostics_roadmap.md) for evaluate-first history, and [`PHASE20_RECONCILIATION_AND_TUNING_READINESS_ROADMAP.md`](PHASE20_RECONCILIATION_AND_TUNING_READINESS_ROADMAP.md) for the completed reconciliation pass.

---
## Event: 2026-07-01 – Phase 16+: Ontology Architecture (In Progress

**Status:** In Progress — Phase 16a complete, Phase 16b seed complete, and core Phase 17 runtime wiring is in place; broad FAQ concept-ID rollout and ontology-driven behavior remain deferred

**Goal:** Separate domain meaning, source extraction, runtime routing, calculation semantics, retrieval metadata, and observability into seven maintainable, independently-versioned layers.

**See:** [`ONTOLOGY_LAYERING_PLAN.md`](ONTOLOGY_LAYERING_PLAN.md) — comprehensive 5-milestone plan for Phases 16–28+

**Quick roadmap:**
## Event: 2025-01-16 – 17)

Core domain ontology + registry
## Event: 2025-01-18 – 20)

Retrieval + runtime integration + health
## Event: 2025-01-21 – 23)

Split calculator ontology
## Event: 2025-01-24 – 25)

Publication mappings + scraper integration
## Event: 2026-07-01 – Milestone E (Phases 26+)

Observability + event logging

**Why now:**
- Boundary hardening (Phase 15) established clear separation between scraper and FAQ
- Active-release schema formalized (Phase 15)
- Health payload wording updated (Phase 15)
- Enough scale (554 FAQs, 9 calc scenarios) to benefit from layered ontology

### Phase 16a — Ontology Inventory (complete)

- Outcome: `docs/roadmap/ONTOLOGY_INVENTORY.md` (3398 labels, 5 conflict families)
- Outcome: `data/analysis/ontology_inventory_review.json` (43 approved typed concept mappings)
- Conflict families resolved: diyat_base, franchise, policy_termination, depreciation, policy_transfer
- Frozen leaf concepts deferred to Phase 16b

**Next step:** complete the remaining Phase 17+ follow-through: optional FAQ `domain_concept_id` rollout, bridge cleanup, and then measured ontology-aware retrieval work after Phase 21 diagnostics
## Event: 2026-07-01 – Outstanding work inherited from earlier phases

This list is the short cross-phase remainder after the Phase 20 reconciliation pass. It is meant to replace guesswork, not the historical phase tables below.

1. Phase 15 archive cleanup is still staged rather than fully closed. The archive copies exist, but source-folder deletion review and any resulting path-sync follow-up remain open.
2. Phase 17 ontology follow-through is partial. `OntologyState`, registry loading, health exposure, and reload wiring are implemented, but broad FAQ `domain_concept_id` rollout is still unfinished.
3. Phase 18 hardening is still carrying release/documentation debt. `v14.1.0` tag/doc parity and ongoing contract synchronization remain open.
4. Phase 19 observability and retrieval follow-through remains incomplete. Structured request-log / route-counter expansion is not done, and Phase 19 is still not a "full green" state, but the former sample-profile `tests/test_answer_quality.py` blocker was resolved on 2026-07-10.
5. Pre-existing test failure remediation remains active for inherited failure clusters outside the cleared `answer_quality` blocker. **Ordered remediation:** [`PREEXISTING_TEST_FAILURE_REMEDIATION_ROADMAP.md`](PREEXISTING_TEST_FAILURE_REMEDIATION_ROADMAP.md).
6. Phase 21 preparation is the next active engineering path. Candidate-lifecycle diagnostics, corpus growth toward 200+ cases, and only then measured tuning remain outstanding. **Ordered queue:** [`PHASE21-22_CONSOLIDATED_EXECUTION_ROADMAP.md`](PHASE21-22_CONSOLIDATED_EXECUTION_ROADMAP.md).
7. Deferred roadmap items remain deferred: active-release indexing policy, scraper ontology publication integration, third-insurer expansion, controlled Playwright acquisition, and related-link fetching.

For future work grouped by practical subject area, use [`FUTURE_OUTSTANDING_WORKS_ROADMAP.md`](FUTURE_OUTSTANDING_WORKS_ROADMAP.md). It expands lifecycle full recheck, site dry-run/actual-run gates, insurance-site scraping, corpus extraction/comparison, FAQ ontology/answer quality, and recalculation/rebuild obligations without changing the active Phase 21-22 order.

---
## Event: 2026-06-01 – Historical phase record

> The phase tables below are retained for traceability. They are not the active roadmap and should not be read as current work ordering.
# Roadmap — Bimeh Knowledge Base
> Part of: [REPORT_INDEX.md](reports/REPORT_INDEX.md)
> Status: âœ… Done | ðŸ”· In Progress | â¬œ Planned | âŒ Blocked | ðŸŸ¡ Deferred
> Last reviewed: 2026-06-05
> **Survey:** [14040307survay.md](reports/14040307survay.md) (1404/03/07) — criticism workbook; drives Phase 11 backlog below

# Roadmap — Bimeh Knowledge Base
## Event: 2026-06-05 – 05

| Metric | Value |
|:-------|:-----:|
| **Total FAQs** | **554** (528 + Phase 13 body 19 + Phase 13b calc 7) |
| Subcategories | **43+** (body, third, injury, calc reference entries) |
| Last phase completed | **Phase 14 — Calc bot + release v14.0.0 âœ…** |
| Git release | **`v14.0.1`** — code + staged deploy runbook |
| FAISS vectors | **554 Ã— 300 dims** (API-compatible tokenizer) |
| Test suite | **136+ passing** (3 known non-blocking failures) |
| Calc bot | **POST /calculate** — ontology v2, coverage pipeline |
| Phase 5d — Audit Cleanup | âœ… Dupes closed; SME triage complete (Phase 12) |
| **Active focus** | **Phase 14c interface stack âœ… â†’ Phase 15 hybrid retrieval** |
| **Deploy runbook** | [PHASE14_SERVER_DEPLOY_PLAN.md](PHASE14_SERVER_DEPLOY_PLAN.md) |

### Top 5 risks (from survey — decide first)

| # | Risk | Priority | Roadmap track |
|:-:|:-----|:--------:|:--------------|
| 1 | Missing `scripts/imports/merge_phase10_branch_json.py` (tests/docs reference it) | ðŸ”´ P0 | Phase 11a |
| 2 | KB + FAISS gitignored — fresh clone needs rebuild | ðŸ”´ P0 | Phase 11a |
| 3 | Tokenizer/index drift (duplicate rebuild scripts, inline tokenize in rebuild) | ðŸ”´ P0 / ðŸŸ¡ P1 | Phase 11a, 11b |
| 4 | TF-IDF retrieval ceiling; no intent routing; global fallback 0.3 only | ðŸŸ¡ P2 / â¬œ P3 | Phase 11c, Variant C/D |
| 5 | Large uncommitted working tree (reorg + Phase 10 artifacts) | ðŸ”´ P0 | Phase 11a |

---
## Event: 2026-05-01 – ðŸ“‹ Phase Completion Tracker

| Phase | Description | Status | Key Deliverables | Date |
|:------|:------------|:------:|:-----------------|:----:|
| **Phase 0** | Cleanup & Dedup (555 â†’ 231 unique) | âœ… **Done** | phase0_clean.json, 307 dupes removed | 2026-05-11 |
| **Phase 1** | Schema design & 35 subcategories | âœ… **Done** | knowledge_base_phase1.json | 2026-05-11 |
| **Phase 2** | Answer writing (231 answers) | âœ… **Done** | knowledge_base_phase2.json | 2026-05-11 |
| **Phase 3** | Enrichment + TF-IDF + FAISS | âœ… **Done** | faiss_index/, 231Ã—293 vectors | 2026-05-11 |
| **Phase 4** | Missing info recovery + subject extraction | âœ… **Done** | Gap matrix, 99% coverage | 2026-05-11 |
| **Phase 5 (API)** | FastAPI deployment, 62 tests, CI | âœ… **Done** | api.py, CI pipeline | 2026-05-14 |
| **Phase 5b** | Deep Search expansion (+147 Qs, 378 total) | âœ… **Done** | knowledge_base_phase5_deep_merged.json | 2026-05-15 |
| **Phase 5c** | Body reorganisation + metadata labeling | âœ… **Done** | body_issuance subcat, faq_type_label + ask_frequency on all | 2026-05-15 |
| **Phase 5d** | Audit Cleanup — delete 3 dupes, fix labels | âœ… **Done** | Dupes removed prior to org; 18 misplaced DS entries deferred | 2026-05-28 |
| **Phase 6** | Third-party content review (NLP, merges, new entries) | âœ… **Done** | 4 merges, 8 new Qs, 613 flow-chain links | 2026-05-15 |
| **Phase 7** | Third-party enrichment — **Ø«Ø§Ù„Ø« Ù…Ø§Ù„ÛŒ 100% enriched** | âœ… **Done ðŸŽ‰** | 74 templates enriched, 202/202 complete | 2026-05-16 |
| **Phase 8 H1** | Short answer expansion (4 body answers <400 chars) | âœ… **Done** | Enriched via Deep Search | 2026-05-16 |
| **Phase 8 H2** | New body questions (13 practical topics) | âœ… **Done** | 13 entries created | 2026-05-16 |
| **Phase 8 H3** | Injury rewrites — 19 rewrite + 16 new = 35 ops | âœ… **Done** | Fixed 2 critical errors, added 16 new | 2026-05-16 |
| **Phase 8 H4** | Ontology update + FAISS rebuild (372â†’409) | âœ… **Done** | Ontology model, 409Ã—300 index | 2026-05-16 |
| **Phase 8 Asia** | Asia migration — 97 entries imported | âœ… **Done** | 27 products + 70 branches, 9 cross-links | 2026-05-16 |
| **Phase 9** | Test & ontology — duplicates, hazm keyword TF-IDF, uncovered predictions | âœ… **Done** | 0 duplicates, 29 new FAQ suggestions, 512 entries | 2026-05-16 |
| **Phase 10 — Web Survey** | Branch address verification — cross-source validation of 70 Asia branches | âœ… **Done** | Deep Research completed, 60 branches corrected, 10 still no data | 2026-05-24 |
| **Phase 10 — Prompt 11** | Real-World Inquiry Integration — 16 entries imported (6 new subcategories) | âœ… **Done** | 16 entries, 6 new subcats, KB now 528 entries | 2026-05-24 |
| **Phase 10 — Branch JSON merge** | Merge 52+18 raw JSONs â†’ map + KB; apply with backup; FAISS rebuild | âœ… **Done** | 70/70 contact, 0 `no_map_data`, see PHASE10_BRANCH_MERGE_VERIFICATION.md | 2026-05-28 |
| **Phase 14 Release** | Git tag v14.0.x, deploy docs, calc bot, 554-FAQ KB | âœ… **Done** | DEPLOY.md, PHASE14_SERVER_DEPLOY_PLAN.md, scripts/deploy/ | 2026-06-05 |
| **Phase 14c Interface stack** | Caddy localhost edge, RTL chat PWA, POST /chat BFF, Telegram bot | âœ… **Done** | `deploy/Caddyfile.local`, `static/chat/`, `src/chat.py`, `/opt/bots/bimeh-telegram/` | 2026-06-05 |

---
## Event: 2026-07-14 – driven

> **Source:** [14040307survay.md](reports/14040307survay.md) (1404/03/07)
> **Goal:** Close engineering debt from Phase 10, add invariant checks, and prepare retrieval/API for production without new FAQ content.

### Capability map (navigation aid)

| Capability | Primary paths | Phase 11 items |
|:-----------|:--------------|:---------------|
| **Ingest** | `scrape/`, `scripts/imports/` | Pydantic validation on Deep Search JSON; `scraped_at` metadata |
| **KB** | `data/processed/knowledge_base_phase10_clean.json` | JSON Schema; duplicate-ID CI tests; relocate 6 misplaced DS |
| **Index** | `scripts/phases/phase10_rebuild_faiss_api_compat.py` | Unify tokenizer; archive deprecated rebuild scripts; index_info hash |
| **Serve** | `src/api.py` | Startup consistency checks; `min_score`; sanitize 500 errors; CORS env |
| **Verify** | `scripts/verify/`, `tests/` | Invariant suite; similarity recall in pytest; map â†” KB parity |
| **Hygiene** | `scripts/imports/`, `docs/rules/KB_HYGIENE.md` | CSV-driven SME workflow; phase5d_merge_decisions.json audit log |

### Phase 11 tracker

| Track | Description | Status | Key deliverables |
|:------|:------------|:------:|:-----------------|
| **11a — P0 Engineering debt** | Restore merge script; commit tree; startup KBâ†”index checks | ðŸ”· **Next** | `merge_phase10_branch_json.py`, startup assertions in `src/api.py` |
| **11b — P1 Quality gates** | Tokenizer single source; similarity in CI; JSON Schema on KB | â¬œ Planned | Refactored rebuild; `test_similarity_recall.py`; KB schema file |
| **11c — P2 Retrieval & API** | Intent router; structured branch contacts; `min_score`; partial contact policy | â¬œ Planned | Router module; `metadata.contact_confidence`; API field |
| **11c — P2 Retrieval & API** | Intent router; structured contacts; `min_score`; CORS from env | âœ… Done | Wave 4 |
| **11d — P3 Strategic** | Hybrid TF-IDF + tag boost; Variant A production stack | â¬œ Planned | See Phases 14-16 |
| **12 — SME Triage** | Content hygiene auto-decide (48 misplaced REJECT, 3 pairs KEEP_BOTH) | âœ… Done | Phase 12 |

### Phase 11a — P0 tasks (do first)

| # | Task | Effort | Acceptance |
|:-:|:-----|:------:|:-----------|
| 1 | **Restore** `scripts/imports/merge_phase10_branch_json.py` | Low | `pytest tests/test_merge_phase10_branch_json.py` collects and passes (or skips only on missing raw inputs, not missing script) |
| 2 | **Commit** working tree in logical chunks (reorg â†’ Phase 10 â†’ personas) | Low | `git status` clean for tracked deliverables |
| 3 | **Startup assertions:** `index.ntotal == len(faq_by_id) == len(pos_to_id)` | Low | Mismatch fails fast at import or `/health` returns `degraded` |
| 4 | **Document** fresh-clone bootstrap: KB present or run `phase10_rebuild_faiss_api_compat.py` | Low | README + `data/README.md` |
| 5 | **Archive** deprecated scripts: `phase10_rebuild_faiss.py`, `phase10_clean_branches_rebuild_faiss.py` | Low | Moved to `archive/scripts/legacy/` + ban list in `scripts/README.md` |

### Phase 11b — P1 tasks

| # | Task | Effort | Acceptance |
|:-:|:-----|:------:|:-----------|
| 6 | Refactor FAISS rebuild to import `src.nlp_utils.tokenize_persian` (no inline copy) | Low | Grep shows single tokenizer path |
| 7 | Promote `tools/similarity_test.py` cases to parametrized pytest | Medium | Recall regression in CI (target â‰¥ 23/24) |
| 8 | JSON Schema validation on KB (pre-commit or import gate) | Medium | Invalid edit blocked before merge |
| 9 | CI duplicate guards: `test_no_duplicate_faq_ids`, optional normalized-question check | Low | Runs on every PR |
| 10 | Write `data/faiss_index/index_info.json` with KB hash + build timestamp on rebuild | Low | `verify_all.py` checks freshness |

### Phase 11c — P2 tasks

| # | Task | Effort | Acceptance |
|:-:|:-----|:------:|:-----------|
| 11 | **Intent router** before FAISS (branch lookup vs policy FAQ) | Medium | Branch queries route to `asia_branch_*` or structured lookup |
| 12 | **Structured `contact`** on branch entries + templated answer rendering | Medium | Phone/address not only in free text |
| 13 | Expose per-request **`min_score`** on `/ask` (or remove from README example) | Low | Docs and API aligned |
| 14 | **Contact confidence policy:** filter or disclaimer for `partial` / `not_found` in API | Medium | Documented behavior for 8 exception branches |
| 15 | **Map â†” KB parity check** for 70 branch codes in `verify_all.py` | Low | Automated post-merge invariant |
| 16 | Pydantic validation on Deep Search branch JSON before merge | Medium | Reject bad phones, wrong area codes |

### Phase 11d — P3 / variant alignment

| Item | Variant | Notes |
|:-----|:--------|:------|
| Hybrid retrieval (TF-IDF + tag/subcategory boost) | C (short-term) | Cheaper than full embedding migration |
| Docker + API key + rate limiting | A | Production hardening |
| In-memory cache + PCA | D | Performance |
| Clarify **company neutrality** vs Asia branch directory scope | E + rules | Update `COMPANY_NEUTRALITY.md` or ROADMAP scope statement |

### Robustness checklist (target: all âœ… in Phase 11)

Add to `scripts/verify/verify_all.py` or `verify_invariants.py`:

- [ ] KB JSON parses; all FAQ `id` values unique
- [ ] `index.ntotal == len(faq_by_id) == len(pos_to_id)`
- [ ] FAISS rebuild imports `src.nlp_utils.tokenize_persian`
- [ ] Branch map â†” KB contact parity (70 codes)
- [ ] No suspect placeholder phones (`021-` in non-Tehran without flag)
- [ ] pytest 62/62 green
- [ ] Similarity recall â‰¥ 23/24
- [ ] `index_info.json` records KB hash + build timestamp

### Conceptual decisions (triage in survey decision log)

| Topic | Options | Default recommendation |
|:------|:--------|:-----------------------|
| Branch FAQs in same FAISS index | Keep shared index vs intent router | **Router** (Phase 11c) |
| Phase 10 "done" with 8 exceptions | Hide vs disclaimer vs block in API | **Disclaimer** until quality pass completes |
| 18 misplaced DS entries | Relocate 6 high-confidence now vs accept noise | **Relocate 6** in Phase 11b; defer 48 heuristic |
| `resolve_kb_path()` archive fallback | Silent fallback vs require `KB_PATH` env in prod | **Require explicit path** in production |
| Multi-turn chat | In-repo vs external session layer | **External** (out of scope for this repo) |

---
## Event: 2026-05-01 – ðŸ”œ Immediate Next Steps

> **Active backlog (2026-05-30):** All 5 waves complete. Remaining: Committing Wave 3-4 changes. See plan at `.cursor/plans/remaining_phases_plan_22a03bc4.plan.md`.

### Phase 11a — P0 (Foundation) âœ… Done

| # | Task | Status |
|:-:|:-----|:------:|
| 1 | Restore `scripts/imports/merge_phase10_branch_json.py` | âœ… Done |
| 2 | Add startup KB â†” FAISS consistency assertions | âœ… Done (`src/api.py`) |
| 3 | Commit uncommitted reorg + Phase 10 artifacts | âœ… Done (2 commits) |
| 4 | Archive deprecated FAISS rebuild scripts | âœ… Done |
| 5 | Document fresh-clone bootstrap | âœ… Done |

### Phase 11b — P1 Verification Gates âœ… Done

| # | Task | Artifact | Status |
|:-:|:-----|:---------|:------:|
| 1 | Create `verify_invariants.py` | `scripts/verify/verify_invariants.py` | âœ… Done |
| 2 | pytest duplicate guard | `tests/test_no_duplicate_faq_ids.py` | âœ… Done |
| 3 | pytest count parity | `tests/test_kb_faiss_count_parity.py` | âœ… Done |
| 4 | Similarity recall test | `tests/test_similarity_recall.py` (â‰¥ 23/24 gate) | âœ… Done |
| 5 | Refactor rebuild â†’ import from `nlp_utils` | `phase10_rebuild_faiss_api_compat.py` | âœ… Done |
| 6 | Emit `index_info.json` with KB hash | During FAISS rebuild | âœ… Done |
| 7 | Report | `docs/reports/PHASE11B_VERIFY_AUTOMATION.md` | âœ… Done |

### Phase 11c — P2 Retrieval & API Hardening âœ… Done

| # | Task | Artifact | Status |
|:-:|:-----|:---------|:------:|
| 1 | Intent router | `src/router.py` — branch vs general, re-ranking | âœ… Done |
| 2 | `min_score` parameter | `AskRequest.min_score`, `/search?min_score=` | âœ… Done |
| 3 | CORS from env var | `CORS_ORIGINS` env var â†’ server starts with restricted origins | âœ… Done |
| 4 | Error sanitization | 500s no longer leak exception details | âœ… Done |
| 5 | Report | `docs/reports/PHASE11C_RETRIEVAL_REPORT.md` | âœ… Done |

### Phase 12 — SME Triage & Content Hygiene (P2) âœ… Complete

> **Status:** All 48 heuristic misplaced entries reviewed and REJECTED (correctly categorized as third-party content). 3 semantic pairs KEEP_BOTH (complementary branded/general content). No KB changes needed. See [PHASE12_SME_TRIAGE_REPORT.md](reports/PHASE12_SME_TRIAGE_REPORT.md).

| # | Task | Artifact | Status |
|:-:|:-----|:---------|:------:|
| 1 | Full similarity scan (384 pairs, 20 clusters) | `data/analysis/phase5d/similarity_clusters.json` | âœ… Done |
| 2 | Semantic review CSV (3 content pairs, asia_branch excluded) | `data/exports/expert_review/semantic_review_pairs.csv` | âœ… Done |
| 3 | CSV-driven relocate script | `scripts/imports/relocate_from_csv.py` | âœ… Done |
| 4 | CSV-driven merge script | `scripts/imports/merge_semantic_dupes.py` | âœ… Done |
| 5 | Merge decision audit log | `data/analysis/phase5d/phase5d_merge_decisions.json` | âœ… Done |
| 6 | KB_HYGIENE.md updated with CSV workflow | `docs/rules/KB_HYGIENE.md` | âœ… Done |
| 7 | SME review — CSVs auto-filled (54 reject + 3 keep_both) | `PHASE5D_expert_review.csv` + `semantic_review_pairs.csv` | âœ… Done |
| 8 | Apply (no-op — all decisions were reject/keep_both) | — | âœ… No changes needed |

### Phase 13a — Content Expansion: OG-only Body Subcats âœ… Batch 1 complete

> **Goal:** Deep Search coverage for 8 body subcategories with 31 OG-only FAQs. **Batch 1** (5 zero-DS subcats) — 19 new entries imported. **Batch 2** (3 partial-DS subcats) deferred. See [PHASE13_BODY_DS_REPORT.md](reports/PHASE13_BODY_DS_REPORT.md).

| # | Task | Status |
|:-:|:-----|:------:|
| 1 | Research existing OG entries | âœ… Done |
| 2 | Create 5 Batch-1 prompts (inspection, transfer, extra, value, valuation) | âœ… Done |
| 3 | Create import script | âœ… Done |
| 4 | Quality-assess 10 Deep Search result files, pick best per subcategory | âœ… Done |
| 5 | Apply 19 new entries, rebuild FAISS, verify, hygiene audit | âœ… Done |
| 6 | Batch-2 prompts (rate, coverage, discount) | â¬œ Deferred |
| 7 | Documentation and commit | âœ… Done |

### Phase 13b — Master Damage Calculation Reference (Deep Search Batch) âœ… Complete

> **Goal:** 7 authoritative Deep Search entries harmonizing franchise rates, unified payout pipeline, and edge cases. See [PHASE13B_CALC_DS_REPORT.md](reports/PHASE13B_CALC_DS_REPORT.md).

| # | Task | Status |
|:-:|:-----|:------:|
| 1 | Create 7 Deep Search prompt files under scrape/prompts/calc/ | âœ… Done |
| 2 | Extend import script (import_body_deep_search.py) to support calc_* subcategories | âœ… Done |
| 3 | Run prompts through ChatGPT Deep Search | âœ… Done |
| 4 | Pool, clean citations, import 7 entries, rebuild FAISS, verify | âœ… Done |
| 5 | Update ROADMAP.md and reports | âœ… Done |

**Imported:** 7 entries (547 â†’ 554 FAQs). Subcategories: body_valuation (1), body_franchise (2), body_claim (1), body_value (1), body_discount (1), body_coverage (1).

### Phase 14 — Calculation Ontology & Bot âœ… Complete (v2.0.0)

> **Goal:** Machine-readable ontology + calculation bot with parameter extraction, validation, clarification, and calc-filtered KB fallback. See [PHASE14_CALC_ONTOLOGY_REPORT.md](reports/PHASE14_CALC_ONTOLOGY_REPORT.md).

| # | Task | Status |
|:-:|:-----|:------:|
| 1 | Create `data/analysis/calc_ontology.json` (7 scenarios, validation blocks) | âœ… Done |
| 2 | Create `src/calculator.py` (pure functions, 7 calc scenarios) | âœ… Done |
| 3 | Add `POST /calculate`, `/admin/reload-ontology`, `/health` calc status | âœ… Done |
| 4 | Extend `src/router.py` with `body_calc` + `injury_calc` intents | âœ… Done |
| 5 | Tests: `test_calculator.py` + `test_parameter_extractor.py` (41 tests) | âœ… Done |
| 6 | Documentation (report, ROADMAP, REPORT_INDEX) | âœ… Done |
| 7 | **Plan-vs-implementation verification** (scenario params, root lemmas, patterns, unit abbreviations) | âœ… Done |
| 8 | **v2 redesign:** coverage profiles, riders, pipeline, `calc_terms.json` | âœ… Done |
| 9 | **v2 tests:** rider interaction, sublimits, term lexicon (`test_calc_coverage.py`, 24 tests) | âœ… Done |
| 10 | **v2 audit:** plan verification, routing fixes, false-positive probes | âœ… Done |

**Endpoints:** `POST /calculate`, `POST /admin/reload-ontology`, extended `GET /health` (`calc_status`).
**Verification:** 65/65 tests pass — see [PHASE14_CALC_ONTOLOGY_REPORT.md Â§v2 audit](reports/PHASE14_CALC_ONTOLOGY_REPORT.md).
**Critique:** [PHASE14_CALC_COVERAGE_CRITIQUE.md](reports/PHASE14_CALC_COVERAGE_CRITIQUE.md) documents the coverage-blind v1 model and v2 fixes.

### Phase 14 Release — Server Deploy (v14.0.0 / v14.0.1) âœ… Done

> **Staged runbook:** [PHASE14_SERVER_DEPLOY_PLAN.md](PHASE14_SERVER_DEPLOY_PLAN.md)  
> **Release notes:** [RELEASE_v14.0.0.md](RELEASE_v14.0.0.md)  
> **Operator reference:** [DEPLOY.md](DEPLOY.md)

| Stage | Task | Status |
|:-----:|:-----|:------:|
| 0 | Prerequisites (Python 3.11+, SSH, data bundle) | âœ… Documented |
| 1 | `git checkout v14.0.1` | âœ… Tagged on GitHub |
| 2 | Transfer KB + FAISS + calc ontology (not in git) | âœ… `scripts/deploy/pack_data_bundle.*` |
| 3 | venv + `pip install -r requirements.txt` | âœ… Documented |
| 4 | `verify_invariants.py` + pytest | âœ… Documented |
| 5 | `start_api.sh` / systemd | âœ… Documented |
| 6 | Smoke tests (`/health`, `/ask`, `/calculate`) | âœ… Documented |
| 7 | Ongoing ops, rollback, KB maintenance | âœ… Documented |

**Data bundle required:** 9 Tier-0 files — see DEPLOY.md. Git pull alone does not update the running KB.

### Phase 14c — Interface stack (localhost-first) âœ… Done

> **Operator reference:** [DEPLOY.md Â§ Phase 14c](DEPLOY.md#phase-14c--interface-stack-localhost)

| # | Deliverable | Status |
|:-:|:------------|:------:|
| 1 | API bind `127.0.0.1:8000` + Caddy `:8080` | âœ… |
| 2 | Static RTL chat PWA (`static/chat/`) | âœ… |
| 3 | `POST /chat` BFF + `tests/test_chat.py` + smoke `phase_b_chat` | âœ… |
| 4 | Telegram bot `/opt/bots/bimeh-telegram/` + systemd | âœ… |

**Implementation report:** [`docs/reports/PHASE14C_INTERFACE_REPORT.md`](reports/PHASE14C_INTERFACE_REPORT.md) — full component verification, gap analysis, live test results.  
**Critique & remediations:** [`docs/reports/PHASE14C_INTERFACE_CRITIQUE.md`](reports/PHASE14C_INTERFACE_CRITIQUE.md) (F1–F25 findings).

### Interface testing

| Layer | Test type | Coverage | Status |
|:------|:----------|:---------|:------:|
| Unit | `tests/test_chat*.py` (19 tests) | FAQ, calc clarify, calc result, injury redirect, empty question, null handlers, timeout, branch meta, calc error, UI contract, HTTP E2E | Automated in pytest |
| Integration | `phase_b_chat` in `smoke_test.sh` | `/chat` calc_result via live API | Automated in smoke |
| Integration | `phase_a` in `smoke_test.sh` | Tier-0 artifact parity, Caddy proxy | Automated in smoke |
| E2E/manual | Browser via SSH tunnel | Full UI state machine, chip click flow, error handling | Manual (Phase C7 below) |
| Bot | `/opt/bots/bimeh-telegram/` imports | `api_client`, `formatters` import checks | Manual (needs TELEGRAM_BOT_TOKEN) |

### Future interface development

| Priority | Item | Effort | Notes |
|:--------:|:-----|:------:|:------|
| P0 | Caddy rate limiting (if going public) | Low | Requires `caddy` rate_limit module; fallback: FastAPI `slowapi` |
| P1 | Browser-based E2E test script for `/chat` UI states | 2–3 h | Playwright or simple `puppeteer` script testing all 7 UI states |
| P1 | UI test for Caddy SPA fallback (`try_files`) | 1 h | Assert `http://127.0.0.1:8080/unknown-path` returns `index.html` |
| P2 | `/chat` response time benchmark (P50/P95) | 1 h | Compare vs `/ask` baseline |
| P2 | `bimeh-telegram` bot smoke gate in `smoke_test.sh` | 1 h | Import check + version assertion (no live Telegram needed) |
| P2 | Chat UI accessibility audit (RTL, keyboard nav, screen reader) | 2 h | aria-labels, focus management, Persian screen reader test |
| P3 | PWA offline support (service worker for cached HTML/CSS/JS) | 1 d | Optional enhancement for mobile/SSH tunnel scenarios |
| P3 | Chat UI theme toggle (light/dark) | 1 d | CSS variables already structured for it |
| P3 | `/chat` response streaming (SSE or WebSocket) | 2–3 d | For long FAQ answers; requires server-side SSE support |

### Phase 14b — Container Hardening (Variant A) â¬œ Planned

> **Goal:** Dockerfile, docker-compose, API key middleware, rate limiting.  
> **Note:** Basic deploy (Stages 0–7) is complete in Phase 14 Release above.

| # | Task | Effort |
|:-:|:-----|:------:|
| 1 | Dockerfile + docker-compose for uvicorn | 2 days |
| 2 | API key middleware + rate limiting | 2 days |
| 3 | Health check hardening (startup probe, graceful shutdown) | 1 day |

### Phase 15 — Hybrid Retrieval (Phase 11d) â¬œ Planned

> **Goal:** Tag/subcategory boost on TF-IDF scores to improve search relevance, especially for branch queries.

| # | Task | Effort |
|:-:|:-----|:------:|
| 1 | Tag overlap re-ranking in `build_response()` | 3-4 days |
| 2 | A/B test set evaluation vs current FAISS-only | 2 days |
| 3 | Configurable boost weights via env var (optional) | 1 day |

### Phase 16 — Dense Embedding Migration (Variant C) â¬œ Deferred

> **Goal:** Evaluate and optionally migrate from TF-IDF to dense embeddings for improved semantic search. May be skipped if Phase 15 hybrid retrieval meets targets.

| # | Task | Effort |
|:-:|:-----|:------:|
| 1 | Evaluate cross-encoder vs bi-encoder for Persian insurance domain | 1 week |
| 2 | Generate embeddings, build dense FAISS index | 1 week |
| 3 | Hybrid dense-sparse fallback if embedding fails | 3 days |

### Phase 10 — Branch quality pass (ðŸŸ¡ exceptions documented)

> **Status:** 7 partial + 1 not_found documented with contact model validation. Branch contact Pydantic model created. API policy defined (return available data). See [PHASE10_BRANCH_QUALITY_PASS.md](reports/PHASE10_BRANCH_QUALITY_PASS.md).

| # | Task | Status |
|:-:|:-----|:------:|
| 1 | Run Deep Search quality pass for 8 branches | âœ… Prompt prepared + model validated |
| 2 | Define API policy for `partial` / `not_found` contacts | âœ… Return available data, no disclaimer |
| 3 | Add map â†” KB parity check to verify suite | âœ… Done (`verify_invariants.py`) |

---

### Phase 5d — Audit Cleanup (âœ… Complete — all items closed)

> **Status (2026-05-30):** 6 high-confidence misplaced entries relocated (Wave 2). 48 heuristic-only reviewed and confirmed correctly categorized (Phase 12). No ID dupes. 3 semantic pairs reviewed and confirmed keep_both. See [PHASE12_SME_TRIAGE_REPORT.md](reports/PHASE12_SME_TRIAGE_REPORT.md).

| Item | Status |
|:-----|:------:|
| Duplicate tombstones confirmed absent | âœ… |
| 6 high-confidence misplaced â†’ relocated (backup + FAISS rebuild) | âœ… |
| 48 heuristic-only misplaced â†’ reviewed, all correctly categorized | âœ… |
| Semantic near-dupe clusters (3 content pairs) â†’ reviewed, all keep_both | âœ… |
| Questionnaire gaps (63 rows) â†’ deferred to Phase 13 | ðŸ”· |

**A. âœ… Delete 3 confirmed duplicates** — already removed from active KB
| ID | Duplicate of | Topic |
|:---|:-------------|:------|
| body_addon_004 | deep_prompt07_011 | Ù¾ÙˆØ´Ø´ Ú©Ø´ÛŒØ¯Ù† Ù…ÛŒØ® (nail pull coverage) |
| body_theft_001 | deep_prompt04_004 | Ù¾ÛŒØ¯Ø§ Ø´Ø¯Ù† Ø®ÙˆØ¯Ø±Ùˆ Ù¾Ø³ Ø§Ø² Ø¯Ø±ÛŒØ§ÙØª Ø®Ø³Ø§Ø±Øª Ø³Ø±Ù‚Øª |
| body_basics_012 | deep_prompt04_001 | ØªÙØ§ÙˆØª Ø³Ø±Ù‚Øª Ø¯Ø±Ø¬Ø§ Ø¨Ø§ Ø³Ø±Ù‚Øª Ú©Ù„ÛŒ |

**B. âœ… Labels fixed** — 3 body_transfer entries set to body-sodour (commit 0067e35)

**C. ðŸ”· Expert review — misplaced Deep Search** (archive-first, not auto-relocated):
- **6 high-confidence** (category/body-keyword mismatch) — see `data/analysis/phase5d/misplaced_deep_search.json`
- **48 heuristic-only** (legacy roadmap rule) — experts confirm before any move
- Export: `data/exports/expert_review/PHASE5D_expert_review.csv`

**D. Review 12 OG-only subcategories (45 entries)** for Deep Search coverage:
| Subcategory | OG count | DS count |
|:------------|:--------:|:--------:|
| body_claim | 29 | 0 |
| body_coverage | 10 | 0 |
| body_issuance | 22 | 0 |
| body_rate | 5 | 0 |
| body_inspection | 3 | 0 |
| body_discount | 4 | 0 |
| body_valuation | 2 | 0 |
| body_value | 1 | 0 |
| body_online | 1 | 0 |
| body_extra | 1 | 0 |
| body_exclusions | 1 | 0 |
| body_transfer | 5 | 0 |

---

### Phase 10 — Branch Address Verification (Priority: ðŸ”´ HIGH) âœ… **Done**

> **Goal:** Fix systematically wrong branch data in the Asia Insurance map_contacts.json.
> **Status:** âœ… **Completed 2026-05-28** — Deep Research + JSON merge applied; 70/70 branches have map+KB contact; FAISS rebuilt (528Ã—300). See [PHASE10_BRANCH_MERGE_VERIFICATION.md](reports/PHASE10_BRANCH_MERGE_VERIFICATION.md).

**Problem:** 70 Asia Insurance branches in map_contacts.json have systematic errors:
- **74%** (52/70) had **no phone or address** at all
- Of the **18 with data**, **10 (77%) had wrong data** (wrong phone codes, wrong addresses)
- Errors followed **template/copy-paste patterns** (Tehran data pasted into non-Tehran branches)

**Results Summary:**
| Outcome | Count |
|:--------|:-----:|
| High confidence (2+ sources) | 12 |
| Medium confidence (1 source) | 28 |
| Low confidence | 8 |
| Still no data (NOT_FOUND) | 10 |
| **Total corrected** | **60** |

**Key Findings from Deep Research Verification (2026-05-24):**

| Branch | Code | Old (Wrong) Data | Verified Data | Status |
|:-------|:-----|:-----------------|:--------------|:-------|
| **Ù…Ø±Ø§ØºÙ‡** | 32034 | ðŸ“ž 021-36138770 (Tehran!) | ðŸ“ž **041-37248212** âœ… | âœ… **Corrected** |
| **Ù…ÛŒØ± Ø§ØµÙÙ‡Ø§Ù†** | 32101 | ðŸ“ž 061-53224372 (Abadan!) | ðŸ“ž **031-33240533** âœ… | âœ… **Corrected** |
| **ØªØ¨Ø±ÛŒØ² Ù…Ø±Ú©Ø²ÛŒ** | 32106 | ðŸ“ž 041-34458001 | ðŸ“ž 041-34458001 âœ… | âœ… **Confirmed correct** |
| **Ù…Ø¯Ù†ÛŒ Ù‡Ù…Ø¯Ø§Ù†** | 32014 | ðŸ“ž 08138255024 | ðŸ“ž 08138272274 (same code) | âš ï¸ **Address differs** |
| **Ù…Ø§Ú©Ùˆ** | 31103 | ðŸ“ž 021-55600703 (Tehran!) | â“ Not found on site | ðŸ” **Need more search** |
| **Ø¨Ø¬Ù†ÙˆØ±Ø¯** | 32035 | ðŸ“ž 021-66929857 (Tehran!) | â“ Not found on site | ðŸ” **Need more search** |
| **Ø®Ø±Ù… Ø¢Ø¨Ø§Ø¯** | 32026 | ðŸ“ž 051-44236590 (Mashhad!) | â“ Not found on site | ðŸ” **Need more search** |
| **Ù…Ø·Ù‡Ø±ÛŒ Ø§ØµÙÙ‡Ø§Ù†** | 32001 | ðŸ“ž 044-36451001 (Khoy!) | â“ Not found on site | ðŸ” **Need more search** |
| **Ø®Ø±Ù…Ø´Ù‡Ø±** | 32046 | ðŸ“ž 07142241651-3 (Shiraz!) | â“ Not found on site | ðŸ” **Need more search** |
| **Ø±Ø´Øª** | 32108 | ðŸ“ž 041-44235409 (Ahar!) | â“ Not found on site | ðŸ” **Need more search** |

**Phone Cross-Contamination Discovered:**
The wrong phone numbers in map_contacts actually belong to OTHER branches:
- **044-36451001** â†’ assigned to Ù…Ø·Ù‡Ø±ÛŒ (Ø§ØµÙÙ‡Ø§Ù†) but actually belongs to **Ø´Ø¹Ø¨Ù‡ Ø®ÙˆÛŒ** (Khoy, West Az.)
- **061-53224372** â†’ assigned to Ù…ÛŒØ± (Ø§ØµÙÙ‡Ø§Ù†) but actually belongs to **Ø´Ø¹Ø¨Ù‡ Ø¢Ø¨Ø§Ø¯Ø§Ù†** (Abadan, Khuzestan)
- **041-44235409** â†’ assigned to Ø±Ø´Øª (Ú¯ÛŒÙ„Ø§Ù†) but actually belongs to **Ø´Ø¹Ø¨Ù‡ Ø§Ù‡Ø±** (Ahar, East Az.)

**Implementation steps:**
1. âœ… Create survey plan (PHASE10_WEB_SURVEY_PLAN.md)
2. âœ… Survey Asia Insurance official site (Ù…Ø±Ø§Ú©Ø²-Ù¾Ø±Ø¯Ø§Ø®Øª-Ø®Ø³Ø§Ø±Øª page) — extracted first 10 entries
3. âœ… Deep Research verification of all 70 branches via multi-source cross-reference
4. âœ… Build verified dataset with frequency table
5. âœ… Update KB branch entries with corrected data (60 of 70 updated)
6. âœ… Rebuild FAISS index for 528 entries
7. âœ… Check for duplicates — 0 found
8. âœ… JSON merge filled 9/10 former NOT_FOUND via file52; **32026 Ø®Ø±Ù… Ø¢Ø¨Ø§Ø¯** remains `not_found` — manual verification

---

### Phase 10 — Real-World Inquiry Integration (Priority: ðŸŸ¡ MEDIUM) âœ… **Done**

> **Goal:** Map Asia Insurance customer service call drivers to new FAQ entries.
> Based on actual top contact reasons from the Asia Insurance service desk.
> **Status:** âœ… **Completed 2026-05-24** — 16 entries imported (deep_prompt11_001 to deep_prompt11_016)

**New subcategories created (6):**
| Code | Name (fa) | faq_type_label |
|:-----|:----------|:-----------------|
| third_cancellation | Ø§Ø¨Ø·Ø§Ù„ Ùˆ Ù„ØºÙˆ Ø¨ÛŒÙ…Ù‡â€ŒÙ†Ø§Ù…Ù‡ | sales-sodour |
| third_payment | Ù†Ø­ÙˆÙ‡ Ù¾Ø±Ø¯Ø§Ø®Øª Ùˆ Ø§Ù‚Ø³Ø§Ø· | sales-sodour |
| third_contracts_special | Ù‚Ø±Ø§Ø±Ø¯Ø§Ø¯Ù‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡ Ùˆ Ú¯Ø±ÙˆÙ‡ÛŒ | sales-sodour |
| third_system_inquiry | Ø§Ø³ØªØ¹Ù„Ø§Ù… Ø³ÛŒØ³ØªÙ…ÛŒ (Ø³Ø§Ù…Ø§Ù†Ù‡â€ŒÙ‡Ø§) | sales-sodour |
| third_contact_info | Ø§Ø·Ù„Ø§Ø¹Ø§Øª ØªÙ…Ø§Ø³ Ùˆ Ù¾ÛŒØ§Ù…Ú© | sales-sodour |
| third_policy_inquiry | Ø§Ø³ØªØ¹Ù„Ø§Ù… Ø´Ù…Ø§Ø±Ù‡ Ø¨ÛŒÙ…Ù‡â€ŒÙ†Ø§Ù…Ù‡ | sales-sodour |

**Topics to cover (11 items):**
| # | Topic | Subcategory |
|:-:|:------|:------------|
| 1 | Cancellation of third-party policy (buyer/seller mismatch, non-payment) | third_cancellation |
| 2 | Premium payment: cash collected vs. instalment registration | third_payment |
| 3 | Price discrepancy across insurers (Azki, Bimito vs. direct) | third_rate (extend) or new |
| 4 | Special contract quotes (manager cars, fleet contracts) | third_contracts_special |
| 5 | Stuck temporary proposals in online portal | third_online (extend) |
| 6 | Policy not visible in fuel card / tyre subsidy systems | third_system_inquiry |
| 7 | SMS not received — wrong agent mobile on policy | third_contact_info |
| 8 | Policy number lookup by national ID / engine-chassis | third_policy_inquiry |
| 9 | Discount transfer outside official rules / Article 6 | third_transfer (extend) |
| 10 | Discount transfer when tariff group changes (plate transfer) | third_transfer (extend) |
| 11 | Group third-party contracts and systemic conditions | third_contracts_special |

**Implementation steps:**
1. âœ… Create 6 new subcategory codes in KB schema + label map
2. âœ… Write ~15 Deep Search entries (deep_prompt11_*) using structured 7-component answer format
3. âœ… Cross-check against existing entries to avoid duplicates
4. âœ… Update scripts/imports/phase10_import_deep_prompt11.py
5. âœ… Run mini-audit before merging
6. âœ… Rebuild FAISS index (528 vectors x 300 dims)

---
## Event: 2026-07-01 – ðŸ—ºï¸ Five Development Variants

### Variant A — Production Hardening

**Goal:** Prepare the KB API for production deployment with enterprise-grade reliability, security, and observability.

| Phase | Timeline | Task | Effort | Dependencies |
|:-----:|:--------:|------|:------:|:------------:|
| **Short-term** | 1–2 weeks | Dockerise the application (Dockerfile, docker-compose.yml) | Low | — |
| | | Add API key authentication (header-based) | Low | — |
| | | Rate limiting (slowapi or middleware) | Low | — |
| | | Request/response logging to JSON (structured logging) | Low | Logging config |
| | | Startup KB â†” index consistency checks + `/health` degraded state | Low | Phase 11a |
| | | Sanitize 500 responses (no raw exception to client) | Low | Phase 11c |
| | | CORS allowlist via environment variable | Low | Phase 11c |
| **Mid-term** | 2–4 weeks | Set up reverse proxy (NGINX / Caddy with HTTPS) | Medium | Docker deployment |
| | | Health check endpoint with deep diagnostics (DB, index) | Low | — |
| | | Prometheus metrics (/metrics endpoint) | Medium | — |
| | | Graceful shutdown handling | Low | Docker |
| **Long-term** | 1–2 months | Kubernetes deployment (helm chart) | High | Docker image |
| | | Horizontal scaling (multiple replicas, shared index) | High | K8s |
| | | Blue-green deployment strategy | Medium | K8s |
| | | Penetration testing and security audit | Medium | Auth in place |

**Total estimated effort:** ~ 4–6 weeks  
**Risk:** Low — well-documented path

---

### Variant B — Content Expansion

**Goal:** Grow the knowledge base breadth and depth to cover more insurance domains and languages.

| Phase | Timeline | Task | Effort | Dependencies |
|:-----:|:--------:|------|:------:|:------------:|
| **Short-term** | 1–2 weeks | Add 50–100 new Q&As from recent chat logs | Medium | Data collection |
| | | Review and improve uncovered roots (Ù…ÛŒØªÙˆ, prediction gaps) | Low | Gap analysis |
| | | Tag review: standardise and extend tag hierarchy | Low | — |
| **Mid-term** | 2–6 weeks | Add lifecycle insurance domain (life_*) | High | Subject matter expert |
| | | Add health insurance domain (health_*) | High | SME |
| | | Create answer quality rubric and review all 528 answers | Medium | Team agreement |
| | | User feedback collection (thumbs up/down per answer) | Low | API endpoint |
| **Long-term** | 1–3 months | English FAQ translations (bilingual KB) | High | Content team |
| | | Arabic FAQ translations | High | Translator |
| | | Speech-to-text integration for voice queries | High | ASR system |
| | | Chatbot conversation flow export (Rasa / Dialogflow) | Medium | — |

**Total estimated effort:** ~ 2–4 months (parallelisable)  
**Risk:** Medium — depends on content availability and SMEs

---

### Variant C — LLM Integration

**Goal:** Enhance answer quality and coverage using large language models, while keeping the FAISS fallback for cost control.

| Phase | Timeline | Task | Effort | Dependencies |
|:-----:|:--------:|------|:------:|:------------:|
| **Short-term** | 1–2 weeks | Hybrid search: TF-IDF + tag/subcategory boost (before full embeddings) | Medium | Phase 11d |
| | | Replace TF-IDF with sentence-transformers embeddings | Medium | GPU or quantised model |
| | | Rebuild FAISS index with 768-dim embeddings | Low | New embeddings |
| | | A/B test: compare recall@k vs TF-IDF baseline | Low | Test queries |
| **Mid-term** | 2–4 weeks | Add cross-encoder reranker (e.g. cross-encoder/ms-marco) | Medium | GPU |
| | | Hybrid search: TF-IDF + dense + reranker ensemble | High | Both indexes |
| | | Implement LLM answer generation for out-of-scope questions | High | LLM API key |
| | | Add "answer confidence" score (LLM self-evaluation) | Medium | LLM integration |
| **Long-term** | 1–3 months | Fine-tune a Persian LLM on the KB for domain-specific Q&A | Very High | GPU cluster, dataset |
| | | Citation-aware generation (answers cite KB source) | High | RAG pipeline |
| | | Multi-turn conversation support (chat history context) | High | Session store |
| | | Human-in-the-loop: LLM drafts reviewed by agents | Medium | Review UI |

**Total estimated effort:** ~ 2–4 months  
**Risk:** High — depends on GPU availability, LLM costs, and evaluation metrics

---

### Variant D — Cost & Performance Optimisation

**Goal:** Reduce operational costs and improve response latency while maintaining or improving quality.

| Phase | Timeline | Task | Effort | Dependencies |
|:-----:|:--------:|------|:------:|:------------:|
| **Short-term** | 1 week | Add in-memory cache for frequent queries (LRU with TTL) | Low | — |
| | | Promote similarity recall tests to pytest (â‰¥ 23/24) | Medium | Phase 11b |
| | | Profile and optimise tokenizer (compile regexes) | Low | — |
| | | Reduce vector dimension by PCA (300 â†’ 128) | Low | Rebuild index |
| | | Enable gzip compression on API responses | Low | — |
| **Mid-term** | 2–3 weeks | Quantise FAISS index (IVF + PQ for faster search) | Medium | Rebuild index |
| | | Batch API requests (process multiple queries at once) | Medium | Client changes |
| | | Background index refresh (hot-reload new answers) | Medium | — |
| | | Response streaming for long answers | Medium | — |
| **Long-term** | 1–2 months | Serverless deployment (AWS Lambda / Cloud Run) | High | Containerised app |
| | | Cold-start optimisation (warm pool / snapstart) | Medium | Serverless |
| | | Edge caching (CDN for top 50 answers) | Medium | CDN service |
| | | Cost dashboard: track per-query cost in $ | Low | Metrics |

**Total estimated effort:** ~ 4–6 weeks  
**Risk:** Low — mostly incremental improvements with measurable ROI

---

### Variant E — Content Organisation & Enhancement

**Goal:** Close ontological gaps, enrich template answers, reorganise subcategories for better coverage and user journey flow.

| Stage | Timeline | Task | Effort | Dependencies | Status |
|:-----:|:--------:|------|:------:|:------------:|:------:|
| **1** | 1 week | Body basics & online purchase — Body_issuance created, body_basics eliminated, 10 moved, 10 redistributed | Low | Phase 6 ontology | âœ… **Done** |
| **2** | 1 week | Body discount, expiry & inquiry — Expanded via Phase 8 H2 (13 new body topics) | Medium | Stage 1 | âœ… **Done** |
| **3** | 2 weeks | Third-party enrichment — **202/202 (100%) enriched.** 74 templates across 4 batches. | Medium | Phase 6 | âœ… **Done ðŸŽ‰** |
| **4** | 0.5 week | Cross-domain bundle — Combined purchase + coordinated claim entries | Low | Stages 2–3 | â¬œ **Planned** |
| **5** | 0.5 week | Injury review — 19 rewritten (fixing 2 critical errors) + 16 new via Phase 8 H3 | Medium | Stage 4 | âœ… **Done** |
| **6** | 1 week | Body & Injury enrichment — H1 (4 shortâ†‘), H2 (13 new), H3 (19 rewrite+16 new), H4 (ontology+FAISS) | Medium | Stages 1–5 | âœ… **Done** |
| **7** | 1 week | Asia migration — 97 entries (27 product + 70 branch), 9 cross-links, company-neutrality | Medium | Stage 6 | âœ… **Done** |
| **8** | 0.5 week | Phase 5d cleanup — Delete 3 dupes âœ…; relocate **6** high-confidence misplaced DS (survey); review 12 OG-only subcats | Low | — | ðŸŸ¡ **Partial** (dupes done; relocation deferred â†’ Phase 11b) |
| **9** | 0.5 week | Phase 10 — Branch Address Verification — Cross-source validation of 70 Asia branches | Medium | Stage 7 | âœ… **Done** |
| **10** | 1–2 weeks | Phase 10 — Real-World Inquiry Integration — 11 call-driver topics â†’ 6 new subcats + ~15 DS entries | Medium | Stage 8 | âœ… **Done** |

**Remaining Variant E work:** Stage 4 (cross-domain bundle) + Stage 8 relocation backlog  
**Risk:** Low — data-driven, no external dependencies

---
## Event: 2026-05-01 – ðŸ“Š Comparison Summary

| Dimension | A — Production | B — Content | C — LLM | D — Cost/Perf | **E — Organisation** |
|-----------|:-------------:|:-----------:|:-------:|:-------------:|:-------------------:|
| **Time to value** | 2 weeks | 2 weeks | 2–4 weeks | 1 week | **Stage 4 + 5d backlog** |
| **Effort** | Medium | High | Very High | Low–Medium | **Low** |
| **Risk** | Low | Medium | High | Low | **Lowest** |
| **Cost** | Low | Medium | High (GPU/API) | Low | **None** |
| **User impact** | Reliability | Breadth | Quality | Speed | **Structure + Coverage** |
| **Dependencies** | DevOps | SMEs | LLM provider | — | **None** |

**Recommended order (2026-05-29, post-survey):**
1. **ðŸ”´ Phase 11a P0** — Restore merge script, startup checks, commit tree, archive deprecated rebuilds
2. **ðŸŸ¡ Phase 10 quality pass** — 8 branch contacts (`deep_search_branches_prompt_v2.json`)
3. **ðŸŸ¡ Phase 11b P1** — Unify tokenizer, similarity in CI, JSON Schema, relocate 6 misplaced DS
4. **ðŸŸ¡ Phase 5d** — SME review CSV; 384 similarity pairs; 63 questionnaire gaps
5. **ðŸŸ¡ Phase 11c P2** — Intent router, structured contacts, `min_score`, contact confidence policy
6. **â¬œ Variant E Stage 4** — Combined purchase + coordinated claim entries
7. **â¬œ Variant D** — Cache, PCA, gzip
8. **â¬œ Variant A** — Docker, auth, metrics (after 11a/11c)
9. **â¬œ Variant B** — Content expansion
10. **â¬œ Variant C / Phase 11d** — Hybrid retrieval, then embeddings if needed

---
## Event: 2026-07-01 – ðŸ§© Outstanding Work Items (Prioritised

> **Synced with** [14040307survay.md](reports/14040307survay.md) decision log. Use survey table to Accept / Defer / Reject.

### P0 — Engineering debt (Phase 11a)

| Priority | Item | Effort |
|:--------:|:-----|:------:|
| ðŸ”´ | Restore `scripts/imports/merge_phase10_branch_json.py` | Low |
| ðŸ”´ | Startup KB â†” FAISS consistency assertions | Low |
| ðŸ”´ | Commit uncommitted reorg + Phase 10 artifacts | Low |
| ðŸ”´ | Document fresh-clone bootstrap (rebuild when data gitignored) | Low |
| ðŸ”´ | Archive `phase10_rebuild_faiss.py` + `phase10_clean_branches_rebuild_faiss.py` | Low |

### P1 — Quality gates (Phase 11b)

| Priority | Item | Effort |
|:--------:|:-----|:------:|
| ðŸŸ¡ | Unify FAISS rebuild tokenizer â†’ `src.nlp_utils.tokenize_persian` | Low |
| ðŸŸ¡ | Promote similarity tests to pytest (target â‰¥ 23/24) | Medium |
| ðŸŸ¡ | JSON Schema validation on KB edits | Medium |
| ðŸŸ¡ | CI: `test_no_duplicate_faq_ids` | Low |
| ðŸŸ¡ | `index_info.json` with KB hash on rebuild | Low |
| ðŸŸ¡ | Relocate **6** high-confidence misplaced Deep Search entries | Medium |
| ðŸŸ¡ | Export Phase 9 **29** FAQ suggestions to `phase9_backlog.json` | Low |

### P2 — Retrieval & API (Phase 11c)

| Priority | Item | Effort |
|:--------:|:-----|:------:|
| ðŸŸ¡ | Intent router (branch vs policy FAQ) | Medium |
| ðŸŸ¡ | Structured `contact` on branch entries | Medium |
| ðŸŸ¡ | Expose `min_score` on `/ask` or fix README | Low |
| ðŸŸ¡ | API policy for `partial` / `not_found` branch contacts | Medium |
| ðŸŸ¡ | Map â†” KB parity check (70 codes) in verify suite | Low |
| ðŸŸ¡ | Pydantic validation on Deep Search branch JSON | Medium |
| ðŸŸ¡ | Scrape JSON smoke tests | Low |
| ðŸŸ¡ | Clarify company neutrality vs Asia branch scope | Low |

### Content & legacy backlog

| Priority | Item | Phase | Effort |
|:--------:|:-----|:-----:|:------:|
| âœ… | Delete 3 duplicates — **closed** | 5d | — |
| ðŸŸ¡ | SME review: **6** high-confidence + **48** heuristic misplaced DS (CSV) | 5d | 1–2 hr |
| ðŸŸ¡ | Review **384** similarity pairs (`similarity_clusters.json`) | 5d | 1 hr |
| ðŸŸ¡ | Mark **63** questionnaire rows vs insured.ir / centinsur.ir | — | 2 hrs |
| ðŸŸ¡ | Phase 10: 7 **partial** + **32026** Ø®Ø±Ù…â€ŒØ¢Ø¨Ø§Ø¯ quality pass | 10 | 1 hr |
| ðŸŸ¡ | OG-only body subcats (12) — Deep Search gap fill | 5d | 1 hr |
| ðŸŸ¡ | Resolve uncovered root "Ù…ÛŒØªÙˆ" | — | 15 min |
| ðŸŸ¡ | Sync REPORT_INDEX with ROADMAP; fix stale Phase 10 doc checkboxes | docs | 30 min |
| ðŸŸ¡ | Update or archive stale `verify_phase4.py` / `verify_phase5.py` (231 FAQ metrics) | verify | 30 min |
| â¬œ | Combined purchase (Ø¨Ø¯Ù†Ù‡ + Ø«Ø§Ù„Ø«) + coordinated claim entries | E-4 | 1 hr |
| â¬œ | Docker + API key + rate limiting | A | 1 week |
| â¬œ | Hybrid TF-IDF + tag boost | 11d / C | Medium |
| â¬œ | In-memory cache + PCA dimension reduction | D | 1 week |

---
## Event: 2026-05-01 – ðŸ”— Related Documents

| Document | Location | Purpose |
|:---------|:---------|:--------|
| Master Report Index | docs/reports/REPORT_INDEX.md | Full deliverable inventory |
| Executive Summary | docs/EXECUTIVE_SUMMARY.md | Stakeholder one-pager |
| Phase 8 Body & Injury Plan | docs/reports/PHASE8_BODY_INJURY_PLAN.md | Completed H1-H4 details |
| Asia Migration Plan | docs/reports/PHASE8_ASIA_MIGRATION_PLAN.md | Asia import & company-neutrality |
| Phase 9 Test & Ontology | docs/reports/PHASE9_TEST_AND_ONTOLOGY_REPORT.md | Duplicate checks, ontology model |
| Phase 7 Enrichment Plan | docs/reports/PHASE7_ENRICHMENT_PLAN.md | Ø«Ø§Ù„Ø« Ù…Ø§Ù„ÛŒ 100% enrichment |
| Phase 6 Content Review | docs/reports/THIRDPARTY_CONTENT_REVIEW_PLAN.md | NLP diagnosis & merges |
| **Phase 10 Web Survey Plan** | **docs/reports/PHASE10_WEB_SURVEY_PLAN.md** | **Branch address verification strategy** |
| **Phase 10 Branch Verification** | **docs/reports/PHASE10_BRANCH_VERIFICATION_FINAL.md** | **Verification results & corrected data** |
| **Phase 10 Deep Search Prompt** | **docs/reports/PHASE10_DEEP_SEARCH_BRANCH_VERIFICATION_PROMPT.md** | **Deep Research prompt for multi-source branch verification** |
| **Phase 10 Branch merge report** | **docs/reports/PHASE10_BRANCH_MERGE_REPORT.md** | **JSON merge QA summary** |
| **Phase 10 Branch merge verification** | **docs/reports/PHASE10_BRANCH_MERGE_VERIFICATION.md** | **Gap check, pytest, FAISS verification (2026-05-28)** |
| **Phase 10 Prompt 11 Import** | **docs/reports/PHASE10_IMPORT_PROMPT11.md** | **16 new entries from call-driver topics** |
| **Project survey (criticism workbook)** | **docs/reports/14040307survay.md** | **1404/03/07 survey — practical + conceptual critics; drives Phase 11** |
| **Phase 11b Verify Automation** | **docs/reports/PHASE11B_VERIFY_AUTOMATION.md** | **verify_invariants, pytest guards, index_info.json** |
| **Phase 11 FAQ Strength** | **docs/reports/PHASE11_FAQ_STRENGTH_REPORT.md** | **Recall fix, 6 misplaced relocated, deferred items** |
| **Phase 11c Retrieval report** | **docs/reports/PHASE11C_RETRIEVAL_REPORT.md** | **Intent router, min_score, CORS from env** |
| **Phase 10 Branch quality pass** | **docs/reports/PHASE10_BRANCH_QUALITY_PASS.md** | **8 exceptions, branch contact model, API policy** |
| **Phase 12 SME Triage** | **docs/reports/PHASE12_SME_TRIAGE_REPORT.md** | **48 misplaced reviewed (REJECT), 3 semantic pairs reviewed (KEEP_BOTH)** |
| **Phase 13 Body DS Expansion** | **docs/reports/PHASE13_BODY_DS_REPORT.md** | **Batch 1 complete: 19 entries imported, OG-only subcats 8â†’0** |
| **Phase 13b Calc DS Reference** | **docs/reports/PHASE13B_CALC_DS_REPORT.md** | **7 calculation reference entries imported; KB 547â†’554** |
| **Phase 14 Calc Ontology & Bot** | **docs/reports/PHASE14_CALC_ONTOLOGY_REPORT.md** | **Ontology v2 + calculator bot, POST /calculate, 65 tests** |
| **Phase 14 Server Deploy Plan** | **docs/PHASE14_SERVER_DEPLOY_PLAN.md** | **Staged runbook Stages 0–7 for Linux server** |
| **Phase 14 Release Notes** | **docs/RELEASE_v14.0.0.md** | **v14.0.0 summary, git vs data bundle, upgrade path** |
| **Deploy & Server Operations** | **docs/DEPLOY.md** | **systemd, API usage, rollback, data bundle tiers** |
| **Phase 14c Interface Report** | **docs/reports/PHASE14C_INTERFACE_REPORT.md** | **Component verification, gap analysis, live test results** |

---

*Last updated: 2026-06-06 (Phase 14c interface stack — implementation report, future development tracks, testing plan)*
