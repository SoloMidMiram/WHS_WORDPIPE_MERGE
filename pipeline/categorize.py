#!/usr/bin/env python3
"""
[DEPRECATED] Thin wrapper -- delegates to wordpipe.chronicle.cli.categorize.

This file is kept for backward compatibility. New code should import
from wordpipe.chronicle.categorize or run wordpipe.chronicle.cli.categorize directly.

See docs/engineering/CHRONICLE_CANONICAL_DECISION.md for migration details.
"""

from __future__ import annotations

import sys
import warnings

warnings.warn(
    "pipeline/categorize.py is deprecated. Use wordpipe.chronicle.cli.categorize instead.",
    DeprecationWarning,
    stacklevel=2,
)

if __name__ == "__main__":
    from wordpipe.chronicle.cli.categorize import main

    main()
    sys.exit(0)
