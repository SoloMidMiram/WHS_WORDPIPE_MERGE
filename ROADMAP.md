# 🗺️ Project Roadmap

> **Date (Gregorian):** 2026-07-09
> **Date (Shamsi/Jalali):** 1405-04-18
> **Last Updated:** 2026-11-26
> Dated entries identify their reviewed branch and PR.

## Current delivery roadmap

The [delivery phases and acceptance gates](docs/engineering/DELIVERY_PHASES_AND_GATES.md)
own the [gateway matrix](docs/engineering/DELIVERY_PHASES_AND_GATES.md#acceptance-gateway-matrix),
[24-package issue map](docs/engineering/DELIVERY_PHASES_AND_GATES.md#backlog-activation-and-synchronization)
and [proposed release milestones](docs/engineering/DELIVERY_PHASES_AND_GATES.md#proposed-release-boundaries).
The deterministic Chronicle and context-export target, v0.2, requires
G0, G1, G2, G3-core, G4-core and G5. Full semantic Flowers evaluation and ontology expansion belong to v0.3. WordPipe DOCX has its own readiness decision. Optional
AI qualification belongs to the v0.5 target. Delivery gateway IDs are scoped
to the matrix. The historical goals and phases below retain their identifiers.

The [three-slot queue](docs/engineering/DELIVERY_PHASES_AND_GATES.md#active-execution-queue)
covers admitted MD-01 (#15) in slot 1 after G0 ACCEPT and #14 closure, a vacant slot 2 after [PR #20](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/20) integrated the B3 deferral, and SEC-01 (#17) in slot 3. SAFE-01 is READY; admission requires documented SEC-01 exit and a separate maintainer decision. No successor was admitted to slot 2. READY does not mean admitted. At most three packages can execute.

| Order | Phase | Current execution |
|---|---|---|
| 1 | Context fidelity | **REVISE** [#8](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/8) / [draft #13](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/13). Frozen B2 failed qualification and G1 remains a mandatory v0.2 blocker. B3 is **DEFERRED** pending the [re-entry evidence](docs/engineering/DELIVERY_PHASES_AND_GATES.md#b3-re-entry). |
| 2 | Document understanding | [Markdown structure #15](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/15) is admitted in slot 1. Characterize structure, source spans and replay. TIME-01 and NLP-01 remain queued. |
| 3 | Corpus acceptance | [Flowers #16](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/16) is queued for G3-full. G3-core synthetic evidence remains a distinct v0.2 gate. |
| 4 | References and ontology | Complete Phase 9c using existing survivor contracts and populate the project ontology before schema expansion. |
| 5 | Product stabilization | [Public audit #17](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/17) occupies slot 3 for release assurance. [Atomic DOCX #18](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/18) is READY for separate DOCX qualification. CLI-01 and CI-01 remain queued v0.2 work. |
| 6 | Knowledge intelligence | Ground citations, claims and relations in provenance. Measure search needs before indexing. |
| 7 | Optional AI research | [NCM #9](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/9) is blocked for real inference. [Jev #10](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/10) has offline preparation available. [Combined benchmark #11](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/11) is blocked on upstream evidence. |

## Active narrative roadmap — newest first

### 2026-11-26 — MD-01 malformed timestamp review fix

Branch `codex/md-01-structural-markdown`,
[PR #23](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/23).
Reviewed head `d55641dbc6783f463bcd1dd416304cb07aa29d3c` and base
`0a6385cbc50ef394a06c3b38129682acd795cf76`.
The [invalid timestamp finding](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/23#discussion_r4709095230)
reproduced with PyYAML 6.0.3. Handling its constructor error exposed a
second failure when the same invalid date reached the staging renderer.
Structural preparation now records malformed frontmatter and uses the
first valid section or file date before the existing default. The
repository map was checked. Local checks passed 32 focused tests, the
separate source-pinned paired replay, and all five governance checks.
Next is exact-head CI and review-thread verification before the
maintainer's merge decision. G2 remains REVISE and #15 stays open in slot 1.

### 2026-11-26 — MD-01 topic runner preflight review fix

Branch `codex/md-01-structural-markdown`,
[PR #23](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/23).
Reviewed head `722f3c175b01ae7d5940b2257ba27ea1931be86d` and base
`0a6385cbc50ef394a06c3b38129682acd795cf76`.
The [runner finding](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/23#discussion_r4708010182)
reproduced under `python -S`. The runner now imports Markdown contract names
from a dependency-free module and defers parser provenance validation until
execution. The new subprocess test covers help and dry-run planning for
both modes with site packages disabled. Local checks passed 97 focused
tests with the source-pinned paired replay passing separately. All five
governance checks passed. The repository map includes the contract module.
Recheck exact-head CI before resolving the finding. The next decision is
merge authorization. G2 remains REVISE and #15 stays open in slot 1.

### 2026-11-26 — MD-01 standalone legacy adapter review fix

Branch `codex/md-01-structural-markdown`,
[PR #23](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/23).
Reviewed head `8522e14ea1538ac5cc9965f5b352164710001e44` and base
`0a6385cbc50ef394a06c3b38129682acd795cf76`. The
[standalone adapter finding](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/23#discussion_r4707855582)
reproduced under `python -S`. Keep Chronicle imports behind structural
preparation. The new standalone test covers help, implicit and explicit
legacy preparation, and summarize with site packages disabled.
Local focused tests reported 30 passes and one deselection for the paired
replay, which hosted CI exercises. All five governance checks passed.
The repository map was checked. The next decision is merge authorization
after exact-head CI and review-thread verification. G2 remains REVISE and
issue #15 stays open in slot 1.

### 2026-11-26 — MD-01 parser provenance correction and acceptance

Branch `codex/md-01-structural-markdown`,
[PR #23](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/23).
Base `0a6385cbc50ef394a06c3b38129682acd795cf76`. The maintainer accepted the
bounded opt-in implementation at `1b700d7a82d9b5e0ee350185421fbb10e2950a82`
subject to parser provenance and final verification. At that original head,
103 focused cases passed, the paired case ran separately, and all five
[hosted jobs](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/45803359319)
passed. The original unpinned Windows run reported 385 passed, 5 failed and
6 skipped. The four pre-existing foreign imports and the paired test's
legacy-leg import failure remain CI-01 evidence.

Reviewed correction `fbcc39603991b4db1ee1d8803843b6da5cccd56c` adds the
actual Markdown parser provenance to the versioned structural sidecars.
Windows Python 3.11 focused checks passed 104 tests with the paired case
run separately. The Windows source suite with the repository explicitly
pinned in `PYTHONPATH` passed 391 tests with 6 skipped, including repeated
paired source replay. Fresh Windows wheel environments passed paired replay
on markdown-it-py 3.0.0, 4.2.0 and 4.3.0. All 22 compared evidence groups
matched after removing the producer provenance fields. The frozen fixture
and legacy identity ledger were verified by hash. The repository map was
checked. Recheck exact-head hosted evidence after this documentation commit.
The maintainer's merge decision is the next boundary. G2 remains REVISE,
#15 stays open in slot 1, and legacy remains the default.

### 2026-11-26 — MD-01 bounded implementation review

Branch `codex/md-01-structural-markdown`,
[draft implementation PR #23](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/23).
The maintainer accepted the compatibility contract at
`2e5c5e363fcdbe001ccdd58fe5d22690fb287d7c` and authorized implementation
under #15 in slot 1. PR #22 integrated through main
`0a6385cbc50ef394a06c3b38129682acd795cf76`, with all five
[hosted jobs](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/45796776892)
passing. The [delivery plan](docs/engineering/DELIVERY_PHASES_AND_GATES.md)
links mode selection, run isolation and paired comparison. The repository
map includes the new verification commands. Original characterization and
foreign import failures remain baseline and CI-01 evidence. Exact implementation
checks and the implementation acceptance decision are separate from the
accepted contract. G0 remains ACCEPT, G1 continues to block v0.2, and G2
remains REVISE. Slot 2 remains vacant pending EXEC-01 admission. SEC-01 retains
slot 3 and SAFE-01 remains READY.

Reviewed implementation parent `2d8e4566da07b7e8aa2cd371ba4c29c6f1c8c48d`.
Local focused checks passed 102 tests with the paired case run separately.
Windows installed-wheel replay passed with four legacy events, two structural
events and two removed fenced headings. The [initial hosted run](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/45800928923)
passed its Windows jobs and failed one Linux test that expected the Windows
launcher name in Linux diagnostics. This iteration corrects that assertion,
exposes the approved heading-level configuration, and verifies the comparison
CLI's exclusive output. The earlier unpinned Windows run preserved foreign
imports in CI-01 evidence and also caught an intermediate wheel build
artifact. Subsequent qualification builds in a separate temporary source tree.

### 2026-11-26 — MD-01 parser and identity contract review

Branch `codex/whs-reliability-handoff`, [draft PR #22](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/22).
Reviewed parent `19fb36863dc9ae184347c385243d552997b15428` and base
`fd2d60f72a47fbccc60e64f72c811d106c01a30e`. Issue #15 records maintainer
ACCEPT for characterization and REVISE for G2. The delivery plan adds
the opt-in compatibility contract for separate approval. The repository
map was checked. The frozen fixture and local evidence inventory were
verified by hash. Prior Windows source results and the unpinned
foreign-checkout failures remain recorded as characterization and CI-01
evidence, respectively. The parent's [hosted PR CI](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/45794447798)
passed. G0 remains ACCEPT and G1 blocks v0.2. MD-01
retains slot 1, slot 2 is vacant pending separate EXEC-01 admission,
and SEC-01 retains slot 3 with SAFE-01 READY. The next decision is
maintainer approval of the proposed parser and identity contract.

### 2026-11-26 — Engineering reliability handoff

Branch `codex/whs-reliability-handoff`, no PR. Reviewed main and production
baseline `fd2d60f72a47fbccc60e64f72c811d106c01a30e` with five successful
[hosted CI jobs](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/45786355631).
The [delivery plan](docs/engineering/DELIVERY_PHASES_AND_GATES.md) records
MD-01 synthetic characterization and an opt-in correction proposal, an
EXEC-01 admission proposal and the SAFE-01 transaction plan. The repository
map includes the fixture and evidence route. The draft B2 PR #13 remains open.
On Windows, source-pinned checks passed 115 focused tests and 383 full-suite
tests with 6 skips. The unpinned full suite had 4 index/chain failures,
379 passes and 6 skips. Keep that import-origin failure in CI-01's scope.
Next decision is maintainer review of the MD-01 correction and identity
compatibility policy in slot 1. EXEC-01 requires explicit admission to the
vacant slot 2. SEC-01 retains slot 3 pending its documented exit and a
separate SAFE-01 admission decision.

### 2026-11-22 — Delivery and topic documentation synchronization

Branch `codex/whs-roadmap-topic-sync`, [draft PR #21](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/21).
Reviewed main `c78c6e90d96ee8e9f07e08b14e74de1bd657de93` integrates PR #20.
[Main CI](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/44922552991) passed at that SHA.
PR #19 is merged and #14 closed. [Draft PR #13](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/13) at
`32387d67b76aad99baa462cf1cc7c3172901681d` retains the frozen B2 negative
experiment. Slot 2 is vacant. MD-01 and SEC-01 retain slots 1 and 3.
The November 21 requirements in [#8](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/8), [#15](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/15), [#16](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/16), [#17](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/17), [#18](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/18)
inform the delivery and backlog updates. The repository map points to the
pinned research and topic evidence. The documentation sync revises active
summaries and leaves historical results in place. Package metadata remains
0.1.0 and the v0.2 and v0.3 gate contracts are unchanged. Next decision:
maintainer review of the documentation-only draft and its exact-head checks.


### 2026-11-21 — B2 REVISE accepted and B3 deferred

Branch `codex/whs-g1-defer-governance`, documentation PR number pending
at preparation, based on
`e85ddc1b04227d9d28c2861733016570612239cc`. The reviewed evidence parent
is `d80560e4846a42545378d66a26a537e3370af80e` on draft PR #13. The
[frozen B2 investigation](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/blob/3cc86ef2e6eee7d55bbc7eac361045d4db418a1f/docs/engineering/WHS_CONTEXT_PACK_B2.md#b2-root-cause-disposition--2026-11-21) and ten synthetic characterization
probes are published at evidence head `3cc86ef2e6eee7d55bbc7eac361045d4db418a1f`.
The first run remains G1 REVISE at 28/30 valid deliveries, 9/20 correct
refusals, 1/10 absent-field refusals and 0% median GPT-2 savings. The evidence
update preserves all 50 reconciled decisions, 88 verified envelopes and
176 private files with unchanged hashes. Local evidence validation passed
413 tests, with six skipped and four expected failures, and passed the
PowerShell chain integration. Both worktrees passed the five governance
checks listed in the retrieval map.

The maintainer deliberately deferred B3. Governance integration releases
slot 2 without admitting a successor. MD-01 and SEC-01 retain slots 1
and 3. Issue #8 stays open and PR #13 stays draft. The retrieval map now
links the published evidence. Re-entry requires a bounded proposal with
responsiveness, narrative and ID-less grounding, and compact-delivery
evidence. G1 thresholds remain in force. The next acceptance decision is
maintainer review of this documentation PR.


### 2026-11-20 — G0 ACCEPT and execution handoff

The maintainer approved the existing numerical planning baselines, without
claiming research or release qualification. GitHub already merged [PR #19](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/19)
with history preserved at `d26e6e998123806e53aa352ea4f40a5a6363e1b5` from
reviewed head `18f24fa51d4517a793fab2568de2123e8ef55d98`; all five
[exact-head CI jobs](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/44688406407)
passed. [GOV-01 #14](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/14)
is closed. MD-01 is admitted in slot 1; B2 and SEC-01 retain slots 2 and 3.
The post-merge [delivery contract](docs/engineering/DELIVERY_PHASES_AND_GATES.md)
records CI-01's mandatory source-test import-origin assertion and foreign-checkout
regression, distinct installed-wheel origin checks, and a mandatory first-measurement
re-baseline review retaining historical thresholds and verdicts. The original
values are unchanged, and no post-holdout threshold change can certify old evidence.
CI-01 remains queued; no implementation or new issue was opened. Reconcile PR #13
with the integrated main during B2, preserving both roadmap and retrieval-map
histories. No other work package is admitted by this handoff.

### 2026-11-20 — G0 acceptance review and contract alignment

Branch `docs/whs-delivery-roadmap`, [draft PR #19](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/19).
Reviewed head `fd2851d2bf1aa2c6dae4171172eaef5eab9ab96d` and base
`e2f1c17643b05016f5617a43c07f850033c6acbd`. GitHub confirms the head is
five commits ahead of the base and changes four Markdown files. Verified
24 unique packages, links to nine open issues, 15 future activation contracts
and eight gateways. The [retrieval map](docs/engineering/REPO_MAP.md) was
checked against this scope.

[Hosted run 44684189554](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/44684189554)
passed all five jobs on the reviewed head. Local validation reconstructed
the candidate over the pinned base using the four GitHub blob IDs. All five
governance checks passed. With the review checkout first on Python's import
path, the local suite passed 383 tests with six skips, and the Windows
PowerShell CI integration passed its success and rejection cases. The first
local attempt loaded Chronicle code from a different checkout and failed
four tests. The corrected run applies to the review checkout.

This revision aligns slot admission, protected-label qualification, G7 cost
scope and SQLite activation. Existing numerical thresholds remain proposed.
Recheck hosted CI at the new head and record the maintainer's decision on
the proposed thresholds before accepting G0. Admit MD-01 after documented
slot release and reconcile PR #13 against the integrated base.

### 2026-11-20 — G0 corrective planning contract

Draft PR #19 remains the sole governance implementation for issue #14.
The canonical delivery plan now explicitly maps seven phases to G1–G7,
with G0 cross-cutting, nine existing issues and 15 future activation contracts.
The revised plan defines scoped G3/G4, numerical fidelity, annotation,
liveness, performance and AI thresholds (proposed pending owner approval),
platform qualification via CI-01/CLI-01, owners, queue admission, cadence and
risks. Existing Windows and Ubuntu jobs are baseline evidence, not fresh
release-candidate qualification. All planning statuses remain provisional
until G0 acceptance. No additional issue or PR is needed. Fresh validation
and independent acceptance remain pending for the corrective head.

### 2026-11-20 — Work packages, gateways and release milestones

Branch `docs/whs-delivery-roadmap`, [draft PR #19](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/19).
Reviewed parent `e0db93ea0cdefa6d5762b6abffcc63621ca0ee0d`, base
`e2f1c17643b05016f5617a43c07f850033c6acbd`. The four Markdown paths now
define 24 unique work packages, nine existing issue mappings, seven delivery
phases, eight gateways and five proposed release milestones. The issue map
assigns activation criteria to the 15 packages awaiting an issue. The
three-slot queue carries governance, B2 and the release audit, with atomic
DOCX publication next in the hardening slot. The retrieval map routes each
new section. The historical phase and evidence entries are preserved.

Local validation found 368 passing tests and 21 platform skips. All five
governance checks passed. The issue inventory was verified against GitHub.
The next decision is G0 acceptance after the issue links and hosted checks
are verified against the published candidate. B2 and Flowers semantic
evaluation still require their own evidence. The deterministic v0.2
release uses G0–G5 with core G4.

### 2026-11-20 — Delivery phase and issue reconciliation

Branch `docs/whs-delivery-roadmap`, based on reviewed main
`e2f1c17643b05016f5617a43c07f850033c6acbd`. The synchronization
work is tracked in [#14](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/14).
The PR number was pending at preparation. The plan, root roadmap, optimization
map and retrieval map are the documentation scope.

GitHub verified seven merged PRs at the starting baseline and five successful
[main CI jobs](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/44562536617).
PR #7 delivered Flowers engineering work. Semantic acceptance remains REVIEW.
PR #12 delivered the NCM research harness and pilot record. Genuine inference
remains BLOCKED. PR #13's passing hosted engineering checks coexist with its
REVISE research verdict. Its B1 benchmark evidence belongs to its draft head.

Keep the dated narrative below for historical decisions. The current public
audit is distinct from the recorded 2026-08-21 ref scan. Use the updated
[retrieval map](docs/engineering/REPO_MAP.md) for workstream evidence. Next
decision is acceptance of the documentation update, with checks recorded at
its published head, followed by the B2 revision and independent bounded work.

### 2026-11-19 — WHS-INTEGRATION-09 PR #12 research reconciliation

Branch `experiment/whs-ncm-flowers-pilot`, [PR #12](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/12).
Reviewed parent `b7f162745c4c6f2b01352dcd71764c594666768f` on main
`87c69d3e89a189ce7a2be89562f748b1e0637540`. The conflict-free merge
`db06e5e58ffd3102e21b4caaf96062c1bcb34c8e` preserved the experimental history.
The correction at `7f84522` bounded POSIX worker stdout and returned the raw
packet for malformed Unicode. The reviewed parent changes only the parser
regression input. Python 3.14.4 accepted the former, valid nested array.
The replacement uses invalid JSON and the focused tests passed on POSIX
Python 3.11.15 and 3.14.4 (24 passed and one platform skip each).

The [pilot report](docs/engineering/NCM_FLOWERS_PILOT.md) records the prior
383-test Windows result, governance checks, and synthetic replay. The frozen
WHS #8 baseline B0 retained 16/23 critical and 18/33 total facts, with a
21.40% median estimated GPT-2 reduction versus raw. The oracle-assisted result
remains historical and the fixture and metric files are preserved.

The [repository map](docs/engineering/REPO_MAP.md) now routes the harness,
focused tests, fixtures and evidence. Genuine inference remains BLOCKED.
Flowers quality and incremental NCM reduction remain UNMEASURED, and adoption
remains DEFER. The optional worker is limited to trusted POSIX synthetic tests.
Next decision is research-only acceptance after the final documentation
head's hosted CI and explicit owner approval.

### 2026-11-19 — WHS-INTEGRATION-06 hosted CI execution blocker

After normal push at head 96727b9, PR workflow 44468789637 and push workflow
44468784712 failed/cancelled before executing any steps. GitHub annotations
report failed account payments or a spending limit requiring increase. No code
regression was observed by those jobs because they never started. Local tests
and navigation remain PASS, but engineering merge readiness is BLOCKED pending
restored Actions capacity and fresh final-head CI. Owner billing action is
required; no account changes or speculative job retries were attempted. Record
this documentation follow-up's actual hosted results in the PR description.
Semantic corpus acceptance remains REVIEW; keep PR7 draft and do not merge.

### 2026-11-19 — WHS-INTEGRATION-06 PR #7 engineering reconciliation

Owner authorized normal main-into-PR7 reconciliation and safe status updates,
not merging PR7. Reviewed refs: main a2ca8a4, PR7 2b08079. PRs #6/#5 are merged
and main CI 44467106766 passed all five jobs. GitHub reported PR7 mergeable but
its baseRefOid still showed the historical d9ef212; live main-ref verification
and the conflict-free local preview established the current base contents.

Clean detached reconciliation commit 0a97fe643245666daa1013ed7a4cf2fea532ebbb has
ordered parents 2b08079 then a2ca8a4. Its tree exactly equals prior tested tree
f6ff67370d899cd0cf9849394e4c7e317edd3872. The fresh seven-source topic run passed
prepare/chain/summarize in 37.24 seconds, preserving 44 survivors, explicit
anchors and valid source locators/lineage, 44 event links and 176 theme links.
The repository map was checked and index/config ownership updated for merged
main. No implementation or taxonomy changes were added. Full pytest passed 364 tests in 176.11 seconds. All five governance checks
passed (security: 878 files, zero findings), as did the synthetic five-stage
PowerShell smoke. All 146 inventoried original files and the detached experiment
remain unchanged. Final exact-head CI is reported in the PR description after
the documentation commit.

Engineering navigation PASS supersedes the historical navigation failure;
semantic corpus acceptance remains REVIEW. Seven preambles, unverified date
semantics, incomplete manual category truth, contextual title acceptability,
semantic duplicate/contradiction review and restricted publication rights stay
open. Persian title navigation is synthetic evidence, not real-corpus coverage.
Keep PR7 draft. No issue #8, NCM, Jev, semantic engine or schema migration work.


This section is the reverse roadmap: put the latest plans and changes first.
Dates identify when a plan or result was recorded; proposed targets are not
delivery promises. Keep older evidence attached to its original revision.
The phase catalogue below remains historical planning context, not live PR status.

### 2026-11-18 — Next acceptance decisions (planned; no merge authorized)

The next Flowers decision is whether independently reviewed category labels and
claim-level date/duplicate evidence support corpus acceptance. Complete those
reviews on the Flowers branch before claiming precision/recall or publication
readiness. Keep configuration validation with PR #6 and survivor navigation with
PR #5, reconciling their current heads before taking dependencies. Semantic NLP,
general literature extraction and ontology migrations remain separate future
slices; no delivery date or implementation commitment is assigned here.

For the next merge-readiness iteration on any branch, first refresh local and
remote revision identity, then prepend a dated narrative with branch/PR, reviewed
head/base, bounded change, actual checks, map review, remaining uncertainty and
next decision. A documentation commit changes the head: verify its CI afterward
rather than attaching its parent's passing run. Use the
[retrieval map](docs/engineering/REPO_MAP.md) and the repository-local
`whs-context-loop` skill to avoid rebuilding context from whole archives.

### 2026-11-18 — Commit context workflow into PR #7 (integration iteration)

The user authorized expanding draft PR #7 to include the context workflow.
Changes were prepared on `codex/context-loop-20261118` from reviewed parent
`364d7fdd14203439e8518209e4e2d8210a319ddc` and will be applied to
`pilot/flowers-seven-md-20261118`, whose last verified head was `39a730a`.
PR #7 was reverified as draft at `39a730a`, base main, before integration.
The integrated reviewed head is `6518018041f2d9f205cd6bdc8a7650827c79d09a`;
last fetched main is `d9ef212`, with refresh initially failing on DNS. This adds rules, a
repository-local skill, bounded Git retrieval, the map and reverse roadmap;
it does not change Flowers extraction, taxonomy, or PR #5/#6 implementations.

The [local organization review](docs/engineering/LOCAL_ORGANIZATION_REVIEW_20261118.md)
accounts for all 54 preexisting/new untracked files, retains a private hash
inventory, and keeps restricted inputs, scratch scripts, generated artifacts and
the editor plan out of the commit. The apparent engineering README modification
has the same normalized Git blob as HEAD. The map was rechecked; two retrieval
tests passed in the original checkout. On integrated head `6518018`, full pytest
recorded 328 passed in 76.46 seconds; all five governance checks passed (security:
1000 files, zero findings), skill validation passed, and the five-stage PowerShell
synthetic smoke passed. All 79 source/archive hashes remain unchanged. Separately,
all 50 unrelated untracked files in the original checkout retain their inventoried
byte hashes. This documentation follow-up changes the head; verify new exact-head
CI after pushing. Historical acceptance limits remain in force; do not merge.

### 2026-11-18 — Reusable context workflow (implemented locally; validation below)

Branch `codex/chronicle-run-evidence`, reviewed head
`364d7fdd14203439e8518209e4e2d8210a319ddc`. `gh pr list --head
codex/chronicle-run-evidence --state all` verified that this branch's PR #4 is
already MERGED against `main`; this documentation/tooling iteration is uncommitted
and has no new PR. The remote main SHA has not been refreshed in this iteration.
Unrelated dirty documentation, scripts and local corpus inputs are preserved.

The goal is cheaper, more reliable context retrieval without weakening evidence
or acceptance rules. `tools/repo_context.py` now exposes a local Git snapshot and
bounded literal keyword grep. The new skill routes decisions to existing tools;
`docs/engineering/REPO_MAP.md` maps code, tests, manifests and their limits. The
map was checked against local files and Git grep references. This adds no model
or network dependency and makes no measured token-saving claim. Two focused
retrieval tests passed; skill frontmatter validation passed. Root-layout,
architecture and documentation-link checks passed; the security scan inspected
943 files with zero findings. Input-catalog validation failed on eight existing
unregistered local Flowers files; these were present in the initial dirty
inventory and were preserved. The focused suite including catalog checks
recorded 22 passed and one failure on that same catalog condition; the retrieval,
root-layout and architecture subset recorded 13 passed. `git diff --check`
passed. No full pytest or new exact-head CI was run for this uncommitted
iteration. Merge readiness still requires a dedicated reviewed branch/PR and
exact-head checks; none is created by this workflow.

### 2026-11-18 — Flowers acceptance hardening (reported prior workstream)

The preceding handoff reports draft PR #7 on
`pilot/flowers-seven-md-20261118` at
`39a730a2149fcf62c29b78c2af3d9248d5d75673`, based on main, with all five jobs
passing in runs `44372900369` and `44372911640`. These are historical reported
results, not reverified remote status in this iteration, and the Flowers files
are not present on this checkout. The reported narrow fix validates linked
worktree Git pointers; it does not broaden root governance.

The reported audit accounts for 44 H2 sections and seven omitted preambles.
Taxonomy ground truth and exhaustive semantic review remain incomplete; the
reported 36/44 contextual title acceptance is not publication approval. Reported
navigation failures remain owned by PR #5. Preserve source rights and keep merge
readiness, corpus acceptance and future engine capabilities separate. Recheck
`WordHorrorStories/flowers/ACCEPTANCE_02.md` on that branch before using its facts.

## Earlier phase catalogue and dated stabilization evidence

Current stabilization status:
- Chronicle dependency ownership is declared through the `chronicle` extra.
- Chronicle ingest/merge/categorize/verify logic is canonical under `wordpipe/chronicle/`.
- `pipeline/` and `tools/pipeline-chronicle/` are compatibility/operator CLI surfaces, not runtime import surfaces.
- WordPipe orchestration is step-based; read/style failures are fatal.
- `wordpipe/chronicle/index.py` is canonical. `pipeline/index.py` is the compatibility wrapper.
- Historical P0–P2 remediation baseline: **105 tests passed** on 2026-07-09;
  see [`docs/engineering/P0_P2_VALIDATION_REPORT.md`](docs/engineering/P0_P2_VALIDATION_REPORT.md).
- Current validation results are recorded by dated activity in `JOURNAL.md` and
  `VERIFICATION.md`; transient test/file counts are not architecture claims.
- Generic topic-runner workflow validated on InsuranceChatbot: 3 Markdown
  inputs, 200 staged/merged events, 194 events with theme tags, 0
  warnings/errors, trend comparison, source attribution, and ontology evidence.
  Evidence: [`WordHorrorStories/insurancechatbot/output/phase13_trend_validation/RUN_SUMMARY.md`](WordHorrorStories/insurancechatbot/output/phase13_trend_validation/RUN_SUMMARY.md).
- Phase 14 genericity remediation is validated on the second topic; root layout
  is enforced by `tools/check_root_layout.py`. See the
  [implementation alignment audit](docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md).
- **2026-07-25: Third-wave P0/P1 remediation complete.** All 5 additional findings
  (ingest rejection manifest with provenance, flatten preflight + abort-on-failure,
  source coverage wildcard parser, dedup defaults aligned end-to-end, sibling
  heading context in both implementations) are fixed. CI includes DOCX extra,
  real DOCX CLI test, and real chain.ps1 execution. The dated third-wave run
  recorded 270 passing tests. Follow-up `7d8e114` corrects the `chain.ps1` CI
  fixture to use raw input; the three-job CI revalidation remains a release gate.
- **2026-07-25: Second-wave P0/P1 remediation complete.** All 7 additional findings
  (flattener fallback decoupling, chain.ps1 abort-on-failure, verify_integrity
  fail-closed default, provenance defects, REVIEW verdict enforcement, API doc
  alignment, catalog v2 schema) are fixed. See
  [`docs/engineering/SECOND_WAVE_P0P1_VALIDATION.md`](docs/engineering/SECOND_WAVE_P0P1_VALIDATION.md)
  for results.
- **2026-07-24: P0 reliability remediation complete.** All 6 verified P0 defects
  (verify-integrity strict mode, malformed event heading validation, ComFlattener
  eager fail, TOC adapter explicit failure, CLI error propagation,
  `--in`/`--out` path guard) are fixed. See
  [`VERIFICATION.md`](VERIFICATION.md) for results.

---

## 🔭 Vision

Transform this workspace into a **maintainable, evidence-backed, ontology-grounded project** where:
- **`tools/`** evidence pipeline is reliable, portable, and independently runnable
- **`wordpipe/`** is a clean, import-safe library for TraceLedger integration
- **`pipeline/`** chronicle automation is end-to-end operational (ingest -> merge -> categorize -> index)
- **Documentation** is accurate, verifiable, and cross-referenced (no stale/lost paths)
- **An ontological model** describes the project's structure, phases, claims, and evidence
- **Journal and roadmap** anchor planning against disruption and chaos

---

## 🎯 Core Goals

| # | Goal | Priority | Status |
|---|------|----------|--------|
| G1 | **Path portability**: Operational docs use repo-relative paths or placeholders | P0 | ✅ Verified after 2026-07-16 cleanup |
| G2 | **Doc accuracy verification**: Verify all `.md` descriptions match actual code/modules | P0 | ✅ Done (P0–P2 validation pass, 2026-07-09) |
| G3 | **Ontological model**: Build a structured ontology of project entities, periods, claims, evidence | P1 | 🟡 Partial — model and per-run spine exist; project-level topic-run instances outstanding |
| G4 | **Journal system**: Create dated journal tracking periods of activity with claims/results/verification | P1 | ✅ Done |
| G5 | **Roadmap anchor**: Single source of truth for planned vs completed work | P0 | ✅ Done |
| G6 | **Comprehensive architecture reference**: ARCHITECTURE_AND_MODULES.md covering all 3 subsystems | P0 | ✅ Done |
| G7 | **NLP/ontology grounding**: Evaluate NLP/POS tagging for extracting ontology from project text | P2 | 🔴 OUTSTANDING |
| G8 | **TraceLedger alignment**: WordPipe as a library consumable by TraceLedger | P1 | 🟡 PARTIAL — protocols/library boundary exist; external integration not validated here |
| G9 | **Chronicle automation**: Composable CLI pipeline to ingest, merge, categorize, index deep-search files | P3 | ✅ Done |
| G10 | **P0/P1 stabilization**: Chronicle deps, canonical verify, fail-fast orchestration, step tests, CI | P0/P1 | ✅ Done |
| G11 | **Topic-neutral report performance loop**: Stage non-Chronicle Markdown bundles, measure extraction/tagging/runtime, and iterate from evidence | P1 | ✅ Done (template + InsuranceChatbot run) |
| G12 | **Generic topic runner and ontology spine**: Run any configured topic with one audited command, trend metrics, and minimal ontology outputs | P1 | ✅ Done (Phase 13) |

---

## 🚧 Constraints

| # | Constraint | Impact |
|---|------------|--------|
| C1 | Limited/unstable internet access | Cannot rely on `pip install`, GitHub API, or external NLP services |
| C2 | Windows environment with PowerShell | Tooling must be Win32-compatible; paths use backslash in shell, forward in code |
| C3 | Existing massive doc set (many `.md` files) | Risk of redundancy, contradiction, and path rot |
| C4 | Absolute paths (`F:\Git\...`) embedded in docs | Breaks for any other clone location or user |
| C5 | Evidence files in `_ARCHIVE/` are append-only or replace-on-run | Must preserve historical evidence |
| C6 | `_WORK/snapshot` is immutable input | Must not modify source snapshot |

---

## 📋 Phases (Newest First)

Status labels: **VERIFIED** means implementation plus proportionate evidence;
**PARTIAL** means meaningful work exists but the stated outcome is incomplete;
**OUTSTANDING** means planned behavior/evidence is absent; **SUPERSEDED** means a
later implementation satisfies the intent differently. Detailed crosswalk:
[`docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md`](docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md).

### Phase 14 — Second Topic Adapter & Multi-Topic Ontology Readiness (P1)
> Goal: Add a second topic through the Phase 13 generic runner, proving reusability and providing multi-topic evidence before any strategic ontology expansion.
> **Date:** 2026-07-16 | **Status:** ✅ Completed

| Slice | Task | Status |
|-------|------|--------|
| 14.1 | Identify and validate a second Markdown topic | ✅ Done (pipelinechronicle: `_ARCHIVE/pipeline-chronicle/`, 5 files) |
| 14.2 | Create generic Markdown-section adapter (`tools/prepare_generic_markdown_chronicle.py`) | ✅ Done |
| 14.3 | Register adapter in `ADAPTER_REGISTRY` and add topic folder (manifest, themes, README) | ✅ Done |
| 14.4 | Baseline + trend runs through the generic runner | ✅ Done |
| 14.5 | Validate ontology spine with multi-topic evidence | ✅ Done |
| 14.6 | Add adapter tests and runner registry tests | ✅ Done |
| 14.7 | Update docs and assess Phase 15 readiness | ✅ Done |
| 14.8 | Remediate genericity review findings and map Phase 14 context | ✅ Done (dynamic month headings, manifest topic summaries, `##` boundary documented) |
| 14.9 | Audit roadmap claims, label outstanding work, and enforce root organization | ✅ VERIFIED (alignment audit + root checker) |

Phase 14 output: `WordHorrorStories/pipelinechronicle/output/phase14_baseline_validation/`
and `phase14_trend_validation/` — 50 staged/merged/tagged events, 0 errors, PASS verdict.
Trend COMPARED against baseline. Both topics (insurancechatbot + pipelinechronicle)
have identical ontology spine coverage.

Genericity remediation evidence: `phase14_genericity_fix_baseline/` and
`phase14_genericity_fix_trend/` preserve the 50/50/50 PASS baseline while
proving date-derived month headings and manifest-derived summary titles.

Phase 15 (semantic ontology expansion) is now justified — see
[Phase 14 doc](docs/PHASE14_SECOND_TOPIC_ONTOLOGY_READINESS.md) for the readiness assessment.

### Phase 15 — Provenance Foundation & Semantic Ontology Design (P1)
> Goal: Strengthen adapter preparation contracts and file-level source lineage before event-level semantic ontology expansion.
> **Date:** 2026-07-17 | **Status:** ✅ Provenance foundation complete; semantic extraction outstanding

Design doc: [`docs/PHASE15_PROJECT_SEMANTIC_ONTOLOGY_DESIGN.md`](docs/PHASE15_PROJECT_SEMANTIC_ONTOLOGY_DESIGN.md)

| Slice | Task | Status |
|-------|------|--------|
| 15.1 | Common preparation-metrics validation in the topic runner | ✅ Done |
| 15.2 | Consumed-source metrics semantics (`input_file_count` / bytes / lines) | ✅ Done |
| 15.3 | Built-in adapter file-level `source_lineage` | ✅ Done |
| 15.4 | Fail-closed prepare-contract handling before pipeline | ✅ Done |
| 15.5 | Lineage-aware aggregate `source_attribution.json` | ✅ Done |
| 15.6 | Project Phase 15 semantic design + decision gate | ✅ Done |
| 15.7 | Append-only run-directory reservation and portable run-ID validation | ✅ Done |
| 15.8 | Top-level staged-path and finite coverage validation | ✅ Done |
| 15.9 | Canonical hash-catalogued input corpus migration and CI guard | ✅ Done |
| 15.10 | Fresh paired Phase 15 closeout evidence under v2 run IDs | ✅ Done |
| 15.11 | Whole-project domain crosswalk, architecture stability gate, and static import-boundary check | ✅ Done |

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

The third-adapter and unsafe-serializer conditions are the primary triggers. Secondary signals—a defect requiring synchronized production edits on two separately audited occasions, an import-boundary violation that cannot be repaired locally, or a public contract that cannot evolve safely despite characterization tests—support but do not independently mandate broad decomposition. Repeated-defect evidence must be dated and path/test-backed in `JOURNAL.md` or the implementation-alignment audit.

This slice implements file-level provenance only (`SourceBundle → raw source → StagedSource`). Source-section locators and stable individual ReportEvent IDs are delivered in Project Phase 16 as evidence sidecars; semantic concept extraction remains outstanding.

### Phase 17 — Event-Provenance Survivor Integrity & Repeatability (P1)
> Goal: Independently verify actual merged survivor keys and prove stable SourceEvent/ReportEvent mappings across a second fresh paired run before ontology v2 design.
> **Date:** 2026-07-17 | **Status:** ✅ Done — survivor verification + paired stability; ontology emission excluded

Design doc: [`docs/PHASE17_EVENT_PROVENANCE_SURVIVOR_AND_REPEATABILITY.md`](docs/PHASE17_EVENT_PROVENANCE_SURVIVOR_AND_REPEATABILITY.md)

| Slice | Task | Status |
|-------|------|--------|
| 17.1 | Merge-note-aware actual survivor-key verification without changing merge behavior | ✅ Done |
| 17.2 | Auditable Phase 16 baseline → Phase 17 stable-id comparison | ✅ Done |
| 17.3 | Fresh paired `phase17_event_provenance_repeatability` runs after collision and preservation preflight | ✅ Done |
| 17.4 | Repeatability gate assessment; ontology emission remains excluded | ✅ Done |

Controlled evidence: `phase17_event_provenance_repeatability` and reserved `phase17_provenance_stability` under both topic output bases. Phase 16 `unmerged_source_event_count` remains keep-both count-parity history; Phase 17 uses actual survivor membership (`merged-note-aware-v1`).

The committed Git scope and boundaries are recorded in [`docs/engineering/PHASE13_17_COMMIT_DRAFT.md`](docs/engineering/PHASE13_17_COMMIT_DRAFT.md). Commit `a635ea2` closes the implementation/evidence stack that began after a Git baseline predating Phase 13; it is not a Phase 15-only change.

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

### Phase 16 — Stable Event Identity & Section-Level Provenance (P1)
> Goal: Transport section/commit locators through prepare → normalised fingerprints → merge survivors without changing Chronicle dedup or aggregate ontology emission.
> **Date:** 2026-07-17 | **Status:** ✅ Evidence sidecars implemented and closeout-tested; Phase 17 repeatability and individual ontology emission deferred

Design doc: [`docs/PHASE16_EVENT_IDENTITY_AND_SECTION_PROVENANCE.md`](docs/PHASE16_EVENT_IDENTITY_AND_SECTION_PROVENANCE.md)

| Slice | Task | Status |
|-------|------|--------|
| 16.0 | Permanent characterization tests (ingest comment→body, hashes, empties) | ✅ Done |
| 16.1 | Adapter raw `event_lineage` emit + pointer + pre-pipeline envelope | ✅ Done |
| 16.2 | Post-pipeline correlation before summarize + provenance exit + summary section | ✅ Done |
| 16.3 | Design doc, roadmap sync, controlled runs (`phase16_event_lineage_validation`) | ✅ Done |
| 16.4 | Aggregate→individual ontology migration gate (design only; no emission) | ✅ Done |

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

Controlled evidence: `WordHorrorStories/insurancechatbot/output/phase16_event_lineage_validation/` and
`WordHorrorStories/pipelinechronicle/output/phase16_event_lineage_validation/`.

### Phase 13 — Generic Topic Report Runner & Performance Trends (P1)
> Goal: Convert the InsuranceChatbot-specific report workflow into a reusable topic-runner with manifests, one-command execution, trend comparison, source attribution, and a minimal ontology spine.
> **Date:** 2026-07-16 | **Status:** ✅ Completed

Roadmap doc: [`docs/PHASE13_GENERIC_TOPIC_REPORT_RUNNER_ROADMAP.md`](docs/PHASE13_GENERIC_TOPIC_REPORT_RUNNER_ROADMAP.md)

| Slice | Task | Status |
|-------|------|--------|
| 13.1 | Define topic-run manifest schema: topic name, input directory, adapter, theme config, output policy, and quality gates | ✅ Done |
| 13.2 | Add one-command runner for prepare -> pipeline -> summarize -> trend update | ✅ Done |
| 13.3 | Refactor InsuranceChatbot preparation into the first registry-backed adapter | ✅ Done |
| 13.4 | Add trend comparison across repeated runs for the same topic | ✅ Done |
| 13.5 | Emit `topic_run_manifest.json` and `topic_run_ontology.json` for each run | ✅ Done |
| 13.6 | Improve source attribution in appendix output and/or a source sidecar JSON | ✅ Done (`source_attribution.json`) |
| 13.7 | Add tests for manifest parsing, dry-run execution, trend comparison, and ontology-spine output | ✅ Done |
| 13.8 | Update docs with the generic runner command and migration path from bespoke adapters | ✅ Done |

Historical Phase 13 validation: `pytest -q` reported 124 passed. Controlled runs
`phase13_baseline_validation` and `phase13_trend_validation` prove repeated-run
trend comparison. The trend run emits `RUN_SUMMARY.md`, `run_metrics.json`,
`topic_run_manifest.json`, `topic_run_ontology.json`, `trend_report.json`,
`trend_report.md`, and `source_attribution.json`.

Ontology stance: Phase 13 is the right time to define the strategic ontology
spine, but not the right time for full ontology population. The minimum model
should cover `Topic`, `SourceBundle`, `TopicAdapter`, `TopicRun`,
`StagedSource`, `ReportEvent`, `Theme`, `Metric`, `EvidenceArtifact`, and
`Verdict`. Larger semantic ontology work should wait until multiple different
topics have passed through the generic runner.

### Phase 12 — Topic Adapter Performance Loop (P1)
> Goal: Make the Chronicle pipeline usable for arbitrary long Markdown topics through staging adapters, topic-specific themes, and repeatable performance checks.
> **Date:** 2026-07-16 | **Status:** ✅ Completed

| Slice | Task | Status |
|-------|------|--------|
| 12.1 | Add InsuranceChatbot preparation tool for commit history, project digest, and roadmap Markdown | ✅ Done |
| 12.2 | Add InsuranceChatbot theme config for knowledge base, retrieval, runtime, ontology, scraper/release, CI, docs, data quality, and operations tags | ✅ Done |
| 12.3 | Fix Chronicle ingest ISO-date heading extraction for staged topic events | ✅ Done |
| 12.4 | Add focused topic-adapter tests; suite now passes with 105 tests | ✅ Done |
| 12.5 | Run measured InsuranceChatbot report and publish `RUN_SUMMARY.md`, `run_metrics.json`, logs, and appendices | ✅ Done |
| 12.6 | Add topic-neutral iterative performance check template for future subjects | ✅ Done |

Observed performance: 195,293 input bytes across 3 files; 169 commit headings and
31 section candidates; 200 staged events; 200 merged events; 194 tagged events;
0 duplicate/conflict entries; 0 warnings/errors; 6.96s wall time.

Template: [`docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md`](docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md)

### Phase 11 — P0–P2 Repository Review Remediation (P0/P1/P2)
> Goal: Stabilize packaging contract, doc trust, canonical verify, orchestration fail-fast, step tests, segmenter perf, CI
> **Date:** 2026-07-09 | **Status:** ✅ Completed

| Slice | Task | Status |
|-------|------|--------|
| P0-1 | Declare `chronicle` optional extra (`pyyaml`, `python-dateutil`) | ✅ Done |
| P0-2 | Fix README/ROADMAP stale metadata; fix docs link checker false positives | ✅ Done |
| P1-1 | Extract `verify_ingest` to `wordpipe.chronicle` + CLI wrappers | ✅ Done |
| P1-2 | Orchestrator fail-fast on style/finalize errors | ✅ Done |
| P1-3 | Step module unit tests | ✅ Done |
| P2-1 | Segmenter heading-path O(n) precompute | ✅ Done |
| P2-2 | Add `.github/workflows/ci.yml` health gate | ✅ Done |
| P2-3 | Authoritative doc crosswalk + validation report | ✅ Done |

Validation: [`docs/engineering/P0_P2_VALIDATION_REPORT.md`](docs/engineering/P0_P2_VALIDATION_REPORT.md)

### Phase 10 — Documentation Architecture & Module Reference (P0)
> Goal: Single source of truth for architecture, modules, integration, flow, logic, goals, and constraints  
> **Date:** 1404/11/25 | **Status:** ✅ Completed
> **Sub-phase 10b (1404/11/25):** Archived 6 stale root docs to `_ARCHIVE/root-docs/`; moved `output/` to `_ARCHIVE/evidence/`; fixed 3 missing pipeline files; updated INDEX.md with pipeline/ section; updated OBSOLETE_DOCS.md with archived root docs

| Task | Description | Status |
|------|-------------|--------|
| 10.1 | Create `ARCHITECTURE_AND_MODULES.md` — comprehensive 3-subsystem reference | ✅ Done |
| 10.2 | Create `docs/OBSOLETE_DOCS.md` — index of superseded vs preserved docs | ✅ Done |
| 10.3 | Update `docs/README.md` — redirect to current source of truth | ✅ Done |
| 10.4 | Update `ROADMAP.md`, `JOURNAL.md`, `ONTOLOGY_MODEL.md`, `PLAN.md` for new phase | ✅ Done |

### Phase 9 — Chronicle Automation Pipeline (P3)
> Goal: Automate deep-search → normalised → merged → categorised → indexed → referenced workflow  
> **Date:** 1404/11/25 | **Status:** ✅ Sub-phase 9a/b completed, 9c pending

**Sub-phase 9a: Tool Completion & Archival (✅ Completed)**
| Task | Description | Status |
|------|-------------|--------|
| 9a.1 | Build `tools/pipeline-chronicle/ingest.py` — deep-search → normalised MD | ✅ Done |
| 9a.2 | Build `tools/pipeline-chronicle/merge.py` — merge N MDs, dedup by hash+date | ✅ Done |
| 9a.3 | Build `tools/pipeline-chronicle/categorize.py` v1 — tag with ontology + themes | ✅ Done |
| 9a.4 | Build `tools/pipeline-chronicle/chain.ps1` v1 — 4-stage orchestrator | ✅ Done |
| 9a.5 | Build `tools/pipeline-chronicle/verify_ingest.py` — batch verification | ✅ Done |
| 9a.6 | Create `tests/test_pipeline_chronicle.py` — 59 tests | ✅ Done |
| 9a.7 | Archive all 5 tools to `_ARCHIVE/pipeline-chronicle/` with ARCHIVE_REPORT.md | ✅ Done |
| 9a.8 | Tag quality review: 61 events, 96.7% coverage, 29.5% over-tagging, 2 false negatives | ✅ Done |

**Sub-phase 9b: Keyword Tuning & Index Builder (✅ Completed)**
| Task | Description | Status |
|------|-------------|--------|
| 9b.1 | Tighten keywords: "exploit"→"prompt exploit", "crash"→"server crash", "error"→"server error"; add "Linux terminal", "simulating", "mega-viral", "interface"; add negative_keywords per theme | ✅ Done |
| 9b.2 | Create `pipeline/categorize.py` v2 — negative keyword support, `--dry-run`, backward-compatible config loading | ✅ Done |
| 9b.3 | Create `pipeline/themes.json` — external theme config (6 themes, 62 positive + 16 negative keywords) | ✅ Done |
| 9b.4 | Build `pipeline/index.py` — generate 4 appendix files with Jinja2 templates + fallback formatting | ✅ Done |
| 9b.5 | Create `pipeline/index_config.json` — configurable output dir, templates dir, dedup method, theme sort | ✅ Done |
| 9b.6 | Create `pipeline/templates/` — 4 Jinja2 templates (event_index, theme_index, source_manifest, link_registry) with fallback string formatting | ✅ Done |
| 9b.7 | Update `pipeline/chain.ps1` v2 — 5 stages with `-SkipIndex`, `-NoLinkRegistry`, `-SourceCoverage`, `-IndexConfig` switches | ✅ Done |
| 9b.8 | Re-run pipeline: 100% coverage (was 96.7%), over-tagging 18.0% (was 29.5%), false negatives eliminated | ✅ Done |

**Sub-phase 9c: Reference Builder & Ontology Wiring (🟡 PARTIAL / OUTSTANDING)**
| Task | Description | Status |
|------|-------------|--------|
| 9c.1 | Build secondary TOC and topic references on existing survivor anchors | 🔴 OUTSTANDING · delivery Phase 4 |
| 9c.2 | Wire chronicle pipeline into ontology | 🟡 PARTIAL — P9 ActivityPeriod exists; topic-run instances remain outstanding |
| 9c.3 | Compare automated output with `ChatGPT_Incidents_Merged.md` where authorized and available | 🔴 OUTSTANDING · delivery Phase 4 |
| 9c.4 | Generalize topic adapter pattern beyond InsuranceChatbot with a config-driven adapter registry | ✅ Superseded by Phase 13 |
| 9c.5 | Add a command wrapper that runs prep, pipeline, summary, and metrics in one audited invocation | ✅ Superseded by Phase 13 |

### Phase 7 — WordPipe Modular Refactor (P1)
> Goal: Refactor wordpipe into clean, import-safe layered architecture  
> **Date:** 1404/11/25 | **Status:** ✅ Completed

| Task | Description | Status |
|------|-------------|--------|
| 7.1 | Create layered architecture (core → interfaces → adapters → orchestration → CLI/plugins) | ✅ Done |
| 7.2 | Create `pyproject.toml` with extras (openai, dotenv, cli, docx) | ✅ Done |
| 7.3 | Create `tests/test_import_safety.py` | ✅ Done |
| 7.4 | Add backward-compatible wrappers in `wordpipe/pipeline/` and `wordpipe/flatteners/` | ✅ Done |
| 7.5 | Pipeline step module refactor: flatten, style, segment, finalize, toc | ✅ Done |
| 7.6 | Add fail-fast read/style behavior and focused step/orchestration tests | ✅ Done |

### Phase 6 — Foundation Fixes & Ontology Building (P0)
> Goal: Make the project portable, navigable, and self-consistent  
> **Date:** 1404/11/25 | **Status:** ✅ Completed

| Task | Description | Status |
|------|-------------|--------|
| 6.1 | Replace absolute Windows paths in docs with relative paths | ✅ Done |
| 6.2 | Create `ROADMAP.md`, `JOURNAL.md`, `ONTOLOGY_MODEL.md`, `INDEX.md`, `README.md` | ✅ Done |
| 6.3 | Create `tools/add_standard_headers.py` — apply standard Jalali-date headers | ✅ Done |
| 6.4 | Apply standard headers to all 82 active Python files | ✅ Done |
| 6.5 | Clean 45 files with duplicate headers | ✅ Done |
| 6.6 | Analyze duplicates (60+ mirror pairs, 8 compatibility wrappers, 18 legacy versions) | ✅ Done |
| 6.7 | Remove BOM from `tools/jalali.py` | ✅ Done |

### Phase 5 — Documentation Pack (P2)
> Goal: Comprehensive documentation with role-based entrypoints  
> **Date:** 1404/11/24 | **Status:** ✅ Completed

| Task | Description | Status |
|------|-------------|--------|
| 5.1 | Create `docs/` directory hierarchy (architecture/, engineering/, operations/, PlansArchive/) | ✅ Done |
| 5.2 | Create `docs/README.md`, `DOC_STYLE_GUIDE.md`, `DUPLICATE_POLICY.md` | ✅ Done |
| 5.3 | Create TraceLedger docs (LOGIC_FLOW, DEBUG_ENHANCEMENT_PLAN, INTEGRATION_CONTRACT, REPOSITORY_REVIEW) | ✅ Done |
| 5.4 | Create `tools/docs_link_check.py` | ✅ Done |
| 5.5 | Add EventSink protocol (`wordpipe/events.py`) | ✅ Done |

### Phase 4 — Security Hardening & Pipeline Contracts (P1)
> Goal: Redact leaked keys, add secrets scanner, standardize stage interfaces  
> **Date:** 1404/11/22 | **Status:** 🟡 PARTIAL — local hardening verified, dated remote-ref audit recorded, public-scope refresh queued

| Task | Description | Status |
|------|-------------|--------|
| 4.1 | Redact leaked API keys from workspace and .gitignore | ✅ Done |
| 4.2 | Create `.env.example` | ✅ Done |
| 4.3 | Create `tools/security_scan.py` | ✅ Done |
| 4.4 | Create `tools/pipeline_contracts.py` with StagePaths/StageResult/StageError | ✅ Done |
| 4.5 | Create `tools/orchestrate.py` for one-command pipeline | ✅ Done |
| 4.6 | Create pipeline docs (RUNBOOK, CONTRACTS, SECURITY, TOOLS_MODULES, INTEGRATION_MAP, LABOR_REPORT) | ✅ Done |
| 4.7 | Audit remote refs/history for previously leaked keys | August 2026 audit recorded in the [optimization map](docs/engineering/OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md). Current public-scope assurance is tracked in [#17](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/17). |

### Phase 3 — Initial Snapshot & Evidence Pipeline (P0)
> Goal: Extract snapshot, create initial workspace, establish evidence pipeline  
> **Date:** 1404/11/21 | **Status:** ✅ Completed

| Task | Description | Status |
|------|-------------|--------|
| 3.1 | Extract `snapshot_20260211_205716.zip` | ✅ Done |
| 3.2 | Create manifest.jsonl/csv | ✅ Done |
| 3.3 | Generate relocation plan and map | ✅ Done |
| 3.4 | Apply legacy reorganization | ✅ Done |
| 3.5 | Build legacy index | ✅ Done |
| 3.6 | Verify integrity | ✅ Done |

---

## 🧭 Outstanding Works

The [delivery plan and backlog](docs/engineering/DELIVERY_PHASES_AND_GATES.md#backlog-activation-and-synchronization)
carry the current work inventory, GitHub issues and activation conditions.
Historical phase numbers above retain their original scope. Phase 9c references
and manual comparison map to delivery Phase 4. Project Phase 15's candidate
semantic schema remains subject to its design and evaluation gate.

Broad topic-runner decomposition is conditional. Reconsider when a third
adapter exposes concrete coupling or ontology schema evolution makes the
current serializer unsafe.

---

## 🏁 Milestones (Newest First)

| MS# | Milestone | Phase | Target Date | Status |
|-----|-----------|-------|-------------|--------|
| M19 | Third-wave P0/P1 remediation (5 findings + CI gap) | — | 1405-05-03 | ✅ code complete; CI revalidation pending |
| M18 | Second-wave P0/P1 remediation (7 additional findings) | — | 1405-05-03 | ✅ |
| M16 | Project Phase 17 survivor integrity and stable-id repeatability | Ph17 | 1405-04-26 | ✅ |
| M17 | P0 reliability remediation (6 verified defects fixed) | — | 1405-05-02 | ✅ |
| M15 | Project Phase 16 section provenance sidecars and correlation | Ph16 | 1405-04-26 | ✅ |
| M14 | Project Phase 15 provenance foundation and semantic design gate | Ph15 | 1405-04-26 | ✅ |
| M13 | Second-topic genericity remediation and root organization enforcement | Ph14 | 1405-04-25 | ✅ |
| M12 | Generic topic runner supports manifest-driven one-command runs and trend comparison | Ph13 | 1405-04-25 | ✅ |
| M11 | Topic-adapter performance loop validated on InsuranceChatbot and template published | Ph12 | 1405-04-25 | ✅ |
| M10 | Comprehensive architecture reference published, old docs indexed as obsolete | Ph10 | 1404-11-25 | ✅ |
| M9 | Tag quality: 100% coverage, <=20% over-tagging | Ph9 | 1404-12-20 | ✅ |
| M8 | Chronicle pipeline operational — ingest→merge→categorize→index works end-to-end | Ph9 | 1404-12-20 | ✅ |
| M7 | WordPipe passes import-safety + unit tests | Ph7 | 1404-12-20 | ✅ |
| M6 | Foundation files (ROADMAP, JOURNAL, ONTOLOGY, INDEX, README) published | Ph6 | 1404-11-25 | ✅ |
| M5 | Documentation pack with role-based entrypoints | Ph5 | 1404-11-24 | ✅ |
| M4 | Security posture improved, pipeline contracts operational | Ph4 | 1404-11-22 | ✅ |
| M3 | Evidence pipeline established with 98 files inventoried | Ph3 | 1404-11-21 | ✅ |
| M2 | Dated doc-accuracy pass completed; later drift reconciled by current alignment audit | Ph10/14 | 1405-04-25 | ✅ |
| M1 | Operational documentation uses relative paths/placeholders | Ph6/14 | 1405-04-25 | ✅ |

---

## 📊 Values & Principles

1. **Evidence over opinion** — every claim should point to a file, a log, or a run
2. **Portability** — no absolute paths, no environment-dependent behavior
3. **Idempotency** — re-running the same pipeline produces the same result
4. **Non-destructive** — copy-only, conflict-safe, append-only where historical
5. **Backward compatibility** — changes must not break existing stage contracts
6. **Traceability** — every phase, task, and decision links to a journal entry

---

## 🔗 See Also

- [`ARCHITECTURE_AND_MODULES.md`](ARCHITECTURE_AND_MODULES.md) — Comprehensive reference: architecture, modules, data flow, logic flow, goals, constraints for all 3 subsystems
- [`PLAN.md`](PLAN.md) — Immutable log of intentions and completions
- [`INDEX.md`](INDEX.md) — Full project file index
- [`JOURNAL.md`](JOURNAL.md) — Dated period journal with claims and verification
- [`ONTOLOGY_MODEL.md`](ONTOLOGY_MODEL.md) — Formal entity/relation model
- [`pipeline/CODEX_WORKING.md`](pipeline/CODEX_WORKING.md) — Working code reference with evolution timeline and known issues
- [`docs/PHASE13_GENERIC_TOPIC_REPORT_RUNNER_ROADMAP.md`](docs/PHASE13_GENERIC_TOPIC_REPORT_RUNNER_ROADMAP.md) — Completed generic runner, trend, and ontology-spine roadmap
- [`docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md`](docs/ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md) — Topic-neutral report run performance checklist
- [`WordHorrorStories/insurancechatbot/output/phase13_trend_validation/RUN_SUMMARY.md`](WordHorrorStories/insurancechatbot/output/phase13_trend_validation/RUN_SUMMARY.md) — Latest measured generic topic-runner run
- [`docs/OBSOLETE_DOCS.md`](docs/OBSOLETE_DOCS.md) — Index of superseded vs preserved documentation
- [`docs/README.md`](docs/README.md) — Documentation entrypoint (redirects to current source of truth)
