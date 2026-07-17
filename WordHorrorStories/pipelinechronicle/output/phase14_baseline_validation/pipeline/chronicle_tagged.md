---
sources:
- 01 Archive Report
- 02 Pipeline Plan
- 03 Readme
- 04 Review Plan
- 05 Roadmap
date_range: 2022-01-01 to 2026-07-16
event_count: 50
merged_from: 5
---## Event: 2022-01-01 – ARCHIVE REPORT - 6. Test Results (at Time of Archive
<!-- themes: Categorize/Themes, Merge/Dedup, Orchestration/CLI -->

### 6.1 Ingestion (16 raw files)

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

## Event: 2025-06-01 – ROADMAP - 🎯 Goal
<!-- themes: Categorize/Themes, Merge/Dedup, Orchestration/CLI, Planning/Roadmap -->

Build a set of **Unix‑style composable CLI tools** (each independent, file‑based, no cross-imports)
that automate the workflow described in `WordHorrorStories/chatgpt-chronicle/`.

See [`PIPELINE_PLAN.md`](PIPELINE_PLAN.md) for the full revised implementation plan with stages, priorities, and error-handling specifications.

---

<!-- Duplicate date, different content -->

## Event: 2025-06-01 – ROADMAP - 📋 Tool Status
<!-- themes: Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap, Testing/Verification -->

| # | Tool | Milestone | Status | Target | Dependencies |
|---|------|-----------|--------|--------|--------------|
| 1 | **`ingest.py`** | A1 | ✅ **DONE** | 1404-12-05 | — |
| 2 | **`verify_ingest.py`** | A1 | ✅ **DONE** | 1404-12-05 | `ingest.py` |
| 3 | **`merge.py`** | A2–A3 | ✅ **DONE** | 1404-12-05 | `ingest.py` output |
| 4 | **`categorize.py`** | B1–B3 | ✅ **DONE** | 1404-12-10 | `merge.py` output |
| 5 | **`index.py`** | B2–B4 | ⬜ Pending | 1404-12-15 | `categorize.py` output |
| 6 | **`reference.py`** | C–E | ⬜ Pending | 1404-12-20 | `categorize.py` output |
| 7 | **`chain.sh`** | All | ⬜ Pending | 1404-12-20 | All above |
| — | **`config.json`** | Shared | ⬜ Pending | 1404-12-05 | `ontology.json` |

---

<!-- Duplicate date, different content -->

## Event: 2025-06-01 – ROADMAP - ✅ Completed: `ingest.py` (Milestone A1) — Final Implementation
<!-- themes: Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap, Testing/Verification -->

### What It Does

Converts a raw deep-search `.md` file (with bullet-list events, H2 period headers, mojibake artifacts) into a standard normalised Markdown file with:

- **YAML front-matter**: `source`, `title`, `date` (range), `input_file`, `event_count`
- **Consistent headers**: `# Source: <source>` / `## Event: YYYY-MM-DD – Title`
- **Mojibake cleanup**: 13 broken byte-sequence replacements (always on)
* **Hierarchical event segmentation**: Parses `## Month Year` period headers and `- **Date – Title:**` bullet items
* **Preamble preservation**: Content before first event saved as `> **Overview:**` blockquote

### CLI Flags (Final — 5 flags only)

| Flag | Description |
|------|-------------|
| `--input` / `-i` | Path to raw `.md` file (required) |
| `--output` / `-o` | Normalised output path (default: `<stem>_normalised.md`) |
| `--source-name` | Override auto-detected source name |
| `--date-override` | Force a date (YYYY-MM-DD or YYYY-MM) when file has no parseable dates |
| `--verbose` / `-v` | Enable debug logging |

### Changes Applied (P0/P1 from REVIEW_PLAN.md)

| Fix | Description | Status |
|-----|-------------|--------|
| FIX-1 | Preamble preservation — `extract_preamble()` + `> **Overview:**` blockquote | ✅ |
| FIX-2 | Verification script — `verify_ingest.py` runs all 16 files | ✅ |
| FIX-3 | CLI flag reduction — 11 → 5 essential flags | ✅ |
| FIX-4 | Title extraction — H1 → H2 → `{source} Incidents` fallback | ✅ |
| FIX-5 | Mojibake map cleanup — removed 8 redundant Unicode entries | ✅ |

### Test Results (16 raw files, 224 total events)

| File | Events | Status |
|------|--------|--------|
| `ChatGPTLitrature` | 38 | ✅ |
| `Timeline_of_ChatGPT_Incidents` (3 copies) | 8 each | ✅ |
| `ChatGPT's_Bugs_and_Lore` | 12 | ✅ |
| `Evolution_of_ChatGPT_Hilarious_Bugs` | 19 | ✅ |
| `Hilarious_ChatGPT_Bugs_and_Creative_Uses` | 20 | ✅ |
| `Project_Activity_Summary` | 6 | ✅ |
| `Investigating_AI_Vision` | 9 | ✅ |
| `Desired_Traits_for_chatgpt_customizations` | 4 | ✅ |
| `Word_Horror_Stories_14040517-18` | 92 | ✅ |
| Narrative/essay files (4) | 0 | ✅ Correct — no bullet-list events |
| `ChatGPT_Incidents_Merged` | 0 | ✅ Correct — already normalized |

### Key Design Decisions

1. **Event splitting uses `:**` (colon before closing `**`)** — matches actual raw file format, not `**`:`
2. **Greedy regex for date-title split** — captures full date ranges like "June 10–11" before the separator dash
3. **Period context fallback** — non-parseable dates like "Early June" or items without dates fall back to the H2 period date (e.g., "June 2025" → 2025-06-01)
4. **No cross-imports** — reads from disk, writes to disk; independent CLI tool
5. **Citation links preserved** — `file://` and `https://` citation links are kept as-is
6. **Mojibake always on** — no flag to disable; cleanup is cheap and idempotent
7. **Preamble strips headings** — H1/H2 are already in YAML front-matter; only descriptive text is preserved

### Files

```
tools/pipeline-chronicle/
├── ingest.py          ← ✅ Implemented (all P0/P1 fixes applied)
├── verify_ingest.py   ← ✅ NEW — verification script (FIX-2)
├── ROADMAP.md         ← This file
├── REVIEW_PLAN.md     ← ✅ Updated — all P0/P1 marked done
├── README.md          ← Full spec documentation
└── templates/         ← (pending)
```

---

<!-- Duplicate date, different content -->

## Event: 2025-06-01 – ROADMAP - ✅ Completed: `merge.py` (Milestone A2–A3
<!-- themes: Categorize/Themes, Index/Appendix, Merge/Dedup, Orchestration/CLI, Planning/Roadmap, Testing/Verification -->

### What It Does

Takes multiple normalised `.md` files (output of `ingest.py`) and combines them into a single, deduplicated chronicle with conflict resolution.

### Input
- One or more normalised `.md` files with YAML front-matter and `## Event: YYYY-MM-DD – Title` blocks
- Accepted via `--inputs file1.md file2.md ...` or `--input-dir normalised/`

### Output
1. **`merged.md`** — Unified markdown with YAML front-matter (`sources`, `date_range`, `event_count`, `merged_from`), `# Source: Merged Chronicles` heading, all unique events sorted by date
2. **`merged.duplicates.json`** — Report of duplicate/conflict events
3. **`merged.source_coverage.md`** — (optional) Table of source contributions

### Deduplication Logic

| Scenario | Identifier | Action |
|----------|-----------|--------|
| Same date + same body | `date + sha256(body)` | **True duplicate** — keep first, record in duplicates report |
| Same date + different body | `date` (hash differs) | **Conflict** — behaviour depends on `--conflict-mode` |
| Different date | `date` | **Unique** — always keep |

### Conflict Modes

