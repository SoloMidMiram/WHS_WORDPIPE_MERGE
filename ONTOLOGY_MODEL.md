# 🧬 Ontological Model



> **Purpose:** Formal entity-relationship model describing the project's structure, activity periods, claims, and evidence.

> **Date:** 1404-11-25 (2026-02-14)

> **Status:** Skeleton — ready for population



---



## 1. Methodology



### 1.1 Approach

The ontology is defined as a **lightweight entity-relationship schema** with:

- **Classes** (entity types) with attributes

- **Relations** (typed edges between classes)

- **Instances** (concrete entities populated from the project)



### 1.2 Proposed NLP/POS Pipeline (P2)

For future automated population:



```text

Source text (.md, .py, .jsonl, logs)

  -> Tokenizer (whitespace + punctuation)

  -> POS Tagger (spaCy / NLTK / regex-based)

  -> Entity Extractor (noun phrases, proper nouns)

  -> Relation Extractor (verb-phrase patterns: "produces", "consumes", "depends on")

  -> Ontology Populator (maps to class instances)

```



**Constraints:** Limited internet means offline-capable tools only (`nltk` with local data, or pure-Python regex extraction).



### 1.3 Manual Ground-Truth Phase

For Phase 1–2, the ontology is **manually curated** from:

- File system structure

- Existing `.md` docs (especially `docs/TOOLS_MODULES_INTEGRATION_REPORT.md`)

- Pipeline contracts (`tools/pipeline_contracts.py`)

- Git commit history (`git log`)



---



## 2. Class Hierarchy



### 2.1 Core Classes



```

Entity (abstract)

├── Artifact          # Any persistent file or data output

│   ├── Doc            # Markdown documentation

│   ├── SourceFile     # Python source code

│   ├── Evidence       # Pipeline output (logs, manifests, reports)

│   └── ConfigFile     # Configuration (.toml, .gitignore, .env.example)

├── ActivityPeriod     # A bounded span of work with a goal

│   ├── Phase          # Named project phase

│   └── Session        # Single work session (date-bound)

├── Claim              # A statement made in docs or code

│   ├── DesignClaim    # "X is designed to do Y"

│   ├── EvidenceClaim  # "The pipeline produces Z"

│   └── StatusClaim    # "Feature is complete"

├── Verification       # How a claim is checked

│   ├── Test           # Automated test (unittest)

│   ├── Command        # CLI command to run

│   └── Inspection     # Manual review

└── Role               # Who interacts with the system

    ├── Operator

    ├── Engineer

    └── Architect

```



### 2.2 Attribute Definitions



| Class | Attribute | Type | Description |

|-------|-----------|------|-------------|

| Artifact | `path` | Path (relative) | Location in repo |

| Artifact | `kind` | Enum | `source`, `doc`, `evidence`, `config` |

| Artifact | `produced_by` | Relation → ActivityPeriod | What work created it |

| Artifact | `consumed_by` | Relation → ActivityPeriod | What work reads it |

| Artifact | `verified_by` | Relation → Verification | How correctness is checked |

| ActivityPeriod | `name` | String | Short label |

| ActivityPeriod | `start_date` | Date (Jalali + Gregorian) | When it began |

| ActivityPeriod | `end_date` | Date (Jalali + Gregorian) | When it ended |

| ActivityPeriod | `goal` | String | What was to be achieved |

| ActivityPeriod | `claims` | Relation → Claim | What was claimed |

| ActivityPeriod | `results` | Relation → Artifact | What was produced |

| Claim | `text` | String | The assertion |

| Claim | `source` | Relation → Artifact | Where it's stated |

| Claim | `verified_by` | Relation → Verification | How to check |

| Claim | `status` | Enum | `true`, `false`, `untested`, `partial` |

| Verification | `method` | Enum | `test`, `command`, `inspection` |

| Verification | `command_or_path` | String | The test command or file to inspect |



---



## 3. Relations



| Relation | Domain | Range | Description |

|----------|--------|-------|-------------|

| `produces` | ActivityPeriod | Artifact | Work output |

| `consumes` | ActivityPeriod | Artifact | Work input |

| `states` | Artifact | Claim | A doc or code makes a claim |

| `verifies` | Verification | Claim | How a claim is checked |

| `verified_by` | Claim | Verification | Inverse of verifies |

| `depends_on` | Artifact | Artifact | Dependency between artifacts |

| `part_of` | ActivityPeriod | ActivityPeriod | Hierarchical (Session → Phase) |

