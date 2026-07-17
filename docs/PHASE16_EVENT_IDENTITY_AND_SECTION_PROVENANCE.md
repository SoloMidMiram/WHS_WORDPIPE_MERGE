# Project Phase 16 — Stable Event Identity and Section-Level Provenance

> Date: 2026-07-17 / 1405/04/26<br>
> Status: Implemented (artifact schemas + runner correlation; ontology emission deferred)<br>
> Scope: Section → SourceEvent → merged ReportEvent evidence via sidecars

## Naming note

**Project Phase 16** is this repository’s topic-report provenance track.
It does **not** change Chronicle merge keys and does **not** emit individual
`ReportEvent` entities into `topic-run-ontology-v1`.

## Exact question answered

> Which source document **and source section/commit locator** supports each
> merged report event?

Phase 15 answered file → staged file. Phase 16 answers section/commit locator →
individual ReportEvent **identity in evidence sidecars**.

## Artifact schemas (not ontology)

| Schema | Owner | When written |
|--------|-------|--------------|
| `event-lineage-v1` | Runner finalizes after pre-pipeline gate | After prepare validation; fingerprints filled post-pipeline |
| `event-correlation-v1` | Runner | After pipeline, **before** adapter summarize |

These do **not** modify `topic-run-ontology-v1`.

### Adapter raw emit

Registered adapters write `event_lineage.json` next to `prepare_metrics.json` and set:

```json
"event_lineage_file": "event_lineage.json"
```

Raw records include locator identity fields only. Adapters must **not** emit
`topic`, `run_id`, final `source_event_id`, or merge-compatible `body_sha256`.

**Locator fields:**

- `locator_kind`: `markdown_section` | `commit_heading`
- `source_file` (portable relative)
- `candidate_ordinal` (1-based among **all** candidates, including empty-skipped)
- `heading_level` **or** normalized `commit_sha` (lowercase hex, length ≥ 7)
- `original_heading_text` (section title or commit subject)
- Descriptive: `staged_file`, `staged_event_ordinal`, `date`, `title`, optional `start_line`

Empty candidates advance ordinals but are omitted from the emit list.
Duplicate commit SHA locators within one source fail closed.

### SourceEvent / ReportEvent ID construction

Domain-separated SHA-256 over UTF-8 fields joined by `\0`:

- SourceEvent canonical:<br>
  `source-event-v1\0<source_file>\0markdown_section\0<ordinal>\0<heading_level>\0<original_heading_text>`<br>
  or<br>
  `source-event-v1\0<source_file>\0commit_heading\0<ordinal>\0<commit_sha>\0<original_heading_text>`<br>
  → `source_event:<topic>:<digest>`

- Individual ReportEvent canonical:<br>
  `report-event-v1\0<date>\0<body_hash>`<br>
  → `report_event:<topic>:<digest>`

`body_hash` is computed **only** from `pipeline/normalised/<staged_file>` via
Chronicle `extract_events` + `compute_body_hash`. Adapter-side hashes of raw or
staged draft text are forbidden. Do **not** re-hash bodies from `merged.md`:
keep-both conflict HTML comments are written between events and attach to the
preceding body when re-parsed, mutating fingerprints.

SHA-256 ID collision: fail closed; record both canonical payloads; do **not**
append disambiguators.

Many SourceEvents sharing `(date, body_hash)` → one ReportEvent with many
`source_event_ids`. That is **not** `ambiguous_matches`.

`ambiguous_matches` is reserved for broken ordinal mapping, conflicting ReportEvent
payloads under one id, or non-deterministic correlation.

### Aggregate ontology ReportEvent (unchanged)

Ontology still emits one aggregate:

```text
report_event:<topic>:<run_id>
```

Individual ids live only in `event_correlation.json`.

## Lifecycle gates

```text
prepare (raw lineage + pointer)
  → pre-pipeline validate + event-lineage-v1 envelope
  → Chronicle pipeline
  → post-pipeline fingerprints + event-correlation-v1
  → summarize
  → attribution / trend
  → runner appends ## Event Provenance to RUN_SUMMARY
  → ontology + verdict
```

| Gate | Failure exit | Effect |
|------|--------------|--------|
| Pre-pipeline lineage | `prepare=1` | Failure ontology; stop before pipeline |
| Post-pipeline correlation | `provenance=1` | Failure ontology; **skip** successful summarize/PASS path |

Registered adapters require the pointer. Custom adapters may omit it; if present,
full validation still applies.

Under the runner’s fixed keep-both merge mode, `unmerged_source_event_count`
must be `0`.

## Evidence inventory

Do **not** add lineage/correlation files to `CORE_EVIDENCE_FILES` (would break
custom adapters without the pointer). When present, list them via
`OPTIONAL_EVIDENCE_FILES` in the ontology evidence inventory. Do **not** mix
root sidecars into `run_metrics.output_files` (pipeline inventory only).

## Why markers were rejected

HTML comments between staged bullets are appended to the **preceding** event body
during Chronicle ingest. Marker protocols would mutate body hashes. Sidecar
transport avoids that.

## Slice map

| Slice | Deliverable |
|-------|-------------|
| 16.0 | Permanent characterization tests |
| 16.1 | Raw lineage emit + pointer + pre-pipeline envelope |
| 16.2 | Post-pipeline correlation before summarize + provenance exit + summary section |
| 16.3 | This design doc + roadmap sync + controlled runs |
| 16.4 | Aggregate→individual ontology migration gate (design only; no emission) |

## Plan-to-implementation closeout audit

