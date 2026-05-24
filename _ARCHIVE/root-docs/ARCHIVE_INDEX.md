# Archived Root-Level Documents

> **Archived:** 2026-02-14 (Jalali: 1404-11-25)
> **Purpose:** Stale or superseded root-level `.md` files preserved for historical/audit purposes.

---

## Archive Index

| Original Path | Archived At | Superseded By | Reason |
|---------------|-------------|---------------|--------|
| `ROADMAP_1404-11-25.md` | `_ARCHIVE/root-docs/ROADMAP_1404-11-25.md` | `ROADMAP.md` | Snapshot of old roadmap before newest-first restructuring and Phase 9 numbering fix |
| `ONTOLOGY.md` | `_ARCHIVE/root-docs/ONTOLOGY.md` | `ONTOLOGY_MODEL.md` | Brief ontology index superseded by full ontology model with entities, relations, periods, and claims |
| `ARCHITECTURE.md` | `_ARCHIVE/root-docs/ARCHITECTURE.md` | `ARCHITECTURE_AND_MODULES.md` | Brief architecture spec superseded by comprehensive 3-subsystem reference |
| `CODEX_LOG.md` | `_ARCHIVE/root-docs/CODEX_LOG.md` | `JOURNAL.md` | Action log superseded by period-based journal with claims and verification |
| `PATH_FIX_LOG.md` | `_ARCHIVE/root-docs/PATH_FIX_LOG.md` | `JOURNAL.md` | Path normalization log folded into journal records |
| `PROJECT_INDEX.md` | `_ARCHIVE/root-docs/PROJECT_INDEX.md` | `INDEX.md` | Early project index superseded by full INDEX.md with all subsystems |

---

## Retention Policy

These files are **preserved for audit only**. They may contain:
- Outdated path references
- Claims that contradict current documentation
- Phase numbering that doesn't match current ROADMAP.md

Do **not** use these as source of truth. Refer to the current documents listed in the "Superseded By" column.

## Restoration

```powershell
# To restore any archived document:
Copy-Item "_ARCHIVE/root-docs/<filename>" "<original-location>"
```
