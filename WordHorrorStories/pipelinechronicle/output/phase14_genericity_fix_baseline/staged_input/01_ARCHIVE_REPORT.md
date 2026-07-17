# ARCHIVE REPORT

## February 2026

- **2026-02-14 - ARCHIVE REPORT - 1. Overview:** This archive contains the original **chronicle pipeline tools** — a set of four independent Python CLI tools and one PowerShell orchestrator (`chain.ps1`) that automate the workflow of normalising, merging, categorising, and verifying raw deep-search markdown files into a structured chronicle.

The tools were built for the `WordHorrorStories/chatgpt-chronicle/` dataset (16 raw files, ~224 events) and were validated end-to-end.

---

- **2026-02-14 - ARCHIVE REPORT - 2. Tool Inventory:** | # | File | Lines | Role | Status at Archive | Current Working Copy |
|---|------|-------|------|-------------------|---------------------|
| 1 | `ingest.py` | ~440 | Normalise raw `.md` → standard chronicle format | ✅ All P0/P1 fixes applied | `pipeline/ingest.py` (copy) |
| 2 | `merge.py` | ~480 | Combine N normalised files → deduplicated merged chronicle | ✅ 3 conflict modes, source coverage | `pipeline/merge.py` (copy) |
| 3 | `categorize.py` | ~390 | Tag events with theme labels via keyword matching | ✅ Built-in + config-driven themes | `pipeline/categorize.py` (v2, refactored) |
| 4 | `verify_ingest.py` | ~140 | Batch-verify `ingest.py` against all raw files | ✅ Runs all 16 files, reports counts | `pipeline/verify_ingest.py` (copy) |
| 5 | `chain.ps1` | ~320 | PowerShell orchestrator: ingest → merge → categorize | ✅ End-to-end tested on 16 files | `pipeline/chain.ps1` (v2, 5 stages) |

### Post-Archival Additions (Phase 9b)

| # | File | Lines | Role |
|---|------|-------|------|
| 6 | `pipeline/index.py` | ~580 | Stage 5: Generate 4 appendix files with Jinja2 + fallback formatting |
| 7 | `pipeline/themes.json` | ~90 | External theme config (6 themes, 62 pos + 16 neg keywords) |
| 8 | `pipeline/index_config.json` | ~15 | Configurable output dir, templates dir, dedup method, theme sort |
| 9 | `pipeline/templates/` | 4 files | Jinja2 templates for appendix rendering (event_index, theme_index, source_manifest, link_registry) |

### Supporting Documents

| File | Content |
|------|---------|
| `README.md` | Full spec with design principles, CLI docs, ontology cross-ref |
| `PIPELINE_PLAN.md` | Revised stage-based implementation plan (6 stages) |
| `REVIEW_PLAN.md` | Code review & remediation plan for `ingest.py` |
| `ROADMAP.md` | Implementation roadmap with tool status and test results |

---

- **2026-02-14 - ARCHIVE REPORT - 3. Architecture & Design:** ### 3.1 Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Independent** | Each tool reads from disk, writes to disk. No Python cross-imports. |
| **Parameterised** | All behaviour via CLI flags (`--input`, `--output`, `--config`, etc.) |
| **Config-driven** | `categorize.py` accepts JSON or YAML config for theme keywords |
| **Deterministic** | Same inputs → same outputs. No randomness. |
| **Composable** | Output of one tool is input to the next. Run individually or via `chain.ps1`. |

### 3.2 Data Flow

