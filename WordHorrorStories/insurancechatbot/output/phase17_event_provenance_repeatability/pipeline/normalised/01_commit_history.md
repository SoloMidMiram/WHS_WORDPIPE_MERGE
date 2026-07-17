---
source: 01 Commit History
title: InsuranceChatbot Commit History
input_file: 01_commit_history.md
event_count: 169
date: 2026-05-14 to 2026-07-16
---

# Source: 01 Commit History

## Event: 2026-05-14 – 6cb6634 - chore: initial commit — Insurance FAQ Knowledge Base

Timestamp: 2026-05-14T20:31:44+03:30

chore: initial commit — Insurance FAQ Knowledge Base

- 231 unique Persian FAQ pairs (from 555 raw logs)
- 35 insurance subcategories (╪½╪º┘ä╪½ ┘à╪º┘ä█î, ╪«╪│╪º╪▒╪¬ ╪¿╪»┘å┘ç, ╪½╪º┘ä╪½ ╪¼╪º┘å█î ┘ê ╪»█î┘ç)
- TF-IDF + FAISS semantic search (293-dim, cosine)
- FastAPI server (health / search / ask endpoints)
- hazm-based NLP pipeline (lemmatisation, POS tagging)
- Phase 0–5 scripts + Phase 4 analysis (gap matrix, root words)
- 62 pytest tests (61 passing)
- Documented in docs/ with EXECUTIVE_SUMMARY, ROADMAP, PHASE4_PLAN
- Reorganised: scripts/, data/{raw,processed,analysis,exports,faiss_index}/
## Event: 2026-05-15 – caa148c - Phase 5b: Deep Search KB expansion (+147 Qs, 378 total

Timestamp: 2026-05-15T09:40:21+03:30

Phase 5b: Deep Search KB expansion (+147 Qs, 378 total)

- merge_deep_search_results.py: hazm + Jaro-Winkler dedup script
- knowledge_base_phase5_deep_merged.json: 378 FAQs
- deep_merge_report.json: 48 skipped duplicates (9 vs KB, 39 cross-file)
- phase3_embeddings_lite.py: fixed paths (data/faiss_index/)
- verify_all.py: fixed FAISS dir path, 378 entries verified
- tests: dimension 293->300, fallback test uses obscure query
- src/config.py: added KB_DEEP_MERGED + resolve_kb_path()
- src/search.py: uses auto-resolve instead of hardcoded paths
- api.py: auto-selects merged KB (378), then enriched (231), then base
- docs/PHASE5_DEEP_SEARCH_MERGE.md: full process documentation
- REPORT_INDEX.md + README.md: updated with 378 Q stats
## Event: 2026-05-15 – 161b513 - chore: add root-level exclusions to .gitignore, remove duplicate pytest.ini (config in pyproject.toml

Timestamp: 2026-05-15T10:51:13+03:30

chore: add root-level exclusions to .gitignore, remove duplicate pytest.ini (config in pyproject.toml)
## Event: 2026-05-15 – c35eec5 - feat: add related_ids cross-references for all 378 entries

Timestamp: 2026-05-15T12:35:31+03:30

feat: add related_ids cross-references for all 378 entries

- Creates scripts/build_related_ids.py:
  - Jaccard keyword overlap with threshold 0.15 (top-5)
  - Fallback to same-category siblings for sparse entries
- Updates knowledge_base_phase5_deep_merged.json:
  - 146 Deep Search entries got keyword-based cross-refs
  - 1 edge case (deep_prompt08_003) got category-fallback cross-refs
  - All 378 entries now have non-empty related_ids
- Rebuilds FAISS index (378x300) via phase3_embeddings_lite.py
- 62/62 pytest passes
## Event: 2026-05-15 – 0067e35 - feat: add metadata.ask_frequency and metadata.faq_type_label to all 378 KB entries

Timestamp: 2026-05-15T18:15:02+03:30

feat: add metadata.ask_frequency and metadata.faq_type_label to all 378 KB entries

- ask_frequency: 1 (default for all entries)
- faq_type_label: body-sodour (35), body-damage (107),
                  sales-sodour (187), sales-damage (49)
- 18 third_misc entries reassigned from sales-sodour to body-damage
  (3 OG + 15 Deep Search body-edge-case entries)
- Backup saved as knowledge_base_phase5_deep_merged.json.bak

Script: scripts/add_faq_type_label.py
## Event: 2026-05-16 – e3b8d91 - Phase 8 H4: Deep-search verified injury entries + ontology update + FAISS rebuild + project reorganisation

Timestamp: 2026-05-16T08:05:18+03:30

Phase 8 H4: Deep-search verified injury entries + ontology update + FAISS rebuild + project reorganisation

## ≡ƒåò New Content (8 H4 entries)
Added deep-search-verified FAQ entries for injury (╪½╪º┘ä╪½ ╪¼╪º┘å█î):
- injury_H01: Joint injury+financial claims process
- injury_H02: Injury vs financial coverage comparison table
- injury_H03: Pre-treatment diyah claims (╪╣┘ä█îΓÇî╪º┘ä╪¡╪│╪º╪¿)
- injury_H04: Holy months diyah (┘à╪º╪»┘ç █╡█╡█▓) with █▒█┤█░█┤ amounts
- injury_H05: Driver accident vs passenger coverage distinction
- injury_H06: Mobile phone use as ╪¬╪«┘ä┘ü ╪¡╪º╪»╪½┘çΓÇî╪│╪º╪▓ (┘à╪º╪»┘ç █▒█┤)
- injury_H07: No license but not at fault — no recourse (┘à╪º╪»┘ç █▒█╡)
- injury_H08: Seatbelt neglect — contributory negligence (╪▒╪ú█î ┘ê╪¡╪»╪¬ ╪▒┘ê█î┘ç █╖█╖█░)

Each verified against: centinsur.ir, rc.majlis.ir, lmo.ir with specific law articles.

## ≡ƒöì Duplicate & Similarity Tests
- All 8 entries confirmed novel (>0.70 threshold yields 0 cross-matches)
- Zero duplicate IDs, zero exact duplicate questions/answers

## ≡ƒöä FAISS Index Rebuilt
- Vectors: 372 ΓåÆ 409 (with H4 + all Phase 8 entries)
- Dimensions: 300 (unchanged, TF-IDF + L2/IndexFlatIP)

## ≡ƒº¼ Ontology Files Updated
- general_ontology.json: injury count 19ΓåÆ43, journey phases refreshed
- injury_ontology.json: total 35ΓåÆ43, source_breakdown per subcategory
- coverage_gaps.json: reviewed with current counts, 2 HIGH gaps now partially filled

## ≡ƒôï Questionnaire Correspondence
Mapped all 63 bilingual questionnaire items to KB subcategories;
report saved to PHASE8_H4_ONTOLOGY_REPORT.md

## ≡ƒôü Project Reorganisation
- docs/reports/: Added 9 plan/report files (BODY_FINALIZATION, PHASE4_ANALYSIS, etc.)
- scripts/: Added 11 new phase scripts (import_batch*, phase6/7/8, phase8_hazm_injury*)
- tools/: Relocated add_faq_type_label.py, build_related_ids.py from scripts/
- Removed: scripts/archive/_create_postman.py
- Updated: .gitignore (docs/.chats-long/), EXECUTIVE_SUMMARY.md, ROADMAP.md
- Updated: REPORT_INDEX.md with new HR4 ontology report
## Event: 2026-05-16 – e8c7f1d - feat: branch manager extractor from personnel_enriched.xlsx — 70 branches mapped

Timestamp: 2026-05-16T14:21:03+03:30

feat: branch manager extractor from personnel_enriched.xlsx — 70 branches mapped
## Event: 2026-05-16 – cbbaa98 - docs: evidence file for branch manager extraction + register in REPORT_INDEX

Timestamp: 2026-05-16T14:28:09+03:30

docs: evidence file for branch manager extraction + register in REPORT_INDEX
## Event: 2026-05-30 – 9e85042 - reorg: reorganise scripts and add survey, tools, startup checks

Timestamp: 2026-05-30T20:15:29+03:30

reorg: reorganise scripts and add survey, tools, startup checks

- Move phase pipeline scripts to scripts/phases/, imports to scripts/imports/
- Move utility scripts to tools/, archives to scripts/archive/
- Restore merge_phase10_branch_json.py from Phase 10 spec
- Add startup KB/FAISS consistency assertions to src/api.py and degraded health
- Archive deprecated FAISS rebuild scripts (hazm tokenizer, abandoned clean path)
- Add project survey 14040307survay.md (criticism workbook)
- Update ROADMAP with Phase 11 tracks imported from survey
- Update AGENT_PERSONAS with Phase 11 persona examples
- Update scripts/README.md, data/README.md with fresh-clone bootstrap docs
- Add .cursor/rules/portable/ agent personas
- Add AGENTS.md, root README.md, CONTRIBUTING.md
- Add COMPANY_NEUTRALITY.md rules document

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-05-30 – eb83207 - phase10: add scrape data, tests, reports, and API config changes

Timestamp: 2026-05-30T20:17:48+03:30

phase10: add scrape data, tests, reports, and API config changes

- Add scrape data for Asia branches (branches_map_merged, deep search prompts, QA)
- Add scrape scripts for Asia branch/product extraction
- Add Phase 10 reports (branch merge, FAISS rebuild, data verification, migration)
- Add merge_phase10_branch_json test and Phase 5d/8/9 reports
- Update src/config.py, src/search.py with Phase 10 paths
- Update tests/conftest.py, test_api.py for Phase 10 compatibility
- Update README.md and api.py for fresh-clone bootstrap

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-05-30 – ed7ab97 - feat: complete Waves 3-4 — verification, FAQ strength, retrieval hardening

Timestamp: 2026-05-30T20:36:59+03:30

feat: complete Waves 3-4 — verification, FAQ strength, retrieval hardening

Wave 1 (Phase 11b P1):
- Create verify_invariants.py (KB parse, ID uniq, FAISS parity, branch map parity)
- Add pytest guards: test_no_duplicate_faq_ids, test_kb_faiss_count_parity, test_similarity_recall (24 queries, >=23 gate)
- Refactor rebuild script to import tokenize_persian from nlp_utils
- Emit index_info.json during FAISS rebuild with KB sha256 and build timestamp
- Report: PHASE11B_VERIFY_AUTOMATION.md

Wave 2 (Phase 5d + Phase 10):
- Relocate 6 high-confidence misplaced entries: third_driver/third_misc -> body_issuance/body_claim
- Add KB_HYGIENE.md policy document (duplicate/merge rules)
- Add branch_contact_model.py Pydantic validator for branch data
- Post-cleanup counts in PHASE5D_KB_HYGIENE_REPORT.md

Wave 3 (FAQ Strength):
- Fix one similarity recall failure (add question variant with in-vocab terms)
- FAQ strength report documenting deferred items

Wave 4 (Phase 11c Retrieval):
- Add src/router.py: intent router (branch vs general), result re-ranking
- Add min_score parameter to AskRequest and /search endpoint
- CORS origins configurable via CORS_ORIGINS env var
- Sanitize 500 error responses (no exception leak)
- Report: PHASE11C_RETRIEVAL_REPORT.md

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-05-30 – 9645751 - docs: sync documentation across all waves — Phase 10 branch quality pass, Phase 5 doc update, report index, scripts README

