# WHS delivery phases and acceptance gates

The [root roadmap](../../ROADMAP.md) is the entry point for delivery order.
This plan defines delivery phases, acceptance gateways, the issue map and
release milestones. GitHub issues own the active work and its acceptance
checklists. Dated experiment and corpus reports own their measurements.
Delivery phase numbers and gateway IDs are scoped to this plan. The root
roadmap retains the original Project Phase 9c, Phases 13–17 and goal IDs.

## Authority and freshness

GOV-01 = issue [#14][i14], implemented by merged [PR #19][pr19].
Do not open another governance issue or PR. This file is the sole authority
for phase execution, gateways, work-package mapping, release readiness and
risks. PHASE_EXECUTION_PLAN.md, ACCEPTANCE_GATE_MATRIX.md, ISSUE_ROADMAP_MAP.md
and RELEASE_READINESS.md are unnecessary: their proposed roles are already
covered here. ROADMAP.md owns strategic direction and dated history,
OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md owns technical debt and historical
evidence, and REPO_MAP.md owns navigation. The maintainer owns all four.
Check these documents and search GitHub before adding a tracking surface;
record a supersession and redirect if authority ever changes.

G0 ACCEPT: the maintainer approved the planning contracts on 2026-11-20.
PR #19 was already merged by the time the final conditions were recorded;
its history-preserving merge is `d26e6e998123806e53aa352ea4f40a5a6363e1b5`.
Issue #14 is closed; MD-01 is admitted to slot 1. The numerical values remain
provisional planning baselines, not qualification results.

At the earlier pre-merge snapshot on 2026-11-20 the nine existing issues were open;
PRs #2–#7 and #12 are merged, #1 is closed unmerged, and #13 and #19 are
open drafts. The existing CI definition has three Windows and two Ubuntu jobs.
Historical CI results remain tied to their original SHA. No fresh test
execution is asserted by this correction.

## Starting decisions

| Work | Verified state on 2026-11-20 | Next decision |
|---|---|---|
| Chronicle baseline | PRs [#2][pr2]–[#6][pr6] are merged, including structured run evidence, strict configuration and survivor navigation. Main at `e2f1c17643b0` has five successful [hosted CI jobs][main-ci]. | Verify release behavior through the installed entry points. |
| Flowers | PR [#7][pr7] is merged with engineering and navigation evidence. Real-corpus semantic acceptance remains **REVIEW**. | Apply the independent rubric in [#16][i16] after the Phase 2 decisions. |
| NCM pilot | PR [#12][pr12] is merged as research evidence. Genuine inference is **BLOCKED**. Real Flowers quality and incremental NCM benefit are **UNMEASURED**. | Reuse upstream runtime qualification for [#9][i9]. |
| Context export | [Frozen B2](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/commit/920c8e044ad7553d11d010bdba6ae580626db961) failed G1. First-run results were 28/30 verified valid deliveries, 9/20 correct refusals, 1/10 absent-field refusals, and 0% median estimated complete-packet GPT-2 savings. | G1 **REVISE** under [#8][i8]. B3 **DEFERRED**. Preserve the [first-run and investigation evidence](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/blob/32387d67b76aad99baa462cf1cc7c3172901681d/docs/engineering/WHS_CONTEXT_PACK_B2.md#b2-root-cause-disposition--2026-11-21) in [draft PR #13][pr13]. |
| Release boundary | The package metadata says `0.1.0`. Proposed v0.2 is the deterministic Chronicle release. | Certify v0.2 against the checklist below. Track WordPipe DOCX readiness independently. |

At the baseline, seven PRs had merged, PR #1 had closed without merging, and
PR #13 was the sole open PR at that earlier baseline; #19 subsequently opened and merged. B0's original eight-case NCM-pilot metrics and
its replay on #13's 24-case benchmark describe different datasets.

## Parallel work and dependencies

The primary sequence is context fidelity, document understanding, corpus
acceptance, references and ontology, product stabilization, knowledge
intelligence, then optional model research. The completed B2 run used the
verified generic Markdown path. Its failures establish no MD-01 dependency. Public
release assurance [#17][i17] and atomic DOCX [#18][i18] are technically independent,
but SEC-01 precedes SAFE-01 in slot 3.
Integrate the documentation PR independently. PR #13 also touches the root
roadmap and retrieval map, so reconcile those two files against the eventual
merge base during the #8 revision and retain both workstreams' evidence.
Reference and project-ontology work may proceed with verified synthetic runs
when Flowers remains under local review. Offline Jev fixture preparation can
begin alongside taxonomy characterization. The combined benchmark waits for
its upstream evidence.

### Phase-to-gate mapping and dependencies

Delivery phases 1–7 map one-to-one to G1–G7 respectively. G0 is governance
across all seven, not another phase. Historical Project Phase 9c, Phases
13–17 and historical goal IDs retain their existing meanings.

```text
G0 governance (#14 / PR #19)
  +--> G1 fidelity (#8; pinned experimental inputs)
  +--> G2 parsing (MD-01 -> TIME-01 / NLP-01)
  |      +--> G3-core deterministic fixtures
  |      +--> G3-full semantic gold (#16)
  +--> G5 security / execution / installed CLI / platform checks
G2 + verified survivors --> G4-core references and compatible instances
G0 + G1 + G2 + G3-core + G4-core + G5 --> v0.2
G3-full + G4-core + NLP evaluation --> G4-full / v0.3
G4-full --> G6 knowledge (PERF-01 -> optional STORE-01)
G1 + qualified upstream runtimes --> G7 (#9 and #10 -> #11)
SAFE-01 / DOCX-01 and INT-01 --> independent product/consumer decisions
```

Arrows denote dependencies, not slot admissions. Offline G7 preparation
may be admitted earlier; G7 never blocks v0.2.

### Active execution queue

Allow at most three admitted work packages, including documentation, research,
hardening and offline preparation. READY means eligible, not admitted;
parallel means technically independent and still consumes a slot if admitted.
QUEUED means capacity or prerequisites are pending. BLOCKED/DEFER releases
its slot after the maintainer records the decision. Record every admission,
exit and successor; no fourth active package.

| Slot | Current package | Next decision |
|---|---|---|
| Slot 1 — document understanding | MD-01 [#15][i15] (admitted) | Characterize Markdown structure and lineage; decide a bounded correction. GOV-01 exited with G0 ACCEPT. |
| Slot 2 — research fidelity | **Vacant** | B2 finished with G1 REVISE and the maintainer deferred B3 under [#8][i8]. No successor is admitted by this decision. |
| Independent hardening | SEC-01 [#17][i17] | Complete the public release audit. SAFE-01 [#18][i18] remains READY until recorded exit and explicit admission. |

**Slot 2 release.** [PR #20](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/20) integrated at
`c78c6e90d96ee8e9f07e08b14e74de1bd657de93`, recording the B3 DEFER exit.
Slot 2 is vacant and unreserved. Any successor requires a separate
priority, prerequisite, scope, ownership and admission decision.
**G1 REVISE remains an unresolved mandatory v0.2 release blocker.**

GOV-01 [#14][i14] exited on 2026-11-20 after PR #19 integration and maintainer
acceptance; MD-01 [#15][i15] is formally admitted in slot 1. This is admission
only, not a claim of implementation or G2 acceptance.
CORP-01 [#16][i16] can prepare its rubric offline once admitted. Technical
independence allows work to start with an available slot. Gated, queued and
deferred entries in the [issue map](#backlog-activation-and-synchronization)
are outside the current execution queue.

## Phase 1 — Context fidelity

**Gateway.** [G1 Fidelity](#acceptance-gateway-matrix).

**Disposition.** The maintainer accepted the completed B2 **REVISE**
result and deferred B3 on 2026-11-21. Preserve B1, frozen B2, the first-run
50-case population and the scorer and gold as dated evidence. Use the
exposed population only for historical and regression work. The failure
was coupled: permissive raw fallback allowed 11 non-responsive deliveries,
while suppressing all raw packets would remove 27 valid deliveries. No
validated correction yet preserves coverage and supplies sufficient compact
verified evidence. The completed experiment consumed slot 2. PR #20 released it upon integration.
Any successor requires separate admission.

### B3 re-entry

The maintainer requires a bounded proposal with evidence in four dimensions
before authorizing implementation.

1. **Authorization.** Require verified evidence for the requested relation
   and entity before raw fallback. Demonstrate 100% correct refusal on at
   least 20 previously unexposed absent-field development cases across
   independently authored source templates.
2. **Narrative grounding.** Show that verified prose can answer a field
   request without a canonical label. Include a narrative deadline and an
   absent-field or cross-entity counterexample. Evaluate deterministic
   evidence first.
3. **ID-less matching.** Retrieve the correct verified evidence and
   qualifications for representative paraphrases without IDs. Report
   exact and paraphrase outcomes separately. Apply the existing aggregate
   G1 coverage criterion.
4. **Compact delivery.** Demonstrate at least 20% median complete-packet
   GPT-2 savings across valid cases on a separate development corpus.
   Compare against raw in the same run with receipt metadata, zero
   consumer rereads, and zero credit for fallback and refusal.

These demonstrations establish readiness for review. After separate
authorization, freeze the new candidate and measurement contract before
independent authorship. Use a fresh independently adjudicated 50-case
holdout with 30 valid requests and 20 expected refusals, including 10
absent-field requests. The registered gates still require at least 29/30 verified
valid deliveries, 20/20 expected refusals and 10/10 absent-field refusals.
Retain the existing retention, provenance, replay and efficiency
requirements below.

MD-01, CORP-01, CORE-01, TIME-01 and NLP-01 are possible contributors.
Add a dependency only when a reproduced gap requires a concrete
capability or interface from that package. Flowers authorization, corpus
review and G3 qualification remain separate.

**Exit gate.** All delivered fresh-holdout packets retain 100% of annotated
critical facts and exact required IDs, have verified anchors and contain zero
unsupported facts. Report results across all cases and delivered cases. Freeze
coverage and efficiency criteria from the quantified G1 contract before scoring. Classify and count structural
delivery, raw fallback and refusals separately, including expected refusals.
Keep budget refusals in the coverage and applicable fact denominators. Report
estimates and measured usage distinctly. Replay deterministically and verify
canonical artifact hashes. Record ACCEPT or REVISE with report and exact head.
Any separately authorized evidence-only integration of draft PR #13 must
reconcile its roadmap and retrieval-map history with current main, then
verify exact-head CI and the diff boundary. The experiment remains research
evidence and issue #8 stays open.

## Phase 2 — Document understanding

**Gateway.** [G2 Parsing](#acceptance-gateway-matrix).

**Entry.** Use synthetic fixtures and characterize the current generic adapter
and lineage contract. MD-01 [#15][i15] is admitted in slot 1 independently of B2.

**Work.** Compare the current extraction with block-aware Markdown using the
existing parser dependency. Cover fenced headings, blockquotes, nested blocks,
tables, frontmatter, preambles, empty sections, heading-level settings,
CRLF/LF and mixed script. Compare the current regex with `markdown-it-py`
tokens and source maps before selecting another parser. Reconcile candidate
and staged ordinals, date role, source/report IDs, survivor and navigation,
and verify source bytes, replay and clean source/installed test origins.

### MD-01 characterization handoff (2026-11-26)

**Maintainer decision.** [Issue #15][i15] records characterization **ACCEPT**
and G2 **REVISE**. [Draft PR #22](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/22)
publishes the original handoff `19fb36863dc9ae184347c385243d552997b15428`.
The opt-in implementation and its identity contract require separate approval.

**Verified at `fd2d60f72a47fbccc60e64f72c811d106c01a30e`.** The frozen
UTF-8 fixture is [md01_structure.md](../../tests/fixtures/md01_structure.md)
(LF SHA-256 `c7fdcfe34300f7bf55f4950455e24b08db41eb1ee8237a3e665c7295c75ccda5`).
The ledger below uses one-based inclusive source lines. The parser emits
zero-based, end-exclusive token maps, so a map of `[9,13]` spans lines 10–13.

| Fixture lines | Regex baseline | markdown-it-py 4.2.0 |
|---|---|---|
| 1–5 | No section. The preamble date still supplies the file fallback. | CommonMark reads the first line as a rule, lines 2–3 as a Setext h2, and line 5 as a paragraph. No YAML frontmatter rule was enabled. |
| 7–8, 10–13, 15–18 | Alpha starts at 7. The backtick/tilde examples become spurious events at 11 and 16. Their boundaries split both fenced blocks. | Alpha is a top-level ATX h2. Each fence is one block with no internal heading token. |
| 20–25 | Quote and list remain body text of the preceding false section. | Quote h2 at 20 is level 1. List h2 at 24 is level 2. Neither is a top-level section. |
| 27–32 | Child h3 stays in the current body with production levels `(2,)`. With `(2,3)` it becomes a candidate. Table rows stay in the body. | Child is a top-level h3. The explicit table rule maps lines 30–32 as one table. CommonMark alone has no table token. |
| 34–40 | Empty at 34 advances the candidate ordinal. Mixed-script h2 at 35 emits. Setext at 38–39 stays in its body. | Empty and mixed-script headings are h2. The later Setext h2 is structurally visible. |

Production extraction has five candidates and four staged events. The
emitted (line, candidate, staged) tuples are (7,1,1), (11,2,2), (16,3,3),
(35,5,4). With `(2,3)` the tuples are (7,1,1), (11,2,2), (16,3,3),
(27,4,4), (35,6,5). LF and CRLF produced equal parsed events, locators and
source IDs at each setting, with source bytes preserved. Alpha uses the first
ISO date in its section. Other emitted events use the first ISO date in the
file for ordering. The current lineage has a start line and date, with no
end line or date-role field.

Two Windows source topic-runner replays with the checkout pinned in
`PYTHONPATH` succeeded with the synthetic manifest. Correlation had four
source events, four report events, four verified survivor keys, zero ambiguous
matches and zero unmerged source events. Lineage and correlation differed
only in the run ID. Merged output and appendix navigation were byte-stable.
All four event-index fragments resolved exactly once. The original unpinned
replay failed index generation with exit 5 after importing the foreign
checkout. The synthetic manifest uses zero extraction and theme minima to
isolate mechanical compatibility. This is Windows source evidence.
Local evidence is under `_WORK/WHS-RELIABILITY-20261126`, including the
manifest, failed and successful runs, and `probe-b/comparison.json`.

**Proposed first correction.** Add a versioned opt-in to the generic adapter.
Select only configured top-level ATX headings using token maps. Use original
source slices for titles and bodies and keep staging/rendering behavior.
Preserve nested headings, fences, tables and Setext text within the enclosing
span. Account separately for preamble, declared leading frontmatter, heading
lines, empty candidates and separator lines. Agree on the supported
frontmatter delimiter rule and treatment of malformed or unterminated blocks.
Derive any byte offsets from the original bytes and newline boundaries. Token
maps are line ranges. They provide neither byte offsets nor a lossless
serialization of the source.

Keep the legacy mode and IDs during the opt-in review. Current source IDs
hash filename, locator kind, candidate ordinal, heading level and original
heading text, under the topic namespace. Removing false candidates can
renumber later headings. Current report IDs hash date and normalized ingest
body, so repaired bodies can also move report IDs and survivor fragments.
Require a per-candidate old/new reconciliation, including excluded candidates,
assigned ordering dates and any affected external references. Publish a
versioned identity or compatibility mapping decision before changing defaults.

#### Contract proposed for maintainer approval

Only the generic Markdown adapter gains an explicit manifest mode,
`adapter.markdown_mode: structural-v1`, passed through to its prepare CLI.
Missing mode or explicit `legacy-v1` selects the existing extraction and
output contract. Reject unknown modes and the option on other adapters.
An opt-in manifest uses a separate output root and fresh run directory.
Refuse reuse or overlap with a legacy output directory, including resolved
aliases. Record mode and version in structural run metadata and sidecars.
Use distinct schema identifiers for structural lineage and correlation.
Readers that only support legacy v1 must reject those structural sidecars
explicitly. Scope previous-run metric comparisons to the same mode.
Legacy artifacts, IDs and schemas remain byte-compatible for a replay
after accounting for existing run metadata. A structural parsing error
fails the run explicitly.

Use configured top-level ATX headings (default h2) and original source
slices. Nested headings, fences, tables and Setext headings inside a section
are body content. Outside sections record exclusions by span. Recognize
frontmatter only on the opening line, with exact `---` delimiter lines
and a YAML mapping payload. Record an invalid or unterminated opener as
a diagnostic and apply ordinary Markdown rules to its text. Preserve the
existing first-section-date and first-file-date fallback order, considering
only valid calendar dates in structural mode. Record
whether the date came from the section, file fallback or default constant.
These are ordering dates. Full date semantics stay with TIME-01.

| Identity layer | Legacy v1 | Structural v1 proposal |
|---|---|---|
| Candidate and staged ordinals | Existing one-based regex order. Empty candidates reserve ordinals. Staged ordinals count emissions. | One-based selected heading order per file. Empty candidates reserve ordinals. Non-boundaries receive no ordinal. Staged ordinals are dense among emissions. Ordinals are scoped to the parser mode. |
| Source event ID | Existing `source-event-v1` hash of source filename, locator kind, candidate ordinal, level and original heading text, with topic in the ID. | Use those fields in the same order with domain tag `source-event-structural-v1`. Retain the ID prefix and topic. Report one-based source spans and input digest in the sidecar. Keep line endings out of the identity hash. |
| Report event ID | Existing `report-event-v1` hash of date and normalized ingest body hash, with topic in the ID. | Keep normalized ingest equivalence and use domain tag `report-event-structural-v1`. Equal normalized bodies on the same date still coalesce within the mode. Record all contributing source IDs. |
| Survivor and navigation | Existing key `(date, normalized-body SHA-256)` and fragment `event-<date>-<hash>` in the published run. | Keep the same key and fragment algorithm within each run. Equal keys may recur across modes. Navigation identity includes the output run and artifact path, so a coincident fragment never substitutes for a legacy target. |

The following ledger is an expected comparison at default levels. Legacy
values were observed. Structural values are proposed and have no execution
result yet. C and S denote candidate and staged ordinals.

| Fixture heading | Legacy C/S | Structural C/S | Reconciliation |
|---|---:|---:|---|
| Alpha, line 7 | 1/1 | 1/1 | Same source heading. Body regains both fenced blocks, so recompute the report and survivor key. |
| Backtick example, line 11 | 2/2 | — | Removed false event. Its text stays inside Alpha's fenced body. No redirect or replacement event. |
| Tilde example, line 16 | 3/3 | — | Removed false event. Its text stays inside Alpha's fenced body. No redirect or replacement event. |
| Empty, line 34 | 4/— | 2/— | Empty candidate. Neither mode emits an event or ID. |
| Persian/English, line 35 | 5/4 | 3/2 | Same source heading. The structural IDs are distinct by construction. Evaluate whether its report payload and run-local survivor key are equal. |

The comparison sidecar joins candidate rows by frozen source snapshot,
relative source path and heading span. Record both modes' ordinals, IDs,
date roles, body hashes, survivor keys and complete run-relative link targets.
Mark removed false events, new events, changed content and ambiguous matches
explicitly. A unique heading correspondence is evidence for review. It gives
no automatic alias, redirect or transfer of historical identity. Removed
legacy links keep resolving in the original output. Test duplicate headings,
many-to-one report correlation, and paired replay with both output roots
present. Reject any legacy file mutation and require every structural index
link to resolve within its own run. Cross-version comparison uses the
sidecar, while published artifacts and reports retain their original IDs.

**Recommendation.** Accept this bounded contract for implementation review.
Keep production work gated on the maintainer decision. G2 qualification
still requires the original acceptance tests below.

#### Implementation handoff

The maintainer accepted the specific PR #22 head
`2e5c5e363fcdbe001ccdd58fe5d22690fb287d7c` and authorized slot-1
implementation under issue #15. G2 remains REVISE pending acceptance.

For a paired run, first run the existing manifest in legacy mode. In a
separate structural manifest set `adapter.markdown_mode` to
`structural-v1`, point `output.legacy_base_dir` at the legacy output root,
and set `output.base_dir` to a new disjoint root. Optional
`adapter.heading_levels` chooses unique integers from 2 through 6 and
defaults to `[2]`. The runner claims the new
root for structural mode and refuses existing unclaimed roots, input
overlap, and resolved aliases of the legacy root. Subsequent structural
runs use fresh run IDs under the claimed root. Comparison creates new
evidence outside both completed runs.

```console
python tools/compare_markdown_modes.py --legacy-run LEGACY_RUN --structural-run STRUCTURAL_RUN --input-dir FROZEN_INPUT --output NEW_COMPARISON.json
python tools/qualify_md01_wheel.py --evidence-dir FRESH_EVIDENCE_DIR
```

The comparison verifies structural input digests and replays the legacy
staged Markdown and lineage against that snapshot. Historical legacy
outputs lack a raw source digest, so equal replay cannot authenticate
source bytes that never contributed to those artifacts. Qualification
uses checkout driver scripts with `wordpipe` resolved from a fresh wheel
install. This scope leaves CLI-01 and CI-01's broader gates intact.

The structural adapter fails explicitly if source content collides with
reserved month/event framing in the shared Chronicle transport. The source
remains intact and the run records failure. Supporting that transport
edge case requires separate compatibility review. Root checks resolve
configured paths and guard normal runner writes. They do not provide
filesystem isolation from concurrent external renames or symlink mutation.

#### Accepted bounded implementation and parser provenance

The maintainer accepted the bounded implementation in PR #23 at
`1b700d7a82d9b5e0ee350185421fbb10e2950a82` subject to the provenance
correction and its final checks. Structural mode remains opt-in.
The historical characterization used markdown-it-py 4.2.0. The original
hosted implementation qualification used 4.3.0.

The maintainer subsequently accepted the three review corrections at
`8f7e87af0d4295ee01008415460f061be2ad10c7`. The bounded implementation
integrated via normal merge commit `df072540cea6ae458ecd0592c6cf2b1fe69cee0d`
with the accepted tree `c5249a2086038c6b9174f855c1718fee24088464`.
All five [main CI jobs](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/45833490849)
passed. The [integration record](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/15#issuecomment-7194046442)
keeps issue #15 open in slot 1 and retains the CI-01 evidence separately.

Structural preparation metrics and raw lineage, finalized lineage and
correlation record `parser_provenance`. Comparison exposes the same producer
record as `structural_parser_provenance`. It has `engine` (`markdown-it-py`),
`distribution_version` (installed distribution metadata), `preset`
(`commonmark`), `enabled_extensions` (`["table"]`), `mode`
(`structural-v1`), integer `contract_version` (1), and ascending effective
`heading_levels`. Preparation uses the same configuration for parsing and
evidence. Readers check supported configuration and provenance agreement
without replacing a producer's version with the current installation.

The structural preparation, lineage, correlation and comparison sidecar
schemas advance to v2. Legacy schemas remain unchanged. A v2 reader rejects
older structural sidecars or missing or incompatible provenance. Retain
historical evidence and use its original implementation and recorded
environment for historical replay where available. For v2 evidence, run
again from verified inputs in a new structural output directory and retain
both runs. Roll back operationally by selecting legacy mode and its separate
output root. Parser provenance is excluded from existing event identity
algorithms.

The Windows wheel comparison exercised markdown-it-py 3.0.0, 4.2.0 and
4.3.0. It found the same candidate selection, spans, payloads, source IDs,
report IDs, survivor keys and run-local navigation on the frozen fixture.
The declared minimum `markdown-it-py>=3` stands. This evidence covers the
three tested versions and the frozen fixture.

**Remaining G2 decision.** Review source coverage and explain all inclusions
and exclusions on the intended inputs. Disposition reserved Chronicle
framing in that scope, then verify stable locators, identities and replay.
Verify temporal roles and evidence locators, including assigned ordering
dates and explicit unknowns, under the separate TIME-01 work. The maintainer
must record G2 acceptance. CI-01 source import isolation remains separate.

**Acceptance.** Attribute every source line to a recorded span or exclusion.
Preserve source hashes. At default levels the candidate should emit only Alpha
and the mixed-script section, with Empty counted and explicit diagnostics for
the preamble/frontmatter and the excluded boundary types. Recheck configured
h3, LF/CRLF, duplicate headings, malformed and nested fences, and source-
to-report-to-survivor navigation. Replay the candidate twice through the
existing runner with verified source and installed origins. Require stable IDs
and links per selected mode, a reviewed identity delta across modes, full
suite and governance results, and exact-candidate CI. **ACCEPT** the
characterization for review of the bounded slice. **REVISE** G2 pending that
implementation and its qualification.

TIME-01 and NLP-01 remain queued. The temporal follow-up uses a
sidecar distinguishing occurred, published, observed, recorded, retrieved and
assigned dates, each with a locator or explicit unknown. Characterize
normalization and phrase matching for Persian and English, including yeh,
kaf and ZWNJ, using independently labeled fixtures. Record offset effects.
Evaluate original keywords against the deterministic candidate before
considering BM25/TF-IDF or POS/NER.

**Exit gate.** Explain every in-scope inclusion and exclusion, account for all
meaningful source content and verify original bytes, locators and replay.
Document identity and schema compatibility for any changes. Assigned dates
remain identifiable as ordering metadata. Freeze taxonomy, annotation rubric,
thresholds and baselines for Phase 3. Promote temporal and multilingual
follow-ups to issues when their interfaces are characterized.

## Phase 3 — Corpus acceptance

**Gateway.** [G3 Corpus](#acceptance-gateway-matrix).

**Entry.** CORP-01 [#16][i16] is queued. Preparation is limited to public or
synthetic rubric and blinded annotation design. Real-corpus work requires
explicit slot admission, the applicable #15, TIME-01 and NLP-01 decisions,
and authorization of the local inventory.

**Work.** Use the [Flowers acceptance report](../../WordHorrorStories/flowers/ACCEPTANCE_02.md)
as the starting evidence. Review preambles, contextual titles and source/date
semantics. Complete multilabel gold and review duplicate, qualification and
contradiction candidates within the declared scope. Record precision, recall,
F1, per-label support, coverage and disagreements.

**Exit gate.** Record separate G3-core deterministic and G3-full semantic
verdicts against their frozen contracts below. Record unknowns, denominators and reproducibility evidence. Keep
restricted sources and row-level derivatives local. Record semantic acceptance
and publication clearance as separate decisions.

## Phase 4 — References and ontology

**Gateway.** [G4 Ontology](#acceptance-gateway-matrix).

**Entry.** Start from verified survivors, existing links and provenance
sidecars. The checkout has a manual-merge candidate under
`inputs/chatgpt-chronicle/markdown/` and historical copies. Verify the intended
revision, digest, and authorization before selecting the comparison input.

**Work.** Deliver Phase 9c references and secondary navigation on existing
identity contracts, with source and cross-topic locators. Compare automated
and manual output for omissions, dates, titles, ordering, sources and
duplicate handling. Record disagreements as comparison evidence. Populate
Phase 13–17 project-level instances from existing provenance. Review an
explicit compatibility decision for individual events, concepts, `mentions`
and `derived_from` following the [Phase 15 design](../PHASE15_PROJECT_SEMANTIC_ONTOLOGY_DESIGN.md)
and measured NLP evaluation.

**Exit gate.** All references resolve uniquely to a survivor or verified
source, with repeatable references and no competing event identity contract.
Manual comparison is evidenced or explicitly BLOCKED. Instance population
passes mapping and provenance checks. A schema decision precedes new semantic
relations and carries its own migration and compatibility evidence.

## Phase 5 — Product stabilization

**Gateway.** [G5 Release](#acceptance-gateway-matrix).

**Entry.** The deterministic release candidate has a declared supported
workflow and synthetic fixtures. SEC-01 [#17][i17] owns slot 3. SAFE-01
[#18][i18] is READY pending documented SEC-01 exit and separate admission.

**Work.** Bound topic-runner execution with configurable deadlines, capped
diagnostics, explicit results and platform-tested cancellation/cleanup. Verify
public refs, dependencies, workflows and release artifacts. Define the minimum
installed Chronicle workflow, with a documented entry point and compatibility
for existing wrappers. For DOCX, implement atomic output, resolve flattener
dependencies and experimental flags, and test capability reporting and the
[TraceLedger boundary](../TRACELEDGER_INTEGRATION_CONTRACT.md) with a real
external consumer before claiming that integration.

SEC-01 records a coverage matrix separating the extension-filtered worktree
credential scanner from reachable refs/history, SAST and dependency
advisories. Record exact refs and release assets, tool/version/scope,
justified suppressions, Actions and dependency provenance, wheel/sdist
contents and SBOM/checksum feasibility. Publish redacted findings and
coverage limits. CLI-01 and CI-01 remain separate queued v0.2 work.

SAFE-01 must locate the final commit point across save, validation and
subsequent TOC updates. Stage destination-mutating TOC work before the
commit point or scope the atomicity claim explicitly. Verify pre-commit
byte preservation, post-commit errors, cleanup ownership and overwrite,
symlink, locking and concurrency behavior through installed API and CLI.

### EXEC-01 admission proposal (2026-11-26)

**Verified baseline.** `tools/run_topic_report.py::run_stage` synchronously
captures both streams in memory via `subprocess.run`, concatenates decoded
output and appends it to the requested log. Stages return `exit_code` and
`output`. The runner reports stage codes and verdicts in its run artifacts.
`pipeline/chain.ps1::Invoke-ChronicleStage` buffers merged native diagnostics
and records stage exits. Neither path supplies a deadline or a coordinated
cancellation result. The Windows synthetic probe at the MD-01 baseline let a
2.25 s sleeper complete successfully after 2.41 s, captured 1,100,000 ASCII
bytes from each stream, waited for an inheriting child to finish, and observed
the finite worker complete after the supervisor was terminated. Abrupt
supervisor termination is one failure case. Cooperative cancellation, Ctrl-C
and Linux tree teardown remain qualification cases. GitHub's all-state issue
inventory and EXEC-01 search returned no owner issue. Slot 2 remains vacant.

**Proposed contract.** Scope to a shared local stage boundary for the topic
runner and its PowerShell child stages. Use a typed policy with deadline,
termination grace, per-stream byte limits and cancellation input. Give each
stage a terminal status (success, nonzero exit, timeout, cancelled,
launch failure or cleanup failure), optional native exit code, elapsed time,
bounded stdout/stderr with byte counts and truncation, and cleanup outcome.
Record the triggering timeout or cancellation even if cleanup fails. Define
precise precedence for a completion/cancel race using a monotonic clock and
one terminal transition. Keep existing exit-code consumers and CLI
nonzero failure behavior through an explicit compatibility mapping. Persist
the failed run and stage reason, skip dependent stages, and give each attempt
its own output directory so prior successful artifacts survive.

Drain both streams during execution at bounded memory cost, continuing to
drain discarded bytes so the process cannot deadlock on a full pipe. Include
PowerShell's internal diagnostic buffer and disk logs in the bound. On Linux,
launch an owned session/process group, signal group termination, escalate to
kill after grace, close streams and reap the direct child. Qualify ordinary
descendants and define the support limit for detached descendants that escape
the group. On Windows, use an owned Job Object with kill-on-close and establish
assignment before child code can spawn descendants. Qualify nested-job launch
and surface ownership/launch failure explicitly. Avoid PID-only tree cleanup.

**Acceptance.** Keep the G5 thresholds below verbatim. Exercise normal,
nonzero, hung, noisy, descendant-held pipes, cancellation, failed process
launch and lost ownership through the public run entry point. Verify terminal
artifacts, absence of live owned fixture processes, and byte-identical prior
outputs. **BLOCKED** for execution until explicit slot-2 admission and issue
authorization.

### SAFE-01 preparation (2026-11-26)

**Verified by inspection.** `wordpipe/orchestration/pipeline.py` calls
`finalize_step`, which passes the destination to `DocxDocumentWriter.write`
and then cleans its working path. The later optional `toc_step` receives the
final output path. A configured updater can mutate that path and report a
warning after the direct save. This leaves a write and a path-mutating TOC
operation before the pipeline has reached its final state.

**Proposed transaction.** Create an exclusively owned, unique sibling .docx
in the destination directory. Close any creation handle before opening it for
save or TOC on Windows. Save, check ZIP integrity and reopen the DOCX with
required content assertions, perform every required TOC mutation on that
sibling, then reopen and validate the actual publication bytes again. With
all handles closed, publish once using same-filesystem atomic replacement.
Represent missing optional TOC capability explicitly. A configured required
TOC failure aborts before replacement. Review the warning-to-failure change
in the existing reports and CLI. Emit final-path success only after replace.

Preserve normal overwrite semantics with atomic last successful replace for
independent writers. Propose rejecting input/output aliases and destination
symlinks, subject to compatibility review. Verify permissions and destination
locks on each platform and scope the contract to supported filesystem
semantics. Before replace, errors leave an existing destination byte-identical.
After replace, cleanup or telemetry errors report committed output and a
secondary diagnostic without rollback. Delete only artifacts owned by the
attempt and retain the primary error if cleanup fails.

**Acceptance.** After documented SEC-01 exit and separate admission, qualify
the installed `wordpipe` CLI and public DOCX API in clean exact-wheel Windows
and Linux environments. Verify new output, overwrite, concurrent writers,
alias/symlink policy, permission and Windows lock behavior, and inject
save, reopen, TOC, replace and cleanup/event failures with hash checks and
observable commit state. Verify the actual configured TOC capability where
supported and document platform-specific unsupported cases. **BLOCKED** for
execution pending SEC-01 exit and admission under issue #18.

**Exit gate.** Complete the v0.2 checklist below. WordPipe DOCX earns its own
readiness decision through installed API and CLI tests on Windows and Linux,
failure preservation, honest flag and flattener support, and documentation of
the supported contract. External TraceLedger acceptance requires its own
recorded consumer result.

## Phase 6 — Knowledge intelligence

**Gateway.** [G6 Knowledge](#acceptance-gateway-matrix).

**Entry.** Reference/provenance and schema decisions are recorded. Corpus
evaluation supplies defensible gold for the intended extraction scope.

**Work.** Evaluate provenance-backed concepts and relationships, citations and
claim lifecycle. Preserve historical claims and qualify, contradict, support,
retract or supersede them through explicit evidence. Measure Chronicle at
100, 1,000, 10,000 and 100,000 events before choosing a rebuildable local
SQLite/FTS projection. Keep Markdown, JSON and sidecars authoritative.

**Exit gate.** Independent evaluation verifies claim and relation precision,
evidence resolution and temporal scope against declared targets. Any local
index reproducibly rebuilds from pinned artifacts and meets a measured need.

## Phase 7 — Optional AI research

**Gateway.** [G7 AI](#acceptance-gateway-matrix).

**Entry.** [#9][i9] requires accepted #8 fidelity and reusable runtime/fidelity
qualification in [upstream #40][a40] and [#41][a41]. [#10][i10] can prepare gold and a deterministic baseline
offline. Real Jev calls require the [upstream adapter][a44] and separate authorization.
NCM compression-routing evaluation also requires #9. [#11][i11] waits for the
required #8–#10 and [upstream candidate evaluation][a45].

**Work.** Benchmark NCM against selected extraction with validated fallback.
Measure Jev as advisory only by using independently annotated multilabel
fixtures, then evaluate the combined task replay with identical inputs and
candidate pools. WHS owns corpora, fixtures, evidence and evaluation.
The agents project owns reusable runtimes, provider adapters and transport.

**Exit gate.** Apply the quantified G7 quality and cost gates across each issue's declared
population. Record accepted outputs, failures, abstentions, fallback, latency,
memory and total cost. Record GO, REVISE or NO-GO for each experiment.
Any adoption requires separate maintainer approval and qualified delivery
contracts. Deterministic release readiness proceeds independently.

## Quantified gateway contracts

The maintainer approved the numerical floors below on 2026-11-20 as
provisional planning baselines only. Preregister before tuning/scoring.
The first executed measurement for each quantified work package triggers a
mandatory documented re-baseline review: retain the original numbers, measured
baseline, environment, corpus/tokenizer identity, proposed changes (or explicit
retention), rationale, and maintainer disposition. Hardware-sensitive PERF-01
and corpus/tokenizer-sensitive G7 values must be reviewed explicitly. Do not
silently drift or retroactively turn a failed evaluation into ACCEPT. A changed
threshold after holdout exposure requires new independent holdout evidence;
retain all original verdicts and evidence. Record fixture digests, versions,
machine, denominators, failures and raw measurements.

- G1 / #8: fresh holdout >= 30 cases, >= 20 valid answerable in-budget
  cases and >= 10 expected-refusal cases (stale, ambiguous, invalid or
  unanswerable inputs). Independently label each input class before
  scoring. >= 95% verified delivery among valid cases (selected or raw),
  100% correct refusal among expected-refusal cases, 100% protected facts
  and IDs in delivered packets, 100% valid anchors, zero unsupported facts.
  Count valid budget refusals as coverage failures and their applicable
  required facts as missing in full-population metrics. Proposed efficiency
  floor: >= 20% median complete-packet and reread token reduction versus raw
  over valid cases, including raw fallbacks; refusals receive zero savings
  credit. Use target tokenizer or label estimates.
- G3-core / v0.2: frozen public/synthetic deterministic fixtures; 100%
  meaningful source-content accounting, verified locators, reproducible output
  and explicit assigned/unknown dates. Characterize rule behavior, not semantic
  correctness; no real Flowers gold or IAA prerequisite.
- G3-full / v0.3: CORP-01 and NLP-01 require two authorized blinded annotators
  independently labeling the same frozen multilabel items; at least one
  independent of the classifier implementation. Independent adjudicator
  resolves all disagreements. Report pre-adjudication per-binary-label
  Cohen's kappa >= 0.70 and macro kappa >= 0.75, raw agreement and support.
  Labels with undefined kappa or fewer than 10 positives or 10 negatives are
  unqualified; report them explicitly. Every predeclared protected label
  must qualify before acceptance of the declared scope. On adequately supported predeclared
  scope require macro F1 >= 0.80, micro F1 >= 0.85 and recall >= 0.90 for
  predeclared protected labels. No qualified reviewers or authorization =
  BLOCKED for G3-full only. Keep restricted material local.
- G4-core / v0.2: unique resolvable references, stable identities, verified
  provenance and compatible existing project-instance mappings. Manual
  comparison is a comparison, not truth. If unavailable, record BLOCKED
  for that comparison, provide synthetic parity and obtain explicit
  maintainer scope approval. G4-full / v0.3 requires G3-full, evaluated
  concepts/relations, versioned schema and migration compatibility.
- G5 / EXEC-01: test normal, hung, noisy and child-spawning stages on
  Windows and Linux. Configurable deadline (test at 2 seconds); terminal
  timeout/cancel verdict and owned child tree terminated within 5 seconds
  after deadline or cancel request. Cap captured stdout/stderr at 1 MiB
  each with explicit truncation. Preserve previous valid outputs and
  non-success run verdict; no orphan fixture processes.
- G5 / CI-01 and CLI-01: existing Ubuntu jobs are baseline, not final
  qualification. Require fresh exact-candidate Windows and Linux
  wheel-installed complete Chronicle runs and governance checks.
  CI-01 platform coverage and source-test import isolation are P1 and v0.2
  blockers; its optional profile split and duplicate scanner remain P2 and
  may be explicitly deferred. The 2026-11-20 local review initially imported
  Chronicle from another checkout and failed four tests; the corrected import
  path passed all four. Require source-test session startup to resolve
  `wordpipe.__file__` and all other imported repository packages under test
  (including package/module origins where applicable) inside the intended
  checkout, using resolved paths, and fail loudly on mismatch with expected
  and actual origins. Add a deliberate foreign-checkout regression; do not
  silently repair imports. Separately, installed-wheel tests must assert
  their origins are in the intended clean installation, not a source checkout.
  DOCX-01 must document actual COM/XML capabilities; COM is not a Linux
  Chronicle requirement. DOCX readiness is independently qualified.
- G6 / PERF-01: deterministic pinned 100, 1k, 10k and 100k-event corpora
  (1 KiB mean body, fixed seed, documented duplication/theme mix);
  three cold runs per size on documented Linux runner (>= 2 vCPU, 8 GiB).
  Measure ingest-to-merge latency and peak process-tree RSS, full-stage
  metrics and failures. Proposed 10k-event floor: median <= 60 seconds,
  max RSS <= 512 MiB. Record 100k completion or resource-limit failure.
  PERF-01 ACCEPT requires complete characterization and 10k budget pass;
  otherwise REVISE/DEFER. STORE-01 requires measured query friction.
- G7: preserve #9 >= 30% median consumer-token saving vs selected
  extraction on compressible accepted cases with full-population results;
  #11 >= 20% median end-to-end consumer-token saving vs B across all
  cases including fallback and no critical-task degradation. For #10 propose
  >= 5 percentage-point macro F1 improvement vs frozen normalized keyword
  baseline on held-out cases (abstentions count as misses) and no protected-label
  recall degradation. For each experiment, require cost per independently
  accepted result no higher than its comparable baseline. For free or
  unmeasured baseline costs, require an explicit
  spending ceiling and approved tradeoff before scoring, no cost-saving
  claim. Zero known accepted critical errors, independent adjudication,
  authorization and explicit adoption decision remain mandatory for all arms.

## Acceptance gateway matrix

A decision records the gateway, candidate revision and scope, evidence links,
reviewer, verdict and remaining conditions. Use **ACCEPT** when the stated
criteria pass, **REVISE** when evaluation identifies an actionable shortfall,
**BLOCKED** when required evidence or authorization is unavailable, and
**DEFER** for a deliberate postponement. Record thresholds, denominators and
exceptions with the reviewed evidence. An issue-level PASS, REVIEW or GO
remains scoped to that evidence. An engineering merge leaves research verdicts
subject to the independent gateway review.

| Gateway | Required evidence for ACCEPT | Owner and current decision |
|---|---|---|
| G0 — Governance | Reconcile the root roadmap, the 24 unique work packages and open GitHub issues. Assign each tracked scope one owner issue, retain the historical evidence and pass repository governance on the integrated candidate. | Maintainer, GOV-01 [#14][i14]. ACCEPT; [#19][pr19] merged; #14 closed. |
| G1 — Fidelity | Freeze the authorized candidate and contract before preparing a new independent holdout. All delivered packets retain 100% of protected facts and required IDs, have verified anchors and contain zero unsupported facts. Record delivery, raw fallback, refusals and full-population coverage separately. Pass the predeclared coverage and efficiency criteria and reproduce results with canonical artifacts preserved. | Context-export maintainer and independent evaluator, [#8][i8]. **REVISE** after frozen B2. B3 **DEFERRED**. |
| G2 — Parsing | Account for included and excluded content without unexplained loss. Verify fences, preambles, identity, replay and stable line mappings. Record temporal roles and provenance, including assigned and unknown dates. | Chronicle maintainer, MD-01 [#15][i15] and TIME-01. **REVISE.** Bounded opt-in implementation accepted and integrated. Intended-input and temporal-role qualification remain. |
| G3 — Corpus | Apply G3-core deterministic fixture criteria for v0.2 and G3-full independent IAA and quality criteria for v0.3. Record restricted Flowers corpus and publication decisions separately. | Corpus reviewer, CORP-01 [#16][i16] and NLP-01. Flowers semantic evidence remains REVIEW. |
| G4 — Ontology | For v0.2, verify unique source/survivor references, stable identities and provenance, schema compatibility and mapped project instances. Record the manual comparison disposition. For full G4, review the versioned schema, evaluated concepts and relations, and migration and compatibility evidence. | Chronicle and ontology maintainers, CORE-01, ONT-01 and ONT-02. Evidence pending. |
| G5 — Release | Verify wheel-installed Chronicle, EXEC-01 liveness and failure recovery, current security review, CI-01 import-origin isolation and CLI-01 exact-candidate Windows and Linux acceptance. Track DOCX capability and external TraceLedger acceptance independently. | Release maintainer, EXEC-01, SEC-01 [#17][i17], CLI-01 and CI-01; DOCX-01 separately. Qualification pending. |
| G6 — Knowledge | Independently evaluate evidence resolution, temporal scope, claim and relation quality against predeclared targets. Preserve earlier claims and record qualifications, contradictions, retractions and supersession explicitly. Apply the quantified PERF-01 budget before performance acceptance. | Knowledge maintainer and independent evaluator, CLAIM-01, CITE-01, PERF-01 and conditional STORE-01. Entry gated. |
| G7 — AI | Qualify the runtime or adapter for the intended use. Obtain applicable data and execution authorization. Independently evaluate all cases, including rejected and fallback cases. Record quality, latency, memory and cost against the deterministic baseline and apply the explicit issue-specific G7 floors above. | Experiment maintainers and independent evaluator, [#9][i9]–[#11][i11]. NCM inference and the combined benchmark are **BLOCKED**. Jev has offline preparation available; live execution requires separate authorization. |

## Proposed release boundaries

| Target | Scope | Gate evidence |
|---|---|---|
| v0.1.x | Foundation and reliability fixes. | G0 and applicable regression checks. |
| v0.2 | Stable deterministic Chronicle and provenance-bound context export. | G0, G1, G2, G3-core, G4-core and G5. Full semantic corpus/ontology qualification excluded. |
| v0.3 | Versioned semantic ontology and independently evaluated claim extraction. | G3-full, G4-full and applicable G6 evidence. |
| v0.4 | Search, knowledge lifecycle and qualified integrations. | G6, measured query need and applicable external consumer acceptance. |
| v0.5 | Optional qualified AI assistance. | G7 with an explicit adoption decision. |

These are planning targets. Record evidence at the candidate SHA before any
tag or release decision. G3-full, G4-full, G6, G7, restricted Flowers semantic acceptance and the
independent WordPipe DOCX readiness decision sit outside v0.2.

### Proposed deterministic v0.2 checklist

- [x] Core ingest, merge, categorize and index exist.
- [x] Stable survivor identities and navigation exist.
- [x] Structured run evidence exists.
- [x] Baseline Windows and Linux hosted CI are verified at the starting main revision.
- [x] Baseline wheel build and installation checks exist.
- [ ] Context-pack fidelity and coverage pass Phase 1.
- [ ] Complete-document extraction passes Phase 2.
- [ ] Temporal semantics are characterized and distinguish inferred and assigned dates.
- [ ] G3-core deterministic synthetic fixture acceptance supports the declared release scope. Real Flowers semantic evaluation and IAA are G3-full/v0.3.
- [ ] Core G4 references, compatible project instances and the manual comparison disposition are evidenced. If the authorized comparison is blocked, record its release impact and obtain a maintainer scope decision.
- [ ] EXEC-01 deadline, cancellation, diagnostic bound, child cleanup and failure recovery pass on supported platforms.
- [ ] Public release scope and dependency/publication review pass [#17][i17].
- [ ] CI-01 source-test origin assertions and foreign-checkout regression pass; CLI-01 clean installed Chronicle workflow passes with verified installation origins on Windows and Linux at the release candidate.

## Backlog activation and synchronization

Counts (not GitHub issue numbers):

| Bucket | Count |
|---|---:|
| Research issues #8–#11 | 4 |
| Engineering issues mapped to WPs (#14–#18) | 5 |
| WPs requiring future GitHub issues on admission | 15 |
| **Total tracked items** | **24** |

The GitHub issue column is the WP-to-issue mapping. To-create means
search and reuse before opening an issue; no number is reserved.
Planning statuses reflect the recorded G0 acceptance and queue admission; research and release qualification remain open. The repository
maintainer (SoloMidMiram) is accountable for every work package; the
responsible roles below are proposed, not confirmed assignees. Independent
reviewers and external owners must be identified and accept their roles
before qualification. The [optimization map](OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md) holds
technical evidence and historical remediation.

| ID | Priority | Work package | GitHub issue | Responsible role | State and activation or acceptance contract |
|---|---|---|---|---|---|
| GOV-01 | P0 | Roadmap and evidence reconciliation | [#14][i14] | Maintainer | ACCEPT / closed. [#19][pr19] merged with history preserved; slot 1 released. |
| MD-01 | P1 | Structure-aware Markdown ingestion | [#15][i15] | Chronicle implementer | Admitted in slot 1. Verify fenced headings, source coverage, stable locators and replay (G2). |
| TIME-01 | P1 | Temporal evidence and date semantics | To-create | Chronicle implementer | Queued. Start after MD-01 establishes spans. Verify all date roles, locators and explicit unknowns (G2). |
| CORP-01 | P1 | Flowers semantic corpus acceptance | [#16][i16] | Corpus lead + independent reviewers | Queued. Prepare rubric offline. Score after G2 decisions, frozen taxonomy and authorization of the local inventory (G3). |
| NLP-01 | P1 | Multilingual normalization and taxonomy | To-create | NLP lead + reviewer | Queued. Define annotation, then measure normalized Persian/English keyword and phrase behavior, offsets and per-label results (G2, G3). |
| CORE-01 | P1 | Reference builder and manual comparison | To-create | Chronicle implementer | Queued. Reuse verified survivor keys for Phase 9c. Require resolvable links, repeatability and an evidenced or explicitly blocked comparison (G4). |
| ONT-01 | P1 | Project ontology population | To-create | Ontology implementer | Queued. Map verified Phase 13–17 runs to existing project entities. Verify stable IDs, schema compatibility and evidence references (core G4). |
| ONT-02 | P1 | Semantic concepts and relationships | To-create | Ontology lead + reviewer | Gated by ONT-01, NLP-01 and the Phase 15 schema decision. Verify versioned migration and evidence-backed relations (full G4). |
| SAFE-01 | P1 | Atomic DOCX publication | [#18][i18] | DOCX implementer | Ready after SEC-01 in slot 3. Prove failure preservation and cleanup through installed paths on Windows and Linux (DOCX readiness). |
| EXEC-01 | P1 | Bounded execution and cancellation | To-create | Runtime implementer | Queued. Define stage process contracts and verify deadlines, bounded diagnostics and cleanup on supported platforms (G5). |
| SEC-01 | P1 | Public repository and dependency audit | [#17][i17] | Release/security maintainer | Admitted in slot 3. Record current ref, dependency, workflow and release-artifact coverage and disposition (G5). |
| DOCX-01 | P2 | Flattener and capability contracts | To-create | DOCX implementer | Queued. Characterize supported COM/XML dependencies and experimental flags. Verify installation and capability reporting (DOCX readiness). |
| INT-01 | P2 | TraceLedger consumer validation | To-create | Integration lead + external consumer | Queued. Require a real available consumer and verify library, EventSink and capability contracts (external consumer acceptance). |
| CLAIM-01 | P2 | Claim lifecycle and contradictions | To-create | Knowledge lead + reviewer | Gated by grounded references and the semantic schema decision. Verify evidence, temporal scope and historical preservation (G6). |
| CITE-01 | P2 | Research citation model | To-create | Knowledge implementer | Queued. Build on CORE-01 source locators. Verify per-claim citations resolve and survive replay (G6). |
| PERF-01 | P2 | Chronicle scaling benchmark | To-create | Benchmark implementer | Queued. Measure wall time and peak memory at 100, 1,000, 10,000 and 100,000 events on pinned fixtures (G6). |
| STORE-01 | P2 | Rebuildable SQLite projection | To-create | Storage implementer | Gated by demonstrated query friction. Use PERF-01 characterization where relevant. Require reproducible rebuilds from canonical artifacts and measured benefit (G6). |
| CLI-01 | P1 | Installed Chronicle CLI | To-create | Release implementer | Queued. Exercise a clean wheel install and documented complete Chronicle flow on Windows and Linux, retaining wrapper compatibility (G5). |
| CI-01 | P1/P2 | CI profiles and duplicate scanner | To-create | CI/release implementer | Queued. P1 platform qualification and test-import hermeticity block v0.2/G5: assert intended source/install origins and fail on foreign checkout; verify deliberate mismatch regression. P2 profile split and duplicate scanner optional with scope decision. Preserve governance checks. |
| REF-01 | P3 | Conditional refactoring and retirement | To-create | Subsystem maintainer | Deferred. Characterize consumer use before wrapper retirement. Require a third-adapter coupling or unsafe schema evolution before decomposing the runner. |
| #8 | P1 | Deterministic context fidelity | [#8][i8] | Context lead + independent evaluator | G1 REVISE after frozen B2. B3 DEFERRED pending [re-entry evidence](#b3-re-entry). |
| #9 | P1 | NCM fidelity | [#9][i9] | Research lead + upstream runtime owner | BLOCKED for genuine inference. Require G1 and upstream runtime/fidelity qualification (G7). |
| #10 | P1 | Jev shadow classification | [#10][i10] | Research lead + independent evaluator | Live work gated. Prepare independent classification fixtures offline. Require upstream adapter qualification and authorization for live work (G7). |
| #11 | P1 | Combined benchmark | [#11][i11] | Research lead + independent evaluator | BLOCKED on #8–#10 and applicable upstream evidence. Reuse identical tasks and candidate pools (G7). |

## Review cadence and risk register

Review active gates on every evidence/head change, at PR acceptance, at release
candidacy and at least weekly. BLOCKED requires missing prerequisite, owner,
next check and slot decision within two business days. Within five business
days the maintainer records an unblock plan, explicit non-release deferral,
or continued mandatory-release blocker. Review unresolved blockers weekly;
no automatic waiver or ACCEPT.

| Risk / trigger | Mitigation | Owner |
|---|---|---|
| No independent annotators or low IAA (G3) | Block G3-full, revise rubric or recruit authorized reviewers; G3-core may proceed. | Corpus lead / maintainer |
| Source tests import another checkout (G5/CI-01) | Fail at session startup on incorrect resolved import origins; test the deliberate mismatch, and independently verify clean wheel installation origins. | CI/release lead |
| Linux fails or Windows-specific code (G5/DOCX-01) | Separate product scopes; fix mandatory CI-01 coverage; qualify actual DOCX capabilities independently. | Release and DOCX leads |
| Holdout contamination (#8) | Retain failure as regression; freeze candidate, independent fresh holdout, hashes and roles. | Context lead / evaluator |
| NCM runtime unavailable (#9) | Escalate to upstream owner; preserve harness, no live inference; defer AI without blocking v0.2. | Research lead / maintainer |
| Duplicate tracking (G0) | Stop duplicate creation, reuse owner issue, update canonical plan and references together. | Maintainer |
| Liveness/performance ceiling exceeded (G5/G6) | Preserve outputs, record failure and measured bounded remediation; no silent acceptance. | Runtime/benchmark lead |

Lower-priority work includes organizing tests as affected subsystems change,
auditing absolute paths, and modeling labor notes, reports and plans when
stable mappings are available. Memorilla, graph or vector servers, web UI,
deployment orchestration, autonomous agents, model fine-tuning, automatic
semantic deduplication and full rewrites stay deferred pending demonstrated
need and a separate decision.

When work becomes actionable, search existing issues, open or reuse one
bounded issue, include its planning ID, dependency and exit criteria, and link it here in
the same planning iteration. When a gate changes, update the matrix, the
owner issue and the root narrative with the exact evidence and disposition. Preserve historical
results. Close issues against their documented acceptance. Use plain `Refs`
links for research PRs that deliver evidence while a quality gate stays open.

[pr2]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/2
[pr6]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/6
[pr7]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/7
[pr12]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/12
[pr19]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/19
[pr13]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/13
[main-ci]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/44562536617
[pr13-ci]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/44574498588
[pr13-push]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/44574480694
[i8]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/8
[i9]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/9
[i10]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/10
[i11]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/11
[i14]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/14
[i15]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/15
[i16]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/16
[i17]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/17
[i18]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/18
[a40]: https://github.com/SoloMidMiram/md-mdc-Agents-Skills-MCPs-Kagent-A2A-SubAgents/issues/40
[a41]: https://github.com/SoloMidMiram/md-mdc-Agents-Skills-MCPs-Kagent-A2A-SubAgents/issues/41
[a44]: https://github.com/SoloMidMiram/md-mdc-Agents-Skills-MCPs-Kagent-A2A-SubAgents/issues/44
[a45]: https://github.com/SoloMidMiram/md-mdc-Agents-Skills-MCPs-Kagent-A2A-SubAgents/issues/45
