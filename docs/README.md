# Documentation Index (Redirect)

> **⚠️ NOTE:** Many docs in this folder are **outdated**. See [`docs/OBSOLETE_DOCS.md`](OBSOLETE_DOCS.md) for the full index of superseded vs preserved docs.

## Current Source of Truth

Start here instead:

| Doc | What It Covers |
|-----|----------------|
| [`ARCHITECTURE_AND_MODULES.md`](../ARCHITECTURE_AND_MODULES.md) | **Comprehensive reference** for all 3 subsystems (chronicle pipeline, evidence pipeline, WordPipe runtime) — architecture, modules, data flow, logic flow, goals, constraints, integration, contracts |
| [`PLAN.md`](../PLAN.md) | Immutable log of intentions and completions |
| [`ROADMAP.md`](../ROADMAP.md) | Project roadmap with phases, milestones, constraints |
| [`JOURNAL.md`](../JOURNAL.md) | Dated period journal with claims and verification |
| [`ONTOLOGY_MODEL.md`](../ONTOLOGY_MODEL.md) | Formal entity-relationship model |
| [`INDEX.md`](../INDEX.md) | Full project file index |
| [`ROOT_ORGANIZATION.md`](../ROOT_ORGANIZATION.md) | Root allowlist, placement rules, and generated-output policy |
| [`../inputs/README.md`](../inputs/README.md) | Canonical corpus-input placement and provenance catalog policy |
| [`../AGENTS.md`](../AGENTS.md) | Repository-specific evidence protocol for planning and review agents |
| [`ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md`](ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md) | Topic-neutral template for repeated report runs, metrics, and quality checks |
| [`PHASE13_GENERIC_TOPIC_REPORT_RUNNER_ROADMAP.md`](PHASE13_GENERIC_TOPIC_REPORT_RUNNER_ROADMAP.md) | Planned generic topic runner, trend comparison, and ontology-spine roadmap |
| [`PHASE14_SECOND_TOPIC_ONTOLOGY_READINESS.md`](PHASE14_SECOND_TOPIC_ONTOLOGY_READINESS.md) | Second-topic evidence, genericity remediation, and Phase 15 readiness |
| [`PHASE15_PROJECT_SEMANTIC_ONTOLOGY_DESIGN.md`](PHASE15_PROJECT_SEMANTIC_ONTOLOGY_DESIGN.md) | Project Phase 15 file-level provenance foundation and semantic decision gate |
| [`PHASE16_EVENT_IDENTITY_AND_SECTION_PROVENANCE.md`](PHASE16_EVENT_IDENTITY_AND_SECTION_PROVENANCE.md) | Project Phase 16 section provenance sidecars and ontology migration gate |
| [`PHASE17_EVENT_PROVENANCE_SURVIVOR_AND_REPEATABILITY.md`](PHASE17_EVENT_PROVENANCE_SURVIVOR_AND_REPEATABILITY.md) | Project Phase 17 survivor integrity and stable-id repeatability gate |
| [`engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md`](engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md) | Current phase crosswalk, corrected flaw claims, and explicitly outstanding work |
| [`engineering/PHASE13_17_COMMIT_DRAFT.md`](engineering/PHASE13_17_COMMIT_DRAFT.md) | Verified Phase 13–17 traceability, staging guidance, and executed closeout commit `a635ea2` |

## Preserved Docs (Still Current)

| Doc | Purpose |
|-----|---------|
| [`SECURITY_HARDENING.md`](SECURITY_HARDENING.md) | Security policies and incident response |
| [`DUPLICATE_POLICY.md`](DUPLICATE_POLICY.md) | Duplicate governance rules |
| [`DOC_STYLE_GUIDE.md`](DOC_STYLE_GUIDE.md) | Documentation conventions |
| [`REPOSITORY_REVIEW_MERGED_2026-02-13.md`](REPOSITORY_REVIEW_MERGED_2026-02-13.md) | Consolidated architectural review |
| [`TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md`](TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md) | TraceLedger implementation roadmap |
| [`TRACELEDGER_INTEGRATION_CONTRACT.md`](TRACELEDGER_INTEGRATION_CONTRACT.md) | TraceLedger library contract |
| [`LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md`](LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md) | TraceLedger logic flow narrative |
| [`LABOR_REPORT.md`](LABOR_REPORT.md) | Labor and effort tracking |
| [`operations/LABOR.md`](operations/LABOR.md) | Operations labor notes |

