# 🧬 Ontology Index

> **Purpose:** Human-readable index of the project's ontological model.
> **Date:** 2026-02-14 (Jalali: 1404-11-25)
> **Machine-readable version:** `ontology.json`

---

## Overview

This ontology describes the **WHS WordPipe Merge** project using a formal entity-relationship model.
It captures:

- **Classes** (entity types) with attributes and subtypes
- **Relations** (typed edges between classes)
- **Instances** (concrete entities populated from the project)

---

## Class Hierarchy

```
Entity (abstract)
├── Artifact          # Any persistent file or data output
│   ├── Doc            # Markdown documentation
│   ├── SourceFile     # Python source code
│   ├── Evidence       # Pipeline output (logs, manifests, reports)
│   └── ConfigFile     # Configuration (.toml, .gitignore, .env.example)
├── DuplicateSet       # Group of files sharing the same name or content
│   ├── MirrorPair     # Active <-> Snapshot copy (archival)
│   ├── CompatibilityWrapper  # Thin re-export for backward compat
│   └── VersionHistory # Dated snapshots of same module (legacy)
├── ActivityPeriod     # A bounded span of work with a goal
│   ├── Phase          # Named project phase
│   └── Session        # Single work session (date-bound)
├── Claim              # A statement made in docs or code
│   ├── DesignClaim    # "X is designed to do Y"
│   ├── EvidenceClaim  # "The pipeline produces Z"
│   └── StatusClaim    # "Feature is complete"
├── Verification       # How a claim is checked
│   ├── Test           # Automated test (unittest)
│   ├── Command        # CLI command to run
│   └── Inspection     # Manual review
└── Role               # Who interacts with the system
    ├── Operator
    ├── Engineer
    └── Architect
```

---

## Class Definitions

| Class | Parent | Description | Key Attributes |
|-------|--------|-------------|----------------|
| Artifact | Entity | Any persistent file | path, kind, sha256, git_created, git_modified, fs_mtime |
| Doc | Artifact | Markdown documentation | (inherits Artifact) |
| SourceFile | Artifact | Python source code | (inherits Artifact) |
| Evidence | Artifact | Pipeline output | (inherits Artifact) |
| ConfigFile | Artifact | Configuration file | (inherits Artifact) |
| DuplicateSet | Entity | Group of duplicate files | canonical_path, duplicate_type, content_match |
| MirrorPair | DuplicateSet | Active <-> Snapshot copy | active_path, snapshot_path, diverged |
| CompatibilityWrapper | DuplicateSet | Backward compat re-export | target_module, import_statement |
| VersionHistory | DuplicateSet | Dated legacy snapshots | versions, earliest, latest |
| ActivityPeriod | Entity | Bounded work span | name, start_date, end_date, goal |
| Phase | ActivityPeriod | Named project phase | (inherits ActivityPeriod) |
| Session | ActivityPeriod | Single work session | (inherits ActivityPeriod) |
| Claim | Entity | A stated assertion | text, status |
| DesignClaim | Claim | Design assertion | (inherits Claim) |
| EvidenceClaim | Claim | Evidence assertion | (inherits Claim) |
| StatusClaim | Claim | Status assertion | (inherits Claim) |
| Verification | Entity | How to check a claim | method, command_or_path |
| Test | Verification | Automated test | (inherits Verification) |
| Command | Verification | CLI command | (inherits Verification) |
| Inspection | Verification | Manual review | (inherits Verification) |
| Role | Entity | Who interacts | (abstract) |
| Operator | Role | Runs pipeline | (inherits Role) |
| Engineer | Role | Modifies pipeline | (inherits Role) |
| Architect | Role | Designs alignment | (inherits Role) |

---

## Relations

