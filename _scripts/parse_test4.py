import re, json
text = open('_ARCHIVE/evidence/chronicle_v2/chronicle_tagged.md', encoding='utf-8').read()
# Find the Global ChatGPT Outage event
idx = text.find('Global ChatGPT Outage')
if idx > 0:
    chunk = text[idx-50:idx+1500]
    print('=== Raw text around Global ChatGPT Outage ===')
    print(repr(chunk[:1200]))
