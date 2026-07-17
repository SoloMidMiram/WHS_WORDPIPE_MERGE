---
source: 02 Project Digest
title: InsuranceChatbot Project Digest
input_file: 02_project_digest.md
event_count: 16
date: 2026-07-01 to 2026-07-04
---

# Source: 02 Project Digest

## Event: 2026-07-04 – Early Project Evolution Narrative (Pre-Baseline

This document summarises the key stages of the InsuranceChatbot project **before** the Phase 14 server‑working baseline (`f74cc4a7`). It traces the evolution from the initial knowledge base to the development of deep‑search expansions, branch address verification, and content hygiene triage. These early commits laid the foundation for the later ontology runtime baseline.
## Event: 2026-07-04 – Initial knowledge base and API (Phase 0–4

- **Initial commit (**`6cb6634` **– “chore: initial commit — Insurance FAQ Knowledge Base”)** set up the repository with 231 unique Persian FAQ pairs derived from 555 raw customer questions. It introduced:
- A TF‑IDF + FAISS semantic search index (293‑dimensional) for fast vector search and retrieval.
- A **FastAPI** server exposing `/health`, `/search`, and `/ask` endpoints.
- A hazm‑based NLP pipeline for Persian tokenisation and lemmatisation.
- Scripts for deduplication (Phase 0), subcategorisation (Phase 1), answer generation (Phase 2), and enrichment (Phase 3–4). Phase 4 analysis produced a gap matrix and root‑word coverage report.
- An initial test suite with 62 tests and CI configuration using flake8, isort, black, mypy, and pytest.
- Extensive documentation under `docs/` including an executive summary, roadmap, and phase plans.

The early knowledge base covered three insurance domains (third‑party liability, body damage, and personal injury) and 35 subcategories. Answer enrichment added context and clarity to 91 questions, achieving a claimed 99 % coverage rate.
## Event: 2026-07-04 – Deep search expansion (Phase 5

- **Phase 5b: Deep Search KB expansion (**`caa148c`**)** responded to coverage gaps by generating 195 new Q&A pairs across nine specialised topics (franchise, installments, theft, issuance types, add‑ons, special vehicles, fines, and edge cases). A hazm + Jaro‑Winkler deduplication script merged 147 of these entries into the knowledge base, increasing the total from 231 to **378** FAQs. The commit updated the preferred knowledge base path to `knowledge_base_phase5_deep_merged.json` and adjusted API logic to automatically select the merged KB when available. It expanded the domain‑coverage table, rebuilt the FAISS index, updated tests (dimension 293→300), and documented the process in `PHASE5_DEEP_SEARCH_MERGE.md` with merge statistics and next steps.
## Event: 2026-07-04 – Ontology update and injury deep search (Phase 8 H4

- **Phase 8 H4 (**`e3b8d91`**)** performed a second deep‑search wave focusing on **injury entries**. It added a curated set of H4 entries (eight new questions), updated the ontology files for injury categories, rebuilt the FAISS index (increasing vectors from 372 to 409 while keeping 300 dimensions), and refreshed gap and coverage reports. It mapped 63 bilingual questionnaire items to knowledge‑base subcategories and reorganised the project’s documentation and scripts, adding numerous plan and report files for later phases.
## Event: 2026-07-04 – Reorganisation and survey integration

- **Scripts and tools reorganisation (**`9e85042`**)** reorganised the repository structure. Phase‑pipeline scripts moved into `scripts/phases/`, imports into `scripts/imports/`, utilities into `tools/`, and archives into `scripts/archive/`. It restored a script (`merge_phase10_branch_json.py`) for Phase 10, added startup checks to `src/api.py` to ensure knowledge base and FAISS index consistency, and archived deprecated scripts. A **project survey** file recorded feedback and criticism, which fed into an updated roadmap (Phase 11 tracks). Additional persona documents (portable agent personas, AGENTS.md) and company neutrality guidelines were added.
## Event: 2026-07-04 – Branch address verification and Asia branch scraping (Phase 10

- **Phase 10 branch merge (**`eb83207`**)** introduced modules to import and verify address and phone numbers for **Asia insurance branches**. It added raw scrape data for 52 Asia branches and a prompt‑based verification file. The commit created scripts for branch address extraction, merging, and reporting (e.g., `scripts/imports/merge_phase10_branch_json.py`), added tests and reports, and updated API configuration to support branch data. This work emphasised offline, deterministic processing and produced reports detailing branch merge results. It also added new prompts and raw data for body damage and calculation domains.
## Event: 2026-07-04 – Verification, retrieval hardening, and quality gates (Phase 11

- **Waves 3–4 completion (**`ed7ab97`**)** automated verification processes: a new `verify_invariants.py` script checked knowledge base/FAISS parity, ID uniqueness, and branch map consistency; tests enforced retrieval recall thresholds; and retrieval logic was hardened with an intent router, minimum score parameter, and improved error sanitisation. A `KB_HYGIENE.md` document established duplicate and merge rules, and the release pipeline generated index metadata. This phase laid the groundwork for gating future changes through CI.
## Event: 2026-07-04 – SME triage and content hygiene (Phase 12

