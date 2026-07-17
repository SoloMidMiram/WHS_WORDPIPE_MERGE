#!/usr/bin/env python3
"""
Convert chronicle pipeline output (v2) into a formatted DOCX report.

Consumes:
  - _ARCHIVE/evidence/chronicle_v2/chronicle_tagged.md       (tagged chronicle)
  - _ARCHIVE/evidence/chronicle_v2/chronicle_tagged.tagged.json (sidecar tags)
  - _ARCHIVE/evidence/chronicle_v2/appendix/*.md             (4 appendix files)

Produces:
  - _WORK/generated-reports/output_report.docx
"""

import json
import re
import sys
from pathlib import Path

# Fix console encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE
except ImportError:
    print("ERROR: python-docx is required. Install with: pip install python-docx")
    sys.exit(1)

# ── Configuration ────────────────────────────────────────────────────
EVIDENCE_DIR = Path("_ARCHIVE/evidence/chronicle_v2")
OUTPUT_DOCX = Path("_WORK/generated-reports/output_report.docx")

# ── Helper Functions ──────────────────────────────────────────────────

def add_heading_styled(doc, text, level=1):
    """Add a heading with colour styling."""
    heading = doc.add_heading(text, level=level)
    return heading


def add_body(doc, text):
    """Add a normal paragraph."""
    return doc.add_paragraph(text)


def add_code_block(doc, text):
    """Add a monospace code-like paragraph."""
    p = doc.add_paragraph()
    p.style = doc.styles['No Spacing']
    run = p.add_run(text)
    run.font.name = 'Consolas'
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    return p


def add_theme_entry(doc, theme_name, count):
    """Add a theme entry with count."""
    p = doc.add_paragraph()
    run = p.add_run(f"▸ {theme_name}")
    run.bold = True
    run.font.size = Pt(10)
    p.add_run(f" — {count} events")
    return p


def add_event(doc, title, date_str, themes, body, event_num):
    """Add a formatted event entry with theme badges."""
    # Event separator
    doc.add_paragraph("─" * 60)
    
    # Title with number
    p = doc.add_paragraph()
    run = p.add_run(f"#{event_num}: {title}")
    run.bold = True
    run.font.size = Pt(11)
    
    # Date
    p2 = doc.add_paragraph()
    run2 = p2.add_run(f"📅 {date_str}")
    run2.font.size = Pt(9)
    run2.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    
    # Theme badges
    if themes:
        p3 = doc.add_paragraph()
        for theme in themes:
            run_theme = p3.add_run(f" [{theme}] ")
            run_theme.bold = True
            run_theme.font.size = Pt(9)
            if "Outages" in theme:
                run_theme.font.color.rgb = RGBColor(0xCC, 0x33, 0x33)
            elif "Jailbreaks" in theme:
                run_theme.font.color.rgb = RGBColor(0xCC, 0x66, 0x00)
            elif "Memory" in theme:
                run_theme.font.color.rgb = RGBColor(0x00, 0x66, 0x99)
            elif "Web UI" in theme:
                run_theme.font.color.rgb = RGBColor(0x33, 0x66, 0x33)
            elif "API" in theme:
                run_theme.font.color.rgb = RGBColor(0x66, 0x33, 0x99)
            elif "Culture" in theme:
                run_theme.font.color.rgb = RGBColor(0xCC, 0x33, 0x66)
    
    # Body (truncated for readability)
    body_text = body.strip()
    if len(body_text) > 500:
        body_text = body_text[:497] + "..."
    p4 = doc.add_paragraph(body_text)
    p4.style = doc.styles['Normal']
    for run in p4.runs:
        run.font.size = Pt(10)


# ── Main ──────────────────────────────────────────────────────────────

