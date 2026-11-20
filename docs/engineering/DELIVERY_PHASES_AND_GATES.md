# WHS delivery phases and acceptance gates

The [root roadmap](../../ROADMAP.md) is the entry point for delivery order.
This plan defines delivery phases, acceptance gateways, the issue map and
release milestones. GitHub issues own the active work and its acceptance
checklists. Dated experiment and corpus reports own their measurements.
Delivery phase numbers and gateway IDs are scoped to this plan. The root
roadmap retains the original Project Phase 9c, Phases 13–17 and goal IDs.

## Authority and freshness

GOV-01 = issue [#14][i14], implemented by existing draft [PR #19][pr19].
Do not open another governance issue or PR. This file is the sole authority
for phase execution, gateways, work-package mapping, release readiness and
risks. PHASE_EXECUTION_PLAN.md, ACCEPTANCE_GATE_MATRIX.md, ISSUE_ROADMAP_MAP.md
and RELEASE_READINESS.md are unnecessary: their proposed roles are already
covered here. ROADMAP.md owns strategic direction and dated history,
OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md owns technical debt and historical
evidence, and REPO_MAP.md owns navigation. The maintainer owns all four.
Check these documents and search GitHub before adding a tracking surface;
record a supersession and redirect if authority ever changes.

Planning statuses and thresholds are provisional until GOV-01 acceptance.
A fresh read on 2026-11-20 confirms the nine existing issues are open;
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
| Context export | PR [#13][pr13] is open and draft at `bd31c0470080`. Both [PR][pr13-ci] and [push][pr13-push] runs passed. B1 retained 43/45 critical facts overall, and 21/22 in delivered holdout packets. Median estimated GPT-2 token reduction versus raw was 46.07%. | **REVISE** under [#8][i8]. Preserve B1 and the exposed holdout failure as evidence. |
| Release boundary | The package metadata says `0.1.0`. Proposed v0.2 is the deterministic Chronicle release. | Certify v0.2 against the checklist below. Track WordPipe DOCX readiness independently. |

At the baseline, seven PRs had merged, PR #1 had closed without merging, and
PR #13 was the sole open PR at that earlier baseline; #19 is now also open. B0's original eight-case NCM-pilot metrics and
its replay on #13's 24-case benchmark describe different datasets.

## Parallel work and dependencies

The primary sequence is context fidelity, document understanding, corpus
acceptance, references and ontology, product stabilization, knowledge
intelligence, then optional model research. B2 can use the existing verified
generic Markdown run while the production adapter is characterized. Public
release assurance [#17][i17] and atomic DOCX [#18][i18] can start independently.
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
| Governance | GOV-01 [#14][i14] | Review and integrate [#19][pr19]; then admit READY MD-01 [#15][i15] in this slot. |
| Research fidelity | [#8][i8] / [draft PR #13][pr13] | Preserve B1, freeze B2 and evaluate a fresh independently adjudicated holdout. |
| Independent hardening | SEC-01 [#17][i17] | Complete the public release audit, then admit SAFE-01 [#18][i18] to this slot. |

MD-01 [#15][i15] remains READY, reserved as the successor to GOV-01 in slot 1.
If GOV-01 becomes BLOCKED and releases its slot, record that decision before
admitting MD-01. No silent deferral.
CORP-01 [#16][i16] can prepare its rubric offline once admitted. Technical
independence allows work to start with an available slot. Gated, queued and
deferred entries in the [issue map](#backlog-activation-and-synchronization)
are outside the current execution queue.

## Phase 1 — Context fidelity

**Gateway.** [G1 Fidelity](#acceptance-gateway-matrix).

**Entry.** Pin PR #13's B1 candidate, fixtures, metrics and source contracts.
Retain the existing trusted receipt, digest, identity, survivor and anchor
checks.

**Work.** Under [#8][i8], convert the nonadjacent qualification miss into a
regression. Compare a bounded B2 change that follows explicit references or
expands relevant structural sections, with cases for negation, exceptions
and conflicting statements. Preserve verified raw fallback and refusal.
Tune separately. Freeze the algorithm and configuration before preparing
and independently adjudicating a fresh holdout. Measure complete
packets and any consumer rereads using the target tokenizer where available.

**Exit gate.** All delivered fresh-holdout packets retain 100% of annotated
critical facts and exact required IDs, have verified anchors and contain zero
unsupported facts. Report results across all cases and delivered cases. Freeze
coverage and efficiency criteria before scoring. Classify and count structural
delivery, raw fallback and refusals separately, including expected refusals.
Keep budget refusals in the coverage and applicable fact denominators. Report
estimates and measured usage distinctly. Replay deterministically and verify
canonical artifact hashes. Record ACCEPT or REVISE with report and exact head.
An evidence-only merge can preserve a negative result while #8 stays open.

## Phase 2 — Document understanding

**Gateway.** [G2 Parsing](#acceptance-gateway-matrix).

**Entry.** Use synthetic fixtures and characterize the current generic adapter
and lineage contract. [#15][i15] is ready independently of B2.

**Work.** Compare the current extraction with block-aware Markdown using the
existing parser dependency. Cover fenced headings, blockquotes, nested blocks,
tables, frontmatter, preambles and empty sections. Follow with a temporal
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

**Entry.** [#16][i16] may prepare an offline rubric immediately. Real-corpus
scoring requires the applicable Phase 2 decisions, an authorized local
inventory and independent adjudication.

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
workflow and synthetic fixtures. [#17][i17] and [#18][i18] can proceed earlier.

**Work.** Bound topic-runner execution with configurable deadlines, capped
diagnostics, explicit results and platform-tested cancellation/cleanup. Verify
public refs, dependencies, workflows and release artifacts. Define the minimum
installed Chronicle workflow, with a documented entry point and compatibility
for existing wrappers. For DOCX, implement atomic output, resolve flattener
dependencies and experimental flags, and test capability reporting and the
[TraceLedger boundary](../TRACELEDGER_INTEGRATION_CONTRACT.md) with a real
external consumer before claiming that integration.

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

**Exit gate.** Apply each issue's quality and cost gate across its declared
population. Record accepted outputs, failures, abstentions, fallback, latency,
memory and total cost. Record GO, REVISE or NO-GO for each experiment.
Any adoption requires separate maintainer approval and qualified delivery
contracts. Deterministic release readiness proceeds independently.

## Quantified gateway contracts

The following numerical floors are proposals requiring maintainer approval
and preregistration before tuning/scoring. A changed threshold after holdout
exposure requires new independent holdout evidence. Record fixture digests,
versions, machine, denominators, failures and raw measurements.

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
  Labels with undefined kappa or < 10 positives and < 10 negatives are
  unqualified; report them explicitly. On adequately supported predeclared
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
  CI-01 platform coverage is P1 and a v0.2 blocker; its optional profile
  split and duplicate scanner remain P2 and may be explicitly deferred.
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
  baseline on held-out cases (abstentions count as misses), no protected-label
  recall degradation, cost per independently accepted result no higher
  when comparable. For free or unmeasured baseline costs, require an explicit
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
| G0 — Governance | Reconcile the root roadmap, the 24 unique work packages and open GitHub issues. Assign each tracked scope one owner issue, retain the historical evidence and pass repository governance on the integrated candidate. | Maintainer, GOV-01 [#14][i14]. Review pending in [#19][pr19]. |
| G1 — Fidelity | Freeze B2 before preparing a fresh independent holdout. All delivered packets retain 100% of protected facts and required IDs, have verified anchors and contain zero unsupported facts. Record delivery, raw fallback, refusals and full-population coverage separately. Pass the predeclared coverage and efficiency criteria and reproduce results with canonical artifacts preserved. | Context-export maintainer and independent evaluator, [#8][i8]. **REVISE** after B1. |
| G2 — Parsing | Account for included and excluded content without unexplained loss. Verify fences, preambles, identity, replay and stable line mappings. Record temporal roles and provenance, including assigned and unknown dates. | Chronicle maintainer, MD-01 [#15][i15] and TIME-01. Evaluation pending. |
| G3 — Corpus | Apply G3-core deterministic fixture criteria for v0.2 and G3-full independent IAA and quality criteria for v0.3. Record restricted Flowers corpus and publication decisions separately. | Corpus reviewer, CORP-01 [#16][i16] and NLP-01. Flowers semantic evidence remains REVIEW. |
| G4 — Ontology | For v0.2, verify unique source/survivor references, stable identities and provenance, schema compatibility and mapped project instances. Record the manual comparison disposition. For full G4, review the versioned schema, evaluated concepts and relations, and migration and compatibility evidence. | Chronicle and ontology maintainers, CORE-01, ONT-01 and ONT-02. Evidence pending. |
| G5 — Release | Verify wheel-installed Chronicle, EXEC-01 liveness and failure recovery, current security review, CI-01/CLI-01 exact-candidate Windows and Linux acceptance. Track DOCX capability and external TraceLedger acceptance independently. | Release maintainer, EXEC-01, SEC-01 [#17][i17], CLI-01 and CI-01; DOCX-01 separately. Qualification pending. |
| G6 — Knowledge | Independently evaluate evidence resolution, temporal scope, claim and relation quality against predeclared targets. Preserve earlier claims and record qualifications, contradictions, retractions and supersession explicitly. Apply the quantified PERF-01 budget before performance acceptance. | Knowledge maintainer and independent evaluator, CLAIM-01, CITE-01, PERF-01 and conditional STORE-01. Entry gated. |
| G7 — AI | Qualify the runtime or adapter for the intended use. Obtain applicable data and execution authorization. Independently evaluate all cases, including rejected and fallback cases. Record quality, latency, memory and cost against the deterministic baseline and apply the explicit issue-specific G7 floors above. | Experiment maintainers and independent evaluator, [#9][i9]–[#11][i11]. NCM inference and the combined benchmark are **BLOCKED**. Jev has offline preparation available. |

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
- [ ] CI-01 platform qualification subset and CLI-01 clean installed Chronicle workflow pass on Windows and Linux at the release candidate.

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
All planning statuses are provisional until G0 approval. The repository
maintainer (SoloMidMiram) is accountable for every work package; the
responsible roles below are proposed, not confirmed assignees. Independent
reviewers and external owners must be identified and accept their roles
before qualification. The [optimization map](OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md) holds
technical evidence and historical remediation.

| ID | Priority | Work package | GitHub issue | Responsible role | State and activation or acceptance contract |
|---|---|---|---|---|---|
| GOV-01 | P0 | Roadmap and evidence reconciliation | [#14][i14] | Maintainer | In progress. Integrate [#19][pr19] after the issue map and governance checks agree (G0). |
| MD-01 | P1 | Structure-aware Markdown ingestion | [#15][i15] | Chronicle implementer | Ready, next available slot. Verify fenced headings, source coverage, stable locators and replay (G2). |
| TIME-01 | P1 | Temporal evidence and date semantics | To-create | Chronicle implementer | Queued. Start after MD-01 establishes spans. Verify all date roles, locators and explicit unknowns (G2). |
| CORP-01 | P1 | Flowers semantic corpus acceptance | [#16][i16] | Corpus lead + independent reviewers | Queued. Prepare rubric offline. Score after G2 decisions, frozen taxonomy and authorization of the local inventory (G3). |
| NLP-01 | P1 | Multilingual normalization and taxonomy | To-create | NLP lead + reviewer | Queued. Define annotation, then measure normalized Persian/English keyword and phrase behavior, offsets and per-label results (G2, G3). |
| CORE-01 | P1 | Reference builder and manual comparison | To-create | Chronicle implementer | Queued. Reuse verified survivor keys for Phase 9c. Require resolvable links, repeatability and an evidenced or explicitly blocked comparison (G4). |
| ONT-01 | P1 | Project ontology population | To-create | Ontology implementer | Queued. Map verified Phase 13–17 runs to existing project entities. Verify stable IDs, schema compatibility and evidence references (core G4). |
| ONT-02 | P1 | Semantic concepts and relationships | To-create | Ontology lead + reviewer | Gated by ONT-01, NLP-01 and the Phase 15 schema decision. Verify versioned migration and evidence-backed relations (full G4). |
| SAFE-01 | P1 | Atomic DOCX publication | [#18][i18] | DOCX implementer | Ready after SEC-01 in slot 3. Prove failure preservation and cleanup through installed paths on Windows and Linux (DOCX readiness). |
| EXEC-01 | P1 | Bounded execution and cancellation | To-create | Runtime implementer | Queued. Define stage process contracts and verify deadlines, bounded diagnostics and cleanup on supported platforms (G5). |
| SEC-01 | P1 | Public repository and dependency audit | [#17][i17] | Release/security maintainer | Ready in slot 3. Record current ref, dependency, workflow and release-artifact coverage and disposition (G5). |
| DOCX-01 | P2 | Flattener and capability contracts | To-create | DOCX implementer | Queued. Characterize supported COM/XML dependencies and experimental flags. Verify installation and capability reporting (DOCX readiness). |
| INT-01 | P2 | TraceLedger consumer validation | To-create | Integration lead + external consumer | Queued. Require a real available consumer and verify library, EventSink and capability contracts (external consumer acceptance). |
| CLAIM-01 | P2 | Claim lifecycle and contradictions | To-create | Knowledge lead + reviewer | Gated by grounded references and the semantic schema decision. Verify evidence, temporal scope and historical preservation (G6). |
| CITE-01 | P2 | Research citation model | To-create | Knowledge implementer | Queued. Build on CORE-01 source locators. Verify per-claim citations resolve and survive replay (G6). |
| PERF-01 | P2 | Chronicle scaling benchmark | To-create | Benchmark implementer | Queued. Measure wall time and peak memory at 100, 1,000, 10,000 and 100,000 events on pinned fixtures (G6). |
| STORE-01 | P2 | Rebuildable SQLite projection | To-create | Storage implementer | Gated by PERF-01 or documented query friction. Require reproducible rebuilds from canonical artifacts and measured benefit (G6). |
| CLI-01 | P1 | Installed Chronicle CLI | To-create | Release implementer | Queued. Exercise a clean wheel install and documented complete Chronicle flow on Windows and Linux, retaining wrapper compatibility (G5). |
| CI-01 | P1/P2 | CI profiles and duplicate scanner | To-create | CI/release implementer | Queued. P1 platform qualification subset blocks v0.2/G5; P2 profile split and duplicate scanner optional with scope decision. Preserve governance checks. |
| REF-01 | P3 | Conditional refactoring and retirement | To-create | Subsystem maintainer | Deferred. Characterize consumer use before wrapper retirement. Require a third-adapter coupling or unsafe schema evolution before decomposing the runner. |
| #8 | P1 | Deterministic context fidelity | [#8][i8] | Context lead + independent evaluator | REVISE. B2 and fresh independent holdout (G1). |
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
