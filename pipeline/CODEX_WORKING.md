# Chronicle Pipeline — Working Code Reference

> **Purpose:** Local documentation of the actual working pipeline code, its evolution, and current state.
> **Date:** 2026-02-14 (Jalali: 1404-11-25)
> **Based on actual file system analysis + git history.**

---

## 1. Timeline & Evolution

The chronicle pipeline was built in two phases across an **active work session outside version control**, producing three generations of code:

```
Generation 1 (Archived)     Generation 2 (Staged)         Generation 3 (Working)
2026-02-14 14:29-19:04      2026-02-14 ~19:00-22:30       2026-02-14 22:29-22:52
                           ─────────────────────────────────────────────────────
_ARCHIVE/pipeline-          tools/pipeline-chronicle/     pipeline/
chronicle/tools/                                           (NOT in git — untracked)
  ingest.py      ✅           ingest.py     <-same-        (missing)
  verify_ingest.py ✅         verify_ingest.py <-same-      (missing)
  merge.py       ✅           merge.py      <-same-        (missing)
  categorize.py  ❌(old)     categorize.py <-same-         categorize.py  ✅(v2)
  chain.ps1      ❌(old)     chain.ps1    <-same-         chain.ps1     ✅(v2)
  (none)                                                   index.py      ✅(new)
                                                           themes.json   ✅(new)
                                                           index_config.json ✅(new)
                                                           templates/    ✅(new)
```

### What Happened

| Time (2026-02-14) | Event | Evidence |
|-------------------|-------|----------|
| ~14:29 | `ingest.py` built (first version) | File timestamp `14:29:56` |
| ~14:45 | `verify_ingest.py` built | File timestamp `14:45:56` |
| ~15:03 | `PIPELINE_PLAN.md` written | File timestamp `15:03:05` |
| ~16:32 | `merge.py` built | File timestamp `16:32:55` |
| ~16:34 | `categorize.py` built (v1 — no negative keywords) | File timestamp `16:34:15` |
| ~17:03 | `REVIEW_PLAN.md`, `ROADMAP.md` written | File timestamps |
| ~19:04 | All 5 tools **archived** to `_ARCHIVE/pipeline-chronicle/tools/` | ARCHIVE_REPORT.md |
| ~19:12 | `chain.ps1` updated (v1 — 4 stages, -Config param) | File timestamp `19:12:01` |
| **~22:29** | **`pipeline/themes.json` created** | File timestamp `22:29:14` |
| **~22:29** | **`pipeline/index_config.json` created** | File timestamp `22:29:14` |
| **~22:29** | **`pipeline/templates/` created (4 templates)** | File timestamps `22:29-22:30` |
| **~22:30** | **`pipeline/chain.ps1` refactored (v2 — 5 stages, all new params)** | File timestamp `22:32:43` |
| **~22:42** | **`pipeline/index.py` built** | File timestamp `22:42:32` |
| **~22:50** | **`pipeline/themes.json` adjusted** | File timestamp `22:50:05` |
| **~22:52** | **`pipeline/categorize.py` refactored (v2 — negative keywords, --dry-run)** | File timestamp `22:52:38` |

### Key Insight

The files in `pipeline/` were **never committed to git**. The `_ARCHIVE/pipeline-chronicle/tools/` versions are the last known-good committed versions. The `pipeline/` folder represents **post-archival development** (Generation 3) that added:
1. Negative keyword support to `categorize.py`
2. The entire `index.py` with Jinja2 templates
3. `themes.json` and `index_config.json`
4. Expanded `chain.ps1` with 5 stages

**However**, `pipeline/` was originally missing `ingest.py`, `merge.py`, and `verify_ingest.py`. These were **copied from `tools/pipeline-chronicle/`** on 1404-11-25 (post-archival fix) to make the pipeline runnable. They are byte-identical to the originals.

**Also fixed:** `tools/ingest.py` was a misnamed markdown design document (starts with `### 1. **`ingest.py`** — Highest priority`) that was moved to `_ARCHIVE/pipeline-chronicle/notes/ingest_design_notes.md`.

---

## 2. Current File Inventory

### Files That Exist in `pipeline/`

