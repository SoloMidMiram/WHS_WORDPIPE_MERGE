# Project Phase 15 — Semantic Ontology Design

> Date: 2026-07-17 / 1405/04/26<br>
> Status: Design and decision-gate artifact (provenance foundation and architecture stability gate implemented)<br>
> Scope: Project-level topic-report ontology — **not** InsuranceChatbot’s internal “Phase 15”

## Naming note

**Project Phase 15** refers to this repository’s topic-report ontology track.
InsuranceChatbot source documents independently use the label “Phase 15” for
repository reorganization and related work. Those source labels must not be
used to name or justify this project phase.

## Exact semantic question

> Which source document and source section supports each report event, and which
> stable cross-topic concepts are evidenced by that event?

### What this slice implements

This Project Phase 15 foundation slice answers only the **file provenance** half
of the first clause (“which source document…”) at **file → staged file**
granularity. It does **not** answer “which source section” per individual event,
and it does **not** extract semantic concepts automatically.

Manual examples below are illustrative evidence for design, not extraction
accuracy results.

## Provenance maturity levels

| Level | Chain | Status after this slice |
|-------|-------|-------------------------|
| File-level | Source file → staged file | **Implemented** (`source_lineage`, lineage-aware aggregate attribution) |
| Section-level | Source section → individual ReportEvent | **Implemented in Project Phase 16** as evidence sidecars (`event-lineage-v1` / `event-correlation-v1`); ontology individuals deferred |
| Concept-level | Individual ReportEvent → SemanticConcept | **Outstanding** |

File-level lineage proves:

```text
SourceBundle → raw source file → StagedSource
```

It does **not** prove:

```text
source section → individual ReportEvent
```

Current `source_attribution.json` remains **aggregate by staged source**. Do not
claim the full `SourceBundle → StagedSource → ReportEvent` chain is repaired.

A future source-section locator might need fields such as:

```json
{
  "source_file": "ARCHIVE_REPORT.md",
  "section_heading": "Tool Inventory",
  "section_ordinal": 3
}
```

Do not implement that shape until stable individual event identity and
adapter-specific section semantics are decided.

## Current ontology spine (unchanged)

Per-run `topic_run_ontology.json` still emits exactly:

- **10 entity types:** Topic, SourceBundle, TopicAdapter, TopicRun, StagedSource,
  ReportEvent, Theme, Metric, EvidenceArtifact, Verdict
- **7 relation types:** consumes, uses_adapter, produces, contains, tagged_with,
  measures, summarizes

`ReportEvent` remains **aggregate**:

```text
report_event:<topic>:<run_id>
```

with a run-level count property. Event-level relations must not be attached to
this aggregate as a shortcut.

## Candidate future ontology additions (not approved schema)

Design candidates only — **do not emit** in this slice:

| Kind | Name | Proposed shape |
|------|------|----------------|
| Entity | `SemanticConcept` | Stable cross-topic (or explicitly scoped) concept |
| Relation | `derived_from` | ReportEvent → StagedSource |
| Relation | `mentions` | ReportEvent → SemanticConcept |

Prerequisites before emission:

- Stable **individual** ReportEvent identifiers
- Per-event provenance (at least section locator or equivalent)
- Vocabulary supported by both topics or explicitly scoped
- Aggregate-to-individual migration design
- Explicit schema version 1 additive vs schema version 2 decision

## Candidate stable individual event ID

Evaluate, do **not** implement:

```text
report_event:<topic>:<sha256(normalized_source_id + date + normalized_title)>
```

### Design evaluation

| Concern | Notes |
|---------|--------|
| Title normalization | Collapse whitespace; Unicode NFC; strip markdown/emoji noise carefully; preserve meaning |
| Duplicate titles across sources | Include normalized source identity in the hash input |
| Same title/date in different sections | May collide; may need section ordinal or body fingerprint later |
| Source renames | Prefer stable source id (manifest path or content id) over display filename if renames are expected |
| Date correction | ID changes if date changes — document as intentional identity break |
| Merge/dedup | Merged events need a defined policy: keep one ID, alias map, or new ID |
| Identical repeated runs | Same inputs should yield same IDs (deterministic hash, no runtime order) |
| Collision handling | Detect hash collisions; append disambiguator only when proven |
| Raw vs staged source | Hash should prefer **raw source identity** for provenance; staged filename is adapter-local |
| Migration from aggregate | Keep aggregate entity for run summaries; add individual entities without silently replacing aggregate IDs |

## Dual-topic illustrative evaluation

Examples drawn from existing Phase 13/14 outputs. Illustrative only.

### insurancechatbot

