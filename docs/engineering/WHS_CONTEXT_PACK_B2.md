# WHS #8 B2 context-pack review

**Research disposition: REVISE.** This iteration prepares a draft candidate for an independently adjudicated G1 evaluation. The [B1 report](WHS_CONTEXT_PACK_FIDELITY.md), frozen fixtures and gold, metrics, and REVISE verdict remain historical evidence.

## First-measurement re-baseline review · 2026-11-20

The first B2 measurement used the exporter and harness from local commit
`ec64f4f1646b4d97da9ae6360e877d3cda2c9ce0` on integrated main
`e85ddc1b04227d9d28c2861733016570612239cc`. The checked Windows 11
build was 26300 on Intel64 Family 6 Model 183, with Python 3.11.4 and package
imports resolved under the #8 checkout. The real synthetic Chronicle runner
used the 12-case B1 tuning partition and its separate gold. Git blob IDs for
the original inputs and gold are `4874f02d9b65c3e93075390d27adb023aade6958`
and `e2b8c21df664fbd937f15a2de8b2bf9848dd84a5`.

B2 delivered nine structural packets and one verified raw fallback. Both
provenance faults refused. The run retained 22/22 critical facts and 32/32
total gold literals, with 10/10 delivered packets passing provenance and
zero unsupported units. Replay matched and input hashes were unchanged.
Median complete-packet byte reduction versus raw was 44.42% across the 12
tuning cases with zero credit for fallback or refusal. The target tokenizer
and pinned historical GPT-2 asset were unavailable for this run. Token savings
remain unmeasured. The simulated consumer performed zero source rereads.
Run verification read sources locally and records those bytes separately.

Local evidence is `_WORK/whs-b2-first-measurement-20261120/case-results.json`
with SHA-256 `c97b3ee11e3409bb50391dff0f485108edc426a8a7feb8750b8b91d639515d2f`.