| File | Status | Source | Role |
|------|--------|--------|------|
| `categorize.py` (17,683 bytes) | ✅ Working | Refactored from archived v1 | Stage 4 — Tag events with themes |
| `index.py` (24,100 bytes) | ✅ Working | Newly built | Stage 5 — Generate appendix files |
| `chain.ps1` (13,586 bytes) | ✅ Working | Refactored from archived v1 | Orchestrator |
| `themes.json` (2,678 bytes) | ✅ Working | Newly created | External theme config |
| `index_config.json` (316 bytes) | ✅ Working | Newly created | Index generation config |
| `templates/event_index.md.j2` | ✅ Working | Newly created | Jinja2 template |
| `templates/theme_index.md.j2` | ✅ Working | Newly created | Jinja2 template |
| `templates/source_manifest.md.j2` | ✅ Working | Newly created | Jinja2 template |
| `templates/link_registry.md.j2` | ✅ Working | Newly created | Jinja2 template |
| `ingest.py` (16,504 bytes) | ✅ Working | Copied from `tools/pipeline-chronicle/ingest.py` (identical) | Stage 1 — Normalise raw .md |
| `merge.py` (17,345 bytes) | ✅ Working | Copied from `tools/pipeline-chronicle/merge.py` (identical) | Stage 3 — Merge + dedup |
| `verify_ingest.py` (4,444 bytes) | ✅ Working | Copied from `tools/pipeline-chronicle/verify_ingest.py` (identical) | Stage 2 — Batch verification |

### Files Referenced by `chain.ps1` That Were MISSING (Now Fixed)

| File | Formerly Missing From `pipeline/` | Source Copied From | Status |
|------|------------------------------------|--------------------|--------|
| `ingest.py` | ❌ (now ✅) | `tools/pipeline-chronicle/ingest.py` | ✅ Fixed 1404-11-25 |
| `merge.py` | ❌ (now ✅) | `tools/pipeline-chronicle/merge.py` | ✅ Fixed 1404-11-25 |
| `verify_ingest.py` | ❌ (now ✅) | `tools/pipeline-chronicle/verify_ingest.py` | ✅ Fixed 1404-11-25 |

### Also Fixed: Misnamed File

| File | Problem | Resolution |
|------|---------|------------|
| `tools/ingest.py` | Markdown design document with `.py` extension | Moved to `_ARCHIVE/pipeline-chronicle/notes/ingest_design_notes.md` |

### Files Referenced by `chain.ps1` That DO Exist at Expected Path

| File | Path in chain.ps1 | Exists? |
|------|-------------------|---------|
| `categorize.py` | `$ScriptDir/categorize.py` | ✅ Yes |
| `index.py` | `$ScriptDir/index.py` | ✅ Yes |

### Duplicate Locations of Tools

| Tool | `pipeline/` | `tools/pipeline-chronicle/` | `_ARCHIVE/pipeline-chronicle/tools/` |
|------|-------------|-----------------------------|--------------------------------------|
| `categorize.py` | ✅ v2 (refactored) | ✅ v1 (same as archived) | ✅ v1 (archived) |
| `index.py` | ✅ v1 (only copy) | ❌ | ❌ |
| `chain.ps1` | ✅ v2 (refactored) | ✅ v1 (4-stage) | ✅ v1 (archived) |
| `themes.json` | ✅ (only copy) | ❌ | ❌ |
| `index_config.json` | ✅ (only copy) | ❌ | ❌ |
| `templates/` | ✅ (only copy) | ❌ | ❌ |
| `ingest.py` | ✅ (copied from tools/pipeline-chronicle/) | ✅ (v1) | ✅ (archived) |
| `merge.py` | ✅ (copied from tools/pipeline-chronicle/) | ✅ (v1) | ✅ (archived) |
| `verify_ingest.py` | ✅ (copied from tools/pipeline-chronicle/) | ✅ (v1) | ✅ (archived) |

---

## 3. Detailed Module Reference

### 3.1 `pipeline/categorize.py` (v2 — Refactored)

**Purpose:** Tag events in a normalised/merged chronicle with theme labels using keyword matching. Supports negative keywords to reduce false positives.

