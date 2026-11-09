# Tools Modules Integration Report

## See Also
- `docs/README.md`
- `docs/LOGIC_FLOW_BEFORE_AFTER_TRACELEDGER.md`

## Executive Introduction
This report documents the `tools/` pipeline as a single architecture narrative for operators and engineers.

Objective:
- Keep copy-only merge behavior intact.
- Make module interfaces predictable and independently runnable.
- Make data flow and control flow auditable from manifest generation through verification.

Safety guarantees:
- No destructive move/delete behavior in pipeline stages.
- Conflict-safe copy behavior in apply stage.
- Append-only audit logging for operational traces.
- Deterministic report/artifact regeneration where expected.

### Frozen Baseline Banner
- `total_files`: 98
- `legacy_candidates`: 25 (`ai`: 18, `misc`: 7)
- `apply`: `copied_current=71`, `legacy_copied=25`, `errors=0`
- `verify`: `failures=0`, `accounted=98/98`, `duplicates=9`

Operator value:
- One command can run the full documented flow.
- Every stage can still run standalone.
- Evidence is split into audit logs (append-only) and reports (replace-on-run) for clear operations and QA.

## Where This Fits in TraceLedger
This document describes the **evidence pipeline** (`tools/`) and its artifacts. TraceLedger should primarily integrate with **WordPipe runtime** (`wordpipe/`) as a library and use `tools/` only as an optional audit/evidence subsystem when needed.

## Scope and Artifact Chain
In-scope modules:
- CLI stages: `tools/make_manifest.py`, `tools/plan_legacy_reorg.py`, `tools/apply_legacy_reorg.py`, `tools/build_legacy_index.py`, `tools/verify_integrity.py`
- Optional CLI composition/auxiliary: `tools/route_unmapped_misc.py`, `tools/orchestrate.py`
- Shared internal modules: `tools/tool_common.py`, `tools/pipeline_contracts.py`, `tools/jalali.py`

Canonical artifact chain:

```text
manifest.jsonl -> relocation_plan.jsonl -> relocation_map.jsonl -> LEGACY_INDEX.md + verify outputs
```

## Evidence and Validation Method
Source of truth used for this report:
1. CLI interface capture via each script `--help` output.
2. Argparse default and behavior verification by static inspection.
3. Artifact and side-effect verification by source inspection and current workspace logs/artifacts.
4. Statements included only where repository evidence exists.

## Module Introductions
Each module card uses fixed fields: `Purpose`, `Role`, `Inputs`, `Outputs`, `Side Effects`, `Independent CLI Run`, `Failure Surface`.

### `tools/make_manifest.py`
- Purpose: Generate manifest files from snapshot content.
- Role: Stage 1 producer for downstream planning and verification.
- Inputs: Snapshot root (`--root`), workspace root (`--workspace-root`), optional auto-normalize switch.
- Outputs: `_ARCHIVE/manifests/manifest.csv`, `_ARCHIVE/manifests/manifest.jsonl`; optional setup log note for root normalization.
- Side Effects: Computes SHA256 and timestamps for all files under effective snapshot root.
- Independent CLI Run: Yes.
- Failure Surface: Missing snapshot root directory, per-row processing exceptions, strict-mode escalation of warnings.

### `tools/plan_legacy_reorg.py`
- Purpose: Build relocation plan for legacy candidates.
- Role: Stage 2 planner consuming manifest rows.
- Inputs: Manifest (`--manifest`), snapshot root (`--root`), output/log paths.
- Outputs: `_ARCHIVE/move_maps/relocation_plan.jsonl`, append to `_ARCHIVE/logs/plan.log`.
- Side Effects: Classifies area/confidence/rule hits and computes destination bucket paths.
- Independent CLI Run: Yes.
- Failure Surface: Missing required manifest, strict-mode escalation of warnings.

