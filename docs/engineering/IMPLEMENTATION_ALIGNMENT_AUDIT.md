# Implementation-to-Roadmap Alignment Audit

> Date: 2026-08-21 (1405/05/30)<br>
> Status: Committed baseline audit (`a635ea2`) plus reliability, installability,
> architecture, and evidence-portability closeout<br>
> Scope: Main roadmap phases, root organization, canonical module boundaries,
> topic-report evidence, and known implementation debt

## Status Vocabulary

| Label | Meaning |
|-------|---------|
| **VERIFIED** | Implementation and proportionate executable evidence exist |
| **PARTIAL** | A meaningful subset exists, but the stated phase outcome is incomplete |
| **OUTSTANDING** | Planned behavior or evidence is absent |
| **SUPERSEDED** | A later implementation satisfies the intent through a different path |
| **HISTORICAL** | A dated result remains valid as history but is not a current baseline |

File existence alone is not sufficient for **VERIFIED**. The audit uses code,
tests, generated run evidence, and focused inspection.

## Phase Crosswalk

| Phase | Roadmap claim | Audit label | Current evidence / correction |
|-------|---------------|-------------|-------------------------------|
| 17 | Actual merged-survivor integrity and two-run stable event IDs | **VERIFIED, with comparator-hardening follow-ups** | `merged-note-aware-v1`, paired repeatability runs, and separately reserved STABLE comparison reports exist; stricter candidate-assurance/count validation remains a local hardening item |
| 16 | Section/commit event identity and correlation sidecars | **VERIFIED evidence contract** | Both adapters and the runner emit `event-lineage-v1` / `event-correlation-v1`; aggregate ontology emission remains unchanged |
| 15 | Provenance foundation and semantic design gate | **VERIFIED foundation; extraction OUTSTANDING** | Metrics contract, consumed-source semantics, file-level lineage, fail-closed validation, lineage-aware attribution, design doc |
| 14 | Second topic and multi-topic ontology readiness complete | **VERIFIED** | Remediation trend has 50 staged/merged/tagged events, PASS, COMPARED, 10 entity types, and 7 relation types |
| 13 | Generic topic runner, trends, attribution, ontology spine complete | **VERIFIED** | Registry, manifests, trend/source evidence, ontology output, and focused tests exist |
| 12 | Topic-neutral adapter performance loop complete | **VERIFIED** | InsuranceChatbot controlled evidence and reusable performance template exist |
| 11 | P0-P2 repository stabilization complete | **VERIFIED** | Canonical verify, fail-fast orchestration, O(n) adapter segmenter, CI, and tests exist; Chronicle index logic is canonical under `wordpipe.chronicle.index` with a compatibility wrapper |
| 10 | Documentation architecture complete | **VERIFIED after maintenance sync** | Canonical docs exist; this audit corrected later drift and added root enforcement |
| 9a/9b | Chronicle automation and index builder complete | **VERIFIED** | Ingest/merge/categorize/verify canonical logic and operator index stage execute in the controlled runs |
| 9c | Reference builder and ontology wiring complete | **PARTIAL / OUTSTANDING** | P9 activity exists in `ontology.json`, but `pipeline/reference.py`, manual-merge validation, and project-level topic-run instances do not |
| 7 | Layered WordPipe refactor complete | **VERIFIED** | `wordpipe/orchestrator.py` is a thin composition root; orchestration and adapter tests pass |
| 6 | Foundation portability and ontology building complete | **VERIFIED after path cleanup** | Governance docs and ontology exist; machine-specific command examples were corrected during this audit |
| 5 | Documentation pack complete | **VERIFIED after mapping sync** | Role-based docs exist and current Phase 14/audit/root guidance are mapped |
| 4 | Local security and pipeline contracts complete | **VERIFIED after remote-ref audit** | Local scanner passes; the 2026-08-21 remote-ref audit found third-party keys only on a stale branch, deleted that branch, and recorded verification in `_SECURITY/scan_reports/remote_refs_secret_audit.json` |
| 3 | Snapshot and evidence pipeline established | **VERIFIED by preserved artifacts** | Manifest, relocation plan/map, logs, and integrity evidence exist |

## Major Flaws and Disposition

