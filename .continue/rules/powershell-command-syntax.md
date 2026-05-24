---
globs: "**/*.py"
description: Use PowerShell-compatible syntax for all terminal commands
---

When running terminal commands in PowerShell, use `;` instead of `&&` to chain commands. Use `2>$null` instead of `2>/dev/null` for stderr suppression. Use `del` instead of `rm`. Use backtick `` ` `` for line continuation instead of `\`. Always quote file paths with parentheses in double quotes.