### `tools/apply_legacy_reorg.py`
- Purpose: Apply relocation plan with copy-only, conflict-safe writes.
- Role: Stage 3 executor for current content copies and legacy routing.
- Inputs: Relocation plan (`--plan`), snapshot root (`--root`), destination map/log paths, preflight switch.
- Outputs: `_ARCHIVE/move_maps/relocation_map.jsonl`, append to `_ARCHIVE/logs/apply_reorg.log`, append to `_ARCHIVE/logs/conflicts.log`.
- Side Effects: Copies files into `wordpipe/` and `WordHorrorStories/`; writes `_conflicts/` files when hashes differ.
- Independent CLI Run: Yes.
- Failure Surface: Missing required plan, preflight abort with `--preflight-mode error`, copy exceptions, strict-mode escalation.

### `tools/build_legacy_index.py`
- Purpose: Generate readable legacy navigation indexes.
- Role: Stage 4 documentation/index generation.
- Inputs: Relocation map path, legacy roots, index outputs, log path, workspace root.
- Outputs: `wordpipe/legacy/LEGACY_INDEX.md`, `WordHorrorStories/legacy/LEGACY_INDEX.md`, append to `_ARCHIVE/logs/legacy_index.log`.
- Side Effects: Traverses legacy directories and enriches bucket statistics from relocation map when present.
- Independent CLI Run: Yes.
- Failure Surface: Missing/empty relocation map and missing legacy roots are warnings; strict mode can escalate warnings.

### `tools/verify_integrity.py`
- Purpose: Validate integrity/coverage and emit consistency/immutability evidence.
- Role: Stage 5 QA gate and reporting.
- Inputs: Manifest (`--manifest`), plan (`--plan` optional), relocation map (`--relocation` optional), snapshot root (`--snapshot-root` required dir), workspace root.
- Outputs: `_ARCHIVE/logs/verify_report.md`, `_ARCHIVE/logs/verify_report.json`, `_ARCHIVE/logs/consistency_report.json`, `_ARCHIVE/logs/immutability_report.json`.
- Side Effects: Re-hashes destination and snapshot files; computes consistency and immutability checks.
- Independent CLI Run: Yes.
- Failure Surface: Missing required manifest or snapshot directory; warning states for missing plan/map and non-OK report states; strict mode escalation.

### `tools/route_unmapped_misc.py`
- Purpose: Optionally route snapshot root docs to `_META` copy-only.
- Role: Optional auxiliary step after apply.
- Inputs: Snapshot root (`--root`), destination root (`--dest`), log path (`--log`), optional auto-normalize switch.
- Outputs: Append to `_ARCHIVE/logs/route_unmapped.log`; optional copied files under `_META/...`.
- Side Effects: Attempts copy of `README.md` and `MERGE_MAP.md` using conflict-safe copy.
- Independent CLI Run: Yes.
- Failure Surface: Missing files are logged as `missing`; no StageResult/strict contract currently.

### `tools/orchestrate.py`
- Purpose: Compose stage CLIs into one command execution flow.
- Role: Pipeline runner and dry-run command printer.
- Inputs: Workspace root (`--workspace-root`), snapshot root (`--root`), switches `--dry-run`, `--run-route-unmapped`.
- Outputs: Command echo to stdout; subprocess exit propagation.
- Side Effects: Executes stage scripts in order unless `--dry-run`.
- Independent CLI Run: Yes.
- Failure Surface: First non-zero subprocess exits orchestrator and prints `ERROR: command failed ...`.

### `tools/tool_common.py`
- Purpose: Shared primitive utilities.
- Role: Internal helper module used by stages.
- Inputs: Paths/hashes/log payloads provided by callers.
- Outputs: Hash strings, normalized paths, appended log blocks, copy status tuples.
- Side Effects: File hashing, file copy operations, append-only log writes.
- Independent CLI Run: No (library module).
- Failure Surface: Caller-level path and filesystem errors.

### `tools/pipeline_contracts.py`
- Purpose: Shared typed stage contract and path/error helpers.
- Role: Internal interface layer for consistent stage behavior.
- Inputs: Stage metadata and path values from stage modules.
- Outputs: `StageResult` JSON payloads, normalized absolute paths, standardized missing-input error emission.
- Side Effects: Writes optional summary JSON and standardized stderr errors.
- Independent CLI Run: No (library module).
- Failure Surface: Path and serialization errors surfaced to caller.

