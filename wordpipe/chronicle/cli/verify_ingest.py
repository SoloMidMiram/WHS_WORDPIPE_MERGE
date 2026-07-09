"""CLI wrapper for Chronicle ingest verification."""

from __future__ import annotations

import sys
from typing import Sequence

from wordpipe.chronicle.verify_ingest import main as _main


def main(argv: Sequence[str] | None = None) -> int:
    return _main(argv)


if __name__ == "__main__":
    sys.exit(main())
