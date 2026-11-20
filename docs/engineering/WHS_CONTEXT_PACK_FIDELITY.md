# WHS-AI-01 Chronicle context packs

**REVISE.** B1 improved literal retention over frozen B0 and exceeded the estimated token reduction target. A delivered holdout packet omitted one critical qualification, so the critical-fact gate remains open. This is a synthetic benchmark for [WHS #8](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/8).

## Export contract

Run `python -m scripts.experiments.chronicle_context_pack --run-dir RUN_DIR --source-root SOURCE_ROOT --receipt RECEIPT_JSON --query QUERY --max-bytes 65536`.

The optional exporter reads a completed generic Markdown Chronicle run. The trusted `whs-context-receipt-v1` JSON has an `artifacts` mapping of run-relative paths to SHA-256 and a `sources` mapping of Markdown basenames to SHA-256. Capture source hashes from the known input set before running Chronicle and bind them to reviewed output hashes. Recomputing hashes for an unknown or stale run cannot establish what its original sources were. The required artifacts are the topic run manifest, both lineage and correlation sidecars, tagged Markdown and tagged JSON, pipeline run record, event index, and the pinned anchored navigation copy when present.

The exporter checks pinned byte digests, shared run and topic identity, successful stages, canonical report and source-event ID recomputation, locator identities, survivor keys, tagged metadata, and unique rendered local navigation. The packet carries the existing survivor anchor and exact file digest, H2 section ordinal and start line. The anchor already encodes the Chronicle date and normalized body hash. The exporter verifies the existing IDs internally and avoids duplicating their digest strings in every packet. The receipt digest identifies this set of input pins. Chronicle dates remain Chronicle metadata. Publication-date semantics are unverified.

B1 returns whole source H2 sections, all exact matches, and adjacent named qualifications in the same file. It resolves terms deterministically and keeps exact identifiers distinct. It returns the full verified raw source for insufficient matches, rejected ingest, or a structural packet that cannot satisfy the byte budget or is larger than raw. A stale or ambiguous source, malformed or mismatched run, missing navigation, or raw packet over budget produces a refusal with no evidence on stdout and exit 2. The UTF-8 byte budget applies to compact JSON before its terminal newline. The `--max-bytes` setting controls delivery, including fallback. Input verification has a separate 32 MiB cap.

## Observed comparison

The 24 synthetic cases are split into 12 tuning and 12 holdout cases. B1 was frozen at `d685e56111a83b54bc4b58d00ae83ff95dd9543c` before the holdout fixture and gold were authored or scored. Source and query inputs and gold live in separate files. Gold is consulted after selection for scoring. A second annotator has not reviewed the references.

| Scope | Arm | Critical retained | Overall retained | Median estimated token reduction vs raw |
| --- | --- | ---: | ---: | ---: |
| Tuning | A raw | 22/22 | 32/32 | 0.00% |
| Tuning | B0 top two | 3/22 | 12/32 | 70.54% |
| Tuning | B1 structural | 22/22 | 32/32 | 35.43% |
| Holdout | A raw | 23/23 | 33/33 | 0.00% |
| Holdout | B0 top two | 4/23 | 13/33 | 56.53% |
| Holdout | B1 structural | 21/23 | 31/33 | 52.00% |
| Combined | A raw | 45/45 | 65/65 | 0.00% |
| Combined | B0 top two | 7/45 | 25/65 | 56.74% |
| Combined | B1 structural | 43/45 | 63/65 | 46.07% |

B1 delivered 18 structural packets and three raw fallbacks. All **21/21 delivered packets** matched their pinned identities and verified survivor data where applicable. No unsupported units were observed in the verbatim comparison. The delivered packets retained **43/44 critical facts**, including **21/22** on holdout. The distant coolant qualification was outside the adjacent window. The budget refusal withheld an otherwise available critical fact. Both index faults refused delivery at the shared provenance boundary in all arms. They carry no scorable facts. The budget-refused case remains in B1's fact denominator. All three refusals earn zero token savings in the median. The three B1 fallbacks cost 737, 858 and 859 estimated tokens, respectively. The rejected-ingest case injects a synthetic chain receipt fault to exercise fallback.

The same source and query inputs were presented to A and frozen B0 through the same envelope. B0 reuses the merged top-two-line implementation. Its original 16/23 critical, 18/33 overall and 21.40% token-reduction result belongs to the earlier eight-case suite. Both historical metric files and original fixtures are unchanged. The separately recorded paraphrase miss (`loose-paraphrase`) keeps its original hashes and remains outside these 24 cases. NCM remains blocked and its incremental reduction unmeasured.

## Measurement and interpretation

GPT-2 BPE from the pinned public tokenizer asset, using the existing local `tokenizers 0.23.3`, estimates the complete compact JSON packet, including instructions, query, provenance, reasons and fallback. The target coding-agent tokenizer and actual billed usage were unavailable. Metadata-only counts have empty evidence text and are separate tokenizations. The reported input reread bytes are the raw sources read per run verification. The simulated consumer makes no follow-up source rereads because the packet includes evidence text. Any consumer that follows links would incur additional cost. No worker or hosted service participated.

The structured [metrics](whs_context_pack_metrics.json) record fallback costs, misses, timing and memory. Packet timings include retrieval and serialization and exclude receipt validation and tokenizer time. Python allocation peaks use `tracemalloc` and exclude RSS and native allocations. The metrics record one separate run-verification measurement for each partition. Packet hashes replayed identically, verified source and run pins were unchanged, and the actual CLI produced byte-identical replay on a synthetic Chronicle run. The initial tuning invocation picked up an older checkout through the local Python import path. The benchmark now explicitly runs the Chronicle child processes against this checkout.

The tuning and holdout runs used the real topic runner over synthetic sources. Normal tests use synthetic local inputs and no optional tokenizer or remote services. Run `python -m pytest tests/test_chronicle_context_pack.py -q` for focused checks. For an explicit benchmark run, use a fresh local evidence path with `python -m scripts.experiments.benchmark_context_pack --partition holdout --work _WORK/NEW_RUN --gpt2-tokenizer LOCAL_TOKENIZER_JSON`. Omit the tokenizer option to measure bytes. Use `--partition tuning` to replay tuning separately.

This slice qualifies the verified generic Markdown path on synthetic data. Restricted Flowers inputs, other adapters, independent annotation adjudication, actual consumer context accounting and production acceptance remain outside the observed results. Preserve the failed holdout as a regression and use a fresh holdout for any later algorithm revision.