The adopted [G1 contract](DELIVERY_PHASES_AND_GATES.md#quantified-gateway-contracts)
remains the preregistration baseline. Require at least 30 fresh cases, including
at least 20 independently labeled valid answerable in-budget cases and 10
expected refusals. Require at least 95% verified valid delivery, 100% correct
expected refusals, 100% protected facts and exact required IDs in deliveries,
100% valid anchors where applicable, zero unsupported facts, and at least 20%
median complete-packet and consumer-reread token reduction across valid cases.
Valid refusals count against delivery and the applicable fact denominator.
Raw fallback and refusal earn zero savings.

**Re-baseline recommendation is to retain all approved values.** The first
measurement exercised runner, provenance, fallback, and replay, with too few
cases and no tokenizer or independent gold for a threshold decision. The
maintainer's disposition on this first-measurement review remains pending.
A threshold change after fresh holdout exposure requires new independent
evidence. Retain all original evidence and verdicts.

## Revised candidate and independent evaluation

The candidate binds source section bodies to canonical survivor keys by using
the existing adapter and ingest transformations. It closes a bounded set of
distant qualifications while retaining exact entity IDs, uses verified raw
for unresolved qualification context when the request has source evidence, and
refuses invalid queries or requests without qualifying lexical evidence.
This lexical check can refuse answerable paraphrases. The historical empty
match cases use unrelated keywords and credit complete raw context. Retain
their misses in historical comparisons.

| Replay | Cases | Structural / raw / refused | Critical facts, delivered / all | Verified deliveries |
| --- | ---: | --- | --- | ---: |
| Historical tuning | 12 | 9 / 0 / 3 | 21/21 / 21/22 | 9/9 |
| Exposed B1 holdout regression | 12 | 9 / 1 / 2 | 21/21 / 21/23 | 10/10 |

The exposed `far-condition` case now retains “Use distilled coolant only”.
The tuning `empty-match` and exposed `empty` cases now refuse, with their
gold misses retained above. The exposed budget refusal still counts as a miss.
Both runs found zero unsupported units, confirmed deterministic replay and
verified that source and canonical output pins were unchanged. These runs
used historical corpora and byte-only accounting.

The tuning result is `_WORK/whs-b2-tuning-final-20261120/case-results.json`
with SHA-256 `c0b8b40a5bc790aaf1d6c1b0a91574d5a282b4c4cef79785561500852ccb0a60`.
The exposed result is `_WORK/whs-b2-exposed-b1-final-20261120/case-results.json`
with SHA-256 `a4e05fb703059397680335a4cb8a56529611dba94c01b2f5eb0770e92677acaa`.

After reviewing the candidate and this preregistration, freeze the candidate
commit, configuration, tokenizer identity and source/input scope before the
independent evaluator authors cases. Keep request stimuli and reference gold
separate. Each fresh gold record needs a `classification` of `valid` or
`expected_refusal`, literal `critical` and `additional` lists and an explicit
`required_ids` list. Cover stale, ambiguous, invalid and unanswerable requests.
Preregister the packet-only simulation with zero follow-up reads or separately
count all complete consumer rereads for both arms. Record the tokenizer and
asset digest, distinguish estimates from actual consumer token counts, and
review the full- and delivered-population results and evidence independently.

Run the optional benchmark with a new evidence directory:

```powershell
python -m scripts.experiments.benchmark_context_pack --partition fresh --fixture FRESH_INPUTS --gold INDEPENDENT_GOLD --work _WORK/NEW_RUN --gpt2-tokenizer LOCAL_TOKENIZER_JSON
```

No independently authored fresh inputs or gold were provided. The scorer
reports coverage, expected refusals, delivered provenance and fact/ID misses,
and valid-population efficiency when a tokenizer is supplied. Analytical
acceptance still requires an independent semantic review and verified
unchanged canonical artifacts and deterministic replay.


## Conditional freeze — maintainer amendment · 2026-11-20

**Disposition: first-measurement instrument check ACCEPT; retain every G1
threshold; candidate conditionally locked; G1 REVISE.** The 44.42% is
median complete-packet **byte** reduction, not measured token savings.
Neither the first measurement nor the exposed B1 replay qualifies G1.
This dated amendment supersedes the sequencing in the preceding
preregistration paragraph: distinguish the candidate lock, a non-holdout
refusal probe, and scoring-instrument qualification. It does not supersede
any historical measurements, verdicts, or approved gate values.

### A — Candidate lock (effective now)

Candidate: `373840a5e869c183b6e09884b104fdfb88009fd2`; integrated base:
`e85ddc1b04227d9d28c2861733016570612239cc`.
The amendment is documentation-only; its commit is not a replacement
experimental candidate. The [candidate CI run](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/44702879518)
has five successful hosted jobs. All code/configuration and historical
inputs are pinned by the candidate commit. Key Git blob identities:

| Path | Git blob SHA |
| --- | --- |
| `scripts/experiments/chronicle_context_pack.py` | `9270794315e8e230d7e5f469035562071376115f` |
| `scripts/experiments/benchmark_context_pack.py` | `00b566453b0c66cdf68a16b34ac34edfee0418ee` |
| `scripts/experiments/ncm_flowers_pilot.py` (tokenizer/baseline helpers only) | `47b65702653aabe82bc0994f9e9424ca5f743078` |
| `tools/prepare_generic_markdown_chronicle.py` | `93f93b3a652982ad2cb5000f8e64e1f8b8300b99` |
| `tools/run_topic_report.py` | `07ac35c27bb06a3ae232dffa1abbae9405e301fe` |
| `pipeline/themes.json` | `d0b4dbf8b57e1bf1edf76ff752aba7a5d406bb8b` |
| `pipeline/index_config.json` | `44fd519c6f46ff53f7aac5127054350662294e07` |
| `tests/fixtures/whs_context_tuning.json` | `4874f02d9b65c3e93075390d27adb023aade6958` |
| `tests/fixtures/whs_context_tuning_gold.json` | `e2b8c21df664fbd937f15a2de8b2bf9848dd84a5` |
| `tests/fixtures/whs_context_holdout.json` | `6ab6470fe3ab3dc1a31e0f206d05c90abb720100` |
| `tests/fixtures/whs_context_holdout_gold.json` | `99d0da6e0a7d31c23161d450085f3589fd4c768e` |
| `tests/test_chronicle_context_pack.py` | `3171f831ba946bc660fd48cb3dac569c7f6f4844` |

Scope: public/synthetic Markdown only; no restricted Flowers data, hosted
inference, NCM or Jev. Use the existing generic Markdown adapter, its
candidate-pinned ingest transformations, canonical run/receipt verification,
and the above theme/index configurations. Historical fixture partitions
remain separate and exposed; neither is fresh evidence. Fresh authoring
must use separate inputs and separate gold, with frozen case roster and
hashes before prediction. The runner manifest uses schema 1, topic
`synthetic_context_pack`, timestamp run format, run ID
`20261119_000001`, `--allow-review`, the existing quality-gate settings
(0% minimum extraction coverage, 0% minimum theme tagging, 0 maximum errors),
120-second runner timeout, and intended checkout import origins. These
synthetic runner settings are not G1 acceptance waivers. Replay flags are
`--partition tuning` or `--partition holdout`, a unique `--work`
directory, no tokenizer for the recorded byte-only runs, normal
65,536-byte maximum and 128-byte injected small-budget fault.
Fresh evaluation uses `--partition fresh --fixture ... --gold ... --work ...`
plus the qualified tokenizer. No undisclosed flag, budget, dependency,
configuration or source-scope change is permitted.

Recorded (not newly recomputed) SHA-256 evidence:

- Initial measurement: `c97b3ee11e3409bb50391dff0f485108edc426a8a7feb8750b8b91d639515d2f`.
- Final tuning replay: `c0b8b40a5bc790aaf1d6c1b0a91574d5a282b4c4cef79785561500852ccb0a60`.
- Exposed B1 replay: `a4e05fb703059397680335a4cb8a56529611dba94c01b2f5eb0770e92677acaa`.

Any change affecting the candidate, scoring implementation, configuration or
declared source/input scope reopens measurement and requires a new candidate
identity, evidence, and reviewed freeze record. Documentation-only amendments
must not alter the pinned experiment. Preserve B1 and all failed results.

### B — Scoring instrument (pending; not a blocker to authoring preparation)

Select the existing pinned GPT-2 BPE estimator as the intended instrument,
not a claim that the asset is available or the instrument qualified.
Its expected JSON SHA-256, enforced by the candidate loader, is
`8414cab924d8b9b33013f0d221c5862f365ee9be39c5c2bfae8a5a9e970478a6`.
Before any fresh scoring or predictions, obtain the asset, verify its actual
digest, load it without truncation/padding, record the exact tokenizers engine
and runtime versions, and verify deterministic counts of complete serialized
packets. Estimates are not actual target-consumer token usage.
If the intended asset is unobtainable, stop and obtain explicit maintainer
approval of a substitute instrument and its compatibility/scorer changes,
if any, before fresh case authorship under that replacement protocol.
If independent authoring has already begun under this protocol, invalidate
that preregistration and arrange new independent cases under the approved
replacement; never choose a tokenizer after seeing holdout predictions.

Preregister the existing **packet-only, zero consumer rereads** simulation
for both arms now: count the complete serialized packets including metadata,
query and instruction; distinguish local verification reads from consumer
rereads. Refusal and raw fallback earn zero savings under the approved G1
contract. No separate reread savings is claimed from zero versus zero.
Actual consumer-reread performance remains unmeasured. Changing this protocol
requires a new pre-exposure preregistration and, if the candidate/scorer
changes, Part A re-freeze.

Independent evaluator recruitment, rubric and isolated authoring preparation
may proceed in parallel with asset qualification and the Part C probe.
Do not finalize the independent case set until Part C resolves and the
candidate is locked without pending code changes. Scoring cannot begin
until Parts A, B, and C are closed and independent inputs/gold are pinned.
Keep the independent author blinded to probe cases, outputs and candidate
predictions; if candidate revision makes any draft holdout exposed or
ineligible, replace it with fresh independent cases.

### C — Non-holdout paraphrase-refusal probe (required, pending)

Before finalizing fresh holdout authorship, execute a small separate
synthetic diagnostic at the pinned candidate, using a separate source and
evidence directory. Proposed bounded protocol: 20 answerable, in-budget,
independently pre-labeled paraphrase requests, paired with direct controls;
use low/no lexical overlap, mixed-script wording, entity references and
nonadjacent qualifications. Add a small distinct set of unanswerable
lexical-overlap controls to detect false delivery. Freeze the probe inputs,
labels, budgets, and roster before running; report exact route, reason,
provenance, facts/IDs, false-refusal numerator and denominator and
false-delivery counts. Count all valid refusals in the denominator.
The 5% trigger is a diagnostic heuristic, not a new G1 gate or a statistical
guarantee: more than one false refusal in 20 valid paraphrase cases triggers
REVISE of the refusal rule before final independent authoring. At or below
the trigger, retain the result and remaining uncertainty; false delivery
of unanswerable controls also requires explicit disposition before freeze
completion. Any change must preserve verified provenance, exact identifiers,
correct expected refusals and safe bounded fallback; absence of lexical
overlap alone is not proof of semantic absence. Do not indiscriminately
return raw evidence. If candidate changes, rerun the 12-case tuning replay,
retain the old results and new hashes, refresh engineering validation,
and re-freeze Part A before finalizing independently authored cases.
The probe cannot qualify G1 or count toward its fresh ≥30-case population.

**Current state:** Part A locked; Part B asset/runtime qualification pending
(packet-only protocol fixed); Part C unexecuted; independent evaluator and
fresh gold pending. No fresh holdout predictions or token measurements.
G1 remains REVISE, issue #8 open, PR #13 draft. No threshold change or new
work package is authorized.


## Conditional-freeze execution · 2026-11-20

**Disposition: the original candidate requires REVISE. Part B is qualified.
The revised candidate `920c8e044ad7553d11d010bdba6ae580626db961` is
pinned for independent authoring. Its replay resolved the Part C failures.
Fresh inputs and independent gold remain pending. G1 remains REVISE.**

### Instrument qualification

The [pinned GPT-2 tokenizer JSON](https://huggingface.co/openai-community/gpt2/blob/607a30d783dfa663caf39e06633721c8d4cfcd7e/tokenizer.json)
matched SHA-256
`8414cab924d8b9b33013f0d221c5862f365ee9be39c5c2bfae8a5a9e970478a6`.
The candidate loader used `tokenizers 0.23.3` on CPython `3.11.4`, with
truncation, padding and special-token insertion disabled. Two independent
tokenizer loads reproduced identical token ID sequences for each of 90
complete serialized envelopes per diagnostic run, across the raw and B2
arms. Delivered-packet counts include metadata, query and instructions.
For example, the locked candidate's first direct control measured 767
raw tokens and 301 B2 tokens.

Both arms used zero consumer rereads. The runner's local verification reads
are separate. Refused envelopes receive no delivered token count and earn
zero savings. Raw fallback likewise earns zero savings. These measurements
are GPT-2 estimates and do not represent actual target-consumer usage.

### Refusal diagnostic and evidence

A separate synthetic source and answer key were pinned before prediction
from literal source facts. No second adjudicator participated in the
development probe. Its 20 valid paraphrases had 20 paired direct controls
and five distinct unanswerable lexical-overlap controls. The paraphrases
covered low lexical overlap, separator variants, mixed-script wording,
and nonadjacent qualifications. Each used a 65,536-byte budget. The
diagnostic and replay are separate from independent G1 inputs and gold.

| Probe outcome | Locked candidate `373840a5e869` | Revised candidate |
| --- | --- | --- |
| False refusals, valid paraphrases | 9/20 | 0/20 |
| False refusals, direct controls | 0/20 | 0/20 |
| False deliveries, unanswerable overlap | 5/5 | 0/5 |
| Verified provenance on all deliveries | 36/36 | 40/40 |
| Paraphrase protected facts, delivered / all | 12/12 / 12/25 | 25/25 / 25/25 |
| Paraphrase required IDs, delivered / all | 11/11 / 11/20 | 20/20 / 20/20 |
| Direct protected facts and IDs | 25/25 facts, 20/20 IDs | 25/25 facts, 20/20 IDs |

The original false refusals reported `no_verified_query_evidence`. The
original 11 paraphrase and five unanswerable deliveries used raw fallback
with `insufficient_exact_evidence`. Both candidates delivered all direct
controls structurally. The revised candidate delivered all 20 paraphrases
structurally with `matching_structural_units` and refused all five overlap
controls with `unverified_entity_field`. Both runs recorded zero unsupported
units and unchanged source and canonical artifact hashes. Verified provenance
alone did not make the original five false deliveries relevant to the query.

The narrow change normalizes spaced identifiers and a limited English/Persian
vocabulary for explicit single-entity field requests. It requires grounding
of the entity, canonical field and significant query terms in the same
verified section before using existing delivery and qualification closure.
Requests outside this vocabulary and paraphrases without explicit entity
references still need fresh independent evaluation. Replaying the exposed
diagnostic establishes a regression result only.

Local evidence under `_WORK/whs-b2-freeze-20261120/`:

| Artifact | SHA-256 |
| --- | --- |
| `diagnostic-inputs.json` | `f2f78129ae4215c79014115e489f9d73bb7d7c07e6f339679d041f9d1830dfd5` |
| `diagnostic-gold.json` | `4a4a65413045dfd0c75f83e097af773f456790d4bbe12f73f386de8b8afd09cc` |
| `run_diagnostic.py` | `9b0d5f617482035643f9cea377f3e49752bca1fa22f409b6a5be89620926d9e6` |
| `locked-candidate/diagnostic-results.json` | `f0c41e5f2df218d15c32ad11c029bcca16956ba44895c2a99b7d1afce56731aa` |
| `revised-candidate/diagnostic-results.json` | `e298462f853e06621ae45f3215cae689028ab6b92b402fd275fe270306e5c10d` |
| `historical-tuning-revised/case-results.json` | `7ed89c131a290db4fa1cdb0ff07406a7afbfd80d2658eb99e5da5b206afa38d8` |

The 12-case historical tuning replay delivered nine structural packets and
refused three requests, including two provenance refusals. It preserved
21/21 delivered critical facts, 21/22 across all cases, and 9/9 verified
deliveries. The historical harness reported 35.53% median estimated
complete-packet token reduction across its 12-case denominator. That is a
new replay result, separate from the historical 44.42% byte measurement and
from the independent G1 valid-population metric. B1 evidence is unchanged.

### Revised freeze identity

Candidate commit `920c8e044ad7553d11d010bdba6ae580626db961`
has tree `9bfa8c3a33054984518bd0cfebf1275c9ecaddeb`. Exporter blob
`463056defa60488c09c7345564437f9bf589d4d9` and focused test blob
`b7341f167980058b678f112f61ae88bf8ef72fa7` are the only changes against
the documentation amendment. The scorer, source scope, runner settings,
historical fixtures, approved G1 thresholds and packet-only protocol
retain their existing pins. Integrated base is
`e85ddc1b04227d9d28c2861733016570612239cc`. Keep the independent evaluator
blinded to the probe. Fresh scoring requires separately authored and pinned
inputs and independent gold. Keep PR #13 draft and issue #8 open.

Local validation first asserted package import origins inside the #8
checkout. Observed 20 focused tests passed, 403 full-suite tests passed
with six skips, all five governance checks passed, and Windows PowerShell
integration passed both CI cases. CLI checks verified the paraphrased
delivery and unsupported-field refusal with no evidence on stdout. The
[exact-candidate CI run](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/actions/runs/44709174672)
covers the revised candidate independently of this documentation update.
