# WHS delivery phases and acceptance gates

The [root roadmap](../../ROADMAP.md) is the entry point for delivery order.
This plan defines delivery phases, acceptance gateways, the issue map and
release milestones. GitHub issues own the active work and its acceptance
checklists. Dated experiment and corpus reports own their measurements.
Delivery phase numbers and gateway IDs are scoped to this plan. The root
roadmap retains the original Project Phase 9c, Phases 13–17 and goal IDs.

## Starting decisions

| Work | Verified state on 2026-11-20 | Next decision |
|---|---|---|
| Chronicle baseline | PRs [#2][pr2]–[#6][pr6] are merged, including structured run evidence, strict configuration and survivor navigation. Main at `e2f1c17643b0` has five successful [hosted CI jobs][main-ci]. | Verify release behavior through the installed entry points. |
| Flowers | PR [#7][pr7] is merged with engineering and navigation evidence. Real-corpus semantic acceptance remains **REVIEW**. | Apply the independent rubric in [#16][i16] after the Phase 2 decisions. |
| NCM pilot | PR [#12][pr12] is merged as research evidence. Genuine inference is **BLOCKED**. Real Flowers quality and incremental NCM benefit are **UNMEASURED**. | Reuse upstream runtime qualification for [#9][i9]. |
| Context export | PR [#13][pr13] is open and draft at `bd31c0470080`. Both [PR][pr13-ci] and [push][pr13-push] runs passed. B1 retained 43/45 critical facts overall, and 21/22 in delivered holdout packets. Median estimated GPT-2 token reduction versus raw was 46.07%. | **REVISE** under [#8][i8]. Preserve B1 and the exposed holdout failure as evidence. |
| Release boundary | The package metadata says `0.1.0`. Proposed v0.2 is the deterministic Chronicle release. | Certify v0.2 against the checklist below. Track WordPipe DOCX readiness independently. |

At the baseline, seven PRs had merged, PR #1 had closed without merging, and
PR #13 was the sole open PR. B0's original eight-case NCM-pilot metrics and
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

### Active execution queue

Allow at most three concurrent work packages. The maintainer admits the next
package when a slot clears and its entry criteria are met.

| Slot | Current package | Next decision |
|---|---|---|
| Governance | GOV-01 [#14][i14] | Review and integrate the documentation update in [#19][pr19]. |
| Research fidelity | [#8][i8] / [draft PR #13][pr13] | Preserve B1, freeze B2 and evaluate a fresh independently adjudicated holdout. |
| Independent hardening | SEC-01 [#17][i17] | Complete the public release audit, then admit SAFE-01 [#18][i18] to this slot. |

MD-01 [#15][i15] is next for document understanding when capacity is available.
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

**Exit gate.** Publish a PASS, REVIEW or BLOCKED decision against the frozen
rubric. Record unknowns, denominators and reproducibility evidence. Keep
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
| G3 — Corpus | Freeze taxonomy, rubric, scope and thresholds first. Independently adjudicate labels, then report precision, recall, F1, support and coverage against the declared release population. Record restricted Flowers corpus and publication decisions separately. | Corpus reviewer, CORP-01 [#16][i16] and NLP-01. Flowers semantic evidence remains REVIEW. |
| G4 — Ontology | For v0.2, verify unique source/survivor references, stable identities and provenance, schema compatibility and mapped project instances. Record the manual comparison disposition. For full G4, review the versioned schema, evaluated concepts and relations, and migration and compatibility evidence. | Chronicle and ontology maintainers, CORE-01, ONT-01 and ONT-02. Evidence pending. |
| G5 — Release | Verify the wheel-installed Chronicle workflow, failure recovery, cancellation, current release security review and passing acceptance on supported Windows and Linux candidates. Track DOCX capability and external TraceLedger acceptance independently. | Release maintainer, EXEC-01, SEC-01 [#17][i17] and CLI-01. Qualification pending. |
| G6 — Knowledge | Independently evaluate evidence resolution, temporal scope, claim and relation quality against predeclared targets. Preserve earlier claims and record qualifications, contradictions, retractions and supersession explicitly. | Knowledge maintainer and independent evaluator, CLAIM-01 and CITE-01. Entry gated. |
| G7 — AI | Qualify the runtime or adapter for the intended use. Obtain applicable data and execution authorization. Independently evaluate all cases, including rejected and fallback cases. Record quality, latency, memory and cost against the deterministic baseline and apply each issue's benefit criteria. | Experiment maintainers and independent evaluator, [#9][i9]–[#11][i11]. NCM inference and the combined benchmark are **BLOCKED**. Jev has offline preparation available. |

## Proposed release boundaries

| Target | Scope | Gate evidence |
|---|---|---|
| v0.1.x | Foundation and reliability fixes. | G0 and applicable regression checks. |
| v0.2 | Stable deterministic Chronicle and provenance-bound context export. | G0–G5, with core G4 limited to references, provenance and project-instance compatibility. |
| v0.3 | Versioned semantic ontology and independently evaluated claim extraction. | Full G4 and applicable G6 evidence. |
| v0.4 | Search, knowledge lifecycle and qualified integrations. | G6, measured query need and applicable external consumer acceptance. |
| v0.5 | Optional qualified AI assistance. | G7 with an explicit adoption decision. |

These are planning targets. Record evidence at the candidate SHA before any
tag or release decision. G6 and G7, semantic expansion under full G4, and the
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
- [ ] Independent taxonomy/corpus evaluation supports the published product scope. Any restricted local corpus verdict and its scope are explicit.
- [ ] Core G4 references, compatible project instances and the manual comparison disposition are evidenced. If the authorized comparison is blocked, record its release impact and obtain a maintainer scope decision.
- [ ] Bounded execution, cancellation and failure recovery pass on supported platforms.
- [ ] Public release scope and dependency/publication review pass [#17][i17].
- [ ] Fresh Windows and Linux checks and a clean-environment installed Chronicle workflow pass at the release candidate.

## Backlog activation and synchronization

The 24 work packages have 20 planning IDs and four existing research issue
references. An issue reference identifies the owner issue. The remaining 15 packages are owned by this plan until their activation
criteria are met. The [optimization map](OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md) holds
technical evidence and historical remediation.

| ID | Priority | Work package | Issue | State and activation or acceptance contract |
|---|---|---|---|---|
| GOV-01 | P0 | Roadmap and evidence reconciliation | [#14][i14] | In progress. Integrate [#19][pr19] after the issue map and governance checks agree (G0). |
| MD-01 | P1 | Structure-aware Markdown ingestion | [#15][i15] | Ready, next available slot. Verify fenced headings, source coverage, stable locators and replay (G2). |
| TIME-01 | P1 | Temporal evidence and date semantics | | Queued. Start after MD-01 establishes spans. Verify all date roles, locators and explicit unknowns (G2). |
| CORP-01 | P1 | Flowers semantic corpus acceptance | [#16][i16] | Queued. Prepare rubric offline. Score after G2 decisions, frozen taxonomy and authorization of the local inventory (G3). |
| NLP-01 | P1 | Multilingual normalization and taxonomy | | Queued. Define annotation, then measure normalized Persian/English keyword and phrase behavior, offsets and per-label results (G2, G3). |
| CORE-01 | P1 | Reference builder and manual comparison | | Queued. Reuse verified survivor keys for Phase 9c. Require resolvable links, repeatability and an evidenced or explicitly blocked comparison (G4). |
| ONT-01 | P1 | Project ontology population | | Queued. Map verified Phase 13–17 runs to existing project entities. Verify stable IDs, schema compatibility and evidence references (core G4). |
| ONT-02 | P1 | Semantic concepts and relationships | | Gated by ONT-01, NLP-01 and the Phase 15 schema decision. Verify versioned migration and evidence-backed relations (full G4). |
| SAFE-01 | P1 | Atomic DOCX publication | [#18][i18] | Ready after SEC-01 in slot 3. Prove failure preservation and cleanup through installed paths on Windows and Linux (DOCX readiness). |
| EXEC-01 | P1 | Bounded execution and cancellation | | Queued. Define stage process contracts and verify deadlines, bounded diagnostics and cleanup on supported platforms (G5). |
| SEC-01 | P1 | Public repository and dependency audit | [#17][i17] | Ready in slot 3. Record current ref, dependency, workflow and release-artifact coverage and disposition (G5). |
| DOCX-01 | P2 | Flattener and capability contracts | | Queued. Characterize supported COM/XML dependencies and experimental flags. Verify installation and capability reporting (DOCX readiness). |
| INT-01 | P2 | TraceLedger consumer validation | | Queued. Require a real available consumer and verify library, EventSink and capability contracts (external consumer acceptance). |
| CLAIM-01 | P2 | Claim lifecycle and contradictions | | Gated by grounded references and the semantic schema decision. Verify evidence, temporal scope and historical preservation (G6). |
| CITE-01 | P2 | Research citation model | | Queued. Build on CORE-01 source locators. Verify per-claim citations resolve and survive replay (G6). |
| PERF-01 | P2 | Chronicle scaling benchmark | | Queued. Measure wall time and peak memory at 100, 1,000, 10,000 and 100,000 events on pinned fixtures (G6). |
| STORE-01 | P2 | Rebuildable SQLite projection | | Gated by PERF-01 or documented query friction. Require reproducible rebuilds from canonical artifacts and measured benefit (G6). |
| CLI-01 | P1 | Installed Chronicle CLI | | Queued. Exercise a clean wheel install and documented complete Chronicle flow on Windows and Linux, retaining wrapper compatibility (G5). |
| CI-01 | P2 | CI profiles and duplicate scanner | | Queued. Establish coverage and timing baselines and preserve equivalent governance checks when splitting profiles. |
| REF-01 | P3 | Conditional refactoring and retirement | | Deferred. Characterize consumer use before wrapper retirement. Require a third-adapter coupling or unsafe schema evolution before decomposing the runner. |
| #8 | P1 | Deterministic context fidelity | [#8][i8] | REVISE. B2 and fresh independent holdout (G1). |
| #9 | P1 | NCM fidelity | [#9][i9] | BLOCKED for genuine inference. Require G1 and upstream runtime/fidelity qualification (G7). |
| #10 | P1 | Jev shadow classification | [#10][i10] | Live work gated. Prepare independent classification fixtures offline. Require upstream adapter qualification and authorization for live work (G7). |
| #11 | P1 | Combined benchmark | [#11][i11] | BLOCKED on #8–#10 and applicable upstream evidence. Reuse identical tasks and candidate pools (G7). |

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