```
Raw .md files
    │
    ▼
┌──────────────────┐     ┌──────────────────┐
│  ingest.py       │────▶│  normalised/*.md │  (YAML front-matter + ## Event: blocks)
│  (Stage 1)       │     └──────────────────┘
└──────────────────┘
    │
    ▼  (optional)
┌──────────────────┐     ┌──────────────────┐
│  verify_ingest.py│────▶│  Verification    │  (pass/fail report)
│  (Stage 2)       │     │  report          │
└──────────────────┘     └──────────────────┘
    │
    ▼
┌──────────────────┐     ┌──────────────────┐
│  merge.py        │────▶│  merged.md       │  (deduplicated, sorted by date)
│  (Stage 3)       │     ├──────────────────┤
└──────────────────┘     │  duplicates.json │
    │                    │  source_cov.md   │
    ▼                    └──────────────────┘
┌──────────────────┐     ┌──────────────────┐
│  categorize.py   │────▶│  chronicle_      │  (inline <!-- themes: ... -->)
│  (Stage 4)       │     │  tagged.md       │
└──────────────────┘     ├──────────────────┤
    │                    │  tagged.json     │  (sidecar)
    ▼                    └──────────────────┘
┌──────────────────┐     ┌──────────────────┐
│  index.py        │────▶│  appendix/       │  4 files: event_index,
│  (Stage 5)       │     │  *.md            │  theme_index, source_manifest,
└──────────────────┘     └──────────────────┘  link_registry
```

### 3.3 Key Design Decisions

