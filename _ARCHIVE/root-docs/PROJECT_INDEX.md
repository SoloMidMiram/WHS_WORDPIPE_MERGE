# 📂 Project Index

> **Project:** WHS WordPipe Merge
> **Problem:** A disordered local project folder with outdated remote Git repository needs archaeology, reconstruction, and organization.
> **Date:** 2026-02-14 (Jalali: 1404-11-25)
> **Branch:** `main` (synced with `origin/main`)

---

## Explicit Goals

1. **Portability** — No absolute paths, no environment-dependent behavior
2. **Evidence-backed** — Every claim points to a file, log, or run
3. **Ontology-grounded** — Structured entity-relationship model describes the project
4. **Journal-anchored** — Dated period-based journal tracks activity, claims, and verification
5. **TraceLedger-ready** — WordPipe as a clean, import-safe library

---

## Constraints

| # | Constraint | Impact |
|---|------------|--------|
| C1 | Limited/unstable internet access | Cannot rely on pip install, GitHub API, or external NLP services |
| C2 | Windows environment with PowerShell | Tooling must be Win32-compatible |
| C3 | Existing massive doc set (many .md files) | Risk of redundancy, contradiction, and path rot |
| C4 | Absolute paths (F:\Git\...) embedded in docs | Breaks for any other clone location or user |
| C5 | Evidence files in _ARCHIVE/ are append-only | Must preserve historical evidence |
| C6 | _WORK/snapshot is immutable input | Must not modify source snapshot |

---

## Key Files Map

| File | Purpose | Read First? |
|------|---------|-------------|
| [`README.md`](README.md) | Friendly entry point with quick start | ✅ Yes |
| [`PROJECT_INDEX.md`](PROJECT_INDEX.md) | This file — project navigation | ✅ Yes |
| [`ROADMAP.md`](ROADMAP.md) | Goals, phases, constraints, milestones | ✅ Yes |
| [`ROADMAP_1404-11-25.md`](ROADMAP_1404-11-25.md) | Consolidated roadmap with Jalali date | ✅ Yes |
| [`JOURNAL.md`](JOURNAL.md) | Dated period-based activity journal | For history |
| [`ONTOLOGY_MODEL.md`](ONTOLOGY_MODEL.md) | Detailed ontology with instance tables | For reference |
| [`ONTOLOGY.md`](ONTOLOGY.md) | Human-readable ontology index | For reference |
| [`ontology.json`](ontology.json) | Machine-readable ontology (JSON) | For automation |
| [`VERIFICATION.md`](VERIFICATION.md) | Claim cross-reference with truth values | For quality |
| [`PLAN.md`](PLAN.md) | Immutable task log with Jalali dates | For planning |
| [`INDEX.md`](INDEX.md) | Complete file map of the repository | For navigation |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Layered architecture specification | For architects |
| [`WORKSPACE_OVERVIEW.md`](WORKSPACE_OVERVIEW.md) | Workspace manual | For operators |

---

## How to Navigate

### First Time Here?

1. Start with **[`README.md`](README.md)** for a friendly overview and quick start
2. Read **[`ROADMAP.md`](ROADMAP.md)** to understand goals, phases, and current status
3. Browse **[`INDEX.md`](INDEX.md)** to see the complete file map

### Looking for History?

1. Read **[`JOURNAL.md`](JOURNAL.md)** for period-based activity entries with claims and verification
2. The "Phases of Activity" section reconstructs all development phases chronologically
3. Each phase links to commits, artifacts, and verification procedures

### Looking for Structure?

1. Read **[`ONTOLOGY.md`](ONTOLOGY.md)** for the human-readable ontology index
2. See **[`ONTOLOGY_MODEL.md`](ONTOLOGY_MODEL.md)** for detailed class definitions and instances
3. Use **[`ontology.json`](ontology.json)** for machine-readable ontology data

### Looking to Contribute?

1. Check **[`PLAN.md`](PLAN.md)** for open tasks with Jalali dates
2. Check **[`VERIFICATION.md`](VERIFICATION.md)** for claims that need verification
3. Follow the documentation style in `docs/DOC_STYLE_GUIDE.md`

---

## Directory Structure

```
/
├── ARCHITECTURE.md          # Architecture specification
├── WORKSPACE_OVERVIEW.md     # Workspace manual
├── README.md                # Entry point
├── PROJECT_INDEX.md         # This file
├── ROADMAP.md               # Goals and phases
├── ROADMAP_1404-11-25.md    # Consolidated roadmap
├── JOURNAL.md               # Activity journal
├── ONTOLOGY_MODEL.md        # Detailed ontology
├── ONTOLOGY.md              # Ontology index
├── ontology.json            # Machine ontology
├── VERIFICATION.md          # Claim verification
├── PLAN.md                  # Task log
├── INDEX.md                 # File map
├── pyproject.toml           # Package config
├──
├── docs/                    # Documentation
├── tools/                   # Evidence pipeline
├── wordpipe/                # Runtime library
├── WordHorrorStories/       # Content archive
├── tests/                   # Unit tests
├── _ARCHIVE/               # Pipeline evidence
├── _WORK/                   # Working trees
├── _META/                   # Meta files
├── _SECURITY/              # Security reports
└── _INBOX/                  # Incoming files
```

---

## Change Log

| Date (Gregorian) | Date (Jalali) | Change |
|------------------|---------------|--------|
| 2026-02-14 | 1404-11-25 | Initial project index created |
