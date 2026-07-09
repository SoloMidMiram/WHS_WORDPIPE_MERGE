# Architecture, Modules & Integration Reference

> **Purpose:** Comprehensive reference documenting all three subsystems — their architecture, module responsibilities, data flow, logic flow, goals, and constraints.
> **Date:** 2026-02-14 (Jalali: 1404-11-25)
> **Supersedes:** `docs/architecture/PROJECT_SUMMARY.md`, `docs/TOOLS_MODULES_INTEGRATION_REPORT.md`, `docs/INTEGRATION_MAP_BEFORE_AFTER.md`

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Subsystem A: Chronicle Pipeline (`pipeline/`)](#2-subsystem-a-chronicle-pipeline-pipeline)
   - 2.1 [Architecture](#21-architecture)
   - 2.2 [Modules](#22-modules)
   - 2.3 [Data Flow](#23-data-flow)
   - 2.4 [Logic Flow](#24-logic-flow)
   - 2.5 [Goals & Constraints](#25-goals--constraints)
3. [Subsystem B: Evidence Pipeline (`tools/`)](#3-subsystem-b-evidence-pipeline-tools)
   - 3.1 [Architecture](#31-architecture)
   - 3.2 [Modules](#32-modules)
   - 3.3 [Data Flow](#33-data-flow)
   - 3.4 [Logic Flow](#34-logic-flow)
   - 3.5 [Goals & Constraints](#35-goals--constraints)
4. [Subsystem C: WordPipe Runtime (`wordpipe/`)](#4-subsystem-c-wordpipe-runtime-wordpipe)
   - 4.1 [Architecture](#41-architecture)
   - 4.2 [Modules](#42-modules)
   - 4.3 [Data Flow](#43-data-flow)
   - 4.4 [Logic Flow](#44-logic-flow)
   - 4.5 [Goals & Constraints](#45-goals--constraints)
5. [Cross-Subsystem Integration](#5-cross-subsystem-integration)
6. [Shared Contracts](#6-shared-contracts)
7. [Verification & Testing](#7-verification--testing)

---

## 1. System Overview

This repository contains **three independent subsystems**, each with its own purpose, architecture, and lifecycle:

| Subsystem | Directory | Purpose | Interface Type | Primary Audience |
|-----------|-----------|---------|----------------|-----------------|
| **Chronicle Pipeline** | `pipeline/` | Automated chronicle ingestion → merging → categorization → indexing | CLI (PowerShell + Python) | Operator, Historian |
| **Evidence Pipeline** | `tools/` | Archival, legacy reorganization, integrity verification | CLI (Python) | Operator, Auditor |
| **WordPipe Runtime** | `wordpipe/` | DOCX processing library for TraceLedger embedding | Library (Python import) | Engineer, TraceLedger |

Current Chronicle split: reusable Chronicle logic lives under `wordpipe/chronicle/`;
`pipeline/` is the operator CLI/config surface.

### Core Design Principles (All Subsystems)

1. **Copy-only, non-destructive** — No stage modifies its inputs in place
2. **Deterministic outputs** — Same inputs + same config = same outputs (idempotent)
3. **Backward compatibility** — CLI flags and contracts are preserved across versions
4. **Graceful fallbacks** — Missing optional dependencies (Jinja2, YAML) degrade gracefully
5. **Audit trail** — Append-only logs for historical evidence; replace-on-run reports for current state

---

## 2. Subsystem A: Chronicle Pipeline (`pipeline/` → `wordpipe.chronicle/`)

**Canonical source decision:** See `docs/engineering/CHRONICLE_CANONICAL_DECISION.md`.
Reusable Chronicle logic for ingest, verify, merge, and categorize now lives in
`wordpipe.chronicle.*`; `pipeline/` retains operator wrappers, configuration,
templates, `chain.ps1`, and the deferred `index.py` stage. `tools/pipeline-chronicle/`
is a legacy/reference CLI location with wrappers where canonical modules exist.

### 2.1 Architecture

The chronicle pipeline is a **5-stage CLI pipeline** that transforms raw ChatGPT incident markdown files into a tagged, indexed, cross-referenced chronicle.

**Architecture pattern:** Pipe-and-filter, each stage reads from the previous stage's output.

**Entrypoint:** `pipeline/chain.ps1` (one-command PowerShell wrapper)

**NOTE - File locations:** `wordpipe.chronicle` is the canonical import surface.
`pipeline/` and `tools/pipeline-chronicle/` are CLI/operator compatibility
surfaces, not runtime import surfaces. `index.py` is the remaining Chronicle
stage deferred from canonical extraction.

```
┌─────────┐    ┌──────────┐    ┌───────┐    ┌────────────┐    ┌───────┐
│ Ingest  │───▶│ Verify   │───▶│ Merge │───▶│ Categorize │───▶│ Index │
│ Stage 1 │    │ Stage 2  │    │Stage 3│    │  Stage 4   │    │Stage 5│
└─────────┘    └──────────┘    └───────┘    └────────────┘    └───────┘
     │              │              │               │               │
     ▼              ▼              ▼               ▼               ▼
 normalised/    verification    merged.md      chronicle_       appendix/
 *.md            report                       tagged.md        *.md
                                              + sidecar.json
```

```
┌─────────┐    ┌──────────┐    ┌───────┐    ┌────────────┐    ┌───────┐
│ Ingest  │───▶│ Verify   │───▶│ Merge │───▶│ Categorize │───▶│ Index │
│ Stage 1 │    │ Stage 2  │    │Stage 3│    │  Stage 4   │    │Stage 5│
└─────────┘    └──────────┘    └───────┘    └────────────┘    └───────┘
     │              │              │               │               │
     ▼              ▼              ▼               ▼               ▼
 normalised/    verification    merged.md      chronicle_       appendix/
 *.md            report                       tagged.md        *.md
                                              + sidecar.json
```

### 2.2 Modules

#### `wordpipe.chronicle.ingest` - Stage 1: Ingestion
- **Purpose:** Convert raw deep-search markdown into normalised format with YAML front-matter
- **Location:** canonical module under `wordpipe/chronicle/`; CLI wrappers in `pipeline/` and `tools/pipeline-chronicle/`
- **Input:** Raw `.md` files from `WordHorrorStories/chatgpt-chronicle/sources/raw/chatgpt_mds/`
- **Output:** Normalised `.md` files with `source`, `title`, `date`, `event_count` in YAML front-matter
- **Key functions:**
  - `clean_mojibake(text)` — Fixes common Unicode corruption patterns
  - `extract_source_name(filename)` — Derives source name from filename or CLI override
  - `extract_title(text)` — Extracts title from H1, H2, or source fallback
  - `find_dates(text)` — Finds ISO and named-month dates
  - `parse_date_range(date_str)` — Parses "YYYY-MM-DD to YYYY-MM-DD" ranges
  - `extract_preamble(text)` — Extracts text before the first event
  - `split_into_events(text)` — Splits chronicle text into individual events by date headers
  - `format_event(event)` — Formats a single event into standard markdown
  - `generate_normalised_md(input_path, output_path)` — Full pipeline for one file
- **CLI flags:** `--input`, `--output`, `--source-name`, `--verbose`
- **Error handling:** Non-zero exit on write failure; logged warnings for malformed input

#### `wordpipe.chronicle.verify_ingest` - Stage 2: Verification (optional)
- **Purpose:** Verify that all input files can be successfully ingested
- **Location:** canonical module under `wordpipe/chronicle/`; CLI wrappers in `pipeline/` and `tools/pipeline-chronicle/`
- **Input:** Directory of raw `.md` files, path to `ingest.py`
- **Output:** Report of which files pass/fail ingestion
- **Key functions:**
  - `verify_files(input_dir, ingest_script)` — Runs ingest.py on each file in dry-run mode
  - `generate_report(results)` — Produces pass/fail summary
- **CLI flags:** `--dir`, `--ingest`, `--verbose`
- **Integration:** Only runs when `chain.ps1 -Verify` is used

#### `wordpipe.chronicle.merge` - Stage 3: Merge
- **Purpose:** Merge N normalised MD files into one, deduplicating by body hash + date
- **Location:** canonical module under `wordpipe/chronicle/`; CLI wrappers in `pipeline/` and `tools/pipeline-chronicle/`
- **Input:** Directory of normalised `.md` files
- **Output:** `merged.md` (merged chronicle), `merged.duplicates.json` (duplicate report), `merged.source_coverage.md` (source attribution)
- **Key functions:**
  - `parse_yaml_frontmatter(text)` — Extracts YAML front-matter blocks
  - `extract_events(text)` — Extracts event blocks with metadata
  - `compute_body_hash(text)` — SHA256 of whitespace-normalized body
  - `merge_files(input_dir, output_path, conflict_mode)` — Main merge orchestrator
  - `generate_source_coverage(events, output_path)` — Writes source attribution markdown
- **CLI flags:** `--input-dir`, `--output`, `--conflict-mode` (keep-both|skip|overwrite), `--verbose`
- **Conflict modes:**
  - `keep-both`: Preserves all variants, appends `(1)`, `(2)` to duplicate titles
  - `skip`: Skips exact hash+date duplicates, keeps first occurrence
  - `overwrite`: Replaces with last-seen variant
- **Duplicates report:** JSON with `duplicate_groups` array, each containing `canonical` and `duplicates` entries

#### `wordpipe.chronicle.categorize` - Stage 4: Categorization
- **Purpose:** Tag each event with theme keywords using positive + negative matching
- **Location:** canonical module under `wordpipe/chronicle/`; CLI wrappers in `pipeline/` and `tools/pipeline-chronicle/`
- **Input:** `merged.md` from Stage 3
- **Output:** `chronicle_tagged.md` (with `<!-- themes: ... -->` inline comments), `chronicle_tagged.tagged.json` (sidecar JSON)
- **Key functions:**
  - `load_themes(config_path)` — Loads theme definitions from JSON or YAML config; falls back to built-in defaults
  - `extract_events(text)` — Extracts events from merged markdown
  - `match_themes(event_body, themes)` — Matches keywords against event body; returns list of theme names
  - `rebuild_tagged_md(events, output_path)` — Writes tagged markdown with theme comments
  - `build_sidecar_json(events, output_path)` — Writes structured JSON with per-event tags
- **CLI flags:** `--input`, `--output`, `--config`, `--sidecar`, `--dry-run`, `--verbose`
- **Theme matching algorithm:**
  1. Normalize body to lowercase
  2. For each theme, check if any positive keyword is a substring of the body
  3. If positive match found, check if any negative keyword is a substring
  4. If no negative keyword matches, assign the theme
  5. Return list of matched theme names
- **Built-in themes** (6 total, 62 positive keywords, 16 negative keywords):
  - `Outages` — Server crashes, 503 errors, downtime
  - `Jailbreaks/Exploits` — Prompt injection, security exploits, DAN mode
  - `Memory/Personalisation` — Memory features, user customisation, GPTs
  - `Web UI` — chat.openai.com, web interface, browser UI
  - `API/Developer` — API, developer tools, tokens, rate limits
  - `Culture/Virality` — Memes, viral moments, community reaction
- **Config format** (`pipeline/themes.json`):
  ```json
  {
    "themes": {
      "Outages": {
        "keywords": ["server crash", "503 error", "downtime"],
        "negative_keywords": ["meme crash", "crash course"]
      }
    }
  }
  ```

#### `pipeline/index.py` — Stage 5: Index Generation
- **Purpose:** Generate 4 appendix files from tagged chronicle output
- **Input:** `chronicle_tagged.md` from Stage 4, optional `source_coverage.md`
- **Output:** `appendix/event_index.md`, `appendix/theme_index.md`, `appendix/source_manifest.md`, `appendix/link_registry.md`
- **Key functions:**
  - `extract_events(text)` — Extracts events with theme tags from tagged markdown
  - `deduplicate_events(events, method)` — Deduplicates by title or date+title; merges themes, keeps longest body
  - `generate_event_index(events, output_path)` — Sorted event table
  - `generate_theme_index(events, output_path)` — Events grouped by theme
  - `generate_source_manifest(events, source_coverage, output_path)` — Source contribution table
  - `generate_link_registry(events, output_path)` — All URLs sorted by domain
- **CLI flags:** `--input`, `--output-dir`, `--config`, `--no-link-registry`, `--source-coverage`, `--verbose`
- **Jinja2 templates:** Uses `pipeline/templates/*.j2` if Jinja2 is installed; falls back to string formatting
- **Atomic writes:** Writes to temp file, then renames to final destination (prevents half-written files)
- **Dedup method:** Default `title` — normalizes title (lowercase, collapse whitespace), merges themes via set union

#### `pipeline/themes.json` — Theme Configuration
- **Purpose:** External config for theme definitions (keywords + negative keywords)
- **Format:** JSON with `themes` object; each theme has `keywords` array and `negative_keywords` array
- **Fallback:** If missing or malformed, `categorize.py` uses built-in defaults with a warning

#### `pipeline/index_config.json` — Index Configuration
- **Purpose:** Configurable output directory, templates directory, dedup method, theme sort, link registry toggle
- **Format:** JSON with optional fields; all fields have sensible defaults

#### `pipeline/templates/` — Jinja2 Templates (4 files)
- `event_index.md.j2` — Template for event index table
- `theme_index.md.j2` — Template for theme grouping
- `source_manifest.md.j2` — Template for source attribution
- `link_registry.md.j2` — Template for URL registry

#### `pipeline/chain.ps1` — Pipeline Orchestrator
- **Purpose:** One-command wrapper for all 5 stages
- **CLI flags:** `-InputDir`, `-OutputDir`, `-ThemesConfig`, `-IndexConfig`, `-Verify`, `-SkipCategorize`, `-SkipIndex`, `-NoLinkRegistry`, `-SourceCoverage`, `-Verbose`
- **Exit codes:** 0=success, 1=ingestion fail, 2=verification fail, 3=merge fail, 4=categorize fail, 5=index fail

### 2.3 Data Flow

```
[Input: Raw .md files]
         │
         ▼
Stage 1: wordpipe.chronicle.ingest (CLI wrapper)
    Input:  *.md (raw deep-search files)
    Output: output/*/normalised/*.md (YAML front-matter + normalised events)
         │
         ▼
Stage 2: wordpipe.chronicle.verify_ingest (optional, --Verify flag)
    Input:  Raw .md directory
    Output: Verification report (stdout)
         │
         ▼
Stage 3: wordpipe.chronicle.merge (CLI wrapper)
    Input:  output/*/normalised/*.md
    Output: output/*/merged.md
            output/*/merged.duplicates.json
            output/*/merged.source_coverage.md
         │
         ▼
Stage 4: wordpipe.chronicle.categorize (CLI wrapper)
    Input:  output/*/merged.md
            pipeline/themes.json (optional)
    Output: output/*/chronicle_tagged.md
            output/*/chronicle_tagged.tagged.json
         │
         ▼
Stage 5: pipeline/index.py
    Input:  output/*/chronicle_tagged.md
            pipeline/index_config.json (optional)
            output/*/merged.source_coverage.md (optional)
    Output: output/*/appendix/event_index.md
            output/*/appendix/theme_index.md
            output/*/appendix/source_manifest.md
            output/*/appendix/link_registry.md
```

### 2.4 Logic Flow

1. **Ingestion:** Run the ingest CLI wrapper for `wordpipe.chronicle.ingest` on each raw .md file → extract preamble + events → normalise format → write per-source files
2. **Verification:** Run the verify CLI wrapper for `wordpipe.chronicle.verify_ingest` on each file → collect passes/fails → report
3. **Merge:** Read all normalised files → parse events → hash bodies → deduplicate by date+hash → resolve conflicts → write merged file + reports
4. **Categorization:** Read merged file → parse events → for each event, test body against theme keywords → assign matched themes → write tagged markdown + sidecar JSON
5. **Index:** Read tagged file → parse events → deduplicate → group by theme → collect URLs → write 4 appendix files

### 2.5 Goals & Constraints

**Goals:**
- Automate the manual chronicle building workflow (was done by hand in Word)
- Achieve ≥95% theme coverage with ≤25% over-tagging
- Generate machine-readable sidecar JSON for downstream processing
- Generate human-readable appendix files for quick reference
- Support configurable theme definitions without code changes

**Constraints:**
- Input files are raw ChatGPT chat exports with inconsistent formatting
- Some files contain duplicate events from different sources
- Keywords must be simple substrings (no regex/NLP — limited internet)
- Same event from different sources may have slightly different text
- Output must be valid markdown with consistent structure

---

## 3. Subsystem B: Evidence Pipeline (`tools/`)

### 3.1 Architecture

The evidence pipeline is a **5-stage CLI pipeline** that archives and reorganizes legacy files from a snapshot, maintaining integrity and audit trails.

**Architecture pattern:** Sequential pipeline with shared stage contract.

**Entrypoint:** `tools/orchestrate.py` (one-command Python wrapper) or stage-by-stage.

```
┌──────────────┐    ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌────────────────┐
│ make_manifest │───▶│ plan_legacy_reorg│───▶│ apply_legacy_reorg│───▶│ build_legacy_index│───▶│ verify_integrity│
│   Stage 1     │    │   Stage 2       │    │   Stage 3        │    │   Stage 4        │    │   Stage 5      │
└──────────────┘    └─────────────────┘    └──────────────────┘    └──────────────────┘    └────────────────┘
```

### 3.2 Modules

| Module | Purpose | Input | Output |
|--------|---------|-------|--------|
| `tools/make_manifest.py` | Generate manifest from snapshot | Snapshot directory | `manifest.jsonl`, `manifest.csv` |
| `tools/plan_legacy_reorg.py` | Build relocation plan | Manifest | `relocation_plan.jsonl` |
| `tools/apply_legacy_reorg.py` | Apply relocation (copy-only) | Plan + snapshot | `relocation_map.jsonl`, conflicts log |
| `tools/build_legacy_index.py` | Generate legacy index docs | Relocation map + legacy trees | `LEGACY_INDEX.md` (×2) |
| `tools/verify_integrity.py` | Verify integrity + coverage | Manifest, plan, map, snapshot | Verify reports (MD + JSON) |
| `tools/orchestrate.py` | One-command pipeline runner | Workspace root + snapshot root | Subprocess execution |
| `tools/pipeline_contracts.py` | Shared stage contract | Stage metadata | `StageResult`, `StagePaths`, `StageError` |
| `tools/tool_common.py` | Shared primitives | Paths/hashes/log payloads | Hash strings, normalized paths |
| `tools/jalali.py` | Gregorian-to-Jalali conversion | Gregorian date | Jalali date string |
| `tools/security_scan.py` | Secret pattern scanning | Repository root | Scan report |
| `tools/docs_link_check.py` | Doc reference validation | Documentation files | Link check report |

### 3.3 Data Flow

```
_WORK/snapshot/ (immutable input)
  │
  ▼
Stage 1: make_manifest.py
  → _ARCHIVE/manifests/manifest.jsonl
  → _ARCHIVE/manifests/manifest.csv
  │
  ▼
Stage 2: plan_legacy_reorg.py
  → _ARCHIVE/move_maps/relocation_plan.jsonl
  │
  ▼
Stage 3: apply_legacy_reorg.py
  → _ARCHIVE/move_maps/relocation_map.jsonl
  → wordpipe/legacy/ (copy-only)
  → WordHorrorStories/legacy/ (copy-only)
  → _ARCHIVE/logs/conflicts.log
  │
  ▼
Stage 4: build_legacy_index.py
  → wordpipe/legacy/LEGACY_INDEX.md
  → WordHorrorStories/legacy/LEGACY_INDEX.md
  │
  ▼
Stage 5: verify_integrity.py
  → _ARCHIVE/logs/verify_report.md
  → _ARCHIVE/logs/verify_report.json
  → _ARCHIVE/logs/consistency_report.json
  → _ARCHIVE/logs/immutability_report.json
```

### 3.4 Logic Flow

1. **Manifest:** Scan snapshot directory → compute SHA256 for each file → emit JSONL + CSV
2. **Plan:** Read manifest → classify files by area (wordpipe, WordHorrorStories, ai, misc) → determine legacy candidates → emit relocation plan
3. **Apply:** Read plan → copy current files to active tree → copy legacy files to legacy tree → detect conflicts → emit relocation map + conflict log
4. **Index:** Read relocation map + legacy trees → build bucket statistics → emit LEGACY_INDEX.md files
5. **Verify:** Read manifest + plan + map + snapshot → compare hashes → check coverage → check consistency → check immutability → emit reports

### 3.5 Goals & Constraints

**Goals:**
- Preserve immutable snapshot evidence
- Reorganize legacy files without destructive operations
- Verify integrity of all pipeline outputs
- Provide audit trail for all operations

**Constraints:**
- Snapshot is read-only (immutable input)
- Copy-only, no move/delete operations
- Append-only audit logs (never rewrite historical logs)
- Windows paths with backslash in shell, forward slash in code

---

## 4. Subsystem C: WordPipe Runtime (`wordpipe/`)

### 4.1 Architecture

WordPipe is a **layered Python library** for DOCX processing, designed for embedding in TraceLedger. It uses dependency injection for testability and optional extras for lightweight installs.

**Architecture pattern:** Layered (core → interfaces → adapters → orchestration → CLI/plugins)

```
┌─────────────────────────────────────────────────────────────┐
│                     External Consumers                       │
│  (TraceLedger, CLI, tests)                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  orchestration/  — pipeline coordinator, dep injection       │
│  cli/            — optional CLI entrypoint                   │
│  plugins/        — optional plugin registry                  │
├─────────────────────────────────────────────────────────────┤
│  interfaces/     — abstract service contracts                │
├─────────────────────────────────────────────────────────────┤
│  adapters/       — concrete implementations (optional deps)  │
│    docx/         — python-docx adapters                      │
│    ai/           — OpenAI adapters                           │
│    flatteners/   — DOCX flattener implementations            │
├─────────────────────────────────────────────────────────────┤
│  core/           — dependency-light datatypes + helpers      │
│  events.py      — EventSink protocol                         │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Modules

| Package | Purpose | Dependencies |
|---------|---------|--------------|
| `wordpipe/core/` | Datatypes, OOXML helpers | stdlib only |
| `wordpipe/interfaces/` | Abstract contracts (reader, writer, styler, segmenter, flattener) | stdlib only |
| `wordpipe/adapters/docx/` | Concrete DOCX implementations | python-docx |
| `wordpipe/adapters/ai/` | OpenAI integration | openai, python-dotenv |
| `wordpipe/adapters/flatteners/` | Concrete flattener implementations | python-docx (Win32) |
| `wordpipe/orchestration/` | Pipeline coordinator with DI | stdlib only |
| `wordpipe/plugins/` | Optional plugin loading | stdlib only |
| `wordpipe/cli/` | Command-line entrypoint | stdlib only |
| `wordpipe/steps/` | Modular step functions (flatten, style, segment, finalize, toc) | stdlib only |
| `wordpipe/events.py` | EventSink protocol | stdlib only |

### 4.3 Data Flow

```
PipelineConfig (input paths, flags)
  │
  ▼
WordPipePipeline(deps).run(cfg)
  │
  ├── Stage 1: flatten_step  (flatten DOCX → working directory)
  ├── Stage 2: style_step    (apply styles)
  ├── Stage 3: segment_step  (segment by headings)
  ├── Stage 4: toc_step      (generate table of contents)
  └── Stage 5: finalize_step (write output DOCX)
  │
  ▼
RunReport (structured result with errors/warnings)
```

### 4.4 Logic Flow

1. **Flatten:** Convert DOCX to plain text/markdown in working directory
2. **Style:** Apply code styles, heading styles, formatting
3. **Segment:** Split document by heading hierarchy
4. **TOC:** Generate table of contents from headings
5. **Finalize:** Write the final DOCX output

### 4.5 Goals & Constraints

**Goals:**
- Provide import-safe library surface (no optional deps at import time)
- Support dependency injection for testability
- Emit structured events via EventSink
- Support both direct library usage and CLI usage

**Constraints:**
- `import wordpipe` must succeed with stdlib only
- Optional deps (python-docx, openai) loaded lazily inside methods
- Windows Win32 COM dependencies for legacy flatteners
- Backward compatibility with existing `process_docx_v3` entrypoint

---

## 5. Cross-Subsystem Integration

The three subsystems are **independent** — they do not share runtime dependencies or import each other. However, they share:

| Shared Element | Location | Used By |
|----------------|----------|---------|
| Jalali date conversion | `tools/jalali.py` | Chronicle + Evidence pipelines |
| EventSink protocol | `wordpipe/events.py` | WordPipe (runtime) |
| Standard headers | `tools/add_standard_headers.py` | All Python files |
| Security scanning | `tools/security_scan.py` | All subsystems |
| Test suite | `tests/` | All subsystems |

### Interaction Model

```
TraceLedger (external)
  │
  ├── Uses wordpipe/ as library (import)
  │     └── WordPipePipeline(deps).run(cfg) → RunReport
  │
  ├── Consumes pipeline/ output (chronicle tagged data)
  │     └── chronicle_tagged.md, tagged.json, appendix/*.md
  │
  └── Consumes tools/ output (evidence artifacts)
        └── verify reports, manifests, LEGACY_INDEX
```

---

## 6. Shared Contracts

### CLI Flag Conventions

| Flag | Type | Purpose | Used By |
|------|------|---------|---------|
| `--input` | Path | Input file/directory | Chronicle stages |
| `--output` | Path | Output file | Chronicle stages |
| `--config` | Path | Configuration file | Chronicle stages |
| `--verbose` | Bool | Enable debug logging | All stages |
| `--dry-run` | Bool | Preview without writing | All stages |
| `--workspace-root` | Path | Path resolution base | Evidence stages |
| `--summary-json` | Path | StageResult JSON output | Evidence stages |
| `--strict` | Bool | Warnings → errors | Evidence stages |

### Exit Code Conventions

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | General failure / Stage 1 failure |
| 2 | Stage 2 failure (verification) |
| 3 | Stage 3 failure (merge) |
| 4 | Stage 4 failure (categorize) |
| 5 | Stage 5 failure (index/verify) |

### Error Message Format

Contracted stages use standardized error format:
```
ERROR: required {name} not found: {abs_path}
```

---

## 7. Verification & Testing

### Automated Tests

| Test File | Tests | Coverage | Command |
|-----------|-------|----------|---------|
| `tests/test_pipeline_chronicle.py` | 70 | Ingest, merge, categorize, verify_ingest, integration | `python -m pytest tests/test_pipeline_chronicle.py -v` |
| `tests/test_import_safety.py` | 2 | Core import safety + chronicle extra contract | `python -m pytest tests/test_import_safety.py -v` |
| `tests/test_steps.py` | 12 | Step modules (flatten, style, segment, finalize, toc) | `python -m pytest tests/test_steps.py -v` |
| `tests/test_orchestration_pipeline.py` | 6 | Fail-fast orchestration behavior | `python -m pytest tests/test_orchestration_pipeline.py -v` |
| `tests/test_segmenter_hpath.py` | 10 | Heading-path precompute semantics | `python -m pytest tests/test_segmenter_hpath.py -v` |
| `tests/test_wordpipe_steps.py` | 6 | Transitional step/orchestration overlap | `python -m pytest tests/test_wordpipe_steps.py -v` |
| **Total** | **105** | Full health signal | `python -m pytest tests -q` |

See also: [`docs/engineering/P0_P2_VALIDATION_REPORT.md`](docs/engineering/P0_P2_VALIDATION_REPORT.md)

### Verification Commands

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Doc link integrity | `python tools/docs_link_check.py` | No broken links |
| Secret scan | `python tools/security_scan.py --root . --fail-on-findings` | Exit 0, no findings |
| Import safety | `python -c "import wordpipe"` | Succeeds without optional deps |
| Header consistency | `python tools/add_standard_headers.py --path .` | "0 files changed, N files skipped" |
| Full pipeline (dry) | `python tools/orchestrate.py --dry-run` | Commands printed, no execution |

### Tag Quality Verification

For the chronicle pipeline, tag quality is verified by inspecting the sidecar JSON:

```powershell
python -c "import json; d=json.load(open('output/*/chronicle_tagged.tagged.json')); total=len(d); tagged=sum(1 for e in d if e['themes']); over=sum(1 for e in d if len(e['themes'])>=4); print(f'{tagged/total*100:.1f}% coverage, {over/total*100:.1f}% over-tagged')"
```

---

## See Also

- `PLAN.md` — Immutable log of intentions and completions
- `ROADMAP.md` — Project roadmap with phases, goals, constraints
- `JOURNAL.md` — Dated period journal with claims and verification
- `ONTOLOGY_MODEL.md` — Formal entity-relationship model
- `INDEX.md` — Full project file index