**Architecture:**
- Reads markdown with `## Event: YYYY-MM-DD – Title` blocks
- Loads theme definitions from JSON or YAML config (with fallback to built-in defaults)
- For each event, tests body against theme keywords (positive + negative substring matching)
- Writes tagged markdown with inline `<!-- themes: ... -->` HTML comments
- Optionally writes sidecar JSON with structured tag data

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `load_themes(config_path)` | Load theme definitions from JSON/YAML or return built-in defaults |
| `extract_events(md_body)` | Split markdown into event blocks by heading regex |
| `match_themes(body, themes)` | Match body text against themes; returns sorted list of matching theme names |
| `rebuild_tagged_md(original_text, events)` | Reconstruct markdown with tag comments inserted |
| `build_sidecar_json(events)` | Build structured JSON with per-event tag data |

**Config Format (themes.json):**
```json
{
  "themes": {
    "Theme Name": {
      "keywords": ["kw1", "kw2"],
      "negative_keywords": ["neg1", "neg2"]
    }
  }
}
```

**Legacy format** (list of strings) is also supported for backward compatibility:
```json
{
  "themes": {
    "Theme Name": ["kw1", "kw2"]
  }
}
```

**Built-in Themes** (6 themes, 62 positive keywords, 16 negative keywords):
- Web UI — interface-related (chat.openai.com, web interface, browser)
- API/Developer — technical (API, Linux terminal, function calling, tokens)
- Outages — service disruptions (server crash, 503 error, downtime)
- Jailbreaks/Exploits — security (prompt injection, DAN, bypass)
- Memory/Personalisation — user memory (memory, custom instructions, bio)
- Culture/Virality — social (viral, Twitter, Reddit, memes)

**Algorithm (`match_themes`):**
1. Convert body to lowercase
2. For each theme, check negative keywords first (fast rejection)
3. If no negative match, check positive keywords via `kw.lower() in body_lower`
4. Returns sorted list of matched theme names

**CLI Flags:**
| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--input`, `-i` | ✅ | — | Path to input .md file |
| `--config`, `-c` | ❌ | Built-in defaults | Theme config file (JSON or YAML) |
| `--output`, `-o` | ❌ | `<input>_tagged.md` | Output tagged markdown path |
| `--sidecar` | ❌ | Off | Write sidecar JSON (`<output>.tagged.json`) |
| `--dry-run` | ❌ | Off | Print tagged output to stdout without writing |
| `--verbose`, `-v` | ❌ | Off | Enable debug logging |

**Exit Codes:**
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Input file not found |
| 2 | Config file not found or malformed |
| 3 | No events found in input |

**How It Differs from Archived v1:**
- ✅ Negative keyword support (new parameter `negative_keywords` in theme config)
- ✅ `--dry-run` flag
- ✅ Graceful fallback to defaults when config is missing/malformed (instead of `sys.exit(1)`)
- ✅ Supports both new format (dict) and legacy format (list) in config
- ✅ PyYAML is now optional (was a hard import)
- ⚠️ Same event heading regex as v1 (shared with merge.py)

---

### 3.2 `pipeline/index.py` (v1 — New)

**Purpose:** Generate appendix files from tagged chronicle markdown. Produces up to four files.

**Architecture:**
- Reads tagged markdown from `categorize.py` output
- Extracts events with their themes
- Deduplicates events by title (merges themes, keeps longest body, merges sources)
- Generates 4 appendix files using Jinja2 templates (with fallback formatting)

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `load_config(config_path)` | Load index config from JSON; falls back to defaults |
| `extract_events_from_tagged(tagged_md)` | Parse tagged markdown into event dicts (date, title, body, themes, sources, snippet) |
| `deduplicate_events(events, method)` | Dedup by `title` or `date_title`; merges themes/sources, keeps longest body |
| `build_event_index(events)` | Build sorted-by-date event index context |
| `build_theme_index(events)` | Group events by theme |
| `build_source_manifest(events, source_coverage_path)` | Build source contribution summary |
| `build_link_registry(events)` | Extract all URLs, deduplicate, group by domain |
| `render_template(template_name, context, templates_dir)` | Render using Jinja2 or fallback |
| `safe_write(path, content)` | Atomic file write (temp file + rename) |

**CLI Flags:**
| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--input`, `-i` | ✅ | — | Path to tagged .md file |
| `--output-dir`, `-o` | ❌ | `appendix/` | Output directory |
| `--config`, `-c` | ❌ | `index_config.json` | Index config file |
| `--templates-dir`, `-t` | ❌ | `pipeline/templates` | Jinja2 templates directory |
| `--source-coverage`, `-s` | ❌ | Off | Path to `source_coverage.md` |
| `--no-link-registry` | ❌ | Off | Skip link registry generation |
| `--theme-sort` | ❌ | `name` | Theme sort: `name` or `count` |
| `--dedup-method` | ❌ | `title` | Dedup method: `title` or `date_title` |
| `--verbose`, `-v` | ❌ | Off | Enable debug logging |

