#!/usr/bin/env python3
"""Build a clean narrative chronicle DOCX from pipeline output."""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
except ImportError:
    print("ERROR: python-docx required. pip install python-docx")
    sys.exit(1)

EVIDENCE_DIR = Path("_ARCHIVE/evidence/chronicle_v2")
OUTPUT_DOCX = Path("_WORK/generated-reports/output_chronicle_report_v2.docx")

# Colours
C_PRIMARY = RGBColor(0x1A, 0x3C, 0x6E)
C_SECONDARY = RGBColor(0x2C, 0x5F, 0x8A)
C_MUTED = RGBColor(0x66, 0x66, 0x66)
C_LIGHT = RGBColor(0x99, 0x99, 0x99)

THEME_COLORS = {
    "Outages": RGBColor(0xCC, 0x33, 0x33),
    "Jailbreaks/Exploits": RGBColor(0xCC, 0x66, 0x00),
    "Memory/Personalisation": RGBColor(0x00, 0x66, 0x99),
    "Web UI": RGBColor(0x33, 0x66, 0x33),
    "API/Developer": RGBColor(0x66, 0x33, 0x99),
    "Culture/Virality": RGBColor(0xCC, 0x33, 0x66),
}

THEME_ICONS = {
    "Outages": "\u26a0\ufe0f",
    "Jailbreaks/Exploits": "\U0001f513",
    "Memory/Personalisation": "\U0001f9e0",
    "Web UI": "\U0001f310",
    "API/Developer": "\u2699\ufe0f",
    "Culture/Virality": "\U0001f525",
}

THEME_DESCRIPTIONS = {
    "Outages": "Server crashes, 503 errors, service disruptions, downtime events",
    "Jailbreaks/Exploits": "Prompt injection, DAN mode, security bypasses, instruction leaks",
    "Memory/Personalisation": "Memory features, custom instructions, user bios, personalisation",
    "Web UI": "chat.openai.com interface, browser UI, button issues, interface redesigns",
    "API/Developer": "API access, developer tools, function calling, tokens, rate limits",
    "Culture/Virality": "Viral moments, memes, social media trends, community reactions",
}

# Mojibake cleanup map
MOJIBAKE = {
    "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "--", "\u2026": "...", "\u00a0": " ",
    "\ufffd": "?", "\u201e": '"', "\u2022": "-", "\u2032": "'",
    "\u2033": '"', "\u00ab": '"', "\u00bb": '"', "\u2015": "--",
    "\u2012": "-",
}


