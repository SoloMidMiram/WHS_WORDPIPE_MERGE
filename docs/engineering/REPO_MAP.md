# WHS repository retrieval map

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
| topic, adapter, lineage, correlation | `tools/run_topic_report.py`, `tools/prepare_generic_markdown_chronicle.py`, `tools/prepare_insurancechatbot_chronicle.py` | `tests/test_run_topic_report.py`, `tests/test_prepare_generic_markdown_chronicle.py`, `tests/test_phase16_event_lineage_runner.py` |
| catalog, hashes, preservation | `inputs/README.md`, `inputs/catalog.json`, `tools/verify_integrity.py` | `tests/test_input_catalog.py`; inspect specific evidence only on demand |
| boundaries, root, imports | `ROOT_ORGANIZATION.md`, `tools/check_root_layout.py`, `tools/check_architecture_boundaries.py` | `tests/test_root_layout.py`, `tests/test_architecture_boundaries.py` |
| NCM Flowers pilot, B0, worker fallback | `scripts/experiments/ncm_flowers_pilot.py` (offline synthetic harness) | `tests/test_ncm_flowers_pilot.py`, `tests/fixtures/ncm_flowers_synthetic.json`, `tests/fixtures/ncm_flowers_synthetic_gold.json`; [report and metrics](NCM_FLOWERS_PILOT.md). Genuine inference remains blocked. |
| context-pack fidelity, B1/B2 | [Draft PR #13](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/13) and [issue #8](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/8) | [Delivery Phase 1](DELIVERY_PHASES_AND_GATES.md#phase-1--context-fidelity) routes the benchmark and revision gate. |
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
conditions. The helper performs no model/API calls; no token savings percentage
has been measured. Update this map when routes or ownership change, and record
the check in every pre-merge roadmap entry.
