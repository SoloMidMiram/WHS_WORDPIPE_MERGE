# 📇 Project File Index

> **Purpose:** Curated map of canonical files, subsystems, evidence areas, and governance artifacts.
> **Generated:** 2026-02-14 (Jalali: 1404-11-25)
> **Last synchronized:** 2026-07-17 (Jalali: 1405-04-26)
> **Ontology Ref:** See `ONTOLOGY_MODEL.md` for entity classification.

---

## Legend

| Symbol | Kind | Description |
|--------|------|-------------|
| 📄 | Doc | Documentation (markdown) |
| 🐍 | Source | Python source code |
| 📊 | Evidence | Pipeline output (logs, manifests, reports) |
| ⚙️ | Config | Configuration file |
| 🗃️ | Archive | Historical / legacy content |
| 🔬 | Test | Unit test |

---

## Root

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `ARCHITECTURE_AND_MODULES.md` | 📄 Doc | Architecture reference | Comprehensive 3-subsystem reference (tools + chronicle + wordpipe) |
| `ROADMAP.md` | 📄 Doc | Roadmap | Phases, goals, constraints, milestones (newest-first) |
| `JOURNAL.md` | 📄 Doc | Journal | Dated period-based activity log with claims and verification |
| `ONTOLOGY_MODEL.md` | 📄 Doc | Ontology model | Entity-relationship model for the project |
| `INDEX.md` | 📄 Doc | File index | This file — full project file map |
| `PLAN.md` | 📄 Doc | Plan log | Immutable log of intentions and completions |
| `README.md` | 📄 Doc | Project entrypoint | Top-level README with quickstart |
| `ROOT_ORGANIZATION.md` | 📄 Doc | Root policy | Root allowlist, placement rules, evidence/output policy, and enforcement command |
| `REPO_ORGANIZATION_PLAN.md` | 📄 Doc | Organization plan | Historical modularization intent with current status annotations |
| `VERIFICATION.md` | 📄 Doc | Verification plan | Cross-reference factual claims against codebase evidence |
| `WORKSPACE_OVERVIEW.md` | 📄 Doc | Workspace manual | Copy-only merge workspace, inputs, outputs, evidence policy |
| `pyproject.toml` | ⚙️ Config | Package config | Project metadata, extras, build system |
| `.gitignore` | ⚙️ Config | Git ignore rules | Ignored patterns for pycache, secrets, environments |
| `.env.example` | ⚙️ Config | Environment template | Placeholder for env vars (no real keys) |
| `AGENTS.md` | 📄 Doc | Agent protocol | Evidence labels, context inspection, collision checks, and preservation rules |

### Archived Root Docs (moved to `_ARCHIVE/root-docs/`)

| Path | Kind | Role | Superseded By |
|------|------|------|---------------|
| `ROADMAP_1404-11-25.md` | 🗃️ Archive | Obsolete roadmap | `ROADMAP.md` |
| `ONTOLOGY.md` | 🗃️ Archive | Obsolete ontology | `ONTOLOGY_MODEL.md` |
| `ARCHITECTURE.md` | 🗃️ Archive | Obsolete architecture | `ARCHITECTURE_AND_MODULES.md` |
| `CODEX_LOG.md` | 🗃️ Archive | Obsolete action log | `JOURNAL.md` |
| `PATH_FIX_LOG.md` | 🗃️ Archive | Obsolete path fix log | `JOURNAL.md` |
| `PROJECT_INDEX.md` | 🗃️ Archive | Obsolete project index | `INDEX.md` |

---

## `docs/` — Documentation