### `tools/jalali.py`
- Purpose: Gregorian-to-Jalali conversion helpers.
- Role: Internal date conversion support for manifest/planning.
- Inputs: Gregorian date components or datetime object.
- Outputs: Jalali tuple/string representations.
- Side Effects: None.
- Independent CLI Run: No (library module).
- Failure Surface: Invalid date values from caller.

## Arguments, Placeholders, and Switches
Columns:
- `Flag`: CLI switch.
- `Type`: Path/string/enum/bool.
- `Default`: Parser default.
- `Required`: Runtime requirement.
- `Placeholder Token`: Reference token from dictionary.
- `Behavior`: Effective behavior.
- `Invalid Input Outcome`: Runtime result on invalid/missing input.
- `Compatibility Note`: Backward-compatibility status.

### `tools/make_manifest.py`
| Flag | Type | Default | Required | Placeholder Token | Behavior | Invalid Input Outcome | Compatibility Note |
|---|---|---|---|---|---|---|---|
| `--root` | path | `_WORK/snapshot` | Yes (directory) | `<SNAPSHOT_ROOT>` | Source root for scan; auto-normalized unless disabled. | `ERROR: required snapshot root directory not found: {abs_path}`, exit non-zero. | Existing default preserved. |
| `--out-dir` | path | `_ARCHIVE/manifests` | No | `<LOG_PATH>` | Directory for `manifest.csv` and `manifest.jsonl`. | Parent dir auto-created. | Existing default preserved. |
| `--workspace-root` | path | `.` | No | `<WORKSPACE_ROOT>` | Base for resolving relative paths. | Bad path can fail downstream IO. | Added shared contract flag. |
| `--summary-json` | path | `` | No | `<SUMMARY_JSON_PATH>` | Writes `StageResult` JSON when provided. | Write/serialize error if unwritable path. | Added shared contract flag. |
| `--strict` | bool | `false` | No | `(none)` | Converts warning-only result to error status. | Exit non-zero on warning states. | Added shared contract flag. |
| `--no-auto-normalize` | bool | `false` | No | `(none)` | Disables nested `snapshot/snapshot` root normalization. | None; may use unnormalized root. | Existing behavior preserved. |

### `tools/plan_legacy_reorg.py`
| Flag | Type | Default | Required | Placeholder Token | Behavior | Invalid Input Outcome | Compatibility Note |
|---|---|---|---|---|---|---|---|
| `--root` | path | `_WORK/snapshot` | No | `<SNAPSHOT_ROOT>` | Used to materialize `src_abs`; auto-normalized unless disabled. | If root does not exist, resulting `src_abs` may point to absent files later. | Existing default preserved. |
| `--manifest` | path | `_ARCHIVE/manifests/manifest.jsonl` | Yes (file) | `<MANIFEST_PATH>` | Input manifest rows for classification/planning. | `ERROR: required manifest.jsonl not found: {abs_path}`, exit non-zero. | Existing default preserved. |
| `--out` | path | `_ARCHIVE/move_maps/relocation_plan.jsonl` | No | `<PLAN_PATH>` | Output plan JSONL path (overwritten). | Parent dir auto-created. | Existing default preserved. |
| `--log` | path | `_ARCHIVE/logs/plan.log` | No | `<LOG_PATH>` | Append-only summary log. | IO failure if unwritable path. | Existing default preserved. |
| `--workspace-root` | path | `.` | No | `<WORKSPACE_ROOT>` | Relative path base. | Bad path can fail downstream IO. | Added shared contract flag. |
| `--summary-json` | path | `` | No | `<SUMMARY_JSON_PATH>` | Optional structured stage summary output. | Write error if path unwritable. | Added shared contract flag. |
| `--strict` | bool | `false` | No | `(none)` | Escalates warnings to errors. | Exit non-zero on warning states. | Added shared contract flag. |
| `--no-auto-normalize` | bool | `false` | No | `(none)` | Disables root normalization. | None. | Existing behavior preserved. |

