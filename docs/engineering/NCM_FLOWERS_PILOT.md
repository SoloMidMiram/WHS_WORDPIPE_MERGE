# NCM-assisted Flowers context pilot

This experiment follows WHS issue [#8 (Chronicle retrieval)](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/8) and [#9 (NCM feasibility)](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/9). Related A2A research is tracked in [#40](https://github.com/SoloMidMiram/md-mdc-Agents-Skills-MCPs-Kagent-A2A-SubAgents/issues/40) and [#41](https://github.com/SoloMidMiram/md-mdc-Agents-Skills-MCPs-Kagent-A2A-SubAgents/issues/41).

## Decision

**BLOCKED at Gate A. Hold NCM adoption for this configuration.** The standalone lab's verified R3 records show an unresolved `libquadmath.so.0` dependency in the bundled Fortran library and an unresolved selection between two different `libgomp.so.1` binaries with the same SONAME. Bundled native-component provenance is incomplete, and the installer bootstrap remains under review. The R2 candidate wheel checksums and R3 evidence checksums passed a local recheck. The R3 disposition, native ABI report, native-component security review and installer bootstrap review remain local.

No NCM lab installation, target-package imports, checkpoint access, genuine synthetic smoke test or real Flowers processing occurred in this pilot. The harness exposes a backend response contract exercised with deterministic test doubles. A functional checkpoint launcher remains blocked. NCM output quality, fact retention, token reduction versus deterministic extraction, fallback rate, latency and peak RSS are unverified. The provisional 20% median reduction criterion for NCM versus extraction remains unevaluated.

## Verified synthetic comparison

The eight [authored fixtures](../../tests/fixtures/ncm_flowers_synthetic.json) use synthetic Markdown-style material with separately authored source facts. They have no second-reviewer validation. Arm A sends the full passage. Arm B ranks source lines by lexical overlap and retains exact critical lines, with the original packet as fallback when no term matches. Arm C stayed unexecuted. All eight A/B source identities matched.

| Metric | A · Raw | B · Deterministic extraction |
| --- | ---: | ---: |
| Annotated facts retained | 33/33 | 25/33 |
| Critical facts retained | 23/23 | 23/23 |
| Total estimated GPT-2 tokens | 1,168 | 1,007 |
| Total UTF-8 bytes | 3,971 | 3,442 |
| Median measured wall time | 0.9763 ms | 1.0136 ms |
| Largest measured Python allocation peak | 7,551 bytes | 7,239 bytes |
| Raw fallbacks | — | 1/8 |

The median per-case reduction was **14.19% estimated tokens** and **13.0% UTF-8 bytes**. The token count covers the complete serialized packet, including the task, question, source reference and hash, text and protected lines. The estimator used a pinned GPT-2 BPE asset, without special tokens. Actual Codex and Cursor usage is unmeasured. Timing includes packet creation, serialization, token estimation and literal-retention checks in one local pass. Allocation peaks come from Python tracing and exclude native allocations. Timings and allocation peaks are descriptive.

Extraction preserved the critical units, thresholds, qualifications and both sides of the conflicting-note case. It omitted eight other annotations across six cases, including scheduling and equipment details and the caveat that neither guide reports pot size. The mixed-script case required raw fallback. Tests exercise the fallback and mandatory independent review of proposed summaries. They provide no evidence about unsupported claims in real NCM output.

## Reproduce and verify

Run the focused tests with `python -m pytest tests/test_ncm_flowers_pilot.py`. Run the comparison with `python scripts/experiments/ncm_flowers_pilot.py --gpt2-tokenizer LOCAL_TOKENIZER_JSON` for the token estimates, or omit the option to measure bytes and literal retention without a tokenizer. The 50 focused tests passed with the pilot worktree first on the Python import path. The full trace belongs in local evidence. The published [metrics](ncm_flowers_synthetic_metrics.json) contain only aggregate synthetic measurements.

The original WHS paraphrase regression evidence matched its recorded hashes. WHS #8 acceptance remains open pending independent annotation review, consumer-token accounting and live Chronicle validation. This pilot uses its own experimental extractor and leaves the canonical Chronicle pipeline untouched.