### docs/ root

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `docs/README.md` | 📄 Doc | Docs entrypoint | Role-based reading paths, document map, artifact map |
| `docs/OBSOLETE_DOCS.md` | 📄 Doc | Obsolete docs index | Index of superseded vs preserved documentation |
| `docs/PIPELINE_RUNBOOK.md` | 📄 Doc | Operations runbook | Happy path, dry-run, stage-by-stage, failure triage |
| `docs/PIPELINE_CONTRACTS.md` | 📄 Doc | Engineering contract | Stage IO contracts, idempotency, portability |
| `docs/SECURITY_HARDENING.md` | 📄 Doc | Security policy | Env rules, scanning, incident response |
| `docs/TOOLS_MODULES_INTEGRATION_REPORT.md` | 📄 Doc | Module catalog | Full tools module catalog with args matrix |
| `docs/INTEGRATION_MAP_BEFORE_AFTER.md` | 📄 Doc | Integration map | Before/after data lineage and control flow |
| `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md` | 📄 Doc | Logic flow | TraceLedger-directed logic flow narrative |
| `docs/LABOR_REPORT.md` | 📄 Doc | Labor report | What work was done, frozen baseline, behavioral changes |
| `docs/REPOSITORY_REVIEW_MERGED_2026-02-13.md` | 📄 Doc | Review | Consolidated architecture review |
| `docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md` | 📄 Doc | Enhancement plan | Phased roadmap for TraceLedger alignment |
| `docs/TRACELEDGER_INTEGRATION_CONTRACT.md` | 📄 Doc | Integration contract | EventSink API, run report envelope |
| `docs/DOC_STYLE_GUIDE.md` | 📄 Doc | Style guide | Documentation conventions |
| `docs/DUPLICATE_POLICY.md` | 📄 Doc | Duplicate policy | Tiered duplicate governance |
| `docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md` | 📄 Doc | Performance template | Topic-neutral report run metrics and iteration checklist |
| `docs/PHASE13_GENERIC_TOPIC_REPORT_RUNNER_ROADMAP.md` | 📄 Doc | Phase roadmap | Generic topic runner, performance trends, and ontology-spine plan |
| `docs/PHASE14_SECOND_TOPIC_ONTOLOGY_READINESS.md` | 📄 Doc | Phase roadmap | Second-topic evidence, genericity remediation, and Phase 15 readiness |
| `docs/PHASE15_PROJECT_SEMANTIC_ONTOLOGY_DESIGN.md` | 📄 Doc | Phase design | Project Phase 15 provenance maturity levels and semantic decision gate |
| `docs/PHASE16_EVENT_IDENTITY_AND_SECTION_PROVENANCE.md` | 📄 Doc | Phase design | Section→SourceEvent→ReportEvent sidecars and ontology migration gate |
| `docs/PHASE17_EVENT_PROVENANCE_SURVIVOR_AND_REPEATABILITY.md` | 📄 Doc | Phase design | Survivor integrity and Phase 16↔17 stable-id gate |

### docs/architecture/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `docs/architecture/README.md` | 📄 Doc | Architecture entry | TraceLedger alignment, modularity direction |
| `docs/architecture/PROJECT_SUMMARY.md` | 📄 Doc | Project summary | Whole-project boundaries, data flow, control flow |

### docs/engineering/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `docs/engineering/README.md` | 📄 Doc | Engineering entry | Changing pipeline stages, verifying contracts |
| `docs/engineering/MODULES_PACKAGES.md` | 📄 Doc | Modules guide | Import rules, DI model, package patterns |
| `docs/engineering/CHRONICLE_CANONICAL_DECISION.md` | 📄 Doc | chronicle decision | Canonical source location for chronicle pipeline logic |
| `docs/engineering/REPOSITORY_BOUNDARIES.md` | 📄 Doc | Boundary guide | Directory classification, packaging and pytest rules, import boundaries |
| `docs/engineering/P0_P2_VALIDATION_REPORT.md` | 📄 Doc | Validation report | P0–P2 remediation stages, claim register, CI readiness (2026-07-09) |
| `docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md` | 📄 Doc | Alignment audit | Phase-by-phase evidence labels, corrected flaw claims, and outstanding architecture debt |
| `docs/engineering/PHASE13_17_COMMIT_DRAFT.md` | 📄 Doc | Commit draft | Verified working-tree scope, Phase 13–17 trace map, staging boundaries, and commit messages |

### docs/operations/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `docs/operations/README.md` | 📄 Doc | Operations entry | Running and triaging the pipeline |
| `docs/operations/MANUAL.md` | 📄 Doc | Operations manual | Quickstart, inputs/outputs, troubleshooting |
| `docs/operations/LABOR.md` | 📄 Doc | Labor notes | Ops-facing labor notes, commit anchors, baseline |