| `precedes` | ActivityPeriod | ActivityPeriod | Temporal ordering |
| `is_duplicate_of` | Artifact | Artifact | Same name/content as another file |
| `wraps` | CompatibilityWrapper | Artifact | Re-exports from target module |
| `mirrors` | MirrorPair | Artifact | Active <-> Snapshot correspondence |
| `evolves_to` | VersionHistory | VersionHistory | Temporal ordering of versions |

| `is_duplicate_of` | Artifact | Artifact | Same name/content as another file |

| `wraps` | CompatibilityWrapper | Artifact | Re-exports from target module |

| `mirrors` | MirrorPair | Artifact | Active <-> Snapshot correspondence |

| `evolves_to` | VersionHistory | VersionHistory | Temporal ordering of versions |



---



## 4. Initial Instances (Seeded from Project)



### 4.1 Artifacts



| Name | Path | Kind | Produced By | Consumed By |

|------|------|------|-------------|-------------|

| ARCHITECTURE.md | `ARCHITECTURE.md` | Doc | Phase: Ground Truth | Operator, Engineer |

| WORKSPACE_OVERVIEW.md | `WORKSPACE_OVERVIEW.md` | Doc | Phase: Setup | Operator |

| Pipeline Runbook | `docs/PIPELINE_RUNBOOK.md` | Doc | Phase: Docs Pack | Operator |

| Tools Integration Report | `docs/TOOLS_MODULES_INTEGRATION_REPORT.md` | Doc | Phase: Docs Pack | Engineer |

| make_manifest.py | `tools/make_manifest.py` | Source | Phase: Pipeline | Stage 1 run |

| pipeline_contracts.py | `tools/pipeline_contracts.py` | Source | Phase: Contracts | All stages |

| manifest.jsonl | `_ARCHIVE/manifests/manifest.jsonl` | Evidence | make_manifest.py | plan_legacy_reorg.py |

| relocation_plan.jsonl | `_ARCHIVE/move_maps/relocation_plan.jsonl` | Evidence | plan_legacy_reorg.py | apply_legacy_reorg.py |

| relocation_map.jsonl | `_ARCHIVE/move_maps/relocation_map.jsonl` | Evidence | apply_legacy_reorg.py | build_legacy_index.py, verify_integrity.py |

| verify_report.json | `_ARCHIVE/logs/verify_report.json` | Evidence | verify_integrity.py | Operator review |
| categorize.py (archived) | `_ARCHIVE/pipeline-chronicle/tools/categorize.py` | Source | Phase 9 | Archived |
| ingest.py (archived) | `_ARCHIVE/pipeline-chronicle/tools/ingest.py` | Source | Phase 9 | Archived |
| merge.py (archived) | `_ARCHIVE/pipeline-chronicle/tools/merge.py` | Source | Phase 9 | Archived |
| ingest.py (current) | `tools/pipeline-chronicle/ingest.py` | Source | Phase 9 | chain.ps1, Operator |
| merge.py (current) | `tools/pipeline-chronicle/merge.py` | Source | Phase 9 | chain.ps1, Operator |
| verify_ingest.py | `tools/pipeline-chronicle/verify_ingest.py` | Source | Phase 9 | chain.ps1 |
| chronicle_tagged.md | `output/*/chronicle_tagged.md` | Evidence | categorize.py | index.py, operator review |
| tagged.json | `output/*/chronicle_tagged.tagged.json` | Evidence | categorize.py | index.py |
| event_index.md | `output/*/appendix/event_index.md` | Evidence | index.py | Operator review |
| theme_index.md | `output/*/appendix/theme_index.md` | Evidence | index.py | Operator review |
| source_manifest.md | `output/*/appendix/source_manifest.md` | Evidence | index.py | Operator review |
| link_registry.md | `output/*/appendix/link_registry.md` | Evidence | index.py | Operator review |
| themes.json | `pipeline/themes.json` | ConfigFile | Phase 9b | categorize.py |
| index_config.json | `pipeline/index_config.json` | ConfigFile | Phase 9b | index.py |
| categorize.py (current) | `pipeline/categorize.py` | Source | Phase 9b | chain.ps1 |
| index.py | `pipeline/index.py` | Source | Phase 9b | chain.ps1 |
| chain.ps1 | `pipeline/chain.ps1` | Source | Phase 9b | Operator |
| ARCHITECTURE_AND_MODULES.md | `ARCHITECTURE_AND_MODULES.md` | Doc | Phase 7 | Operator, Engineer, Architect |
| OBSOLETE_DOCS.md | `docs/OBSOLETE_DOCS.md` | Doc | Phase 7 | Operator, Engineer, Architect |



### 4.2 Duplicate Sets (Populated from Analysis)



| Set Name | Type | Canonical | Copies | Content Match |

|----------|------|-----------|--------|---------------|