### `tools/apply_legacy_reorg.py`
| Flag | Type | Default | Required | Placeholder Token | Behavior | Invalid Input Outcome | Compatibility Note |
|---|---|---|---|---|---|---|---|
| `--root` | path | `_WORK/snapshot` | No | `<SNAPSHOT_ROOT>` | Source root for current-file copy pass; auto-normalized unless disabled. | If invalid root, copy pass may do no useful work. | Existing default preserved. |
| `--plan` | path | `_ARCHIVE/move_maps/relocation_plan.jsonl` | Yes (file) | `<PLAN_PATH>` | Legacy relocation plan input. | `ERROR: required relocation_plan.jsonl not found: {abs_path}`, exit non-zero. | Existing default preserved. |
| `--out-map` | path | `_ARCHIVE/move_maps/relocation_map.jsonl` | No | `<MAP_PATH>` | Apply result mapping output (overwritten). | Parent dir auto-created. | Existing default preserved. |
| `--log` | path | `_ARCHIVE/logs/apply_reorg.log` | No | `<LOG_PATH>` | Append-only run summary log. | IO failure if unwritable. | Existing default preserved. |
| `--conflict-log` | path | `_ARCHIVE/logs/conflicts.log` | No | `<LOG_PATH>` | Append-only conflict summary log, includes `conflicts_total` even when zero. | IO failure if unwritable. | Additive new flag. |
| `--preflight-mode` | enum | `warn` | No | `(none)` | `warn`: continue with warning on non-empty targets; `error`: abort before copy; `off`: skip preflight warning logic. | Invalid value rejected by argparse; `error` mode returns non-zero on non-empty targets. | Additive new switch. |
| `--workspace-root` | path | `.` | No | `<WORKSPACE_ROOT>` | Relative path base. | Bad path can fail downstream IO. | Added shared contract flag. |
| `--summary-json` | path | `` | No | `<SUMMARY_JSON_PATH>` | Optional structured stage summary output. | Write error if path unwritable. | Added shared contract flag. |
| `--strict` | bool | `false` | No | `(none)` | Escalates warnings to errors. | Exit non-zero on warning states. | Added shared contract flag. |
| `--no-auto-normalize` | bool | `false` | No | `(none)` | Disables root normalization. | None. | Existing behavior preserved. |

### `tools/build_legacy_index.py`
| Flag | Type | Default | Required | Placeholder Token | Behavior | Invalid Input Outcome | Compatibility Note |
|---|---|---|---|---|---|---|---|
| `--workspace-root` | path | `.` | No | `<WORKSPACE_ROOT>` | Relative path base. | Bad path can fail downstream IO. | Additive explicit root support. |
| `--relocation-map` | path | `_ARCHIVE/move_maps/relocation_map.jsonl` | No | `<MAP_PATH>` | Optional enrichment input for confidence/labels. | Missing/empty map becomes warning; index still generated. | Additive explicit input flag. |
| `--wordpipe-legacy-root` | path | `wordpipe/legacy` | No | `<WORKSPACE_ROOT>` | Source tree for wordpipe index. | Missing root warning; index still written. | Additive explicit input flag. |
| `--whs-legacy-root` | path | `WordHorrorStories/legacy` | No | `<WORKSPACE_ROOT>` | Source tree for WHS index. | Missing root warning; index still written. | Additive explicit input flag. |
| `--wordpipe-index-out` | path | `wordpipe/legacy/LEGACY_INDEX.md` | No | `<LOG_PATH>` | Output path for wordpipe legacy index (overwritten). | Parent dir auto-created. | Additive explicit output flag. |
| `--whs-index-out` | path | `WordHorrorStories/legacy/LEGACY_INDEX.md` | No | `<LOG_PATH>` | Output path for WHS legacy index (overwritten). | Parent dir auto-created. | Additive explicit output flag. |
| `--log` | path | `_ARCHIVE/logs/legacy_index.log` | No | `<LOG_PATH>` | Append-only summary log. | IO failure if unwritable path. | Existing default preserved. |
| `--summary-json` | path | `` | No | `<SUMMARY_JSON_PATH>` | Optional structured stage summary output. | Write error if path unwritable. | Added shared contract flag. |
| `--strict` | bool | `false` | No | `(none)` | Escalates warnings to errors. | Exit non-zero on warning states. | Added shared contract flag. |

