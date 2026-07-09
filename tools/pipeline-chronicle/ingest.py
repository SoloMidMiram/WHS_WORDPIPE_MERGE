#!/usr/bin/env python3
"""
[DEPRECATED] Thin wrapper -- delegates to wordpipe.chronicle.cli.ingest.

This file is kept for backward compatibility (frozen v1 reference).
New code should import from wordpipe.chronicle.ingest or run
wordpipe.chronicle.cli.ingest directly.

See docs/engineering/CHRONICLE_CANONICAL_DECISION.md for migration details.
"""

from __future__ import annotations

import sys
import warnings

warnings.warn(
    "tools/pipeline-chronicle/ingest.py is deprecated. Use wordpipe.chronicle.cli.ingest instead.",
    DeprecationWarning,
    stacklevel=2,
)

if __name__ == "__main__":
    from wordpipe.chronicle.cli.ingest import main

    main()
    sys.exit(0)
