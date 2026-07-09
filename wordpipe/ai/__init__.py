"""Deprecated compatibility package for legacy AI scripts.

Script-style AI modules formerly lived here. They have been moved to
``scripts/ai/`` and are not part of the packaged runtime library.

Public runtime AI surface:
- ``wordpipe.interfaces.ai`` — protocols/contracts
- ``wordpipe.adapters.ai`` — import-safe adapters (``DummySummarizer``, etc.)

Manual scripts and canaries:
- ``scripts/ai/`` — run directly, not imported by runtime code
"""

from __future__ import annotations

import warnings

warnings.warn(
    "wordpipe.ai is deprecated. Use wordpipe.interfaces.ai / wordpipe.adapters.ai "
    "for runtime code, or scripts/ai/ for manual scripts.",
    DeprecationWarning,
    stacklevel=2,
)
