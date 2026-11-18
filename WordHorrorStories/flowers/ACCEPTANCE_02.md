# WHS-FLOWERS-PILOT-02 acceptance hardening

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