| Event (date / title) | Raw source | Staged source | Candidate cross-topic concepts | Topic-specific (do not promote yet) | Ambiguity |
|----------------------|------------|---------------|--------------------------------|-------------------------------------|-----------|
| 2026-05-14 / `6cb6634 - chore: initial commit — Insurance FAQ Knowledge Base` | `Commit history.md` | `01_commit_history.md` | Repository bootstrap; documentation evidence | Insurance FAQ KB; Persian FAQ pairs | Commit subject vs roadmap “phase” labels |
| 2026-05-15 / `caa148c - Phase 5b: Deep Search KB expansion` | `Commit history.md` | `01_commit_history.md` | Knowledge-base expansion; retrieval | InsuranceChatbot Phase 5b numbering | “Phase 5b” is topic-local, not Project Phase |
| 2026-05-11 / Phase Completion Tracker | `ROADMAP.md` | `03_roadmap.md` | Progress tracking; milestone reporting | Roadmap emoji/section chrome | File-level lineage cannot prove the source section without a locator |

### pipelinechronicle

| Event (date / title) | Raw source | Staged source | Candidate cross-topic concepts | Topic-specific (do not promote yet) | Ambiguity |
|----------------------|------------|---------------|--------------------------------|-------------------------------------|-----------|
| 2026-02-14 / `ARCHIVE REPORT - 2. Tool Inventory` | `ARCHIVE_REPORT.md` | `01_ARCHIVE_REPORT.md` | Tool inventory; archival reporting | Archive-time snapshot wording | Section ordinal needed for stable section provenance |
| 2025-06-01 / `ROADMAP - ✅ Completed: ingest.py` | `ROADMAP.md` | `05_ROADMAP.md` | Pipeline stage completion; ingest | Milestone A1 labels | Duplicate “Future” vs “Completed” headings need careful IDs |
| 2025-08-06 / `README - Build Order (Prioritised` | `README.md` | `03_README.md` | Build order; workflow documentation | Chronicle-specific tool names | Truncated titles in merge may affect hash stability |

Cross-topic concept candidates that appear supportable by both topics (still
manual): **documentation evidence**, **pipeline/tooling evolution**,
**repository organization**, **quality gates / verification**. Do not promote
InsuranceChatbot phase numbers or Chronicle milestone codes to global concepts
without review.

## Decision gate

Semantic implementation (extraction + emission) remains blocked until:

1. Stable individual ReportEvent IDs are decided.
2. Both topics express provenance without filename reconstruction (file-level
   lineage is the foundation; section locators still outstanding).
3. Candidate vocabulary is supported by both topics or explicitly scoped.
4. Aggregate-to-individual ontology migration is designed.
5. Schema version 1 additive compatibility versus schema version 2 is decided.
6. A manual review/evaluation method exists for concept assignment.

## Related evidence

- Superseded lineage run: InsuranceChatbot `phase15_lineage_validation` was
  regenerated in place before collision protection existed. Its earlier bytes
  cannot be reconstructed, so it is preserved but is not authoritative proof
  of append-only execution.
- Authoritative closeout runs: `phase15_lineage_validation_v2` (per topic output base)
- Prior multi-topic spine: Phase 13/14 run directories under
  `WordHorrorStories/*/output/`
- Runner contract: `tools/run_topic_report.py` (`validate_prepare_metrics`,
  `source_lineage`, lineage-aware `source_attribution.json`)

## Provenance closeout and input migration

**Date:** 2026-07-17 (1405/04/26)

The closeout adds enforcement without expanding the semantic ontology:

- Topic runs reserve a new output directory atomically and reject collisions,
  including dry-run preflight. Unsafe multi-segment run IDs are rejected, and
  there is no overwrite switch.
- `source_file` may remain a nested portable relative path, while staged paths
  must be top-level filenames because Chronicle consumes only top-level `*.md`.
- Preparation coverage must be finite as well as between zero and 100.
- The 16 ChatGPT Chronicle and three InsuranceChatbot Markdown inputs moved
  byte-for-byte into `inputs/<corpus>/markdown/` and are protected by
  `inputs/catalog.json`. Exact duplicate and derived members remain in the
  established 16-file corpus and are explicitly classified.
- No source DOCX exists in this repository. The three DOCX files under
  `_ARCHIVE/evidence/generated-reports/` are generated evidence, not inputs;
  the referenced `ChatGPTLitrature.docx` is absent and was not fabricated.
- `AGENTS.md` now requires repository inspection, evidence labels, reference
  scans, hash checks, and run-ID availability checks before material claims.

This repairs file-level provenance and preservation policy only. Stable
individual event IDs, section locators, semantic extraction, and schema
evolution remain behind the decision gate above.

### Controlled closeout evidence

