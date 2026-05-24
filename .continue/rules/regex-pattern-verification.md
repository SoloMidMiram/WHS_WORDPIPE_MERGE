---
globs: "**/*.py"
description: Always test regex patterns against real data before finalizing
---

Before finalizing a regex pattern, always test it against actual data samples. Use a small test script that reads real file content and verifies the pattern matches correctly. Pay special attention to: (1) lazy vs greedy quantifiers, (2) Unicode characters vs ASCII equivalents, (3) anchor characters like `$` that may fail on trailing whitespace, (4) the exact order of characters (e.g., `**text:**` vs `**text**:`).