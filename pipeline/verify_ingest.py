#!/usr/bin/env python3
"""
[DEPRECATED] Thin wrapper — delegates to wordpipe.chronicle.cli.verify_ingest.

This file is kept for backward compatibility. New code should import
from wordpipe.chronicle.verify_ingest or run wordpipe.chronicle.cli.verify_ingest directly.

See docs/engineering/CHRONICLE_CANONICAL_DECISION.md for migration details.
"""

from __future__ import annotations

import sys
import warnings

warnings.warn(
    "pipeline/verify_ingest.py is deprecated. "
    "Use wordpipe.chronicle.cli.verify_ingest instead.",
    DeprecationWarning,
    stacklevel=2,
)

if __name__ == "__main__":
    from wordpipe.chronicle.cli.verify_ingest import main

    sys.exit(main())
