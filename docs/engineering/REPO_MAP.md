# WHS repository retrieval map

Checked 2026-11-22 against main `c78c6e90d96e` and the November 21 issue reconciliation.

Checked 2026-11-21 against main `e85ddc1b0422` for the WHS #8 deferral.

Checked 2026-11-20 for delivery and backlog planning against main `e2f1c17643b0`.
This is a routing map, not live PR status or an acceptance certificate.
Canonical dependency rules remain in [architecture](../../ARCHITECTURE_AND_MODULES.md).
The broad file inventory remains [INDEX.md](../../INDEX.md).

## Start small

Run `python tools/repo_context.py snapshot`, then read the newest relevant entry
in [ROADMAP.md](../../ROADMAP.md). Search the lane below with
`python tools/repo_context.py find "term" --scope tools --scope tests`.
Use `git grep -n -I -i -F -e "term" -- <paths>` directly for custom retrieval.
Use `rg` for selected untracked files. These are keyword references, not a
semantic index; verify the caller and contract before editing.

| Goal / keywords | Production or configuration | Tests / evidence route |
|---|---|---|
| DOCX, process_docx_v3, flatten, EventSink | `wordpipe/__init__.py`, `wordpipe/orchestrator.py`, `wordpipe/pipeline/`, `wordpipe/steps/`, `wordpipe/adapters/`, `wordpipe/interfaces/` | `tests/test_steps.py`, `tests/test_orchestration_pipeline.py`, `tests/test_traceledger_consumer.py`; `docs/TRACELEDGER_INTEGRATION_CONTRACT.md` |
| ingest, rejected, allow-undated | `wordpipe/chronicle/ingest.py`, `pipeline/ingest.py` | `tests/test_pipeline_chronicle.py`, `tests/test_chain_partial_ingest.py` |
| merge, survivor, dedup, conflict | `wordpipe/chronicle/merge.py`, `pipeline/merge.py` | `tests/test_phase17_survivor_verification.py`, `tests/test_phase17_provenance_stability.py` |
| theme, negative_keywords, substring | `wordpipe/chronicle/categorize.py`, `pipeline/themes.json` | `tests/test_pipeline_chronicle.py`, `tests/test_acceptance_remediation.py` |
| index, anchors, Unicode | `wordpipe/chronicle/index.py`, `pipeline/index.py`, `pipeline/index_config.json`, `pipeline/templates/` | `tests/test_index_extraction.py`; PR #5 implementation merged; refresh current refs before work |
| chain, stages, run.json, fresh artifacts | `pipeline/chain.ps1`, `pipeline/chain_evidence.ps1` | `tests/test_pipeline_contracts.py`, `.github/workflows/ci.yml` |
| EXEC-01 policy, ownership and terminal stage evidence | `wordpipe/execution.py`, `wordpipe/_execution_posix.py`, `wordpipe/_execution_windows.py`, `pipeline/execute_stage.py` | `tests/test_execution.py`, `tests/test_chain_partial_ingest.py`, `tests/test_run_topic_report.py` |
| CLI-01 installed workflow and evidence-safe publication | [#34](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/34), [delivery plan](DELIVERY_PHASES_AND_GATES.md), `pyproject.toml`, `wordpipe/chronicle/cli/`, `tools/run_topic_report.py` | `tools/qualify_md01_wheel.py`, `tests/test_pipeline_chronicle.py`, `tests/test_acceptance_remediation.py` (existing coverage; full qualification pending) |
| Merge equivalence and legacy consumer errors | `wordpipe/chronicle/merge.py`, `wordpipe/orchestrator.py`, [optimization map](OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md) | [CORE-02 #36](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/36) under CORE-01/G3-core and DOCX-01/INT-01 queued characterization |
| CI-01 source and installed origins, foreign checkout | [CI-01 #30](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/30), [bounded contract](DELIVERY_PHASES_AND_GATES.md#ci-01-p1-admission-and-bounded-contract), `pipeline/_import_origin.py`, `tests/conftest.py`, `tools/qualify_md01_wheel.py` | `tests/test_import_origin.py`, `tests/test_index_extraction.py`, `tests/test_chain_partial_ingest.py`, `tests/test_md01_markdown_modes.py`, `.github/workflows/ci.yml` |
| topic, adapter, lineage, correlation | `tools/run_topic_report.py`, `tools/prepare_generic_markdown_chronicle.py`, `tools/prepare_insurancechatbot_chronicle.py` | `tests/test_run_topic_report.py`, `tests/test_prepare_generic_markdown_chronicle.py`, `tests/test_phase16_event_lineage_runner.py` |
| MD-01 fixture and three reliability handoffs | [Delivery phases and gates](DELIVERY_PHASES_AND_GATES.md) | `tests/fixtures/md01_structure.md`; dated MD-01, EXEC-01 and SAFE-01 sections in the delivery plan |
| MD-01 opt-in structural Markdown, paired runs and wheel qualification | `wordpipe/markdown_contract.py`, `wordpipe/chronicle/markdown_sections.py`, `tools/prepare_generic_markdown_chronicle.py`, `tools/run_topic_report.py` | `tests/test_md01_markdown_modes.py`, `tools/compare_markdown_modes.py`, `tools/qualify_md01_wheel.py` |
| catalog, hashes, preservation | `inputs/README.md`, `inputs/catalog.json`, `tools/verify_integrity.py` | `tests/test_input_catalog.py`; inspect specific evidence only on demand |
| boundaries, root, imports | `ROOT_ORGANIZATION.md`, `tools/check_root_layout.py`, `tools/check_architecture_boundaries.py` | `tests/test_root_layout.py`, `tests/test_architecture_boundaries.py` |
| NCM Flowers pilot, B0, worker fallback | `scripts/experiments/ncm_flowers_pilot.py` (offline synthetic harness) | `tests/test_ncm_flowers_pilot.py`, `tests/fixtures/ncm_flowers_synthetic.json`, `tests/fixtures/ncm_flowers_synthetic_gold.json`; [report and metrics](NCM_FLOWERS_PILOT.md). Genuine inference remains blocked. |
| Context-pack fidelity, B1/B2 | [Draft PR #13](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/13) and [issue #8](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/8) | [Frozen B2 findings](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/blob/32387d67b76aad99baa462cf1cc7c3172901681d/docs/engineering/WHS_CONTEXT_PACK_B2.md#b2-root-cause-disposition--2026-11-21), [ten synthetic probes](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/blob/32387d67b76aad99baa462cf1cc7c3172901681d/tests/fixtures/whs_context_raw_fallback_regressions.json), [strict expected-failure tests](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/blob/32387d67b76aad99baa462cf1cc7c3172901681d/tests/test_chronicle_context_pack.py), and [B3 re-entry](DELIVERY_PHASES_AND_GATES.md#b3-re-entry) |
| Flowers topic acceptance | [Flowers pilot](../../WordHorrorStories/flowers/README.md) and [#16](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/16) | [Historical engineering evidence and open semantic review](../../WordHorrorStories/flowers/ACCEPTANCE_02.md) |
| gateways, issue ownership, release milestones | [Delivery plan](DELIVERY_PHASES_AND_GATES.md) | [G0–G7](DELIVERY_PHASES_AND_GATES.md#acceptance-gateway-matrix), [work packages](DELIVERY_PHASES_AND_GATES.md#backlog-activation-and-synchronization), [release gates](DELIVERY_PHASES_AND_GATES.md#proposed-release-boundaries) |
| priorities, architecture, ontology | `ROADMAP.md`, `ARCHITECTURE_AND_MODULES.md`, `ONTOLOGY_MODEL.md` | [Delivery phases and gates](DELIVERY_PHASES_AND_GATES.md), `docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md`, `docs/engineering/OUTSTANDING_WORK_AND_OPTIMIZATION_MAP.md` |

## Reuse tools and interpret their limits

| Tool / command | What to retain | What it does not prove |
|---|---|---|
| `python tools/repo_context.py snapshot` | local branch, full head, dirt summary, tracked control paths | remote freshness or clean state of other worktrees |
| `python tools/repo_context.py find "term"` | bounded path:line snippets and truncation notice | absence outside tracked selected scopes; completeness after truncation |
| `python tools/run_topic_report.py --manifest <manifest> --run-id <fresh-id>` | run manifest, observed stage results, lineage, metrics, verdict | semantic label correctness, publication dates, source rights |
| `python tools/verify_integrity.py --help` | choose existing supported hash-verification options | unchanged untracked evidence from git diff alone |
| `python -m pytest tests -q` | observed summary, checkout/config/environment | external consumer or corpus acceptance |
| `gh pr view <number> --json headRefOid,headRefName,baseRefName,isDraft` | current metadata and ownership | merge permission or CI success |
| `gh run view <id> --json headSha,status,conclusion,jobs` | exact SHA and individual jobs | success for a later commit |

Five governance checks, from repository root:

```powershell
python tools/check_root_layout.py --root .
python tools/check_input_catalog.py --root .
python tools/check_architecture_boundaries.py --root .
python tools/docs_link_check.py
python tools/security_scan.py --root . --fail-on-findings
```

Use existing PowerShell integration in `.github/workflows/ci.yml` when applicable.
`python tools/smoke_flowers.py` runs the synthetic five-stage smoke on this
Flowers branch; verify presence when using another checkout. PR #6 configuration/metadata validation and PR #5 survivor navigation are now
merged into main. Those are reported workstream
boundaries, not a reason to import their code or assume their current heads.

## Context cost and preservation

Default retrieval excludes `inputs/`, `_WORK/`, `_ARCHIVE/`, topic outputs,
legacy code and secrets. Inspect those only for an explicit evidence question;
keep restricted text local. Reuse a run by manifest/hash/SHA identity, not by
folder name. Read the relevant small section instead of entire historical files.
Cache derived facts in the dated roadmap with locators and invalidation
conditions. The helper performs no model/API calls. Update this map when routes
or ownership change, and record the check in every pre-merge roadmap entry.

## Pre-pilot engineering efficiency

Use a revision-bound operational capsule as the starting context for engineering
work. Use up to 2,500 tokens initially, with 1,500–2,500 as the budget range for
multi-step work and less for small tasks. Record:

- Task and scope, local branch and exact head/base, last accepted revision, and
  PR state with its verification time when relevant.
- Active ownership, constraints, decisions and blockers relevant to the task.
- Affected contracts, checks, evidence locators, and conditions that invalidate
  each reused result. Link the authoritative source for each material fact.
- Next action and acceptance decision.

Refresh the capsule when head, base, ownership or an evidence dependency
changes. Keep the delivery plan, issue records and historical roadmap as the
sources of record. Review deltas from the last accepted SHA. Retrieve symbols
and failing assertions on demand. Use deterministic tools for inventories,
hashes and checks. Keep raw logs and detailed receipts in evidence artifacts.
Review completion, by itself, does not trigger a second review.

### Engineering measurement

Keep one usage receipt per bounded task. Record task class, revisions, verdict,
attempts and reviews, token telemetry source, cached and uncached input, output,
reasoning, model calls, repeated retrievals, avoidable iterations and broad scans. Count repeated
retrieval when an unchanged evidence locator is fetched again for the same
decision. Record final report length using a consistent tokenizer or, if
unavailable, characters as a separate metric. Include retries and review turns
when attributing usage to a task. Mark missing fields unavailable. Keep
estimates separate and retain only aggregate metadata from private session logs.

Compare like task classes and acceptance coverage. Use observed tokens across
the measured tasks divided by accepted results, including the usage of failed
attempts in the numerator. Report total and uncached input separately and record
sample size, model and cache conditions where available. The initial reference
sample is one recorded Codex turn per row, measured from cumulative telemetry
deltas between turn boundaries on 2026-11-27. Additional turns and unreported
usage remain outside this sample.

| Reference turn | Cached input | Uncached input | Output | Reasoning within output | Total tokens |
|---|---:|---:|---:|---:|---:|
| PR #27 integration | 5,552,640 | 20,122 | 6,211 | 617 | 5,578,973 |
| PR #28 documentation integration and exit | 8,110,336 | 29,313 | 8,197 | 1,142 | 8,147,846 |
| PR #32 integration and exit | 12,688,512 | 421,035 | 9,013 | 804 | 13,118,560 |
| PR #35 independent review, REVISE | 3,334,016 | 478,350 | 5,005 | 328 | 3,817,371 |

Uncached input is reported input minus cached input. The sampled Codex
telemetry includes reasoning within output, so count it once in the total.
For other sources, record how reasoning is counted. This sample measures recorded model usage and
does not establish quota consumption, billing, or achieved savings. Proposed
targets after matched baseline collection are 40% fewer tokens per accepted
task, 70% fewer repeated retrievals, 60% shorter reports, 50% fewer unnecessary
review iterations and zero unnecessary full scans. Require zero protected
information loss and zero reduction in regression coverage. Maintain all
correctness, security, provenance and acceptance requirements.

### Runtime pilot measurement

Once the pilot is separately authorized, run the same questions on frozen
documents and an independently scored answer set in three modes. A loads raw
Markdown, B uses Chronicle output and indexes, and C uses eligible
provenance-bound targeted evidence. Pin revisions, model settings and scoring
rules. Include tool results as reflected in model telemetry, retry and fallback
calls, elapsed time, correctness and actual cost where available. Report
acceptance rates and total tokens per correct accepted result, including failed
attempts in the total. Record protected facts and supporting references in the
scoring rubric. A zero-acceptance arm has no defined per-acceptance ratio.

Engineering efficiency is cross-cutting. This measurement plan leaves the
execution queue, G1 qualification, B3 deferral and release decisions with
their existing authorities.

### Evidence routing

Publish approved pilot statistics in a topic-named directory under
docs/engineering/pilots. Keep the input identities, run registration,
measurement units and sanitized receipts together. Track measurement
qualification and workload-specific limits through
[issue #38](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/38).
Keep raw corpus copies, generated output and detailed logs in the local
workspace unless separately approved for publication. Stage named paths
after reviewing the full staged inventory and its source hashes.