### `tools/verify_integrity.py`
| Flag | Type | Default | Required | Placeholder Token | Behavior | Invalid Input Outcome | Compatibility Note |
|---|---|---|---|---|---|---|---|
| `--manifest` | path | `_ARCHIVE/manifests/manifest.jsonl` | Yes (file) | `<MANIFEST_PATH>` | Manifest input for integrity and coverage checks. | `ERROR: required manifest.jsonl not found: {abs_path}`, exit non-zero. | Existing default preserved. |
| `--plan` | path | `_ARCHIVE/move_maps/relocation_plan.jsonl` | No | `<PLAN_PATH>` | Optional consistency input. | Missing file becomes warning. | Additive explicit input flag. |
| `--relocation` | path | `_ARCHIVE/move_maps/relocation_map.jsonl` | No | `<MAP_PATH>` | Optional integrity/consistency input. | Missing file becomes warning. | Additive explicit input flag. |
| `--snapshot-root` | path | `_WORK/snapshot` | Yes (directory) | `<SNAPSHOT_ROOT>` | Source root for immutability check; auto-normalized internally. | `ERROR: required snapshot root directory not found: {abs_path}`, exit non-zero. | Additive explicit input flag. |
| `--workspace-root` | path | `.` | No | `<WORKSPACE_ROOT>` | Relative path base. | Bad path can fail downstream IO. | Added shared contract flag. |
| `--summary-json` | path | `` | No | `<SUMMARY_JSON_PATH>` | Optional structured stage summary output. | Write error if unwritable. | Added shared contract flag. |
| `--diagnostic-only` | bool | `false` | No | `(none)` | Warnings do not cause non-zero exit. | Exit non-zero on actual error states. | Replaced `--strict` (now default-true). |

### `tools/route_unmapped_misc.py`
| Flag | Type | Default | Required | Placeholder Token | Behavior | Invalid Input Outcome | Compatibility Note |
|---|---|---|---|---|---|---|---|
| `--root` | path | `_WORK/snapshot` | No | `<SNAPSHOT_ROOT>` | Source root for optional routed docs; auto-normalized unless disabled. | Missing target files are counted/logged as `missing`. | Existing behavior preserved. |
| `--dest` | path | `_META/from_snapshot_20260211_205716` | No | `<WORKSPACE_ROOT>` | Destination root for routed docs. | IO failure if unwritable destination. | Existing behavior preserved. |
| `--log` | path | `_ARCHIVE/logs/route_unmapped.log` | No | `<LOG_PATH>` | Append-only routing log. | IO failure if unwritable. | Existing behavior preserved. |
| `--no-auto-normalize` | bool | `false` | No | `(none)` | Disables root normalization. | None. | Existing behavior preserved. |

### `tools/orchestrate.py`
| Flag | Type | Default | Required | Placeholder Token | Behavior | Invalid Input Outcome | Compatibility Note |
|---|---|---|---|---|---|---|---|
| `--workspace-root` | path | `.` | No | `<WORKSPACE_ROOT>` | Subprocess working directory for all stage commands. | Invalid path causes subprocess execution failure. | Additive composition helper. |
| `--root` | path | `_WORK/snapshot` | No | `<SNAPSHOT_ROOT>` | Passed through to root-aware stage commands. | Stage-level validation handles invalid root. | Existing default preserved. |
| `--dry-run` | bool | `false` | No | `(none)` | Prints resolved commands and executes nothing. | None. | Additive safety switch. |
| `--run-route-unmapped` | bool | `false` | No | `(none)` | Inserts `route_unmapped_misc.py` after apply stage. | Any non-zero inserted step aborts orchestration. | Additive optional step switch. |

