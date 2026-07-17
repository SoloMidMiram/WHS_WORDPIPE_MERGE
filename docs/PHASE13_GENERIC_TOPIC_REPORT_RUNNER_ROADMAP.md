# Phase 13 Roadmap — Generic Topic Report Runner & Performance Trends

> Date: 2026-07-16 / 1405-04-25<br>
> Status: Completed<br>
> Builds on: Phase 12 InsuranceChatbot topic-adapter run and `docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md`

## Implemented (2026-07-16 / 1405-04-25)

- **13.1**: Added `topic_manifest.json` schema at `WordHorrorStories/insurancechatbot/topic_manifest.json` with `schema_version`, `topic`, `input_dir`, `adapter`, `themes_config`, `index_config`, `output` policy, and `quality_gates`. Validation rejects missing keys, bad types, non-existent paths, and negative gate values.
- **13.2**: Added `tools/run_topic_report.py` — the generic one-command runner. Accepts `--manifest` (required), `--dry-run`, and `--run-id` flags. Executes three stages (prepare via adapter, pipeline via `chain.ps1`, summarize via adapter) with log capture, wall-clock timing, and ontology output. Stdlib only, no changes to `pipeline/`, `wordpipe/`, or `chain.ps1`.
- **13.3**: Added a small adapter registry to `tools/run_topic_report.py`. `prepare_insurancechatbot_chronicle` is the first registered adapter; direct `adapter.script` remains supported for custom/backward-compatible manifests.
- **13.4**: Added previous-run discovery under the same topic output folder and trend reports in `trend_report.json` and `trend_report.md`.
- **13.5**: Hardened ontology output. Each run emits `topic_run_manifest.json` and `topic_run_ontology.json`; ontology includes all 10 entity types, all 7 relation types, the ontology file itself as an `EvidenceArtifact`, trend artifacts when present, source attribution as evidence, and `previous_run` on `TopicRun` when compared.
- **13.6**: Added `source_attribution.json` with staged source -> normalised file -> contributed event count.
- **13.7**: Expanded `tests/test_run_topic_report.py` to cover registry fallback, trend comparison, source attribution, ontology evidence, and existing manifest/command/dry-run behavior.
- **13.8**: Updated README, pipeline README, architecture reference, iterative performance template, roadmap, and plan with the generic runner command and completion evidence.

### Validation

- `pytest -q`: 124 passed
- Controlled baseline run: `WordHorrorStories/insurancechatbot/output/phase13_baseline_validation/`
- Controlled trend run: `WordHorrorStories/insurancechatbot/output/phase13_trend_validation/`
- Trend run metrics: 3 input files, 195,293 bytes, 3,285 lines, 200 staged events, 200 merged events, 194 events with theme tags, 0 duplicate/conflict entries, 0 warnings, 0 errors, 6.51s runner wall-clock time.
- Trend comparison: `trend_report.json` compares against `phase13_baseline_validation`; event/tag/error counts were stable and runtime changed by +1.54s.
- Source attribution: 3 staged sources contributed 169, 16, and 15 events for a total of 200.
- Ontology verdict: `PASS`; all 10 entity types and all 7 relation types present.

## Summary

Phase 13 turns the one-off InsuranceChatbot report success into a reusable
topic-report system. The goal is not merely to add another script; it is to make
topic runs repeatable, measurable, comparable, and ready to feed a project-level
ontology later.

Strategic ontology work belongs here, but only as a lightweight spine:
define the entities, identifiers, evidence links, and metrics that every topic
run must emit. Full ontology population, NLP extraction, and deep semantic
reasoning should wait until the runner has produced several comparable runs.

## Phase 13 Goals

| Goal | Outcome |
|------|---------|
| One-command runner | A single command prepares input, runs the Chronicle pipeline, captures logs, measures runtime, summarizes results, and writes metrics. |
| Topic adapter registry | Topic folders can declare which adapter, theme config, input folder, and output policy to use without custom shell glue. |
| Performance trend ledger | Repeated runs can be compared by extraction coverage, event count, tag coverage, warning/error count, and wall-clock time. |
| Strategic ontology spine | Topic runs emit stable concepts such as Topic, SourceBundle, Adapter, Run, Event, Theme, Metric, Evidence, and Verdict. |
| Better source attribution | Generated appendix files show which staged source contributed which events clearly enough for audit. |

