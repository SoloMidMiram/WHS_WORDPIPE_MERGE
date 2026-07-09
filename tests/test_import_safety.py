import importlib
import sys
import unittest
import warnings
from contextlib import contextmanager
from importlib.abc import MetaPathFinder


class _BlockOptionalDeps(MetaPathFinder):
    def __init__(self, blocked: set[str]):
        self._blocked = blocked

    def find_spec(self, fullname, path, target=None):  # noqa: D401
        for base in self._blocked:
            if fullname == base or fullname.startswith(base + "."):
                raise ModuleNotFoundError(f"blocked optional dependency: {fullname}")
        return None


@contextmanager
def _blocked_imports(*names: str):
    blocked = set(names)
    finder = _BlockOptionalDeps(blocked)
    sys.meta_path.insert(0, finder)
    try:
        yield
    finally:
        sys.meta_path = [f for f in sys.meta_path if f is not finder]


def _purge(prefix: str) -> None:
    for key in [k for k in sys.modules.keys() if k == prefix or k.startswith(prefix + ".")]:
        sys.modules.pop(key, None)


class ImportSafetyTests(unittest.TestCase):
    def test_import_wordpipe_without_optional_deps(self):
        # Even if these packages are installed in the dev environment, we block them
        # to simulate a "core-only" installation.
        optional = [
            "docx",
            "openai",
            "dotenv",
            "httpx",
            "lxml",
            "MergedpipelineV3",
            "win32com",
            "pythoncom",
            "comtypes",
        ]

        with _blocked_imports(*optional):
            _purge("wordpipe")
            importlib.import_module("wordpipe")
            importlib.import_module("wordpipe.core")
            importlib.import_module("wordpipe.pipeline")
            importlib.import_module("wordpipe.interfaces")
            importlib.import_module("wordpipe.orchestration")
            importlib.import_module("wordpipe.plugins")
            # Common "independent module" imports should also be safe.
            importlib.import_module("wordpipe.core.datatypes")
            importlib.import_module("wordpipe.core.ooxml")
            importlib.import_module("wordpipe.core.segment")
            importlib.import_module("wordpipe.core.styles")
            # AI adapter imports should also be safe (lazy deps).
            importlib.import_module("wordpipe.adapters")
            importlib.import_module("wordpipe.adapters.ai")
            # Verify core AI interfaces are importable.
            importlib.import_module("wordpipe.interfaces.ai")
            # Verify DummySummarizer does not require OpenAI.
            from wordpipe.adapters.ai import DummySummarizer
            ds = DummySummarizer()
            self.assertEqual(ds.summarize("hello"), "hello")
            # Deprecated wordpipe.ai stub must also be import-safe.
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                importlib.import_module("wordpipe.ai")
            self.assertTrue(any(isinstance(w.message, DeprecationWarning) for w in caught))


if __name__ == "__main__":
    unittest.main()