- **Phase 12 triage infrastructure (**`e4a01f6`**)** introduced scripts for subject‑matter‑expert (SME) review. Tools exported semantic pairs requiring human judgment, captured expert decisions (e.g., “keep both” or “reject”), and automatically applied those decisions to the knowledge base. A triage audit log was created, and the knowledge hygiene document was updated.

- **Phase 12 completion (**`364a401`**)** finalised this process: all 48 heuristic‑flagged entries were reviewed and rejected, while three semantic pairs were kept as complementary content. Reports documented the analysis and updated the roadmap, marking Phase 12 as complete.
## Event: 2026-07-04 – Importing scrape results (Phase 13

- **Phase 13 scrape import (**`19ee6fd`**)** imported curated scrape results for the body damage and calculation domains from the scraper workspace into the main knowledge base. The commit added prompts and JSON results covering topics like valuation, limits/exclusions, and total loss, along with import scripts supporting dry‑run previews.
## Event: 2026-07-04 – Summary and impact

These early phases built a strong foundation for the InsuranceChatbot. Starting from a lean knowledge base and basic API, the project rapidly expanded its coverage through deep‑search research (Phases 5 and 8), improved data quality through branch verification (Phase 10) and SME triage (Phase 12), and reorganised its structure for maintainability. Ontology files and FAISS indexes were updated to accommodate new entries, and the CI pipeline matured to enforce quality gates. This groundwork allowed later phases (14–17) to focus on runtime validation, ontology integration, scraper release pipelines, and active‑release management. Without these early efforts, the sophisticated ontology runtime baseline would not have been possible.

------------------------------------------------------------------------

---

## Source: git_history_review.md
_SHA256:_ `62228ade0e5bfd20cad8e390c2fcfcc0347c77fa7aea8e724cc681ffc4791083`
## Event: 2026-07-04 – Ref verification summary

| Reference | Exists? | Notes |
|----|----|----|
| **Default branch** | ✓ | The repository’s default branch is `main`. |
| `main` **vs.** `ontology-runtime-baseline-2026-07-04` | ✓ | The `main` branch head commit (`716e9b02`) matches `ontology-runtime-baseline-2026-07-04`; they are identical. |
| `roadmap-ontology-organize` | ✓ | This branch exists and also points to `716e9b02`, so it is identical to `main`. |
| `server-working-main-plus-gitignore-2026-07-04` | ✓ | This tag/branch exists with commit `f74cc4a7` and matches the backup branch. It represents the preserved Phase 14 server‑working baseline. |
| **Backup branch** `backup/main-server-working-plus-gitignore-2026-07-04` | ✓ | This branch points to the same commit (`f74cc4a7`) as `server-working-main-plus-gitignore-2026-07-04`. |
| **Old preserved SHA** `f74cc4a7834a6f3c1625c018fdd00bec4ffdc3ea` | ✓ | Represents the Phase 14 server‑working baseline that remains unchanged. |
| **New promoted SHA** `716e9b02b4ad13fd8459393f662d489c60789aab` | ✓ | Represents the ontology runtime baseline after promotion; identical to `main` and `roadmap-ontology-organize`. |

**Consistency checks:**

- `main` and `ontology-runtime-baseline-2026-07-04` are identical, confirming that promotion happened correctly.
- `roadmap-ontology-organize` matches `main`, meaning the branch used for promotion was fully merged.
- The old baseline tag (`server-working-main-plus-gitignore-2026-07-04`) equals the backup branch, ensuring preservation of the Phase 14 server‑working state.
## Event: 2026-07-04 – Theme grouping summary

The commit history from `f74cc4a7` (server‑working baseline) to `716e9b02` (ontology runtime baseline) spans many incremental changes across several domains. The work can be grouped into the following themes, each representing a coherent engineering effort:

