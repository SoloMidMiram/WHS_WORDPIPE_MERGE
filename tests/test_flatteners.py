"""Import-safety and fallback tests for ComFlattener (P0.3 / second-wave P0.1).

Verifies:
- ``from wordpipe.adapters.flatteners.com_flattener import ComFlattener`` does
  NOT fail on any platform (import safety).
- ``ComFlattener()`` construction raises ``RuntimeError`` when ``MergedpipelineV3``
  is unavailable.
- ``make_flattener(prefer_win32=...)`` returns ``_UnavailableFlattener`` when
  ``MergedpipelineV3`` is absent (both Windows and non-Windows paths).
- ``_UnavailableFlattener.run()`` raises ``RuntimeError``.
"""

from __future__ import annotations

from pathlib import Path

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
    """``make_flattener`` returns ``_UnavailableFlattener`` when
    ``MergedpipelineV3`` is absent (both flattener paths require it).
    """

    def test_make_flattener_falls_back(self) -> None:
        """When ``MergedpipelineV3`` is unavailable, ``make_flattener`` returns
        ``_UnavailableFlattener`` even with ``prefer_win32=True``."""
        from wordpipe.adapters.flatteners.base import _UnavailableFlattener, make_flattener

        fl = make_flattener(prefer_win32=True)
        assert isinstance(fl, _UnavailableFlattener), (
            f"Expected _UnavailableFlattener, got {type(fl).__name__}"
        )

    def test_make_flattener_no_flattener(self) -> None:
        """When ``MergedpipelineV3`` is unavailable, ``make_flattener`` returns
        ``_UnavailableFlattener`` even with ``prefer_win32=False``."""
        from wordpipe.adapters.flatteners.base import _UnavailableFlattener, make_flattener

        fl = make_flattener(prefer_win32=False)
        assert isinstance(fl, _UnavailableFlattener), (
            f"Expected _UnavailableFlattener, got {type(fl).__name__}"
        )

    def test_make_flattener_non_windows_preflight(self, monkeypatch) -> None:
        """Non-Windows + prefer_win32 probes the legacy dependency up front
        instead of returning a live XmlFlattener that fails later."""
        import sys

        from wordpipe.adapters.flatteners.base import _UnavailableFlattener, make_flattener

        monkeypatch.setattr(sys, "platform", "linux")
        fl = make_flattener(prefer_win32=True)
        assert isinstance(fl, _UnavailableFlattener), (
            f"Expected _UnavailableFlattener, got {type(fl).__name__}"
        )

    def test_unavailable_flattener_run_raises(self) -> None:
        """``_UnavailableFlattener.run()`` raises ``RuntimeError``."""
        from wordpipe.adapters.flatteners.base import _UnavailableFlattener

        stub = _UnavailableFlattener(reason="test")
        with pytest.raises(RuntimeError, match="test"):
            stub.run(Path("in.docx"), Path("out.docx"))