def clean_text(text):
    """Clean mojibake, markdown artifacts, and file:// links."""
    for bad, good in MOJIBAKE.items():
        text = text.replace(bad, good)
    # Strip markdown bold/italic (with DOTALL for multiline matches)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text, flags=re.DOTALL)
    # Remove file:// citation links entirely: [\[N\]](file://...) or <file://...>
    text = re.sub(r"\[(?:\\\[)?\d+(?:\\\])?\]\(file://[^)]+\)", "", text)
    text = re.sub(r"<file://[^>]+>", "", text)
    text = re.sub(r"file://\S+", "", text)
    # Remove HTML comments like <!-- Duplicate date -->
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # Convert [domain.com](url) to just url
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\2", text)
    # Clean up whitespace
    text = re.sub(r"  +", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_events():
    """Parse chronicle_tagged.md, deduplicating via tagged.json."""
    md_path = EVIDENCE_DIR / "chronicle_tagged.md"
    json_path = EVIDENCE_DIR / "chronicle_tagged.tagged.json"

    text = md_path.read_text(encoding="utf-8")
    jdata = json.loads(json_path.read_text(encoding="utf-8"))

    json_keys = set()
    for ev in jdata:
        json_keys.add((ev.get("date", ""), ev.get("title", "")))

    blocks = re.split(r"(?=^## Event:)", text, flags=re.MULTILINE)
    seen = set()
    events = []

    for b in blocks[1:]:
        if not b.strip():
            continue
        m = re.search(r"^## Event:\s*(.+)$", b, re.MULTILINE)
        if not m:
            continue
        title_line = m.group(1).strip()
        dm = re.match(r"(\d{4}-\d{2}-\d{2})\s*[\u2013-]\s*(.*)", title_line)
        date_str = dm.group(1) if dm else "Unknown"
        clean_title = dm.group(2).strip() if dm else title_line

        key = (date_str, clean_title)
        if key not in json_keys or key in seen:
            continue
        seen.add(key)

        tm = re.search(r"<!-- themes:\s*(.+?)\s*-->", b)
        themes = [t.strip() for t in tm.group(1).split(",")] if tm else []

        bm = re.search(r"-->\n\n(.*)", b, re.DOTALL)
        body = bm.group(1).strip() if bm else ""
        body = clean_text(body)

        events.append({
            "date": date_str,
            "title": clean_title,
            "themes": themes,
            "body": body,
        })

    return events


# DOCX helpers

def set_cell_shading(cell, color_hex):
    shading = cell._element.get_or_add_tcPr()
    se = shading.makeelement(qn("w:shd"), {qn("w:fill"): color_hex, qn("w:val"): "clear"})
    shading.append(se)


def add_heading(doc, text, level=1, color=C_PRIMARY):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = color
    return h


def add_para(doc, text, size=10, color=None, bold=False, italic=False, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    if bold:
        run.bold = True
    if italic:
        run.italic = True
    return p


def add_event_block(doc, event, num):
    """Add a formatted event with clean body text."""
    # Separator
    sep = doc.add_paragraph()
    sep.paragraph_format.space_before = Pt(4)
    sep.paragraph_format.space_after = Pt(2)
    r = sep.add_run("_" * 70)
    r.font.color.rgb = C_LIGHT
    r.font.size = Pt(6)

    # Title with number
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(1)
    rn = p.add_run(f"#{num}  ")
    rn.font.size = Pt(9)
    rn.font.color.rgb = C_MUTED
    rt = p.add_run(event["title"])
    rt.bold = True
    rt.font.size = Pt(12)
    rt.font.color.rgb = C_PRIMARY

    # Date
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(2)
    rd = p2.add_run(f"\U0001f4c5 {event['date']}")
    rd.font.size = Pt(9)
    rd.font.color.rgb = C_MUTED

    # Theme badges
    if event["themes"]:
        p3 = doc.add_paragraph()
        p3.paragraph_format.space_after = Pt(4)
        for theme in event["themes"]:
            icon = THEME_ICONS.get(theme, "\U0001f3f7\ufe0f")
            rt2 = p3.add_run(f"  {icon} {theme}  ")
            rt2.font.size = Pt(8)
            rt2.bold = True
            rt2.font.color.rgb = THEME_COLORS.get(theme, C_MUTED)

    # Body text
    body = event["body"]
    p4 = doc.add_paragraph(body)
    p4.paragraph_format.space_after = Pt(6)
    for run in p4.runs:
        run.font.size = Pt(10)


# Main

def main():
    print("Parsing events...")
    events = parse_events()
    print(f"  {len(events)} unique events")

    # Stats
    theme_counts = Counter()
    for ev in events:
        for t in ev["themes"]:
            theme_counts[t] += 1
    sorted_themes = sorted(theme_counts.items(), key=lambda x: -x[1])

    # Group by year
    by_year = defaultdict(list)
    for ev in events:
        by_year[ev["date"][:4]].append(ev)

    # Create document
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10)

    # COVER PAGE
    for _ in range(6):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ChatGPT Incident Chronicle")
    r.bold = True
    r.font.size = Pt(32)
    r.font.color.rgb = C_PRIMARY

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run(
        "A Narrative Analysis of ChatGPT's Bugs, Exploits,\n"
        "Viral Moments, and Evolution (2022\u20132025)"
    )
    r2.font.size = Pt(14)
    r2.font.color.rgb = C_SECONDARY

    doc.add_paragraph()

    for line in [
        "Generated from the Chronicle Pipeline v2",
        f"16 source files  |  {len(events)} events  |  6 theme categories",
        "WordHorrorStories  |  2026-02-14",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(line)
        r.font.size = Pt(10)
        r.font.color.rgb = C_MUTED

    doc.add_page_break()

    # TABLE OF CONTENTS
    add_heading(doc, "Table of Contents", level=1)
    toc = [
        ("1", "Executive Summary"),
        ("2", "Methodology & Pipeline Configuration"),
        ("3", "Thematic Analysis"),
        ("4", "Chronicle Timeline"),
        ("", "  2022 \u2013 The Birth of ChatGPT"),
        ("", "  2023 \u2013 The Wild West of AI Chat"),
        ("", "  2024 \u2013 Platform Maturation"),
        ("", "  2025 \u2013 Current Landscape"),
        ("5", "Key Narratives & Patterns"),
        ("6", "Appendix: Source Manifest"),
        ("7", "Appendix: Link Registry"),
    ]
    for num, title in toc:
        p = doc.add_paragraph()
        label = f"{num}  {title}" if num else f"     {title}"
        r = p.add_run(label)
        r.font.size = Pt(10)
        if num:
            r.bold = True

    doc.add_page_break()

    # 1. EXECUTIVE SUMMARY
    add_heading(doc, "1. Executive Summary", level=1)

    add_para(doc, (
        "This chronicle documents the evolution of ChatGPT from its November 2022 launch through "
        "mid-2025, capturing 42 distinct incidents across six thematic categories. The incidents range "
        "from server outages and security exploits to viral cultural moments and interface changes."
    ))

    # Stats table
    st = doc.add_table(rows=5, cols=2)
    st.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (label, value) in enumerate([
        ("Total Unique Events", str(len(events))),
        ("Source Files", "16"),
        ("Date Range", "2022-01-01 to 2025-07-15"),
        ("Themes Applied", "6 categories, 62 keywords, 16 negative filters"),
        ("Tagging Coverage", "100% (all events tagged)"),
    ]):
        row = st.rows[i]
        row.cells[0].text = label
        row.cells[1].text = value
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(10)
        set_cell_shading(row.cells[0], "E8E8E8")

    doc.add_paragraph()

    add_para(doc, (
        "The chronicle reveals several key narratives: the rapid evolution from simple refusal-message "
        "memes to sophisticated prompt injection exploits; the recurring pattern of server outages "
        "following major feature launches; the emergence of ChatGPT as a cultural phenomenon driving "
        "viral social media moments; and the ongoing tension between platform restrictions and user "
        "creativity that has defined the ChatGPT experience."
    ))

    doc.add_page_break()

    # 2. METHODOLOGY
    add_heading(doc, "2. Methodology & Pipeline Configuration", level=1)

    add_heading(doc, "2.1 Pipeline Architecture", level=2)
    add_para(doc, (
        "This report was generated by the Chronicle Pipeline v2, a 5-stage pipe-and-filter architecture "
        "implemented in Python and PowerShell. The pipeline processes raw markdown files through "
        "ingestion, verification, merging, categorisation, and index generation."
    ))

    pt = doc.add_table(rows=6, cols=3)
    pt.style = "Light Shading Accent 1"
    for i, cells in enumerate([
        ["Stage", "Script", "Function"],
        ["1 \u2013 Ingest", "ingest.py", "Normalise raw .md to standard format with YAML front-matter"],
        ["2 \u2013 Verify", "verify_ingest.py", "Batch-verify ingestion on all files"],
        ["3 \u2013 Merge", "merge.py", "Deduplicate by body hash + date, resolve conflicts"],
        ["4 \u2013 Categorise", "categorize.py", "Tag events with 6 themes via keyword matching"],
        ["5 \u2013 Index", "index.py", "Generate 4 appendix files from tagged chronicle"],
    ]):
        for j, val in enumerate(cells):
            pt.rows[i].cells[j].text = val

    doc.add_paragraph()

    add_heading(doc, "2.2 Theme Configuration", level=2)
    add_para(doc, (
        "The categorisation engine uses substring matching with positive and negative keyword lists. "
        "A theme is assigned if at least one positive keyword matches and no negative keyword matches."
    ))

    tt = doc.add_table(rows=7, cols=3)
    tt.style = "Light Shading Accent 1"
    for i, cells in enumerate([
        ["Theme", "Positive Keywords", "Negative Keywords"],
        ["Web UI", "10", "2"],
        ["API/Developer", "13", "2"],
        ["Outages", "11", "5"],
        ["Jailbreaks/Exploits", "9", "3"],
        ["Memory/Personalisation", "9", "3"],
        ["Culture/Virality", "10", "1"],
    ]):
        for j, val in enumerate(cells):
            tt.rows[i].cells[j].text = val

    doc.add_page_break()

    # 3. THEMATIC ANALYSIS
    add_heading(doc, "3. Thematic Analysis", level=1)

    add_para(doc, (
        "The following analysis breaks down the events by theme, showing distribution, "
        "temporal patterns, and notable observations for each category."
    ))

    # Summary table
    theme_over_time = defaultdict(lambda: Counter())
    for ev in events:
        for t in ev["themes"]:
            theme_over_time[t][ev["date"][:4]] += 1

    sht = doc.add_table(rows=1 + len(sorted_themes), cols=4)
    sht.style = "Light Shading Accent 1"
    for j, h in enumerate(["Theme", "Events", "% of Total", "Peak Year"]):
        sht.rows[0].cells[j].text = h
    for i, (theme, count) in enumerate(sorted_themes):
        row = sht.rows[i + 1]
        row.cells[0].text = f"{THEME_ICONS.get(theme, '')} {theme}"
        row.cells[1].text = str(count)
        row.cells[2].text = f"{count/len(events)*100:.1f}%"
        peak = theme_over_time[theme].most_common(1)[0][0] if theme_over_time[theme] else "-"
        row.cells[3].text = peak

    doc.add_paragraph()

    for i, (theme, count) in enumerate(sorted_themes):
        add_heading(doc, f"3.{i+1}  {THEME_ICONS.get(theme, '')}  {theme}", level=2)
        add_para(doc, THEME_DESCRIPTIONS.get(theme, ""), size=9, color=C_MUTED, italic=True)
        add_para(doc, f"Appears in {count} of {len(events)} events ({count/len(events)*100:.1f}%).")

        years = sorted(theme_over_time[theme].keys())
        yr_strs = [f"{y}: {theme_over_time[theme][y]}" for y in years]
        add_para(doc, "Year distribution: " + ", ".join(yr_strs), size=9, color=C_MUTED)

        samples = [e for e in events if theme in e["themes"]][:3]
        if samples:
            add_para(doc, "Notable events:", size=9, bold=True)
            for se in samples:
                p = doc.add_paragraph(style="List Bullet")
                r = p.add_run(f"{se['date']} \u2013 {se['title']}")
                r.font.size = Pt(9)

    doc.add_page_break()

    # 4. CHRONICLE TIMELINE
    add_heading(doc, "4. Chronicle Timeline", level=1)

    add_para(doc, (
        "The following timeline presents all events in chronological order, grouped by year. "
        "Each event includes its full narrative body with theme labels."
    ))

    year_info = {
        "2022": ("The Birth of ChatGPT",
            "ChatGPT launched in November 2022 and immediately became a cultural phenomenon. "
            "Early incidents focused on the model's quirks, refusal messages, and the first "
            "jailbreak attempts as users explored the boundaries of the new technology."),
        "2023": ("The Wild West of AI Chat",
            "2023 saw an explosion of creativity and conflict. Users discovered prompt injection, "
            "DAN mode, and other exploits. Server outages became common as demand surged. "
            "Viral moments spread across Twitter and Reddit. The platform matured with "
            "feature updates, custom instructions, and memory capabilities."),
        "2024": ("Platform Maturation",
            "By 2024, ChatGPT had become a platform. Agent mode, GPTs, and advanced features "
            "brought new capabilities and new vulnerabilities. The community shifted from "
            "simple jailbreaks to sophisticated prompt engineering."),
        "2025": ("Current Landscape",
            "The most recent period shows continued evolution with agent mode exploits, "
            "memory feature refinements, and ongoing cultural impact. The line between "
            "bug and feature remains blurred."),
    }

    global_num = 0
    for year in sorted(by_year.keys()):
        year_events = by_year[year]
        info = year_info.get(year, (year, ""))

        add_heading(doc, f"4.{list(by_year.keys()).index(year)+1}  {year} \u2013 {info[0]}", level=2)
        add_para(doc, info[1], size=10, italic=True)

        # Period stats
        ptc = Counter()
        for ev in year_events:
            for t in ev["themes"]:
                ptc[t] += 1
        add_para(doc, f"This period contains {len(year_events)} events.", size=9, color=C_MUTED)
        if ptc:
            ts = [f"{t} ({c})" for t, c in ptc.most_common()]
            add_para(doc, "Theme distribution: " + ", ".join(ts), size=9, color=C_MUTED)

        doc.add_paragraph()

        for ev in year_events:
            global_num += 1
            add_event_block(doc, ev, global_num)

        doc.add_page_break()

    # 5. KEY NARRATIVES
    add_heading(doc, "5. Key Narratives & Patterns", level=1)

    narratives = [
        ("The Arms Race of Jailbreaking",
         "From the first \"Biblical Peanut Butter Sandwich\" jailbreak in December 2022 to "
         "sophisticated prompt injection attacks in 2025, the cat-and-mouse game between "
         "OpenAI's safety measures and user creativity has been a defining feature of the "
         "ChatGPT experience. Each new safety update was met with novel bypass techniques, "
         "creating a continuous cycle of restriction and circumvention."),
        ("The Viral Economy",
         "ChatGPT incidents regularly went viral on social media, creating a feedback loop "
         "where unusual outputs, funny failures, and creative uses were amplified across "
         "Twitter, Reddit, and other platforms. This viral economy drove both engagement "
         "and scrutiny, making ChatGPT one of the most discussed products of its era."),
        ("Infrastructure Under Pressure",
         "Server outages and service disruptions correlated strongly with major feature "
         "launches and viral moments. The Outages theme captures the growing pains of "
         "a platform struggling to scale while maintaining reliability."),
        ("From Chat to Platform",
         "The evolution from a simple chat interface to a platform with memory, custom "
         "instructions, agent mode, and GPTs represents a fundamental shift. Each new "
         "capability brought new categories of incidents, from memory leaks to agent "
         "mode exploits."),
    ]

    for i, (title, body) in enumerate(narratives):
        add_heading(doc, f"5.{i+1}  {title}", level=2)
        add_para(doc, body)

    doc.add_page_break()

    # 6. APPENDIX: SOURCE MANIFEST
    add_heading(doc, "6. Appendix: Source Manifest", level=1)
    add_para(doc, "Source contribution summary showing which files contributed events to this chronicle.")

    src_path = EVIDENCE_DIR / "appendix" / "source_manifest.md"
    if src_path.exists():
        content = src_path.read_text(encoding="utf-8")
        content = clean_text(content)
        lines = [l for l in content.split("\n") if l.strip() and not l.startswith("#") and not l.startswith("|---")]
        for line in lines:
            add_para(doc, line.strip(), size=9)

    doc.add_page_break()

    # 7. APPENDIX: LINK REGISTRY
    add_heading(doc, "7. Appendix: Link Registry", level=1)
    add_para(doc, "All external URLs referenced in the chronicle, sorted by domain.")

    link_path = EVIDENCE_DIR / "appendix" / "link_registry.md"
    if link_path.exists():
        content = link_path.read_text(encoding="utf-8")
        content = clean_text(content)
        lines = [l for l in content.split("\n") if l.strip() and not l.startswith("#") and not l.startswith("|---")]
        for line in lines:
            add_para(doc, line.strip(), size=8)

    # FOOTER
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("\u2014 End of Chronicle Report \u2014")
    r.italic = True
    r.font.color.rgb = C_LIGHT
    r.font.size = Pt(10)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run(
        "Generated by Chronicle Pipeline v2 (Phase 9b)\n"
        "WordHorrorStories  |  2026-02-14 (Jalali: 1404-11-25)\n"
        f"16 source files  |  {len(events)} unique events  |  6 themes  |  100% coverage"
    )
    r2.font.size = Pt(8)
    r2.font.color.rgb = C_LIGHT

    # Save
    OUTPUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUTPUT_DOCX))
    print(f"\nDone: {OUTPUT_DOCX.resolve()}")
    print(f"  Size: {OUTPUT_DOCX.stat().st_size / 1024:.1f} KB")
    print(f"  Events: {len(events)}")
    print(f"  Themes: {', '.join(f'{t}={c}' for t, c in sorted_themes)}")


if __name__ == "__main__":
    main()
