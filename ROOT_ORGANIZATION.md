# Repository Root Organization Rules

> Status: Active<br>
> Effective: 2026-07-17 (1405/04/26)<br>
> Enforcement: `python tools/check_root_layout.py --root .`

## Purpose

Keep the repository root limited to entrypoints, governance documents, and
project configuration. Runtime code, tooling, generated outputs, evidence, and
experiments must live in their owned directories.

## Root Allowlist

Root files are limited to:

- entrypoint and governance docs: `AGENTS.md`, `README.md`, `ROADMAP.md`, `PLAN.md`,
  `INDEX.md`, `JOURNAL.md`, `ONTOLOGY_MODEL.md`, `ROOT_ORGANIZATION.md`,
  `ARCHITECTURE_AND_MODULES.md`, `REPO_ORGANIZATION_PLAN.md`,
  `WORKSPACE_OVERVIEW.md`, and `VERIFICATION.md`;
- machine-readable project metadata: `ontology.json` and `pyproject.toml`;
- repository configuration: `.gitignore` and `.env.example`.

Canonical top-level directories are described in
`docs/engineering/REPOSITORY_BOUNDARIES.md`. New root directories require an
explicit boundary classification and an update to the root-layout checker.

Ignored tool-generated caches such as `.pytest_cache/` and `*.egg-info/` may
appear locally. They are not curated root content, are excluded from version
control, and are explicit checker exemptions rather than allowed project areas.

## Placement Rules

| Material | Required location |
|----------|-------------------|
| Importable runtime code | `wordpipe/<area>/` |
| Chronicle operator CLI | `pipeline/` |
| Administrative/evidence CLI | `tools/` |
| Manual, diagnostic, or report-building scripts | `scripts/<area>/` |
| Tests | `tests/` |
| Maintained documentation | `docs/<area>/`, except allowlisted root governance docs |
| Catalogued corpus inputs | `inputs/<corpus>/<format>/` |
| Temporary/generated outputs | `_WORK/<purpose>/` |
| Curated historical evidence | `_ARCHIVE/evidence/<purpose>/` |
| Immutable source snapshots | `_ARCHIVE/` or `_WORK/snapshot/`, according to provenance |
| Topic manifests, themes, and measured runs | `WordHorrorStories/<topic>/` |

Generated files must never default to the repository root. A generator writes
to `_WORK/` by default; a deliberate evidence-curation step may copy or move a
stable result into `_ARCHIVE/evidence/`.

## Dependency and Ownership Rules

- `wordpipe/` never imports `tools/`, `pipeline/`, `scripts/`, content, work, or
  archive directories.
- `tools/` and `pipeline/` are operator surfaces, not public runtime APIs.
- Shared reusable Chronicle logic belongs in `wordpipe/chronicle/`; wrappers
  remain thin CLI surfaces.
- Topic-specific parsing and vocabulary stay in adapters and topic folders,
  outside the core Chronicle stages.
- Evidence is append-only or preserved by new run ID; historical run folders
  are not overwritten to make current metrics look cleaner.
- Corpus inputs are byte-catalogued in `inputs/catalog.json`; project Markdown
  and generated reports are not corpus inputs.

## Change Checklist

Before adding or moving a root item:

1. Classify it as runtime, CLI, script, test, documentation, temporary output,
   evidence, configuration, or content.
2. Place it using the table above.
3. Update `INDEX.md` and, for a new boundary, both
   `docs/engineering/REPOSITORY_BOUNDARIES.md` and `tools/check_root_layout.py`.
4. Record planned or incomplete work in `ROADMAP.md` with an explicit status;
   never mark a phase complete from file existence alone.
5. Run root-layout, input-catalog, tests, documentation-link, and security checks.

## Current Remediation

The former tracked `_scripts/` files now live in `scripts/reporting/`. Generated
root DOCX reports were preserved under `_ARCHIVE/evidence/generated-reports/`.
Report builders now default to `_WORK/generated-reports/`, preventing recurrence.
The active ChatGPT Chronicle and InsuranceChatbot Markdown corpora live under
`inputs/`; their catalog distinguishes source, exact-duplicate, and derived
members. No source DOCX is currently present.
