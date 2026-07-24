# ✅ Project Verification Plan

> **Purpose:** Cross-reference all factual claims about the project against actual codebase evidence.
> **Date:** 2026-02-14 (Jalali: 1404-11-25)
> **Status:** Historical baseline; current corrections and phase evidence are in
> `docs/engineering/IMPLEMENTATION_ALIGNMENT_AUDIT.md`

---

## Latest P0 Reliability Remediation Result

Observed on 2026-07-24 (1405/05/02):

| Check | Observed result |
|-------|-----------------|
| P0-focused tests (`test_p0_cli`, `test_pipeline_contracts`, `test_flatteners`, P0.2/P0.4 additions) | **22 new tests** |
| `pytest -q` | **253 passed** (up from 231) |
| Architecture boundaries | OK; 296 static edges; 6 reviewed path roles; 0 active v1 bypasses |
| Root layout / input catalog | Both OK |
| Documentation links | 36 files scanned; 33 references valid |
| Security scan | 911 files scanned; 0 findings |
| `git diff --check` | Exit 0; CRLF conversion notices only |
| P0.1: `verify_integrity --strict` flag in orchestration | Verified via `--dry-run` subprocess test |
| P0.2: Malformed event heading pre-scan | 6 validation tests + merge-integration test pass |
| P0.3: ComFlattener eager fail | Import-safe + construction-raise tests pass |
| P0.4: TOC adapter explicit failure | Adapter test raises `ImportError` on Windows; returns None on non-Windows |
| P0.5: CLI error exit code | Success exits 0; error exits 1 (monkeypatched pipeline) |
| P0.6: `--in`/`--out` path guard | Same path, relative-vs-absolute, case-insensitive (Windows) all rejected |

---

## Latest Phase 17 Closeout Result

Observed on 2026-07-17 (1405/04/26):

| Check | Observed result |
|-------|-----------------|
| Phase 17 focused tests | See JOURNAL for live `pytest` counts |
| `pytest -q` | **231 passed** |
| Architecture boundaries | OK; 292 static edges; 6 reviewed path roles; 0 active v1 bypasses |
| Root layout / input catalog | Both OK |
| Documentation links | 36 files scanned; 33 references valid |
| Security scan | 908 files scanned; 0 findings |
| `git diff --check` | Exit 0; line-ending conversion notices only |
| InsuranceChatbot `phase17_event_provenance_repeatability` | 200/200/194; `merged-note-aware-v1`; missing/unexpected 0; unmerged 0; PASS; ontology 10/7 |
| PipelineChronicle `phase17_event_provenance_repeatability` | 50/50/50; same survivor method; PASS; ontology 10/7 |
| Stability vs explicit `phase16_event_lineage_validation` | Both topics exit 0 STABLE under reserved `phase17_provenance_stability/` |
| Phase 16 tree digests (preflight) | ICB `0fde0e97…7022ed9f` (26 files); PC `99606f4c…a082801a` (30 files) |
| `_ARCHIVE/` + `_WORK/snapshot/` (preflight) | 185 files; digest `da5a6761…2868ae0c` |

Phase 16 `unmerged_source_event_count` remains keep-both count-parity history. Phase 17 correlation uses actual survivor membership. Stability evidence is indexed here and in JOURNAL — not via `OPTIONAL_EVIDENCE_FILES`.

## Latest Phase 16 Closeout Result

Observed on 2026-07-17 (1405/04/26):

| Check | Observed result |
|-------|-----------------|
| Import-safety + Phase 16 focused group | 17 passed |
| `pytest -q` | 216 passed |
| `python tools/check_architecture_boundaries.py --root .` | OK; 292 static edges; 6 reviewed path roles; 0 active v1 bypasses |
| `python tools/check_root_layout.py --root .` | OK |
| `python tools/check_input_catalog.py --root .` | OK |
| `python tools/docs_link_check.py` | 34 files scanned; 29 references valid |
| `python tools/security_scan.py --root . --fail-on-findings` | 843 files scanned; 0 findings |
| `git diff --check` | Exit 0; CRLF conversion notices only |

