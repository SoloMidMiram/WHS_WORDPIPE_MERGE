# 🏗️ WHS WordPipe Merge

> **A copy-only archival pipeline and modular DOCX processing library**
> 
> **Date (Gregorian):** 2026-02-14 | **Date (Jalali):** 1404-11-25
> **Branch:** `main` | **Commit:** `af39e9b`

---

## 📋 Overview

This repository contains **two subsystems**:

| Subsystem | Role | Tech Stack |
|-----------|------|------------|
| **`tools/`** | Evidence pipeline — copy-only archival, manifest generation, integrity verification | Python CLI, JSONL, SHA256 |
| **`wordpipe/`** | Runtime library — modular DOCX processing, import-safe, TraceLedger-oriented | Python, optional `python-docx` / `openai` |

Plus **evidence trees** (`_ARCHIVE/`, `_WORK/`, legacy content) preserved for audit.

---

## 🚀 Quick Start

### Tools Pipeline (Full Flow)

```powershell
# One-command orchestration
python tools/orchestrate.py --root _WORK/snapshot

# Dry-run (print commands, no writes)
python tools/orchestrate.py --root _WORK/snapshot --dry-run
```

### WordPipe Library

```powershell
# Install with DOCX support
python -m pip install -e ".[docx,cli]"

# Run CLI
wordpipe --in "input.docx" --out "output.docx"
```

### Pre-Push Checks

```powershell
python tools/docs_link_check.py
python tools/security_scan.py --root . --fail-on-findings
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 📂 Project Map

| File | Purpose |
|------|---------|
| [`INDEX.md`](INDEX.md) | Complete file map of the repository |
| [`ROADMAP.md`](ROADMAP.md) | Goals, phases, constraints, milestones |
| [`JOURNAL.md`](JOURNAL.md) | Dated period-based activity journal |
| [`ONTOLOGY_MODEL.md`](ONTOLOGY_MODEL.md) | Formal entity-relationship model |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Layered architecture specification |
| [`docs/README.md`](docs/README.md) | Documentation index with role-based paths |

---

## 🧭 Documentation Entry Points

| Role | Start Here |
|------|------------|
| **Operator** (run and triage) | [`docs/PIPELINE_RUNBOOK.md`](docs/PIPELINE_RUNBOOK.md), [`docs/operations/MANUAL.md`](docs/operations/MANUAL.md) |
| **Engineer** (modify pipeline) | [`docs/PIPELINE_CONTRACTS.md`](docs/PIPELINE_CONTRACTS.md), [`docs/TOOLS_MODULES_INTEGRATION_REPORT.md`](docs/TOOLS_MODULES_INTEGRATION_REPORT.md) |
| **Architect** (TraceLedger alignment) | [`docs/architecture/PROJECT_SUMMARY.md`](docs/architecture/PROJECT_SUMMARY.md), [`docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md`](docs/TRACELEDGER_DEBUG_ENHANCEMENT_PLAN.md) |
| **Security** | [`docs/SECURITY_HARDENING.md`](docs/SECURITY_HARDENING.md) |

---

## 🧬 Ontology & Knowledge Management

This project uses an **ontological model** to organize knowledge:

1. **[`ONTOLOGY_MODEL.md`](ONTOLOGY_MODEL.md)** — Defines classes (Artifact, ActivityPeriod, Claim, Verification) and relations (produces, consumes, states, verifies)
2. **[`JOURNAL.md`](JOURNAL.md)** — Period-based entries mapping activity to claims, artifacts, and verification results
3. **[`ROADMAP.md`](ROADMAP.md)** — Phased plan with goals, constraints, milestones, all linkable to journal entries

**Proposed NLP pipeline (future):** POS tagging and entity extraction from `.md` files to auto-populate the ontology.

---

## 🔒 Security

- Secrets are **env-only** (`.env` file, gitignored)
- Use `tools/security_scan.py` for high-confidence pattern scanning
- See [`docs/SECURITY_HARDENING.md`](docs/SECURITY_HARDENING.md) for policy and incident response

---

## 🧪 Current Status

| Metric | Value |
|--------|-------|
| Branch | `main` ✅ synced with `origin/main` |
| Tools pipeline stages | 5 (manifest → plan → apply → index → verify) |
| Baseline files | 98 |
| Legacy candidates | 25 (AI: 18, misc: 7) |
| Pipeline errors | 0 |
| Integrity failures | 0 |
| Remote PRs | 1 (codex review — no action needed) |

---

## 📅 Dates

| System | Current Date |
|--------|--------------|
| Gregorian | 2026-02-14 |
| Jalali (Shamsi) | 1404-11-25 |
| Timezone | Asia/Tehran (UTC+3:30) |

---



---

## 📂 New Organizational Structure

This project has been reorganized with a **knowledge management system**:

| File | Purpose |
|------|---------|
| [`PROJECT_INDEX.md`](PROJECT_INDEX.md) | **Start here** — project navigation and file map |
| [`ROADMAP_1404-11-25.md`](ROADMAP_1404-11-25.md) | Consolidated roadmap with Jalali date |
| [`ONTOLOGY.md`](ONTOLOGY.md) | Human-readable ontology index |
| [`ontology.json`](ontology.json) | Machine-readable ontology (JSON) |
| [`VERIFICATION.md`](VERIFICATION.md) | Claim cross-reference with truth values |
| [`PLAN.md`](PLAN.md) | Immutable task log with Jalali dates |

All dates use the **Jalali (Shamsi) calendar** for consistency with the project's Iranian context.

## 📄 License

See `pyproject.toml` for package metadata.