| Theme | What changed | Why it mattered | Representative commits | Implemented | Deferred |
|----|----|----|----|----|----|
| **1. Server‑working chatbot foundation** | The Phase 14 release delivered a functional Persian insurance FAQ chatbot using FastAPI, a retrieval layer with TF‑IDF/embedding/hybrid modes, an insurance calculator implementing Articles 8, 32–34, value reduction, and third‑party rules, and a well‑tuned knowledge base. | Established a working baseline for the chatbot, enabling users to query FAQs and calculations. | `f74cc4a7` (baseline), `9b271597` (retrieval decision integration), `1688c98b` (retrieval pipeline and evaluation), `c9e05fde` (KB validator and fixes), `f5c1a132` (value reduction), `4a6c614e` (Article 8), `0d4818ca` (third‑party ontology synchronisation). | Yes—baseline is preserved as a tag; retrieval and calculator modes are functional. | Ontology‑driven ranking and dynamic concept IDs remain deferred. |
| **2. Repository and documentation organization** | Consolidated scattered `.org` planning files into `docs/organization/`, added a reverse roadmap, file‑reference map, mermaid dependency graphs, and archiving structure. Introduced metadata patterns with `investigation_status` flags for knowledge base entries. | Provided structure for maintainers and separated long‑term planning from runtime code. Flags make it clear which FAQs need further research. | `9f821b01` (docs consolidation), `0a032f6f` (Phase 15 reorganization and metadata flags), `bf6aedbb` (ontology layering plan). | Yes—docs reorganised; does not change runtime. | None—ongoing updates continue in separate branches. |
| **3. Runtime artifact validation** | Added `active_release_loader`, `branch_lookup`, and `decision_engine` modules to load release bundles, validate artifacts, and enforce runtime safety. Provided CLI tests and phase 3 reports summarising branch compliance. | Ensured that only validated active‑release records are loaded into runtime, preventing corrupt or unverified data. | `a8a2e2ed` (runtime loaders and validation), `ed7ab974` (verification automation & branch quality pass). | Yes—runtime now validates release bundles and exposes errors without crashing. | No search indexing of active‑release overlay; dynamic reload remains limited. |
| **4. Retrieval pipeline and evaluation** | Added retrieval modes (TF‑IDF, hybrid, embedding), evaluation scripts (`eval_report.py`, `eval_coverage.py`) that compute Recall@1/3, MRR, fallback precision/recall, and gating metrics. Integrated retrieval decisions into `build_response()`. | Improved the chatbot’s answer quality and allowed maintainers to measure retrieval performance. | `1688c98b` (pipeline & evaluation), `9b271597` (decision integration), `2064b433` (evaluation framework & CI gating), `ed7ab974` (intent router and retrieval hardening). | Yes—retrieval modes and evaluation scripts exist with baseline metrics; integrated into CI. | Embedding‑based semantic search for active‑release overlay deferred. |
| **5. Third‑party insurance knowledge consolidation** | Synchronised third‑party ontology and glossary across variables and clusters; added values matrix summarising coverage limits, coefficients, and rules. Added 60 Persian terms mapped to 38 variables across eight clusters. | Provided a coherent, machine‑readable mapping between Persian terms and third‑party variables, reducing duplication and ensuring consistency across calculators and FAQs. | `0d4818ca` (glossary, ontology, values matrix), `c19b3caa` (FAQ ontology builder), `0d4818ca` replicates across ontology and glossary. | Yes—glossary, ontology and values matrix implemented; integrated into rules and FAQs. | Expansion beyond the first insurer remains deferred. |
| **6. Value reduction (افت قیمت) and Article 8 work** | Introduced a value‑reduction knowledge cluster explaining depreciation formulas and created new FAQs. Updated `insurance_rules.json` with variables and added synonyms in the ontology. Added Article 8 variables (min/max bodily/financial cover) and related FAQs. | Captured key Iranian insurance regulations around depreciation and coverage thresholds, improving calculation accuracy. | `f5c1a132` (value reduction cluster), `4a6c614e` (Article 8 variables & FAQs). | Yes—formulas and variables available in calculator; FAQs added. | Full domain concept IDs and ranking based on ontology remain deferred. |
| **7. Persian KB validation** | Added a Hazm‑based knowledge‑base validator that extracts lemmas, detects anomalies and stop‑words, and generates a validation report. Fixed stale or unclear answers and added new FAQs (e.g., on Article 33/34 deadlines). Updated ontology `key_concepts` for meaningful names. | Ensured the knowledge base uses clear Persian, reduced duplication, and flagged entries needing improvement. | `c9e05fde` (KB validator & fixes). | Yes—validator exists and report checked into repo; improvements integrated. | Ongoing content review needed; not all flagged entries resolved. |
| **8. Active‑release safety and lookup‑only overlay** | Implemented active‑release publication, promotion, and rollback via CLI. Added runtime overlay that loads approved release bundles while restricting them to lookup‑only. Ensured overlay entries are not vector‑indexed and thus are not retrieved via semantic search. | Enabled a controlled path to deploy new knowledge without risking unvalidated data in search, and provided ability to roll back. | `a656596a` (scraper workspace & release lifecycle), `a8a2e2ed` (active‑release loader), `ed7ab974` (phase 3 verification), `scrape` docs. | Yes—publication, promotion, rollback and runtime overlay implemented. | Semantic search over active‑release data deferred; overlay remains lookup‑only. |
| **9. Insurance site scraper and release pipeline** | Added a canonical `scrape/` workspace with acquisition modules (HTTP fetcher, deterministic parsing of headings, paragraphs, lists, FAQ pairs), curation layer (deduplication, normalisation, prompt‑building), publication layer (bundling into release packages), promotion layer (upload to runtime), and rollback. Provided Asmari & Pasargad scrapers, curation CLI, release CLI, and tests. Added `scrape/docs` describing implementation and roadmap; emphasised that related links are recorded but not fetched and that live acquisition uses `playwright` only under a lock which is disabled. | Provided a structured pipeline for scraping insurer websites and producing validated, reproducible release bundles. | `a656596a` (canonical scraper workspace), `eb832076` (Phase 10 scrape data), `2eb203c6d97` (fix POSIX & regenerate fixtures), `9f821b0123` (docs consolidation). | Yes—scraper pipeline exists with deterministic curation, release bundles, promotion & rollback. | Third‑insurer expansion, automatic related‑link retrieval, Playwright live acquisition, and vector search integration deferred. |
| **10. Scraper ontology/tagger layer** | Added Pydantic models for scraper ontology contract, deterministic tagger that labels extracted FAQ pairs with concept IDs based on heuristics, golden corpus tests validating tags, and quality‑audit reports. | Prepared the ground for linking scraped content to ontology terms and evaluating annotation quality. | `a656596a` (ontology & tagger in scraper), `PHASE_4_IMPLEMENTATION_STATUS_AND_FORWARD_ROADMAP.md` (doc). | Partial—ontology contract and tagger exist; validated with tests. | Publication integration, FAQ mapping, retrieval usage, and vocabulary expansion remain deferred. |
| **11. CI, lint, formatting, and cross‑platform hardening** | Added Ruff configuration and `pytest` markers, cross‑platform normalisation of file paths and encoding, made tests skip by default for slow scrapers, improved error sanitisation and CORS, introduced GitHub Actions for lint & test gating, and added evaluation regression tests. | Ensured the repository is maintainable across environments and that quality gates prevent regressions. | `3544640e29` (scrape workspace hardening with Ruff), `2eb203c6d9` (POSIX tests & fixture regeneration), `8efe15d3dd` (cross‑platform normalisation), `2064b433` (eval gating), `ed7ab974` (CI & retrieval hardening). | Yes—CI pipeline enforces linting and tests across OSs. | None; improvements continue. |
| **12. Ontology registry and runtime ontology state** | Added core domain ontology schema and registry, discovered available ontologies, added `OntologyState` dataclass capturing version, registry details, and compatibility warnings. Integrated ontology state into runtime health and added admin endpoint to reload ontology. | Enabled the system to understand which ontologies are available and whether the current runtime is compatible, and to provide this information through the health endpoint. | `ca618f53` (Phase 16b schema & registry), `f2e2045e` (close compatibility & add OntologyState), `3f03c377` (expose state & reload endpoint), `52ccc599` (health payload improvements). | Yes—ontology registry and state exposed. | Full domain concept‑ID rollout and ontology‑driven ranking deferred. |
| **13. Main promotion, baseline preservation, and tagging** | Created a new branch `roadmap-ontology-organize` where the ontology and documentation work accumulated, then promoted it to `main`. Preserved the old server‑working baseline in tags and backup branches. Tagged `ontology-runtime-baseline-2026-07-04` for future reference. | Maintained a clear timeline and allowed users to access both the stable baseline and the new ontology runtime baseline. | `716e9b02` (merge promotion), tag creation, branch backup. | Yes—promotion completed and baseline preserved. | None. |
## Event: 2026-07-04 – Scraper pipeline narrative (deep review

