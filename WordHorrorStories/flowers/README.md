# Flowers seven-document pilot

Current status (2026-11-22): [PR #7](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/pull/7) merged the engineering
changes. The dated seven-source navigation PASS remains recorded in
[ACCEPTANCE_02.md](ACCEPTANCE_02.md). G3-full semantic acceptance remains
REVIEW under queued [#16](https://github.com/SoloMidMiram/WHS_WORDPIPE_MERGE/issues/16). G3-core is a separate synthetic v0.2
gate. Restricted sources and row-level evidence remain local.
Earlier observations below are historical.

Verdict: REVIEW. This is partial evaluation, not publication acceptance.

Seven user-supplied UTF-8 research reports total 233194 bytes. Raw hashes and heading inventories are in source_inventory.json. Source text and derived standard runner artifacts remain local under output/ because redistribution rights are unverified. Embedded citation tokens are historical source claims, not independently verified references. Dates in bodies must not be interpreted as publication dates.

Baseline, candidate and repeat used the same read-only external source directory. Each output directory was checked absent before execution. All three prepare/pipeline/summarize stages exited zero in all runs. See pilot_metrics.json for observed counts and timings. CommonMark inspection independently found 44 nonempty H2 sections. All seven documents have preambles outside the adapter's extraction boundary; this is a known coverage limitation, so the runner's 100% coverage is not complete-document recall. Local output/literature_review retains 44 title suggestions with source line ranges, original headings and pending review status. No semantic consolidation was performed.

## Reproduction

Obtain the seven originals matching source_inventory.json. Keep them read-only. Copy topic_manifest.json to topic_manifest.local.json and set input_dir to their directory. The example canonical directory is intentionally absent: originals are not redistributed or registered as committed corpus. Run python tools/run_topic_report.py --manifest WordHorrorStories/flowers/topic_manifest.local.json --run-id YOUR_UNIQUE_ID only after confirming its output directory does not exist. Standard runner artifacts contain source text: do not publish without rights review.

## Narrow regression

parse_file silently replaced invalid UTF-8. The new isolated temporary-file regression failed (1 failed, 15 passed), then passed after strict decoding (16 passed). Valid UTF-8 behavior is unchanged; invalid input now raises UnicodeDecodeError with its original cause. No subprocess exception handling changed.

## Reconciliation and boundaries

Original checkout: codex/chronicle-run-evidence at 364d7fd; local main 06209c2; origin/main d9ef212135c049390a234bf33e70b1380cb8d03f. Existing dirty files were not edited. Independent managed worktree starts at that origin/main, branch pilot/flowers-seven-md-20261118. A repeated fetch encountered GitHub DNS failure after the earlier successful fetch. Repository-local core.longpaths=true was required for managed worktree creation.

GitHub API reports PR 6 open at acbac03c22e406a88fbf342a8f75b333c78efbb3 and PR 5 open at 315cd4fb0c29a7e903d9346596e9f31ba3794c7d, stacked on PR 6. Neither was incorporated. Configuration validation belongs to PR 6; survivor indexing and Unicode navigation belong to PR 5. Their historical CI descriptions do not establish current checks.

## Findings and follow-up

- REPRODUCED_REGRESSION: silent UTF-8 replacement in generic parse_file, fixed with focused test.
- DESIGN_LIMITATION: generic adapter uses regex H2 boundaries, omits preambles and assigns fallback date 2026-07-16. Canonical schema unchanged; derived dates unsuitable as publication assertions.
- ALREADY_HANDLED_BY_OPEN_PR: malformed theme metadata and survivor/Unicode indexing; await independent PR 6/5 review.
- UNVERIFIED_RISK: timeout/child termination, repeated aliases and Unicode path collisions require dedicated characterization. No timeout safety claim.
- Required follow-up: manually label each source and suspicious relationships; measure category precision/recall and title acceptability; inspect all survivor links; assess Unicode/ZWNJ matching and meaningful negative keywords. Current taxonomy is provisional.
- Duplicate/contradiction semantic assessment and full ground-truth acceptance remain incomplete. Zero pipeline conflict candidates does not prove absence of semantic duplicates.

Input-catalog, architecture-boundary and documentation-link checks passed. Root-layout check fails on the managed worktree .git file; do not change governance to hide this. Full-suite and security results must be read from the execution report, not inferred from historical tests.

## Observed validation results

Full suite: 323 passed, 1 failed in 208.98 seconds; only test_current_repository_root_matches_allowlist failed on .git. No skipped tests reported. Final focused adapter suite: 16 passed. Security scan: 971 files, zero findings. git diff --check passed. Review API: PR 5 has one COMMENTED automated review on older f69a7017f0; PR 6 has no submitted reviews. Current-head CI checks remain unverified. Git fetch/ls-remote repeatedly failed with Could not resolve host: github.com.