## Placeholder Dictionary
- `<WORKSPACE_ROOT>`: Absolute or relative repo/workspace root used as path resolution base.
- `<SNAPSHOT_ROOT>`: Snapshot tree root containing source files.
- `<MANIFEST_PATH>`: `manifest.jsonl` input path.
- `<PLAN_PATH>`: `relocation_plan.jsonl` input/output path.
- `<MAP_PATH>`: `relocation_map.jsonl` input/output path.
- `<LOG_PATH>`: Any log/report/index/manifests output path depending on command context.
- `<SUMMARY_JSON_PATH>`: Optional path for machine-readable `StageResult` JSON output.

Path resolution rules:
1. If a CLI path value is absolute, use it as-is.
2. If relative, resolve as `<WORKSPACE_ROOT>/{value}`.
3. For root-aware stages (`make_manifest`, `plan_legacy_reorg`, `apply_legacy_reorg`, `route_unmapped_misc`), `auto_normalize_root` promotes nested `snapshot/snapshot` roots unless `--no-auto-normalize` is set.
4. `verify_integrity.py` auto-normalizes `--snapshot-root` internally for immutability checks.

## Before vs After Integration Map

### Before: Data-Lineage Flow (manual and implicit)
```text
_WORK/snapshot
  -> make_manifest.py
     -> _ARCHIVE/manifests/manifest.csv
     -> _ARCHIVE/manifests/manifest.jsonl

manifest.jsonl
  -> plan_legacy_reorg.py
     -> _ARCHIVE/move_maps/relocation_plan.jsonl

relocation_plan.jsonl + snapshot
  -> apply_legacy_reorg.py
     -> _ARCHIVE/move_maps/relocation_map.jsonl
     -> copy-only destination trees

relocation_map.jsonl + legacy roots
  -> build_legacy_index.py
     -> LEGACY_INDEX.md files

manifest + plan/map + snapshot
  -> verify_integrity.py
     -> verify reports
```

### Before: Control-Path Flow
```text
Operator runs 5 commands manually, in order.
Failures are stage-local. No single composition command.
Machine-readable per-stage summary contract is not guaranteed.
```

### After: Data-Lineage Flow (contracted and explicit)
```text
Stage 1 make_manifest
  produces manifest.csv + manifest.jsonl

Stage 2 plan_legacy_reorg
  consumes manifest.jsonl
  produces relocation_plan.jsonl

Stage 3 apply_legacy_reorg
  consumes relocation_plan.jsonl + snapshot root
  produces relocation_map.jsonl + conflicts.log
  writes copy-only trees and _conflicts paths when needed

Stage 4 build_legacy_index
  consumes relocation_map.jsonl (optional enrichment) + legacy roots
  produces two LEGACY_INDEX.md documents

Stage 5 verify_integrity
  consumes manifest.jsonl (+ optional plan/map) + snapshot root
  produces verify_report.md/json + consistency_report.json + immutability_report.json
```

### After: Control-Path Flow
```text
Option A: one-command orchestration via tools/orchestrate.py.
Option B: independent stage execution via each CLI.
Shared StageResult contract exists for core stages via --summary-json.
Consistent missing-required-input format exists for contracted stages.
```

## Logic Integration
### Path Normalization Precedence
1. Resolve `--workspace-root` to absolute path.
2. Resolve each relative argument path against workspace root.
3. Apply stage root normalization where implemented.

### Standardized Missing-Input Error Format
Contracted stages use:
- `ERROR: required {name} not found: {abs_path}`

Implemented for required-file/dir checks in:
- `make_manifest.py`
- `plan_legacy_reorg.py`
- `apply_legacy_reorg.py`
- `verify_integrity.py`

### Audit Logs vs Deterministic Reports
Append-only audit logs:
- `_ARCHIVE/logs/setup.log`
- `_ARCHIVE/logs/plan.log`
- `_ARCHIVE/logs/apply_reorg.log`
- `_ARCHIVE/logs/legacy_index.log`
- `_ARCHIVE/logs/conflicts.log`
- `_ARCHIVE/logs/route_unmapped.log`