##### 1. Purpose of the scraper subsystem

The `scrape/` workspace is a canonical subsystem designed to collect insurance‑related content from insurer websites (currently two: Asmari and Pasargad), curate it deterministically into clean FAQ pairs, package it into versioned release bundles, and promote these bundles to the chatbot runtime. The goal is to extend the knowledge base without manual entry while maintaining high quality and reproducibility.

##### 2. Workspace boundary

The `scrape/` directory is authoritative; an older snapshot at `0209-042926/scrape/` exists for reference but should not be modified. The canonical workspace contains acquisition code (`acquire`), extraction helpers (`extract`), curation scripts (`curation`), publication logic (`publication`), promotion CLI (`promotion`), ontology helpers (`ontology`), and schemas. It includes test fixtures and a comprehensive test suite with 232 passing tests.

##### 3. Supported insurer slice

Only two insurers are supported: Asmari and Pasargad. Each has dedicated extraction scripts that parse headings, paragraphs, lists, FAQ pairs, and related links. There is no live scraping beyond these sites, and a lock prevents Playwright‑based scraping; live tests are skipped by default.

##### 4. Acquisition layer

The acquisition module uses a simple HTTP fetcher to download static HTML pages. It does not execute JavaScript. The pipeline records related links but does not fetch them automatically. Playwright integration for dynamic pages exists behind a lock but is disabled until explicit approval.

##### 5. Extraction layer

Extraction helpers traverse HTML trees to identify headings, paragraphs, lists, and definition lists. FAQ pairs are detected by pattern matching (question prefix followed by answer blocks). The extraction outputs include the raw text and a trace of the DOM structure, enabling reproducibility. Extraction is deterministic; no AI heuristics are used.

##### 6. Deterministic curation layer

The curation layer deduplicates and normalises extracted content, removes boilerplate, converts Persian punctuation, and constructs `CuratedFAQ` objects. It supports prompts for manual review and can generate JSON fixtures for static tests. The CLI (`scrape/src/insurance_scraper/cli.py`) provides subcommands to run acquisition, extraction, curation, and generation of release bundles.

##### 7. Publication/release bundle layer

Curated FAQs are packaged into release bundles that include metadata (source URL, hash, version), curated content, and derived statistics. Validation scripts ensure schema compliance. Bundles are placed in `scrape/releases/` with version numbers and are accompanied by markdown reports summarising the release. These bundles are the only artefacts consumed by the runtime.

