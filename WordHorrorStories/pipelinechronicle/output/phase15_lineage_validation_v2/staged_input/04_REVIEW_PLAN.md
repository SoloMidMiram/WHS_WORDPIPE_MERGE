# REVIEW PLAN

## July 2026

- **2026-07-16 - REVIEW PLAN - 1. Review Summary:** The critic reviewed an **earlier version** of `ingest.py` that used a fragile `date_line_pattern` regex for event splitting. The current code has already replaced that with a `bullet_bold_pattern` approach that matches the actual raw file structure. However, several valid issues remain.

### ✅ Already Fixed (Critic's complaints no longer apply)

| Issue | Original Problem | Current Status |
|-------|-----------------|----------------|
| `date_line_pattern` regex too brittle | Required date at line start with `$` anchor | **Replaced** with `bullet_bold_pattern` matching `- **Title:**` structure |
| Date parsing inaccuracies with `fuzzy=True` | Could match non-dates | **Mitigated** by regex pre-filter + year range check (2022–2027) |
| Mojibake double-fix risk | Redundant Unicode→Unicode entries | **Removed** — no `\u2013` etc. in current mapping |

### ✅ All Resolved (1404-11-25)

| # | Issue | Severity | Resolution |
|---|-------|----------|------------|
| 1 | **Preamble silently discarded** | 🔴 Critical | **FIXED** — `extract_preamble()` captures content before first `- **` bullet; rendered as `> **Overview:**` blockquote |
| 2 | **Title extraction too narrow** | 🟡 Medium | **FIXED** — fallback chain: H1 → first H2 → `{source} Incidents` |
| 3 | **Excess CLI flags** | 🟡 Low | **FIXED** — reduced from 11 to 5 essential flags |
| 4 | **Redundant Unicode entries in mojibake map** | 🟢 Trivial | **FIXED** — removed 8 redundant Unicode→Unicode entries |
| 5 | **No preamble preservation** | 🟡 Medium | **FIXED** — preamble rendered as `> **Overview:**` blockquote after `# Source:` header |

---

- **2026-07-16 - REVIEW PLAN - 2. Prioritised Remediation Plan:** ### ✅ P0 — Critical (Completed 1404-11-25)

| ID | Task | Description | Effort | Status |
|----|------|-------------|--------|--------|
| **FIX-1** | **Preserve preamble** | Save all content before the first detected event. Insert as `> **Overview:**` blockquote after `# Source:` header. | 1h | ✅ Done |
| **FIX-2** | **Verify all 16 files produce correct output** | Created `verify_ingest.py` — runs `ingest.py` on every raw file, reports event counts and warnings. All 16 files pass. | 2h | ✅ Done |

### ✅ P1 — High (Completed 1404-11-25)

| ID | Task | Description | Effort | Status |
|----|------|-------------|--------|--------|
| **FIX-3** | **Strip excess CLI flags** | Reduced from 11 to 5: `--input`, `--output`, `--source-name`, `--date-override`, `--verbose`. Removed `--config`, `--source-url`, `--date-format`, `--no-mojibake`, `--dry-run`, `--metadata-only`. | 1h | ✅ Done |
| **FIX-4** | **Improve title extraction** | Fallback chain: H1 → first `##` heading → `{source} Incidents`. | 0.5h | ✅ Done |
| **FIX-5** | **Clean mojibake map** | Removed 8 redundant Unicode→Unicode entries (`\u2013`, `\u2014`, `\u2018`, `\u2019`, `\u201c`, `\u201d`, `\u2026`, `\u2022`). Map now contains only broken byte sequences. | 0.25h | ✅ Done |

### 🟡 P2 — Medium (Before `categorize.py`)

| ID | Task | Description | Effort | Target |
|----|------|-------------|--------|--------|
| **FIX-6** | **Add unit tests** | Create `tests/test_ingest.py` with 3–5 curated input/output pairs covering: normal timeline, narrative-only, date ranges, no dates, preamble content. | 3h | 1404-12-01 |
| **FIX-7** | **Add date confidence ranking** | Tag dates in YAML as `date_confidence: high|medium|low` based on format specificity (ISO=high, "June 2025"=medium, fuzzy=low). | 1h | 1404-12-01 |

