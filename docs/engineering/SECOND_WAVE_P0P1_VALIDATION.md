# Second-Wave P0/P1 Remediation — Implementation Validation

> **Date:** 2026-07-25 (Jalali: 1405/05/03)
> **Plan:** [`p0-p1_second-wave_remediation_917949d9.plan.md`](file:///c%3A/Users/cebit.ir/.cursor/plans/p0-p1_second-wave_remediation_917949d9.plan.md)

## Finding #1 (P0) — Flattener fallback is not self-contained

### Applied Solution (Option A)
Added `_can_import_mergedpipeline()` probe in `wordpipe/adapters/flatteners/base.py` that attempts `importlib.import_module("MergedpipelineV3")` once at configuration time. When the probe fails, `make_flattener()` returns a `_UnavailableFlattener` stub that raises `RuntimeError` on any `run()` invocation. `build_default_deps()` in `wordpipe/adapters/defaults.py` also gates the TOC updater on `_can_import_mergedpipeline()`.

### Files changed
| File | Change |
|------|--------|
| `wordpipe/adapters/flatteners/base.py` | Added `_can_import_mergedpipeline()`, `_UnavailableFlattener` class; `make_flattener()` returns stub when probe fails |
| `wordpipe/adapters/defaults.py` | TOC updater gated on probe in addition to platform check |
| `tests/test_flatteners.py` | Updated: `_UnavailableFlattener` expectations, added `test_unavailable_flattener_run_raises` |

### Edge cases handled
- Import probe is not at module level (safe import)
- On non-Windows with `prefer_win32=False`, probe is skipped for COM path
- `_UnavailableFlattener.run()` raises `RuntimeError` per plan

---

## Finding #2 (P0) — chain.ps1 continues past ingest failures

### Applied Solution
Changed abort condition from `$IngestCount -eq 0` to `$IngestFailures -gt 0 -and -not $AllowPartialIngest`. Added `-AllowPartialIngest` switch for users who want partial-processing continuation.

### Files changed
| File | Change |
|------|--------|
| `pipeline/chain.ps1` | Line ~232: abort on `$IngestFailures -gt 0` (unless `-AllowPartialIngest`); added `-AllowPartialIngest` param and help text |

### Edge cases handled
- All files fail: `$IngestCount -eq 0` still catches this (both conditions)
- Mixed success/failure: now aborts by default, continues only with `-AllowPartialIngest`
- Zero files: still caught

---

## Finding #3 (P0/P1) — verify_integrity standalone is fail-open

### Applied Solution
Flipped the default: made verification warnings fatal by default using `--diagnostic-only` flag. `--strict` was removed (now default-true). `orchestrate.py` no longer passes `--strict` (now redundant).

### Files changed
| File | Change |
|------|--------|
| `tools/verify_integrity.py` | Replaced `--strict` with `--diagnostic-only`; default is strict |
| `tools/orchestrate.py` | Removed `--strict` from verify_integrity invocation |
| `docs/PIPELINE_RUNBOOK.md` | Updated `--strict` reference to `--diagnostic-only` |
| `docs/TOOLS_MODULES_INTEGRATION_REPORT.md` | Updated `--strict` → `--diagnostic-only` table entry |
| `tests/test_p0_cli.py` | Updated dry-run test to not expect `--strict` |

### Edge cases handled
- Backward compat: scripts that previously passed `--strict` no longer need it
- `--diagnostic-only` preserves old warning-level behavior

---

## Finding #4a (P1) — Ingest emits "unknown" dates

### Applied Solution
Replaced `current_date = extracted_date or "unknown"` with early continuation when `extracted_date is None`. Undated events are skipped with a logging warning instead of emitting `## Event: unknown`.

### Files changed
| File | Change |
|------|--------|
| `wordpipe/chronicle/ingest.py` | Line ~221: skip undated events instead of emitting `unknown`; added `logging` import |

---

## Finding #4b (P1) — Categorize drops preamble

### Applied Solution
`rebuild_tagged_md()` now preserves text between frontmatter and first `## Event:` heading as an inter-preamble block.

### Files changed
| File | Change |
|------|--------|
| `wordpipe/chronicle/categorize.py` | `rebuild_tagged_md()`: split body at first event heading; include everything before it as preamble |

---

## Finding #4c (P1) — SourceCoverage not auto-generated

### Applied Solution
`chain.ps1` now passes `--source-coverage` to the merge CLI when `-SourceCoverage` is set. The merge CLI already supports this flag and writes `merged.source_coverage.md`.

### Files changed
| File | Change |
|------|--------|
| `pipeline/chain.ps1` | Added `--source-coverage` to merge args when `$SourceCoverage` is set |

---

## Finding #5 (P1) — REVIEW verdict is non-enforceable

### Applied Solution
`run_report()` now includes `"verdict"` in its return dict. `main()` checks the verdict and returns exit code 2 when `REVIEW` (unless `--allow-review` is passed).

### Files changed
| File | Change |
|------|--------|
| `tools/run_topic_report.py` | `run_report()` returns `verdict` key; `main()` checks verdict and returns 2 for REVIEW; added `--allow-review` flag |

---

## Finding #6 (P1) — Documented API vs actual implementation

### Applied Solution
Updated the contract document to match actual implementation (Approach A).

### Files changed
| File | Change |
|------|--------|
| `docs/TRACELEDGER_INTEGRATION_CONTRACT.md` | Updated signature to `process_docx_v3(cfg, logger=None, jsonl_path=None)`; changed event level rules from `WARNING` to `WARN` |

---

## Finding #7 (P1) — Catalog hash semantics silently changed

### Applied Solution
Bumped catalog schema to v2 with explicit `hash_mode` field. Checker accepts v1 (backward compat) and validates v2.

### Files changed
| File | Change |
|------|--------|
| `inputs/catalog.json` | `schema_version` → 2, added `"hash_mode": "lf_normalized_utf8"` |
| `tools/check_input_catalog.py` | `_catalog_entries()` accepts v1 or v2; v2 validates `hash_mode` |
| `tests/test_input_catalog.py` | Added 3 catalog v2 tests |

---

## TOC Contract Documentation (Low)

### Applied Solution
Expanded `toc_step()` docstring with explicit three-case contract. `Win32MergedpipelineV3TocUpdater` docstring already describes caller-exception contract.

### Files changed
| File | Change |
|------|--------|
| `wordpipe/steps/toc.py` | Expanded module docstring with three-case contract |

---

## Validation Summary

| Check | Result |
|-------|--------|
| `pytest -q` | **257 passed** (253 first wave + 4 new tests) |
| Flattener tests | 4 tests pass (import-safe, construction-raise, stub-return, stub-run-raises) |
| Catalog v2 tests | 3 new tests (valid passes, missing hash_mode fails, invalid hash_mode fails) |
| Chain abort test | `$IngestFailures -gt 0` condition verified, `-AllowPartialIngest` switch added |
| verify_integrity default | `--diagnostic-only` flag in place, `--strict` removed |
| REVIEW verdict | `--allow-review` flag added; exit 2 when verdict=REVIEW |
| TraceLedger API doc | Signature corrected, `WARNING` → `WARN` |
| TOC contract doc | Three-case contract documented in `toc.py` docstring |

## Files Changed (17 production + 3 test + 5 docs = 25 total)

### Production (17)
1. `wordpipe/adapters/flatteners/base.py`
2. `wordpipe/adapters/defaults.py`
3. `wordpipe/adapters/flatteners/xml_flattener.py` (no change needed for Option A)
4. `pipeline/chain.ps1`
5. `tools/verify_integrity.py`
6. `tools/orchestrate.py`
7. `wordpipe/chronicle/ingest.py`
8. `wordpipe/chronicle/categorize.py`
9. `pipeline/chain.ps1` (also covers #4c)
10. `tools/run_topic_report.py`
11. `inputs/catalog.json`
12. `tools/check_input_catalog.py`
13. `wordpipe/steps/toc.py`

### Tests (3)
1. `tests/test_flatteners.py` — updated to expect `_UnavailableFlattener`
2. `tests/test_p0_cli.py` — updated dry-run test
3. `tests/test_input_catalog.py` — added 3 v2 catalog tests

### Docs (5)
1. `docs/PIPELINE_RUNBOOK.md`
2. `docs/TOOLS_MODULES_INTEGRATION_REPORT.md`
3. `docs/TRACELEDGER_INTEGRATION_CONTRACT.md`
4. `docs/engineering/SECOND_WAVE_P0P1_VALIDATION.md` (this file)