### docs/PlansArchive/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `docs/PlansArchive/PLAN.md` | 📄 Doc | Archived plan | Merge reviews + TraceLedger-ready debug/enhancement roadmap |
| `docs/PlansArchive/Merge Reviews + TraceLedger-Ready Debug-Enhancement Roadmap.md` | 📄 Doc | Archived plan | Same content (duplicate — preserve for audit) |

---

## `tools/` — Evidence Pipeline

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `tools/make_manifest.py` | 🐍 Source | Stage 1 | Generate manifest from snapshot |
| `tools/plan_legacy_reorg.py` | 🐍 Source | Stage 2 | Build relocation plan |
| `tools/apply_legacy_reorg.py` | 🐍 Source | Stage 3 | Apply relocation (copy-only, conflict-safe) |
| `tools/build_legacy_index.py` | 🐍 Source | Stage 4 | Generate legacy index docs |
| `tools/verify_integrity.py` | 🐍 Source | Stage 5 | Verify integrity, consistency, immutability |
| `tools/orchestrate.py` | 🐍 Source | Orchestrator | One-command pipeline runner |
| `tools/route_unmapped_misc.py` | 🐍 Source | Auxiliary | Route snapshot docs to _META |
| `tools/pipeline_contracts.py` | 🐍 Source | Shared lib | StagePaths, StageResult, StageError |
| `tools/tool_common.py` | 🐍 Source | Shared lib | Hash, path, copy, log utilities |
| `tools/jalali.py` | 🐍 Source | Shared lib | Gregorian-to-Jalali conversion |
| `tools/docs_link_check.py` | 🐍 Source | Validation | Check doc cross-references |
| `tools/security_scan.py` | 🐍 Source | Validation | High-confidence secret pattern scanning |
| `tools/check_root_layout.py` | 🐍 Source | Validation | Enforce the documented repository-root allowlist |
| `tools/check_input_catalog.py` | 🐍 Source | Validation | Validate canonical input layout, hashes, duplicate declarations, and legacy-path absence |
| `tools/check_architecture_boundaries.py` | 🐍 Source | Validation | Enforce narrow static production import directions with a reviewed path-role registry; no active v1 bypasses |
| `tools/prepare_insurancechatbot_chronicle.py` | 🐍 Source | Topic adapter | Converts InsuranceChatbot commit/roadmap/digest Markdown into Chronicle-compatible staged events and run summaries |
| `tools/prepare_generic_markdown_chronicle.py` | 🐍 Source | Topic adapter | Converts `##` Markdown sections into dated Chronicle events |
| `tools/run_topic_report.py` | 🐍 Source | Topic runner | Manifest-driven prepare/pipeline/summarize/trend/ontology orchestration with prepare-metrics contract and lineage-aware attribution |
| `tools/compare_event_provenance_stability.py` | 🐍 Source | Provenance check | Compares Phase 16/17 SourceEvent and ReportEvent mappings and writes only to a separately reserved evidence directory |

---

## `wordpipe/` — Runtime Library

### wordpipe/ root

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/__init__.py` | 🐍 Source | Public API | `process_docx_v3`, `PipelineConfig`, `RunReport` exports |
| `wordpipe/code_style.py` | 🐍 Source | Style | Code block styling — **has duplicate `style_code_blocks()` def** |
| `wordpipe/logging_tools.py` | 🐍 Source | Logging | Logger setup, JSONL output — **has duplicate imports, fragile mkdir** |
| `wordpipe/orchestrator.py` | 🐍 Source | Orchestrator | `process_docx_v3` — **mixes flatten, style, segment, save, TOC** |
| `wordpipe/events.py` | 🐍 Source | Events | EventSink Protocol + StdlibLoggerSink + JsonlSink |

### wordpipe/core/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/core/__init__.py` | 🐍 Source | Core init | Core package exports |
| `wordpipe/core/datatypes.py` | 🐍 Source | Data types | PipelineConfig, RunReport |
| `wordpipe/core/ooxml.py` | 🐍 Source | OOXML | OOXML utilities |
| `wordpipe/core/segment.py` | 🐍 Source | Segmentation | Heading-based segmenter — **O(n²) worst case** |
| `wordpipe/core/styles.py` | 🐍 Source | Styles | Style constants and helpers |

