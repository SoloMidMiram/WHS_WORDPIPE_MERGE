# Iterative Topic Performance Check Template

> Purpose: repeatable, topic-neutral performance review for turning source notes
> into a structured report with measurable extraction, tagging, and output quality.

Use this template for any topic: project history, research notes, incident logs,
course material, product discovery, travel journals, legal timelines, or another
long-form Markdown bundle. Keep the topic-specific adapter/config beside the
topic input; keep the measurement shape stable across runs.

---

## 1. Topic Card

| Field | Value |
|-------|-------|
| Topic name | `<topic>` |
| Audience | `<reader / maintainer / client / self>` |
| Source folder | `<relative path>` |
| Output folder | `<relative path>/output/<run_id>` |
| Topic manifest | `<topic-folder>/topic_manifest.json` |
| Prep adapter | `<registered adapter id or script>` |
| Theme config | `<theme config path>` |
| Report goal | `<what the report should help someone decide or understand>` |

## 2. Run Command

```powershell
python tools\run_topic_report.py `
  --manifest <topic-folder>\topic_manifest.json `
  --run-id <run_id>
```

Expected runner artifacts: `RUN_SUMMARY.md`, `run_metrics.json`,
`topic_run_manifest.json`, `topic_run_ontology.json`, `trend_report.json`,
`trend_report.md`, `source_attribution.json`, `run.log`, `performance.txt`,
`staged_input/`, and `pipeline/`.

## 3. Quantitative Check

| Metric | Current Run | Previous Run | Target / Gate | Notes |
|--------|-------------|--------------|---------------|-------|
| Input files |  |  | `>= 1` | |
| Input bytes |  |  | informational | |
| Input lines |  |  | informational | |
| Candidate source units |  |  | topic-defined | commits, sections, chapters, cases |
| Staged events |  |  | close to candidate units | |
| Extraction coverage |  |  | `>= 95%` unless intentionally filtered | |
| Merged events |  |  | should not unexpectedly inflate | |
| Events with theme tags |  |  | `>= 85%` for themed reports | |
| Duplicate/conflict entries |  |  | review if `> 0` | |
| Warning count |  |  | `0` preferred | |
| Error count |  |  | `0` required | |
| Wall-clock seconds |  |  | compare to prior run | |
| Source attribution total |  |  | equals staged/merged event count unless filtered | |

## 4. Quality Read

Sample the outputs before trusting the numbers:

- `pipeline/merged.md`: Are events readable and sorted by real dates?
- `pipeline/chronicle_tagged.md`: Are theme comments useful, not noisy?
- `pipeline/appendix/event_index.md`: Does the index tell the story at a glance?
- `pipeline/appendix/theme_index.md`: Do theme groups match the topic vocabulary?
- `source_attribution.json`: Does each staged source map to a normalised file and event count?
- `trend_report.md`: Does the current-vs-previous delta make sense?
- `run.log`: Are there warnings that the summary script missed?

## 5. Iteration Notes

| Finding | Evidence | Next adjustment | Owner | Status |
|---------|----------|-----------------|-------|--------|
| `<example: dates collapsed to fallback>` | `<file + line or metric>` | `<parser fix>` | `<name>` | `<open/done>` |
| `<example: weak theme coverage>` | `<tag count / sample>` | `<theme keyword update>` | `<name>` | `<open/done>` |

## 6. Run Verdict

Choose one:

- `PASS`: report is usable, metrics meet gates, sampled quality is acceptable.
- `REVIEW`: report generated, but quality needs manual review before sharing.
- `FAIL`: a stage failed or output is structurally misleading.

Verdict: `<PASS | REVIEW | FAIL>`

Short rationale:

```text
<one paragraph, based on evidence>
```
