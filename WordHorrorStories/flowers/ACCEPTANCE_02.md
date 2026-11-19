# WHS-FLOWERS-PILOT-02 acceptance hardening

## 2026-11-19 — WHS-INTEGRATION-06 current engineering acceptance

Verified now on reconciliation commit `0a97fe643245666daa1013ed7a4cf2fea532ebbb`:
ordered parents are prior PR #7 head `2b08079` then integrated main `a2ca8a4`.
Its tree is `f6ff67370d899cd0cf9849394e4c7e317edd3872`, exactly matching the
WHS-INTEGRATION-01 tested tree. PRs #6 and #5 are merged. No production or
configuration edits were added during this reconciliation.

| Decision | Current verdict | Fresh evidence / remaining limit |
|---|---|---|
| Engineering implementation and pilot execution | PASS | Complete topic runner: prepare, chain, summarize exit 0; seven inputs, 44 candidates/staged/merged/tagged events; zero reported warnings/errors/duplicate conflicts. Observed runner time 37.24s. |
| Survivor and actual navigation acceptance | PASS | Independently matched all 44 normalized survivor identities in order, 44 explicit anchors, 44 event links and 176 theme links to unique existing targets in chronicle_tagged.md. Supersedes the dated pre-integration navigation FAIL below. |
| Source locators and lineage | PASS | All 44 file/line/heading locators verified; source identities, body hashes, candidate ordinals and dates match historical lineage; no unexplained event loss or duplicate removal. |
| Source preservation | PASS | Seven raw source hashes match inventory. Original/archive/dirty-file preservation is checked separately against the 146-file investigation inventory. |
| Configuration and metadata compatibility | PASS | Integrated survivor configuration and seven Flowers themes load; configuration, nonmapping metadata, and negative-keyword characterization regressions remain in the full suite. |
| Real Persian title coverage | UNVERIFIED | Corpus has zero Persian event titles. Persian/mixed-script coverage is from separate synthetic navigation regressions, including both renderers. |
| Complete-document recall | REVIEW | Seven preambles remain omitted. Candidate counts/byte proportions do not prove semantic recall. |
| Publication dates | REVIEW | Assigned dates retain historical derivation; publication-date semantics remain unverified. No dates rewritten. |
| Taxonomy quality | REVIEW | Manual 308-cell ground truth incomplete; precision/recall unavailable. Taxonomy implementation unchanged. |
| Contextual titles | REVIEW | Historical review: 36/44 acceptable (81.818%), eight generic titles need context; below the proposed acceptance goal. No numerical target is newly invented here. |
| Semantic duplicates / contradictions | REVIEW | Exhaustive claim-level adjudication remains incomplete; zero pipeline conflicts is not semantic proof. |
| Restricted corpus publication | REVIEW | No redistribution authorization; sources, run outputs and row-level audit remain local. |
| Local validation | PASS | Full pytest: 364 passed in 176.11s on reconciliation code; all five governance checks passed (security: 878 files, zero findings); synthetic five-stage PowerShell smoke passed. Final exact-head hosted CI is recorded separately in the PR description. |
| Engineering merge-readiness recommendation | Conditional PASS | Subject to the final documentation diff, governance/full-test results and fresh exact-head hosted CI recorded in the PR description. Keep draft; no merge authorized. |
| Semantic corpus acceptance | REVIEW | Navigation PASS does not approve publication or settle literature quality. |
| Future literature engine | Deferred | No issue #8/NCM/Jev/NLP/general extraction/ontology migration implementation. |

The fresh local run is retained under the WHS-INTEGRATION-06 evidence directory
as `topic-runs/flowers-reconciled`; navigation.local.json and lineage-audit.json
retain aggregate verification and local scripts retain the procedure. Standard
run artifacts contain restricted text and must not be uploaded. This is local
CommonMark link/anchor analysis, not a claim of live browser inspection.

## Historical WHS-FLOWERS-PILOT-02 observations (preserved)

The following failures, counts and ownership statements describe the earlier
pre-integration checkout. They remain historical evidence, not current status.

Evidence classification: observations below are verified now by local commands unless marked inferred or unverified. Source-derived row-level files remain ignored under `output/acceptance_02b/`; no redistribution approval is inferred. This is a partial acceptance report, not completed semantic acceptance.

## Reconciliation

PR #7 remained draft, base main at d9ef212135c049390a234bf33e70b1380cb8d03f, head aa742ac305ea8d93305f668a116e3b6672cc2a18 before edits. `gh pr view` and `gh api .../branches/main` verified refs. Run 44366289326 reports success at that exact head: build, test-linux, test (3.10, false), test (3.11, false), test (3.11, true). These results do not certify the follow-up commit.

PR #5 head 315cd4fb0c29a7e903d9346596e9f31ba3794c7d owns survivor/Unicode navigation and is stacked on PR #6. PR #6 head acbac03c22e406a88fbf342a8f75b333c78efbb3 owns configuration/metadata validation. Neither was changed or incorporated.

