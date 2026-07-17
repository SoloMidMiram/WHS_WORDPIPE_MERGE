---
source: 02 Pipeline Plan
title: PIPELINE PLAN
input_file: 02_PIPELINE_PLAN.md
event_count: 12
date: 2026-07-01 to 2026-07-16
---

# Source: 02 Pipeline Plan

## Event: 2026-07-16 – PIPELINE PLAN - 🎯 Design Principles

1. **Modularity** — Each tool is independent, file-based, no cross-imports. They communicate only through files on disk.
2. **Error resilience** — Every tool validates inputs at the start, fails fast with clear messages, and never silently corrupts data.
3. **Minimal flags** — Each tool exposes only the flags needed for its single responsibility. Configuration belongs in files, not CLI args.
4. **Deterministic output** — Same inputs → same outputs. No randomness, no environment-dependent behavior.
5. **Backward compatibility** — Output format of each tool is the input contract for the next. Changes must be coordinated.

---
## Event: 2026-07-16 – PIPELINE PLAN - 📋 Stage Overview

| Stage | Tools | Milestone | Status | Target |
|-------|-------|-----------|--------|--------|
| **1 — Ingestion** | `ingest.py`, `verify_ingest.py` | A1 | ✅ **DONE** | 1404-12-05 |
| **2 — Merge** | `merge.py` | A2–A3 | ✅ **DONE** | 1404-12-05 |
| **3 — Categorisation** | `categorize.py`, `config.json` | B1–B3 | ✅ **DONE** | 1404-12-10 |
| **4 — Indexing** | `index.py`, `templates/` | B2–B4 | ⬜ Pending | 1404-12-15 |
| **5 — Reference** | `reference.py` | C–E | ⬜ Pending | 1404-12-20 |
| **6 — Automation** | `chain.sh` | All | ⬜ Pending | 1404-12-20 |

---
## Event: 2026-07-16 – PIPELINE PLAN - ✅ Stage 1: Ingestion (Complete

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
## Event: 2026-07-16 – PIPELINE PLAN - Event: YYYY-MM-DD – Title

<body text>
## Event: 2026-07-16 – PIPELINE PLAN - Event: YYYY-MM-DD – Another Title

<body text>
...
```

### Verification Results
- **16 files processed**, **224 total events**
- **4 narrative files** correctly yield 0 events (no bullet-list structure)
- **12 timeline files** yield correct event counts (range: 4–92)
- **0 errors**, **0 regressions**

---
## Event: 2026-07-16 – PIPELINE PLAN - ✅ Stage 2: Merge (Complete

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
## Event: 2026-07-16 – PIPELINE PLAN - ✅ Stage 3: Categorisation (Complete

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
## Event: 2026-07-16 – PIPELINE PLAN - ⬜ Stage 4: Indexing (Planned

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
## Event: 2026-07-16 – PIPELINE PLAN - ⬜ Stage 5: Reference (Planned

### Tool: `reference.py`

**Role:** Build cross-reference system for AI iteration.

### Features
- Stable anchor IDs for each event (survive re-merges)
- Header map (H2/H3 structure)
- Topic model (keyword frequency analysis)
- Cross-reference links between related events

---
## Event: 2026-07-16 – PIPELINE PLAN - ⬜ Stage 6: Automation (Planned

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
## Event: 2026-07-16 – PIPELINE PLAN - 🔗 Cross-References

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
## Event: 2026-07-16 – PIPELINE PLAN - 📝 Change Log

| Date (Jalali) | Change |
|---------------|--------|
| 1404-11-25 | Initial plan created — Stage 1 complete, Stage 2 in progress |
| 1404-11-25 | Stage 2 complete (merge.py). Stage 3 complete (categorize.py). Critique-driven fixes applied to merge.py (duplicate import, source_names return, event count from front-matter). categorize.py built with: built-in default themes, JSON+YAML config, substring matching, sidecar JSON. |