### wordpipe/ai/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/ai/__init__.py` | 🐍 Source | Deprecated stub | Emits `DeprecationWarning`; no script modules remain |
| `wordpipe/ai/run.MD` | 📄 Doc | Run notes | Points to `scripts/ai/` for manual commands |

> Script-style modules (`ailoader.py`, `canary_test.py`, `helpers.py`, etc.) were moved to `scripts/ai/`. See `docs/engineering/MODULES_PACKAGES.md` AI Boundary section.

### wordpipe/adapters/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/adapters/__init__.py` | 🐍 Source | Adapters init | Adapter package exports |
| `wordpipe/adapters/defaults.py` | 🐍 Source | Defaults | Default adapter wiring |
| `wordpipe/adapters/transforms.py` | 🐍 Source | Transforms | Document transformations |

### wordpipe/adapters/ai/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/adapters/ai/__init__.py` | 🐍 Source | AI adapters init | AI adapter exports |
| `wordpipe/adapters/ai/dummy.py` | 🐍 Source | Dummy AI | No-op AI provider for testing |
| `wordpipe/adapters/ai/openai_summarizer.py` | 🐍 Source | OpenAI | OpenAI-based summarization adapter |

### wordpipe/adapters/docx/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/adapters/docx/__init__.py` | 🐍 Source | DOCX adapters init | DOCX adapter exports |
| `wordpipe/adapters/docx/io.py` | 🐍 Source | DOCX IO | DOCX reader/writer |
| `wordpipe/adapters/docx/segmenter.py` | 🐍 Source | DOCX segmenter | DOCX-specific segmentation |
| `wordpipe/adapters/docx/styler.py` | 🐍 Source | DOCX styler | DOCX styling adapter |

### wordpipe/adapters/flatteners/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/adapters/flatteners/__init__.py` | 🐍 Source | Flattener init | Flattener adapter exports |
| `wordpipe/adapters/flatteners/base.py` | 🐍 Source | Base flattener | Abstract flattener interface |
| `wordpipe/adapters/flatteners/com_flattener.py` | 🐍 Source | COM flattener | Windows COM-based flattener |
| `wordpipe/adapters/flatteners/xml_flattener.py` | 🐍 Source | XML flattener | XML-based flattener |

### wordpipe/cli/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/cli/__init__.py` | 🐍 Source | CLI init | CLI package exports |
| `wordpipe/cli/__main__.py` | 🐍 Source | CLI main | `python -m wordpipe` entry |
| `wordpipe/cli/main.py` | 🐍 Source | CLI main | `wordpipe` console script |

### wordpipe/flatteners/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/flatteners/__init__.py` | 🐍 Source | Flatteners init | Flattener package exports |
| `wordpipe/flatteners/base.py` | 🐍 Source | Flattener base | Abstract flattener (legacy compat) |
| `wordpipe/flatteners/com_flattener.py` | 🐍 Source | COM flattener | COM flattener (legacy compat) |
| `wordpipe/flatteners/xml_flattener.py` | 🐍 Source | XML flattener | XML flattener (legacy compat) |

### wordpipe/interfaces/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/interfaces/__init__.py` | 🐍 Source | Interfaces init | Interface package exports |
| `wordpipe/interfaces/ai.py` | 🐍 Source | AI interface | AI service contract |
| `wordpipe/interfaces/config.py` | 🐍 Source | Config interface | Config provider contract |
| `wordpipe/interfaces/documents.py` | 🐍 Source | Document interface | Document reader/writer contracts |
| `wordpipe/interfaces/logging.py` | 🐍 Source | Logging interface | Logger contract |
| `wordpipe/interfaces/transforms.py` | 🐍 Source | Transforms interface | Transform contract |