The original checkout remains on codex/chronicle-run-evidence with unrelated dirty files. The pilot linked worktree already contained two modified root-layout files at reconciliation; the reviewed implementation was retained and its Windows temporary-file test corrected.

## Acceptance matrix

| Decision | Verdict | Evidence / remaining requirement |
|---|---|---|
| Linked-worktree regression | PASS | Baseline checker invoked from HEAD returns ['.git'] in actual pilot worktree. Reciprocal admin/common/gitdir pointers checked; no allowlist expansion. Real temporary Git checkout/worktree, malformed pointer and unexpected-file tests pass. |
| Preservation | PASS | Seven original source hashes match inventory; 79 source/archive file hashes unchanged before/after audit. Local hashes_before.json and audit.py record verification. |
| Adapter candidate coverage | PASS | Independent source line inventory matches all 44 lineage records by filename, line and heading. |
| Complete-document extraction | REVIEW | Seven preambles omitted; exact UTF-8 span accounting covers every byte, extracted H2 spans represent 99.0419993653353% of bytes. Byte proportion is not semantic recall. |
| Taxonomy accuracy | REVIEW | 308-cell prediction matrix exists locally; manual ground truth remains UNREVIEWED. TP, FP, FN, precision and recall are unavailable, not zero. Zero predicted-unclassified records does not establish correct assignments. |
| Contextual title evaluation | REVIEW | All 44 unchanged-heading suggestions reviewed for contextual navigation: 36 acceptable (81.818%), eight generic headings need context. Local titles.local.json has originals, suggestions, locators, decisions and reasons. Standalone publication titles not approved. |
| Publication dates | REVIEW | All 44 assigned dates retained locally; 19 use constant 2026-07-16, remaining 25 use document/section dates. Publication dates remain unverified. Access/reference dates are not publication assertions. |
| Semantic duplicates / contradictions | REVIEW | Repeated identity/care tranches overlap; no semantic consolidation authorized. Relationships below need claim-level adjudication. |
| Actual index navigation | FAIL | 44 distinct fragment-only links in appendix/event_index.md target that appendix, which has no event headings. Inspecting local Markdown proves wrong destinations; no rendered-browser claim. Repair belongs to PR #5. |
| Synthetic reproducibility | PASS | tools/smoke_flowers.py generates original synthetic input, executes five PowerShell stages and verifies fresh run evidence and event index. No restricted corpus required. |
| Local validation | PASS | 326 pytest passed in 106.18s; five focused root tests passed. All five governance checks passed; security scan: 982 files, zero findings. |
| PR merge readiness | REVIEW | Keep draft; incomplete semantic acceptance and navigation dependency remain. |
| Real-corpus pilot acceptance | REVIEW | Not accepted for publication; manual category truth and claim/date review incomplete. |
| Future literature engine | REVIEW | Semantic NLP, generalized extraction, ontology migration and broad refactors deferred; no capability claim. |

## Date, duplicate and contradiction review

Local dates.local.json preserves section locators and assigned dates. Assigned distribution: 2026-07-16: 19; 2026-11-12: 6; 2026-11-15: 13; 2026-11-16: 6. No original dates were rewritten.

Inferred review relationships, using source inventory order and H2 ordinal: S2-4, S3-4, S4-2 and S7-1 repeat the pothos care subject; S2-3, S4-3, S6-3 and S7-2 revisit trade-name ambiguity. Shared subject is not duplicate identity. S4-1 readiness language and S3-1/S3-6 release blockers must remain scoped to their historical runs; they cannot be collapsed into current approval. S1-2 itself distinguishes shipping statements by inspected surface. S3-7 and S7-6 differ in media-rights progress and require asset-specific reconciliation. These are candidate relationships, not verified contradictions or an exhaustive semantic audit. No deduplication behavior was changed.

## Provisional taxonomy characterization

The actual matcher uses lowercased substrings. Executed probes show that plain Persian words match while Arabic yeh variants do not; inserting ZWNJ within a keyword prevents a match. The synthetic phrase `framework growth` matches the plant growth category. A marketplace substring matches market. These probes characterize mechanics, not corpus precision.

Local keyword_examples.local.json retains actual corpus contexts for manual negative-keyword selection. The existing `synthetic regression only` negatives have no demonstrated corpus value. Do not deploy broad negatives such as `research program` or `taxonomy`: sections mix research framing with genuine care/identity evidence, and whole-event negatives could suppress true positives. A defensible negative list remains unresolved pending the manual matrix. No normalization engine or taxonomy change introduced.

## Reproduce safely

Install `.[chronicle,test]`, then run `python tools/smoke_flowers.py` from a checkout. Requires PowerShell. For real sources follow README.md, source_inventory.json and topic_manifest.local.json; output directories must be absent. Derived source content stays local. Local audit data is under output/acceptance_02b: coverage.local.json, taxonomy_matrix.local.csv, titles.local.json, dates.local.json, navigation.json, unicode.json, summary.json, hashes_before.json and validation logs.