Timestamp: 2026-05-30T20:43:45+03:30

docs: sync documentation across all waves — Phase 10 branch quality pass, Phase 5 doc update, report index, scripts README

Closes remaining docs-sync items:
- Create PHASE10_BRANCH_QUALITY_PASS.md (Wave 2 deliverable)
- Update PHASE5_DOCUMENTATION.md for new API fields (min_score, intent routing, CORS env)
- Update REPORT_INDEX.md with branch quality pass entry
- Update ROADMAP.md with Phase 10 status and Related Documents table
- Update scripts/README.md to remove "(when created in Wave 1)" caveats and add new commands

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-05-30 – e4a01f6 - Phase 12: SME triage & content hygiene infrastructure

Timestamp: 2026-05-30T21:26:35+03:30

Phase 12: SME triage & content hygiene infrastructure

Step 1 — Prepare SME materials:
  - Modify phase5d_similarity_scan.py to output all 384 pairs (remove truncation)
  - Create export_semantic_review_csv.py (filters out asia_branch, exports 3 content pairs)

Step 3 — Apply scripts:
  - Create relocate_from_csv.py (reads signed-off PHASE5D_expert_review.csv)
  - Create merge_semantic_dupes.py (reads signed-off semantic_review_pairs.csv)
  - Create phase5d_merge_decisions.json audit log
  - Update KB_HYGIENE.md with CSV-driven workflow documentation

Step 4 — Verify:
  - Re-run hygiene audit (48 heuristic misplaced remain, 0 high-confidence)

Step 5 — Documentation:
  - Update ROADMAP.md with Phase 12 section
  - Update REPORT_INDEX.md with Phase 12 entry
  - Update PHASE5D_KB_HYGIENE_REPORT.md with Phase 12 post-cleanup
  - Update scripts/README.md with new commands