### 🔵 P3 — Low (After Pipeline Works End-to-End)

| ID | Task | Description | Effort | Target |
|----|------|-------------|--------|--------|
| **FIX-8** | **Integration test** | Run full pipeline (ingest→merge→categorize→index) and compare output against `ChatGPT_Incidents_Merged.md`. | 4h | 1404-12-10 |
| **FIX-9** | **Better preamble handling** | Instead of `> [!note]`, add a `description` field to YAML front-matter for preamble text. | 0.5h | 1404-12-10 |

---

- **2026-07-16 - REVIEW PLAN - 3. Detailed Issue Analysis:** ### FIX-1: Preamble Discarded (🔴 Critical)

**Current code** (`split_into_events`):
```python
for line in lines:
    stripped = line.strip()
    # ... check for period header or bullet event ...
    # If we're inside an event, accumulate body lines
    if current_date is not None:
        current_body.append(line)
```

Lines before the first `- **Title:**` bullet are silently skipped because `current_date` is `None`.

**Fix approach:**
```python
preamble_lines = []
in_preamble = True

for line in lines:
    stripped = line.strip()
    if is_event_start(stripped) and in_preamble:
        in_preamble = False
        # save preamble, then process event
    if in_preamble:
        preamble_lines.append(line)
    else:
        # existing event processing
```

The preamble is then inserted as a `> [!note] Preamble` block at the top of the output, or stored in YAML front-matter as `description`.

### FIX-3: Excess CLI Flags (🟡 Low)

**Current:** 11 flags  
**Target:** 5 essential flags

| Flag | Verdict | Reason |
|------|---------|--------|
| `--input` | ✅ **Keep** | Required |
| `--output` | ✅ **Keep** | Required |
| `--source-name` | ✅ **Keep** | Essential for attribution |
| `--date-override` | ✅ **Keep** | Critical for files without dates |
| `--verbose` | ✅ **Keep** | Debugging |
| `--config` | ❌ **Remove** | Auto-detect `config.json` in same directory |
| `--source-url` | ❌ **Remove** | Can be added later via enrichment |
| `--date-format` | ❌ **Remove** | Always output `%Y-%m-%d` |
| `--no-mojibake` | ❌ **Remove** | Premature optimisation |
| `--dry-run` | ❌ **Remove** | Use `--metadata-only` or pipe to stdout |
| `--metadata-only` | 🔶 **Hide** | Rename to `--debug-metadata` (hidden) |

### FIX-5: Mojibake Map Cleanup (🟢 Trivial)

**Current map includes redundant entries:**
```python
"\u2013": "–",     # en dash — already correct
"\u2014": "—",     # em dash — already correct
"\u2018": "‘",     # left quote — already correct
# ... etc
```

These are harmless (replace character with itself) but confusing. Remove them. The map should only contain broken byte sequences → correct characters.

---

- **2026-07-16 - REVIEW PLAN - 4. Acceptance Criteria — P0/P1 Verification:** | # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| **AC1** | All 16 raw files produce correct event counts (no regressions) | ✅ **PASS** | `verify_ingest.py` reports 224 total events across 16 files; counts match previous baseline |
| **AC2** | Preamble content is preserved in output (visible as `> **Overview:**` blockquote) | ✅ **PASS** | Narrative files (e.g., `ChatGPT_Agent_Mode_...`) show preamble; timeline files with no preamble show none |
| **AC3** | Title extraction works for files with H1, H2-only, and no headings | ✅ **PASS** | H1 files use H1; H2-only files fall back to H2; no-heading files use `{source} Incidents` |
| **AC4** | Only 5 CLI flags exposed (`--input`, `--output`, `--source-name`, `--date-override`, `--verbose`) | ✅ **PASS** | `--help` confirms exactly 5 flags; removed flags rejected with error |
| **AC5** | `--metadata-only` removed (was hidden debug flag) | ✅ **PASS** | Flag removed entirely; no hidden flags remain |
| **AC6** | Mojibake map contains only broken→fixed mappings (no redundant Unicode entries) | ✅ **PASS** | All 8 `\uXXXX`→same-char entries removed; only byte-sequence artifacts remain |
| **AC7** | Unit tests pass for 3+ curated input/output pairs | ⬜ **PENDING** | FIX-6 deferred to P2 (before `categorize.py`) |