Read-only artifact inspection reconfirmed InsuranceChatbot 200 lineage / 200 merged / 194 theme-bearing events and PipelineChronicle 50/50/50, both event-sidecar schemas, empty ambiguity arrays, Event Provenance summary sections, and the aggregate 10-entity/7-relation ontology spine.

No topic run was executed during closeout. The paired Phase 16 evidence inventory remained 56 files with digest `9a4c4afda024756e19a95f7e493dbb9a7e4eff97a18c0c7f450f66864a1d452f`; `_ARCHIVE/` plus `_WORK/snapshot/` remained 185 files with digest `8627104576ae6179be8eaa9707dcecb81c5d4d91e9c0accd848e8a1f318204b8`.

Historical Phase 16 assessment: the Phase 16 evidence proved normalized identity
and fixed keep-both count parity; independent actual-survivor membership and a
second paired stable-id run remained the then-planned Phase 17 gate. The current
Phase 17 result is recorded above and supersedes that limitation without
rewriting the historical Phase 16 artifacts.

## Latest Architecture Stability Result

Observed on 2026-07-17 (1405/04/26):

| Check | Observed result |
|-------|-----------------|
| `pytest -q` | 200 passed |
| `python tools/check_architecture_boundaries.py --root .` | OK; 292 static import edges; 6 reviewed path roles in the registry; 0 active v1 bypasses |
| `python tools/check_root_layout.py --root .` | OK |
| `python tools/check_input_catalog.py --root .` | OK |
| `python tools/docs_link_check.py` | 33 files scanned; 29 references valid |
| `python tools/security_scan.py --root . --fail-on-findings` | 784 files scanned; 0 findings |
| `git diff --check` | Exit 0; CRLF conversion notices only |

No controlled topic run was executed for this documentation-and-guardrails slice. Task-start and post-validation SHA-256 inventory digests match for `_ARCHIVE/` plus `_WORK/snapshot/` and for both `phase15_lineage_validation_v2` evidence trees.

## Historical Summary (2026-02-14)

| Metric | Value |
|--------|-------|
| Total claims verified | 20 |
| True | 19 |
| False | 1 |
| Uncertain | 0 |

The table below records the 2026-02-14 audit and must not be read as current
truth for later-refactored modules. In particular, DC12, DC14, and DC15 were
subsequently fixed or superseded, while DC17 requires external/remote evidence
and is not established by the current dirty worktree.

## Current Corrections

| Historical claim | Current status |
|------------------|----------------|
| Duplicate `style_code_blocks()` definitions | FIXED — one definition remains |
| Monolithic `wordpipe/orchestrator.py` | SUPERSEDED — thin composition root delegates to `WordPipePipeline` |
| O(n²) `wordpipe/core/segment.py` | SUPERSEDED — core module is a stub; active adapter precomputes heading states |
| Duplicate logging imports / fragile mkdir | FIXED or superseded by the EventSink compatibility wrapper |
| Main synchronized with remote | NOT REVALIDATED — requires remote evidence and a clean comparison point |

---

## Claim Verification Checklist

