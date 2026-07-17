# Phase 14 Roadmap — Second Topic Adapter & Multi-Topic Ontology Readiness

> Date: 2026-07-16 / 1405-04-25<br>
> Status: Completed<br>
> Builds on: Phase 13 generic topic report runner with manifest, trend, and ontology spine

## Summary

Phase 14 adds a second topic through the same Phase 13 generic runner contract,
proving the runner is truly reusable and providing multi-topic evidence before
any strategic ontology expansion.

A generic Markdown-section adapter was created alongside the InsuranceChatbot-
specific adapter, showing that the registry-backed runner handles both.

## Topic Selection

**Topic:** `pipelinechronicle`<br>
**Source:** `_ARCHIVE/pipeline-chronicle/` (read-only, 5 long `.md` files)

Chosen because:
- Fits the preferred 2–5 file input shape
- Archived (never edited, no drift risk between runs)
- Coherent narrative: how the Chronicle pipeline tools were built, then archived
- Contains parseable Gregorian dates in headings and body text
- The alternative (`inputs/chatgpt-chronicle/markdown/`, 16 files with near-duplicates and one 352KB outlier) is out of the preferred shape

## Implementation

| Slice | Status |
|-------|--------|
| Generic Markdown-section adapter (`tools/prepare_generic_markdown_chronicle.py`) | Done |
| Adapter registered in `ADAPTER_REGISTRY` | Done |
| Topic folder with manifest, themes config, README | Done |
| Phase 14 adapter tests | Done |
| Phase 14 runner registry test | Done |
| Baseline run | Done |
| Trend run | Done |
| InsuranceChatbot regression | Done |
| Documentation | Done |
| Genericity review remediation and context mapping | Done |

## Run Evidence

### Baseline (`phase14_baseline_validation`)
- Input files: 5
- Candidate sections: 50
- Staged events: 50 (100.0% extraction)
- Merged events: 50
- Events with theme tags: 50 (100%)
- Errors: 0, Warnings: 0, Duplicates: 0
- Wall time: 10.71s (first run with cache-warming)
- Verdict: PASS

### Trend (`phase14_trend_validation`)
- Identical metrics: staged=50, merged=50, tagged=50
- Timing: 4.04s (stable, faster on re-run)
- Trend status: COMPARED against baseline
- Verdict: PASS

### Regression
InsuranceChatbot dry-run confirmed correct — the Phase 13 adapter still resolves through the registry, and all Phase 13 run artifacts remain untouched.

## Genericity Remediation

A post-implementation review found three mismatches between the generic adapter
claim and its implementation. They were resolved within Phase 14 rather than
deferred to semantic ontology work:

- Staged month headings now derive from each event's ISO date instead of using
  a fixed July 2026 heading. Source event order is preserved, and a new heading
  is emitted whenever the month changes.
- The runner adds the manifest's canonical `topic` to `prepare_metrics.json`.
  The adapter uses that context in `RUN_SUMMARY.md` and `run_metrics.json`, with
  no change to the adapter CLI contract.
- `##` is the canonical event boundary. Nested `###` and deeper headings remain
  part of the parent event body; the earlier `##`/`###` architecture wording was
  documentation drift.

### Remediation Evidence

| Run | Staged | Merged | Tagged | Errors | Verdict | Trend |
|-----|--------|--------|--------|--------|---------|-------|
| `phase14_genericity_fix_baseline` | 50 | 50 | 50 | 0 | PASS | Compared with prior Phase 14 evidence |
| `phase14_genericity_fix_trend` | 50 | 50 | 50 | 0 | PASS | COMPARED with remediation baseline |

The remediation trend run retains all 10 entity types and all 7 relation types,
with 31 entities, 24 relations, trend evidence, and source attribution. Its
staged files contain date-derived headings including January 2022, June/August
2025, and February/July 2026. InsuranceChatbot registry resolution was verified
with a dry-run, and the historical Phase 13/14 evidence directories and archived
source bundle were preserved.

### Remediation Validation

- `pytest -q`: 141 passed
- `python tools/docs_link_check.py`: 31 files scanned, 27 references valid
- `python tools/security_scan.py --root . --fail-on-findings`: 668 files scanned, 0 findings

## Ontology Coverage (Trend Run)

All 10 Phase 13 entity types present:
- Topic, SourceBundle, TopicAdapter, TopicRun
- StagedSource (5 per staged file), ReportEvent, Theme (8 themes)
- Metric (2 — main metrics + source attribution)
- EvidenceArtifact (10 — all core + optional files)
- Verdict (PASS)

All 7 relation types present:
- `consumes`, `uses_adapter`, `produces`, `contains`
- `tagged_with`, `measures`, `summarizes`

Two topics (insurancechatbot + pipelinechronicle) now have successful generic-run
evidence with identical ontology spine coverage.

## Is Phase 15 (Semantic Ontology Expansion) Justified?

**Yes, cautiously.** Now that two different topics have passed through the generic
runner with stable evidence and matching ontology spines, the project has enough
multi-topic evidence to begin designing a richer project-level ontology. However:

- The ontology should remain **incremental** — add entity relationships and
  attributes one at a time, not all at once.
- Any NLP/POS-based extraction (Phase 15) should be designed to work across
  both topic formats, not hardcoded to one.
- If Phase 15 involves a database or graph backend, ensure the runner's current
  file-based evidence contract (JSON artifacts per run directory) is preserved
  as the canonical source of truth.

## Files Changed/Created

| File | Action |
|------|--------|
| `tools/prepare_generic_markdown_chronicle.py` | Created |
| `tools/run_topic_report.py` | Updated (ADAPTER_REGISTRY entry) |
| `WordHorrorStories/pipelinechronicle/topic_manifest.json` | Created |
| `WordHorrorStories/pipelinechronicle/themes.pipelinechronicle.json` | Created |
| `WordHorrorStories/pipelinechronicle/README.md` | Created |
| `tests/test_prepare_generic_markdown_chronicle.py` | Created |
| `tests/test_run_topic_report.py` | Updated (registry test + flaky test fix) |
| `docs/PHASE14_SECOND_TOPIC_ONTOLOGY_READINESS.md` | Created |
| `ROADMAP.md` | Updated |
| `PLAN.md` | Updated |
| `README.md` | Updated |
| `ARCHITECTURE_AND_MODULES.md` | Updated |
| `INDEX.md`, `docs/README.md`, `ONTOLOGY_MODEL.md`, `JOURNAL.md` | Updated (Phase 14 context mapping) |
