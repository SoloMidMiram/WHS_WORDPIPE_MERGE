---
globs: "**/*.py"
description: Avoid UnicodeEncodeError when printing to Windows console
---

When printing to stdout in Python on Windows, avoid emoji and non-ASCII characters that may not be supported by the console encoding (CP1252). Either use ASCII-safe characters, call `sys.stdout.reconfigure(encoding='utf-8')` at the start, or set `PYTHONIOENCODING=utf-8` environment variable.