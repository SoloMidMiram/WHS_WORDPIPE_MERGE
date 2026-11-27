#!/usr/bin/env python3
"""
[DEPRECATED] Thin wrapper — delegates to wordpipe.chronicle.cli.verify_ingest.

This file is kept for backward compatibility. New code should import
from wordpipe.chronicle.verify_ingest or run wordpipe.chronicle.cli.verify_ingest directly.

See docs/engineering/CHRONICLE_CANONICAL_DECISION.md for migration details.
"""

from __future__ import annotations

import os
import sys
import warnings

warnings.warn(
    "pipeline/verify_ingest.py is deprecated. "
    "Use wordpipe.chronicle.cli.verify_ingest instead.",
    DeprecationWarning,
    stacklevel=2,
)

if __name__ == "__main__":
    if "WORDPIPE_ORIGIN_QUALIFICATION" in os.environ:
        from pathlib import Path
        from runpy import run_path

        run_path(str(Path(__file__).with_name("_import_origin.py")))["require_driver"](
            __file__, "wordpipe.chronicle.verify_ingest", "wordpipe.chronicle.cli.verify_ingest",
        )
    from wordpipe.chronicle.cli.verify_ingest import main

    sys.exit(main())