##### 8. FAQ import compatibility probe

Before promoting a release, a probe is run to check whether the release is compatible with the chatbot’s FAQ schema and retrieval pipeline. The probe ensures that new FAQs do not conflict with existing IDs, that answers are non‑empty, and that metadata is valid. Compatibility results are summarised in reports and exposed through CI.

##### 9. Promotion pipeline

The promotion CLI uploads a validated release bundle into a designated branch (`active_release`). Promotion creates a commit containing the new bundle and updates the `active_release_state.json` pointer. Only one active release is allowed at a time. Promotion is optional—maintainers must run the CLI intentionally. Rollback is provided by promoting the previous bundle.

##### 10. Rollback pipeline

Rollback commands revert the `active_release` branch to a previous release commit and update the runtime pointer. This ensures that if a release introduces problems, maintainers can quickly revert to a known good state. Rollbacks are logged with a reason field.

##### 11. FAQ runtime handoff

Once promoted, the release bundle is consumed by the runtime via the `active_release_loader`. The loader reads the bundle, validates its schema, and registers the FAQs into the runtime overlay. The overlay is read‑only; any attempt to modify or persist data at runtime fails. Overlay records are loaded into the runtime state but are **not FAISS‑indexed**; they are accessible only via direct ID lookup or fallback rules.

##### 12. Active‑release lookup‑only behavior

Active‑release records are intentionally excluded from vector search and ranking to avoid mixing experimental content with curated FAQs. When a user query matches an overlay FAQ ID or triggers a fallback, the overlay answer is returned. Otherwise, the system falls back to its base knowledge base. This ensures safety while enabling staged updates.

##### 13. Scraper ontology/tagger layer

Phase 4 introduced an ontology contract and a deterministic tagger. The tagger labels each extracted FAQ with concept IDs based on heuristics and a golden corpus. It generates annotation reports and quality metrics. This layer prepares scraped content for eventual integration with the broader ontology. Publication of tags and retrieval using them is **not implemented** yet.

##### 14. Validation and quality gates

The scraper subsystem includes extensive tests (232 passing) verifying extraction, curation, release creation, and ontology tagging. CI scripts run these tests and ensure that release bundles are reproducible. Additional quality gates check for missing fields, unusual text patterns, and non‑Persian content. Release and promotion are blocked if validation fails.

##### 15. Current constraints

- Only two insurers are supported; there is **no third‑insurer expansion**.
- Active‑release overlay is not vector‑indexed; semantic search across overlay content is deferred.
- Automatic fetching of related links is not implemented; they are recorded for manual follow‑up.
- Playwright live acquisition is disabled by default; manual enabling is required.
- Publication integration for ontology tags and FAQ mapping is deferred.
- Phases 4C–4F (ontology enrichment, retrieval integration, vocabulary expansion) remain future work.

##### 16. Future roadmap

The forward roadmap calls for expanded insurer support, integration of ontology tags into retrieval, mapping FAQs to domain concept IDs, enabling vector search over active‑release content, and completing phases 4C–4F. The roadmap emphasises that any expansion must maintain reproducibility and safety and must be explicitly authorised.
## Event: 2026-07-04 – Draft narrative v1

##### Executive summary

The InsuranceChatbot project evolved from a functional Phase 14 FAQ chatbot into an ontology‑aware, release‑managed platform. Starting with a server‑working FastAPI application capable of answering Persian insurance FAQs and performing calculations under Iranian insurance laws, the team embarked on a multi‑phase roadmap. Major achievements include building a deterministic insurer‑scraper pipeline, introducing release‑bundle promotion and rollback with rigorous validation, expanding the knowledge base with value‑reduction and Article 8 rules, consolidating third‑party ontologies, adding retrieval modes and evaluation gating, exposing ontology state in runtime health, and reorganising the repository for clarity. The resulting system balances innovation with caution: new knowledge can be staged as lookup‑only releases without affecting search ranking, and maintainers have clear tools to validate, promote, and roll back content. The project preserved the old baseline for stability while promoting an ontology runtime baseline that sets the stage for future semantic integrations.

##### Baseline transition

The Phase 14 **server‑working baseline** is preserved as `server-working-main-plus-gitignore-2026-07-04` (commit `f74cc4a7`). This baseline delivered a functioning FAQ chatbot with retrieval and calculator capabilities. After extensive development, the `roadmap-ontology-organize` branch was promoted into `main`, yielding the **ontology runtime baseline** at commit `716e9b02` (`ontology-runtime-baseline-2026-07-04`). The promotion process preserved the old baseline via a backup branch and tag while making the new ontology runtime the default line of development.

##### Engineering timeline

###### 1. Server‑working FAQ chatbot baseline

The early commits established the base functionality: a FastAPI application serving Persian insurance FAQs with retrieval modes and a calculator. Phase 14 delivered 554 FAQs, retrieval algorithms, an `insurance_rules.json` file defining variables and formulas, and endpoints for search, answer generation, and health checks. This baseline is retained as a tag for reference.

###### 2. Calculation and insurance‑rule expansion