---

- **2026-07-16 - REVIEW PLAN - 5. Implementation Details:** ### FIX-1: Preamble Preservation

**File:** `ingest.py` — new function `extract_preamble()`

```python
def extract_preamble(text: str, events: List[Dict[str, str]]) -> str:
```

**Logic:**
1. If no events found → return entire text with markdown headings stripped
2. Find first `- **` bullet line via regex
3. Extract all text before that line
4. Strip structural headings (`#`, `##`, etc.) since they're already in YAML front-matter
5. Return cleaned text as preamble

**Output rendering** (in `generate_normalised_md`):
```python
if preamble:
    output += f"> **Overview:** {preamble}\n\n"
```

### FIX-2: Verification Script

**New file:** `verify_ingest.py`

- Runs `ingest.py` against every `.md` file in the raw directory
- Parses stderr for event counts and warnings
- Reports per-file status: `[OK]`, `[ZERO]`, or `[ERROR]`
- Exits with code 0 on success, non-zero on errors
- Uses temp directory for output files (auto-cleaned)

### FIX-3: CLI Flag Reduction

**Before (11 flags):** `--input`, `--output`, `--config`, `--source-name`, `--source-url`, `--date-format`, `--date-override`, `--no-mojibake`, `--dry-run`, `--metadata-only`, `--verbose`

**After (5 flags):** `--input`, `--output`, `--source-name`, `--date-override`, `--verbose`

**Removed functionality:**
- `--config` → removed entirely; mojibake cleanup uses built-in map only
- `--source-url` → removed; can be added later via enrichment tool
- `--date-format` → removed; always outputs `%Y-%m-%d`
- `--no-mojibake` → removed; cleanup is always on
- `--dry-run` → removed; use `--output` to control destination
- `--metadata-only` → removed; no hidden debug flag retained

### FIX-4: Title Extraction

**Before:** H1 → `{source} Incidents`
**After:** H1 → first H2 → `{source} Incidents`

```python
def extract_title(raw_text: str, source: str) -> str:
    # 1. Look for H1 heading
    match = re.search(r"^#\s+(.+)$", raw_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # 2. Look for first H2 heading
    match = re.search(r"^##\s+(.+)$", raw_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # 3. Fall back to source name
    return f"{source} Incidents"
```

### FIX-5: Mojibake Map Cleanup

**Removed 8 redundant entries** (Unicode codepoint → same character):
- `"\u2013": "–"` (en dash)
- `"\u2014": "—"` (em dash)
- `"\u2018": "‘"`, `"\u2019": "’"` (quotes)
- `"\u201c": "“"`, `"\u201d": "”"` (double quotes)
- `"\u2026": "…"` (ellipsis)
- `"\u2022": "•"` (bullet)

**Kept 13 broken byte-sequence entries** (e.g., `"â€"` → `"–"`, `"Ã©"` → `"é"`).

---

- **2026-07-16 - REVIEW PLAN - 6. Change Log:** | Date (Jalali) | Change |
|---------------|--------|
| 1404-11-25 | Initial review plan created based on automated code critic analysis |
| 1404-11-25 | **All P0/P1 fixes applied:** preamble preservation (FIX-1), verification script (FIX-2), CLI flag reduction (FIX-3), title extraction improvement (FIX-4), mojibake map cleanup (FIX-5). All 16 files verified passing. |
