#!/usr/bin/env python3
"""
[DEPRECATED] Thin wrapper -- delegates to wordpipe.chronicle.cli.merge.

This file is kept for backward compatibility. New code should import
from wordpipe.chronicle.merge or run wordpipe.chronicle.cli.merge directly.

See docs/engineering/CHRONICLE_CANONICAL_DECISION.md for migration details.
"""

from __future__ import annotations

import sys
import warnings

warnings.warn(
    "pipeline/merge.py is deprecated. Use wordpipe.chronicle.cli.merge instead.",
    DeprecationWarning,
    stacklevel=2,
)

if __name__ == "__main__":
    from wordpipe.chronicle.cli.merge import main

    main()
    sys.exit(0)