| Topic | Run | Staged / merged / tagged | Lineage / mismatches | Trend | Ontology | Verdict |
|-------|-----|---------------------------|----------------------|-------|----------|---------|
| insurancechatbot | `phase15_lineage_validation_v2` | 200 / 200 / 194 | 3 / 0 | COMPARED | 10 entity types / 7 relation types | PASS |
| pipelinechronicle | `phase15_lineage_validation_v2` | 50 / 50 / 50 | 5 / 0 | COMPARED | 10 entity types / 7 relation types | PASS |

The full suite passed with **192 tests**. The canonical input and root checks
passed. The migrated Chronicle corpus still produced **224 events across 16
files**; its legacy verifier continued to return failure for four known
zero-event narrative/manual-merge inputs, so this result is recorded rather
than relabelled as a clean verifier pass. A repeated Insurance dry-run against
the v2 ID exited 1 and left its tree digest unchanged.

Pre/post preservation checks matched exactly for 212 historical Phase 13–15
files (`ca6c0a...49b5c`) and 123 `_ARCHIVE/pipeline-chronicle` plus
`_WORK/snapshot` files (`5cbbbe...6afd`).

## Architecture stability plan and implementation record

**Date:** 2026-07-17 (1405/04/26)<br>
**Roadmap slice:** 15.11<br>
**Decision:** Completed as documentation and guardrails; no production restructuring

### Approved plan

| Planned concern | Approved constraint |
|-----------------|---------------------|
| Whole-project vision | Map six bounded domains onto the existing three subsystems plus Topic Reporting; do not derive packages from ontology entities or text frequency |
| Logical flow | Distinguish catalog/operator prerequisites from the topic-runner lifecycle and describe the observed fail-closed preparation gate and append-only reservation |
| Separation of concerns | State machine-enforced v1 import directions separately from design-only rules |
| Enforcement | Add a narrow AST checker only after inventorying current imports and establishing a green baseline |
| Exceptions | Keep one reviewed registry with path and reason; do not scatter suppressions |
| Refactoring | Preserve the exact conditional Phase 15 trigger and extract no production seam in this slice |
| Evidence | Reuse read-only v2 evidence and preservation inventories; do not execute topic runs for documentation/checker changes |

### Implemented result

- `ARCHITECTURE_AND_MODULES.md` now contains the domain crosswalk, ownership table, whole-project and topic-run flowcharts, separation rules, explicit non-goals, refactor eligibility gate, and directional-frequency appendix.
- `tools/check_architecture_boundaries.py` enforces the approved v1 static import directions and fails closed on parse errors or forbidden edges.
- `tests/test_architecture_boundaries.py` characterizes the current tree, forbidden directions, registry specificity, test exclusions, and `TYPE_CHECKING` behavior.
- CI and the README, verification, and test pre-push lists run the boundary checker beside layout, input-catalog, link, and security checks.
- `AGENTS.md`, ROADMAP, PLAN, ontology, repository boundaries, and the implementation-alignment audit use the same conditional-refactor language.
- Historical/snapshot content and both `phase15_lineage_validation_v2` evidence trees were inventoried before and after validation and remained byte-identical. No topic command or new evidence directory was created.

The dated executable results for this slice are recorded in `VERIFICATION.md` and `JOURNAL.md`, not frozen into roadmap or architecture claims.

### Enforcement boundary and accepted limitations

- The six registry entries are **reviewed path roles**, not six exemptions. No entry currently bypasses a forbidden v1 edge; the pipeline wrappers do not intersect a classified forbidden rule, and the composition root's adapter import is already allowed.
- The v1 AST scan covers `wordpipe/` and `pipeline/`. It does **not** scan `tools/`, so topic-runner and adapter import hygiene remains a policy and characterization-test responsibility.
- Detailed inward rules for `wordpipe.steps` remain documentation-only. They must not become CI rules without a fresh green inventory and focused fixtures.
- AST inspection cannot observe dynamic imports, subprocess execution, plugin entry points, or test-time module loading and is not a call-graph or security proof.
- A single synchronized edit is not a secondary refactor trigger. Two dated occurrences with paths, rationale, and tests must be recorded in `JOURNAL.md` or the implementation-alignment audit.

### Phase closeout decision

The stability slice does not justify a runner split, adapter-helper package, ontology projector extraction, NLP, index move, or filesystem reorganization. Broad topic-runner decomposition remains conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

The recommended next phase is a separately reviewed **event identity and section-level provenance** design slice. It should characterize where identity is currently lost—adapter `ChronicleEvent` values contain only date/title/body, Chronicle ingest emits the same fields, and merge deduplicates by date plus normalized body hash—before approving any schema or implementation change. SemanticConcept extraction remains blocked.
