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
    if clean_title == 'Global ChatGPT Outage':
        print('=== Global ChatGPT Outage body (first 800 chars) ===')
        print(repr(body[:800]))
        print()
        # Check link format
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', body)
        print(f'Links found: {len(links)}')
        for l in links[:5]:
            print(f'  [{l[0]}] -> {l[1][:80]}')
        break