## Current Evidence Highlights

| Evidence | What It Shows |
|----------|---------------|
| [`../WordHorrorStories/insurancechatbot/output/20260716_091000/RUN_SUMMARY.md`](../WordHorrorStories/insurancechatbot/output/20260716_091000/RUN_SUMMARY.md) | InsuranceChatbot topic-adapter run: 3 input files, 200 staged/merged events, 194 tagged events, 0 warnings/errors, 6.96s wall time |
| [`ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md`](ITERATIVE_PERFORMANCE_CHECK_TEMPLATE.md) | Reusable measurement loop for future topics and non-Chronicle Markdown bundles |
| [`../WordHorrorStories/pipelinechronicle/output/phase14_genericity_fix_trend/RUN_SUMMARY.md`](../WordHorrorStories/pipelinechronicle/output/phase14_genericity_fix_trend/RUN_SUMMARY.md) | Phase 14 remediation: 50 events, dynamic month headings, manifest-topic summary, compared trend, PASS |
| [`../WordHorrorStories/insurancechatbot/output/phase15_lineage_validation_v2/RUN_SUMMARY.md`](../WordHorrorStories/insurancechatbot/output/phase15_lineage_validation_v2/RUN_SUMMARY.md) | Authoritative Phase 15 closeout: 200 events, explicit lineage, collision-protected run, PASS |
| [`../WordHorrorStories/pipelinechronicle/output/phase15_lineage_validation_v2/RUN_SUMMARY.md`](../WordHorrorStories/pipelinechronicle/output/phase15_lineage_validation_v2/RUN_SUMMARY.md) | Authoritative second-topic closeout: 50 events, explicit lineage, COMPARED, PASS |
| [`../WordHorrorStories/insurancechatbot/output/phase16_event_lineage_validation/RUN_SUMMARY.md`](../WordHorrorStories/insurancechatbot/output/phase16_event_lineage_validation/RUN_SUMMARY.md) | Phase 16: 200 lineage events, correlation complete, exactly 194 theme-bearing, PASS |
| [`../WordHorrorStories/pipelinechronicle/output/phase16_event_lineage_validation/RUN_SUMMARY.md`](../WordHorrorStories/pipelinechronicle/output/phase16_event_lineage_validation/RUN_SUMMARY.md) | Phase 16 second topic: 50/50/50, correlation complete, COMPARED, PASS |
| [`../WordHorrorStories/insurancechatbot/output/phase17_event_provenance_repeatability/RUN_SUMMARY.md`](../WordHorrorStories/insurancechatbot/output/phase17_event_provenance_repeatability/RUN_SUMMARY.md) | Phase 17: merged-note-aware-v1 survivor gate, 200/200/194, PASS |
| [`../WordHorrorStories/insurancechatbot/output/phase17_provenance_stability/provenance_stability.json`](../WordHorrorStories/insurancechatbot/output/phase17_provenance_stability/provenance_stability.json) | Phase 17 vs Phase 16 stable-id comparison (STABLE) |
| [`../WordHorrorStories/pipelinechronicle/output/phase17_event_provenance_repeatability/RUN_SUMMARY.md`](../WordHorrorStories/pipelinechronicle/output/phase17_event_provenance_repeatability/RUN_SUMMARY.md) | Phase 17 second topic: merged-note-aware-v1 survivor gate, 50/50/50, PASS |
| [`../WordHorrorStories/pipelinechronicle/output/phase17_provenance_stability/provenance_stability.json`](../WordHorrorStories/pipelinechronicle/output/phase17_provenance_stability/provenance_stability.json) | PipelineChronicle Phase 17 vs Phase 16 stable-id comparison (STABLE) |

## Obsolete Docs

See [`docs/OBSOLETE_DOCS.md`](OBSOLETE_DOCS.md) for the full list of superseded docs and their replacements.