### wordpipe/legacy/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/legacy/LEGACY_INDEX.md` | 📄 Doc | Legacy index | Legacy file index for wordpipe/ |
| `wordpipe/legacy/ai/` | 🗃️ Archive | Legacy AI | Legacy AI module snapshots |
| `wordpipe/legacy/misc/` | 🗃️ Archive | Legacy misc | Miscellaneous legacy files |

### wordpipe/orchestration/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/orchestration/__init__.py` | 🐍 Source | Orchestration init | Orchestration package exports |
| `wordpipe/orchestration/pipeline.py` | 🐍 Source | Pipeline | WordPipePipeline runner |

### wordpipe/pipeline/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/pipeline/code_style.py` | 🐍 Source | Pipeline style | Pipeline-specific code style (compat) |
| `wordpipe/pipeline/orchestrator.py` | 🐍 Source | Pipeline orchestrator | Pipeline orchestrator (compat) |

### wordpipe/plugins/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/plugins/__init__.py` | 🐍 Source | Plugins init | Plugin package exports |
| `wordpipe/plugins/registry.py` | 🐍 Source | Plugin registry | Dynamic capability registration |

### wordpipe/chronicle/

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `wordpipe/chronicle/__init__.py` | 🐍 Source | Package init | Re-exports ingest/merge/categorize public API |
| `wordpipe/chronicle/ingest.py` | 🐍 Source | Ingest logic | Pure functions for raw MD normalisation |
| `wordpipe/chronicle/merge.py` | 🐍 Source | Merge logic | Pure functions for merge, dedup, conflict resolution |
| `wordpipe/chronicle/categorize.py` | 🐍 Source | Categorize logic | v2 theme tagging with negative keywords |
| `wordpipe/chronicle/verify_ingest.py` | 🐍 Source | Verify logic | Batch ingest verification (parse, classify, report) |
| `wordpipe/chronicle/models.py` | 🐍 Source | Data models | ChronicleEvent, NormalisedDocument, MergeResult |
| `wordpipe/chronicle/io.py` | 🐍 Source | I/O helpers | UTF-8 read/write helpers |
| `wordpipe/chronicle/cli/__init__.py` | 🐍 Source | CLI init | CLI package init |
| `wordpipe/chronicle/cli/ingest.py` | 🐍 Source | Ingest CLI | CLI wrapper delegating to wordpipe.chronicle.ingest |
| `wordpipe/chronicle/cli/merge.py` | 🐍 Source | Merge CLI | CLI wrapper delegating to wordpipe.chronicle.merge |
| `wordpipe/chronicle/cli/categorize.py` | 🐍 Source | Categorize CLI | CLI wrapper delegating to wordpipe.chronicle.categorize |
| `wordpipe/chronicle/cli/verify_ingest.py` | 🐍 Source | Verify CLI | CLI wrapper delegating to wordpipe.chronicle.verify_ingest |

> Canonical chronicle implementation. See `docs/engineering/CHRONICLE_CANONICAL_DECISION.md`.

---

## `inputs/` — Canonical Corpus Inputs

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `inputs/catalog.json` | ⚙️ Config | Provenance catalog | SHA-256, size, corpus, format, and source classification for 19 active inputs |
| `inputs/chatgpt-chronicle/markdown/` | 📊 Evidence | Source corpus | Established 16-file Chronicle input set; duplicate/derived members remain catalogued |
| `inputs/insurancechatbot/markdown/` | 📊 Evidence | Source corpus | Three sources consumed by the InsuranceChatbot adapter |
| `inputs/README.md` | 📄 Doc | Input policy | Canonical placement and source-DOCX policy |

---