Replace-on-run deterministic artifacts:
- `_ARCHIVE/manifests/manifest.csv`
- `_ARCHIVE/manifests/manifest.jsonl`
- `_ARCHIVE/move_maps/relocation_plan.jsonl`
- `_ARCHIVE/move_maps/relocation_map.jsonl`
- `wordpipe/legacy/LEGACY_INDEX.md`
- `WordHorrorStories/legacy/LEGACY_INDEX.md`
- `_ARCHIVE/logs/verify_report.md`
- `_ARCHIVE/logs/verify_report.json`
- `_ARCHIVE/logs/consistency_report.json`
- `_ARCHIVE/logs/immutability_report.json`

### Strict-Mode Escalation
For contracted stage scripts, `--strict` converts warning-only outcomes into error status via `StageResult.finalize(strict=True)`.

### Idempotency Notes by Stage
- `make_manifest.py`: Deterministic rewrite of manifest outputs.
- `plan_legacy_reorg.py`: Deterministic rewrite of relocation plan output.
- `apply_legacy_reorg.py`: Copy-only, non-destructive; same-content destinations are skipped; hash mismatches preserved in `_conflicts/`.
- `build_legacy_index.py`: Deterministic rewrite of index documents, append-only log.
- `verify_integrity.py`: Deterministic rewrite of report files.
- `route_unmapped_misc.py`: Copy-only behavior using conflict-safe copy.
- `orchestrate.py`: No direct artifact writes; composes subprocesses.

## Operational Usage
All examples are shown first with placeholders, then with one concrete path.

### Orchestrated Happy Path
```powershell
python tools/orchestrate.py --workspace-root <WORKSPACE_ROOT> --root <SNAPSHOT_ROOT>
python tools/orchestrate.py --workspace-root <WORKSPACE_ROOT> --root _WORK/snapshot
```

### Orchestrator Dry Run
```powershell
python tools/orchestrate.py --workspace-root <WORKSPACE_ROOT> --root <SNAPSHOT_ROOT> --dry-run
python tools/orchestrate.py --workspace-root <WORKSPACE_ROOT> --root _WORK/snapshot --dry-run
```

### Optional Route Step in Orchestration
```powershell
python tools/orchestrate.py --workspace-root <WORKSPACE_ROOT> --root <SNAPSHOT_ROOT> --run-route-unmapped
python tools/orchestrate.py --workspace-root <WORKSPACE_ROOT> --root _WORK/snapshot --run-route-unmapped
```

### Independent Stage Runs
```powershell
python tools/make_manifest.py --workspace-root <WORKSPACE_ROOT> --root <SNAPSHOT_ROOT>
python tools/make_manifest.py --workspace-root <WORKSPACE_ROOT> --root _WORK/snapshot
```

```powershell
python tools/plan_legacy_reorg.py --workspace-root <WORKSPACE_ROOT> --root <SNAPSHOT_ROOT> --manifest <MANIFEST_PATH> --out <PLAN_PATH>
python tools/plan_legacy_reorg.py --workspace-root <WORKSPACE_ROOT> --root _WORK/snapshot --manifest _ARCHIVE/manifests/manifest.jsonl --out _ARCHIVE/move_maps/relocation_plan.jsonl
```

```powershell
python tools/apply_legacy_reorg.py --workspace-root <WORKSPACE_ROOT> --root <SNAPSHOT_ROOT> --plan <PLAN_PATH> --out-map <MAP_PATH> --preflight-mode warn
python tools/apply_legacy_reorg.py --workspace-root <WORKSPACE_ROOT> --root _WORK/snapshot --plan _ARCHIVE/move_maps/relocation_plan.jsonl --out-map _ARCHIVE/move_maps/relocation_map.jsonl --preflight-mode warn
```

```powershell
python tools/build_legacy_index.py --workspace-root <WORKSPACE_ROOT> --relocation-map <MAP_PATH>
python tools/build_legacy_index.py --workspace-root <WORKSPACE_ROOT> --relocation-map _ARCHIVE/move_maps/relocation_map.jsonl
```