1. **Event splitting uses `:** (colon before closing `**`)** — matches actual raw file format `- **Title:** Description`
2. **Substring matching, not word-boundary regex** — keywords like `chat.openai.com` and `503 error` contain special chars that break `\b` word boundaries
3. **Built-in default themes** — `categorize.py` works without a config file (6 themes, 48 keywords)
4. **JSON + YAML config** — both formats supported transparently
5. **`python.exe` not `python`** in `chain.ps1` — pyenv shim (`python.bat`) breaks on filenames with parentheses
6. **Array-based argument passing** in `chain.ps1` — handles special characters correctly

---

- **2026-02-14 - ARCHIVE REPORT - 4. CLI Signatures (Complete Reference:** ### 4.1 `ingest.py`

```
--input, -i       Path to raw .md file (required)
--output, -o      Path for normalised output (default: <stem>_normalised.md)
--source-name     Override source name (otherwise derived from filename)
--date-override   Force a date (YYYY-MM-DD or YYYY-MM) when file has no parseable dates
--verbose, -v     Enable debug logging
```

### 4.2 `merge.py`

```
--inputs, -i      One or more normalised .md files (mutually exclusive with --input-dir)
--input-dir, -d   Directory containing normalised .md files
--output, -o      Output merged markdown (default: merged.md)
--conflict-mode   keep-both | manual | skip (default: keep-both)
--source-coverage Also generate source_coverage.md table
--verbose, -v     Enable debug logging
```

### 4.3 `categorize.py`

```
--input, -i       Path to input .md file (required)
--config, -c      JSON or YAML config file with theme keywords (optional)
--output, -o      Path for tagged output (default: <input>_tagged.md)
--sidecar         Also write a sidecar JSON file with structured tag data
--verbose, -v     Enable debug logging
```

### 4.4 `verify_ingest.py`

```
--dir             Directory containing raw .md files (default: WordHorrorStories/.../chatgpt_mds)
--ingest          Path to ingest.py (default: tools/pipeline-chronicle/ingest.py)
--verbose, -v     Show per-file details
```

### 4.5 `chain.ps1`

```
-InputDir         Directory containing raw .md files (required)
-OutputDir        Directory for output files (required; created if missing)
-Config           Theme config file for categorize.py (optional)
-Verify           Run verify_ingest.py before merging
-SkipCategorize   Stop after merge (skip categorisation)
-Verbose          Enable debug logging
```

---

- **2026-02-14 - ARCHIVE REPORT - 5. Known Issues & Critique (at Time of Archive:** ### 5.1 Issues Fixed Before Archive

| # | Issue | Fix Applied |
|---|-------|-------------|
| 1 | Preamble silently discarded in `ingest.py` | Added `extract_preamble()` — renders as `> **Overview:**` blockquote |
| 2 | Title extraction too narrow (H1 only) | Fallback chain: H1 → first H2 → `{source} Incidents` |
| 3 | Excess CLI flags (11 flags) | Reduced to 5 essential flags |
| 4 | Redundant Unicode entries in mojibake map | Removed 8 redundant Unicode→Unicode entries |
| 5 | `import yaml as _yaml` inside `merge.py main()` | Removed duplicate import |
| 6 | Source coverage used `file.stem` not source name | `merge_files()` now returns `source_names` list |
| 7 | Event count from `str.count()` inflated by body text | Event count read from front-matter YAML |
| 8 | `python` (pyenv shim) breaks on parenthesised filenames | Changed to `python.exe` in `chain.ps1` |
| 9 | PowerShell parameter sets caused parsing errors | Removed parameter sets, simplified to flat params |

### 5.2 Issues Deferred (Not Fixed Before Archive)

| # | Issue | Severity | Recommended Fix |
|---|-------|----------|-----------------|
| 1 | No file I/O error handling in Python tools | Medium | Wrap `read_text`/`write_text` in `try/except` |
| 2 | `verify_ingest.py` re-runs ingestion (double work) | Medium | Refactor to read JSON sidecar from `ingest.py` |
| 3 | `-Config` parameter name in `chain.ps1` is confusing | Low | Rename to `-ThemesConfig` |
| 4 | Dead variables `$verboseFlag`, `$configArgs` in `chain.ps1` | Low | Remove unused assignments |
| 5 | `$ProjectRoot` unused in `chain.ps1` | Low | Remove or wire in |
| 6 | No `--source-coverage` exposed in `chain.ps1` | Low | Add `-SourceCoverage` switch |
| 7 | No output file validation after stages | Low | Add size check after each stage |
| 8 | `verify_ingest.py` uses `subprocess.run` without timeout | Low | Add `timeout=` parameter |
| 9 | No `--dry-run` or `--quiet` flags | Low | Add when dataset grows to 50+ files |

### 5.3 Design Limitations

1. **`verify_ingest.py` parses log output** — fragile. If log format changes (e.g., "Extracted 8 events." becomes "Extracted 8 event(s)."), the parser breaks silently.
2. **Substring matching is naive** — `"memory"` in `"memory"` matches, but so does `"memory"` in `"commemorative"`. No word-boundary awareness.
3. **No cross-file dedup in `merge.py`** — dedup is per-run. If you merge 5 files, then later add 2 more and re-merge, previously seen duplicates are re-detected (not remembered).
4. **`chain.ps1` is PowerShell-only** — no bash equivalent for Linux/macOS users.
5. **No unit tests** — tools were validated by integration testing only (run against real files, inspect output).

---

## January 2022

- **2022-01-01 - ARCHIVE REPORT - 6. Test Results (at Time of Archive:** ### 6.1 Ingestion (16 raw files)

| Metric | Value |
|--------|-------|
| Files processed | 16 |
| Total events extracted | 224 |
| Files with 0 events (narrative) | 4 (correct) |
| Errors | 0 |

### 6.2 Merge (5 normalised files)

| Conflict Mode | Events | Duplicates | Behaviour |
|---------------|--------|------------|-----------|
| `keep-both` | 40 | 0 true duplicates | 8 date conflicts resolved by keeping all variants |
| `skip` | 17 | 23 conflicts | Only first occurrence per date kept |
| `manual` | 9 | 31 conflicts | Only unique dates without conflicts kept |

### 6.3 Categorisation (3 normalised files → merged → tagged)

| Config | Events | Tagged | Coverage |
|--------|--------|--------|----------|
| Built-in defaults (6 themes, 48 keywords) | 28 | 27 | 96.4% |
| Custom JSON (2 themes, 6 keywords) | 28 | 11 | 39.3% |
| Custom YAML (2 themes, 5 keywords) | 28 | 20 | 71.4% |

### 6.4 Full Pipeline (16 raw files via `chain.ps1`)

| Metric | Value |
|--------|-------|
| Files ingested | 16/16 (0 failures) |
| Merged events | 61 |
| Tagged events | 59/61 (96.7%) |
| Duplicates found | 17 |
| Date range | 2022-01-01 to 2025-07-15 |

---

## February 2026

- **2026-02-14 - ARCHIVE REPORT - 7. Ontology Cross-Reference:** | Pipeline Concept | Ontology Class | Relation |
|------------------|----------------|----------|
| `ingest.py` run | `ActivityPeriod(name="Chronicle Ingestion")` | `produces → Artifact(path=normalised/*.md)` |
| `merge.py` run | `ActivityPeriod(name="Chronicle Merge")` | `consumes → normalised/*.md` → `produces → merged/*.md` |
| `categorize.py` run | `ActivityPeriod(name="Chronicle Categorisation")` | `states → Claim(text="Event X is tagged as Outages")` |
| Merged event entry | `Claim(subtype=EvidenceClaim)` | `verified_by → Verification(method=inspection)` |
| Source attribution | `Artifact(kind=evidence)` | `produced_by → ActivityPeriod` |

---

- **2026-02-14 - ARCHIVE REPORT - 8. File Checksums:** ```
SHA256 (ingest.py)         = <computed at archive time>
SHA256 (merge.py)          = <computed at archive time>
SHA256 (categorize.py)     = <computed at archive time>
SHA256 (verify_ingest.py)  = <computed at archive time>
SHA256 (chain.ps1)         = <computed at archive time>
```

---

- **2026-02-14 - ARCHIVE REPORT - 9. Restoration Instructions:** To restore and use the archived tools:

```powershell
# Copy from archive to working location
Copy-Item "_ARCHIVE/pipeline-chronicle/tools/*" "tools/pipeline-chronicle/" -Recurse

# Run the pipeline
powershell -File tools/pipeline-chronicle/chain.ps1 -InputDir raw/ -OutputDir output/

# Or run individual tools
python tools/pipeline-chronicle/ingest.py --input raw/file.md --output normalised/file.md
python tools/pipeline-chronicle/merge.py --input-dir normalised/ --output merged.md
python tools/pipeline-chronicle/categorize.py --input merged.md --output tagged.md
```

---

- **2026-02-14 - ARCHIVE REPORT - 10. Post-Archival Developments (Phase 9b:** After archival, a second development session (22:29-22:52 same day) refactored and extended the pipeline:

### What Changed

| File | Archived (v1) | Current (v2) |
|------|---------------|---------------|
| `categorize.py` | No negative keywords; PyYAML hard import; no `--dry-run` | Negative keyword support; PyYAML optional; `--dry-run` flag; graceful config fallback |
| `chain.ps1` | 4 stages; `-Config` param; no index | 5 stages; `-ThemesConfig`/`-IndexConfig`/`-SkipIndex`/`-NoLinkRegistry`/`-SourceCoverage` params |
| `index.py` | Did not exist | New — generates 4 appendix files with Jinja2 + fallback formatting |
| `themes.json` | Did not exist | New — 6 themes, 62 positive + 16 negative keywords |
| `index_config.json` | Did not exist | New — configurable output dir, templates dir, dedup, theme sort |
| `templates/` | Did not exist | New — 4 Jinja2 templates for appendix rendering |

### What Was Copied (Identical)

| File | From | To |
|------|------|----|
| `ingest.py` | `tools/pipeline-chronicle/ingest.py` | `pipeline/ingest.py` |
| `merge.py` | `tools/pipeline-chronicle/merge.py` | `pipeline/merge.py` |
| `verify_ingest.py` | `tools/pipeline-chronicle/verify_ingest.py` | `pipeline/verify_ingest.py` |

### What Was Fixed

- `tools/ingest.py` — was a markdown design document with wrong `.py` extension; moved to `_ARCHIVE/pipeline-chronicle/notes/ingest_design_notes.md`
- `ARCHITECTURE_AND_MODULES.md` §2 — corrected all `pipeline/ingest.py` etc. references to `tools/pipeline-chronicle/ingest.py`
- `ONTOLOGY_MODEL.md` — added current working copy entries for ingest, merge, verify at `tools/pipeline-chronicle/`

### What Remains to Be Fixed

- `pipeline/reference.py` not yet built (sub-phase 9c)
- 59 tests import from archived v1 code with flat list format — need update for v2 dict format
- No ontology wiring for P9/P9b ActivityPeriods

- **2026-02-14 - ARCHIVE REPORT - 11. Change Log:** | Date | Change |
|------|--------|
| 2026-02-14 | Phase 9b post-archival update: refactored categorize.py, chain.ps1; built index.py, themes.json, index_config.json, templates/; copied ingest/merge/verify into pipeline/; archived misnamed tools/ingest.py; fixed ARCHITECTURE_AND_MODULES.md paths |
| 2026-02-14 | Initial archive — all 5 tools + 4 docs archived |