| code_style.py | CompatibilityWrapper | wordpipe/code_style.py | wordpipe/pipeline/code_style.py | Different (wrapper) |

| orchestrator.py | CompatibilityWrapper | wordpipe/orchestrator.py | wordpipe/pipeline/orchestrator.py | Different (wrapper) |

| flattener/base.py | CompatibilityWrapper | wordpipe/adapters/flatteners/base.py | wordpipe/flatteners/base.py | Different (re-export) |

| flattener/com_flattener.py | CompatibilityWrapper | wordpipe/adapters/flatteners/com_flattener.py | wordpipe/flatteners/com_flattener.py | Different (re-export) |

| flattener/xml_flattener.py | CompatibilityWrapper | wordpipe/adapters/flatteners/xml_flattener.py | wordpipe/flatteners/xml_flattener.py | Different (re-export) |

| logging_tools.py | CompatibilityWrapper | wordpipe/logging_tools.py | wordpipe/ai/logging_tools.py | Different (wrapper) |

| __init__.py | MirrorPair | wordpipe/__init__.py | _WORK/snapshot/.../__init__.py | Different (diverged) |

| helpers.py | MirrorPair | wordpipe/ai/helpers.py | _WORK/snapshot/.../helpers.py | Identical |

| ailoader.py | MirrorPair | wordpipe/ai/ailoader.py | _WORK/snapshot/.../ailoader.py | Identical |

| AI helpers | VersionHistory | wordpipe/ai/helpers.py | 11 legacy snapshots | Various |



### 4.3 Activity Periods



| Name | Start | End | Goal |

|------|-------|-----|------|

| P0: Setup | 1404-08-?? | 1404-08-?? | Initial workspace creation, snapshot extraction |

| P1: Pipeline Contracts | 1404-10-?? | 1404-10-?? | Standardize stage interfaces with StageResult |

| P2: Docs Pack | 1404-11-20 | 1404-11-25 | Add ops manual, labor notes, module/package guide |

| P3: Security Hardening | 1404-11-22 | 1404-11-23 | Add secret scanner, env-only secrets policy |

| P4: Foundation Fixes | 1404-11-25 | 1404-11-25 | Fix absolute paths, verify doc accuracy |
| P7: Documentation Architecture | 1404-11-25 | 1404-11-25 | Create ARCHITECTURE_AND_MODULES.md, index obsolete docs |

| P5: Ontology & Journal (planned) | TBD | TBD | Build structured knowledge model |
| P8: Duplicate Analysis | 1404-11-25 | 1404-11-25 | Analyze all duplicates, apply standard headers |
| P9: Chronicle Pipeline Tools | 1404-11-25 | 1404-11-25 | Build ingest, verify, merge, categorize tools; archive to _ARCHIVE |
| P9b: Keyword Tuning & Index Builder | 1404-11-25 | 1404-11-25 | Tighten keywords, add negatives, build index.py, re-run pipeline |
| P9c: Reference Builder (planned) | TBD | TBD | Build reference.py, wire ontology, validate against manual merge |

| P8: Duplicate Analysis | 1404-11-25 | 1404-11-25 | Analyze all duplicates, apply standard headers |



### 4.3 Claims (Sample)



| # | Text | Source | Verified By | Status |

|---|------|--------|-------------|--------|

| C1 | "The pipeline has 5 stages: make_manifest, plan_legacy_reorg, apply_legacy_reorg, build_legacy_index, verify_integrity" | `docs/PIPELINE_RUNBOOK.md` | `ls tools/` + `--help` on each | ✅ true |

| C2 | "Stage scripts support `--workspace-root`, `--summary-json`, `--strict` flags" | `docs/TOOLS_MODULES_INTEGRATION_REPORT.md` | Run `python tools/make_manifest.py --help` | ✅ true |

| C3 | "verify reports are stable across machines" | `docs/PlansArchive/PLAN.md` | Run on two machines and compare | ❓ untested |

| C4 | "Core has zero runtime-heavy dependencies" | `ARCHITECTURE.md` | Inspect `wordpipe/core/__init__.py` imports | ✅ true (P0) |