def main():
    doc = Document()
    
    # ══ Cover Page ═════════════════════════════════════════════════════
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Chronicle Pipeline Output Report")
    run.bold = True
    run.font.size = Pt(26)
    run.font.color.rgb = RGBColor(0x1A, 0x3C, 0x6E)
    
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run2 = p2.add_run("WordHorrorStories — ChatGPT Incidents")
    run2.font.size = Pt(14)
    run2.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    
    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run3 = p3.add_run("Generated from Phase 9b pipeline (v2) • 2026-02-14")
    run3.font.size = Pt(10)
    run3.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    
    doc.add_page_break()
    
    # ══ Table of Contents placeholder ═════════════════════════════════
    add_heading_styled(doc, "Table of Contents", level=1)
    toc_items = [
        "1. Pipeline Overview",
        "2. Theme Distribution (from tagged.json)",
        "3. Tagged Chronicle — Event Log",
        "4. Appendix: Event Index",
        "5. Appendix: Theme Index",
        "6. Appendix: Source Manifest",
        "7. Appendix: Link Registry",
    ]
    for item in toc_items:
        p = doc.add_paragraph(item)
        p.style = doc.styles['List Bullet']
    
    doc.add_page_break()
    
    # ══ Section 1: Pipeline Overview ══════════════════════════════════
    add_heading_styled(doc, "1. Pipeline Overview", level=1)
    
    add_body(doc, "This report was generated by the Chronicle Pipeline v2 (5-stage pipe-and-filter architecture). The pipeline processes raw ChatGPT incident markdown files through ingestion, merging, categorisation (with negative keyword filtering), and index generation.")
    
    add_heading_styled(doc, "Pipeline Stages", level=2)
    stages = [
        ("Stage 1 — Ingest", "ingest.py", "Normalises raw .md files into standard format with YAML front-matter"),
        ("Stage 2 — Verify", "verify_ingest.py", "Optional batch verification of ingestion"),
        ("Stage 3 — Merge", "merge.py", "Deduplicates and merges events by body hash + date"),
        ("Stage 4 — Categorise", "categorize.py", "Tags events with 6 themes using positive + negative keyword matching"),
        ("Stage 5 — Index", "index.py", "Generates 4 appendix files from tagged chronicle"),
    ]
    
    table = doc.add_table(rows=6, cols=3)
    table.style = 'Light Shading Accent 1'
    hdr = table.rows[0].cells
    hdr[0].text = "Stage"
    hdr[1].text = "Script"
    hdr[2].text = "Function"
    for i, (stage, script, func) in enumerate(stages):
        row = table.rows[i + 1].cells
        row[0].text = stage
        row[1].text = script
        row[2].text = func
    
    add_heading_styled(doc, "Theme Configuration", level=2)
    add_body(doc, "Using pipeline/themes.json — 6 themes, 62 positive keywords, 16 negative keywords:")
    
    themes_info = [
        ("Web UI", "chat.openai.com, web interface, browser, buttons, UI freeze"),
        ("API/Developer", "API, developer, Linux terminal, function calling, tokens, rate limits"),
        ("Outages", "server crash, 503 error, downtime, unavailable, service disruption"),
        ("Jailbreaks/Exploits", "prompt injection, DAN, bypass, jailbreak, security exploit"),
        ("Memory/Personalisation", "memory, chat history, custom instructions, bio, remembers"),
        ("Culture/Virality", "viral, Twitter, Reddit, meme, trending, social media"),
    ]
    
    for theme, keywords in themes_info:
        add_theme_entry(doc, theme, "?")
    
    doc.add_page_break()
    
    # ══ Section 2: Theme Distribution ═════════════════════════════════
    add_heading_styled(doc, "2. Theme Distribution", level=1)
    
    # Load tagged.json
    tag_path = EVIDENCE_DIR / "chronicle_tagged.tagged.json"
    if tag_path.exists():
        with open(tag_path, "r", encoding="utf-8") as f:
            events_data = json.load(f)
        
        # Count themes
        theme_counts = {}
        for event in events_data:
            for theme in event.get("themes", []):
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        total_events = len(events_data)
        tagged_events = sum(1 for e in events_data if e.get("themes"))
        over_tagged = sum(1 for e in events_data if len(e.get("themes", [])) >= 4)
        
        p = doc.add_paragraph()
        run = p.add_run(f"Total events: {total_events}")
        run.bold = True
        
        add_body(doc, f"Events with at least one theme: {tagged_events} ({tagged_events/total_events*100:.1f}%)")
        add_body(doc, f"Events with 4+ themes (over-tagged): {over_tagged} ({over_tagged/total_events*100:.1f}%)")
        
        add_heading_styled(doc, "Per-Theme Counts", level=2)
        
        # Sort by count descending
        sorted_themes = sorted(theme_counts.items(), key=lambda x: -x[1])
        
        table2 = doc.add_table(rows=1 + len(sorted_themes), cols=3)
        table2.style = 'Light Shading Accent 1'
        hdr2 = table2.rows[0].cells
        hdr2[0].text = "Theme"
        hdr2[1].text = "Event Count"
        hdr2[2].text = "% of Total"
        
        for i, (theme, count) in enumerate(sorted_themes):
            row = table2.rows[i + 1].cells
            row[0].text = theme
            row[1].text = str(count)
            row[2].text = f"{count/total_events*100:.1f}%"
    else:
        add_body(doc, "⚠️ tagged.json not found — cannot display theme distribution.")
        events_data = []
    
    doc.add_page_break()
    
    # ══ Section 3: Tagged Chronicle ═══════════════════════════════════
    add_heading_styled(doc, "3. Tagged Chronicle — Event Log", level=1)
    add_body(doc, "Each event from the merged chronicle with theme labels applied by categorize.py.")
    
    if events_data:
        for event_num, event in enumerate(events_data, 1):
            title = event.get("title", "Untitled Event")
            date_str = event.get("date", "Unknown date")
            themes = event.get("themes", [])
            body = event.get("body", "")
            add_event(doc, title, date_str, themes, body, event_num)
            
            if event_num >= 50:
                p = doc.add_paragraph()
                run = p.add_run(f"\n[... {len(events_data) - 50} more events truncated for document brevity ...]")
                run.italic = True
                run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
                break
    
    doc.add_page_break()
    
    # ══ Section 4: Appendix — Event Index ═════════════════════════════
    add_heading_styled(doc, "4. Appendix: Event Index", level=1)
    add_body(doc, "Sorted event table from appendix/event_index.md")
    
    event_idx_path = EVIDENCE_DIR / "appendix" / "event_index.md"
    if event_idx_path.exists():
        content = event_idx_path.read_text(encoding="utf-8")
        # Basic markdown to plain text for DOCX
        lines = content.split("\n")
        for line in lines[:60]:
            if line.strip():
                add_body(doc, line.strip().lstrip("#| "))
        if len(lines) > 60:
            add_body(doc, f"[... {len(lines) - 60} more lines in full appendix ...]")
    
    doc.add_page_break()
    
    # ══ Section 5: Appendix — Theme Index ═════════════════════════════
    add_heading_styled(doc, "5. Appendix: Theme Index", level=1)
    add_body(doc, "Events grouped by theme from appendix/theme_index.md")
    
    theme_idx_path = EVIDENCE_DIR / "appendix" / "theme_index.md"
    if theme_idx_path.exists():
        content = theme_idx_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for line in lines[:80]:
            if line.strip():
                add_body(doc, line.strip().lstrip("#| "))
        if len(lines) > 80:
            add_body(doc, f"[... {len(lines) - 80} more lines in full appendix ...]")
    
    doc.add_page_break()
    
    # ══ Section 6: Appendix — Source Manifest ═════════════════════════
    add_heading_styled(doc, "6. Appendix: Source Manifest", level=1)
    add_body(doc, "Source contribution summary from appendix/source_manifest.md")
    
    src_path = EVIDENCE_DIR / "appendix" / "source_manifest.md"
    if src_path.exists():
        content = src_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for line in lines[:30]:
            if line.strip():
                add_body(doc, line.strip().lstrip("#| "))
    
    doc.add_page_break()
    
    # ══ Section 7: Appendix — Link Registry ═══════════════════════════
    add_heading_styled(doc, "7. Appendix: Link Registry", level=1)
    add_body(doc, "All URLs sorted by domain from appendix/link_registry.md")
    
    link_path = EVIDENCE_DIR / "appendix" / "link_registry.md"
    if link_path.exists():
        content = link_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for line in lines[:60]:
            if line.strip():
                add_body(doc, line.strip())
        if len(lines) > 60:
            add_body(doc, f"[... {len(lines) - 60} more URLs in full appendix ...]")
    
    # ══ Footer ═════════════════════════════════════════════════════════
    doc.add_page_break()
    p_footer = doc.add_paragraph()
    p_footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_footer = p_footer.add_run("— End of Report —")
    run_footer.italic = True
    run_footer.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    
    p_footer2 = doc.add_paragraph()
    p_footer2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_footer2 = p_footer2.add_run("Generated by chronicle_pipeline v2 (Phase 9b) • WordHorrorStories • 2026-02-14")
    run_footer2.font.size = Pt(8)
    run_footer2.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)
    
    # ── Save ──────────────────────────────────────────────────────────
    OUTPUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUTPUT_DOCX))
    print(f"✅ Report saved: {OUTPUT_DOCX.resolve()}")
    print(f"   Size: {OUTPUT_DOCX.stat().st_size / 1024:.1f} KB")
    
    # Print summary
    if events_data:
        print(f"\n📊 Summary:")
        print(f"   Total events: {total_events}")
        print(f"   Tagged: {tagged_events}/{total_events} ({tagged_events/total_events*100:.1f}%)")
        if 'over_tagged' in locals():
            print(f"   Over-tagged (4+ themes): {over_tagged}/{total_events} ({over_tagged/total_events*100:.1f}%)")
        print(f"   Themes: {', '.join(f'{t}={c}' for t, c in sorted_themes)}")


if __name__ == "__main__":
    main()
