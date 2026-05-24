# ✅ Project Verification Plan

> **Purpose:** Cross-reference all factual claims about the project against actual codebase evidence.
> **Date:** 2026-02-14 (Jalali: 1404-11-25)
> **Status:** Baseline established

---

## Summary

| Metric | Value |
|--------|-------|
| Total claims verified | 20 |
| True | 19 |
| False | 1 |
| Uncertain | 0 |

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
