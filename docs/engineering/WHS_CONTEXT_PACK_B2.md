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