```powershell
python tools/verify_integrity.py --workspace-root <WORKSPACE_ROOT> --manifest <MANIFEST_PATH> --plan <PLAN_PATH> --relocation <MAP_PATH> --snapshot-root <SNAPSHOT_ROOT>
python tools/verify_integrity.py --workspace-root <WORKSPACE_ROOT> --manifest _ARCHIVE/manifests/manifest.jsonl --plan _ARCHIVE/move_maps/relocation_plan.jsonl --relocation _ARCHIVE/move_maps/relocation_map.jsonl --snapshot-root _WORK/snapshot
```

### Non-Repo CWD Operation
```powershell
python tools/build_legacy_index.py --workspace-root <WORKSPACE_ROOT>
```

## Known Limits and Deferred Work
- Parallel hashing is not implemented in stage scripts.
- Duplicate/hardlink consolidation is intentionally out of scope.
- Transactional rollback for partial failures is not implemented.
- `route_unmapped_misc.py` and `orchestrate.py` do not yet emit `StageResult` JSON.
- `route_unmapped_misc.py` does not yet expose shared `--workspace-root`, `--summary-json`, `--strict` flags.

## Documentation Accuracy Tests
1. Coverage test: confirm all 10 modules above are documented once.
2. Interface fidelity: each documented flag appears in corresponding script `--help`.
3. Placeholder fidelity: every placeholder token used in commands exists in placeholder dictionary.
4. Flow fidelity: data lineage includes manifest, plan, map, index outputs, and verify outputs.
5. Switch fidelity: `--preflight-mode`, `--dry-run`, `--run-route-unmapped`, and `--strict` defaults/outcomes documented.
6. Operator usability: happy path and dry-run commands are executable from this report alone.

## Quick Reference
### Command Index
- Stage 1: `python tools/make_manifest.py --workspace-root <WORKSPACE_ROOT> --root <SNAPSHOT_ROOT>`
- Stage 2: `python tools/plan_legacy_reorg.py --workspace-root <WORKSPACE_ROOT> --root <SNAPSHOT_ROOT> --manifest <MANIFEST_PATH>`
- Stage 3: `python tools/apply_legacy_reorg.py --workspace-root <WORKSPACE_ROOT> --root <SNAPSHOT_ROOT> --plan <PLAN_PATH> --preflight-mode warn`
- Stage 4: `python tools/build_legacy_index.py --workspace-root <WORKSPACE_ROOT> --relocation-map <MAP_PATH>`
- Stage 5: `python tools/verify_integrity.py --workspace-root <WORKSPACE_ROOT> --manifest <MANIFEST_PATH> --snapshot-root <SNAPSHOT_ROOT>`
- Full flow: `python tools/orchestrate.py --workspace-root <WORKSPACE_ROOT> --root <SNAPSHOT_ROOT>`
- Full flow dry-run: `python tools/orchestrate.py --workspace-root <WORKSPACE_ROOT> --root <SNAPSHOT_ROOT> --dry-run`

### Artifact Index
- Manifest outputs: `_ARCHIVE/manifests/manifest.csv`, `_ARCHIVE/manifests/manifest.jsonl`
- Plan/map outputs: `_ARCHIVE/move_maps/relocation_plan.jsonl`, `_ARCHIVE/move_maps/relocation_map.jsonl`
- Legacy indexes: `wordpipe/legacy/LEGACY_INDEX.md`, `WordHorrorStories/legacy/LEGACY_INDEX.md`
- Verification outputs: `_ARCHIVE/logs/verify_report.md`, `_ARCHIVE/logs/verify_report.json`, `_ARCHIVE/logs/consistency_report.json`, `_ARCHIVE/logs/immutability_report.json`
- Audit logs: `_ARCHIVE/logs/setup.log`, `_ARCHIVE/logs/plan.log`, `_ARCHIVE/logs/apply_reorg.log`, `_ARCHIVE/logs/conflicts.log`, `_ARCHIVE/logs/legacy_index.log`, `_ARCHIVE/logs/route_unmapped.log`
