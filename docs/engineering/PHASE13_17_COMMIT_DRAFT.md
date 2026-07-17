# Phase 13–17 Working-Tree Commit Draft

> Date: 2026-07-17 / 1405/04/26<br>
> Status: Draft only — no commit has been created<br>
> Baseline inspected: `dcb4c01` (`docs: record P0-P2 validation and reconcile top-level docs`)

## Why the scope starts at Phase 13

The current `main` commit predates the generic topic-report runner. The dirty
working tree contains the Phase 13 runner and adapters, Phase 14 second-topic
validation, Phase 15 provenance and repository guardrails, Phase 16 event
identity sidecars, and Phase 17 survivor/repeatability evidence. A commit
described as “Phase 15 only” or “Phase 17 only” would therefore omit material
dependencies that are not yet represented in Git history.

This draft records the real pending scope. It does not authorize `git add .`,
rewrite evidence, or perform another repository reorganization.

## Traceability map

| Slice | Implementation | Tests | Design and status | Controlled evidence |
|-------|----------------|-------|-------------------|---------------------|
| Phase 13 | `tools/run_topic_report.py`, registered Insurance adapter, topic manifest | `tests/test_run_topic_report.py` | `docs/PHASE13_GENERIC_TOPIC_REPORT_RUNNER_ROADMAP.md`, ROADMAP, PLAN | `phase13_baseline_validation`, `phase13_trend_validation` |
| Phase 14 | Generic Markdown adapter and PipelineChronicle topic configuration | Generic-adapter and runner tests | `docs/PHASE14_SECOND_TOPIC_ONTOLOGY_READINESS.md` | Phase 14 baseline/trend and genericity-fix runs |
| Phase 15 | Prepare-metrics contract, file lineage, run collision guard, input and architecture checks | Catalog, root-layout, architecture, adapter, and runner tests | `docs/PHASE15_PROJECT_SEMANTIC_ONTOLOGY_DESIGN.md`, `AGENTS.md` | `phase15_lineage_validation_v2` for both topics |
| Phase 16 | `event-lineage-v1` and `event-correlation-v1` sidecars | Phase 16 identity and runner tests | `docs/PHASE16_EVENT_IDENTITY_AND_SECTION_PROVENANCE.md` | `phase16_event_lineage_validation` for both topics |
| Phase 17 | `merged-note-aware-v1` survivor verification and stability comparator | Phase 17 survivor and stability tests | `docs/PHASE17_EVENT_PROVENANCE_SURVIVOR_AND_REPEATABILITY.md` | `phase17_event_provenance_repeatability` plus separately reserved stability reports |

Canonical status is mapped through `ROADMAP.md`, `PLAN.md`, `JOURNAL.md`,
`VERIFICATION.md`, `ONTOLOGY_MODEL.md`, `ARCHITECTURE_AND_MODULES.md`, `INDEX.md`,
`docs/README.md`, and `docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md`.

## Organization decision before modularity

Finish and commit the organization already present in the working tree before
starting new package work. Do not perform more moves during this closeout.

- Canonical inputs belong under `inputs/` and are governed by
  `inputs/catalog.json`.
- Active topic manifests and run evidence remain under
  `WordHorrorStories/<topic>/`; they are not historical archive content.
- Generated historical reports remain under
  `_ARCHIVE/evidence/generated-reports/`.
- Reporting utilities remain under `scripts/reporting/`.
- `_WORK/codex_smoke_chronicle/` is scratch output and should not be staged
  unless a separate evidence decision explicitly promotes it.
- The runner stays structurally stable. Ontology entities do not become
  packages merely because they exist in the model.

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

The next architecture work should therefore be semantic design and contract
pressure, not filesystem movement. If a primary trigger occurs, characterize
the behavior and extract one pure seam while preserving CLI and JSON contracts.

## Recommended commit organization

Use two dependency-ordered commits. This avoids pretending that the evolving
runner can be cleanly reconstructed as five independent historical commits.

### Execution decision

The current tree cannot demonstrate a green intermediate boundary between the
organization work and the Phase 13–17 runner work without temporarily removing
interdependent untracked implementation, evidence, and documentation. The
closeout therefore uses the guarded fallback from this document: one
consolidated commit with the subject
`feat(project): establish governed topic provenance through Phase 17`.
`_WORK/codex_smoke_chronicle/` remains excluded as scratch output.

### Commit 1 — repository and evidence governance

```text
chore(repo): govern corpus inputs and repository evidence

- move active Markdown inputs into the hash-catalogued inputs hierarchy
- preserve generated reports and reporting utilities under owned directories
- enforce root layout, input integrity, and architecture import boundaries
- add repository agent evidence rules and CI validation commands
- document active-topic, archive, working-tree, and generated-output ownership
```

Stage the migration pairs together and verify Git recognizes their relationship:

- former ChatGPT Markdown locations with `inputs/chatgpt-chronicle/markdown/`;
- root `_scripts/` deletions with `scripts/reporting/`;
- root DOCX deletions with `_ARCHIVE/evidence/generated-reports/`;
- governance tools, tests, CI, and boundary documentation.

### Commit 2 — generic topic provenance through Phase 17

```text
feat(topic-report): establish provenance and repeatability through Phase 17

- add the manifest-driven runner and registered topic adapters
- validate two topics with trends, attribution, and aggregate ontology evidence
- enforce preparation metrics, file lineage, and append-only run directories
- add section-level event identity and correlation sidecars
- verify actual merged survivors with merged-note-aware parsing
- compare Phase 16 and Phase 17 event IDs in reserved stability directories
- map Phase 13–17 design, evidence, limitations, and verification results

Validation:
- pytest: 231 passed on 2026-07-17
- architecture, root-layout, input-catalog, docs-link, and security checks passed
- both Phase 17 comparisons reported STABLE
- per-run ontology remains aggregate with 10 entity and 7 relation types
```

This commit owns the runner/adapters, topic manifests and curated evidence,
Phase 13–17 tests, phase reports, and their roadmap/ontology/journal mappings.

## Staging and review guardrails

1. Do not run `git add .` or stage `_WORK/codex_smoke_chronicle/` by accident.
2. Generate a path inventory for each proposed commit before staging.
3. After staging, inspect `git diff --cached --name-status` and
   `git diff --cached --summary` for unexpected deletions or missing move pairs.
4. Confirm every curated evidence directory is intentional; untracked evidence
   cannot be proven unchanged with `git diff`.
5. Run the full validation contract after each commit boundary. If the first
   commit cannot pass independently, combine the two commits rather than
   manufacturing a broken intermediate state.
6. Do not amend historical run artifacts to make paths or schemas look current.

## Current validation record

Observed locally on 2026-07-17:

```powershell
pytest -q
python tools/check_architecture_boundaries.py --root .
python tools/check_root_layout.py --root .
python tools/check_input_catalog.py --root .
python tools/docs_link_check.py
python tools/security_scan.py --root . --fail-on-findings
git diff --check
```

Results: 231 tests passed; all five repository checks passed; the security scan
reported zero findings; `git diff --check` exited successfully with line-ending
conversion notices only.

## Before committing

- Apply and test the small comparator-hardening follow-ups recorded by the
  Phase 17 review, or explicitly defer them in the Phase 17 design record.
- Re-run the commands above after the final documentation and staging changes.
- Review the complete staged diff. This document is a draft, not proof that the
  staged commit matches it.
