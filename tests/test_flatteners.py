"""Import-safety and fallback tests for ComFlattener (P0.3).

Verifies:
- ``from wordpipe.adapters.flatteners.com_flattener import ComFlattener`` does
  NOT fail on any platform (import safety).
- ``ComFlattener()`` construction raises ``RuntimeError`` when ``MergedpipelineV3``
  is unavailable.
- ``make_flattener(prefer_win32=True)`` falls back to ``XmlFlattener`` when COM
  is unavailable.
"""

from __future__ import annotations

import pytest


class TestComFlattenerImportSafety:
    """Importing the class must never fail — only construction may fail."""

    def test_import_com_flattener_safe(self) -> None:
        """Importing ``ComFlattener`` at module level succeeds."""
        from wordpipe.adapters.flatteners.com_flattener import ComFlattener

        assert ComFlattener.__name__ == "ComFlattener"

    def test_construct_com_flattener_raises(self) -> None:
        """Constructing ``ComFlattener()`` raises ``RuntimeError`` when
        ``MergedpipelineV3`` is unavailable."""
        from wordpipe.adapters.flatteners.com_flattener import ComFlattener

        with pytest.raises(RuntimeError) as exc_info:
            ComFlattener()
        assert "COM flattener unavailable" in str(exc_info.value)


class TestMakeFlattenerFallback:
    """``make_flattener`` should return ``XmlFlattener`` when COM is unavailable."""

    def test_make_flattener_falls_back(self) -> None:
        """``make_flattener(prefer_win32=True)`` returns an ``XmlFlattener``
        instance (not ``ComFlattener``) when COM is unavailable."""
        from wordpipe.adapters.flatteners.base import make_flattener
        from wordpipe.adapters.flatteners.xml_flattener import XmlFlattener

        fl = make_flattener(prefer_win32=True)
        assert isinstance(fl, XmlFlattener), (
            f"Expected XmlFlattener, got {type(fl).__name__}"
        )

    def test_make_flattener_no_flattener(self) -> None:
        """``make_flattener(prefer_win32=False)`` returns an ``XmlFlattener``."""
        from wordpipe.adapters.flatteners.base import make_flattener
        from wordpipe.adapters.flatteners.xml_flattener import XmlFlattener

        fl = make_flattener(prefer_win32=False)
        assert isinstance(fl, XmlFlattener), (
            f"Expected XmlFlattener, got {type(fl).__name__}"
        )
