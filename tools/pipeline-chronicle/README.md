# 📡 Chronicle Pipeline Tools

> **Phase:** P9 — Chronicle Automation  
> **Target:** 1404-12-05 onward  
> **Date:** 2026-02-14 (Jalali: 1404-11-25)  
> **Ontology Ref:** `ActivityPeriod(name="P9: Chronicle Automation")` — see `ONTOLOGY.md`

---

## 🧱 What This Is

A set of **Unix‑style composable CLI tools** (each independent, file‑based, no cross‑imports)
that automate the workflow described in `WordHorrorStories/chatgpt-chronicle/`:

> Two (or more) heavily‑marked‑up deep‑search files → normalised Markdown → merged, deduped, categorised → auto‑generated appendices (event index, theme index, source manifest, link registry) → cross‑reference system for future AI iteration.

Each tool reads from disk, writes to disk, accepts flags — never imports another tool's Python code.

---

## 📁 Directory Structure

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

## 🔧 Design Principles

| Principle | How It's Achieved |
|-----------|-------------------|
| **Independent** | Every tool reads from disk; no Python cross-imports. |
| **Parameterised** | All behaviour via CLI flags (`--input`, `--output`, `--config`, `--no-dedup`, ...). |
| **Boolean toggles** | Flags like `--no-dedup`, `--no-themes`, `--verbose`. |
| **Config‑driven** | `config.json` contains ontology classes, theme keywords, header taxonomy. |
| **Idempotent** | Same command + same inputs → same output. `merge.py` can be re‑run with new sources. |
| **Composable** | Output of one tool is input to the next. Run individually or via `chain.sh`. |

---

## 🔗 Relationship to Existing Project Files

| Existing File | How Pipeline Uses It |
|---------------|---------------------|
| `ontology.json` | Config file loads ontology classes & relations for categorisation |
| `WordHorrorStories/chatgpt-chronicle/appendix/event_index.md` | **Target** of `index.py` — regenerates from tagged merged MD |
| `WordHorrorStories/chatgpt-chronicle/appendix/theme_index.md` | **Target** of `index.py` — auto‑populated from tagged entries |
| `WordHorrorStories/chatgpt-chronicle/appendix/source_manifest.md` | **Target** of `index.py` — lists sources with merge/drop decisions |
| `WordHorrorStories/chatgpt-chronicle/appendix/link_registry.md` | **Target** of `index.py` — extracts external links |
| `WordHorrorStories/chatgpt-chronicle/appendix/source_coverage.md` | Updated by `merge.py` — merged/dropped/notes per source |
| `WordHorrorStories/chatgpt-chronicle/book/02_master_current.md` | **Consumed by** `categorize.py` and `reference.py` for Topic Model |
| `inputs/chatgpt-chronicle/markdown/*.md` | **Input** to `ingest.py` — raw deep-search MD files |
| `WordHorrorStories/chatgpt-chronicle/sources/dropped/` | Populated by `merge.py` when sources are flagged as duplicates |
| `inputs/chatgpt-chronicle/markdown/ChatGPT_Incidents_Merged.md` | Example of a **manual merge** that `merge.py` will automate |

---

## 🚦 Build Order (Prioritised)

### 1. `ingest.py` — Highest Priority
**Milestone:** A1  
**Target:** 1404-12-05

Converts a single raw deep‑search file (any `.md` with file:// or https:// citation links) into a standard normalised Markdown file with:

- Extracted title, source date, source attribution
- Consistent headers (`# Source: xxx`, `## Event: yyy`, `### Evidence: zzz`)
- YAML front‑matter block: `date`, `source_name`, `source_url`, `ontology_classes`, `themes`
- Stripped mojibake (the â€“, â€™ patterns seen in existing files)

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
  --input "inputs/chatgpt-chronicle/markdown/2025-08-06-ChatGPT_Agent_Mode_-_Bugs,_Exploits,_and_Cultural_Phenomena_(June-July_2025).md" `
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
./chain.sh --input-dir "inputs/chatgpt-chronicle/markdown/"
           --output-dir "WordHorrorStories/chatgpt-chronicle/sources/normalised/"
           --merged "WordHorrorStories/chatgpt-chronicle/sources/merged/merged_chronicle.md"
           --appendix "WordHorrorStories/chatgpt-chronicle/appendix/"
```

---

## ⚙️ Shared Configuration: `config.json`

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

## 📋 Example End-to-End Workflow

```powershell
# 1. Ingest two raw deep-search files
python tools/pipeline-chronicle/ingest.py `
  --input "inputs/chatgpt-chronicle/markdown/2025-08-06-ChatGPT_Agent_Mode_-_Bugs,_Exploits,_and_Cultural_Phenomena_(June-July_2025).md" `
  --output "WordHorrorStories/chatgpt-chronicle/sources/normalised/agent_mode.md" `
  --source-name "Agent Mode Deep Report"

python tools/pipeline-chronicle/ingest.py `
  --input "inputs/chatgpt-chronicle/markdown/2025-08-06-ChatGPT's_Bugs_&_Lore_-_May_to_July_2025_Timeline.md" `
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

## 🔗 Ontology Cross-Reference

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

## 📝 Change Log

| Date (Gregorian) | Date (Jalali) | Change |
|------------------|---------------|--------|
| 2026-02-14 | 1404-11-25 | Initial plan created — 6 tools defined, mapped to existing project structure |

---

## See Also

- `ontology.json` — Machine-readable ontology loaded by `config.json`
- `ONTOLOGY.md` — Human-readable ontology index
- `ONTOLOGY_MODEL.md` — Detailed ontology with full instance tables
- `PLAN.md` — Project plan with phase targets (P9 planned)
- `WordHorrorStories/chatgpt-chronicle/book/02_master_current.md` — Target book structure
- `docs/README.md` — All project documentation