## `WordHorrorStories/` — Content Archive

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `WordHorrorStories/autobiography/` | 🗃️ Archive | Content | Autobiography content |
| `WordHorrorStories/chatgpt-chronicle/` | 🗃️ Archive | Content | ChatGPT chronicle book, source-disposition notes, and appendix; active inputs are under `inputs/` |
| `WordHorrorStories/insurancechatbot/` | 📊 Evidence | Topic run | InsuranceChatbot manifest, theme config, staged report outputs, and performance summaries |
| `WordHorrorStories/pipelinechronicle/` | 📊 Evidence | Topic run | Second-topic manifest, themes, controlled runs, attribution, trends, and ontology evidence |
| `WordHorrorStories/instructions/` | 🗃️ Archive | Content | Instructions |
| `WordHorrorStories/legacy/` | 🗃️ Archive | Legacy | Legacy content from WHS |
| `WordHorrorStories/legacy/LEGACY_INDEX.md` | 📄 Doc | Legacy index | Legacy file index for WHS |
| `WordHorrorStories/reports/` | 🗃️ Archive | Reports | WHS reports |

---

## `_ARCHIVE/` — Pipeline Evidence

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `_ARCHIVE/manifests/manifest.jsonl` | 📊 Evidence | Manifest | File inventory with hashes |
| `_ARCHIVE/manifests/manifest.csv` | 📊 Evidence | Manifest | CSV version of manifest |
| `_ARCHIVE/move_maps/relocation_plan.jsonl` | 📊 Evidence | Plan | Planned legacy moves |
| `_ARCHIVE/move_maps/relocation_map.jsonl` | 📊 Evidence | Map | Applied relocation results |
| `_ARCHIVE/logs/plan.log` | 📊 Evidence | Log | Planning audit trail |
| `_ARCHIVE/logs/apply_reorg.log` | 📊 Evidence | Log | Apply audit trail |
| `_ARCHIVE/logs/legacy_index.log` | 📊 Evidence | Log | Index generation audit |
| `_ARCHIVE/logs/conflicts.log` | 📊 Evidence | Log | Copy conflict log |
| `_ARCHIVE/logs/route_unmapped.log` | 📊 Evidence | Log | Route unmapped audit |
| `_ARCHIVE/logs/verify_report.md` | 📊 Evidence | Report | Verification report (human) |
| `_ARCHIVE/logs/verify_report.json` | 📊 Evidence | Report | Verification report (machine) |
| `_ARCHIVE/logs/consistency_report.json` | 📊 Evidence | Report | Consistency check |
| `_ARCHIVE/logs/immutability_report.json` | 📊 Evidence | Report | Immutability check |
| `_ARCHIVE/raw_zips/` | 🗃️ Archive | Raw | Original snapshot zips |
| `_ARCHIVE/evidence/generated-reports/` | 📊 Evidence | Generated reports | Preserved DOCX reports formerly placed at repository root |

---

## `_WORK/` — Working Trees

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `_WORK/snapshot/` | 🗃️ Archive | Snapshot | Immutable snapshot input (extracted zip) |

---

## `_META/` — Meta Files

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `_META/from_snapshot_20260211_205716/README.md` | 📄 Doc | Meta | Snapshot README |
| `_META/from_snapshot_20260211_205716/MERGE_MAP.md` | 📄 Doc | Meta | Snapshot merge map |

---

## `_SECURITY/` — Security

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `_SECURITY/scan_reports/` | 🗃️ Archive | Scans | Secret scan reports (gitignored) |

---

## `_INBOX/` — Inbox

| Path | Kind | Role | Description |
|------|------|------|-------------|
| _(empty)_ | | | Reserved for incoming files |

---

## `pipeline/` — Chronicle Pipeline (Generation 3)

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `pipeline/categorize.py` | 🐍 Source | Wrapper | Thin wrapper delegating to wordpipe.chronicle.categorize (v2) **DEPRECATED** |
| `pipeline/index.py` | 🐍 Source | Stage 5 | Generate 4 appendix files with Jinja2 + fallback |
| `pipeline/ingest.py` | 🐍 Source | Wrapper | Thin wrapper delegating to wordpipe.chronicle.ingest **DEPRECATED** |
| `pipeline/merge.py` | 🐍 Source | Wrapper | Thin wrapper delegating to wordpipe.chronicle.merge **DEPRECATED** |
| `pipeline/verify_ingest.py` | 🐍 Source | Wrapper | Thin wrapper delegating to wordpipe.chronicle.verify_ingest **DEPRECATED** |
| `pipeline/chain.ps1` | 🐍 Source | Orchestrator | 5-stage PowerShell orchestrator (v2) |
| `pipeline/themes.json` | ⚙️ Config | Theme config | 6 themes, 62 positive + 16 negative keywords |
| `pipeline/index_config.json` | ⚙️ Config | Index config | Configurable output dir, templates dir, dedup |
| `pipeline/templates/` | ⚙️ Config | Jinja2 templates | 4 templates (event_index, theme_index, source_manifest, link_registry) |
| `pipeline/CODEX_WORKING.md` | 📄 Doc | Codex reference | Working code reference with evolution timeline and known issues |
| `pipeline/README.md` | 📄 Doc | Pipeline quickstart | Quickstart reference and file inventory |

