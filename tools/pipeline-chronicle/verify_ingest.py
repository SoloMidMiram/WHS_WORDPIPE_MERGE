#!/usr/bin/env python3
"""Compatibility wrapper for the canonical Chronicle verify-ingest CLI."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from wordpipe.chronicle.cli.verify_ingest import main as _main


def main(argv: Sequence[str] | None = None) -> int:
    warnings.warn(
        "tools/pipeline-chronicle/verify_ingest.py is deprecated. Use python -m "
        "wordpipe.chronicle.cli.verify_ingest instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _main(argv)


if __name__ == "__main__":
    sys.exit(main())