| Mode | Behaviour |
|------|-----------|
| `keep-both` (default) | Keep all conflicting events; annotate second+ with `<!-- Duplicate date, different content -->` |
| `manual` | Omit all conflicting events from merged output; write all to duplicates report |
| `skip` | Keep first occurrence; silently drop rest with warning in duplicates report |

### CLI Flags (6 flags)

| Flag | Description |
|------|-------------|
| `--inputs` / `-i` | One or more normalised `.md` files (mutually exclusive with `--input-dir`) |
| `--input-dir` / `-d` | Directory of normalised `.md` files (mutually exclusive with `--inputs`) |
| `--output` / `-o` | Output merged markdown path (default: `merged.md`) |
| `--conflict-mode` | `keep-both` (default), `manual`, or `skip` |
| `--source-coverage` | Also generate `source_coverage.md` table |
| `--verbose` / `-v` | Enable debug logging |

### Error Handling

| Condition | Behaviour |
|-----------|-----------|
| No input files found | Exit with error, list searched paths |
| File not found | Exit with error, show missing path |
| File has no YAML front-matter | Warning, treat as body-only |
| File has no `## Event:` headings | Warning, skip file (0 events contributed) |
| Malformed YAML front-matter | Warning, treat as body-only |
| Empty event body after heading | Warning, still include (date-only event) |
| Duplicate file paths | Warning, skip duplicate |

### Test Results (5 normalised files)

| Mode | Events | Duplicates | Behaviour |
|------|--------|------------|-----------|
| `keep-both` | 40 | 0 true duplicates | 8 date conflicts resolved by keeping all variants |
| `skip` | 17 | 23 conflicts | Only first occurrence per date kept |
| `manual` | 9 | 31 conflicts | Only unique dates without conflicts kept |

### Key Design Decisions

1. **Identifier = `(date, sha256(body))`** — catches true duplicates even if titles differ slightly
2. **Body normalisation** — collapses all whitespace before hashing for robust comparison
3. **Source tracking** — each event records which source files contributed it
4. **Front-matter event_count** — computed from `len(final_events)` not from `## Event:` count in body (body text may contain `## Event:` as citation text)
5. **No cross-imports** — reads from disk, writes to disk; independent CLI tool

### Files

```
tools/pipeline-chronicle/
├── ingest.py              ← ✅ Implemented (all P0/P1 fixes applied)
├── verify_ingest.py       ← ✅ Verification script (FIX-2)
├── merge.py               ← ✅ Merge + dedup + conflict resolution
├── categorize.py          ← ✅ NEW — theme tagging with config-driven keywords
├── PIPELINE_PLAN.md        ← ✅ Revised stage-based implementation plan
├── ROADMAP.md             ← This file
├── REVIEW_PLAN.md         ← ✅ Updated — all P0/P1 marked done
├── README.md              ← Full spec documentation
└── templates/             ← (pending)
```

---

<!-- Duplicate date, different content -->

## Event: 2025-06-01 – ROADMAP - ✅ Completed: `categorize.py` (Milestone B1–B3
<!-- themes: Archive/Refactor, Categorize/Themes, Merge/Dedup, Orchestration/CLI, Testing/Verification -->

### What It Does

Reads a normalised or merged chronicle file and tags each event with theme labels using config-driven keyword matching.

### Input
- A markdown file with `## Event: YYYY-MM-DD – Title` blocks (output of `ingest.py` or `merge.py`)
- Optional JSON or YAML config file with a `themes` key

### Output
1. **`tagged.md`** — Same structure as input, with `<!-- themes: X, Y -->` comments after each event heading
2. **`tagged.tagged.json`** — (optional, with `--sidecar`) Structured JSON with per-event tag data

### CLI Flags (5 flags)

| Flag | Description |
|------|-------------|
| `--input` / `-i` | Path to input `.md` file (required) |
| `--config` / `-c` | JSON or YAML config file (optional; uses built-in defaults if omitted) |
| `--output` / `-o` | Path for tagged output (default: `<input>_tagged.md`) |
| `--sidecar` | Also write a sidecar JSON file |
| `--verbose` / `-v` | Enable debug logging |

### Key Design Decisions

1. **Substring matching, not word-boundary regex** — Keywords like `chat.openai.com` and `503 error` contain special chars that break `\b` word boundaries. Simple `in` operator is more robust.
2. **Built-in defaults** — `--config` is optional. 6 themes with 48 keywords are built in.
3. **JSON + YAML config** — Supports both formats transparently.
4. **Non-destructive** — Only adds comments; never alters original content.

### Test Results

| Config | Events | Tagged | Notes |
|--------|--------|--------|-------|
| Built-in defaults (6 themes, 48 keywords) | 28 | 27 | 1 event had no matching keywords |
| Custom JSON (2 themes, 6 keywords) | 28 | 11 | Only Web UI and Outages matched |
| Custom YAML (2 themes, 5 keywords) | 28 | 20 | Culture/Virality matched many events |

---

<!-- Duplicate date, different content -->

## Event: 2025-06-01 – ROADMAP - ⬜ Future: `categorize.py` (Milestone B1–B3
<!-- themes: Categorize/Themes, Merge/Dedup -->

### Requirements

- Read merged MD, map keywords to ontology classes
- Assign theme tags (Web UI, API/Developer, Outages, Jailbreaks/Exploits, Memory/Personalisation, Culture/Virality)
- Add as inline annotations or sidecar JSON

---

<!-- Duplicate date, different content -->

## Event: 2025-06-01 – ROADMAP - ⬜ Future: `index.py` (Milestone B2–B4
<!-- themes: Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup -->

### Requirements

- Regenerate appendix files: `event_index.md`, `theme_index.md`, `source_manifest.md`, `link_registry.md`
- Use Jinja2 templates from `templates/` directory

---

<!-- Duplicate date, different content -->

## Event: 2025-06-01 – ROADMAP - ⬜ Future: `reference.py` (Milestone C–E
<!-- themes: Merge/Dedup -->

### Requirements

- Build header map, topic model, cross-reference anchors
- Stable anchor IDs that survive re-merges

---

<!-- Duplicate date, different content -->

## Event: 2025-06-01 – ROADMAP - ⬜ Future: `chain.sh` (Milestone All
<!-- themes: Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI -->

### Requirements

- One-command wrapper: `ingest → merge → categorize → index`

---

<!-- Duplicate date, different content -->

## Event: 2025-06-01 – ROADMAP - 🔗 Cross-References
<!-- themes: Ingest/Normalise, Planning/Roadmap -->

| Resource | Link |
|----------|------|
| Project Roadmap | [`ROADMAP.md`](../../ROADMAP.md) |
| Project Plan | [`PLAN.md`](../../PLAN.md) |
| Full Spec | [`README.md`](README.md) |
| Source Code | [`ingest.py`](ingest.py) |
| Ontology | [`ontology.json`](../../ontology.json) |
| Raw Sources | `WordHorrorStories/chatgpt-chronicle/sources/raw/chatgpt_mds/` |
| Normalised Output | `WordHorrorStories/chatgpt-chronicle/sources/normalised/` |

---

## Event: 2025-08-06 – README - 🚦 Build Order (Prioritised
<!-- themes: Archive/Refactor, Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap -->

### 1. `ingest.py` — Highest Priority
**Milestone:** A1  
**Target:** 1404-12-05

