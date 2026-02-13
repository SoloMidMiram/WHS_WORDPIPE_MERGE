from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class CapabilityRegistry:
    """Simple in-process capability registry.

    This provides a stable surface for optional features without leaking
    dependencies into the base import path.
    """

    _caps: dict[str, Any] = field(default_factory=dict)

    def register(self, name: str, provider: Any) -> None:
        self._caps[name] = provider

    def get(self, name: str) -> Any | None:
        return self._caps.get(name)

    def names(self) -> list[str]:
        return sorted(self._caps.keys())

    def load_entrypoints(self, group: str = "wordpipe.plugins") -> list[str]:
        """Load plugins from Python entry points (optional).

        This performs imports only when called.
        """

        loaded: list[str] = []
        try:
            from importlib import metadata
        except Exception:  # pragma: no cover
            return loaded

        try:
            eps = metadata.entry_points()
            candidates = (
                eps.select(group=group) if hasattr(eps, "select") else eps.get(group, [])
            )
        except Exception:
            return loaded

        for ep in candidates:
            try:
                obj = ep.load()
                self.register(ep.name, obj)
                loaded.append(ep.name)
            except Exception:
                continue
        return loaded


global_registry = CapabilityRegistry()

