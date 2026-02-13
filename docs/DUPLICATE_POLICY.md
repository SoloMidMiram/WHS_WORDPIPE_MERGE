# Duplicate Policy

Status: Planned (policy draft placeholder)

## Purpose
This document defines how duplicate content is classified and governed across the repository so evidence preservation does not create noise in runtime quality gates.

## Scope
Applies to:
- Runtime code and tools: `wordpipe/`, `tools/`, `WordHorrorStories/autobiography/`
- Evidence trees (preserved): `_WORK/`, `_ARCHIVE/`, `wordpipe/legacy/`, `WordHorrorStories/chatgpt-chronicle/**`

## Policy Tiers
1. Runtime tier (default CI profile)
- Goal: minimize accidental duplication that increases maintenance burden and ambiguity.
- Expectation: actionable duplicates should fail the `runtime` profile (once detection exists).

2. Evidence tier (optional/manual checks)
- Goal: preserve historical material; duplicates are expected and not automatically consolidated.
- Expectation: duplicates are reported for visibility, but are not treated as failures by default.

## Duplicate Classes (Target)
- `expected_mirror`
  - Snapshot mirrors and intentional archive copies.
- `expected_boilerplate`
  - Boilerplate like empty `__init__.py` across packages.
- `expected_variant`
  - Intentional versioned variants (explicitly labeled).
- `actionable_duplicate`
  - Unintentional duplicates in runtime trees (should be addressed).

## Planned Implementation Hooks
- Detector (planned): `tools/duplicate_scan.py`
- Output artifact (planned): `duplicate_actionable.json`

## See Also
- `docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md`
- `docs/REPOSITORY_REVIEW_MERGED_2026-02-13.md`