Converts a single raw deep‑search file (any `.md` with file:// or https:// citation links) into a standard normalised Markdown file with:

- Extracted title, source date, source attribution
- Consistent headers (`# Source: xxx`, `## Event: yyy`, `### Evidence: zzz`)
- YAML front‑matter block: `date`, `source_name`, `source_url`, `ontology_classes`, `themes`
- Stripped mojibake (the –, ’ patterns seen in existing files)

**CLI Flags:**
```
--input <path>              # Raw deep‑search .md file
--output <path>             # Normalised output .md
--config <path>             # Optional: config.json for header hints
--source-name <str>         # Override auto‑detected source name
--date-format <str>         # Default: %Y-%m-%d
--date-override <str>       # Force a date if not extractable
--metadata-only             # Only print extracted metadata, skip full conversion
--verbose
```

**Example:**
```powershell
python tools/pipeline-chronicle/ingest.py `
  --input "WordHorrorStories/chatgpt-chronicle/sources/raw/chatgpt_mds/2025-08-06-ChatGPT_Agent_Mode_-_Bugs,_Exploits,_and_Cultural_Phenomena_(June-July_2025).md" `
  --output "WordHorrorStories/chatgpt-chronicle/sources/normalised/2025-08-06-chatgpt-agent-mode.md" `
  --source-name "ChatGPT Agent Mode Report" `
  --verbose
```

---

### 2. `merge.py` — Highest Priority
**Milestone:** A2–A3  
**Target:** 1404-12-05

Reads multiple normalised MD files (or a directory), diffs by date + content hash (SHA256, matching `ontology.json`'s `sha256` field), merges unique entries, flags duplicates in a report, and updates `source_coverage.md`.

**Dedup Logic:**
| Method | Behaviour |
|--------|-----------|
| `hash` | Exact content match → keep first, flag rest |
| `date` | Same date → keep most recent source, flag others |
| `hash+date` (default) | Same hash **or** same date → dedup; contents differ but same date → flag for manual review |
| `none` | Concatenate all entries (no dedup) |

**CLI Flags:**
```
--input file1.md file2.md ...  # One or more normalised files
--input-dir <path>             # Directory of normalised files (scanned recursively)
--output <path>                # Merged output .md
--dedup-method <str>           # hash | date | hash+date | none (default: hash+date)
--duplicates-report <path>     # JSON report of flagged duplicates (default: dupes.json)
--no-dedup                     # Skip dedup entirely
--update-source-coverage       # Write/update appendix/source_coverage.md
--verbose
```

**Example:**
```powershell
python tools/pipeline-chronicle/merge.py `
  --input-dir "WordHorrorStories/chatgpt-chronicle/sources/normalised/" `
  --output "WordHorrorStories/chatgpt-chronicle/sources/merged/merged_chronicle.md" `
  --duplicates-report "_ARCHIVE/logs/chronicle_dupes.json" `
  --update-source-coverage
```

---

### 3. `categorize.py` — High Priority
**Milestone:** B1–B3  
**Target:** 1404-12-10

Reads the merged MD, maps keywords to ontology classes (from `config.json` → loaded from `ontology.json`), assigns theme tags (Web UI, API/Developer, Outages, Jailbreaks/Exploits, Memory/Personalisation, Culture/Virality), and adds them as inline annotations or a sidecar JSON.

**Theme Categories** (matching `WordHorrorStories/chatgpt-chronicle/appendix/theme_index.md`):

| Theme | Keyword Hints (from config.json) |
|-------|----------------------------------|
| Web UI | web interface, chat.openai.com, UI, interface, website |
| API / Developer | api.openai.com, API, developer, function calling, SDK |
| Outages | outage, down, error, unavailable, downtime, 503, 500 |
| Jailbreaks / Exploits | jailbreak, exploit, DAN, grandma, prompt injection, bypass |
| Memory / Personalisation | memory, history, chat history, ghost memory, profile |
| Culture / Virality | meme, viral, lore, Reddit, Twitter, persona, trend |

**CLI Flags:**
```
--input <path>               # Merged .md
--output <path>              # Tagged output .md (or sidecar .json)
--config <path>              # Config file (loads ontology.json classes + theme keywords)
--method keyword             # keyword | (future) nlp
--tag-style inline           # inline (<!-- ontology:Claim theme:Outages -->) or sidecar
--theme-model <path>         # Override theme definitions (default: from --config)
--no-themes                  # Skip theme assignment
--verbose
```

**Example:**
```powershell
python tools/pipeline-chronicle/categorize.py `
  --input "WordHorrorStories/chatgpt-chronicle/sources/merged/merged_chronicle.md" `
  --output "WordHorrorStories/chatgpt-chronicle/sources/merged/merged_chronicle_tagged.md" `
  --config "tools/pipeline-chronicle/config.json" `
  --tag-style inline
```

---

### 4. `index.py` — Medium Priority
**Milestone:** B2–B4  
**Target:** 1404-12-15

Reads the tagged (or untagged) merged MD and **regenerates** the four appendix files that already exist as shells in `WordHorrorStories/chatgpt-chronicle/appendix/`:

| Appendix | Generated File | Content |
|----------|----------------|---------|
| A — Source Coverage | `appendix/source_coverage.md` | Which sources are merged/dropped/kept, with notes |
| B — Event Index | `appendix/event_index.md` | Events sorted by date, linked to Parts/Exhibits |
| C — Link Registry | `appendix/link_registry.md` | All external URLs extracted, with where‑used references |
| D — Theme Index | `appendix/theme_index.md` | Entries grouped by theme with links |
| E — (future) Gloss | `appendix/gloss.md` | Terms and entities extracted during categorisation |

**CLI Flags:**
```
--input <path>               # Tagged merged .md
--output-dir <path>          # Target appendix directory (default: WordHorrorStories/.../appendix/)
--config <path>              # Config file (templates, footer text, etc.)
--templates <path>           # Jinja2 template directory (default: templates/)
--update                     # Append/refresh existing indices instead of overwriting
--no-source-manifest         # Skip source_manifest.md generation
--no-event-index             # Skip event_index.md generation
--no-link-registry           # Skip link_registry.md generation
--verbose
```

**Example:**
```powershell
python tools/pipeline-chronicle/index.py `
  --input "WordHorrorStories/chatgpt-chronicle/sources/merged/merged_chronicle_tagged.md" `
  --output-dir "WordHorrorStories/chatgpt-chronicle/appendix/" `
  --config "tools/pipeline-chronicle/config.json" `
  --update
```

---

### 5. `reference.py` — Lower Priority (Nice‑to‑Have)
**Milestone:** C–E  
**Target:** 1404-12-20

Builds a **general‑to‑specific header map**, a topic model, and cross‑reference anchors for the merged chronicle. This is what enables "future AI iteration" references — stable anchor IDs that survive re‑merges.

**Header Taxonomy** (defined in `config.json`):
```
H1: Domain         → e.g., "ChatGPT Incidents"
H2: Period         → e.g., "June 2025"
H3: Event          → e.g., "34-Hour Global Outage"
H4: Evidence       → e.g., "User Report #42"
```

Each header gets a stable anchor ID (e.g., `#event-34hr-outage`) that can be referenced in future AI prompts.

**CLI Flags:**
```
--input <path>               # Tagged merged .md
--output-dir <path>          # Output reference directory
--config <path>              # Config file with header taxonomy
--generate-toc               # Generate secondary TOC from header structure
--topic-model <path>         # Write topic model to this file
--anchor-style <str>         # github | jira (default: github)
--nlp                        # (future) enable POS/entity extraction
--verbose
```

---

### 6. `chain.sh` — Convenience Wrapper
**Milestone:** All  
**Target:** 1404-12-20

A shell script that runs `ingest → merge → categorize → index` in sequence with sensible defaults.

```bash
# Run full pipeline on all raw sources
./chain.sh --input-dir "WordHorrorStories/chatgpt-chronicle/sources/raw/chatgpt_mds/"
           --output-dir "WordHorrorStories/chatgpt-chronicle/sources/normalised/"
           --merged "WordHorrorStories/chatgpt-chronicle/sources/merged/merged_chronicle.md"
           --appendix "WordHorrorStories/chatgpt-chronicle/appendix/"
```

---

<!-- Duplicate date, different content -->

## Event: 2025-08-06 – README - 📋 Example End-to-End Workflow
<!-- themes: Archive/Refactor, Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI -->

```powershell
# 1. Ingest two raw deep-search files
python tools/pipeline-chronicle/ingest.py `
  --input "WordHorrorStories/chatgpt-chronicle/sources/raw/chatgpt_mds/2025-08-06-ChatGPT_Agent_Mode_-_Bugs,_Exploits,_and_Cultural_Phenomena_(June-July_2025).md" `
  --output "WordHorrorStories/chatgpt-chronicle/sources/normalised/agent_mode.md" `
  --source-name "Agent Mode Deep Report"

python tools/pipeline-chronicle/ingest.py `
  --input "WordHorrorStories/chatgpt-chronicle/sources/raw/chatgpt_mds/2025-08-06-ChatGPT's_Bugs_&_Lore_-_May_to_July_2025_Timeline.md" `
  --output "WordHorrorStories/chatgpt-chronicle/sources/normalised/bugs_lore_may_jul.md" `
  --source-name "Bugs & Lore Timeline"

# 2. Merge
python tools/pipeline-chronicle/merge.py `
  --input-dir "WordHorrorStories/chatgpt-chronicle/sources/normalised/" `
  --output "WordHorrorStories/chatgpt-chronicle/sources/merged/merged.md" `
  --duplicates-report "_ARCHIVE/logs/chronicle_dupes.json" `
  --update-source-coverage

# 3. Categorise
python tools/pipeline-chronicle/categorize.py `
  --input "WordHorrorStories/chatgpt-chronicle/sources/merged/merged.md" `
  --output "WordHorrorStories/chatgpt-chronicle/sources/merged/merged_tagged.md" `
  --config "tools/pipeline-chronicle/config.json"

# 4. Generate appendices
python tools/pipeline-chronicle/index.py `
  --input "WordHorrorStories/chatgpt-chronicle/sources/merged/merged_tagged.md" `
  --output-dir "WordHorrorStories/chatgpt-chronicle/appendix/" `
  --config "tools/pipeline-chronicle/config.json" `
  --update

# 5. (Optional) Build reference system
python tools/pipeline-chronicle/reference.py `
  --input "WordHorrorStories/chatgpt-chronicle/sources/merged/merged_tagged.md" `
  --output-dir "WordHorrorStories/chatgpt-chronicle/reference/" `
  --config "tools/pipeline-chronicle/config.json" `
  --generate-toc
```

---

## Event: 2026-02-14 – ARCHIVE REPORT - 1. Overview
<!-- themes: Archive/Refactor, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Testing/Verification -->

This archive contains the original **chronicle pipeline tools** — a set of four independent Python CLI tools and one PowerShell orchestrator (`chain.ps1`) that automate the workflow of normalising, merging, categorising, and verifying raw deep-search markdown files into a structured chronicle.

The tools were built for the `WordHorrorStories/chatgpt-chronicle/` dataset (16 raw files, ~224 events) and were validated end-to-end.

---

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – ARCHIVE REPORT - 2. Tool Inventory
<!-- themes: Archive/Refactor, Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap, Testing/Verification -->

| # | File | Lines | Role | Status at Archive | Current Working Copy |
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

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – ARCHIVE REPORT - 3. Architecture & Design
<!-- themes: Categorize/Themes, Index/Appendix, Merge/Dedup, Orchestration/CLI, Testing/Verification -->

### 3.1 Design Principles

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

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – ARCHIVE REPORT - 4. CLI Signatures (Complete Reference
<!-- themes: Categorize/Themes, Merge/Dedup, Orchestration/CLI, Testing/Verification -->

### 4.1 `ingest.py`

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

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – ARCHIVE REPORT - 5. Known Issues & Critique (at Time of Archive
<!-- themes: Archive/Refactor, Categorize/Themes, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap, Testing/Verification -->

### 5.1 Issues Fixed Before Archive

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

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – ARCHIVE REPORT - 7. Ontology Cross-Reference
<!-- themes: Categorize/Themes, Ingest/Normalise, Merge/Dedup, Orchestration/CLI -->

| Pipeline Concept | Ontology Class | Relation |
|------------------|----------------|----------|
| `ingest.py` run | `ActivityPeriod(name="Chronicle Ingestion")` | `produces → Artifact(path=normalised/*.md)` |
| `merge.py` run | `ActivityPeriod(name="Chronicle Merge")` | `consumes → normalised/*.md` → `produces → merged/*.md` |
| `categorize.py` run | `ActivityPeriod(name="Chronicle Categorisation")` | `states → Claim(text="Event X is tagged as Outages")` |
| Merged event entry | `Claim(subtype=EvidenceClaim)` | `verified_by → Verification(method=inspection)` |
| Source attribution | `Artifact(kind=evidence)` | `produced_by → ActivityPeriod` |

---

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – ARCHIVE REPORT - 8. File Checksums
<!-- themes: Archive/Refactor, Categorize/Themes, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Testing/Verification -->

```
SHA256 (ingest.py)         = <computed at archive time>
SHA256 (merge.py)          = <computed at archive time>
SHA256 (categorize.py)     = <computed at archive time>
SHA256 (verify_ingest.py)  = <computed at archive time>
SHA256 (chain.ps1)         = <computed at archive time>
```

---

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – ARCHIVE REPORT - 9. Restoration Instructions
<!-- themes: Archive/Refactor, Categorize/Themes, Ingest/Normalise, Merge/Dedup, Orchestration/CLI -->

To restore and use the archived tools:

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

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – ARCHIVE REPORT - 10. Post-Archival Developments (Phase 9b
<!-- themes: Archive/Refactor, Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Testing/Verification -->

After archival, a second development session (22:29-22:52 same day) refactored and extended the pipeline:

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

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – ARCHIVE REPORT - 11. Change Log
<!-- themes: Archive/Refactor, Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Testing/Verification -->

| Date | Change |
|------|--------|
| 2026-02-14 | Phase 9b post-archival update: refactored categorize.py, chain.ps1; built index.py, themes.json, index_config.json, templates/; copied ingest/merge/verify into pipeline/; archived misnamed tools/ingest.py; fixed ARCHITECTURE_AND_MODULES.md paths |
| 2026-02-14 | Initial archive — all 5 tools + 4 docs archived |

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – README - 🧱 What This Is
<!-- themes: Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI -->

A set of **Unix‑style composable CLI tools** (each independent, file‑based, no cross‑imports)
that automate the workflow described in `WordHorrorStories/chatgpt-chronicle/`:

> Two (or more) heavily‑marked‑up deep‑search files → normalised Markdown → merged, deduped, categorised → auto‑generated appendices (event index, theme index, source manifest, link registry) → cross‑reference system for future AI iteration.

Each tool reads from disk, writes to disk, accepts flags — never imports another tool's Python code.

---

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – README - 📁 Directory Structure
<!-- themes: Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI -->

```
tools/pipeline-chronicle/
├── config.json              # Shared ontology + themes + header taxonomy (loaded by all tools)
├── ingest.py                # deep‑search raw file → normalised MD + YAML front‑matter
├── merge.py                 # N normalised MDs → deduped merged MD + duplicates report
├── categorize.py            # merged MD → tagged with ontology classes + theme labels
├── index.py                 # tagged MD → event_index, theme_index, source_manifest, link_registry
├── reference.py             # taggged MD → header map, secondary TOC, topic model, anchor IDs
├── chain.sh                 # (optional) wrapper: runs ingest → merge → categorize → index
├── README.md                # this file
└── templates/               # Jinja2 templates for appendix generation
    ├── event_index.md.j2
    ├── theme_index.md.j2
    ├── source_manifest.md.j2
    └── link_registry.md.j2
```

---

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – README - 🔧 Design Principles
<!-- themes: Categorize/Themes, Ingest/Normalise, Merge/Dedup, Orchestration/CLI -->

| Principle | How It's Achieved |
|-----------|-------------------|
| **Independent** | Every tool reads from disk; no Python cross-imports. |
| **Parameterised** | All behaviour via CLI flags (`--input`, `--output`, `--config`, `--no-dedup`, ...). |
| **Boolean toggles** | Flags like `--no-dedup`, `--no-themes`, `--verbose`. |
| **Config‑driven** | `config.json` contains ontology classes, theme keywords, header taxonomy. |
| **Idempotent** | Same command + same inputs → same output. `merge.py` can be re‑run with new sources. |
| **Composable** | Output of one tool is input to the next. Run individually or via `chain.sh`. |

---

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – README - 🔗 Relationship to Existing Project Files
<!-- themes: Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap -->

| Existing File | How Pipeline Uses It |
|---------------|---------------------|
| `ontology.json` | Config file loads ontology classes & relations for categorisation |
| `WordHorrorStories/chatgpt-chronicle/appendix/event_index.md` | **Target** of `index.py` — regenerates from tagged merged MD |
| `WordHorrorStories/chatgpt-chronicle/appendix/theme_index.md` | **Target** of `index.py` — auto‑populated from tagged entries |
| `WordHorrorStories/chatgpt-chronicle/appendix/source_manifest.md` | **Target** of `index.py` — lists sources with merge/drop decisions |
| `WordHorrorStories/chatgpt-chronicle/appendix/link_registry.md` | **Target** of `index.py` — extracts external links |
| `WordHorrorStories/chatgpt-chronicle/appendix/source_coverage.md` | Updated by `merge.py` — merged/dropped/notes per source |
| `WordHorrorStories/chatgpt-chronicle/book/02_master_current.md` | **Consumed by** `categorize.py` and `reference.py` for Topic Model |
| `WordHorrorStories/chatgpt-chronicle/sources/raw/chatgpt_mds/*.md` | **Input** to `ingest.py` — raw deep‑search MD files |
| `WordHorrorStories/chatgpt-chronicle/sources/dropped/` | Populated by `merge.py` when sources are flagged as duplicates |
| `WordHorrorStories/chatgpt-chronicle/sources/raw/chatgpt_mds/ChatGPT_Incidents_Merged.md` | Example of a **manual merge** that `merge.py` will automate |

---

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – README - ⚙️ Shared Configuration: `config.json
<!-- themes: Categorize/Themes, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Testing/Verification -->

All tools accept `--config <path>` pointing to a single file. The config loads the project's own `ontology.json` and adds theme keywords + header taxonomy:

```json
{
  "meta": {
    "title": "WHS Chronicle Pipeline Config",
    "version": "1.0.0",
    "date_jalali": "1404-11-25"
  },
  "ontology_source": "ontology.json",
  "themes": {
    "Web UI": ["web interface", "chat.openai.com", "UI", "interface", "website", "web app"],
    "API / Developer": ["api.openai.com", "API", "developer", "SDK", "function calling", "endpoint"],
    "Outages / Regressions": ["outage", "down", "error", "unavailable", "downtime", "503", "500", "regression"],
    "Jailbreaks / Exploits": ["jailbreak", "exploit", "DAN", "grandma", "prompt injection", "bypass", "filter bypass"],
    "Memory / Personalisation": ["memory", "history", "chat history", "ghost memory", "profile", "recall", "personalisation"],
    "Culture / Virality": ["meme", "viral", "lore", "Reddit", "Twitter", "persona", "trend", "cultural"]
  },
  "header_taxonomy": {
    "H1": "Domain",
    "H2": "Period",
    "H3": "Event",
    "H4": "Evidence"
  },
  "dedup": {
    "method": "hash+date",
    "hash_algorithm": "sha256"
  }
}
```

Each tool reads only the relevant section. CLI flags can override config values (e.g., `--dedup-method`).

---

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – README - 🔗 Ontology Cross-Reference
<!-- themes: Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI -->

| Pipeline Concept | Ontology Class (from `ontology.json`) | Relation |
|------------------|---------------------------------------|----------|
| `ingest.py` run | `ActivityPeriod(name="Chronicle Ingestion")` | `produces → Artifact(path=normalised/*.md)` |
| `merge.py` run | `ActivityPeriod(name="Chronicle Merge")` | `consumes → normalised/*.md` → `produces → merged/*.md` |
| `categorize.py` run | `ActivityPeriod(name="Chronicle Categorisation")` | `states → Claim(text="Event X is tagged as Outages")` |
| `index.py` run | `ActivityPeriod(name="Chronicle Indexing")` | `produces → appendix/event_index.md, theme_index.md, ...` |
| `reference.py` run | `ActivityPeriod(name="Chronicle Reference")` | `produces → reference/topic_model.md` |
| Merged event entry | `Claim(subtype=EvidenceClaim)` | `verified_by → Verification(method=inspection)` |
| Source attribution | `Artifact(kind=evidence)` | `produced_by → ActivityPeriod` |

---

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – README - 📝 Change Log
<!-- themes: Merge/Dedup, Planning/Roadmap -->

| Date (Gregorian) | Date (Jalali) | Change |
|------------------|---------------|--------|
| 2026-02-14 | 1404-11-25 | Initial plan created — 6 tools defined, mapped to existing project structure |

---

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – README - See Also
<!-- themes: Index/Appendix, Merge/Dedup, Planning/Roadmap -->

- `ontology.json` — Machine-readable ontology loaded by `config.json`
- `ONTOLOGY.md` — Human-readable ontology index
- `ONTOLOGY_MODEL.md` — Detailed ontology with full instance tables
- `PLAN.md` — Project plan with phase targets (P9 planned)
- `WordHorrorStories/chatgpt-chronicle/book/02_master_current.md` — Target book structure
- `docs/README.md` — All project documentation

<!-- Duplicate date, different content -->

## Event: 2026-02-14 – ROADMAP - 📝 Change Log
<!-- themes: Categorize/Themes, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap -->

| Date (Gregorian) | Date (Jalali) | Change |
|------------------|---------------|--------|
| 2026-02-14 | 1404-11-25 | Created — `ingest.py` completed and documented |
| 2026-02-14 | 1404-11-25 | **All P0/P1 fixes applied:** preamble preservation, verification script, CLI reduction (11→5), title fallback, mojibake cleanup. `REVIEW_PLAN.md` updated to reflect completion. |
| 2026-02-14 | 1404-11-25 | **`merge.py` implemented** with 3 conflict modes, source coverage, duplicates report. `PIPELINE_PLAN.md` created with revised stage-based plan. `ROADMAP.md` updated to reflect 2/6 tools complete. |
| 2026-02-14 | 1404-11-25 | **`categorize.py` implemented** with built-in default themes, JSON+YAML config, substring matching, sidecar JSON. Critique-driven fixes applied to `merge.py` (duplicate import, source_names return, event count from front-matter). `PIPELINE_PLAN.md` and `ROADMAP.md` updated to reflect 3/7 tools complete. |

## Event: 2026-07-16 – PIPELINE PLAN - 🎯 Design Principles
<!-- themes: Merge/Dedup, Orchestration/CLI, Testing/Verification -->

1. **Modularity** — Each tool is independent, file-based, no cross-imports. They communicate only through files on disk.
2. **Error resilience** — Every tool validates inputs at the start, fails fast with clear messages, and never silently corrupts data.
3. **Minimal flags** — Each tool exposes only the flags needed for its single responsibility. Configuration belongs in files, not CLI args.
4. **Deterministic output** — Same inputs → same outputs. No randomness, no environment-dependent behavior.
5. **Backward compatibility** — Output format of each tool is the input contract for the next. Changes must be coordinated.

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – PIPELINE PLAN - 📋 Stage Overview
<!-- themes: Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap, Testing/Verification -->

| Stage | Tools | Milestone | Status | Target |
|-------|-------|-----------|--------|--------|
| **1 — Ingestion** | `ingest.py`, `verify_ingest.py` | A1 | ✅ **DONE** | 1404-12-05 |
| **2 — Merge** | `merge.py` | A2–A3 | ✅ **DONE** | 1404-12-05 |
| **3 — Categorisation** | `categorize.py`, `config.json` | B1–B3 | ✅ **DONE** | 1404-12-10 |
| **4 — Indexing** | `index.py`, `templates/` | B2–B4 | ⬜ Pending | 1404-12-15 |
| **5 — Reference** | `reference.py` | C–E | ⬜ Pending | 1404-12-20 |
| **6 — Automation** | `chain.sh` | All | ⬜ Pending | 1404-12-20 |

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – PIPELINE PLAN - ✅ Stage 1: Ingestion (Complete
<!-- themes: Archive/Refactor, Categorize/Themes, Ingest/Normalise, Merge/Dedup, Testing/Verification -->

### Tools
- **`ingest.py`** — Normalises raw deep-search `.md` → standard chronicle format
- **`verify_ingest.py`** — Batch verification against all 16 raw files

### Output Contract (Input Contract for Stage 2)

Every normalised file has this structure:

```yaml
---
source: <source_name>
title: <derived_title>
input_file: <original_filename>
event_count: <int>
date: <YYYY-MM-DD> or <YYYY-MM-DD to YYYY-MM-DD>
---
# Source: <source_name>

> **Overview:** <optional preamble text>

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – PIPELINE PLAN - Event: YYYY-MM-DD – Title
<!-- themes: Merge/Dedup -->

<body text>

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – PIPELINE PLAN - Event: YYYY-MM-DD – Another Title
<!-- themes: Merge/Dedup, Testing/Verification -->

<body text>
...
```

### Verification Results
- **16 files processed**, **224 total events**
- **4 narrative files** correctly yield 0 events (no bullet-list structure)
- **12 timeline files** yield correct event counts (range: 4–92)
- **0 errors**, **0 regressions**

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – PIPELINE PLAN - ✅ Stage 2: Merge (Complete
<!-- themes: Categorize/Themes, Merge/Dedup, Orchestration/CLI -->

### Tool: `merge.py`

**Role:** Take multiple normalised `.md` files → single deduplicated chronicle.

### Input Contract
- One or more files matching the Stage 1 output format
- Accepted via `--inputs file1.md file2.md ...` or `--input-dir normalised/`

### Output Contract
1. **`merged.md`** — Unified markdown with:
   - YAML front-matter: `sources` (list), `date_range`, `event_count`, `merged_from` (count)
   - `# Source: Merged Chronicles` heading
   - All unique events, sorted by date ascending
   - Each event block left **exactly** as in input (unchanged)

2. **`merged.duplicates.json`** — Report of duplicate/conflict events

3. **`merged.source_coverage.md`** — Table of source contributions (optional, generated when `--source-coverage` flag is set)

### Deduplication Logic

| Scenario | Identifier | Action |
|----------|-----------|--------|
| Same date + same body | `date + sha256(body)` | **True duplicate** — keep first occurrence, record in duplicates report |
| Same date + different body | `date` (hash differs) | **Conflict** — behaviour depends on `--conflict-mode` |
| Different date | `date` | **Unique** — always keep |

### Conflict Modes

| Mode | Behaviour |
|------|-----------|
| `keep-both` (default) | Keep all conflicting events; annotate second+ with `<!-- Duplicate date, different content -->` |
| `manual` | Omit all conflicting events from merged output; write all to `conflicts.md` for human review |
| `skip` | Keep first occurrence; silently drop rest with warning in duplicates report |

### CLI Flags (6 flags)

| Flag | Description |
|------|-------------|
| `--inputs` / `-i` | One or more normalised `.md` files (mutually exclusive with `--input-dir`) |
| `--input-dir` / `-d` | Directory of normalised `.md` files (mutually exclusive with `--inputs`) |
| `--output` / `-o` | Output merged markdown path (default: `merged.md`) |
| `--conflict-mode` | `keep-both` (default), `manual`, or `skip` |
| `--source-coverage` | Also generate `source_coverage.md` table |
| `--verbose` / `-v` | Enable debug logging |

### Error Handling

| Condition | Behaviour |
|-----------|-----------|
| No input files found | Exit with error, list searched paths |
| File not found | Exit with error, show missing path |
| File has no YAML front-matter | Warning, treat as body-only |
| File has no `## Event:` headings | Warning, skip file (0 events contributed) |
| Malformed YAML front-matter | Warning, treat as body-only |
| Empty event body after heading | Warning, still include (date-only event) |
| Duplicate file paths | Warning, skip duplicate |

### Critique-Driven Fixes Applied

| Issue | Fix |
|-------|-----|
| `import yaml as _yaml` inside `main()` | Removed duplicate import; uses module-level `yaml` |
| Source coverage used `file.stem` not source name | `merge_files()` now returns `source_names` list; `main()` uses it directly |
| `## Event:` in body text inflated count | Event count read from front-matter YAML, not from `str.count()` |

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – PIPELINE PLAN - ✅ Stage 3: Categorisation (Complete
<!-- themes: Archive/Refactor, Categorize/Themes, Merge/Dedup, Orchestration/CLI, Testing/Verification -->

### Tool: `categorize.py`

**Role:** Read merged chronicle, tag each event with thematic categories.

### Input Contract
- `merged.md` from Stage 2 (or any normalised file with `## Event:` blocks)
- Optional `config.json` or `config.yaml` with a `themes` key mapping theme names to keyword lists

### Output
- **`tagged.md`** — Same structure as input, with inline `<!-- themes: X, Y -->` comments after each event heading
- **`tagged.tagged.json`** — (optional, with `--sidecar`) Structured JSON with per-event tag data

### Theme Categories (built-in defaults)

| Theme | Keywords |
|-------|----------|
| Web UI | `chat.openai.com`, `chatgpt.com`, `web interface`, `browser`, `UI freeze`, `button disappeared`, `interface`, `web app` |
| API / Developer | `api.openai.com`, `ChatGPT API`, `playground`, `code interpreter`, `function calling`, `API`, `developer`, `endpoint`, `rate limit`, `token`, `GPT-4 API` |
| Outages | `down`, `outage`, `downtime`, `unreachable`, `503 error`, `service disruption`, `error`, `unavailable`, `crash` |
| Jailbreaks / Exploits | `jailbreak`, `DAN`, `prompt injection`, `bypass`, `ignore previous instructions`, `exploit`, `prompt leak` |
| Memory / Personalisation | `memory`, `custom instructions`, `bio`, `personalised`, `remembers`, `personalisation` |
| Culture / Virality | `viral`, `Twitter`, `Reddit`, `meme`, `social media`, `went viral`, `community` |

### CLI Flags (5 flags)

| Flag | Description |
|------|-------------|
| `--input` / `-i` | Path to input `.md` file (required) |
| `--config` / `-c` | JSON or YAML config file with theme keywords (optional; uses built-in defaults if omitted) |
| `--output` / `-o` | Path for tagged output (default: `<input>_tagged.md`) |
| `--sidecar` | Also write a sidecar JSON file with structured tag data |
| `--verbose` / `-v` | Enable debug logging |

### Design Decisions

1. **Substring matching, not word-boundary regex** — Keywords like `chat.openai.com`, `503 error`, and `DALL·E` contain dots, numbers, and special chars that break `\b` word boundaries. Simple `in` operator with case-insensitive comparison is more robust.
2. **Built-in defaults** — `--config` is optional. If omitted, 6 themes with 48 keywords are used. This makes the tool immediately useful without setup.
3. **JSON + YAML config** — Supports both formats transparently. Tries JSON first, falls back to YAML.
4. **Non-destructive** — Only adds `<!-- themes: ... -->` comments; never alters original content.
5. **Same event extraction as merge.py** — Uses the same `## Event:` regex pattern for consistency.

### Error Handling

| Condition | Behaviour |
|-----------|-----------|
| Input file not found | Exit with error |
| Config file not found | Exit with error |
| Config file is neither JSON nor YAML | Exit with error |
| Config has no `themes` key | Warning, use built-in defaults |
| Theme value is not a list | Exit with error |
| No events found in input | Copy input to output unchanged, warn |
| Empty event body | Still process (no keywords to match) |

### Test Results (3 normalised files → merged → tagged)

| Config | Events | Tagged | Notes |
|--------|--------|--------|-------|
| Built-in defaults (6 themes, 48 keywords) | 28 | 27 | 1 event had no matching keywords |
| Custom JSON (2 themes, 6 keywords) | 28 | 11 | Only Web UI and Outages matched |
| Custom YAML (2 themes, 5 keywords) | 28 | 20 | Culture/Virality matched many events |

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – PIPELINE PLAN - ⬜ Stage 4: Indexing (Planned
<!-- themes: Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup -->

### Tool: `index.py`

**Role:** Generate appendix files from categorised chronicle.

### Output Files
- `event_index.md` — Alphabetical list of all events with links
- `theme_index.md` — Events grouped by theme
- `source_manifest.md` — Source file metadata table
- `link_registry.md` — All `file://` and `https://` citations indexed

### Templates
- Uses Jinja2 templates from `templates/` directory
- Default templates bundled with the tool

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – PIPELINE PLAN - ⬜ Stage 5: Reference (Planned
<!-- themes: Categorize/Themes, Merge/Dedup -->

### Tool: `reference.py`

**Role:** Build cross-reference system for AI iteration.

### Features
- Stable anchor IDs for each event (survive re-merges)
- Header map (H2/H3 structure)
- Topic model (keyword frequency analysis)
- Cross-reference links between related events

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – PIPELINE PLAN - ⬜ Stage 6: Automation (Planned
<!-- themes: Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI -->

### Tool: `chain.sh`

**Role:** One-command wrapper for the full pipeline.

```bash
./chain.sh --input-dir raw/ --output-dir output/
```

Equivalent to:
```bash
for f in raw/*.md; do
    python ingest.py --input "$f" --output "output/normalised/$(basename $f)"
done
python merge.py --input-dir output/normalised/ --output output/merged.md
python categorize.py --input output/merged.md --output output/categorized.md
python index.py --input output/categorized.md --output-dir output/
```

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – PIPELINE PLAN - 🔗 Cross-References
<!-- themes: Ingest/Normalise, Merge/Dedup, Planning/Roadmap -->

| Resource | Link |
|----------|------|
| Project Roadmap | [`ROADMAP.md`](../../ROADMAP.md) |
| Project Plan | [`PLAN.md`](../../PLAN.md) |
| Review & Remediation | [`REVIEW_PLAN.md`](REVIEW_PLAN.md) |
| Full Spec | [`README.md`](README.md) |
| Ontology | [`ontology.json`](../../ontology.json) |
| Raw Sources | `WordHorrorStories/chatgpt-chronicle/sources/raw/chatgpt_mds/` |
| Normalised Output | `WordHorrorStories/chatgpt-chronicle/sources/normalised/` |

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – PIPELINE PLAN - 📝 Change Log
<!-- themes: Categorize/Themes, Ingest/Normalise, Merge/Dedup, Planning/Roadmap -->

| Date (Jalali) | Change |
|---------------|--------|
| 1404-11-25 | Initial plan created — Stage 1 complete, Stage 2 in progress |
| 1404-11-25 | Stage 2 complete (merge.py). Stage 3 complete (categorize.py). Critique-driven fixes applied to merge.py (duplicate import, source_names return, event count from front-matter). categorize.py built with: built-in default themes, JSON+YAML config, substring matching, sidecar JSON. |

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – REVIEW PLAN - 1. Review Summary
<!-- themes: Archive/Refactor, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap, Testing/Verification -->

The critic reviewed an **earlier version** of `ingest.py` that used a fragile `date_line_pattern` regex for event splitting. The current code has already replaced that with a `bullet_bold_pattern` approach that matches the actual raw file structure. However, several valid issues remain.

### ✅ Already Fixed (Critic's complaints no longer apply)

| Issue | Original Problem | Current Status |
|-------|-----------------|----------------|
| `date_line_pattern` regex too brittle | Required date at line start with `$` anchor | **Replaced** with `bullet_bold_pattern` matching `- **Title:**` structure |
| Date parsing inaccuracies with `fuzzy=True` | Could match non-dates | **Mitigated** by regex pre-filter + year range check (2022–2027) |
| Mojibake double-fix risk | Redundant Unicode→Unicode entries | **Removed** — no `\u2013` etc. in current mapping |

### ✅ All Resolved (1404-11-25)

| # | Issue | Severity | Resolution |
|---|-------|----------|------------|
| 1 | **Preamble silently discarded** | 🔴 Critical | **FIXED** — `extract_preamble()` captures content before first `- **` bullet; rendered as `> **Overview:**` blockquote |
| 2 | **Title extraction too narrow** | 🟡 Medium | **FIXED** — fallback chain: H1 → first H2 → `{source} Incidents` |
| 3 | **Excess CLI flags** | 🟡 Low | **FIXED** — reduced from 11 to 5 essential flags |
| 4 | **Redundant Unicode entries in mojibake map** | 🟢 Trivial | **FIXED** — removed 8 redundant Unicode→Unicode entries |
| 5 | **No preamble preservation** | 🟡 Medium | **FIXED** — preamble rendered as `> **Overview:**` blockquote after `# Source:` header |

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – REVIEW PLAN - 2. Prioritised Remediation Plan
<!-- themes: Categorize/Themes, Index/Appendix, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap, Testing/Verification -->

### ✅ P0 — Critical (Completed 1404-11-25)

| ID | Task | Description | Effort | Status |
|----|------|-------------|--------|--------|
| **FIX-1** | **Preserve preamble** | Save all content before the first detected event. Insert as `> **Overview:**` blockquote after `# Source:` header. | 1h | ✅ Done |
| **FIX-2** | **Verify all 16 files produce correct output** | Created `verify_ingest.py` — runs `ingest.py` on every raw file, reports event counts and warnings. All 16 files pass. | 2h | ✅ Done |

### ✅ P1 — High (Completed 1404-11-25)

| ID | Task | Description | Effort | Status |
|----|------|-------------|--------|--------|
| **FIX-3** | **Strip excess CLI flags** | Reduced from 11 to 5: `--input`, `--output`, `--source-name`, `--date-override`, `--verbose`. Removed `--config`, `--source-url`, `--date-format`, `--no-mojibake`, `--dry-run`, `--metadata-only`. | 1h | ✅ Done |
| **FIX-4** | **Improve title extraction** | Fallback chain: H1 → first `##` heading → `{source} Incidents`. | 0.5h | ✅ Done |
| **FIX-5** | **Clean mojibake map** | Removed 8 redundant Unicode→Unicode entries (`\u2013`, `\u2014`, `\u2018`, `\u2019`, `\u201c`, `\u201d`, `\u2026`, `\u2022`). Map now contains only broken byte sequences. | 0.25h | ✅ Done |

### 🟡 P2 — Medium (Before `categorize.py`)

| ID | Task | Description | Effort | Target |
|----|------|-------------|--------|--------|
| **FIX-6** | **Add unit tests** | Create `tests/test_ingest.py` with 3–5 curated input/output pairs covering: normal timeline, narrative-only, date ranges, no dates, preamble content. | 3h | 1404-12-01 |
| **FIX-7** | **Add date confidence ranking** | Tag dates in YAML as `date_confidence: high|medium|low` based on format specificity (ISO=high, "June 2025"=medium, fuzzy=low). | 1h | 1404-12-01 |

### 🔵 P3 — Low (After Pipeline Works End-to-End)

| ID | Task | Description | Effort | Target |
|----|------|-------------|--------|--------|
| **FIX-8** | **Integration test** | Run full pipeline (ingest→merge→categorize→index) and compare output against `ChatGPT_Incidents_Merged.md`. | 4h | 1404-12-10 |
| **FIX-9** | **Better preamble handling** | Instead of `> [!note]`, add a `description` field to YAML front-matter for preamble text. | 0.5h | 1404-12-10 |

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – REVIEW PLAN - 3. Detailed Issue Analysis
<!-- themes: Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap, Testing/Verification -->

### FIX-1: Preamble Discarded (🔴 Critical)

**Current code** (`split_into_events`):
```python
for line in lines:
    stripped = line.strip()
    # ... check for period header or bullet event ...
    # If we're inside an event, accumulate body lines
    if current_date is not None:
        current_body.append(line)
```

Lines before the first `- **Title:**` bullet are silently skipped because `current_date` is `None`.

**Fix approach:**
```python
preamble_lines = []
in_preamble = True

for line in lines:
    stripped = line.strip()
    if is_event_start(stripped) and in_preamble:
        in_preamble = False
        # save preamble, then process event
    if in_preamble:
        preamble_lines.append(line)
    else:
        # existing event processing
```

The preamble is then inserted as a `> [!note] Preamble` block at the top of the output, or stored in YAML front-matter as `description`.

### FIX-3: Excess CLI Flags (🟡 Low)

**Current:** 11 flags  
**Target:** 5 essential flags

| Flag | Verdict | Reason |
|------|---------|--------|
| `--input` | ✅ **Keep** | Required |
| `--output` | ✅ **Keep** | Required |
| `--source-name` | ✅ **Keep** | Essential for attribution |
| `--date-override` | ✅ **Keep** | Critical for files without dates |
| `--verbose` | ✅ **Keep** | Debugging |
| `--config` | ❌ **Remove** | Auto-detect `config.json` in same directory |
| `--source-url` | ❌ **Remove** | Can be added later via enrichment |
| `--date-format` | ❌ **Remove** | Always output `%Y-%m-%d` |
| `--no-mojibake` | ❌ **Remove** | Premature optimisation |
| `--dry-run` | ❌ **Remove** | Use `--metadata-only` or pipe to stdout |
| `--metadata-only` | 🔶 **Hide** | Rename to `--debug-metadata` (hidden) |

### FIX-5: Mojibake Map Cleanup (🟢 Trivial)

**Current map includes redundant entries:**
```python
"\u2013": "–",     # en dash — already correct
"\u2014": "—",     # em dash — already correct
"\u2018": "‘",     # left quote — already correct
# ... etc
```

These are harmless (replace character with itself) but confusing. Remove them. The map should only contain broken byte sequences → correct characters.

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – REVIEW PLAN - 4. Acceptance Criteria — P0/P1 Verification
<!-- themes: Categorize/Themes, Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap, Testing/Verification -->

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| **AC1** | All 16 raw files produce correct event counts (no regressions) | ✅ **PASS** | `verify_ingest.py` reports 224 total events across 16 files; counts match previous baseline |
| **AC2** | Preamble content is preserved in output (visible as `> **Overview:**` blockquote) | ✅ **PASS** | Narrative files (e.g., `ChatGPT_Agent_Mode_...`) show preamble; timeline files with no preamble show none |
| **AC3** | Title extraction works for files with H1, H2-only, and no headings | ✅ **PASS** | H1 files use H1; H2-only files fall back to H2; no-heading files use `{source} Incidents` |
| **AC4** | Only 5 CLI flags exposed (`--input`, `--output`, `--source-name`, `--date-override`, `--verbose`) | ✅ **PASS** | `--help` confirms exactly 5 flags; removed flags rejected with error |
| **AC5** | `--metadata-only` removed (was hidden debug flag) | ✅ **PASS** | Flag removed entirely; no hidden flags remain |
| **AC6** | Mojibake map contains only broken→fixed mappings (no redundant Unicode entries) | ✅ **PASS** | All 8 `\uXXXX`→same-char entries removed; only byte-sequence artifacts remain |
| **AC7** | Unit tests pass for 3+ curated input/output pairs | ⬜ **PENDING** | FIX-6 deferred to P2 (before `categorize.py`) |

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – REVIEW PLAN - 5. Implementation Details
<!-- themes: Ingest/Normalise, Merge/Dedup, Orchestration/CLI, Planning/Roadmap, Testing/Verification -->

### FIX-1: Preamble Preservation

**File:** `ingest.py` — new function `extract_preamble()`

```python
def extract_preamble(text: str, events: List[Dict[str, str]]) -> str:
```

**Logic:**
1. If no events found → return entire text with markdown headings stripped
2. Find first `- **` bullet line via regex
3. Extract all text before that line
4. Strip structural headings (`#`, `##`, etc.) since they're already in YAML front-matter
5. Return cleaned text as preamble

**Output rendering** (in `generate_normalised_md`):
```python
if preamble:
    output += f"> **Overview:** {preamble}\n\n"
```

### FIX-2: Verification Script

**New file:** `verify_ingest.py`

- Runs `ingest.py` against every `.md` file in the raw directory
- Parses stderr for event counts and warnings
- Reports per-file status: `[OK]`, `[ZERO]`, or `[ERROR]`
- Exits with code 0 on success, non-zero on errors
- Uses temp directory for output files (auto-cleaned)

### FIX-3: CLI Flag Reduction

**Before (11 flags):** `--input`, `--output`, `--config`, `--source-name`, `--source-url`, `--date-format`, `--date-override`, `--no-mojibake`, `--dry-run`, `--metadata-only`, `--verbose`

**After (5 flags):** `--input`, `--output`, `--source-name`, `--date-override`, `--verbose`

**Removed functionality:**
- `--config` → removed entirely; mojibake cleanup uses built-in map only
- `--source-url` → removed; can be added later via enrichment tool
- `--date-format` → removed; always outputs `%Y-%m-%d`
- `--no-mojibake` → removed; cleanup is always on
- `--dry-run` → removed; use `--output` to control destination
- `--metadata-only` → removed; no hidden debug flag retained

### FIX-4: Title Extraction

**Before:** H1 → `{source} Incidents`
**After:** H1 → first H2 → `{source} Incidents`

```python
def extract_title(raw_text: str, source: str) -> str:
    # 1. Look for H1 heading
    match = re.search(r"^#\s+(.+)$", raw_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # 2. Look for first H2 heading
    match = re.search(r"^##\s+(.+)$", raw_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # 3. Fall back to source name
    return f"{source} Incidents"
```

### FIX-5: Mojibake Map Cleanup

**Removed 8 redundant entries** (Unicode codepoint → same character):
- `"\u2013": "–"` (en dash)
- `"\u2014": "—"` (em dash)
- `"\u2018": "‘"`, `"\u2019": "’"` (quotes)
- `"\u201c": "“"`, `"\u201d": "”"` (double quotes)
- `"\u2026": "…"` (ellipsis)
- `"\u2022": "•"` (bullet)

**Kept 13 broken byte-sequence entries** (e.g., `"â€"` → `"–"`, `"é"` → `"é"`).

---

<!-- Duplicate date, different content -->

## Event: 2026-07-16 – REVIEW PLAN - 6. Change Log
<!-- themes: Orchestration/CLI, Planning/Roadmap -->

| Date (Jalali) | Change |
|---------------|--------|
| 1404-11-25 | Initial review plan created based on automated code critic analysis |
| 1404-11-25 | **All P0/P1 fixes applied:** preamble preservation (FIX-1), verification script (FIX-2), CLI flag reduction (FIX-3), title extraction improvement (FIX-4), mojibake map cleanup (FIX-5). All 16 files verified passing. |