Subsequent work expanded the calculator’s scope. New variables and formulas were added to support value reduction (افت قیمت), capture minimum and maximum coverage under Article 8, and address deadlines for Articles 33 and 34. The knowledge base was updated to include new FAQs explaining these concepts. Glossary and ontology files were synchronised to ensure variables, synonyms, and descriptions aligned.

###### 3. Third‑party insurance knowledge normalization

The team consolidated third‑party insurance knowledge into a coherent ontology. A glossary of 60 Persian terms was mapped to 38 variables across eight clusters, and a values matrix summarised coverage limits and coefficients. These artifacts ensure that the calculator and retrieval layer refer to consistent definitions and units.

###### 4. Scraper workspace and release pipeline

To scale the knowledge base responsibly, a canonical scraper subsystem was introduced. It supports static scraping of Asmari and Pasargad websites, deterministic extraction and curation, and packaging of release bundles with metadata. A promotion CLI allows maintainers to publish a release bundle to a special `active_release` branch after validation; rollback commands revert if needed. Tests (232) guarantee reproducibility, and documentation outlines the implementation and roadmap.

###### 5. Runtime artifact validation and active‑release safety

Alongside the scraper, runtime loaders were added to read release bundles, validate artifacts, and register them into a lookup‑only overlay. Branch quality checks and verification scripts ensure that only compliant releases are loaded. Active‑release FAQs do not participate in vector search; they are accessible only via direct lookups or fallback rules.

###### 6. Retrieval pipeline and evaluation

The retrieval system was upgraded to support TF‑IDF, embedding, and hybrid modes. Evaluation scripts measure recall and MRR, and CI gates ensure retrieval quality does not regress. The `build_response()` function now includes retrieval decisions in its output, and an intent router chooses between retrieval modes. A configurable minimum score and fallback threshold improve answer selection.

###### 7. Repository organization and documentation governance

Mid‑project, documentation and planning files were consolidated into `docs/organization/`. A reverse roadmap and dependency map provide newcomers with context. Archiving patterns and metadata flags highlight deprecated or investigated entries. This reorganisation improved maintainability without affecting runtime behavior.

###### 8. Ontology registry and compatibility layer

Phases 16a–16b introduced a core domain ontology schema and registry. An `OntologyState` dataclass captures the active ontology version, registry details, and compatibility warnings. The runtime exposes this state via the health endpoint and provides an admin endpoint to reload the ontology. The registry allows detection of missing or incompatible ontologies at startup.

###### 9. Runtime ontology health integration

Following the registry, the runtime integrated ontology health into its `/health` endpoint. When an ontology mismatch occurs, the system returns warnings but remains operational. Admins can reload the ontology state to apply updates. This integration lays the groundwork for concept‑ID‑driven retrieval and ranking.

###### 10. CI, lint, and promotion hardening

Throughout the timeline, the team improved CI pipelines by configuring Ruff for linting, ensuring cross‑platform path normalisation, skipping slow scraper tests by default, and adding retrieval evaluation as a gating step. Branch verification automation checks that new releases meet quality standards before promotion.

##### What changed technically

- Added retrieval modes (TF‑IDF, embedding, hybrid) with evaluation scripts and quality gates.
- Built a deterministic scraping and release pipeline with Asmari/Pasargad support, including acquisition, extraction, curation, publication, promotion, and rollback layers.
- Introduced runtime loaders and validators to safely load active‑release bundles into a lookup‑only overlay.
- Expanded `insurance_rules.json` and ontology to include value reduction formulas and Article 8 variables, and synchronised third‑party ontology and glossary.
- Added a Hazm‑based knowledge‑base validator and corrected stale or incomplete answers.
- Created an ontology registry, `OntologyState`, and admin reload endpoint.
- Improved CI with Ruff configuration, cross‑platform fixes, evaluation gating, and skip markers for slow tests.
- Consolidated documentation and added reverse roadmaps, dependency diagrams, and metadata flags for investigation.

##### What changed operationally

- Maintainers now have CLI tools to scrape insurer websites, curate content, generate release bundles, validate them, promote them, and roll them back.
- Active‑release content is loaded into runtime via a safe, lookup‑only overlay, ensuring new knowledge does not affect search ranking until explicitly integrated.
- Retrieval quality is monitored via evaluation scripts, and metrics (Recall@1/3, MRR) are used to gate changes.
- The runtime exposes ontology health and allows admin reloads, providing transparency into ontology compatibility.
- Documentation is better organised, enabling newcomers to understand the roadmap and dependency structure.

##### What is intentionally not included

- **No full FAQ remapping** to new domain concept IDs yet; the system still uses text‑based IDs.
- **No full domain_concept_id rollout** across retrieval or runtime; concept IDs exist only in planning and partial tagger.
- **No ontology‑driven ranking**; retrieval ranking is still heuristic/embedding based.
- **No active‑release searchability**; overlay records are not vector‑indexed.
- **No scraper runtime import into FAQ app**; scraped FAQs are delivered via release bundles, not fed into the live FAQ search.
- **No third‑insurer expansion yet**; only Asmari and Pasargad are implemented.
- **No Playwright‑dependent live acquisition path**; dynamic scraping remains disabled.

