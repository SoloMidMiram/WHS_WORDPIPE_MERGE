# Issue #38 measurement checkpoint

The checkpoint is REVISE. It preserves sanitized measurements from six prior
single-file runs and a separate, frozen five-document synthetic cohort. It
does not contain raw logs, local paths, corpus excerpts, or session telemetry.
No historical workload was rerun.

From a fresh clone, run:

    python scripts/measurement/issue38/test_collect.py
    python scripts/measurement/issue38/collect.py scripts/measurement/issue38/evidence

The focused tests verify the fixture bytes, manifests, registration and
sanitized receipts. The collector computes wall and stage distributions,
throughput and failure rates. Integrity verdicts in the sanitized historical
receipts were established before export; reproduction recalculates the
aggregates. Use rg or PowerShell Select-String to locate attempt IDs in JSONL.
Use the JSON parser for statistics.

## Native observer

On Windows 26300 and Python 3.11.4, three synthetic Job Object probes recorded
1, 2 and 3 lifetime members and zero active members after exit. The two terminal
queries together took 41–74 microseconds. Lifetime CPU combines user and kernel
time for job members. Peak job commit measures committed memory. Sampled RSS
measures resident memory at observation points and is unavailable here.
Terminal query timings do not establish whole-observer overhead or qualification
on Chronicle's nested jobs. See evidence/windows-job-probes.json. The probe
script has a three-attempt cap and a ten-second wait per process.

Defer CPU, commit and RSS for cohort acceptance. Request maintainer approval
to execute the six registered attempts with wall time, throughput, correctness
and provenance. Keep the existing executor, quality and release limits, and
stop admitting work after the registered budget. Native observer results
remain synthetic characterization and existing soft limits remain advisory.

The historical engineering sample has no established matched pair. This
checkpoint adds no model calls, production changes or release decision.

## Registered cohort outcome

All six pre-registered Windows attempts completed in 124.55 seconds of the
300-second budget at checkpoint 6e86cdb. Both modes merged five events per
attempt with zero reported errors and stable same-mode lineage and correlation.
All three cross-mode pairs matched five headings. The fixture hashes were
preserved. CPU and RSS qualification was deferred in this run.

| Mode | Wall min / median / max (s) | Wall IQR / MAD (s) | Median events/s |
| --- | ---: | ---: | ---: |
| Legacy | 18.91 / 20.88 / 21.85 | 1.47 / 0.97 | 0.239 |
| Structural | 20.40 / 20.78 / 21.48 | 0.54 / 0.37 | 0.241 |

For this synthetic Windows workload only, propose an advisory warning at 25 s
per run, rounding the observed maxima upward to a five-second boundary. A
separately approved one-time advisory allowance could extend to 30 s, adding
the observed IQR rounded upward to five seconds. No automatic allowance or
threshold change. Three observations per mode do not establish upper tails.
Independent confirmation is still needed for operational limits.

See evidence/topic-cohort.jsonl and evidence/topic-cohort-summary.json.
READY FOR PILOT on these measured axes, subject to separate real-input
authorization. No further runs or observer experiments were made.

The [ChatGPT agent history pilot](../../../docs/engineering/pilots/md01-chatgpt-agent-history/README.md)
records the separate real-input workload. Its metrics are not pooled with
this synthetic cohort.
