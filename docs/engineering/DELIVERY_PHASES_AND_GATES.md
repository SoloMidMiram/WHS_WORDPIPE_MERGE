# WHS delivery phases and acceptance gates

The [root roadmap](../../ROADMAP.md) is the entry point for delivery order.
This plan defines phase transitions and the queued backlog. GitHub issues own
the active work, dependencies and evidence links. Dated experiment and corpus
reports own their measurements.

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

## Phase 1 — Context fidelity

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

## Proposed release boundaries

| Target | Scope and evidence |
|---|---|
| v0.1.x | Foundation and reliability fixes. |
| v0.2 | Stable deterministic Chronicle and provenance-bound export, using the checklist below. |
| v0.3 | Versioned ontology and independently evaluated semantic extraction. |
| v0.4 | Measured knowledge querying and qualified external consumers. |
| v0.5 | Optional AI assistance only where separate qualification and adoption decisions pass. |

These are planning targets. Record evidence at the candidate SHA before any
tag or release decision.

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
- [ ] References and the manual comparison disposition are evidenced. If the authorized comparison is blocked, record its release impact and obtain a maintainer scope decision.
- [ ] Bounded execution, cancellation and failure recovery pass on supported platforms.
- [ ] Public release scope and dependency/publication review pass [#17][i17].
- [ ] Fresh Windows and Linux checks and a clean-environment installed Chronicle workflow pass at the release candidate.

## Backlog activation and synchronization

| Workstream | Item | State and next decision |
|---|---|---|
| A · Deterministic | Context fidelity [#8][i8] | Active · Revise B2 under Phase 1. |
| Cross-track governance | Roadmap reconciliation [#14][i14] | In progress · Close with the integrated documentation update. |
| A · Deterministic | Markdown extraction [#15][i15] | Ready · Characterize structure and line mapping. |
| A · Deterministic | Flowers semantic acceptance [#16][i16] | Queued · Freeze rubric, then run with authorized local data after Phase 2 decisions. |
| A · Deterministic | Temporal evidence and date semantics | Queued · Characterize adapter spans, then design the sidecar. |
| A · Deterministic | Multilingual taxonomy and NLP evaluation | Queued · Establish labeled data, compare normalization and phrase matching, then consider targeted lexical retrieval or POS/NER. Embeddings and relation extraction require evidence. |
| A · Deterministic | Reference builder and manual comparison | Queued · Use Phase 4 entry criteria and existing navigation contracts. |
| B · Semantic | Project ontology instance population | Queued · Map verified topic runs to the existing project model. |
| B · Semantic | Semantic concepts and relationships | Queued · Require NLP evidence and the Phase 4 schema decision. |
| C · Delivery | Atomic DOCX publication [#18][i18] | Ready · Characterize and implement in an independent slice. |
| C · Delivery | Bounded stage execution | Queued · Define topic-runner process contract and platform checks. |
| Cross-track governance | Public and dependency audit [#17][i17] | Ready · Record current public-ref and release coverage. |
| B · Semantic | Claim lifecycle and contradiction detection | Queued · Require reference and semantic grounding. |
| B · Semantic | Citation and bibliography model | Queued · Extend source and reference contracts with per-claim evidence. |
| C · Delivery | DOCX capability, flattener lifecycle and flag decisions | Queued · Characterize COM/XML installation constraints and classify supported, deferred or deprecated options. |
| C · Delivery | External TraceLedger integration | Queued · Require an available consumer and verified capability/contract. |
| A · Deterministic | Chronicle scaling benchmark | Queued · Establish repeatable performance and memory baselines. |
| B · Semantic | Rebuildable local knowledge index | Conditional · Require measured scaling or query friction. |
| C · Delivery | Installed Chronicle CLI and packaging | Queued · Define a minimum wheel-installed workflow and preserve existing consumer contracts. |
| Cross-track governance | Governed duplicate inventory and CI profile split | Queued · Document contracts and keep equivalent governance coverage. |
| D · Research | NCM fidelity [#9][i9] | Blocked for genuine inference · Upstream runtime and Phase 1 gates. |
| D · Research | Jev shadow classification [#10][i10] | Gated for live work · Offline fixture and evaluation prep available. |
| D · Research | Combined benchmark [#11][i11] | Blocked · Prerequisite evidence missing. |
| Cross-track governance | Wrapper retirement and runner decomposition | Conditional · Require consumer inventory or the existing architecture trigger. |

Lower-priority work includes organizing tests as affected subsystems change,
auditing absolute paths, and modeling labor notes, reports and plans when
stable mappings are available. Memorilla, graph or vector servers, web UI,
deployment orchestration, autonomous agents, model fine-tuning, automatic
semantic deduplication and full rewrites stay deferred pending demonstrated
need and a separate decision.

When work becomes actionable, search existing issues, open or reuse one
bounded issue, add its dependency and exit criteria, and link it here in the
same planning iteration. When a gate changes, update its issue and the root
narrative with the exact evidence and disposition. Preserve historical
results. Close issues against their documented acceptance. Use plain `Refs`
links for research PRs that deliver evidence while a quality gate stays open.

[pr2]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/2
[pr6]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/6
[pr7]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/7
[pr12]: https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/12
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
