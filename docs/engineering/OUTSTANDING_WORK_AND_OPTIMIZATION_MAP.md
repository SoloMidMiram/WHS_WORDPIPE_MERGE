# Outstanding Work and Optimization Map

> **Historical baseline:** August 2026 PR #2 review and third-wave remediation
> **Purpose:** Keep remaining delivery work, review closure, and refactor choices
> explicit without treating planned work as implemented.

For current delivery ordering, active issue links and activation gates, see the
[delivery plan](DELIVERY_PHASES_AND_GATES.md#backlog-activation-and-synchronization).
This map retains historical remediation and technical context. The delivery
plan's gateway IDs are distinct from the historical roadmap goals cited below.

## Evidence Labels

| Label | Meaning |
|---|---|
| **VERIFIED** | Supported by current repository inspection or an executable result. |
| **HISTORICAL** | A dated commit/report result; do not present it as a new run. |
| **LOCAL PENDING** | Present in the current worktree but not part of the published PR head. |
| **OUTSTANDING** | Required behavior or evidence is not yet present. |
| **CONDITIONAL** | Reassess only when the documented architecture trigger is met. |

## 2026-11-27 review reconciliation

Source inspection at [c0a6d1fac7dc](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/commit/c0a6d1fac7dcf9c51021e6a8c62ad462e255389a); [main CI](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/45948321058) is existing evidence, not new runtime validation. The findings below describe observed code and proposed probes, not independently reproduced end-to-end failures.

| Finding | Observed implementation / limitation | Owner and disposition |
|---|---|---|
| A | `wordpipe/chronicle/merge.py` collapses whitespace and keys on date/body hash; tests explicitly preserve whitespace normalization. Distinct indentation/title may collapse. | P1 CORE-01/G3-core queued characterization via [CORE-02 #36](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/36), no new identity algorithm or separate admission. |
| B | `steps/finalize.py` writes destination before `toc_step`; `steps/flatten.py` uses predictable working path. | P1 SAFE-01 #18 READY; preserve destination and invocation ownership. |
| C | `orchestrator.py` compatibility shim returns path/count without inspecting report errors. | DOCX-01/INT-01 queued; characterize consumers and strict failure semantics. |
| D | Ingest writes output directly; merge publishes main report and sidecar separately; wheel qualification copies checkout drivers. | P1 CLI-01 #34 admitted for characterization only. |
| E | Structural mode is opt-in and rejects certain reserved framing collisions. | P1 MD-01 #15 retained; document supported input and replay. |
| F | Scanner is extension/pattern-limited; no history/dependency/SAST or resource assurance. | P1 SEC-01 #17 retained. |

The canonical delivery plan owns status and release gates. Subjective review scores do not qualify any gateway. No broad refactor, semantic deduplication redesign or storage change is authorized.

## Historical PR #2 Review Closure

The August review tracked CI confirmation and four P2 findings as open. The
table below records their subsequent closure. The 270-test run at `777c62a`
and the 273-test local run from 2026-07-26 are historical evidence. See the
[PR #2 description](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/2)
for validation tied to the published head.

| Priority | State | Work | Completion evidence |
|---|---|---|---|
| P0 | **VERIFIED** | Confirm `7d8e114` on the three current Windows CI jobs (3.10 base, 3.11 base, 3.11 DOCX). | All three matrix jobs green on head `e59852d` (2026-08-21); run https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/32478622595. |
| P1 | **VERIFIED** | Preserve pre-existing `.work.docx` artifacts on a flatten failure. | Committed `f70b3f0` (2026-08-20) with two regression tests; review thread r3652927664 resolved. |
| P1 | **VERIFIED** | Restore `tools/verify_integrity.py --strict` as a compatibility selector while strict remains the default. | Committed `f70b3f0` (2026-08-20); review thread r3652927668 resolved. |
| P2 | **VERIFIED** | Probe the XML flattener dependency on non-Windows default wiring. | `test_make_flattener_non_windows_preflight` added; non-Windows path probes `_can_import_mergedpipeline()` before returning XmlFlattener. |
| P2 | **VERIFIED** | Preserve multi-line undated-event body text in rejection records. | `test_ingest_rejection_preserves_multiline_body` added; pending rejection accumulates continuation lines. |
| P2 | **VERIFIED** | Reject non-object input catalogs with the normal diagnostic rather than a traceback. | `test_catalog_rejects_non_object_catalog` added; `_catalog_entries` raises ValueError for non-dict. |
| P2 | **VERIFIED** | Hash DOCX catalog inputs as raw binary while retaining text normalization only for text formats. | `test_catalog_docx_hashes_raw_binary` added; DOCX hashed as raw bytes, text LF-normalized. |

## Frozen B2 routing evidence

**HISTORICAL / DEFERRED.** The [B2 investigation](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/blob/3cc86ef2e6eee7d55bbc7eac361045d4db418a1f/docs/engineering/WHS_CONTEXT_PACK_B2.md#b2-root-cause-disposition--2026-11-21)
reproduced an authorization defect in raw fallback. A verified source
and lexical overlap can return authentic but non-responsive evidence.
Suppressing raw wholesale would also remove 27 valid deliveries. Narrative
field grounding and ID-less match failures were reproduced with intact H2
units. The completed G1 result is REVISE, and recovery is deliberately
deferred under [#8](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/8).
The [delivery plan](DELIVERY_PHASES_AND_GATES.md#b3-re-entry) owns the
re-entry criteria and work-package dependencies.

## Product and Evidence Backlog

| Priority | State | Work | Source / dependency | Completion criteria |
|---|---|---|---|---|
| P0 | **HISTORICAL** | Review remote refs within the August 2026 audit inventory. | Roadmap Phase 4. | The dated map records 3 scanned remote branches and remediation on a stale branch. Evidence locator `_SECURITY/scan_reports/remote_refs_secret_audit.json`. |
| P1 | **ACTIVE** | MD-01 · Markdown structure. | [#15](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/15), slot 1. | [Opt-in implementation #23](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/23) accepted and integrated. Legacy remains the default. G2 REVISE pending intended-input coverage, framing, locator and replay qualification, and separate temporal evidence work. |
| P1 | **COMPLETE** | EXEC-01 · Bounded subprocess execution. | [#25](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/25), exit accepted. | [Implementation #27](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/27) is integrated. Slot 2 is vacant. Aggregate G5 remains pending. |
| P1 | **QUEUED** | TIME-01 · Date provenance. | Applicable MD-01 spans. | Separate assigned dates from evidenced roles and retain source locators. |
| P1 | **READY** | SAFE-01 · DOCX final publication. | [#18](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/18), READY; admission requires SEC-01 exit and a separate decision. | Test staging, save/reopen, TOC mutation and replace. Preserve destination bytes on pre-commit failures. |
| P1 | **COMPLETE** | CI-01 · Source-test import isolation and installed origins. | [#30](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/30), bounded P1 exit. | Windows and Linux qualification accepted. Slot 2 released. |
| P1 | **ADMITTED — characterization** | CLI-01 · Complete installed Chronicle flow and safe publication. | [#34](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/34), slot 2. | Reproduce clean installed flow, driver dependencies, aliases, output discovery and multi-artifact failure; propose bounded contract before implementation. |
| P1 | **ACTIVE** | SEC-01 · Public repository and supply-chain assurance. | [#17](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/17), slot 3. | Distinguish scanner coverage from reachable history, SAST and dependency advisories. Record tool scope, refs, artifacts, dependency and Actions evidence, and redacted dispositions. |
| P1 | **BLOCKED** | Genuine NCM inference and combined AI evaluation. | [#9](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/9), [#11](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/11). | Resolve the documented upstream prerequisites. Jev offline preparation under [#10](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/10) is permissible; live use requires separate authorization. |
| P1 | **VERIFIED** | Canonicalize Chronicle index logic under `wordpipe.chronicle`. | Alignment audit and index extraction tests. | Characterized via `tests/test_index_extraction.py`; pure seam extracted to `wordpipe/chronicle/index.py`; `pipeline/index.py` retained as a thin wrapper preserving CLI/import/JSON contracts. |
| P1 | **PARTIAL** | ONT-01 · Add Phase 13–17 project-level ontology instances. | Alignment audit; per-run ontology is complete but root `ontology.json` only records older P9 activity. | Define the mapping and add project instances without changing the aggregate 10-entity/7-relation model unintentionally. |
| P1 | **OUTSTANDING** | ONT-02 · Emit semantic concepts, mentions, and `derived_from` relationships. | Phase 15 design / G7. | Approve an NLP/POS evaluation gate, then add characterized extraction and provenance tests. |
| P1 | **OUTSTANDING** | CORE-01 · Build the reference stage and validate the manual merge. | Roadmap Phase 9c. | Reuse existing survivor/navigation contracts and compare automated output against the manual merge where authorized and available. |
| P1 | **VERIFIED** | Make integrity evidence portable. | Plan and alignment audit. | Relocation maps emit `src_rel`/`dst_rel`/`conflict_path_rel`; `verify_integrity.py --portable` resolves relative identities against the active workspace while retaining absolute diagnostics; `run_topic_report.py` writes repo-relative manifest identity fields. |
| P2 | **OUTSTANDING** | Map labor notes, reports, and plans into the ontology; audit remaining absolute paths. | Plan backlog. | Produce traceable model instances and an audit with zero unapproved machine-specific paths. |
| P2 | **DEFERRED** | CI-01 · Add `tools/duplicate_scan.py` and split runtime/evidence CI profiles. | Separate scope decision. | Preserve governance checks. |
| P2 | **PARTIAL** | INT-01 · Validate an external TraceLedger integration. | Roadmap G8. | `tests/test_traceledger_consumer.py` validates the internal top-level API + EventSink boundary, and the unimplemented capability-report claim was removed; an actual external TraceLedger consumer has not been validated in this repository. |
| P1 | **QUEUED** | NLP-01 · Establish a multilingual deterministic baseline and evaluate NLP/POS tooling for ontology extraction. | Roadmap G7; subject to external-access constraint C1. | Record candidate comparison, corpus, quality threshold, and go/no-go decision. |
| P3 | **DEFERRED** | REF-01 · Conditional runner decomposition and wrapper retirement. | Architecture stability gate. | Reconsider only after a third adapter exposes concrete coupling or ontology evolution makes the current serializer unsafe. |

## Refactoring and Optimization Lanes

| Lane | Candidates | Required gate |
|---|---|---|
| Low effort / high safety | Remove compatibility wrappers only after import-consumer inventory; prune an empty pipeline compatibility surface; retire obsolete AI copies/stubs only after consumer confirmation. | Record consumers and byte hashes before moving/removing files; preserve external imports or add a compatibility release path. |
| Medium effort / controlled risk | Organize tests by subsystem; assess the `process_docx_v3_simple` compatibility shim. | Characterization tests first; do not combine a package move with a feature or schema migration. |
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
