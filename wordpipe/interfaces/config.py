from __future__ import annotations

from typing import Any, Protocol


class ConfigProvider(Protocol):
    """Configuration provider for composition roots and CLIs.

    Core/orchestration code should not read environment variables directly.
    """

    def get(self, key: str, default: Any = None) -> Any: ...

