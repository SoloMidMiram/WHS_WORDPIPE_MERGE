# =============================
# file: wordpipe/config.py
# =============================
"""Central configuration: styles & timing knobs.
Keep this as the single source of truth and import everywhere.
"""

CHANGE_NOTE_STYLE = "ChangeNote"
CHANGE_LOG_HEADING_STYLE = "ChangeLogHeading"
CHANGE_LOG_TABLE_STYLE = "ChangeLogTable"
AI_HEADING_STYLE = "AIHeading"
KEYWORD_STYLE = "KeywordInsert"
CODE_STYLE = "CodeBlock"
ENTRY_DATE_STYLE = "EntryDate"

# Cluster inserts in COM flattener if they happen close together (seconds)
MERGE_INSERTS_SECONDS = 30
