from docx import Document
import re
doc = Document('output_chronicle_report_v2.docx')
t = doc.paragraphs[106].text
print(f'Length: {len(t)}')
contains = "<!--" in t
print(f'Contains <!--: {contains}')
matches = list(re.finditer("<!--", t))
print(f'Matches: {len(matches)}')
for m in matches[:3]:
    start = m.start()
    print(f'  at {start}: {repr(t[start-5:start+15])}')