### Chronicle Pipeline — Archived (Generation 1/2)

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `tools/pipeline-chronicle/ingest.py` | 🐍 Source | Wrapper (v1) | Thin wrapper delegating to wordpipe.chronicle.ingest **DEPRECATED** |
| `tools/pipeline-chronicle/merge.py` | 🐍 Source | Wrapper (v1) | Thin wrapper delegating to wordpipe.chronicle.merge **DEPRECATED** |
| `tools/pipeline-chronicle/verify_ingest.py` | 🐍 Source | Wrapper (v1) | Thin wrapper delegating to wordpipe.chronicle.verify_ingest **DEPRECATED** |
| `tools/pipeline-chronicle/categorize.py` | 🐍 Source | Wrapper (v1) | Thin wrapper delegating to wordpipe.chronicle.categorize **DEPRECATED** |
| `tools/pipeline-chronicle/chain.ps1` | 🐍 Source | Orchestrator (v1) | Original v1 (4-stage, no index) |
| `_ARCHIVE/pipeline-chronicle/tools/` | 🗃️ Archive | All 5 tools | Frozen copy at archive time |
| `_ARCHIVE/pipeline-chronicle/ARCHIVE_REPORT.md` | 📄 Doc | Archive report | Full documentation of archived tools |
| `_ARCHIVE/pipeline-chronicle/notes/ingest_design_notes.md` | 🗃️ Archive | Design notes | Markdown design doc originally misnamed as `tools/ingest.py` |
| `_ARCHIVE/evidence/chronicle_review/` | 📊 Evidence | Pipeline output | First pipeline run (21:40): normalised/*.md, merged.md, chronicle_tagged.md |
| `_ARCHIVE/evidence/chronicle_v2/` | 📊 Evidence | Pipeline output | Second pipeline run (22:38-53): normalised/*.md, chronicle_tagged.md, appendix/*.md |
| `_ARCHIVE/root-docs/` | 🗃️ Archive | Archived root docs | 6 superseded root .md files (see `_ARCHIVE/root-docs/ARCHIVE_INDEX.md`) |

---

## `tests/` — Tests

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `tests/test_import_safety.py` | 🔬 Test | Import safety | Verifies wordpipe imports succeed without optional deps |
| `tests/test_pipeline_chronicle.py` | 🔬 Test | chronicle regression | 59 tests for ingest/merge/categorize/verify logic |
| `tests/test_prepare_insurancechatbot_chronicle.py` | 🔬 Test | topic adapter | Verifies commit heading parsing, fallback dates, mojibake cleanup, and staged-event compatibility |
| `tests/test_prepare_generic_markdown_chronicle.py` | 🔬 Test | topic adapter | Verifies `##` event boundaries, date headings, generic summaries, and ingest compatibility |
| `tests/test_run_topic_report.py` | 🔬 Test | topic runner | Manifest, registry, metrics contract, lineage attribution, trends, and ontology evidence |
| `tests/test_root_layout.py` | 🔬 Test | governance | Verifies the root allowlist and rejection of misplaced outputs |
| `tests/test_input_catalog.py` | 🔬 Test | governance | Verifies input hashes, layout, legacy-path prevention, and catalog completeness |
| `tests/test_architecture_boundaries.py` | 🔬 Test | architecture | Verifies current-tree boundaries, forbidden edges, path-role registry behavior, and TYPE_CHECKING exclusions |
| `tests/test_phase16_event_identity_characterization.py` | 🔬 Test | event identity | Characterizes Chronicle event extraction, normalization, hashing, and keep-both behavior |
| `tests/test_phase16_event_lineage_runner.py` | 🔬 Test | event provenance | Verifies event-lineage preparation, runner gates, correlation, and summaries |
| `tests/test_phase17_survivor_verification.py` | 🔬 Test | survivor integrity | Verifies merge-note-aware actual survivor membership and fail-closed ambiguity handling |
| `tests/test_phase17_provenance_stability.py` | 🔬 Test | repeatability | Verifies stable-id comparison, drift reporting, collision protection, and comparator exits |
| `tests/README.md` | 📄 Doc | Test readme | Authoritative test run instructions |

## `scripts/` — Executable Scripts (not packaged)

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `scripts/ai/canary_openai.py` | 🐍 Source | OpenAI canary | API connectivity/latency test (run directly, not via pytest) |
| `scripts/ai/one_openai_api.py` | 🐍 Source | OpenAI CLI | Multi-mode OpenAI Responses API script |
| `scripts/ai/helpers.py` | 🐍 Source | AI helpers | Legacy script helpers (sibling imports) |
| `scripts/ai/reorganize.py` | 🐍 Source | AI reorganize | Legacy DOCX reorganize experiment |
| `scripts/ai/ailoader.py` | 🐍 Source | AI loader | Legacy provider loader script |
| `scripts/verify_changes.py` | 🐍 Source | Verification | Change verification utility |
| `scripts/reporting/` | 🐍 Source | Report utilities | DOCX builders and diagnostics formerly stored in `_scripts/`; outputs default to `_WORK/generated-reports/` |

---

## `REVIEW_EVALUATION.md` — Codex PR Artifact

| Path | Kind | Role | Description |
|------|------|------|-------------|
| `REVIEW_EVALUATION.md` | 📄 Doc | Review | Codex branch PR #1 review (not in main — see `codex/` branch) |

---

## Change Log

| Date (Gregorian) | Date (Jalali) | Change |
|------------------|---------------|--------|
| 2026-07-17 | 1405-04-26 | Added the Phase 13–17 working-tree commit draft and synchronized implementation, test, and evidence mappings |
| 2026-07-17 | 1405-04-26 | Added Phase 17 survivor integrity (`merged-note-aware-v1`) and Phase 16↔17 stable-id evidence |
| 2026-07-17 | 1405-04-26 | Added Phase 16 section provenance sidecars (`event-lineage-v1` / `event-correlation-v1`) and controlled-run evidence |
| 2026-07-16 | 1405-04-25 | Added InsuranceChatbot topic adapter evidence, iterative performance check template, and docs sync for 200-event report run |
| 2026-07-16 | 1405-04-25 | Added Phase 14 alignment audit and root organization enforcement; moved report scripts/outputs to owned directories |
| 2026-07-17 | 1405-04-26 | Added Phase 15 provenance closeout, canonical input catalog, collision guard, and agent evidence protocol |
| 2026-02-14 | 1404-11-25 | Added pipeline/ section (Phase 9b: 11 files + 4 templates); archived 6 superseded root docs to _ARCHIVE/root-docs/; added docs/OBSOLETE_DOCS.md; added VERIFICATION.md, WORKSPACE_OVERVIEW.md |
| 2026-02-14 | 1404-11-25 | Initial index created |

---

## See Also

- [ROADMAP.md](ROADMAP.md) — Project goals and phases
- [JOURNAL.md](JOURNAL.md) — Activity log with claims and verification
- [ONTOLOGY_MODEL.md](ONTOLOGY_MODEL.md) — Formal entity model
- [docs/README.md](docs/README.md) — Documentation entrypoint
- [docs/engineering/REPOSITORY_BOUNDARIES.md](docs/engineering/REPOSITORY_BOUNDARIES.md) — Directory classification and import boundaries
- [docs/engineering/P0_P2_VALIDATION_REPORT.md](docs/engineering/P0_P2_VALIDATION_REPORT.md) — P0–P2 remediation validation (2026-07-09)