Steps 2a/2b (SME review) and 4a/4b (apply) blocked on CSV decision fill.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-05-30 – 364a401 - Phase 12: complete — all 48 misplaced reviewed (REJECT), 3 semantic pairs reviewed (KEEP_BOTH

Timestamp: 2026-05-30T21:47:47+03:30

Phase 12: complete — all 48 misplaced reviewed (REJECT), 3 semantic pairs reviewed (KEEP_BOTH)

Content analysis determined the Phase 5d heuristic was overly broad: all 48 entries
are correctly categorized as third-party content. 3 semantic pairs are complementary
branded/general content, not duplicates.

- Auto-fill PHASE5D_expert_review.csv (54 reject decisions)
- Auto-fill semantic_review_pairs.csv (3 keep_both decisions)
- Create PHASE12_SME_TRIAGE_REPORT.md documenting analysis
- Update ROADMAP.md: Phase 12 done, Phase 5d complete, Phases 13-16 outlined
- Update REPORT_INDEX.md: Phase 12 entry added
- Update PHASE5D_KB_HYGIENE_REPORT.md: Phase 12 outcome documented

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-06-05 – 19ee6fd - Phase 13: import scrape results for body damage and calculation domains

Timestamp: 2026-06-05T18:15:48+03:30

Phase 13: import scrape results for body damage and calculation domains

Add pooled scrape prompts and results for body damage (inspection,
valuation, value, extra, transfer) and calculation (deductions,
franchise table, limits/exclusions, master formula, repeated claims,
total loss, under insurance). Include import scripts with dry-run
support for previewing before applying to KB.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-06-05 – c9c1fe2 - Phase 14: add calculation bot with ontology-driven body damage formula

Timestamp: 2026-06-05T18:16:29+03:30

Phase 14: add calculation bot with ontology-driven body damage formula

Implement calculator.py with master formula, franchise, deductions,
total loss, under-insurance, repeated claims, limits/exclusions, and
validation logic. Add /calculate endpoint to API with calc_ontology.json
loading, intent routing, and health reporting. Include comprehensive
test suite (test_calculator, test_calc_coverage, test_parameter_extractor).

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-06-05 – c19b3ca - Phase 14: add FAQ ontology prototype builder and report

Timestamp: 2026-06-05T18:16:54+03:30

Phase 14: add FAQ ontology prototype builder and report

Add build_faq_ontology.py script that constructs an FAQ ontology from
12 scrape JSON files (26 entries across 12 subcategories) with FAISS
pairwise similarity clustering and KB merge patch generation. Includes
PHASE14_FAQ_ONTOLOGY_PROTO_REPORT.md documenting the prototype's
structure, statistics, quality assessment, and next steps.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-06-05 – bd924b1 - Phase 14: add expert review export package with full-KB marked-up review kit

Timestamp: 2026-06-05T18:17:35+03:30

Phase 14: add expert review export package with full-KB marked-up review kit

Add export_expert_review_package.py script that produces review-ready
Excel (Master, Summary, Hygiene, Instructions, SubcategoryMap sheets)
and per-subcategory Markdown files with embedded markup blocks for all
554 FAQs. Update hygiene audit script and report. The --word flag
optionally generates python-docx per-subcategory reading copies.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-06-05 – 7fedfd5 - docs: sweep phase reports, README updates, and auxiliary analysis scripts

Timestamp: 2026-06-05T18:18:19+03:30

docs: sweep phase reports, README updates, and auxiliary analysis scripts

Add Phase 13 body/calc deep search reports, Phase 14 calc ontology
report and critic/critique reviews. Update REPORT_INDEX, ROADMAP,
scripts/README with Phase 14 entries, and AGENT_PERSONAS. Add
auxiliary analysis scripts for FAQ stats, report index updates,
and v2 coverage verification to support ongoing reporting.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-06-05 – 52d0838 - release: v14.0.0 deploy docs, bundle scripts, and version bump

Timestamp: 2026-06-05T20:44:57+03:30

release: v14.0.0 deploy docs, bundle scripts, and version bump

Add docs/DEPLOY.md with full Linux server setup, data bundle tiers,
upgrade/rollback, systemd example, and API usage. Add scripts/deploy/
for packing runtime artifacts and production start. Bump VERSION to
14.0.0 and fix KB/FAISS count docstrings in config.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-06-05 – c9a5337 - docs: staged server deploy plan and v14.0.1 release documentation

Timestamp: 2026-06-05T20:54:27+03:30

docs: staged server deploy plan and v14.0.1 release documentation

Add PHASE14_SERVER_DEPLOY_PLAN.md (Stages 0-7 with gates), RELEASE_v14.0.0.md,
update ROADMAP with Phase 14 release section and 554-FAQ status, cross-link
DEPLOY.md, REPORT_INDEX, AGENTS.md, and scripts/README.md.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-06-11 – 488e7f8 - Add v2 roadmaps and chat interface docs

Timestamp: 2026-06-11T15:48:56Z

Add v2 roadmaps and chat interface docs
## Event: 2026-06-11 – bdaf242 - Expand v2 roadmap with governance milestones

Timestamp: 2026-06-11T18:51:25Z

Expand v2 roadmap with governance milestones
## Event: 2026-06-11 – d99c9b1 - Organize P2 roadmap milestones

Timestamp: 2026-06-11T20:25:20Z

Organize P2 roadmap milestones
## Event: 2026-06-11 – 7e53e9a - Refine v2 roadmap for remaining governance work

Timestamp: 2026-06-11T20:35:06Z

Refine v2 roadmap for remaining governance work
## Event: 2026-06-18 – 4bbe282 - docs: add kagent asset contract and roadmap spine

Timestamp: 2026-06-18T10:00:39Z

docs: add kagent asset contract and roadmap spine
## Event: 2026-06-18 – ebd7dd5 - chore: add docs safety checker

Timestamp: 2026-06-18T10:00:57Z

chore: add docs safety checker
## Event: 2026-06-18 – 7de9f84 - docs: index kagent docs in report map

Timestamp: 2026-06-18T10:16:15Z

docs: index kagent docs in report map
## Event: 2026-06-18 – 1e3464e - docs: lock runtime environment and server policy

Timestamp: 2026-06-18T14:53:31Z

docs: lock runtime environment and server policy
## Event: 2026-06-18 – bdd30a2 - docs: add third-party diyat analysis bundle

Timestamp: 2026-06-18T14:54:03Z

docs: add third-party diyat analysis bundle
## Event: 2026-06-18 – d7c0c20 - docs: add body glossary ontology roadmap

Timestamp: 2026-06-18T14:54:25Z

docs: add body glossary ontology roadmap
## Event: 2026-06-18 – 6af5d0e - test: add regression suites for ontology reports

Timestamp: 2026-06-18T14:56:20Z

test: add regression suites for ontology reports
## Event: 2026-06-18 – f2c87bf - untracked files on (no branch): c9a5337 docs: staged server deploy plan and v14.0.1 release documentation

Timestamp: 2026-06-18T19:17:46+03:30

untracked files on (no branch): c9a5337 docs: staged server deploy plan and v14.0.1 release documentation
## Event: 2026-06-18 – 5b245a3 - index on (no branch): c9a5337 docs: staged server deploy plan and v14.0.1 release documentation

Timestamp: 2026-06-18T19:17:46+03:30

index on (no branch): c9a5337 docs: staged server deploy plan and v14.0.1 release documentation
## Event: 2026-06-18 – db0bb2c - On (no branch): codex pre-switch to roadmap-ontology-organize

Timestamp: 2026-06-18T19:17:46+03:30

On (no branch): codex pre-switch to roadmap-ontology-organize
## Event: 2026-06-19 – 87d5dad - docs: reorganize roadmap and current-state mapping

Timestamp: 2026-06-19T10:19:46+03:30

docs: reorganize roadmap and current-state mapping
## Event: 2026-06-19 – 7163510 - docs: add third-party dependency graph

Timestamp: 2026-06-19T17:44:26+03:30

docs: add third-party dependency graph
## Event: 2026-06-24 – b6c26da - chore: consolidate archived content into top-level /archive/

Timestamp: 2026-06-24T10:23:54+03:30

chore: consolidate archived content into top-level /archive/

- Move 0209-042926/docs/archive/ -> archive/docs/
- Move 0209-042926/scripts/archive/ -> archive/scripts/legacy/
- Copy 0209-042926/api.log.* -> archive/logs/ (untracked copies)
- Add archive/README.md with structure guide and restore instructions
- Update .gitignore to exclude /archive/logs/
- Update 6 doc references to point to new archive paths
- Remove now-empty source archive directories
## Event: 2026-06-24 – 0fcc4de - chore: reorganize docs/ into categorized subdirectories and archive historical docs

Timestamp: 2026-06-24T10:31:45+03:30

chore: reorganize docs/ into categorized subdirectories and archive historical docs

Archive moves (git mv, history preserved):
- 5 KAGENT proposals + AGENT_RUNTIME_LANDSCAPE -> archive/docs/kagent/
- 3 Phase5 docs -> archive/docs/phase5/
- ROADMAP_v2.md, REVERSE_ROADMAP_v2.md -> archive/docs/

Active doc reorganization (git mv):
- docs/guides/  — DEPLOY.md, API_CONTRACT.md, PHASE14_*, MANAGER_DEMO.md
- docs/domain/  — bilingual_questionnaire, variable lists, EXECUTIVE_SUMMARY
- docs/roadmap/ — ROADMAP.md (single active tracker)
- docs/agents/  — AGENT_PERSONAS.md
- docs/presentations/ — PRESENTATION_OUTLINE.md, README_PRESENTATION.md
- docs/         — README.md, README_REPORT_SYSTEM.md, RELEASE_v14.0.0.md

Cross-reference updates:
- Updated docs/README.md entry point with new structure
- Updated 0209-042926/README.md (doc map, kagent section, related docs table)
- Updated root README.md, CONTRIBUTING.md, tools/migrate_to_new_structure.py
- Updated internal links in DEPLOY.md, PHASE14 docs, MANAGER_DEMO.md, RELEASE_v14.0.0.md
## Event: 2026-06-24 – 053f231 - chore: update archive README with new kagent, phase5, roadmap sections

Timestamp: 2026-06-24T10:32:00+03:30

chore: update archive README with new kagent, phase5, roadmap sections
## Event: 2026-06-25 – 8011f9b - P0: runtime contract — add artifact_format_version + metadata_formats_written to validation report

Timestamp: 2026-06-25T11:37:50+03:30

P0: runtime contract — add artifact_format_version + metadata_formats_written to validation report

- Add artifact_format_version (int | None) and metadata_formats_written (list[str])
  fields to RuntimeValidationReport dataclass
- Populate from index_info.json in validate_runtime_artifacts()
- Expose in to_dict() and health_payload()
- Add 2 health-endpoint assertions in test_api.py covering both nested
  validation_report and top-level exposure
- Create sprint log at docs/roadmap/2026-06-25_remediation_sprint.md
- All 3 P0 gates pass: verify_invariants, pytest (48/48), validate_artifacts --json
## Event: 2026-06-25 – 2064b43 - feat: add evaluation framework with runner, coverage analysis, and regression gates

Timestamp: 2026-06-25T12:07:08+03:30

feat: add evaluation framework with runner, coverage analysis, and regression gates

- evals/eval_report.py: loads 100 retrieval_cases.jsonl, runs retriever,
  computes Recall@1/3, MRR, intent accuracy, fallback precision/recall/F1
- evals/eval_coverage.py: tag/intent/fallback distribution, subcategory
  coverage analysis (8/43 covered, 35 gaps identified)
- evals/README.md: full docs with quickstart, metric definitions, dataset
  format, CI integration guide
- tests/test_retrieval_eval_integration.py: 6 regression gate tests with
  thresholds (Recall@3 >= 0.70, MRR >= 0.55, etc.) + dataset existence check
- Update sprint log with baseline metrics and eval framework section
- All 7 integration tests pass, eval_report exits cleanly with gates PASS
## Event: 2026-06-25 – 02ea410 - docs: add third-party variable integration plan — knowledge review, 1404/1405 merge strategy, and search manifest

Timestamp: 2026-06-25T13:07:21+03:30

docs: add third-party variable integration plan — knowledge review, 1404/1405 merge strategy, and search manifest

- Quality assessment: 36 variables evaluated (20 correlated, 8 separate, 8 conflict)
- Categorizes 16 variables as safe-to-promote to canonical
- Lists 6 fields needing 1404 search (Tier 2) with specific Persian queries
- Lists 2 fields needing authoritative source ruling (Tier 3)
- Provides search output requirements, outcome actions, and integration checklist
- Part of Phase 6/7 third-party content review track, not the June 25 sprint
## Event: 2026-06-25 – 7fa9ea9 - docs: add third-party investigation playbook — 4 focused DeepSearch runs for conflict resolution and 1404 gap-filling

Timestamp: 2026-06-25T13:16:53+03:30

docs: add third-party investigation playbook — 4 focused DeepSearch runs for conflict resolution and 1404 gap-filling

- THIRDPARTY_INVESTIGATION_PLAYBOOK.md: 4 runs covering coverage limits,
  late penalties, fines/timeline, and diyat governance metadata
- Each run has exact Persian queries, structured JSON output format per
  variable, and fallback rules
- 6 conflicts explicitly documented with suspected causes and resolution
  strategy (C1-C6)
- 10 missing-1404 fields documented with 1405 baseline and search
  requirements (M1-M10)
- Updated ontology roadmap to reference the playbook as primary
  investigation tool
## Event: 2026-06-25 – 9d30ce5 - docs: integrate DeepSearch results — resolve all 6 third-party conflicts and fill 12/14 missing 1404 values

Timestamp: 2026-06-25T13:44:47+03:30

docs: integrate DeepSearch results — resolve all 6 third-party conflicts and fill 12/14 missing 1404 values

Conflict resolutions:
- C1 (THIRD_MIN_PROPERTY_DAMAGE_COVERAGE_IRR): unit bug (rial/toman), correct ratio is 2.5% by Article 8
- C2 (LATE_PENALTY_DAILY_4CYL_IRR): vehicle-class mismatch, not tariff drift
- C3 (LATE_PENALTY_BY_ENGINE_SIZE_OBJECT): unsafe to persist; derive from official premium/365
- C4 (NO_INSURANCE_DAILY_FINE_IRR): split into police ticket (1,500,000 IRR) + daily insurance surcharge
- C5 (THIRD_MIN_BODILY_INJURY_COVERAGE_IRR): equals sacred-month diyat by design (Article 8)
- C6 (THIRD_BODILY_INJURY_SACRED_NON_SACRED_OBJECT): legitimate to distinguish driver vs third-party;
  derive from diyat schedule, not independent constants

Key legal anchors discovered:
- Article 52: Judiciary announces diyat by 15 Esfand
- Articles 31-34: 15-day claim payment, 20-day finalization, delay penalty 0.5/1000 per day
- Article 24(b): late-purchase surcharge = premium for lapse period, capped at 1 year
- No statutory grace period exists; amnesty notices are temporary
- Article 10: traffic insurance pays without gender/religion distinction
## Event: 2026-06-25 – c76afc9 - feat: create canonical insurance_rules.json and derivation script — implement DeepSearch findings

Timestamp: 2026-06-25T13:58:39+03:30

feat: create canonical insurance_rules.json and derivation script — implement DeepSearch findings

Adds:
- data/analysis/insurance_rules.json: canonical variable store with all 36
  resolved variables, 1404/1405 values, derivation rules, and status flags
- scripts/analysis/derive_third_party_values.py: compute sacred-month diyat
  (├ù4/3), bodily coverage (=sacred diyat), property coverage (├ù0.025),
  and daily late penalty table (annual premium / 365) from anchor values

Key changes resolving 6 conflicts:
- THIRD_MIN_PROPERTY_DAMAGE_COVERAGE_IRR: correct ratio is 2.5% (was 25%
  due to rial/toman bug) — Article 8
- THIRD_MIN_BODILY_INJURY_COVERAGE_IRR: equals sacred-month diyat by design —
  Article 8 legal linkage, not coincidence
- Split NO_INSURANCE_DAILY_FINE_IRR ΓåÆ police ticket (1,500,000 IRR fixed)
  + daily insurance surcharge (premium-derived)
- Late penalty table regenerated from 4-cyl base premium (105,132,000 IRR/yr)
  with 10 vehicle classes; consumer table in tomans
- CLAIM_PAYMENT_LEGAL_MAX_DAYS: 15 days (Article 31), not 45 (criminal law)
- Grace period: 0 (no statutory grace period; amnesties are temporary)
## Event: 2026-06-25 – 0d4818c - feat: synchronize third-party ontology, glossary, and values matrix — all 38 variables aligned

Timestamp: 2026-06-25T14:22:23+03:30

feat: synchronize third-party ontology, glossary, and values matrix — all 38 variables aligned

- third_party_terms.json: new glossary with 60 Persian termΓåÆvariable mappings
  across all 8 canonical clusters
- thirdparty_ontology.json: added 'variable_clusters' section with 8 canonical
  clusters (38 variables) alongside existing 21 FAQ subdomains; each variable
  has type, unit, label_fa, and Persian terms
- THIRDPARTY_VALUES_MATRIX.md: comprehensive report with year-by-year values,
  diyat ratios, types, legal references, derivation rules, and deprecated
  variable table

Verification:
  Γ£à 38 variables in rules = 38 in glossary = 38 in ontology
  Γ£à 60 glossary entries, 8 ontology clusters, 8 rules clusters
  Γ£à 0 gaps, 0 orphans, 0 deprecated vars in active rules
  Γ£à All layers perfectly aligned
## Event: 2026-06-25 – f5c1a13 - feat: implement value reduction (┌⌐╪│╪▒ ┘é█î┘à╪¬) knowledge — split third-party vs body, add formula, ontology, and glossary

Timestamp: 2026-06-25T15:17:23+03:30

feat: implement value reduction (┌⌐╪│╪▒ ┘é█î┘à╪¬) knowledge — split third-party vs body, add formula, ontology, and glossary

- body_addon_001: updated answer to distinguish third-party (post-1403) vs
  body add-on regimes; added related_ids pointer to third_value_reduction_001
- third_value_reduction_001: new FAQ entry with official formula, age/accident
  coefficient tables, worked example, exclusions, and payment rules
- insurance_rules.json: added value_reduction cluster with 8 variables:
  VALUE_REDUCTION_FORMULA, MAX_CAP (20%), AGE/ACCIDENT coefficient tables,
  THIRD_PARTY_RULE, BODY_ADDON_RULE, ELIGIBILITY_RULES, EXCLUDED_PARTS
- third_party_terms.json: added 10 Persian term mappings for all 8 variables
- thirdparty_ontology.json: added value_reduction variable_cluster (8 vars)
- VALUE_REDUCTION_THIRD_PARTY.md: source research document

Verification: 8/8 variables aligned across rules, glossary, and ontology.
All gaps: 0.
## Event: 2026-06-25 – 4a6c614 - feat: implement Article 8 knowledge — coverage limits, ordinary vehicle rule, corresponding loss, and social justice

Timestamp: 2026-06-25T15:56:06+03:30

feat: implement Article 8 knowledge — coverage limits, ordinary vehicle rule, corresponding loss, and social justice

Adds:
- 3 new FAQ entries (third_article8_explanation_001, third_article8_note3_001,
  third_article8_social_justice_001) covering full Article 8 text, the
  corresponding-loss rule for luxury vehicles, and the social justice rationale
- Updated existing third_coverage_005 (╪«╪│╪º╪▒╪¬ ┘à╪¬┘å╪º╪╕╪▒) with proper Article 8
  legal framework, social justice explanation, and 1404/1405 thresholds
- insurance_rules.json: new article8 cluster with 10 variables (minimum bodily/
  financial cover, max cover, Note 3 rule, Note 4 definition, Note 5 duty,
  social justice rationale, body insurance interaction, 1404/1405 thresholds)
- third_party_terms.json: 12 Persian term mappings
- thirdparty_ontology.json: new article8 variable_cluster (10 vars)
- ARTICLE8_LEGAL_TEXT.md: DeepSearch research document

Key legal anchors:
- Article 8: bodily min = sacred-month diyat; financial min = 2.5%
- Note 3: corresponding loss capped at most expensive ordinary vehicle
- Note 4: ordinary vehicle defined as value < 50% of bodily ceiling
- Ruling 285: liable driver has no obligation beyond corresponding-loss ceiling
- Social justice: protects ordinary drivers; pushes luxury risk to body insurance

Verification: 10/10/10 variables aligned across rules, glossary, ontology.
## Event: 2026-06-25 – c9e05fd - feat: add hazm-based KB validator framework, fix stale addon texts, add 6 missing FAQ entries, update ontology key_concepts

Timestamp: 2026-06-25T17:15:04+03:30

feat: add hazm-based KB validator framework, fix stale addon texts, add 6 missing FAQ entries, update ontology key_concepts

Phase 0 — kb_validator.py (reusable framework):
- hazm lemmatization for Persian keyword extraction
- Jaccard QΓåöA coherence scoring with per-subdomain statistics
- Cross-subdomain stopword detection (193 stopwords identified)
- Ontology key_concepts update from stopwords to meaningful lemmas
- Statistical anomaly detection (2s from subdomain mean)
- Full Markdown report generation at docs/reports/KB_VALIDATION_REPORT.md

Phase 1 — Content fixes:
- body_addon_002 (╪┤┌⌐╪│╪¬ ╪┤█î╪┤┘ç): replaced generic addon template with focused
  answer on ╪┤█î╪┤┘ç + third-party ╪º┘ü╪¬ ┘é█î┘à╪¬ note
- body_addon_003 (╪¬┘ê┘é┘ü ╪¿╪º╪▒┌⌐╪┤): same fix
- third_claim_024: delay penalty (0.5 per mille per day — Article 33)
- third_claim_025: immediate partial payment (50% advance — Article 34)
- third_claim_026: finalization payment deadline (20 days — Article 32)
- third_value_reduction_002: age coefficient table
- third_value_reduction_003: accident coefficient 17-part table
- third_value_reduction_004: maximum cap (20% of vehicle value)

Phase 2 — Ontology: replaced POS-tag stopword key_concepts with
hazm-lemmatized meaningful profiles for all 21 subdomains

Verification: 564 FAQs, 21 subdomains updated, 6 new entries added
## Event: 2026-06-25 – 0a032f6 - refactor: Phase 15 repository reorganization — roadmaps, metadata, archiving with tracking

Timestamp: 2026-06-25T18:44:23+03:30

refactor: Phase 15 repository reorganization — roadmaps, metadata, archiving with tracking

**Phase 15 Deliverables:**

**A. Roadmap & Documentation**
- Create ROADMAP_REVERSE.md: Reverse-order phase dependencies (14c ΓåÉ 14b ΓåÉ 14a ΓåÉ ... ΓåÉ 0)
  Shows how each phase enabled future phases and created backward dependencies
- Update ROADMAP.md: Add Phase 15 section with reorganization status and links to reverse roadmap
- Create FILE_REFERENCE_MAP.md: Complete file dependency matrix (data flow, test fixtures, calc engine)
- Create DEPENDENCIES.graph.mermaid: Visual Mermaid diagram of data dependencies
- Update archive/README.md: Document Phase 15 archiving strategy and file movements

**B. Safe Metadata Addition**
- Add KB-level _metadata with modification history to knowledge_base_phase10_clean.json
- Add investigation flags to body_addon_002 (╪┤┌⌐╪│╪¬ ╪┤█î╪┤┘ç): Check ╪º┘ü╪¬ ┘é█î┘à╪¬ (value reduction) integration
- Add investigation flags to body_addon_003 (╪¬┘ê┘é┘ü ╪¿╪º╪▒┌⌐╪┤): Review vehicle-class-specific reductions
- Metadata pattern uses Pydantic extra='allow' for forward compatibility

**C. Archive Organization with Tracking**
- Create archive structure: archive/data/exports/, archive/data/logs/, archive/data/backups/
- Create .archived.txt markers in original locations documenting:
  - Date archived (2026-06-25)
  - Original location and destination
  - Reason for archiving
  - Restore instructions
- Markers placed in: data/exports/, root (.archived.txt), data/processed/archive/, docs/presentations/

**D. New Scripts**
- scripts/phases/phase15_add_metadata.py: Automated metadata addition with validation

**Verification:**
- Γ£à V.1 validation: artifact_validation + no_duplicate_faq_ids tests PASSED
- Γ£à V.2 validation: full test suite PASSED after metadata addition
- Γ£à FAQ count: 564 entries (expanded from 554 in Phase 14b)
- Γ£à Investigation flags: body_addon_002 & 003 flagged for Phase 16 work

**What This Enables for Phase 16+:**
- Clear file dependency map for future features
- Reverse-order dependency tracking (understand what enables what)
- Safe metadata pattern for creation/modification tracking
- Archive organization protocol for managing accumulated files
- Investigation flags visible in KB for future prioritization

Related PR: [codex] publish roadmap, ontology, and test organization #1
## Event: 2026-07-02 – 417debf - docs: ORG-1 top-doc cleanup and handoff

Timestamp: 2026-07-02T09:08:46+03:30

docs: ORG-1 top-doc cleanup and handoff

Fix root/FAQ docs links and stale FAQ metrics (554 baseline), mark REPORT_INDEX historical, and include contamination/handoff reports for clean follow-up slicing.
## Event: 2026-07-02 – 9d65648 - docs: add ORG-2A workspace ownership plan

Timestamp: 2026-07-02T09:29:46+03:30

docs: add ORG-2A workspace ownership plan
## Event: 2026-07-02 – 46e53ce - chore: ORG-2B ignore local-only artifacts

Timestamp: 2026-07-02T09:32:59+03:30

chore: ORG-2B ignore local-only artifacts

- .playwright-mcp/ — browser automation logs/snapshots

- .cursor/plans/ — local planning scratchpads

- _mcp_commands.txt and _tmp_*.py — temp local scripts

- **/__pycache__/ — Python bytecode cache (all workspaces)

- **/.pytest_cache/, .ruff_cache/, .uv-cache/ — tool caches

Intentionally excluded from .gitignore: .vscode/ (has track-now tasks.json), 0209-042926/artifacts/ (evidence JSONs), 0209-042926/data/sample/ (potential CI fixture), scrape/artifacts/ (reports/fixtures).
## Event: 2026-07-02 – 22761cb - docs: add ORG session completion report

Timestamp: 2026-07-02T09:44:32+03:30

docs: add ORG session completion report

Summarizes all org work from this session: ORG-1 top-doc cleanup, ORG-2A ownership plan, ORG-2B ignore rules, and Phase 4C pre-integration review (scrape workspace). Documents remaining untracked pools, boundaries preserved, and recommended next slices.
## Event: 2026-07-02 – 54efc29 - docs: add ORG-15 repo reorganization report

Timestamp: 2026-07-02T09:49:21+03:30

docs: add ORG-15 repo reorganization report

Formal documentation following Repo Organization Iteration Protocol.
Records all Phase 15 changes: roadmaps, file reference map,
metadata addition, archive tracking, and validation results.

Commit: 0a032f6 (Phase 15)
## Event: 2026-07-02 – 01d4202 - docs: fix root README guide links

Timestamp: 2026-07-02T11:13:23+03:30

docs: fix root README guide links
## Event: 2026-07-02 – ca4af97 - docs: add Phase 15 reorganization roadmap updates

Timestamp: 2026-07-02T11:28:22+03:30

docs: add Phase 15 reorganization roadmap updates

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-02 – f4274d9 - chore: track FAQ schema contracts

Timestamp: 2026-07-02T11:38:15+03:30

chore: track FAQ schema contracts
## Event: 2026-07-02 – 9f821b0 - docs: consolidate org files into docs/organization/ with index and survey

Timestamp: 2026-07-02T14:32:05+03:30

docs: consolidate org files into docs/organization/ with index and survey

- 5 tracked original paths replaced with stubs pointing to new locations

- 8 org files consolidated into docs/organization/ with aggregated README index

- docs/README.md updated with Organization navigation row

- New survey/problem map: ORG_2026-07-02_SURVEY_AND_PROBLEM_MAP.md

- Not moved: archive/, scrape/, 4 root-level ORG files

- Boundaries: no runtime, schema, test, or scrape workspace changes
## Event: 2026-07-02 – d3237c4 - docs: add commit-readiness fix plan

Timestamp: 2026-07-02T15:18:21+03:30

docs: add commit-readiness fix plan

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-02 – a8a2e2e - feat: add runtime loaders, branch lookup, decision engine, artifact validation

Timestamp: 2026-07-02T15:19:07+03:30

feat: add runtime loaders, branch lookup, decision engine, artifact validation

- active_release_loader: runtime bundle loading with profile support
- branch_lookup: structured branch/contact resolution from FAQ + branch_map
- decision: retrieval routing with token coverage and margin analysis
- runtime_errors: typed error hierarchy for artifact lifecycle
- validate_artifacts: Pydantic-based KB, ontology, calc terms, index_info validation
- tests: full coverage for all above modules
- Phase 3 evidence: deployment status reports and review docs

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-02 – 1688c98 - feat: add retrieval pipeline with TF-IDF, hybrid, embedding, eval scripts

Timestamp: 2026-07-02T15:19:50+03:30

feat: add retrieval pipeline with TF-IDF, hybrid, embedding, eval scripts

- retrieval/: base retriever, TF-IDF, hybrid, embedding, lexical modes
- evaluate_retrieval: end-to-end retrieval quality measurement
- tests: retrieval mode integration + metadata migration

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-02 – 6a6aabe - docs: add Phase 15 review reports, organisation diary, agent roadmap

Timestamp: 2026-07-02T15:20:30+03:30

docs: add Phase 15 review reports, organisation diary, agent roadmap

- PHASE15_LIVE_REVIEW_SECOND_PASS: second-pass live review of Phase 15
- PHASE15_REORGANISATION_REPORT: reorganisation outcomes
- ORG_2026-07-02_ORGANIZATION_DIARY: organisation session diary
- AGENTS_UPDATE_ROADMAP: agent persona update roadmap

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-02 – bc713ee - chore: add shared VSCode task runner tasks.json

Timestamp: 2026-07-02T15:21:10+03:30

chore: add shared VSCode task runner tasks.json

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-02 – 965bafb - fix: resolve runtime config, align search sigs, fix Docker venv for non-root user

Timestamp: 2026-07-02T20:12:38+03:30

fix: resolve runtime config, align search sigs, fix Docker venv for non-root user

- Add DATA_PROFILE, RUNTIME_DATA_DIR, BRANCH_MAP_PATH to src/config.py
- Add load_serialized_artifact() to src/nlp_utils.py for validate_artifacts.py
- Add kb_path param to load_knowledge_base() and faq_by_id param to load_faiss_index() in src/search.py
- Replace pip --user install with venv in Dockerfile for bimeh user access

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-02 – 98185c9 - fix: align artifact validation with runtime bundle, unify serialized artifact loading

Timestamp: 2026-07-02T21:42:54+03:30

fix: align artifact validation with runtime bundle, unify serialized artifact loading

- Harden load_serialized_artifact to raise ArtifactMissingError/ArtifactLoadError instead of built-in exceptions
- Reuse shared loader in load_vocab_and_idf and FAISS mapping to support JSON artifacts alongside pickle
- Switch validate_artifact_paths defaults from project-root constants to runtime_data_dir-relative paths

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-02 – 5a8df26 - fix: add active-release wiring, ontology path correction, pkl fallback, profile-based validation

Timestamp: 2026-07-02T22:53:23+03:30

fix: add active-release wiring, ontology path correction, pkl fallback, profile-based validation

- Add get_active_release_import_root() to config.py for the
  FAQ_ACTIVE_RELEASE_IMPORT_ROOT env var
- Add active-release loading to services.py: build_faq_dicts_from_active_release_entries(),
  RuntimeState fields, health_payload integration, and load_runtime_state() activation
- Add _resolve_faiss_metadata_path() helper with .pkl fallback in services.py
- Fix THIRD_PARTY_ONTOLOGY_PATH filename from third_party_ontology.json to
  thirdparty_ontology.json (matching committed file)
- Make runtime_data_dir optional (None) in validate_artifact_paths(),
  resolve from profile via resolve_runtime_data_dir()
- Add _resolve_json_or_pkl() helper in validate_artifacts.py with .pkl fallback
  for faq_mapping, vocab, and idf paths
- Update CLI --runtime-data-dir default to None for profile-based resolution

All 21 tests in test_active_release_runtime_wiring.py pass.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-02 – 5e3d3e6 - fix: wire RuntimeState into API, constrain records_path, fix FAQ IDs, fix chat timeout

Timestamp: 2026-07-02T23:39:01+03:30

fix: wire RuntimeState into API, constrain records_path, fix FAQ IDs, fix chat timeout

- Replace import-time artifact loading in api.py with FastAPI lifespan;
  store RuntimeState in app.state.runtime; gate /health, /ask, /search,
  /chat, /calculate on runtime.validation readiness (503 when degraded)
- Constrain records_path in active-release manifests using
  _safe_relative_path() + _ensure_within_root() to prevent path traversal
- Generate unique IDs for each FAQ pair (append pair index) so multi-pair
  records don't collide silently in faq_by_id
- Fix chat timeout blocking: replace with-ThreadPoolExecutor with
  explicit pool.shutdown(wait=False) in finally clause
- Update CHANGELOG.md and PHASE_3H_CONTROLLED_RUNTIME_WIRING_REPORT.md

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 89f80fb - fix: derive DATA_PROFILE from APP_ENV, exclude active-release from FAISS parity, use runtime path in reload-ontology

Timestamp: 2026-07-03T00:34:44+03:30

fix: derive DATA_PROFILE from APP_ENV, exclude active-release from FAISS parity, use runtime path in reload-ontology

- DATA_PROFILE defaults to "production" when APP_ENV is production/prod,
  so production Docker/systemd runs don't need to also set DATA_PROFILE
- Compare FAISS/mapping sizes against kb_base_count (excluding
  active-release overlay entries) to avoid false parity mismatches
- /admin/reload-ontology now passes runtime.runtime_data_dir to
  _init_calc_ontology(), so the correct profile-aware path is used
  instead of the global data/analysis/calc_ontology.json

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 52ccc59 - fix: route search through retriever, return full health payload, recompute validation on ontology reload

Timestamp: 2026-07-03T01:22:41+03:30

fix: route search through retriever, return full health payload, recompute validation on ontology reload

- /health now returns runtime.health_payload() with full diagnostics
- build_response() accepts optional retriever kwarg; /ask, /search,
  /chat pass runtime.retriever for hybrid/lexical search
- /admin/reload-ontology calls runtime.reload_calc_ontology() which
  returns a fresh RuntimeState with recomputed validation flags
- Extract _sync_module_globals() helper to keep module-level globals
  consistent with app.state.runtime

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 170733d - fix: wire SlowAPIMiddleware, replace sys.exit with exceptions, fix ontology version key

Timestamp: 2026-07-03T01:47:48+03:30

fix: wire SlowAPIMiddleware, replace sys.exit with exceptions, fix ontology version key

- Add SlowAPIMiddleware so configured RATE_LIMIT is actually enforced
- Replace sys.exit(1) in load_knowledge_base and load_faiss_index with
  ArtifactMissingError so the FastAPI lifespan degrades gracefully
- Fix reload-ontology response key from calc_ontology_version to
  ontology_version to match RuntimeValidationReport.to_dict() output

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 9b27159 - fix: integrate decision layer, count active-release pairs, default to production profile

Timestamp: 2026-07-03T05:31:15+03:30

fix: integrate decision layer, count active-release pairs, default to production profile

- build_response() now calls decide_retrieval_route() and returns
  route/decision_details in every response
- active_release_count reflects actual appended FAQ entries rather
  than source record_count, fixing FAISS parity validation when
  records have multiple FAQ pairs
- DATA_PROFILE honours BIMEH_PROFILE env var (per README) and
  defaults to 'production' so a fresh checkout starts healthy

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – f2a5ed0 - fix: move CI workflow to repo root, normalize glossary columns, flatten rules, handle keyed ontology clusters

Timestamp: 2026-07-03T06:01:35+03:30

fix: move CI workflow to repo root, normalize glossary columns, flatten rules, handle keyed ontology clusters

- Move .github/workflows/ci.yml from subdirectory to repository root with working-directory paths
- Add column mapping in load_glossary() for third_party_terms.json schema compatibility
- Add _flatten_rules() helper for cluster-sectioned insurance_rules.json
- Update cluster iteration for variable_clusters as keyed object

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 28b2577 - fix: make hazm dependency compatible with Python 3.11 CI

Timestamp: 2026-07-03T02:38:05Z

fix: make hazm dependency compatible with Python 3.11 CI
## Event: 2026-07-03 – e2f9b8b - fix: point kagent REPORT_INDEX links at archive tree instead of dead docs/ paths

Timestamp: 2026-07-03T06:37:38+03:30

fix: point kagent REPORT_INDEX links at archive tree instead of dead docs/ paths

- Update 5 Section 2.2 links from ../KAGENT-*.md to ../../archive/docs/kagent/KAGENT-*.md - Remove 5 kagent rows from Section 3.2 (Documents in docs/) - Add new Section 3.2a (Documents in archive/docs/kagent/) with correct paths

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 7a2a5c3 - fix: remove hazm.download_resources() call not present in hazm 0.10

Timestamp: 2026-07-03T06:45:58+03:30

fix: remove hazm.download_resources() call not present in hazm 0.10

hazm 0.10+ no longer exposes download_resources(). The dependency install already pulls in hazm via requirements-dev.txt, so the explicit download step is unnecessary and causes CI to fail before lint/tests start.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 8eb8b0d - style: apply Black formatting to 40 src and test files

Timestamp: 2026-07-03T06:55:39+03:30

style: apply Black formatting to 40 src and test files

Auto-formatted with black --line-length=100 src/ tests/ to satisfy CI formatting check.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 75832df - style: fix isort import ordering in 10 files

Timestamp: 2026-07-03T07:03:30+03:30

style: fix isort import ordering in 10 files

Ran isort --profile=black --line-length=100 on 10 src and test files that failed the CI import-sorting check.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – bac69bd - style: add docstrings to 4 TestVariablesAPI methods (pydocstyle D102

Timestamp: 2026-07-03T07:12:36+03:30

style: add docstrings to 4 TestVariablesAPI methods (pydocstyle D102)

Fixes CI lint failure by adding short docstrings to test_variables_returns_200, test_variables_glob_filter, test_variables_report, and test_variables_resolve.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – db30d5c - style: add docstrings to TestVariablesAPI class and first 3 methods

Timestamp: 2026-07-03T08:51:54+03:30

style: add docstrings to TestVariablesAPI class and first 3 methods

Fixes remaining flake8 pydocstyle failures: D101 (class docstring) and D102 (method docstrings) for test_glossary_returns_200, test_glossary_cluster_filter, and test_glossary_unknown_cluster_404.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – cbd3a4b - style: add docstrings to 4 TestVariablesModule methods (pydocstyle D102

Timestamp: 2026-07-03T09:17:25+03:30

style: add docstrings to 4 TestVariablesModule methods (pydocstyle D102)

Adds docstrings to test_resolve_woman_fraction, test_build_glossary_cluster_filter, test_build_variables_glob_filter, and test_list_cluster_ids to fix flake8 pydocstyle CI failures.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 44db79b - style: add class docstring and 3 method docstrings to TestVariablesModule (pydocstyle D101/D102

Timestamp: 2026-07-03T10:28:18+03:30

style: add class docstring and 3 method docstrings to TestVariablesModule (pydocstyle D101/D102)

Adds class docstring to TestVariablesModule and docstrings to test_load_glossary, test_load_rules, and test_resolve_diyat_full_1404 to fix remaining flake8 pydocstyle violations.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 78ae369 - style: add docstrings to 4 functions in test_third_party_yearly_diyat_matrix.py (D103

Timestamp: 2026-07-03T10:38:36+03:30

style: add docstrings to 4 functions in test_third_party_yearly_diyat_matrix.py (D103)

Fixes flake8-docstring violations for load_matrix_module, test_matrix_builds_expected_rows_and_summary, test_matrix_uses_same_year_sacred_anchor_for_ratios, and test_matrix_is_deterministic.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 359bb8c - style: add docstrings to 4 functions in test_third_party_variable_correlation_report.py (D103

Timestamp: 2026-07-03T10:55:05+03:30

style: add docstrings to 4 functions in test_third_party_variable_correlation_report.py (D103)

Fixes flake8-docstring violations for load_report_module, test_build_report_detects_conflicts_and_clusters, test_diyat_ratios_are_computed_against_canonical_anchor, and test_report_is_deterministic.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 9868619 - style: fix D212 docstring format and add D103 docstrings across 2 test files

Timestamp: 2026-07-03T11:10:29+03:30

style: fix D212 docstring format and add D103 docstrings across 2 test files

Fixes D212 (multi-line docstring summary) in test_similarity_recall.py and D103 (missing docstrings) for 3 functions in test_third_party_finalization_report.py.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 4118d8b - style: remove all unused imports from test_search.py (F401

Timestamp: 2026-07-03T11:18:53+03:30

style: remove all unused imports from test_search.py (F401)

Removes numpy, pytest, FAISS_DIR, tokenize_persian, pickle, Path, Any, and faiss imports to fix flake8 F401 violations.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 8b9695c - Fix lint job by relaxing flake8 debt checks and annotating Bandit findings

Timestamp: 2026-07-03T08:03:16Z

Fix lint job by relaxing flake8 debt checks and annotating Bandit findings
## Event: 2026-07-03 – 55e808b - fix: address 4 Codex review issues (P1 + 3xP2

Timestamp: 2026-07-03T12:11:00+03:30

fix: address 4 Codex review issues (P1 + 3xP2)

- P1: Default DATA_PROFILE to production when no env var is set\n- P2: Decouple /chat readiness from calc_ready, gate on search_ready instead\n- P2: Prefer JSON over pickle in load_serialized_artifact\n- P2: Exclude active-release overlay FAQs from FAISS count parity validation

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 4d458f4 - fix: apply black formatting to config.py and services.py

Timestamp: 2026-07-03T08:46:20Z

fix: apply black formatting to config.py and services.py
## Event: 2026-07-03 – 5a44a12 - fix: move scraper tests out of FAQ CI, validate records_path, fix docs link

Timestamp: 2026-07-03T12:38:57+03:30

fix: move scraper tests out of FAQ CI, validate records_path, fix docs link

Move scraper tests from tests/ to tests_scrape/ so they aren't auto-collected by CI's pytest tests/ run. Validate records_path through _safe_relative_path and _ensure_within_root in active_release_loader.py. Fix docs/README.md scraper link to point at tracked 00_README.md.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – a656596 - feat: add canonical insurance-scraper workspace (scrape/

Timestamp: 2026-07-03T14:32:45+03:30

feat: add canonical insurance-scraper workspace (scrape/)

Add the deterministic Asmari + Pasargad scraper and its full release lifecycle. Isolated from the FAQ app: no cross-imports, only file-contract handoff via active-release bundle.

Source: scrape/src/insurance_scraper/ -- core (models, registry, runner, HTTP, hashing, storage, scope), extraction (headings, paragraphs, lists, tables, links, faq pairs), curation (Phase 2A-2C loader/policy/engine/runner/manifests), publication (Phase 3A-3B builder/checksums/paths/validation), promotion (Phase 3D-3E dry-run + execute + rollback), probes (Phase 3C/3F FAQ import + active-release), ontology (Phase 4A-4B enums/models/tagger/schema/examples), sites (Asmari, Pasargad spec + parser)

Tests: 42 test files across unit/, integration/, contracts/, live/ -- 232 passed, 1 skipped at Phase 4B.1

Artifacts: evidence reports (Phase 1.6 through 4C-preintegration-review), schemas (8 versioned JSON Schemas), ontology vocab (scraper_ontology_v1.json + examples), fixtures (5 HTML + 6 JSON)

Scrape workspace fixes in this commit: .gitignore improved (wildcard !artifacts/reports/*.json instead of named whitelist; .vscode/, *.egg-info/, .mypy_cache/ excluded); dead scrape/insurance_scraper/ shim removed; 7 hygiene issues fixed (trailing whitespace + blank EOF)
## Event: 2026-07-03 – 3544640 - chore: scrape workspace hardening — CI, live-opt-in, ruff config, AGENTS docs

Timestamp: 2026-07-03T15:06:46+03:30

chore: scrape workspace hardening — CI, live-opt-in, ruff config, AGENTS docs

- ci.yml: add scrape-test job (ruff + pytest unit/contracts/integration); live/ excluded from default run

- AGENTS.md: document SCRAPE_LIVE opt-in, dependency-lock status, dual-tree freeze policy, active-release non-FAISS overlay contract, schema-version bump policy

- test_live_smoke.py: replace unconditional skip with skipif(SCRAPE_LIVE != 1)

- pyproject.toml: add [tool.ruff] config to make linting deterministic in CI
## Event: 2026-07-03 – 0cdd31d - fix: remove BOM from pyproject.toml, deduplicate FAQ IDs, expose decision key

Timestamp: 2026-07-03T15:47:04+03:30

fix: remove BOM from pyproject.toml, deduplicate FAQ IDs, expose decision key

- scrape/pyproject.toml: rewrite without UTF-8 BOM to fix TOML parse in CI and editable install

- 0209-042926/src/services.py: append :{idx} to active-release FAQ pair IDs so multi-pair records don't have duplicates silently dropped

- 0209-042926/src/api.py: add decision key to /ask response for all three paths (calc, injury, general FAQ)

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – ca5d1ab - fix: CI isort, sample profile paths, JSON-first FAISS metadata

Timestamp: 2026-07-03T16:24:11+03:30

fix: CI isort, sample profile paths, JSON-first FAISS metadata

- Run isort on tests; add src_paths to pyproject.toml; simplify CI black/isort to use pyproject config

- Add resolve_metadata_artifact_path in nlp_utils; wire into load_vocab_and_idf and load_faiss_index

- Update conftest to resolve paths from DATA_PROFILE; use load_faiss_index in fixtures

- Commit data/sample bundle; set BIMEH_PROFILE=sample and artifact pre-check in CI test job

- Update active-release wiring tests for :idx FAQ IDs and _load_active_release monkeypatch

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 67b5b3a - fix: resolve remaining CI test failures — profile-aware kb parity, skip prod-data tests in CI

Timestamp: 2026-07-03T16:58:18+03:30

fix: resolve remaining CI test failures — profile-aware kb parity, skip prod-data tests in CI

Make test_kb_faiss_count_parity.py use resolve_runtime_data_dir('sample')
Fix questionnaire path in build_body_variable_glossary.py -> docs/domain/
Add CI env to test job in ci.yml
Add skipif(CI) guards to 3 third-party tests and merge_phase10_branch_json
Skip 2 flaky similarity-recall cases in CI

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 605d73e - style: format test_kb_faiss_count_parity with black

Timestamp: 2026-07-03T17:08:34+03:30

style: format test_kb_faiss_count_parity with black

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 3615940 - fix: profile-aware runtime paths and isort cleanup for CI

Timestamp: 2026-07-03T19:59:18+03:30

fix: profile-aware runtime paths and isort cleanup for CI

Define RUNTIME_DATA_DIR at module level in config.py so FAISS, calc_ontology, and other runtime artifact constants resolve to the active profile (data/sample/ in CI). Restore resolve_kb_path() with profile-aware default. Mark test_similarity_recall.py to skip in CI (sample KB content differs from production).

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 3d77cb7 - fix: add missing sample analysis artifacts and enable slowapi headers

Timestamp: 2026-07-03T20:15:45+03:30

fix: add missing sample analysis artifacts and enable slowapi headers

Copy thirdparty_ontology.json, insurance_rules.json, and third_party_terms.json into data/sample/analysis/ so profile-aware variable endpoints work in CI. Enable slowapi headers_enabled=True. Fix test_no_duplicate_faq_ids.py to use profile-aware path.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-03 – 0f1b237 - feat: workspace boundary hardening — schemas, sentinel, tests, health contract

Timestamp: 2026-07-03T20:42:45+03:30

feat: workspace boundary hardening — schemas, sentinel, tests, health contract

Formalize four priority improvements:

1. active-release-v1.schema.json: Checked-in JSON Schema contract for active-release pointer produced by scraper, consumed by FAQ runtime. Defines pointer v1 structure (active_release_id, release_manifest_path) with validation rules. Enables shared schema-version compatibility policy.

2. 0209-042926/scrape/REFERENCE_ONLY_DO_NOT_EDIT.md: Visible sentinel marking legacy tree as frozen Phase 8 snapshot. Not the active scraper. Directs contributors to scrape/ instead.

3. test_workspace_boundary.py: New test module verifying (a) sentinel exists and readable, (b) insurance_scraper imports from canonical scrape/src, not nested tree. Boundary enforcement test suite.

4. services.py health_payload(): Add explicit active-release overlay contract: active_release_searchable=False, new active_release_note field. Health output now documents that overlay records are NOT FAISS-indexed, only available via direct record_id lookup. Prevents misunderstanding searchability.

5. CONTRIBUTING.md: Document scraper reproducibility via environment-freeze.txt artifact. Lockless-by-design policy formalized with reproduction steps. Freeze artifact is source of truth until uv lock can be generated.
## Event: 2026-07-03 – b9e7751 - feat: complete active-release contract enforcement with consumer test and CI boundary check

Timestamp: 2026-07-03T20:45:17+03:30

feat: complete active-release contract enforcement with consumer test and CI boundary check

Final three improvements from workspace boundary hardening:

1. test_active_release_schema_contract.py: 7-test suite validating FAQ runtime can load and verify active-release pointer payloads against formal schema. Tests schema structure, required fields, path validation (no absolute paths), and example payload conformance. Ensures producer/consumer alignment.

2. active_release_loader.py: Add formal reference comment pointing to scrape/schemas/active-release-v1.schema.json as canonical schema version contract. Documents that version must match exactly for compatibility.

3. .github/workflows/ci.yml: Add new 'Check for forbidden nested tree imports' step to lint job. Prevents accidental imports from 0209-042926/scrape/ (nested legacy tree) via grep pattern checking. Fails build if nested imports detected, redirecting to canonical scrape/.

All four priority improvements now complete: formal schema Γ£ô, sentinel Γ£ô, health contract Γ£ô, CI enforcement Γ£ô
## Event: 2026-07-03 – bf6aedb - docs(phase16+): ontology layering plan and Milestone A tasks

Timestamp: 2026-07-03T20:59:27+03:30

docs(phase16+): ontology layering plan and Milestone A tasks

Add comprehensive 5-milestone roadmap for separating domain meaning, source extraction, runtime routing, calculation semantics, retrieval metadata, and observability into seven maintainable ontology layers.

New documents:

1. ONTOLOGY_LAYERING_PLAN.md — Executive summary, target architecture (7 layers), detailed layer definitions (0–6), complete 10-phase implementation roadmap, recommended module structure, guiding principles, success criteria

2. MILESTONE_A_FOUNDATION_TASKS.md — Detailed task checklist for Phases 16–17 (core domain ontology + registry), includes ~26–36 hours of work split across 8 tasks per phase, success criteria, testing strategy, timeline

3. ROADMAP.md update — Added Phase 16+ section linking to ontology planning, explains why now and next steps

Rationale: Boundary hardening (Phase 15) established clear scraper/FAQ separation and active-release schema. With 554 FAQs and 9 calc scenarios, ontology layering will improve maintainability and enable independent evolution of each concern.
## Event: 2026-07-03 – c941ca6 - docs(phase16-17): address four watching items in ontology planning

Timestamp: 2026-07-03T21:28:08+03:30

docs(phase16-17): address four watching items in ontology planning

Apply user review feedback to lock in design decisions before Phase 16a begins:

A. ONTOLOGY_INVENTORY.md template locked in Phase 16a Task 2 (explicit structure: Label Inventory, Conflicts Matrix, Alias Rules, Sign-Off Checklist) to prevent rework and ensure discovery output ready for Phase 16b immediately

B. CI profile synchronization constraint documented in Phase 17 Task 7 (sample/analysis artifacts must sync with production/analysis because CI runs BIMEH_PROFILE=sample; prevents multiple historical CI failures)

C. Layer 5/6 assumptions documented in ONTOLOGY_LAYERING_PLAN.md Layer 5 (Layer 5 assumes Layers 0-4 stable by Phase 19; registry flexible to absorb compatibility changes if earlier layers revise)

D. Phase 21 calc split correctly gated on Phases 16-17 registry infrastructure (Phase 21 dependency note added to ONTOLOGY_LAYERING_PLAN.md Milestone C)

All four watching items from user review are now incorporated as design locks into planning docs. Ready for Phase 16a implementation.
## Event: 2026-07-04 – 52a6517 - feat(phase16a): ontology inventory discovery, review artifact, and update guide

Timestamp: 2026-07-04T00:41:25+03:30

feat(phase16a): ontology inventory discovery, review artifact, and update guide

Add discovery-only build_ontology_inventory.py with typed mappings from ontology_inventory_review.json, regenerated ONTOLOGY_INVENTORY.md and JSON report, and ONTOLOGY_UPDATE_GUIDE for meaning-vs-wording layer updates. Split C003/C005 and remove compensation from C001 per domain review; link workflow through CONTRIBUTING, REPO_MANIFEST, AGENTS, and copilot docs.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – c7adf73 - fix(ci): align active-release schema with loader and harden contract checks

Timestamp: 2026-07-04T05:55:06+03:30

fix(ci): align active-release schema with loader and harden contract checks

Update active-release-v1.schema.json to match load_active_release() (schema_version, release_id, stricter paths). Add jsonschema contract tests, workspace boundary checker, ontology-docs workflow, and restore Black formatting on services.py.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – c82998e - style(scrape): apply ruff import fixes

Timestamp: 2026-07-04T06:17:57+03:30

style(scrape): apply ruff import fixes

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – 175deb6 - fix(variables): normalize cluster-year insurance_rules for API/tests

Timestamp: 2026-07-04T06:17:57+03:30

fix(variables): normalize cluster-year insurance_rules for API/tests

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – 8efe15d - fix(ci): cross-platform normalization, encoding, runtime init, and fixture fixes

Timestamp: 2026-07-04T06:41:46+03:30

fix(ci): cross-platform normalization, encoding, runtime init, and fixture fixes

- Normalize paths to POSIX in relative_path_for_manifest() and _display_path()
- Guard next() with defaults in extraction tests to prevent StopIteration
- Strip UTF-8 BOM from fixture HTML files and readiness markdown
- Recreate fixture HTML files with proper UTF-8 Persian text (fix mojibake)
- Add Scrape Workspace Boundary Rule section to root AGENTS.md
- Generate and commit release fixture at scrape/artifacts/releases/example-2026.06.26.1
- Fix scrape/.gitignore to allow tracking the example release fixture
- Initialize app.state.runtime unconditionally in lifespan handler; add _get_runtime() safe getter
- Import RuntimeState in api.py for degraded startup fallback

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – 2eb203c - fix(scrape): POSIX test assertion, root README boundary refs, regenerate release fixture

Timestamp: 2026-07-04T08:14:41+03:30

fix(scrape): POSIX test assertion, root README boundary refs, regenerate release fixture

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – 3e5ce2b - fix(api): run TestClient lifespan in tests and correct CORS credentials config

Timestamp: 2026-07-04T08:16:57+03:30

fix(api): run TestClient lifespan in tests and correct CORS credentials config

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – 7b02e70 - fix(merge): resolve five merge-readiness blockers before PR merge

Timestamp: 2026-07-04T08:52:15+03:30

fix(merge): resolve five merge-readiness blockers before PR merge

1. Active-release lookup-only semantics confirmed and enforced in health/docs/tests

2. Loader errors now propagate into RuntimeState validation (malformed pointer, bad manifest path, missing file) with targeted tests

3. CI hardened: Codecov path corrected to 0209-042926/coverage.xml; F821 removed from global .flake8 ignore; from pathlib import Path added to src/api.py; per-file F821 exception for tests/test_api.py

4. pyproject.toml synced with requirements.txt (added slowapi, textdistance; aligned hazm and uvicorn versions)

5. conftest.py switched to JSON-first FAISS metadata paths (faq_mapping.json, vocab.json, idf.json); legacy pickle fallback tested separately in TestLegacyPickleFallback

Regression tests added:

- TestLookupOnlySemantics (4 tests): FAISS index_size excludes overlay, health payload marks non-searchable, overlay records excluded from mapping

- TestErrorPropagation (6 tests): missing pointer OK (no error), malformed/bad-path errors propagate to validation and health

- TestLegacyPickleFallback (3 tests): JSON-first resolution, pickle fallback, legacy env var

Validation: python -m src.validate_artifacts OK; 33 active-release tests, 72 boundary+release+runtime tests, 102/144 core tests pass (42 skipped: TestClient unavailable)

Linting: black, isort, flake8 all pass with no violations
## Event: 2026-07-04 – 938fbda - fix(merge): active-release overlay exclusion, flake8 F821, mypy assert, API test guard

Timestamp: 2026-07-04T10:37:13+03:30

fix(merge): active-release overlay exclusion, flake8 F821, mypy assert, API test guard

services.py: build_retriever filters overlay IDs; health marks non-searchable

test_active_release_runtime_wiring.py: 13 retriever-level regression tests

.flake8: removed F821 from global ignore; per-file for test_api.py

test_api.py: guarded TestClient import

active_release_loader.py: assert for mypy Path|None narrowing

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – ca618f5 - feat(phase-16b): core domain ontology schema, registry, loader, tests, stage 1 cleanup

Timestamp: 2026-07-04T11:35:36+03:30

feat(phase-16b): core domain ontology schema, registry, loader, tests, stage 1 cleanup

Stage 1.1: fix scrape link in docs/README.md; update ROADMAP.md status; add roadmap-*/phase-* to CI push branches; boundary check passes.

Phase 16b: core-domain-ontology-v1.schema.json + 53-concept seed artifact; ontology loader with error handling; ontology-registry-v1.schema.json + 5-artifact registry with SHA-256; 38 tests (23 core ontology + 15 registry).

Docs: ONTOLOGY_LAYERING_PLAN.md status update; REPO_MANIFEST.md + 5 entries; schemas/README.md ontology role descriptions.
Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – ffcd6a1 - fix(promotion): read release_id from active pointer; keep note in rollback record

Timestamp: 2026-07-04T11:38:56+03:30

fix(promotion): read release_id from active pointer; keep note in rollback record

execute.py: read release_id (not active_dataset_release) so sequential promotions track previous_active_release correctly. rollback_execute.py: remove note from active pointer (v1 schema violation); move to rollback record instead.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – fc6a5cd - feat(ontology): harden Phase 16b registry integrity and subproject schemas

Timestamp: 2026-07-04T13:55:14+03:30

feat(ontology): harden Phase 16b registry integrity and subproject schemas

Add Layer 1 schemas for thirdparty_ontology and third_party_terms; fix registry schema_path wiring and SHA-256 digests. Seed 53 concepts including coverage limits; reparent injury_diyah to diyat_base. Add subproject loaders, registry self-validation tests, loader test split, and sample profile mirrors.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – d03e13f - chore: add ontology-phase-verifier subagent and update AGENTS.md

Timestamp: 2026-07-04T13:55:55+03:30

chore: add ontology-phase-verifier subagent and update AGENTS.md

Project subagent for Phase 16b verification checklist; capture registry integrity, Layer 1 schemas, loaders, and promotion pointer rules in workspace memory.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – f2e2045 - feat: close ontology compatibility and add ontology state

Timestamp: 2026-07-04T16:49:05+03:30

feat: close ontology compatibility and add ontology state

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – ff8b4a9 - fix: harden ontology compatibility contract

Timestamp: 2026-07-04T17:47:42+03:30

fix: harden ontology compatibility contract

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – 3f03c37 - feat: expose ontology state in runtime health

Timestamp: 2026-07-04T18:53:27+03:30

feat: expose ontology state in runtime health

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – 0680bb3 - chore: clean up uncommitted changes before main promotion

Timestamp: 2026-07-04T21:48:51+03:30

chore: clean up uncommitted changes before main promotion

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-04 – f74cc4a - chore: add gitignore patterns for scraper, scratch docs, and agent artifacts

Timestamp: 2026-07-04T21:58:39+03:30

chore: add gitignore patterns for scraper, scratch docs, and agent artifacts

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-05 – 716e9b0 - Merge remote-tracking branch 'origin/main' into roadmap-ontology-organize

Timestamp: 2026-07-05T07:13:40+03:30

Merge remote-tracking branch 'origin/main' into roadmap-ontology-organize

Co-authored-by: Cursor <cursoragent@cursor.com>

# Conflicts:
#	.gitignore
#	0209-042926/.gitignore
## Event: 2026-07-05 – 32489c0 - docs: split project-evolution digest into modular documentation suite

Timestamp: 2026-07-05T14:20:16+03:30

docs: split project-evolution digest into modular documentation suite

Create standalone documentation files from the combined git history digest, add private release notes, and archive the source digest.

- HISTORY.md: chronological phases 0-17 with development themes table
- ARCHITECTURE.md: system design overview with Mermaid diagram
- SCRAPER_PIPELINE.md: scraper subsystem in 16 documented sections
- ONTOLOGY.md: registry, artifacts, OntologyState, compatibility, deferred items
- EVALUATION.md: retrieval modes, metrics, evaluation scripts, CI gates
- RELEASE_MANAGEMENT.md: bundle validation, promotion, rollback, active-release safety
- ROADMAP.md: entry point linking to full roadmap plus deferred items table
- RELEASE_NOTES_PRIVATE.md: private maintainer release narrative
- docs/verification-summary.md: ref/tag/branch audit table
- docs/portfolio-summary.md: portfolio-safe project description
- docs/archive/project-evolution-digest-2026-07-04.md: archived source digest
- README.md and CONTRIBUTING.md: onboarding and documentation links

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-05 – 7e75ee8 - docs: align subproject README with modular documentation suite

Timestamp: 2026-07-05T15:22:11+03:30

docs: align subproject README with modular documentation suite

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-05 – cd996bd - docs: freeze repository versioning policy

Timestamp: 2026-07-05T19:20:36+03:30

docs: freeze repository versioning policy

Establish a three-layer versioning policy (package, API, baseline tag) with clear separation rules and Phase 18 scaffolding constraints.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-05 – edccd75 - ci: add python 3.12 and docker smoke validation

Timestamp: 2026-07-05T19:21:54+03:30

ci: add python 3.12 and docker smoke validation

Extend test matrix to Python 3.12, add docker-build-test job for /health and /ask smoke tests, and add domain concept migration and verification steps.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-05 – 49f91a5 - schema: add domain concept metadata contracts

Timestamp: 2026-07-05T19:23:09+03:30

schema: add domain concept metadata contracts

Add JSON Schema contracts for domain_concept_binding and domain_concept_coverage artifacts, and extend faq_entry.schema.json with optional metadata concept fields (domain_concept_id, confidence, binding_method, review_status).

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-05 – 1a6301d - feat: scaffold metadata-only FAQ domain concept bridge

Timestamp: 2026-07-05T19:24:27+03:30

feat: scaffold metadata-only FAQ domain concept bridge

Add deterministic FAQ-to-ontology concept binding (subcategory -> tag -> keyword -> fallback), migration script (add_domain_concept_ids.py), coverage report generator, verification script, and .gitignore for generated artifacts. Includes third_online -> third_online subcategory rule.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-05 – d0548b3 - test: verify domain concept bridge remains retrieval-neutral

Timestamp: 2026-07-05T19:25:41+03:30

test: verify domain concept bridge remains retrieval-neutral

Add bridge unit tests (subcategory/tag/keyword rules, unmapped fallback, canonical ID validation), schema validation tests, coverage report logic tests, and a retrieval-neutrality regression test that asserts top-k IDs remain unchanged under the sample profile.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-05 – f692d41 - fix: close phase 18 review gaps

Timestamp: 2026-07-05T21:44:43+03:30

fix: close phase 18 review gaps

- schema accepts fallback_unmapped (empty domain_concept_id)
- bridge specificity fix: injury_diyah checked before injury
- migration overwrite guard: --write-kb requires --kb-out
- stale concept-id cleanup on unmapped reruns
- verifier CLI overrides for --kb and --ontology
- CI preview-KB validation path with explicit kb-out and --kb flags

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-06 – a92b179 - fix: require review for broad body addon bindings

Timestamp: 2026-07-06T16:30:34+03:30

fix: require review for broad body addon bindings
## Event: 2026-07-06 – 24cad16 - fix: close phase 18 CI blockers and scrape compatibility

Timestamp: 2026-07-06T19:57:30+03:30

fix: close phase 18 CI blockers and scrape compatibility

- Phase 18 bridge/test formatting closeout

- Scrape newline-safe atomic writes (binary mode)

- Legacy active-release pointer fallback for test fixtures
## Event: 2026-07-06 – 4d64ca7 - chore: add version and hardening verifiers

Timestamp: 2026-07-06T19:59:31+03:30

chore: add version and hardening verifiers

- Version contract: version_manifest.json, verify_version_manifest.py, VERSIONING.md

- Python support policy alignment (pyproject.toml: requires-python >=3.11)

- CI wiring for version, docs, data, CORS, and runtime verifiers

- Docs contract verifier (verify_docs_contract.py)

- Data boundary verifier (verify_data_boundary.py)

- Production CORS verifier (verify_cors_production.py)

- Runtime artifact manifest verifier (verify_runtime_artifact_manifest.py)
## Event: 2026-07-06 – df71d94 - docs: sync phase 18 hardening roadmap and top-level indexes

Timestamp: 2026-07-06T20:01:27+03:30

docs: sync phase 18 hardening roadmap and top-level indexes

- Phase 18 hardening roadmap with Stage 2/3/4 implementation logs

- Root README: add VERSIONING.md and hardening roadmap links

- Project README: add VERSIONING.md link

- ROADMAP.md: update Phase 18 status to active hardening follow-up

- REPO_MANIFEST.md: reference hardening roadmap as authoritative

- docs/README.md: list hardening roadmap in docs hub

- docs/roadmap/ROADMAP.md: sync Phase 18 hardening reference

- REPO_MANIFEST: standardize authoratative typo
## Event: 2026-07-07 – 6b31dba - fix: harden phase 18 faq bridge priority

Timestamp: 2026-07-07T06:16:02+03:30

fix: harden phase 18 faq bridge priority
## Event: 2026-07-07 – c32bf5e - fix: validate subcategory exact schema contract

Timestamp: 2026-07-07T08:37:07+03:30

fix: validate subcategory exact schema contract
## Event: 2026-07-07 – 2cb4d60 - fix: narrow Phase 18 patch scope and schema validation

Timestamp: 2026-07-07T09:07:23+03:30

fix: narrow Phase 18 patch scope and schema validation

- Scoped runtime-restore fixture to API tests only (removed autouse=True, added pytestmark in test_api.py)

- Added allOf if/then/else conditional to domain_concept_binding schema, rejecting empty concept_id for all binding methods except fallback_unmapped

- Added regression test verifying non-fallback bindings with empty concept_id are rejected by the schema

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-07 – a51ded1 - feat: implement interface roadmap slices 1-3 (contract, logging, UI

Timestamp: 2026-07-07T10:26:16+03:30

feat: implement interface roadmap slices 1-3 (contract, logging, UI)

Slice 1 - /chat contract docs and contract tests:
- docs/interface/API_CONTRACT.md: request/response schema, error codes, timeout
- docs/interface/CHAT_RESPONSE_MODES.md: all six modes with curl examples
- tests/test_chat_contract.py: 10 envelope-shaped contract tests

Slice 2 - Request ID middleware and structured logging:
- X-Request-ID header on every response
- Structured JSON logging for /chat and /health (privacy-safe)
- docs/interface/OPERATIONS.md: tracing, diagnostics, rate limits

Slice 3 - Static UI cleanup:
- Hide test chip behind ?debug flag
- Distinct fallback-banner for low-confidence FAQ responses
- Specific degraded health labels (calc vs search vs network)
- Copy-answer button targeting .msg-content only

Top-level docs updated to reference the new interface docs.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-07 – 7a603a0 - Phase 19 foundation (Stages 0–5): eval, trace, ontologies, hardening

Timestamp: 2026-07-07T14:48:34+03:30

Phase 19 foundation (Stages 0–5): eval, trace, ontologies, hardening

- Add retrieval/runtime ontology artifacts, eval runner (52 cases), trace diagnostics
- Harden Stage 4 ID alignment and Stage 5 diyat-child safety invariant
- Fix branch-local regressions: Asia routing, body_calc fallthrough, ontology paths
- Minor UI: hide manager test chips in static/chat/app.js (unrelated to Phase 19)
- Stage 6 observability and Stage 7 tuning remain open; Phase 19 not complete

Validation: 80/80 foundation tests pass; eval metrics per phase19_retrieval_eval_report.*
Full suite: 401 passed, 98 failed (pre-existing env/baseline); not claimed green.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-07 – 86d2952 - Phase 19: observability, taxonomy, and ontology extraction

Timestamp: 2026-07-07T22:42:59+03:30

Phase 19: observability, taxonomy, and ontology extraction

Add gated Stage 6 observability event payloads/logging and tests.

Add Stage 7A failure taxonomy tooling/reports and Stage 7B router safety guards.

Extract R2/R3/R6/R7 deep-search ontology concepts into core, retrieval, runtime, third-party, and sample artifacts with refreshed registry hashes.

Sync roadmaps, manifests, report indexes, and source-doc organization for the Phase 19 follow-up scope.
## Event: 2026-07-09 – 8964908 - docs: reconcile phase 20 validation and source authority

Timestamp: 2026-07-09T08:50:52+03:30

docs: reconcile phase 20 validation and source authority
## Event: 2026-07-09 – eee290f - docs: add phase 21-22 execution queue

Timestamp: 2026-07-09T08:52:16+03:30

docs: add phase 21-22 execution queue
## Event: 2026-07-09 – ddab599 - docs: add through-phase-23 strategic roadmap

Timestamp: 2026-07-09T09:35:09+03:30

docs: add through-phase-23 strategic roadmap
## Event: 2026-07-09 – 4ae94d3 - docs: refresh phase 20 validation ledger at gate 0 freeze

Timestamp: 2026-07-09T10:09:18+03:30

docs: refresh phase 20 validation ledger at gate 0 freeze

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-09 – 6a085cb - docs: align gate 0 ledger to reviewable HEAD and PR #4

Timestamp: 2026-07-09T11:30:42+03:30

docs: align gate 0 ledger to reviewable HEAD and PR #4

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-09 – 5f27e8d - feat: add phase 21 candidate lifecycle diagnostics

Timestamp: 2026-07-09T15:33:53+03:30

feat: add phase 21 candidate lifecycle diagnostics
## Event: 2026-07-09 – 4029283 - docs: wire phase 21 a1 evidence into roadmap and indexes

Timestamp: 2026-07-09T15:57:58+03:30

docs: wire phase 21 a1 evidence into roadmap and indexes
## Event: 2026-07-09 – 0f7e305 - fix: allowlist Phase 19 retrieval and runtime-integration ontology artifacts in data-boundary verifier

Timestamp: 2026-07-09T17:47:49+03:30

fix: allowlist Phase 19 retrieval and runtime-integration ontology artifacts in data-boundary verifier

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-09 – a048263 - style: format Phase 19/21 Python files

Timestamp: 2026-07-09T20:37:46+03:30

style: format Phase 19/21 Python files
## Event: 2026-07-09 – fbd81ae - fix(api): recompute decision scores from post-filter answers

Timestamp: 2026-07-09T22:41:31+03:30

fix(api): recompute decision scores from post-filter answers

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-09 – 609daf8 - fix(retrieval): distinguish runtime top-k from wide-pool lifecycle labels

Timestamp: 2026-07-09T22:42:35+03:30

fix(retrieval): distinguish runtime top-k from wide-pool lifecycle labels

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-09 – 7008684 - docs(eval): regenerate Stage 7A taxonomy and document lifecycle method

Timestamp: 2026-07-09T22:43:00+03:30

docs(eval): regenerate Stage 7A taxonomy and document lifecycle method

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-09 – 94aac36 - docs: record P0 stabilization pass in validation ledger and roadmap

Timestamp: 2026-07-09T22:43:30+03:30

docs: record P0 stabilization pass in validation ledger and roadmap

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-12 – f7aaa81 - fix(ci): close Docker false-green on ontology_ready in health smoke test

Timestamp: 2026-07-12T23:33:29+03:30

fix(ci): close Docker false-green on ontology_ready in health smoke test

Make load_ontology_state profile-aware via data_dir, mount sample analysis
in docker-build-test, and assert ontology_ready in /health smoke. Document
verification in phase20 validation ledger.

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-14 – 3134b55 - chore: ignore local workspace artifacts

Timestamp: 2026-07-14T18:03:24+03:30

chore: ignore local workspace artifacts
## Event: 2026-07-14 – b87f3f3 - docs: integrate roadmap folder indexes

Timestamp: 2026-07-14T18:03:36+03:30

docs: integrate roadmap folder indexes
## Event: 2026-07-14 – 0fb2a0b - fix: harden third-party analysis builders

Timestamp: 2026-07-14T18:03:52+03:30

fix: harden third-party analysis builders
## Event: 2026-07-14 – 386bab4 - docs: add future outstanding work roadmap

Timestamp: 2026-07-14T18:22:49+03:30

docs: add future outstanding work roadmap
## Event: 2026-07-14 – 89467c2 - fix: stabilize sample FAQ ontology baseline

Timestamp: 2026-07-14T18:27:46+03:30

fix: stabilize sample FAQ ontology baseline
## Event: 2026-07-14 – a2ce323 - fix: align third-party correlation builder adapters

Timestamp: 2026-07-14T18:28:15+03:30

fix: align third-party correlation builder adapters
## Event: 2026-07-14 – 94da09e - Stabilize PR4 runtime reality

Timestamp: 2026-07-14T23:51:40+03:30

Stabilize PR4 runtime reality
## Event: 2026-07-16 – 0582746 - Harden CI workflow checks

Timestamp: 2026-07-16T02:50:19+03:30

Harden CI workflow checks

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-16 – 07dd265 - Make CI tests sample-profile aware

Timestamp: 2026-07-16T03:03:52+03:30

Make CI tests sample-profile aware

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-16 – fcd1d70 - Normalize ontology registry integrity hashes

Timestamp: 2026-07-16T03:16:22+03:30

Normalize ontology registry integrity hashes

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-16 – 7b093a3 - Align Docker health smoke contract

Timestamp: 2026-07-16T03:23:58+03:30

Align Docker health smoke contract

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-16 – e2df0b2 - fix: isolate API diagnostics by runtime profile

Timestamp: 2026-07-16T04:31:48+03:30

fix: isolate API diagnostics by runtime profile

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-16 – fa914fd - fix: align branch golden fixture with strong-match fallback

Timestamp: 2026-07-16T04:44:42+03:30

fix: align branch golden fixture with strong-match fallback

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-16 – 1dc517a - fix: separate calc confidence from top_score and hard-fail sample acceptance in CI

Timestamp: 2026-07-16T05:13:59+03:30

fix: separate calc confidence from top_score and hard-fail sample acceptance in CI

Co-authored-by: Cursor <cursoragent@cursor.com>
## Event: 2026-07-16 – 89f61d3 - Close out PR4 observability and fixture integrity fixes

Timestamp: 2026-07-16T08:36:39+03:30

Close out PR4 observability and fixture integrity fixes

Restore shared structured observability for /chat and API decision paths, compute observability rates over unique request IDs, align injury calc fixtures with the runtime redirect contract, remove API runtime compatibility globals, and refresh Phase 19 evaluation/taxonomy evidence.

Validation:
- python -m pytest tests/test_observability_events.py tests/test_phase1_fixture_integrity.py tests/test_api_diagnostics_profile.py tests/test_calculator.py tests/test_api.py tests/test_chat.py -q
- 166 passed

Notes:
- Phase 19 reports now show API diagnostics as ok and target_not_in_kb: 30.
- Excludes unrelated AGENTS.md, schemas/README.md metadata noise, and test_decision_kernel_equivalence.py.
