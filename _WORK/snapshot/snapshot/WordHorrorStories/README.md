# Word Horror Stories – Codex Logger ➜ Coding Autobiography

## Overview
This repository glues together a VS Code webview logger and a Python DOCX builder so every chat exchange can be archived as a “Coding Autobiography.” The JS modules run inside the Codex/Continue panel, emitting JSONL log files with ISO + Jalali timestamps. The Python `autobiography` package ingests those logs, deduplicates entries, and renders a Word document (single column or optional two‑column layout) that future WordPipe automations can extend.

---

## JSONL Log Schema
Each line inside `logs/*.jsonl` must be a JSON object with the following keys:

| Field | Type | Notes |
| --- | --- | --- |
| `version` | str | Schema version, e.g. `"1.0"` |
| `id` | str | UUID v4 unique per entry |
| `session_id` | str | UUID grouping entries per panel session |
| `ts_iso` | str | ISO8601, e.g. `2025-11-14T08:30:12.345Z` |
| `ts_jalali` | str | `YYYY/MM/DD HH:MM:SS` |
| `source` | str | `"codex"` or `"continue"` |
| `model` | str \| null | Model identifier |
| `project_path` | str | e.g. `F:/Git/WHS/WordHorrorStories` |
| `workspace` | str \| null | VS Code workspace title |
| `user` | str \| null | Reserved for future auth info |
| `q_text` / `a_text` | str | Full prompt / answer |
| `q_summary` / `a_summary` | str \| null | Short summaries |
| `language_guess` | str \| null | e.g. `"python"` |
| `tags` | list[str] \| null | Arbitrary labels |

The schema is enforced by `codex_logger_entry.js` (producer) and `autobiography/log_reader.py` (consumer).

---

## JavaScript Logger
* Canonical entry point: **`codex_logger_bootstrap.js`** (ES module).
* Modules live at repo root (`codex_logger_*.js`):
  * `config` – selectors, labels, model metadata.
  * `time` – Jalali/ISO timestamps.
  * `summary` – whitespace trimming and ellipsis (`…`).
  * `dom` – finds assistant nodes, tags them via `dataset.codexEntryId` before logging.
  * `entry` – builds JSONL objects, UUID v4.
  * `collector` – holds log entries, exports Copy All helper.
  * `ui` – single toolbar with “Copy All Logs” + per-answer “Copy Log Line.” Clipboard fallback uses a hidden `<textarea>`.
  * `observer` – MutationObserver guarded so only one instance runs; logs each assistant once even if the DOM reflows.
  * `bootstrap` – waits for `document.body`, initializes toolbar/observer, exposes `window.CodexLogger.init()`.

**Usage (Custom CSS & JS Loader):**
```html
<script type="module" src="file:///F:/Git/WHS/WordHorrorStories/codex_logger_bootstrap.js"></script>
```
Adjust `CodexLoggerConfig` (project path, selectors, labels) per workspace.

---

## Python Autobiography Package
```
autobiography/
  __init__.py                # exposes build_autobiography_from_logs()
  cli.py                     # python -m autobiography.cli …
  config.py                  # ChronicleConfig, DocxConfig
  log_reader.py              # JSONL → LogEntry
  collection.py              # dedupe, sorting, grouping
  docx_builder.py            # DocxBuilder + DocxBuilderTwoColumn
  models.py                  # LogEntry dataclass (Jalali helpers)
```

### Features
* Reads multiple JSONL files, deduplicates by `id`, sorts by `ts_iso`, groups by Jalali date (or any attribute/callable name).
* `DocxConfig` centralizes headings, labels, separator, layout (`single_column` vs `two_column`), prompt/project toggles, and Markdown rendering toggle.
* `AnswerRenderer` handles lightweight Markdown inside answers (headings, bullets, fenced code blocks) before writing to DOCX.
* Two‑column layout renders prompt vs summary rows via tables when `DocxConfig.layout == "two_column"`.
* High-level API `build_autobiography_from_logs()` lets WordPipe (or other Python callers) feed existing `Document` instances for further processing.

### CLI
```bash
cd F:/Git/WHS/WordHorrorStories
python -m autobiography.cli logs/2025-11-14_codex.jsonl out/CodingAutobiography.docx \
  --group-by jalali_date \
  --layout single_column
```
*Accepts multiple log files; layout can be `two_column` for prompt/summary tables.*

### Programmatic API
```python
from pathlib import Path
from autobiography import build_autobiography_from_logs, DocxConfig

doc = build_autobiography_from_logs(
    [Path("logs/2025-11-14_codex.jsonl")],
    config=DocxConfig(layout="two_column")
)
doc.save("out/CodingAutobiography.docx")
```

---

## WordPipe Integration Hints
1. Load logs via `LogFileReader`, feed into `LogCollection.unique().sort_by_iso()` and `group_by` whatever dimension WordPipe cares about.
2. Choose a builder via `builder_for_config()` (single or two column) and call `build_document(grouped, base_doc)` to append directly to a WordPipe-managed `Document`.
3. Extend `DocxConfig` or wrap `DocxBuilder` to add styles, two-column templates, or Markdown rules specific to your pipe.

---

## Maintenance Notes
* Legacy, monolithic scripts live under `legacy/` for reference but no longer affect imports.
* Always adjust `CodexLoggerConfig.selectors` if Codex/Continue DOM classes change; dataset flags prevent double-logging even during DOM churn.
* Jalali conversion lives in `codex_logger_time.js` — do not replace unless you test conversions thoroughly.
* For new DOCX layouts or Markdown tokens, extend `AnswerRenderer` or add another builder; WordPipe can call `build_autobiography_from_logs` and continue formatting down the pipeline.