| C5 | "The pipeline produces manifest.jsonl, relocation_plan.jsonl, relocation_map.jsonl" | `WORKSPACE_OVERVIEW.md` | Check `_ARCHIVE/` exists | ✅ true |
| C6 | "All 82 Python files have standard Jalali-date headers" | `tools/add_standard_headers.py` | Run `python tools/add_standard_headers.py --path .` | ✅ true |
| C7 | "45 files had duplicate headers which were cleaned" | `JOURNAL.md` (Period 8) | `Select-String "Created:" *.py` | ✅ true |
| C8 | "Active tree has 28 new modular architecture files not in snapshot" | `JOURNAL.md` (Period 8) | Diff active vs snapshot `wordpipe/` | ✅ true |
| C9 | "Git history spans only 3 days (2026-02-12 to 2026-02-14)" | `git log` | `git log --format="%h %ai %s"` | ✅ true |
| C10 | "Filesystem timestamps (2026-05-18) are snapshot artifacts" | `JOURNAL.md` (Period 8) | Compare git dates vs fs dates | ✅ true |
| C11 | "Keyword tightening + negative keywords reduce over-tagging from 29.5% to ≤18%" | `JOURNAL.md` (Period 9) | Re-run pipeline; inspect sidecar JSON | ✅ true (18.0%) |
| C12 | "False negatives eliminated — 100% coverage" | `JOURNAL.md` (Period 9) | Re-run pipeline; count untagged events | ✅ true (61/61) |
| C13 | "index.py generates 4 appendix files from tagged MD" | `JOURNAL.md` (Period 9) | Run index.py; check appendix/ directory | ✅ true |
| C14 | "index.py deduplicates events by title" | `JOURNAL.md` (Period 9) | Check dedup output (60→42 unique) | ✅ true |
| C15 | "index.py falls back to string formatting when Jinja2 is unavailable" | `JOURNAL.md` (Period 9) | Run without Jinja2; verify output | ✅ true |
| C16 | "categorize.py falls back to built-in defaults when config is missing" | `JOURNAL.md` (Period 9) | Run without --config; verify output | ✅ true |
| C17 | "ARCHITECTURE_AND_MODULES.md covers all 3 subsystems with complete module listings" | `ARCHITECTURE_AND_MODULES.md` | Read the doc; verify all modules listed | ✅ true |
| C18 | "Old docs in docs/ are accurately indexed as superseded vs preserved" | `docs/OBSOLETE_DOCS.md` | Cross-reference with docs/ directory listing | ✅ true |



---



## 5. Population Plan



### Phase A — Manual Curation (Immediate)

- [ ] Enumerate all artifacts (files) with `kind`, `produced_by`, `consumed_by`

- [ ] Extract claims from key `.md` files (ARCHITECTURE, runbook, labor report)

- [ ] Define verification commands for each claim



### Phase B — NLP-Assisted (P2)

- [ ] Evaluate offline POS taggers (NLTK `pos_tag`, spaCy `en_core_web_sm`)

- [ ] Build entity extractor for markdown headers + code blocks

- [ ] Build relation extractor for "produces/consumes" patterns

- [ ] Cross-validate against manual ground truth



### Phase C — Automation (Future)

- [ ] Auto-generate ontology instances from git history

- [ ] Auto-verify claims by running verification commands

- [ ] Link ontology to journal entries



---



## 6. Linking Convention (Ontology ↔ Journal ↔ Roadmap)



Each journal entry should:

1. Reference the **activity period** it belongs to

2. List **claims** made or verified during that period

3. Link to **artifacts** produced or consumed

4. Describe **verification** results



```

JOURNAL ENTRY EXAMPLE:



## Period: 1404-11-25 — Foundation Fixes

### Phase: P4 — Foundation Fixes

### Claims Addressed: C1, C2, C4

### Artifacts Produced: ROADMAP.md, ONTOLOGY_MODEL.md, JOURNAL.md, INDEX.md

### Verification:

  - C1: Confirmed by listing tools/ directory — 5 stage scripts exist ✅

  - C4: Inspected wordpipe/core/imports — no external dependencies ✅

### Result: Foundation for ontology established

```



---



## 7. Change Log



| Date (Gregorian) | Date (Jalali) | Change |

|------------------|---------------|--------|

| 2026-02-14 | 1404-11-25 | Initial skeleton created |
| 2026-02-14 | 1404-11-25 | Added DuplicateSet, MirrorPair, CompatibilityWrapper, VersionHistory classes |
| 2026-02-14 | 1404-11-25 | Populated DuplicateSet instances from analysis |
| 2026-02-14 | 1404-11-25 | Added claims C6-C10 from Period 8 |

| 2026-02-14 | 1404-11-25 | Added DuplicateSet, MirrorPair, CompatibilityWrapper, VersionHistory classes |

| 2026-02-14 | 1404-11-25 | Populated DuplicateSet instances from analysis |

| 2026-02-14 | 1404-11-25 | Added claims C6-C10 from Period 8 |

| 2026-02-14 | 1404-11-25 | Added DuplicateSet, MirrorPair, CompatibilityWrapper, VersionHistory classes |

| 2026-02-14 | 1404-11-25 | Populated DuplicateSet instances from analysis |

| 2026-02-14 | 1404-11-25 | Added claims C6�C10 from Period 8 |