**Exit Codes:**
| Code | Meaning |
|------|---------|
| 0 | All indices generated successfully |
| 1 | Input file not found or invalid |
| 2 | Template directory missing (only with Jinja2) |
| 3 | Index generation failed |

**Output Files:**

| File | Content |
|------|---------|
| `appendix/event_index.md` | Events sorted by date with themes, table format |
| `appendix/theme_index.md` | Events grouped by theme, one section per theme |
| `appendix/source_manifest.md` | Source contribution table with stats |
| `appendix/link_registry.md` | All external URLs, deduplicated, grouped by domain |

**Template System:**
- Uses 4 Jinja2 templates in `pipeline/templates/`:
  - `event_index.md.j2` — Table of events with links to anchors
  - `theme_index.md.j2` — Events grouped by theme section
  - `source_manifest.md.j2` — Source contribution table
  - `link_registry.md.j2` — URLs by domain
- Falls back to string formatting (`_fallback_render`) when Jinja2 is unavailable
- Each fallback produces a simple markdown table

**Safe Write:**
- Writes to temporary file first (`tempfile.mkstemp`)
- Renames to final destination via `os.replace()` (atomic on Windows)
- Cleans up temp file if write fails

**Deduplication:**
- Default method: `title` (normalize title, merge duplicates)
- Merges themes via set union
- Keeps longest body text
- Deduplicates sources (set union)
- Logs dedup count: `"N events → M unique"`

---

### 3.3 `pipeline/chain.ps1` (v2 — Refactored)

**Purpose:** One-command PowerShell orchestrator for the entire 5-stage pipeline.

**Architecture:**
1. Stage 1 — Ingestion: Runs `ingest.py` on each `.md` file in InputDir
2. Stage 2 — Verification: Runs `verify_ingest.py` (optional, `-Verify` flag)
3. Stage 3 — Merge: Runs `merge.py` with `keep-both` conflict mode
4. Stage 4 — Categorisation: Runs `categorize.py` (optional, skip with `-SkipCategorize`)
5. Stage 5 — Index Generation: Runs `index.py` (optional, skip with `-SkipIndex`)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `-InputDir` | string | ✅ | Directory containing raw `.md` files |
| `-OutputDir` | string | ✅ | Directory for all output files (created if missing) |
| `-ThemesConfig` | string | ❌ | Theme config for categorize.py (JSON or YAML) |
| `-IndexConfig` | string | ❌ | Index config for index.py (JSON) |
| `-Verify` | switch | ❌ | Run verify_ingest.py before merging |
| `-SkipCategorize` | switch | ❌ | Stop after merge, skip stages 4-5 |
| `-SkipIndex` | switch | ❌ | Stop after categorize, skip stage 5 |
| `-NoLinkRegistry` | switch | ❌ | Skip link registry generation |
| `-SourceCoverage` | switch | ❌ | Pass source_coverage.md to index.py |
| `-Verbose` | switch | ❌ | Enable debug logging in all stages |

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | All stages completed successfully |
| 1 | Ingestion stage failed |
| 2 | Verification stage failed (only with `-Verify`) |
| 3 | Merge stage failed |
| 4 | Categorisation stage failed |
| 5 | Index generation failed |

**Script Path Resolution:**
```powershell
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path  # = pipeline/
$IngestPy    = "$ScriptDir/ingest.py"          # pipeline/ingest.py — ❌ MISSING
$VerifyPy    = "$ScriptDir/verify_ingest.py"    # pipeline/verify_ingest.py — ❌ MISSING
$MergePy     = "$ScriptDir/merge.py"            # pipeline/merge.py — ❌ MISSING
$CategorizePy = "$ScriptDir/categorize.py"      # pipeline/categorize.py — ✅ EXISTS
$IndexPy     = "$ScriptDir/index.py"            # pipeline/index.py — ✅ EXISTS
```

