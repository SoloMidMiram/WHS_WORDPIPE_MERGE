import re, json
text = open('_ARCHIVE/evidence/chronicle_v2/chronicle_tagged.md', encoding='utf-8').read()
jdata = json.load(open('_ARCHIVE/evidence/chronicle_v2/chronicle_tagged.tagged.json', encoding='utf-8'))
json_keys = set()
for ev in jdata:
    json_keys.add((ev.get('date',''), ev.get('title','')))
blocks = re.split('(?=^## Event:)', text, flags=re.MULTILINE)
seen = set()
for b in blocks[1:]:
    if not b.strip():
        continue
    m = re.search('^## Event:\s*(.+)$', b, re.MULTILINE)
    if not m:
        continue
    title_line = m.group(1).strip()
    dm = re.match(r'(\d{4}-\d{2}-\d{2})\s*[\u2013-]\s*(.*)', title_line)
    date_str = dm.group(1) if dm else 'Unknown'
    clean_title = dm.group(2).strip() if dm else title_line
    key = (date_str, clean_title)
    if key not in json_keys:
        continue
    if key in seen:
        continue
    seen.add(key)
    bm = re.search(r'-->\n\n(.*)', b, re.DOTALL)
    body = bm.group(1).strip() if bm else ''
    # Show raw body for first event
    if clean_title == 'Polite Refusals and Quirks':
        print('=== RAW BODY (first 500 chars) ===')
        print(repr(body[:500]))
        print()
        # Check for markdown artifacts
        print('Has **bold**:', '**' in body)
        print('Has *italic*:', bool(re.search(r'(?<!\*)\*(?!\*)', body)))
        print('Has <!--:', '<!--' in body)
        print('Has file://:', 'file://' in body)
        print('Has [text](url):', bool(re.search(r'\[([^\]]+)\]\(([^)]+)\)', body)))
        break
