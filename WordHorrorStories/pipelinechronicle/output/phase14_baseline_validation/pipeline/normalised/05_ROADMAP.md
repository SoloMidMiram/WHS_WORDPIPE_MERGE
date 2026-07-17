---
source: 05 Roadmap
title: ROADMAP
input_file: 05_ROADMAP.md
event_count: 11
date: 2025-06-01 to 2026-07-01
---

# Source: 05 Roadmap

## Event: 2025-06-01 – ROADMAP - 🎯 Goal

Build a set of **Unix‑style composable CLI tools** (each independent, file‑based, no cross-imports)
that automate the workflow described in `WordHorrorStories/chatgpt-chronicle/`.

See [`PIPELINE_PLAN.md`](PIPELINE_PLAN.md) for the full revised implementation plan with stages, priorities, and error-handling specifications.

---
## Event: 2025-06-01 – ROADMAP - 📋 Tool Status

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
## Event: 2025-06-01 – ROADMAP - ✅ Completed: `ingest.py` (Milestone A1) — Final Implementation

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
## Event: 2025-06-01 – ROADMAP - ✅ Completed: `merge.py` (Milestone A2–A3

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
## Event: 2025-06-01 – ROADMAP - ✅ Completed: `categorize.py` (Milestone B1–B3

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
## Event: 2025-06-01 – ROADMAP - ⬜ Future: `categorize.py` (Milestone B1–B3

### Requirements

- Read merged MD, map keywords to ontology classes
- Assign theme tags (Web UI, API/Developer, Outages, Jailbreaks/Exploits, Memory/Personalisation, Culture/Virality)
- Add as inline annotations or sidecar JSON

---
## Event: 2025-06-01 – ROADMAP - ⬜ Future: `index.py` (Milestone B2–B4

### Requirements

- Regenerate appendix files: `event_index.md`, `theme_index.md`, `source_manifest.md`, `link_registry.md`
- Use Jinja2 templates from `templates/` directory

---
## Event: 2025-06-01 – ROADMAP - ⬜ Future: `reference.py` (Milestone C–E

### Requirements

- Build header map, topic model, cross-reference anchors
- Stable anchor IDs that survive re-merges

---
## Event: 2025-06-01 – ROADMAP - ⬜ Future: `chain.sh` (Milestone All

### Requirements

- One-command wrapper: `ingest → merge → categorize → index`

---
## Event: 2025-06-01 – ROADMAP - 🔗 Cross-References

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
## Event: 2026-02-14 – ROADMAP - 📝 Change Log

| Date (Gregorian) | Date (Jalali) | Change |
|------------------|---------------|--------|
| 2026-02-14 | 1404-11-25 | Created — `ingest.py` completed and documented |
| 2026-02-14 | 1404-11-25 | **All P0/P1 fixes applied:** preamble preservation, verification script, CLI reduction (11→5), title fallback, mojibake cleanup. `REVIEW_PLAN.md` updated to reflect completion. |
| 2026-02-14 | 1404-11-25 | **`merge.py` implemented** with 3 conflict modes, source coverage, duplicates report. `PIPELINE_PLAN.md` created with revised stage-based plan. `ROADMAP.md` updated to reflect 2/6 tools complete. |
| 2026-02-14 | 1404-11-25 | **`categorize.py` implemented** with built-in default themes, JSON+YAML config, substring matching, sidecar JSON. Critique-driven fixes applied to `merge.py` (duplicate import, source_names return, event count from front-matter). `PIPELINE_PLAN.md` and `ROADMAP.md` updated to reflect 3/7 tools complete. |