**How It Differs from Archived v1:**
- ✅ 5 stages instead of 4 (added Stage 5: Index Generation)
- ✅ `-ThemesConfig` (renamed from `-Config` in v1)
- ✅ `-IndexConfig`, `-SkipIndex`, `-NoLinkRegistry`, `-SourceCoverage` (new)
- ✅ Script validation now also checks `index.py` when not skipped
- ✅ Better summary output with all appendix files listed
- ⚠️ `$ProjectRoot` variable is defined but unused (same as v1)
- ⚠️ `$result` captures stdout+stderr but is only used in verbose mode and on failure

---

### 3.4 `pipeline/themes.json` (New)

**Purpose:** External theme configuration for `categorize.py` defining positive and negative keywords.

**Format:** JSON with `themes` object.

**Themes Defined (6):**

| Theme | Positive Keywords (count) | Negative Keywords (count) |
|-------|--------------------------|---------------------------|
| Web UI | 10 (chat.openai.com, web interface, UI freeze, button disappeared, interface, etc.) | 2 (API interface, command line interface) |
| API/Developer | 13 (API, developer, Linux terminal, simulating, code interpreter, rate limit, token, etc.) | 2 (graphical, GUI) |
| Outages | 11 (server crash, 503 error, downtime, outage, service disruption, etc.) | 5 (meme crash, crash course, trial and error, error in judgment, crash diet) |
| Jailbreaks/Exploits | 9 (jailbreak, DAN, prompt injection, bypass, ignore previous instructions, etc.) | 3 (creative exploit, exploit the system creatively, exploit a loophole creatively) |
| Memory/Personalisation | 9 (memory, chat history, memory feature, custom instructions, bio, remembers, etc.) | 3 (in memory of, memory lane, memory game) |
| Culture/Virality | 10 (viral, mega-viral, Twitter, Reddit, meme, trending, social media, etc.) | 1 (anti-viral) |

---

### 3.5 `pipeline/index_config.json` (New)

**Purpose:** Configuration for `index.py`.

**Format:** JSON with optional fields.

**Default Values:**
```json
{
  "output_dir": "appendix",
  "templates_dir": "pipeline/templates",
  "dedup_method": "title",
  "theme_sort": "name",
  "no_link_registry": false,
  "event_snippet_max_chars": 200
}
```

---

### 3.6 `pipeline/templates/` (New — 4 Jinja2 Templates)

| Template | Purpose | Key Variables |
|----------|---------|---------------|
| `event_index.md.j2` | Table of events sorted by date | `events`, `date_range_start`, `date_range_end` |
| `theme_index.md.j2` | Events grouped by theme | `themes` (dict of theme_name → events) |
| `source_manifest.md.j2` | Source contribution table | `sources`, `total_events`, `sources_with_events`, `sources_without_events` |
| `link_registry.md.j2` | URLs grouped by domain | `links` (dict of domain → links) |

---

## 4. Data Flow (Complete Pipeline)

```
[Input: Raw .md files in -InputDir]
         │
         ▼
[Stage 1] pipeline/ingest.py  ──→  output/normalised/*.md
  (per file: normalize, clean mojibake, extract events, add YAML front-matter)
         │
         ▼ (optional, -Verify)
[Stage 2] pipeline/verify_ingest.py  ──→  stdout verification report
  (batch: verify all files can be ingested)
         │
         ▼
[Stage 3] pipeline/merge.py  ──→  output/merged.md
  (merge all normalised files, dedup by date+hash, conflict mode: keep-both)
                           ──→  output/merged.duplicates.json (if any)
                           ──→  output/merged.source_coverage.md (if supported)
         │
         ▼ (optional, -SkipCategorize to stop here)
[Stage 4] pipeline/categorize.py  ──→  output/chronicle_tagged.md
  (tag events with theme keywords, negative keyword support)
                                  ──→  output/chronicle_tagged.tagged.json
         │
         ▼ (optional, -SkipIndex to stop here)
[Stage 5] pipeline/index.py  ──→  output/appendix/event_index.md
  (generate appendix files)      output/appendix/theme_index.md
                                 output/appendix/source_manifest.md
                                 output/appendix/link_registry.md
```

