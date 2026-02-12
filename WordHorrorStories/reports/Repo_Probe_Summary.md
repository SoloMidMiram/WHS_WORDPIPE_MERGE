# Repository Probe Summary

## Tracked Junk Files Check

- No tracked `.pyc` files found in the repository.
- No tracked `__pycache__` directories found.
- No tracked `.venv` or `venv` directories found.
- No tracked files under `WordHorrorStories/out/`, `WordHorrorStories/media/`, or `wordpipe/ai/data/outputs/` except `.docx` files as previously noted.

## Commit History Junk Check

- No junk files found in commit history for `__pycache__` or `.pyc`.
- No `.venv` or `venv` junk files found in commit history.
- No junk files found in commit history for `WordHorrorStories/out/`, `WordHorrorStories/media/`, or `wordpipe/ai/data/outputs/`.

## Packaging Visibility

- `wordpipe/__init__.py` exists.
- `WordHorrorStories/autobiography/__init__.py` exists.
- `pyproject.toml` project name: `wordpipeline`, version: `0.0.0`.
- `setuptools` packages find includes `["wordpipe*", "autobiography*"]` in `[".", "WordHorrorStories"]`.

## Script Sanity

- `scripts/bootstrap.ps1` has no PowerShell parse errors.
- `scripts/smoke_import.ps1` assumes editable install exists; it activates the virtual environment and runs import and CLI help checks.

## Codex Job Summaries

### Job 1 	6 Fix `bootstrap.ps1`

- Updated `bootstrap.ps1` to use single-quoted PowerShell strings for printed pip install commands.
- Validation: Only `bootstrap.ps1` changed.

### Job 2 	6 Make `smoke_import.ps1` Truthful

- Added guarded `autobiography` import that prints a clear instruction to run `.scripts\bootstrap.ps1` and exits non-zero on failure.
- Validation: Only `smoke_import.ps1` changed.

### Job 3 	6 Make COM Flattener Safe

- Wrapped `MergedpipelineV3` import with clear error if missing.
- Fallback to `XmlFlattener` on missing COM dependencies.
- Behavior matrix for Windows and non-Windows environments.

### Job 4 	6 Turn `cli/loader.py` into Real CLI

- Added argparse-based main with options for input docx, output directory, and Windows preference.
- Added console script entry point `wordpipe`.

### Job 5 	6 Hygiene Pass (Remove Tracked Artifacts)

- Removed tracked artifact `ai_Modular word pipeline__1404-05-23_12-00_Tehran.docx`.
- Added `.gitignore` entry for `wordpipe/ai/data/outputs/`.
- Validation: No content edits, index-only.

---

This report is generated for documentation and conversion to Word format if needed.