# Project Phase 17 — Event-Provenance Survivor Integrity and Repeatability

> Date: 2026-07-17 / 1405/04/26<br>
> Status: Implemented (survivor verification + paired stability evidence)<br>
> Scope: Actual merged-survivor key integrity and two-run ID stability — **not** ontology emission

## Naming note

**Project Phase 17** closes the gate between Phase 16 sidecars and any future
individual ReportEvent ontology design. It does **not** bump
`topic-run-ontology-v1` or emit individual ReportEvent entities.

## Assurance upgrade

| Field | Phase 16 | Phase 17 |
|-------|----------|----------|
| `unmerged_source_event_count` | Keep-both **count-parity** invariant (normalised keys vs the same set) | Count of normalised source fingerprints **absent from actual merged survivors** after merge-note-aware parse |
| `survivor_verification.method` | Absent | `merged-note-aware-v1` |

Do **not** reinterpret historical Phase 16 zeros as Phase 17-strength survivor membership.

## Survivor verification (`merged-note-aware-v1`)

Owned by [`tools/run_topic_report.py`](../tools/run_topic_report.py) inside
`correlate_event_provenance`:

1. Expected unique keys from `pipeline/normalised/` (`extract_events` + `compute_body_hash`).
2. Read `pipeline/merged.md`; strip exact keep-both note
   `<!-- Duplicate date, different content -->` only when it immediately precedes
   an Event heading (whitespace-only blank lines allowed; LF/CRLF) **and** the
   previous Event shares that date.
3. If the previous event body already ends with that exact note before a
   same-date next Event → fail closed (`ambiguous_merge_note_vs_body_content`).
4. Parse cleaned body; duplicate keys in actual merged output → fail closed.
5. `missing` / `unexpected` key sets must be empty; unmerged must be 0.
6. Raw `## Event:` heading count is diagnostic only.

Authority of tests: real `merge_files(..., conflict_mode="keep-both")` output,
not `merge.py` source-text synchronization.

## Repeatability comparator

[`tools/compare_event_provenance_stability.py`](../tools/compare_event_provenance_stability.py):

- Pure `compare_event_provenance_stability(...)` plus CLI writer.
- **Non-mutating** of topic-run directories.
- Writes only into a **separately reserved** comparison-evidence directory
  (e.g. `…/output/phase17_provenance_stability/`).
- Refuses output collisions; atomic JSON write on success and verified drift.
- Exit codes: `0` stable, `1` verified drift, `2` invalid/incomplete (no partial JSON).
- Explicit baseline run id `phase16_event_lineage_validation` (not trend selection).
- Validates topic/schema/run_ids, duplicate IDs, lineage↔correlation consistency,
  and both `source→report` and `report→sources` maps.
- Titles are diagnostic only; identity remains date + normalised body hash.

Stability reports are **not** added to `OPTIONAL_EVIDENCE_FILES` (runner does not
create them during the topic run). Index them in VERIFICATION/JOURNAL separately.

## Controlled evidence

| Topic | Baseline | Candidate | Stability dir |
|-------|----------|-----------|---------------|
| insurancechatbot | `phase16_event_lineage_validation` | `phase17_event_provenance_repeatability` | `phase17_provenance_stability` |
| pipelinechronicle | same | same | same |

Acceptance: ICB 200/200/**194**; PC 50/50/50; survivor missing/unexpected 0;
unmerged 0 (Phase 17 sense); stability exit 0; ontology aggregate 10/7; PASS.

## Closeout hardening follow-ups

The Phase 17 gate is implemented and its controlled evidence is valid. Review
identified small comparator-contract improvements that should be completed
before using the tool as a general cross-run gate:

- require the candidate correlation to declare `merged-note-aware-v1` with
  zero missing, unexpected, unmerged, and ambiguous results;
- reject non-object lineage entries and validate declared counts against the
  actual lineage/correlation collections;
- record title-only drift as a non-identity diagnostic;
- avoid leaving an empty reserved directory after invalid evidence and publish
  the JSON and Markdown comparison reports as one complete unit.

These are local validation/atomicity improvements. They do not reopen survivor
identity, change the 10/7 ontology spine, or trigger runner decomposition.

## Non-goals

No SemanticConcept/NLP; no ontology schema bump; no `tools/topic_report/`;
no merge-key/conflict-mode change; no broad runner decomposition.

## Architecture constraints (locked)

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.