| # | Claim | Source | Truth | Evidence | Procedure |
|---|-------|--------|-------|----------|-----------|
| DC1 | The pipeline has 5 stages: make_manifest, plan_legacy_reorg, apply_legacy_reorg, build_legacy_index, verify_integrity | docs/PIPELINE_RUNBOOK.md, WORKSPACE_OVERVIEW.md | ✅ True | ls tools/*.py shows all 5 stage scripts; each has --help with documented behavior | ls tools/make_manifest.py tools/plan_legacy_reorg.py tools/apply_legacy_reorg.py tools/build_legacy_index.py tools/verify_integrity.py |
| DC2 | Stage scripts support --workspace-root, --summary-json, --strict flags | docs/TOOLS_MODULES_INTEGRATION_REPORT.md | ✅ True | Each stage script has argparse with these flags; verified by running --help | python tools/make_manifest.py --help | Select-String "workspace-root|summary-json|strict" |
| DC3 | Core has zero runtime-heavy dependencies | ARCHITECTURE.md | ✅ True | wordpipe/core/__init__.py imports only standard library modules | python -c "import wordpipe.core" (should work without any pip install) |
| DC4 | The pipeline produces manifest.jsonl, relocation_plan.jsonl, relocation_map.jsonl | WORKSPACE_OVERVIEW.md | ✅ True | _ARCHIVE/manifests/manifest.jsonl, _ARCHIVE/move_maps/relocation_plan.jsonl, _ARCHIVE/move_maps/relocation_map.jsonl all exist | ls _ARCHIVE/manifests/manifest.jsonl _ARCHIVE/move_maps/relocation_plan.jsonl _ARCHIVE/move_maps/relocation_map.jsonl |
| DC5 | Secrets are env-based only; no keys in code | docs/SECURITY_HARDENING.md | ✅ True | security_scan.py passes with no findings; .env.example has placeholders only | python tools/security_scan.py --root . --fail-on-findings |
| DC6 | All 82 Python files have standard Jalali-date headers | tools/add_standard_headers.py, JOURNAL.md | ✅ True | python tools/add_standard_headers.py --path . reports 0 files changed | python tools/add_standard_headers.py --path . |
| DC7 | WordPipe is a proper installable package with pyproject.toml | ARCHITECTURE.md, pyproject.toml | ✅ True | pyproject.toml exists with name, version, extras, build system | python -c "import tomllib; d = tomllib.load(open('pyproject.toml','rb')); print(d['project']['name'])" |
| DC8 | EventSink protocol is defined in wordpipe/events.py | docs/TRACELEDGER_INTEGRATION_CONTRACT.md | ✅ True | wordpipe/events.py contains EventSink Protocol class | python -c "from wordpipe.events import EventSink; print(EventSink)" |
| DC9 | Duplicate files are governed by a tiered policy in docs/DUPLICATE_POLICY.md | docs/DUPLICATE_POLICY.md | ✅ True | docs/DUPLICATE_POLICY.md exists with tier definitions | Test-Path docs/DUPLICATE_POLICY.md |
| DC10 | Git history spans only 3 days (2026-02-12 to 2026-02-14) | JOURNAL.md (Period 8) | ✅ True | git log --format="%ai" shows all commits within this window | git log --format="%ai" | ForEach-Object { $_ -match "^2026-02-1[2-4]" } |
| DC11 | Filesystem timestamps (2026-05-18) are snapshot artifacts, not real modification dates | JOURNAL.md (Period 8) | ✅ True | git dates (Feb 2026) vs fs dates (May 2026) discrepancy confirmed | Compare git log dates with (Get-Item wordpipe/__init__.py).LastWriteTime |
| DC12 | wordpipe/code_style.py has duplicate style_code_blocks() definitions | docs/PlansArchive/PLAN.md | ✅ True | grep shows two def style_code_blocks in the file | Select-String "def style_code_blocks" wordpipe/code_style.py |
| DC13 | wordpipe/logging_tools.py has duplicate imports | docs/PlansArchive/PLAN.md | ❌ False | Duplicate imports were fixed during header standardization | Check wordpipe/logging_tools.py for duplicate import statements |
| DC14 | wordpipe/orchestrator.py (process_docx_v3) mixes flattening, styling, segmentation, save, cleanup, TOC update, and telemetry | docs/PlansArchive/PLAN.md | ✅ True | Inspection of wordpipe/orchestrator.py shows all these responsibilities in one function | Read wordpipe/orchestrator.py and count distinct responsibilities |
| DC15 | wordpipe/core/segment.py uses O(n^2) worst-case heading context scanning | docs/PlansArchive/PLAN.md | ✅ True | build_hpath() scans from start per segment boundary | Inspect wordpipe/core/segment.py build_hpath() implementation |
| DC16 | All doc paths are relative, no absolute F:\... references | ROADMAP.md (G1) | ✅ True | grep for [A-Z]:\\ in docs/ returns no results | Select-String -Path "docs/*.md" -Pattern "[A-Z]:\\" |
| DC17 | main branch is in sync with origin/main | JOURNAL.md (Period 7) | ✅ True | git status shows "up to date"; git ls-remote confirms same hash | git status; git log origin/main -1 --format="%H" |
| DC18 | The project has an ontological model with classes, relations, and instances | ONTOLOGY_MODEL.md | ✅ True | ONTOLOGY_MODEL.md contains class hierarchy, attribute definitions, relations, and populated instances | Check ONTOLOGY_MODEL.md sections 2, 3, 4 |
| DC19 | Active tree has 28 new modular architecture files not in snapshot | JOURNAL.md (Period 8) | ✅ True | Diff of wordpipe/ vs _WORK/snapshot/snapshot/wordpipe/ shows 28 files only in active | Compare directories: Get-ChildItem -Recurse wordpipe/ vs _WORK/snapshot/snapshot/wordpipe/ |
| DC20 | 45 files had duplicate headers which were cleaned to single headers | JOURNAL.md (Period 8) | ✅ True | Select-String for duplicate "Created:" lines shows no duplicates | Select-String "^# Created:" *.py | Group-Object Filename | Where Count -gt 1 |

---

## Verification Procedures

### Automated Checks (Run These)

```powershell
# 1. Pipeline stage existence
ls tools/make_manifest.py, tools/plan_legacy_reorg.py, tools/apply_legacy_reorg.py, tools/build_legacy_index.py, tools/verify_integrity.py

# 2. Standard CLI flags
python tools/make_manifest.py --help
python tools/plan_legacy_reorg.py --help
python tools/apply_legacy_reorg.py --help
python tools/build_legacy_index.py --help
python tools/verify_integrity.py --help

# 3. Import safety
python -c "import wordpipe"

# 4. Security scan
python tools/security_scan.py --root . --fail-on-findings

# 5. Header consistency
python tools/add_standard_headers.py --path .

# 6. Absolute path check
Select-String -Path "docs/*.md" -Pattern "[A-Z]:\\\"

# 7. Git sync
git status
git log origin/main -1 --format="%H"

# 8. Duplicate headers
Select-String "^# Created:" *.py -Recurse | Group-Object Filename | Where-Object { $_.Count -gt 1 }

# 9. Package metadata
python -c "import tomllib; d = tomllib.load(open('pyproject.toml','rb')); print(d['project']['name'])"

# 10. EventSink protocol
python -c "from wordpipe.events import EventSink; print(EventSink)"

# 11. Repository, canonical input, and architecture placement
python tools/check_root_layout.py --root .
python tools/check_input_catalog.py --root .
python tools/check_architecture_boundaries.py --root .

# 12. Topic report, docs, and security regression
python -m pytest -q
python tools/docs_link_check.py
python tools/security_scan.py --root . --fail-on-findings
```

### Manual Inspection Checks

| # | What to Inspect | How |
|---|-----------------|-----|
| M1 | wordpipe/code_style.py duplicate defs | Search for "def style_code_blocks" |
| M2 | wordpipe/orchestrator.py responsibility count | Read the file, count distinct tasks in process_docx_v3 |
| M3 | wordpipe/core/segment.py complexity | Inspect build_hpath() implementation |
| M4 | Ontology model completeness | Read ONTOLOGY_MODEL.md sections 2-4 |
| M5 | Journal period coverage | Read JOURNAL.md all 8 periods |

---

## False Claims (Needs Attention)

| Claim | Why False | Action Needed |
|-------|-----------|---------------|
| DC13: wordpipe/logging_tools.py has duplicate imports | Was true historically, but was fixed during header standardization | Update docs/PlansArchive/PLAN.md to reflect current state |

---

## Change Log

| Date (Gregorian) | Date (Jalali) | Change |
|------------------|---------------|--------|
| 2026-02-14 | 1404-11-25 | Initial verification plan created with 20 claims |
