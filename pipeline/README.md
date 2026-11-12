# Chronicle Pipeline — `pipeline/`

> **Purpose:** Automated chronicle processing: raw or staged topic files → normalised → merged → categorised → indexed.
> **Date:** 2026-02-14 (Jalali: 1404-11-25)
> **Status:** Working code — see `CODEX_WORKING.md` for full reference and known issues.

---

## Quick Start

```powershell
# Full pipeline (6 raw files → appendix files)
.\chain.ps1 -InputDir "path/to/raw/files" -OutputDir "output/" -ThemesConfig themes.json

# Stop after merge (debugging)
.\chain.ps1 -InputDir "path/to/raw/files" -OutputDir "output/" -SkipCategorize

# With verification and index config
.\chain.ps1 -InputDir "path/to/raw/files" -OutputDir "output/" -Verify -ThemesConfig themes.json -IndexConfig index_config.json

# Categorize only (skip index generation)
.\chain.ps1 -InputDir "path/to/raw/files" -OutputDir "output/" -SkipIndex
```

For source material that is not already shaped like dated Chronicle events,
prefer the generic topic runner. It stages the topic through a registered
adapter, runs `chain.ps1`, captures logs/performance, writes run metrics, emits
trend reports, and records ontology evidence:

```powershell
python tools\run_topic_report.py `
  --manifest WordHorrorStories\insurancechatbot\topic_manifest.json `
  --run-id phase13_trend_validation
```

## Output Files

### Chronicle run evidence

`run.json` is the latest invocation summary for a usable output directory.
Schema version 1 records a run ID, UTC start and finish times, the operator
exit code, and a status of `ok`, `partial`, or `failed`. Partial means the
chain exited successfully after skipping failed inputs under
`-AllowPartialIngest`. Any nonzero operator exit makes the run failed.

The ordered `stages` array includes ingest, verify, merge, categorize, and
index. Stage states are `ok`, `partial`, `failed`, `skipped` for an explicit
flag or omitted verification, and `not_run` for a stage an abort prevented.
Stage entries record elapsed milliseconds, native exit code when applicable,
bounded diagnostic codes, and output paths relative to the output directory.
`merge_inputs` records exactly the ordered paths supplied to merge and is
empty if merge was never invoked.

`ingest_files` records accepted and rejected counts from the normalized
front matter or a current rejection manifest. A count of `null` means the
artifact was missing, malformed, too large to inspect, or could not be
distinguished from stale evidence. Only diagnostic codes are recorded.
Document bodies and captured process output stay out of the summary.

The chain invalidates the previous summary before running any stage and
publishes the new summary by moving a completed temporary file within the same
directory. Runs sharing an output directory are serialized by an exclusive
file handle. A hard interruption or an unusable output directory can leave
the current summary absent.

| Stage | Output File | Description |
|-------|-------------|-------------|
| 1 (ingest) | `output/normalised/*.md` | Normalised per-source files |
| 3 (merge) | `output/merged.md` | Deduplicated merged chronicle |
| 4 (categorize) | `output/chronicle_tagged.md` | Tagged chronicle with theme comments |
| 4 (categorize) | `output/chronicle_tagged.tagged.json` | Structured tag data (sidecar) |
| 5 (index) | `output/appendix/event_index.md` | Events sorted by date |
| 5 (index) | `output/appendix/theme_index.md` | Events grouped by theme |
| 5 (index) | `output/appendix/source_manifest.md` | Source contribution summary |
| 5 (index) | `output/appendix/link_registry.md` | All URLs by domain |

## File Inventory

| File | Role | Dependencies |
|------|------|--------------|
| `ingest.py` | Stage 1 — Normalise raw .md files | stdlib |
| `verify_ingest.py` | Stage 2 — Batch verification | stdlib |
| `merge.py` | Stage 3 — Merge + dedup | stdlib |
| `categorize.py` | Stage 4 — Tag events with themes | stdlib + optional PyYAML |
| `index.py` | Stage 5 — Generate appendix files | stdlib + optional Jinja2 |
| `chain.ps1` | Orchestrator — runs all 5 stages | PowerShell + Python |
| `themes.json` | External theme config (6 themes, 62 pos + 16 neg keywords) | JSON |
| `index_config.json` | Index generation config | JSON |
| `templates/` | 4 Jinja2 templates for appendix rendering | Optional Jinja2 |
| `CODEX_WORKING.md` | Working code reference, evolution, known issues | Read this first |

## Index identity and navigation

The default `survivor` projection lists every tagged survivor. Anchors use
`event-<date>-<normalized-body-sha256>`, the topic-neutral key used by Phase 17
survivor verification. New tagged files carry explicit anchors. Standalone
indexing writes a navigation copy for older unanchored tagged files or when
the tagged file is on a different Windows volume. The copy is named
`chronicle_tagged_anchored.md` by default and uses a numbered suffix if that
name would overwrite an input. Event and theme indices use relative,
URL-encoded links in both Jinja2 and fallback rendering.
Install the `chronicle` extra to validate the rendered links and targets
under CommonMark with Markdown tables enabled.

The chain passes `--merged` to verify the ordered tagged keys against its
merged output before indexing. The index checks navigation and required files
before returning success. Custom event and theme templates should use
`{{ event_link(event) }}` for each expected event row. The chain rejects
missing or stale required index artifacts even when the index process exits 0.

Explicit `title` and `date_title` projections retain the compatibility
grouping and report the number of omitted survivor entries. A grouped row
links to its first survivor. Set `dedup_method` to `survivor` in older
configs to list all survivors.

The index CLI uses built-in defaults and logs a warning if a supplied config
cannot be read, decoded, or validated. Pass `--strict-config` to
`python -m pipeline.index` to reject an invalid config or unknown setting with
exit code 2 before writing any appendix files. Omitting `--config` uses defaults
in either mode.

Theme configuration must have a mapping at its root and, when present, a
mapping under `themes`. Blank positive and negative keywords are ignored.
Merge ignores non-mapping YAML front matter with a warning and retains the
event body.

## Status

All 5 stages are complete. `ingest.py`, `merge.py`, and `verify_ingest.py` were copied from `tools/pipeline-chronicle/` (byte-identical, SHA256 verified). `categorize.py` and `chain.ps1` are v2 refactored versions with additional features (negative keywords, `--dry-run`, Stage 5 index). `index.py`, `themes.json`, `index_config.json`, and `templates/` are new.

The pipeline is now **runnable end-to-end** from `pipeline/`.

Latest generic topic-runner evidence:
`WordHorrorStories/insurancechatbot/output/phase13_trend_validation/RUN_SUMMARY.md`
records 3 input files, 200 staged events, 200 merged events, 194 events with
theme tags, 0 warnings/errors, and 6.51 seconds wall-clock time. The same run
also writes `trend_report.json`, `trend_report.md`, `source_attribution.json`,
`topic_run_manifest.json`, and `topic_run_ontology.json`.

## Tests

Tests are in `tests/test_pipeline_chronicle.py` (59 tests). They import from the **archived** versions in `tools/pipeline-chronicle/` (v1 of the tools). The current `pipeline/` code is v2 with different internal APIs.

## See Also

- `ARCHITECTURE_AND_MODULES.md` — Full system architecture (§2 for chronicle pipeline)
- `CODEX_WORKING.md` — Detailed working code reference, evolution timeline, issues
- `_ARCHIVE/pipeline-chronicle/ARCHIVE_REPORT.md` — Archived tool documentation
