# MD-01 pilot — ChatGPT agent history and incidents

Five authorized, public Markdown sources were copied from the catalog and
verified against their original raw SHA-256 hashes before and after the
pilot. The run used source-tree qualification on native Windows at
3d32ba1ce4292a44a6a509c5a4d3585fc884f9ae. The production baseline was
1295ad15cc085732391a6d1dfe8069de32752ad1.

## Measured results

| Measure | Legacy | Structural |
| --- | ---: | ---: |
| First run / replay wall time | 32.51 / 35.27 s | 34.60 / 42.58 s |
| Median wall time | 33.89 s | 38.59 s |
| Median events/s | 0.502 | 0.445 |
| Events merged per run | 17 | 17 |
| Reported errors and duplicate conflicts | 0 | 0 |
| Resolved event / theme index links per run | 17 / 85 | 17 / 85 |

All four registered runs completed in 145.25 s within the 1,000 s admission
budget. Both mode pairs matched 17 headings and all body hashes. Source and
report IDs remained distinct across modes and stable on same-mode replay.
Structural spans accounted for all 247,046 bytes and 2,535 physical lines.
The summary counted 2,540 lines, reproducing the trailing-newline metric
discrepancy under [MD-01 #15](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/15).

All 17 dates were assigned the same fallback date, 2026-07-16. Source
citations can recover incident timing, but the generated chronology cannot
order incidents. Carry that finding into TIME-01. The configured theme index
supports navigation; the tag rate alone does not establish topic relevance.
There was no demonstrated semantic deduplication defect.

The pinned, local GPT-2 tokenizer counted 87,421 raw, 87,915 merged, and
89,448 tagged tokens. The event and theme indexes contained 2,152 and 8,040
tokens respectively. These are representation-size estimates. Correctness-
adjusted savings remain unmeasured under [G1 #8](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/8).
Runtime results feed [#38](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/38)
as a distinct real workload. Two runs per mode do not support tail estimates
or performance thresholds.

## Evidence inventory

- [Metrics](metrics.json) includes per-run wall time, stage durations,
  throughput, survivor checks, dates, themes, link resolution, and token counts.
- [Inputs](inputs.json), [registration](registration.json), and
  [environment](environment.json) identify the workload and fixed run order.
  The original [legacy](legacy.json) and [structural](structural.json) manifests
  retain their recorded hashes. Their relative paths refer to the local
  pilot workspace.
- [Run receipts](run.jsonl) contain the four start and terminal records. Find
  terminal records with rg -n -F RUN_END run.jsonl or PowerShell Select-String.
  Use a JSON parser for counts and statistics.
- [Research questions](questions.json) were fixed before execution. The
  measurement used local keyword and provenance checks, with CPU, RSS and
  model-based evaluation deferred. No model calls were made.

Raw source snapshots, Chronicles, detailed comparisons and logs are retained
in the local pilot workspace. G2 remains REVISE and the pilot did not change a
release gate, execution slot, threshold or production file.

## Maintainer disposition

**ACCEPT pilot execution as characterization evidence. REVISE product
usefulness.** Semantic and release acceptance remain separate. Preserve these
inputs, parser modes, GPT-2 estimates and findings as the TIME-01 and future
context-efficiency comparison baseline.

The existing artifacts were inspected without rerunning the pilot. Both
modes and both replays reported one source, **Merged Chronicle**, in the
source manifest. Their lineage contains five distinct original contributors.
This is a presentation-layer fidelity discrepancy. Track it under MD-01
[#15](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/15) and CORE-01.

Each link registry labels **30** as total unique links. The Markdown tables
contain **162** distinct URL strings, **45** after stripping fragments, across
**30** domain headings. The displayed total matches the domain count. Clarify
the intended URL identity before changing the count. Track this under MD-01
and CORE-01.

| Follow-up | Existing ownership |
| --- | --- |
| Source manifest and link counts | MD-01 / CORE-01 |
| Incident dates and fallback semantics | TIME-01 |
| Context-size growth and evidence retention | G1 [#8](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/8) |
| Domain-appropriate categorization | ONT-01 / NLP-01 |
| Physical-line summary overcount | MD-01 |
| Descriptive runtime comparison | [#38](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/38) / PERF-01 |

The structural median was 13.9% higher in two observations per mode. This
does not establish a performance regression or justify a new budget. No
correction, new slot, corpus expansion, or release-gate change is recorded.