##### Practical impact

This evolution transforms the project from a static FAQ bot into a platform capable of controlled knowledge expansion. The deterministic scraper and release pipeline enable maintainers to add new content safely and reproducibly. Runtime validation ensures that unverified data never enters the search index. The integration of retrieval evaluation metrics provides objective quality measures, while ontology registry and health endpoints prepare the system for future concept‑driven features. Documentation reorganisation enhances maintainability, and the preservation of the Phase 14 baseline ensures a stable fallback. Overall, the project demonstrates disciplined engineering, balancing innovation with caution.

##### Next recommended branch

`phase-18-domain-concept-id-scaffold` — this branch should scaffold the rollout of domain concept IDs across FAQs, retrieval, and the scraper. It would implement concept‑driven ranking and complete the integration of ontology tags, enabling semantic search over both base and active‑release content.
## Event: 2026-07-04 – Self‑review table

| Area | Status | Fix needed |
|----|----|----|
| **Ref verification** | Completed—identified branches and tags, ensured main equals ontology baseline. | None |
| **Commit evidence collection** | Gathered major commits and extracted messages; used citations from docs to support claims. | None—minor commits (e.g., small lint fixes) not individually detailed but covered by CI theme. |
| **Theme grouping** | Developed 13 themes covering server baseline, scraper pipeline, validation, retrieval, ontology, etc. | Review whether any minor theme (e.g., evaluation gating) deserves more detail; overall grouping appears comprehensive. |
| **Scraper narrative** | Provided detailed 16‑point breakdown of scraper subsystem, citing docs and listing constraints. | None—ensured to highlight that overlay records are not FAISS‑indexed and that third‑insurer expansion is not implemented. |
| **Draft narrative** | Produced a coherent storyline connecting phases; emphasised baseline preservation, promotion, and future work. | Should ensure final outputs mention not exposing private commit history in the public snapshot. |
| **Planned vs. implemented** | Clearly labelled deferred items. | None |
## Event: 2026-07-04 – Final outputs

##### Output A — Private GitHub Release Narrative

**Title:** Ontology Runtime Baseline — 2026‑07‑04

**Overview**

This release promotes the `roadmap-ontology-organize` branch into `main`, establishing the **ontology runtime baseline** (`716e9b02`). It preserves the Phase 14 **server‑working baseline** via the `server-working-main-plus-gitignore-2026-07-04` tag (`f74cc4a7`) and backup branch. The promotion completes Phase 17 of the roadmap and prepares the project for ontology‑driven features.

**Highlights**

* **Scraper pipeline and release management:** Added a canonical `scrape/` workspace with deterministic acquisition, extraction, curation, publication, promotion, and rollback for Asmari and Pasargad sites. Release bundles include metadata and are validated before promotion. Active‑release records load into a lookup‑only overlay and do not participate in vector search.
* **Runtime validation:** Introduced `active_release_loader`, `branch_lookup`, and `decision_engine` modules to load and validate release bundles. Added CLI reports summarising branch compliance and tests to enforce quality gates.
* **Retrieval and evaluation:** Implemented TF‑IDF, hybrid, and embedding retrieval modes with evaluation scripts measuring recall and MRR. Integrated retrieval decisions into response generation and added gating to CI.
* **Knowledge base expansion:** Added value‑reduction formulas and Article 8 variables with corresponding FAQs and ontology updates. Consolidated third‑party ontology and glossary; synchronised variables and synonyms across eight clusters.
* **Ontology registry and health:** Added core domain ontology schema and registry, `OntologyState` dataclass, runtime health integration, and admin reload endpoint.
* **Documentation & organisation:** Consolidated planning files into `docs/organization/`, added reverse roadmaps and dependency graphs, introduced metadata flags for investigative FAQs, and reorganised archives without changing runtime behaviour.

**Not included**

- No domain concept ID rollout or ontology‑driven ranking.
- No vector search over active‑release overlay (lookup‑only mode remains).
- Scraped FAQs are not automatically imported into the FAQ app; they are available via release bundles only.
- Third‑insurer expansion and dynamic scraping (Playwright) remain future work.

**Future work**

- Implement domain concept ID scaffolding (`phase-18-domain-concept-id-scaffold`).
- Integrate ontology tags into retrieval and ranking.
- Expand scraper to additional insurers and enable dynamic page acquisition under controlled conditions.

##### Output B — Public Snapshot README Narrative

**Project snapshot (2026‑07‑04)**

This repository hosts a **clean snapshot** of the InsuranceChatbot as of 4 July 2026. It reflects the state of the public knowledge base and runtime code at that date, without exposing internal commit history. The snapshot is based on the **ontology runtime baseline** (commit `716e9b02`) and includes:

- A FastAPI application answering Persian insurance FAQs and performing basic calculations under Iranian insurance laws.
- Retrieval modes (TF‑IDF, embedding, hybrid) and evaluation scripts ensuring answer quality.
- A deterministic scraper subsystem supporting Asmari and Pasargad sites, with tools to produce release bundles; the scraper’s output is included as static data.
- A validated knowledge base covering third‑party insurance regulations, value reduction, and Articles 8, 32–34, with an aligned glossary and ontology.
- An ontology registry and runtime health endpoint summarising active ontologies.
- Documentation explaining how to use the API, build the project, and contribute.

