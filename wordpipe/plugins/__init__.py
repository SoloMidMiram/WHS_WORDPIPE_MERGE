"""Plugin registry and capability loading.

Plugins are optional and must not be loaded implicitly at import time.
Call `wordpipe.plugins.registry.load_entrypoints()` explicitly if needed.
"""

from wordpipe.plugins.registry import (
    CapabilityRegistry,
    global_registry,
)

__all__ = ["CapabilityRegistry", "global_registry"]