---

## 5. Key Issues Found

### Critical (Now Fixed)

| # | Issue | Location | Impact | Resolution |
|---|-------|----------|--------|------------|
| 1 | `ingest.py`, `merge.py`, `verify_ingest.py` missing from `pipeline/` | `chain.ps1` lines 79-81 | Stages 1-3 would fail | Copied from `tools/pipeline-chronicle/` (1404-11-25) |
| 2 | `tools/ingest.py` was a markdown design doc with `.py` extension | `tools/ingest.py` | Confusion, wrong file type | Moved to `_ARCHIVE/pipeline-chronicle/notes/ingest_design_notes.md` |

### Moderate (Still Open)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | `$ProjectRoot = Resolve-Path "$ScriptDir/.."` is defined but never used | `chain.ps1` line 78 | Dead code, but harmless |
| 2 | No explicit `-SkipVerify` flag (verify is skip-if-omitted) | `chain.ps1` | Minor UX issue |
| 3 | The `themes.json` at `pipeline/themes.json` is not the default config path | `categorize.py` | User must pass `--config pipeline/themes.json` explicitly |

### Low

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | `$Result` captures stdout+stderr but only displayed in verbose mode | `chain.ps1` | Non-verbose failures show no detail |
| 2 | No output file size/validity check after stages | `chain.ps1` | Can't tell if output is empty |
| 3 | `pipeline/index.py` has `logging.basicConfig` called at module level | Line 69-71 | Cannot be imported silently |

---

## 6. Where the Archived Tools Live

| Tool | Archive Location | Working Copy Location | In `pipeline/`? |
|------|------------------|----------------------|-----------------|
| `ingest.py` | `_ARCHIVE/pipeline-chronicle/tools/ingest.py` | `tools/pipeline-chronicle/ingest.py` | ✅ Yes (copied) |
| `merge.py` | `_ARCHIVE/pipeline-chronicle/tools/merge.py` | `tools/pipeline-chronicle/merge.py` | ✅ Yes (copied) |
| `verify_ingest.py` | `_ARCHIVE/pipeline-chronicle/tools/verify_ingest.py` | `tools/pipeline-chronicle/verify_ingest.py` | ✅ Yes (copied) |
| `categorize.py` (v1) | `_ARCHIVE/pipeline-chronicle/tools/categorize.py` | `tools/pipeline-chronicle/categorize.py` | ✅ Yes (v2 refactored) |
| `chain.ps1` (v1) | `_ARCHIVE/pipeline-chronicle/tools/chain.ps1` | `tools/pipeline-chronicle/chain.ps1` | ✅ Yes (v2 refactored) |

---

## 7. Completed Fixes

### Files Copied into `pipeline/` (from `tools/pipeline-chronicle/`)

All copies are byte-identical (SHA256 verified).

| Source | Destination | Bytes |
|--------|-------------|-------|
| `tools/pipeline-chronicle/ingest.py` | `pipeline/ingest.py` | 16,504 |
| `tools/pipeline-chronicle/merge.py` | `pipeline/merge.py` | 17,345 |
| `tools/pipeline-chronicle/verify_ingest.py` | `pipeline/verify_ingest.py` | 4,444 |

### Misnamed File Archived

`tools/ingest.py` (19,964 bytes) was a markdown design document with a `.py` extension. It contained the initial design notes for `ingest.py` from PIPELINE_PLAN.md. Moved to `_ARCHIVE/pipeline-chronicle/notes/ingest_design_notes.md`.

### Documentation Fixed

- `ARCHITECTURE_AND_MODULES.md` §2 — corrected all `pipeline/ingest.py` references to `tools/pipeline-chronicle/ingest.py`
- `ONTOLOGY_MODEL.md` — added current working copy entries for ingest/merge/verify
- `_ARCHIVE/pipeline-chronicle/ARCHIVE_REPORT.md` — updated with post-archival developments

---

## 8. Pipeline is Now Runnable

After the fixes above, `pipeline/chain.ps1` should work end-to-end with no file-not-found errors (assuming all required Python dependencies are installed).

---