| Slice | Planned behavior | Implemented evidence |
|-------|------------------|----------------------|
| 16.0 | Characterize identity loss and merge-compatible hashing before production changes | Permanent tests cover whitespace/CRLF hashing, mojibake cleanup, nested-bullet escaping, unsafe inter-event comments, true duplicates, and keep-both conflicts |
| 16.1 | Emit raw locator records without making adapters own run context or final hashes | Both registered adapters write raw `event_lineage.json` plus a top-level `event_lineage_file`; the runner validates paths, counts, locator identity, ordinals, and collisions before the pipeline and adds the `event-lineage-v1` envelope |
| 16.2 | Correlate only from canonical normalised fingerprints and fail before a successful summary on provenance errors | The runner reads `pipeline/normalised/<staged_file>`, computes domain-separated ids, writes `event-correlation-v1`, sets `provenance=1` on failure, and appends the successful provenance summary after adapter summarize |
| 16.3 | Document the contract and create fresh append-only paired evidence | This document and the mapped ROADMAP/PLAN/JOURNAL/ontology/architecture records exist; both topics have `phase16_event_lineage_validation` evidence |
| 16.4 | Define but do not cross the aggregate-to-individual ontology gate | `topic-run-ontology-v1` remains aggregate with 10 entity types and 7 relation types; no individual ontology ReportEvent or semantic relation is emitted |

### Ownership and compatibility result

- Adapters own source-native locator extraction and raw event-lineage emission.
- The runner owns canonical topic/run context, identifier construction, post-pipeline correlation, evidence inventory, failure policy, and the summary addition.
- Chronicle remains topic-neutral and retains its existing merge key and fixed keep-both runner behavior.
- Registered adapter ids require the event-lineage pointer even when a manifest supplies an explicit script. Custom adapters may omit it; claimed optional lineage still validates fully.
- The new sidecars are artifact-specific v1 schemas and do not change `topic-run-ontology-v1`, manifest schema v1, or existing custom-adapter CLI arguments.

### Closeout verification

- Import-safety simulation now removes blocked optional dependencies even when test collection preloaded them, then restores the original modules. The targeted import-safety plus Phase 16 group passes **17 tests**.
- The full suite passes **216 tests** on 2026-07-17 / 1405/04/26.
- Existing controlled evidence confirms InsuranceChatbot 200 lineage / 200 merged / exactly 194 theme-bearing events and PipelineChronicle 50/50/50, with both correlation schemas present, empty ambiguity arrays, provenance summary sections, and the unchanged aggregate 10/7 ontology spine.
- This closeout performs no topic run and does not rewrite either Phase 16 evidence directory.

### Remaining evidence limits

Phase 16 proves locator-to-normalised-event identity and keep-both merged-count parity. It does **not yet independently compare the actual merged survivor key set**: current correlation constructs the survivor set from the same normalised keys, so `unmerged_source_event_count == 0` is an invariant of that implementation plus the fixed keep-both assumption rather than independent survivor-membership evidence.

Only one provenance-enabled controlled run exists per topic. Therefore the first Phase 16.4 migration prerequisite—stable correlation across at least two fresh controlled runs—has not been met. Phase 17 must add merge-note-aware survivor verification and a second paired stable-id comparison before ontology v2 design can be considered implementation-ready.

## Acceptance evidence

| Topic | Run ID | Expected |
|-------|--------|----------|
| insurancechatbot | `phase16_event_lineage_validation` | 200 lineage events; 3 file lineage; 200 merged; **exactly 194** theme-bearing; 0 errors; PASS; correlation complete; `ambiguous_matches` empty; `unmerged_source_event_count` 0; ontology still 10 entities / 7 relation types (aggregate ReportEvent) |
| pipelinechronicle | `phase16_event_lineage_validation` | 50/50/50; 5 file lineage; PASS; trend COMPARED; same ontology invariants |

## Slice 16.4 — Aggregate → individual ontology migration gate

**Decision: do not emit individual ReportEvent entities yet.**

Migration is allowed only when **all** of the following are true:

1. `event-correlation-v1` is stable across both registered topics for ≥2 fresh
   controlled runs with `ambiguous_matches == []` and
   `unmerged_source_event_count == 0`.
2. An explicit schema bump plan for `topic-run-ontology-v1` is approved
   (entity count / relation count changes are intentional versioned changes).
3. Aggregate `report_event:<topic>:<run_id>` either remains as a rollup entity or
   is replaced with a documented migration that keeps EvidenceArtifact /
   Verdict consumers working.
4. No SemanticConcept / NLP / `derived_from` / `mentions` work is bundled into
   the same change.
5. Broad topic-runner decomposition remains gated by the exact AGENTS/ROADMAP
   conditional sentence; ontology entity growth alone does **not** authorize
   packaging splits.

Until that gate opens, section→event provenance is complete as **evidence**
(`event_lineage.json` + `event_correlation.json`), not as ontology individuals.

## Phase 17 planning handoff

Phase 17 is limited to **Event-Provenance Survivor Integrity and Repeatability**. Its planning agent must verify the current implementation, design a merge-note-aware actual-survivor comparison, choose the smallest auditable repeatability checker or artifact, and specify a second fresh paired run against the Phase 16 baseline. It must keep ontology emission, semantic extraction, merge behavior, package restructuring, index movement, input migration, and historical rewrites out of scope.

Candidate run id `phase17_event_provenance_repeatability` was absent under both topic output bases during this closeout inspection. Availability must be rechecked immediately before any future execution.

## Non-goals

- Semantic extraction / NLP / SemanticConcept
- Individual ontology ReportEvent emission
- Merge dedup / conflict-mode changes
- Marker / HTML-comment transport
- `tools/topic_report/` package split
- Historical rewrite of prior run trees

## Architecture constraints (locked)

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

Chronicle remains topic-neutral. One behavioral seam per slice. Ontology entities ≠ packages.
