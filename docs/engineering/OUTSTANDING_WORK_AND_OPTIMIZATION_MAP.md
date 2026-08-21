# Outstanding Work and Optimization Map

> **As of:** 2026-08-20 (1405-05-29)
> **Baseline:** PR #2 published head `f70b3f0`; third-wave remediation commit `777c62a`
> **Purpose:** Keep remaining delivery work, review closure, and refactor choices
> explicit without treating planned work as implemented.

## Evidence Labels

| Label | Meaning |
|---|---|
| **VERIFIED** | Supported by current repository inspection or an executable result. |
| **HISTORICAL** | A dated commit/report result; do not present it as a new run. |
| **LOCAL PENDING** | Present in the current worktree but not part of the published PR head. |
| **OUTSTANDING** | Required behavior or evidence is not yet present. |
| **CONDITIONAL** | Reassess only when the documented architecture trigger is met. |

`777c62a` records **270 passed** for the third-wave suite. That is
**HISTORICAL** evidence; a fresh result requires a configured Python 3.10/3.11
environment with the needed extras. Commit `7d8e114` corrects the CI raw-input
fixture; fresh matrix success is therefore **OUTSTANDING** until all jobs finish
green.

The current local worktree ran **273 passed** on 2026-07-26 (**VERIFIED**), a
result that included the two P1 review fixes. Those fixes are now committed as
`f70b3f0` (2026-08-20) and pushed to PR #2; the matching Codex review threads are
resolved. The four P2 items and the P0 CI confirmation remain **OUTSTANDING**.

## Immediate PR #2 Closure

| Priority | State | Work | Completion evidence |
|---|---|---|---|
| P0 | **VERIFIED** | Confirm `7d8e114` on the three current Windows CI jobs (3.10 base, 3.11 base, 3.11 DOCX). | All three matrix jobs green on head `e59852d` (2026-08-21); run https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/32478622595. |
| P1 | **VERIFIED** | Preserve pre-existing `.work.docx` artifacts on a flatten failure. | Committed `f70b3f0` (2026-08-20) with two regression tests; review thread r3652927664 resolved. |
| P1 | **VERIFIED** | Restore `tools/verify_integrity.py --strict` as a compatibility selector while strict remains the default. | Committed `f70b3f0` (2026-08-20); review thread r3652927668 resolved. |
| P2 | **VERIFIED** | Probe the XML flattener dependency on non-Windows default wiring. | `test_make_flattener_non_windows_preflight` added; non-Windows path probes `_can_import_mergedpipeline()` before returning XmlFlattener. |
| P2 | **VERIFIED** | Preserve multi-line undated-event body text in rejection records. | `test_ingest_rejection_preserves_multiline_body` added; pending rejection accumulates continuation lines. |
| P2 | **VERIFIED** | Reject non-object input catalogs with the normal diagnostic rather than a traceback. | `test_catalog_rejects_non_object_catalog` added; `_catalog_entries` raises ValueError for non-dict. |
| P2 | **VERIFIED** | Hash DOCX catalog inputs as raw binary while retaining text normalization only for text formats. | `test_catalog_docx_hashes_raw_binary` added; DOCX hashed as raw bytes, text LF-normalized. |

## Product and Evidence Backlog

