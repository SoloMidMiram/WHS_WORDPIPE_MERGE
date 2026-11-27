#!/usr/bin/env python3
"""
[DEPRECATED] Thin wrapper -- delegates to wordpipe.chronicle.cli.merge.

This file is kept for backward compatibility. New code should import
from wordpipe.chronicle.merge or run wordpipe.chronicle.cli.merge directly.

See docs/engineering/CHRONICLE_CANONICAL_DECISION.md for migration details.
"""

from __future__ import annotations

import os
import sys
import warnings

warnings.warn(
    "pipeline/merge.py is deprecated. Use wordpipe.chronicle.cli.merge instead.",
    DeprecationWarning,
    stacklevel=2,
)

if __name__ == "__main__":
    if "WORDPIPE_ORIGIN_QUALIFICATION" in os.environ:
        from pathlib import Path
        from runpy import run_path

        run_path(str(Path(__file__).with_name("_import_origin.py")))["require_driver"](
            __file__, "wordpipe.chronicle.merge", "wordpipe.chronicle.cli.merge",
        )
    from wordpipe.chronicle.cli.merge import main

    main()
    sys.exit(0)