## Implementation Slices

| Slice | Task | Status |
|-------|------|--------|
| 13.1 | Define topic-run manifest schema (`topic`, `input_dir`, `adapter`, `themes`, `output_dir`, `quality_gates`) | Done |
| 13.2 | Add a generic runner command that executes prepare -> pipeline -> summarize -> trend update | Done |
| 13.3 | Refactor InsuranceChatbot prep into the first registry-backed adapter | Done |
| 13.4 | Add trend comparison against the latest previous run for the same topic | Done |
| 13.5 | Add machine-readable `topic_run_manifest.json` and `topic_run_ontology.json` outputs | Done |
| 13.6 | Improve source attribution in `source_manifest.md` and/or a sidecar JSON | Done (`source_attribution.json`) |
| 13.7 | Add tests for manifest parsing, runner dry-run behavior, trend comparison, and ontology-spine output | Done |
| 13.8 | Update README, roadmap, architecture, and performance template with the generic runner command | Done |

## Minimal Ontology Spine

Phase 13 should define these entity types and relationships, without attempting
full semantic extraction:

| Entity | Meaning | Example |
|--------|---------|---------|
| Topic | A named subject being reported on | `insurancechatbot` |
| SourceBundle | The raw input set for a run | `inputs/insurancechatbot/markdown` |
| TopicAdapter | Parser/stager used before Chronicle | `prepare_insurancechatbot_chronicle` |
| TopicRun | One measured execution | `20260716_091000` |
| StagedSource | Adapter output fed into Chronicle | `01_commit_history.md` |
| ReportEvent | A normalized event after ingest/merge | commit, roadmap section, project digest section |
| Theme | A topic vocabulary label | `Ontology`, `Testing/CI` |
| Metric | A measured count or duration | `merged_event_count=200` |
| EvidenceArtifact | Output proving a run claim | `RUN_SUMMARY.md`, `run_metrics.json` |
| Verdict | PASS/REVIEW/FAIL decision | `PASS` |

Core relationships:

- `TopicRun consumes SourceBundle`
- `TopicRun uses TopicAdapter`
- `TopicAdapter produces StagedSource`
- `TopicRun produces EvidenceArtifact`
- `ReportEvent belongs_to TopicRun`
- `ReportEvent tagged_with Theme`
- `Metric measures TopicRun`
- `Verdict summarizes TopicRun`

## Acceptance Criteria

- A topic run can be launched with one command from a manifest.
- The InsuranceChatbot topic can run through the new generic command and produce
  equivalent or better metrics than the Phase 12 reference run.
- Each run writes `RUN_SUMMARY.md`, `run_metrics.json`, `topic_run_manifest.json`,
  `topic_run_ontology.json`, `trend_report.json`, `trend_report.md`, and
  `source_attribution.json`.
- Trend output shows at least current vs previous values for staged events,
  merged events, theme-tagged events, warning/error count, and wall-clock time.
- `pytest -q`, docs link check, and security scan remain green.

## Why Not Full Ontology Yet?

It is too soon for a large ontology-population phase because the system has only
one successful non-Chronicle topic run. Building a full ontology now would
encode guesses. Phase 13 should instead create the small, stable ontology spine
that every future run must emit. After two or three different topics pass
through the generic runner, the project will have enough evidence to design a
larger strategic ontology model with less rework.

**Phase 14 follow-up:** See [`PHASE14_SECOND_TOPIC_ONTOLOGY_READINESS.md`](PHASE14_SECOND_TOPIC_ONTOLOGY_READINESS.md)
for the second-topic implementation (`pipelinechronicle`) that proves multi-topic
reusability of the Phase 13 runner. Phase 15 semantic ontology expansion is now
justified – see that doc for the readiness assessment.