| Priority | State | Work | Source / dependency | Completion criteria |
|---|---|---|---|---|
| P0 | **VERIFIED** | Audit all remote branches and tags for leaked keys. | Roadmap Phase 4; local `security_scan.py` is worktree-only. | Scanned 3 remote branches 2026-08-21; third-party keys on stale `codex/evaluate-repo-review-for-workspace` branch deleted; evidence `_SECURITY/scan_reports/remote_refs_secret_audit.json`. |
| P1 | **VERIFIED** | Canonicalize Chronicle index logic under `wordpipe.chronicle`. | Alignment audit; `pipeline/index.py` is the only active stage outside the canonical package. | Characterized via `tests/test_index_extraction.py`; pure seam extracted to `wordpipe/chronicle/index.py`; `pipeline/index.py` retained as a thin wrapper preserving CLI/import/JSON contracts. |
| P1 | **PARTIAL** | Add Phase 13–17 project-level ontology instances. | Alignment audit; per-run ontology is complete but root `ontology.json` only records older P9 activity. | Define the mapping and add project instances without changing the aggregate 10-entity/7-relation model unintentionally. |
| P1 | **OUTSTANDING** | Emit semantic concepts, mentions, and `derived_from` relationships. | Phase 15 design / G7. | Approve an NLP/POS evaluation gate, then add characterized extraction and provenance tests. |
| P1 | **OUTSTANDING** | Build the reference stage and validate the manual merge. | Roadmap Phase 9c. | Implement `pipeline/reference.py` and compare automated output against `ChatGPT_Incidents_Merged.md`. |
| P1 | **VERIFIED** | Make integrity evidence portable. | Plan and alignment audit. | Relocation maps emit `src_rel`/`dst_rel`/`conflict_path_rel`; `verify_integrity.py --portable` resolves relative identities against the active workspace while retaining absolute diagnostics; `run_topic_report.py` writes repo-relative manifest identity fields. |
| P2 | **OUTSTANDING** | Map labor notes, reports, and plans into the ontology; audit remaining absolute paths. | Plan backlog. | Produce traceable model instances and an audit with zero unapproved machine-specific paths. |
| P2 | **OUTSTANDING** | Add `tools/duplicate_scan.py` and split runtime/evidence CI profiles. | Plan backlog and alignment audit. | Give each tool/profile a documented contract, focused tests, and no lost governance checks. |
| P2 | **PARTIAL** | Validate an external TraceLedger integration. | Roadmap G8. | `tests/test_traceledger_consumer.py` validates the internal top-level API + EventSink boundary, and the unimplemented capability-report claim was removed; an actual external TraceLedger consumer has not been validated in this repository. |
| P3 | **OUTSTANDING** | Evaluate NLP/POS tooling for project-text ontology extraction. | Roadmap G7; subject to external-access constraint C1. | Record candidate comparison, corpus, quality threshold, and go/no-go decision. |
| P3 | **CONDITIONAL** | Decompose the topic-report runner. | Architecture stability gate. | Reconsider only after a third adapter exposes concrete coupling or ontology evolution makes the current serializer unsafe. |

## Refactoring and Optimization Lanes

| Lane | Candidates | Required gate |
|---|---|---|
| Low effort / high safety | Remove compatibility wrappers only after import-consumer inventory; prune an empty pipeline compatibility surface; retire obsolete AI copies/stubs only after consumer confirmation. | Record consumers and byte hashes before moving/removing files; preserve external imports or add a compatibility release path. |
| Medium effort / controlled risk | Canonicalize index logic; organize tests by subsystem; assess the `process_docx_v3_simple` compatibility shim. | Characterization tests first; do not combine a package move with a feature or schema migration. |
| High value / measured | Split CI runtime/evidence profiles; profile Chronicle ingest→merge on large inputs; determine whether COM/XML flatteners are both live implementations. | Establish current timing/coverage baseline, make one measured change, and preserve current CLI behavior. |
| Conditional architecture | Topic-runner decomposition. | Follow the explicit third-adapter/unsafe-schema trigger above; extract at most one pure seam and stop to reassess. |

## Operating Rules

- `ARCHITECTURE_AND_MODULES.md` remains the dependency-rule source; run
  `python tools/check_architecture_boundaries.py --root .` after production
  import changes.
- Do not mix a feature, schema migration, and package/filesystem move in one
  implementation slice.
- Treat generated evidence as append-only: reserve a new run directory and
  retain hashes/inventories before any material move.
- Update this map when an item changes state, but keep dated validation counts
  in their historical reports rather than rewriting them as current evidence.