| Finding | Disposition | Evidence |
|---------|-------------|----------|
| Topic runner combines manifest, execution, trends, attribution, verdict, and ontology concerns in one CLI | **CONDITIONAL architecture debt** | Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe |
| File-level lineage existed without section→event identity | **FIXED through Phases 16–17; semantic concepts OUTSTANDING** | Section/commit locators, stable SourceEvent/ReportEvent sidecars, actual survivor membership, and two-run repeatability are verified; SemanticConcept/mentions/derived_from emission remains deferred |
| Chronicle `index` was the only active stage not canonical under `wordpipe.chronicle` | **FIXED** | Characterization tests cover the extracted pure seam in `wordpipe/chronicle/index.py`; `pipeline/index.py` remains a thin CLI/import compatibility wrapper |
| Static project ontology does not contain Phase 13–17 topic-run instances | **PARTIAL** | Per-run ontology JSON is complete and remains aggregate 10/7, while project-level `ontology.json` only contains the older P9 activity |
| P0 external-review defects (6 findings across verify_integrity, chronicle merge, ComFlattener, TOC adapter, CLI error handling, path guard) | **FIXED in P0 reliability remediation slice** | `--strict` added to orchestration; `validate_event_headings()` pre-scan added; `ComFlattener.__init__` eager import; `Win32MergedpipelineV3TocUpdater` exception blocks removed; CLI rewritten to check `RunReport.errors`; `--in`/`--out` path guard added. 253 tests pass. See `VERIFICATION.md` and `JOURNAL.md` |
| Second-wave P0/P1 review findings (7 findings across flattener decoupling, chain abort, verify defaults, ingest provenance, categorize preamble, REVIEW verdict, API doc alignment, catalog v2) | **FIXED in second-wave slice** | `_can_import_mergedpipeline()` probe + `_UnavailableFlattener` stub; chain.ps1 aborts on `$IngestFailures -gt 0`; `verify_integrity.py` defaults to strict (`--diagnostic-only` to relax); ingest skips undated events; categorize preserves preamble; `run_topic_report.py` returns exit 2 for REVIEW verdict; TraceLedger contract doc corrected; catalog bumped to v2 with hash_mode. 257 tests pass. See `docs/engineering/SECOND_WAVE_P0P1_VALIDATION.md` |
| Third-wave P0/P1 review findings (5 findings across ingest rejection manifest, flatten preflight+abort, source coverage parser, dedup defaults, sibling heading context; CI gap) | **FIXED in third-wave slice** | `split_into_events()` returns structured rejection records; CLI `--allow-undated` flag; `build_default_deps()` preflight RuntimeError; `WordPipePipeline.run()` aborts on flatten failure; `build_source_manifest()` accepts both numbered/un-numbered formats; dedup defaults aligned to `date_title`; H2/H3 sibling transition guards removed; CI matrix expanded with DOCX extra, real DOCX CLI test, real chain.ps1 execution. 270 tests pass. |
| Evidence portability deliverables were incomplete | **FIXED** | Relocation rows emit relative identities alongside absolute diagnostics; `verify_integrity.py --portable` prefers those identities and resolves destination/conflict paths against the active workspace; regression tests cover clone-path drift |
| Roadmap outstanding table described completed Phase 14 work as future | **FIXED** | Outstanding table now lists only current work |
| Root mixed tracked report scripts and generated DOCX outputs with governance files | **FIXED** | Scripts moved to `scripts/reporting/`; reports preserved in `_ARCHIVE/evidence/generated-reports/`; root checker passes |
| Fixed month and topic labels weakened the generic Markdown adapter | **FIXED in Phase 14 remediation** | Dynamic headings, manifest-owned topic context, focused tests, and controlled evidence |

## Superseded or Incorrect Previous Flaw Claims

| Previous claim | Current truth |
|----------------|---------------|
| `wordpipe/orchestrator.py` mixes seven responsibilities | **SUPERSEDED:** it now wires dependencies and delegates to `WordPipePipeline` |
| `wordpipe/core/segment.py` contains O(n²) heading scanning | **SUPERSEDED:** it is a deprecation stub; active DOCX heading paths are precomputed in the adapter |
| `wordpipe/code_style.py` contains duplicate `style_code_blocks` definitions | **FIXED:** one definition remains |
| `wordpipe/logging_tools.py` has duplicate imports | **FIXED:** the earlier verification already marked this claim false |
| P9 ontology wiring is entirely absent | **PARTIAL, not absent:** a P9 activity instance exists, but topic-run/project ontology wiring remains incomplete |

## Minor Follow-ups

- Align the repo-root bootstrap style of `pipeline/verify_ingest.py` with the
  other wrappers when packaging assumptions permit.
- Keep historical validation counts labelled by date; the current suite count
  must come from the latest test run rather than replacing old reports.
- Remove duplicated numbering and stale “skeleton” language from the ontology
  document as the model is incrementally populated.
- Keep generated caches (`.pytest_cache`, `*.egg-info`) ignored; they are not
  curated repository content and are exempted by the root checker.
- Add `tools/duplicate_scan.py` and split runtime/evidence CI profiles if those
  historical governance deliverables remain desired; neither is implemented.

## Architecture Stability Gate

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

Those are the primary triggers. Secondary support requires either an import-boundary violation that cannot be repaired locally, a public contract that cannot evolve safely despite characterization tests, or the same defect requiring synchronized edits across production modules on two separate occasions. For the repeated-defect trigger, record the date and defect, affected production paths, first and second occurrence, why synchronized changes were required, and the tests demonstrating shared responsibility. No such repeated-defect record exists as of this slice.

The static v1 import-boundary checker guards dependency direction without claiming complete call-graph coverage. Its exception registry is a reviewed architecture-change surface, not a general suppression mechanism.

## Current Verification Contract

```powershell
python tools/check_root_layout.py --root .
python tools/check_input_catalog.py --root .
python tools/check_architecture_boundaries.py --root .
pytest -q
python tools/docs_link_check.py
python tools/security_scan.py --root . --fail-on-findings
```

The latest command results belong in `ROADMAP.md` and the relevant phase report;
historical reports retain their original dated counts.

## Latest Validation Results

Observed locally on 2026-07-25 after the second-wave P0/P1 closeout. Earlier
phase documents retain their dated counts.

| Check | Result |
|-------|--------|
| Root layout | OK |
| Input catalog | OK (v2 with hash_mode) |
| Architecture boundaries | OK; 296 static edges; 6 reviewed path roles; 0 active v1 bypasses |
| `pytest -q` | 270 passed |
| Documentation links | 37 files scanned, 34 references valid |
| Security scan | 911 files scanned, 0 findings |
| `git diff --check` | Exit 0; line-ending conversion notices only |

Evidence preservation claims use the Phase 16/17 inventories and digests in
`VERIFICATION.md` and `JOURNAL.md`; they are not inferred from Git diff.