| Relation | Domain | Range | Description |
|----------|--------|-------|-------------|
| produces | ActivityPeriod | Artifact | Work output |
| consumes | ActivityPeriod | Artifact | Work input |
| states | Artifact | Claim | A doc or code makes a claim |
| verifies | Verification | Claim | How a claim is checked |
| verified_by | Claim | Verification | Inverse of verifies |
| depends_on | Artifact | Artifact | Dependency between artifacts |
| part_of | ActivityPeriod | ActivityPeriod | Hierarchical (Session -> Phase) |
| precedes | ActivityPeriod | ActivityPeriod | Temporal ordering |
| is_duplicate_of | Artifact | Artifact | Same name/content as another file |
| wraps | CompatibilityWrapper | Artifact | Re-exports from target module |
| mirrors | MirrorPair | Artifact | Active <-> Snapshot correspondence |
| evolves_to | VersionHistory | VersionHistory | Temporal ordering of versions |

---

## Key Instances

### Artifacts (Selected)

| Name | Path | Kind | Produced By |
|------|------|------|-------------|
| ARCHITECTURE.md | `ARCHITECTURE.md` | Doc | Phase 4: Modular Refactor |
| Pipeline Runbook | `docs/PIPELINE_RUNBOOK.md` | Doc | Phase 2: Security & Contracts |
| make_manifest.py | `tools/make_manifest.py` | Source | Phase 1: Initial Setup |
| add_standard_headers.py | `tools/add_standard_headers.py` | Source | Phase 6: Foundation Fixes |
| manifest.jsonl | `_ARCHIVE/manifests/manifest.jsonl` | Evidence | Phase 1: Initial Setup |

### Duplicate Sets (Selected)

| Set Name | Type | Canonical | Copies |
|----------|------|-----------|--------|
| code_style.py | CompatibilityWrapper | `wordpipe/code_style.py` | `wordpipe/pipeline/code_style.py` |
| __init__.py | MirrorPair | `wordpipe/__init__.py` | `_WORK/snapshot/.../__init__.py` (diverged) |
| AI helpers | VersionHistory | `wordpipe/ai/helpers.py` | 11 legacy snapshots |

### Activity Periods

| Name | Start | End | Goal |
|------|-------|-----|------|
| P0: Setup | 1404-08-23 | 1404-08-23 | Initial workspace creation |
| P4: Foundation Fixes | 1404-11-25 | 1404-11-25 | Fix absolute paths, verify docs |
| P8: Duplicate Analysis | 1404-11-25 | 1404-11-25 | Analyze duplicates, apply headers |

### Claims

| ID | Text | Status |
|----|------|--------|
| C1 | The pipeline has 5 stages | ✅ true |
| C4 | Core has zero runtime-heavy dependencies | ✅ true |
| C6 | All 82 Python files have standard Jalali-date headers | ✅ true |
| C3 | verify reports are stable across machines | ❓ untested |

---

## File Mappings

| Concept | File/Folder |
|---------|-------------|
| Pipeline Stage | `tools/make_manifest.py`, `tools/plan_legacy_reorg.py`, `tools/apply_legacy_reorg.py`, `tools/build_legacy_index.py`, `tools/verify_integrity.py` |
| Pipeline Contract | `tools/pipeline_contracts.py` |
| Orchestrator | `tools/orchestrate.py`, `wordpipe/orchestrator.py` |
| Event System | `wordpipe/events.py` |
| Plugin System | `wordpipe/plugins/registry.py` |
| Adapters | `wordpipe/adapters/` |
| Interfaces | `wordpipe/interfaces/` |
| CLI | `wordpipe/cli/` |
| Security Scanner | `tools/security_scan.py` |
| Header Tool | `tools/add_standard_headers.py` |
| Jalali Converter | `tools/jalali.py` |
| Documentation | `docs/` |
| Evidence Archive | `_ARCHIVE/` |
| Snapshot Input | `_WORK/snapshot/` |

---

## See Also

- [`ONTOLOGY_MODEL.md`](ONTOLOGY_MODEL.md) — Detailed ontology with full instance tables
- [`ontology.json`](ontology.json) — Machine-readable ontology (JSON)
- [`JOURNAL.md`](JOURNAL.md) — Activity journal linked to ontology periods
- [`VERIFICATION.md`](VERIFICATION.md) — Claim verification against codebase