**Excluded items**

- Internal planning documents and development history are omitted.
- Branch names and private tags are not present in the snapshot; only the final state is included.
- Active‑release records are provided as static data; they are not searchable by semantic vectors.

This snapshot is provided for transparency and archival purposes. It does not include unpublished future features or private branches.

##### Output C — Portfolio / Project Description

**InsuranceChatbot – A Structured Persian Insurance FAQ Bot with Safe Knowledge Expansion**

InsuranceChatbot is a Python‑based project that delivers a Persian question‑answering system and insurance calculator, focusing on Iranian third‑party regulations. It combines:

* **FastAPI runtime:** A web application serving search and calculation endpoints, with health checks and admin utilities. Users can ask insurance questions or compute compensation under Articles 8, 32–34, value reduction, and other rules.

* **Search and retrieval:** Multiple retrieval strategies (TF‑IDF, hybrid, embedding) select relevant FAQs. Evaluation scripts ensure high recall and mean reciprocal rank, and a Hazm‑based validator maintains quality in Persian.

* **Structured rules and ontology:** An `insurance_rules.json` defines variables and formulas, while an ontology registry tracks concept definitions and compatibility. An `OntologyState` object is exposed in runtime health and can be reloaded via admin endpoint.

* **Scraper release pipeline:** A deterministic scraping subsystem collects content from insurer websites (Asmari and Pasargad), curates it into clean FAQs, packages it into release bundles, and promotes bundles via CLI. Releases are validated and loaded into a lookup‑only overlay, ensuring that new knowledge does not affect search ranking until explicitly integrated.

* **Active‑release safety:** Release bundles are gated by tests and quality checks, and the runtime refuses to index them for vector search. Administrators can roll back releases if issues arise.

The project emphasises disciplined engineering, reproducibility, and safety over unchecked expansion. It is not a production SaaS but a research‑grade chatbot with careful validation and a clear roadmap for future semantic integration.

##### Output D — Commit Theme Table

| Theme | Representative commits | Summary | Implemented | Deferred |
|----|----|----|----|----|
| **Server‑working chatbot foundation** | `f74cc4a7`, `9b271597`, `1688c98b`, `c9e05fde`, `f5c1a132`, `4a6c614e`, `0d4818ca` | Baseline with retrieval, calculator, and core FAQs. | ✓ | Domain concept IDs. |
| **Repository and documentation organization** | `9f821b01`, `0a032f6f`, `bf6aedbb` | Consolidated docs, added reverse roadmap, metadata flags. | ✓ | Ongoing documentation updates. |
| **Runtime artifact validation** | `a8a2e2ed`, `ed7ab974` | Added active‑release loader, branch lookup, decision engine, and verification reports. | ✓ | Search indexing of overlay deferred. |
| **Retrieval pipeline and evaluation** | `1688c98b`, `9b271597`, `2064b433`, `ed7ab974` | Added retrieval modes, evaluation scripts, decision integration, and gating. | ✓ | Ontology‑driven ranking. |
| **Third‑party insurance knowledge consolidation** | `0d4818ca`, `c19b3caa` | Added glossary, ontology clusters, values matrix; synchronised variables. | ✓ | Expansion beyond first insurer. |
| **Value reduction & Article 8** | `f5c1a132`, `4a6c614e` | Added value‑reduction formulas, Article 8 variables, and FAQs. | ✓ | Integration into concept ID system. |
| **Persian KB validation** | `c9e05fde` | Added Hazm‑based KB validator and fixed content. | ✓ | Ongoing review. |
| **Active‑release safety & overlay** | `a656596a`, `a8a2e2ed`, `ed7ab974` | Implemented release pipeline, promotion, rollback, and lookup‑only overlay. | ✓ | Vector search over overlay. |
| **Scraper pipeline** | `a656596a`, `eb832076`, `2eb203c6d9` | Added deterministic scraping, curation, release bundling, promotion CLI, and tests. | ✓ | Third‑insurer expansion, Playwright, auto‑link fetch. |
| **Scraper ontology/tagger** | `a656596a` (ontology & tagger), docs | Added ontology contract and deterministic tagger with golden corpus. | Partial | Publication integration, retrieval using tags. |
| **CI, lint & hardening** | `3544640e29`, `2eb203c6d9`, `8efe15d3dd`, `2064b433` | Added Ruff, cross‑platform fixes, skip markers, evaluation gating. | ✓ | Continuous improvements. |
| **Ontology registry & runtime state** | `ca618f53`, `f2e2045e`, `3f03c377`, `52ccc599` | Added core domain ontology schema and registry, `OntologyState`, health integration, admin reload. | ✓ | Domain concept ID rollout. |
| **Main promotion & tagging** | `716e9b02` | Promoted `roadmap-ontology-organize` to `main` and tagged new baseline; preserved old baseline. | ✓ | — |

------------------------------------------------------------------------

---
